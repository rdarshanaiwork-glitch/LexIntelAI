import json
import time
import logging
from typing import Dict, Any, Type, TypeVar, Optional
import httpx
from pydantic import BaseModel
from app.core.config import settings
from app.core.providers.base import BaseLLMProvider, T

logger = logging.getLogger("lexintel.llm.remote")

class OllamaLLMProvider(BaseLLMProvider):
    """Local high-performance provider using local Ollama instance (gpt-oss:20b).

    Supports OpenAI-compatible /v1/chat/completions with json_object response format
    and Pydantic model validation.
    """
    def __init__(self, base_url: Optional[str] = None, model: Optional[str] = None):
        super().__init__()
        self.base_url = (base_url or settings.OLLAMA_BASE_URL or "http://localhost:11434").rstrip("/")
        raw_model = model or settings.LLM_MODEL or "gpt-oss:20b"
        if raw_model.startswith("openai/"):
            raw_model = raw_model.replace("openai/", "")
        if ":" not in raw_model and raw_model in ("gpt-oss-20b", "gpt-oss"):
            raw_model = "gpt-oss:20b"
        self.model = raw_model
        # Keep a pooled local connection for each agent/provider instance.
        self._client = httpx.Client(timeout=max(120.0, float(settings.LLM_TIMEOUT_SECONDS) * 2))

    def _call(self, messages: list, response_format: Optional[Dict[str, Any]] = None, temperature: float = 0.2, max_tokens: int = 8192) -> str:
        started = time.time()
        self.telemetry["llm_calls"] += 1
        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if response_format:
            payload["response_format"] = response_format

        try:
            res = self._client.post(f"{self.base_url}/v1/chat/completions", json=payload)
            res.raise_for_status()
            data = res.json()
            self.telemetry["latency_ms"] += int((time.time() - started) * 1000)
            choices = data.get("choices", [])
            if choices:
                return choices[0]["message"]["content"]
            raise RuntimeError("Ollama returned empty choices.")
        except Exception as e:
            logger.warning(f"Ollama /v1/chat/completions failed: {e}. Trying /api/chat...")
            native_payload = {
                "model": self.model,
                "messages": messages,
                "stream": False,
                "options": {"temperature": temperature, "num_predict": max_tokens},
            }
            if response_format:
                native_payload["format"] = "json"
            res = self._client.post(f"{self.base_url}/api/chat", json=native_payload)
            res.raise_for_status()
            self.telemetry["latency_ms"] += int((time.time() - started) * 1000)
            return res.json().get("message", {}).get("content", "")

    def generate_text(self, prompt: str, system_prompt: Optional[str] = None, temperature: float = 0.2) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        try:
            return self._call(messages, temperature=temperature)
        except Exception as e:
            if settings.ALLOW_MOCK_FALLBACK:
                logger.warning("Ollama generate_text failed; explicit mock fallback enabled: %s", e)
                from app.core.providers.mock import MockLLMProvider
                return MockLLMProvider().generate_text(prompt, system_prompt, temperature)
            raise RuntimeError(f"Ollama model {self.model} failed: {e}") from e

    def generate_structured(self, prompt: str, system_prompt: Optional[str], response_model: Type[T], temperature: float = 0.2) -> T:
        schema = response_model.model_json_schema()
        props = schema.get("properties", {})
        required = schema.get("required", list(props.keys()))
        clean_template = {k: f"<{props[k].get('type', 'value')}>" for k in props}

        sys_content = (
            (system_prompt or "You are a rigorous legal intelligence agent.")
            + "\nYou MUST respond ONLY with a single valid JSON object. Do NOT return schema definitions. Fill in concrete instantiated values for these keys:\n"
            + json.dumps(clean_template, indent=2)
            + f"\nRequired fields: {', '.join(required)}"
        )
        user_content = f"{prompt}\n\nRespond strictly with the required JSON object containing your actual findings and instantiated values."
        messages = [
            {"role": "system", "content": sys_content},
            {"role": "user", "content": user_content}
        ]
        try:
            text = self._call(messages, response_format={"type": "json_object"}, temperature=temperature).strip()
            if text.startswith("```json"):
                text = text[7:-3].strip()
            elif text.startswith("```"):
                text = text[3:-3].strip()

            data = json.loads(text)
            if isinstance(data, dict):
                # 1. Unwrap model name if nested: {"ResearchStep": {...}}
                if response_model.__name__ in data and isinstance(data[response_model.__name__], dict):
                    data = data[response_model.__name__]
                elif "data" in data and isinstance(data["data"], dict) and len(data) == 1:
                    data = data["data"]
                elif len(data) == 1:
                    only_val = next(iter(data.values()))
                    if isinstance(only_val, dict):
                        data = only_val

                # 2. Unwrap schema properties format if model mistakenly nested under "properties"
                if isinstance(data, dict) and "properties" in data and isinstance(data["properties"], dict):
                    inner = {}
                    for k, v in data["properties"].items():
                        if isinstance(v, dict):
                            if "value" in v: inner[k] = v["value"]
                            elif "default" in v: inner[k] = v["default"]
                            elif "description" in v and len(v) == 1: inner[k] = v["description"]
                            else: inner[k] = v
                        else:
                            inner[k] = v
                    if inner:
                        data = inner

            return response_model.model_validate(data)
        except Exception as e:
            if settings.ALLOW_MOCK_FALLBACK:
                logger.warning("Ollama structured generation failed; explicit mock fallback enabled: %s", e)
                from app.core.providers.mock import MockLLMProvider
                return MockLLMProvider().generate_structured(prompt, system_prompt, response_model, temperature)
            raise RuntimeError(
                f"Ollama model {self.model} could not return valid {response_model.__name__}: {e}"
            ) from e

