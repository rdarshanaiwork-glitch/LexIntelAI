from app.core.config import settings
from app.core.providers.base import BaseLLMProvider
from app.core.providers.mock import MockLLMProvider
from app.core.providers.remote import OllamaLLMProvider, OpenAILLMProvider, GeminiLLMProvider, GroqLLMProvider

def get_llm_provider() -> BaseLLMProvider:
    provider = settings.LLM_PROVIDER.lower().strip()
    if provider == "mock":
        return MockLLMProvider()
    if provider == "groq":
        return GroqLLMProvider()
    if provider == "gemini":
        return GeminiLLMProvider()
    if provider == "ollama":
        return OllamaLLMProvider()
    elif provider == "openai":
        return OpenAILLMProvider()
    raise RuntimeError(f"Unsupported LLM_PROVIDER={provider}.")

__all__ = [
    "BaseLLMProvider",
    "MockLLMProvider",
    "OllamaLLMProvider",
    "OpenAILLMProvider",
    "GeminiLLMProvider",
    "GroqLLMProvider",
    "get_llm_provider"
]
