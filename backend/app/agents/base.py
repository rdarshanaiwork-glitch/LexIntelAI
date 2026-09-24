import time
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from app.core.llm_provider import get_llm_provider, BaseLLMProvider

logger = logging.getLogger('lexintel.agents')

class BaseLegalAgent(ABC):
    def __init__(self, name: str, description: str, llm_provider: Optional[BaseLLMProvider] = None):
        self.name = name
        self.description = description
        self.llm = llm_provider or get_llm_provider()

    @abstractmethod
    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        pass

    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        start_time = time.time()
        before = dict(getattr(self.llm, "telemetry", {}))
        logger.info(f"[{self.name}] Starting execution...")
        try:
            result = self.execute(state)
            elapsed_ms = int((time.time() - start_time) * 1000)
            logger.info(f"[{self.name}] Finished successfully in {elapsed_ms}ms")
            after = getattr(self.llm, "telemetry", {})
            return {
                "status": "completed",
                "execution_time_ms": elapsed_ms,
                "data": result,
                "error": None,
                "llm_calls": max(0, after.get("llm_calls",0)-before.get("llm_calls",0)),
                "retries": max(0, after.get("retries",0)-before.get("retries",0)),
            }
        except Exception as e:
            elapsed_ms = int((time.time() - start_time) * 1000)
            logger.error(f"[{self.name}] Failed after {elapsed_ms}ms: {e}", exc_info=True)
            after = getattr(self.llm, "telemetry", {})
            return {
                "status": "failed",
                "execution_time_ms": elapsed_ms,
                "data": {},
                "error": str(e),
                "llm_calls": max(0, after.get("llm_calls",0)-before.get("llm_calls",0)),
                "retries": max(0, after.get("retries",0)-before.get("retries",0)),
            }