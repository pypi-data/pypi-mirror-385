from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
from typing import Any

@dataclass
class BaseTelemetryEvent(ABC):
    @property
    @abstractmethod
    def event_name(self) -> str:
        pass

    @property
    def properties(self) -> dict[str,Any]:
        return {k: v for k, v in asdict(self).items()}
    
@dataclass
class AgentTelemetryEvent(BaseTelemetryEvent):
    query: str
    answer: str | None
    error: str | None
    use_vision:bool
    model:str
    provider:str
    agent_log: list[dict]|None
    event_name: str = "agent_event"
    