class OpenAILLMProvider(BaseLLMProvider):
    def __init__(self, api_key: str = settings.OPENAI_API_KEY, base_url: str = settings.OPENAI_BASE_URL, model: str = settings.LLM_MODEL):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model if model != "llama3:8b" else "gpt-4o-mini"

    def generate_text(self, prompt: str, system_prompt: Optional[str] = None, temperature: float = 0.2) -> str:
        if not self.api_key:
            from app.core.providers.mock import MockLLMProvider
            return MockLLMProvider().generate_text(prompt, system_prompt, temperature)
        try:
            headers = {"Authorization": f"Bearer {self.api_key}"}
            messages = [{"role": "system", "content": system_prompt or ""}, {"role": "user", "content": prompt}]
            with httpx.Client(timeout=60.0) as client:
                res = client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json={"model": self.model, "messages": messages, "temperature": temperature}
                )
                res.raise_for_status()
                return res.json()["choices"][0]["message"]["content"]
        except Exception as e:
            logger.warning(f"OpenAI error: {e}. Falling back to Mock.")
            from app.core.providers.mock import MockLLMProvider
            return MockLLMProvider().generate_text(prompt, system_prompt, temperature)

    def generate_structured(self, prompt: str, system_prompt: Optional[str], response_model: Type[T], temperature: float = 0.2) -> T:
        if not self.api_key:
            from app.core.providers.mock import MockLLMProvider
            return MockLLMProvider().generate_structured(prompt, system_prompt, response_model, temperature)
        try:
            schema_json = json.dumps(response_model.model_json_schema())
            full_prompt = f"{prompt}\n\nRespond with valid JSON matching:\n{schema_json}"
            text = self.generate_text(full_prompt, system_prompt, temperature).strip()
            if text.startswith("```json"): text = text[7:-3].strip()
            elif text.startswith("```"): text = text[3:-3].strip()
            return response_model.model_validate_json(text)
        except Exception as e:
            logger.warning(f"OpenAI structured error: {e}. Falling back to Mock.")
