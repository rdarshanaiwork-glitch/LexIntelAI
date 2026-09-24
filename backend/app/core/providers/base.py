from abc import ABC, abstractmethod
from typing import Type, TypeVar, Optional
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)

class BaseLLMProvider(ABC):
    def __init__(self):
        self.telemetry = {"llm_calls": 0, "retries": 0, "latency_ms": 0}

    @abstractmethod
    def generate_text(self, prompt: str, system_prompt: Optional[str] = None, temperature: float = 0.2) -> str:
        pass

    @abstractmethod
    def generate_structured(self, prompt: str, system_prompt: Optional[str], response_model: Type[T], temperature: float = 0.2) -> T:
        pass