"""Base agent class for all CodeCourt agents."""

from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel


class AgentMessage(BaseModel):
    """Message passed between agents."""

    role: str
    content: str
    metadata: dict[str, Any] = {}


class AgentResponse(BaseModel):
    """Response from an agent."""

    agent_name: str
    verdict: str | None = None
    findings: list[dict[str, Any]] = []
    confidence: float = 0.0
    reasoning: str = ""


class BaseAgent(ABC):
    """Base class for all CodeCourt agents."""

    def __init__(self, name: str, role: str) -> None:
        self.name = name
        self.role = role

    @abstractmethod
    async def analyze(self, context: dict[str, Any]) -> AgentResponse:
        """Analyze the given context and return findings."""
        ...

    @abstractmethod
    async def respond(self, message: AgentMessage) -> AgentMessage:
        """Respond to a message from another agent."""
        ...

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name!r}, role={self.role!r})"