class GroqLLMProvider(BaseLLMProvider):
    """High-speed production provider using Groq Cloud API (OpenAI-compatible).

    Uses Qwen 3 32B, a fast reasoning model available through Groq.
    Structured output is guaranteed via json_object response format + Pydantic schema validation.
    """
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None, base_url: Optional[str] = None):
        super().__init__()
        self.api_key = api_key if api_key is not None else settings.GROQ_API_KEY
        raw_model = model or settings.LLM_MODEL or "openai/gpt-oss-20b"
        if raw_model in ("qwen3:8b", "qwen/qwen3-32b", "gpt-oss:20b", "default"):
            raw_model = "openai/gpt-oss-20b"
        elif raw_model in ("gpt-oss:120b", "gpt-oss-120b"):
            raw_model = "openai/gpt-oss-120b"
        self.model = raw_model
        self.base_url = (base_url or settings.GROQ_BASE_URL or "https://api.groq.com/openai/v1").rstrip("/")
        self._client = httpx.Client(timeout=settings.LLM_TIMEOUT_SECONDS)

    def _call(self, messages: list, response_format: Optional[Dict[str, Any]] = None, temperature: float = 0.2, max_tokens: int = 4096) -> str:
        if not self.api_key:
            raise RuntimeError("GROQ_API_KEY is not configured.")
        retries = max(4, int(settings.LLM_MAX_RETRIES))
        backoff = 2.5
        # 4096 tokens provides full room for JSON completion while staying safely within TPM limits
        safe_max_tokens = min(max_tokens, 4096)
        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": safe_max_tokens,
        }
        if response_format:
            payload["response_format"] = response_format

        for attempt in range(1, retries + 1):
            started = time.time()
            self.telemetry["llm_calls"] += 1
            try:
                res = self._client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json=payload,
                )
                self.telemetry["latency_ms"] += int((time.time() - started) * 1000)
                if res.status_code in (429, 503):
                    err_text = res.text.lower()
                    # If daily quota (TPD) is reached for 20b, immediately pivot to 120b which has a separate quota
                    if ("tokens per day" in err_text or "tpd" in err_text or "daily" in err_text) and payload.get("model") == "openai/gpt-oss-20b":
                        logger.warning("Groq 20B daily token quota exhausted. Seamlessly switching to openai/gpt-oss-120b!")
                        payload["model"] = "openai/gpt-oss-120b"
                        self.model = "openai/gpt-oss-120b"
                        time.sleep(1.0)
                        continue

                    if attempt < retries:
                        self.telemetry["retries"] += 1
                        sleep_time = backoff
                        token_reset_hdr = res.headers.get("x-ratelimit-reset-tokens")
                        retry_after_hdr = res.headers.get("Retry-After")

                        if token_reset_hdr:
                            try:
                                raw = token_reset_hdr.strip().lower()
                                if raw.endswith("ms"):
                                    parsed_tokens = float(raw[:-2]) / 1000.0
                                elif raw.endswith("s"):
                                    parsed_tokens = float(raw[:-1])
                                else:
                                    parsed_tokens = float(raw)
                                sleep_time = max(backoff, parsed_tokens + 0.5)
                            except Exception:
                                pass
                        elif retry_after_hdr:
                            try:
                                parsed = float(retry_after_hdr)
                                # Never sleep for the 30-min request window: cap at 8.0s for token bucket refill
                                sleep_time = max(backoff, min(8.0, parsed))
                            except ValueError:
                                pass

                        # Absolute safety ceiling: never sleep more than 8.0 seconds per retry
                        sleep_time = min(sleep_time, 8.0)

                        logger.warning(
                            "Groq %s on model %s; backing off for %.1fs to refill token bucket (retry %s/%s)",
                            res.status_code,
                            payload.get("model"),
                            sleep_time,
                            attempt,
                            retries,
                        )
                        time.sleep(sleep_time)
                        backoff = min(backoff * 1.5, 8.0)
                        continue
                res.raise_for_status()
                data = res.json()
                choices = data.get("choices", [])
                if not choices:
                    raise RuntimeError("Groq returned no choices in response.")
                return choices[0]["message"]["content"]
            except httpx.HTTPStatusError as exc:
                if exc.response.status_code in (429, 503) and attempt < retries:
                    self.telemetry["retries"] += 1
                    time.sleep(min(backoff, 8.0))
                    backoff = min(backoff * 1.5, 8.0)
                    continue
                logger.error("Groq HTTP error %s: %s", exc.response.status_code, exc.response.text)
                raise
            except Exception:
                if attempt < retries:
                    self.telemetry["retries"] += 1
                    time.sleep(min(backoff, 8.0))
                    backoff = min(backoff * 1.5, 8.0)
                    continue
                raise
        raise RuntimeError("Groq request failed after retries")

    def generate_text(self, prompt: str, system_prompt: Optional[str] = None, temperature: float = 0.2) -> str:
        if not self.api_key:
            if settings.ALLOW_MOCK_FALLBACK:
                from app.core.providers.mock import MockLLMProvider
                return MockLLMProvider().generate_text(prompt, system_prompt, temperature)
            raise RuntimeError("GROQ_API_KEY is not configured.")
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        try:
            return self._call(messages, temperature=temperature)
        except Exception as e:
            if settings.ALLOW_MOCK_FALLBACK:
                logger.warning(f"Groq generate_text failed: {e}. Falling back to MockLLMProvider.")
                from app.core.providers.mock import MockLLMProvider
                return MockLLMProvider().generate_text(prompt, system_prompt, temperature)
            raise

    def generate_structured(self, prompt: str, system_prompt: Optional[str], response_model: Type[T], temperature: float = 0.2) -> T:
        if not self.api_key:
            if settings.ALLOW_MOCK_FALLBACK:
                from app.core.providers.mock import MockLLMProvider
                return MockLLMProvider().generate_structured(prompt, system_prompt, response_model, temperature)
            raise RuntimeError("GROQ_API_KEY is not configured.")
        schema = response_model.model_json_schema()
        props = schema.get("properties", {})
        required = schema.get("required", list(props.keys()))
        clean_template = {k: f"<{props[k].get('type', 'value')}>" for k in props}

        sys_content = (
            (system_prompt or "You are a rigorous legal intelligence agent.")
            + "\nYou MUST respond ONLY with a single valid JSON object. Do NOT return schema definitions. Fill in concrete instantiated values for these keys:\n"
            + json.dumps(clean_template, indent=2)
            + f"\nRequired fields: {', '.join(required)}"
        )
        user_content = f"{prompt}\n\nRespond strictly with the required JSON object containing your actual findings and instantiated values."
        messages = [
            {"role": "system", "content": sys_content},
            {"role": "user", "content": user_content}
        ]
        try:
            try:
                text = self._call(messages, response_format={"type": "json_object"}, temperature=temperature).strip()
            except httpx.HTTPStatusError as exc:
                if exc.response.status_code == 400:
                    logger.warning("Groq 400 on strict json_object format; retrying with prompt-guided JSON...")
                    text = self._call(messages, response_format=None, temperature=temperature).strip()
                else:
                    raise

            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].split("```")[0].strip()

            if "{" in text and "}" in text:
                start_idx = text.find("{")
                end_idx = text.rfind("}") + 1
                text = text[start_idx:end_idx]

            data = json.loads(text)
            if isinstance(data, dict):
                # Unwrap model name if nested: {"ResearchStep": {...}}
                if response_model.__name__ in data and isinstance(data[response_model.__name__], dict):
                    data = data[response_model.__name__]
                elif "data" in data and isinstance(data["data"], dict) and len(data) == 1:
                    data = data["data"]
                elif len(data) == 1:
                    only_val = next(iter(data.values()))
                    if isinstance(only_val, dict):
                        data = only_val

                # Unwrap schema properties format if model mistakenly nested under "properties"
                if isinstance(data, dict) and "properties" in data and isinstance(data["properties"], dict):
                    inner = {}
                    for k, v in data["properties"].items():
                        if isinstance(v, dict):
                            if "value" in v:
                                inner[k] = v["value"]
                            elif "default" in v:
                                inner[k] = v["default"]
                            elif "description" in v and len(v) == 1:
                                inner[k] = v["description"]
                            else:
                                inner[k] = v
                        else:
                            inner[k] = v
                    if inner:
                        data = inner

            return response_model.model_validate(data)
        except Exception as e:
            if settings.ALLOW_MOCK_FALLBACK:
                logger.warning(f"Groq generate_structured failed: {e}. Falling back to MockLLMProvider.")
                from app.core.providers.mock import MockLLMProvider
                return MockLLMProvider().generate_structured(prompt, system_prompt, response_model, temperature)
            raise

class GeminiLLMProvider(BaseLLMProvider):
    """Production provider using Google Gemini Flash-Lite (gemini-flash-lite-latest).

    Features:
    - High-throughput, low-latency agent execution
    - Native responseMimeType: application/json support
    - Model rotation across Gemini Lite models (flash-lite-latest, 3.5-flash-lite, 3.1-flash-lite) to avoid 429 rate limits
    """
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        super().__init__()
        self.api_key = api_key if api_key is not None else settings.GEMINI_API_KEY
        raw_model = model or settings.LLM_MODEL or "gemini-flash-lite-latest"
        if raw_model in ("default", "gemini", "gemini-flash", "gemini-1.5-flash", "gemini-2.5-flash", "openai/gpt-oss-20b", "openai/gpt-oss-120b", "gemini-3.6-flash"):
            raw_model = "gemini-flash-lite-latest"
        self.model = raw_model
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"
        self._client = httpx.Client(timeout=settings.LLM_TIMEOUT_SECONDS)

    def _call(self, payload: Dict[str, Any]) -> str:
        if not self.api_key:
            raise RuntimeError("GEMINI_API_KEY is not configured.")
        retries = max(3, int(settings.LLM_MAX_RETRIES))
        backoff = 1.5
        current_model = self.model

        # Rotation models on Gemini Lite
        lite_models = ["gemini-flash-lite-latest", "gemini-3.5-flash-lite", "gemini-3.1-flash-lite"]

        for attempt in range(1, retries + 1):
            started = time.time()
            self.telemetry["llm_calls"] += 1
            url = f"{self.base_url}/{current_model}:generateContent?key={self.api_key}"
            try:
                res = self._client.post(url, json=payload)
                self.telemetry["latency_ms"] += int((time.time() - started) * 1000)
                if res.status_code in (429, 503):
                    # Rotate to next Gemini Lite model to bypass per-model quota
                    next_idx = (lite_models.index(current_model) + 1) % len(lite_models) if current_model in lite_models else 0
                    alt_model = lite_models[next_idx]
                    logger.warning(
                        "Gemini %s on %s; rotating to %s to avoid rate limits (attempt %s/%s)",
                        res.status_code,
                        current_model,
                        alt_model,
                        attempt,
                        retries,
                    )
                    current_model = alt_model
                    self.model = alt_model
                    time.sleep(min(backoff, 4.0))
                    backoff = min(backoff * 1.5, 4.0)
                    continue

                res.raise_for_status()
                data = res.json()
                candidates = data.get("candidates", [])
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    for part in parts:
                        if isinstance(part, dict) and "text" in part:
                            return part["text"]
                raise RuntimeError("Gemini returned empty candidates.")
            except httpx.HTTPStatusError as exc:
                if exc.response.status_code in (429, 503) and attempt < retries:
                    self.telemetry["retries"] += 1
                    time.sleep(min(backoff, 4.0))
                    backoff = min(backoff * 1.5, 4.0)
                    continue
                logger.error("Gemini HTTP error %s: %s", exc.response.status_code, exc.response.text)
                raise
            except Exception:
                if attempt < retries:
                    self.telemetry["retries"] += 1
                    time.sleep(min(backoff, 4.0))
                    backoff = min(backoff * 1.5, 4.0)
                    continue
                raise
        raise RuntimeError("Gemini request failed after retries")

    def generate_text(self, prompt: str, system_prompt: Optional[str] = None, temperature: float = 0.2) -> str:
        combined_text = (f"System: {system_prompt}\n\n" if system_prompt else "") + f"User: {prompt}"
        payload = {
            "contents": [{"parts": [{"text": combined_text}]}],
            "generationConfig": {"temperature": temperature}
        }
        try:
            return self._call(payload)
        except Exception as e:
            if settings.ALLOW_MOCK_FALLBACK:
                logger.warning(f"Gemini generate_text failed: {e}. Falling back to MockLLMProvider.")
                from app.core.providers.mock import MockLLMProvider
                return MockLLMProvider().generate_text(prompt, system_prompt, temperature)
            raise

    def generate_structured(self, prompt: str, system_prompt: Optional[str], response_model: Type[T], temperature: float = 0.2) -> T:
        schema_json = json.dumps(response_model.model_json_schema(), indent=2)
        instruction = (
            (f"{system_prompt}\n\n" if system_prompt else "You are a rigorous legal intelligence agent.\n\n")
            + f"{prompt}\n\n"
            + "Respond STRICTLY with a single valid JSON object satisfying this schema:\n"
            + schema_json
        )
        payload = {
            "contents": [{"parts": [{"text": instruction}]}],
            "generationConfig": {
                "responseMimeType": "application/json",
                "temperature": temperature
            }
        }
        try:
            raw_text = self._call(payload).strip()
            if "```json" in raw_text:
                raw_text = raw_text.split("```json")[1].split("```")[0].strip()
            elif "```" in raw_text:
                raw_text = raw_text.split("```")[1].split("```")[0].strip()

            if "{" in raw_text and "}" in raw_text:
                start_idx = raw_text.find("{")
                end_idx = raw_text.rfind("}") + 1
                raw_text = raw_text[start_idx:end_idx]

            data = json.loads(raw_text)
            if isinstance(data, dict):
                if response_model.__name__ in data and isinstance(data[response_model.__name__], dict):
                    data = data[response_model.__name__]
                elif "data" in data and isinstance(data["data"], dict) and len(data) == 1:
                    data = data["data"]
                elif len(data) == 1:
                    only_val = next(iter(data.values()))
                    if isinstance(only_val, dict):
                        data = only_val

            return response_model.model_validate(data)
        except Exception as e:
            # Dual-LLM Resilience: Try Groq if Gemini structured output fails
            try:
                logger.warning("Gemini structured failed (%s). Failing over to GroqLLMProvider...", e)
                from app.core.providers.remote import GroqLLMProvider
                return GroqLLMProvider(model="openai/gpt-oss-120b").generate_structured(prompt, system_prompt, response_model, temperature)
            except Exception as fallback_err:
                logger.warning("Dual-LLM Groq failover also failed: %s", fallback_err)

            if settings.ALLOW_MOCK_FALLBACK:
                logger.warning("Falling back to MockLLMProvider.")
                from app.core.providers.mock import MockLLMProvider
                return MockLLMProvider().generate_structured(prompt, system_prompt, response_model, temperature)
            raise
