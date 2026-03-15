"""Base class for debate agents.

All debate participants (Defender, Prosecutor, Judge) inherit from this.
"""

from abc import abstractmethod
from typing import Any

from codecourt.agents.base import BaseAgent
from codecourt.agents.debate.models import (
    DebateMessage,
    DebateRole,
    DebateState,
    RoundType,
)
from codecourt.providers import BaseLLMProvider, get_provider
from codecourt.tools import ParsedDiff


class BaseDebateAgent(BaseAgent):
    """
    Base class for agents participating in the debate.

    Each debate agent has:
    - A role (defender, prosecutor, judge)
    - A system prompt defining their perspective
    - Methods to participate in their designated rounds
    """

    def __init__(
        self,
        name: str,
        role: DebateRole,
        provider: BaseLLMProvider | None = None,
        provider_name: str = "openai",
        model: str | None = None,
    ) -> None:
        """
        Initialize a debate agent.

        Args:
            name: Display name of the agent
            role: Role in the debate (defender, prosecutor, judge)
            provider: LLM provider instance
            provider_name: Provider name if not providing instance
            model: Specific model to use
        """
        super().__init__(name=name, role=role.value)
        self.debate_role = role
        self.provider = provider or get_provider(provider_name)
        self.model = model

    @property
    @abstractmethod
    def system_prompt(self) -> str:
        """Get the system prompt for this agent."""
        ...

    @abstractmethod
    def get_round_types(self) -> list[RoundType]:
        """Get the round types this agent participates in."""
        ...

    async def participate(
        self,
        round_type: RoundType,
        state: DebateState,
        diff: ParsedDiff,
    ) -> DebateMessage:
        """
        Participate in a debate round.

        Args:
            round_type: The type of round (opening, challenge, etc.)
            state: Current debate state with all messages so far
            diff: The code diff being debated

        Returns:
            DebateMessage with this agent's contribution.
        """
        # Build the prompt for this round
        user_prompt = self._build_round_prompt(round_type, state, diff)

        # Get the response from LLM
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        try:
            response = await self.provider.complete_json(
                messages=messages,
                schema={
                    "type": "object",
                    "properties": {
                        "argument": {"type": "string"},
                        "key_points": {"type": "array", "items": {"type": "string"}},
                        "evidence": {"type": "array", "items": {"type": "string"}},
                        "confidence": {"type": "number"},
                    },
                },
                model=self.model,
            )

            return DebateMessage(
                role=self.debate_role,
                round_type=round_type,
                content=response.get("argument", ""),
                key_points=response.get("key_points", []),
                evidence=response.get("evidence", []),
                confidence=response.get("confidence", 0.8),
            )

        except Exception as e:
            # Return error message if something goes wrong
            return DebateMessage(
                role=self.debate_role,
                round_type=round_type,
                content=f"[Error generating response: {str(e)}]",
                confidence=0.0,
            )

    def _build_round_prompt(
        self,
        round_type: RoundType,
        state: DebateState,
        diff: ParsedDiff,
    ) -> str:
        """Build the prompt for a specific round."""
        # Get the debate transcript so far
        transcript = state.transcript if state.messages else "No prior discussion."

        # Get initial findings context
        findings_text = ""
        if state.initial_findings:
            findings_text = "\n".join(
                f"- [{f.severity.value}] {f.file}:{f.line}: {f.message}"
                for f in state.initial_findings
            )
        else:
            findings_text = "No initial findings from code review."

        # Build round-specific instructions
        round_instruction = self._get_round_instruction(round_type)

        return f"""## Code Changes Being Reviewed

Files: {', '.join(diff.changed_files)}
Lines added: {diff.total_additions}
Lines removed: {diff.total_deletions}

## Initial Code Review Findings

{findings_text}

## Debate Transcript So Far

{transcript}

## Your Task

{round_instruction}

Respond with JSON containing:
- "argument": Your main argument (2-4 paragraphs)
- "key_points": List of 2-4 main points you're making
- "evidence": List of specific code references or facts supporting your argument
- "confidence": Your confidence in this argument (0.0-1.0)
"""

    @abstractmethod
    def _get_round_instruction(self, round_type: RoundType) -> str:
        """Get specific instructions for this round."""
        ...

    async def analyze(self, context: dict[str, Any]) -> Any:
        """Implement BaseAgent interface."""
        # Debate agents use participate() instead
        return None

    async def respond(self, message: Any) -> Any:
        """Implement BaseAgent interface."""
        # Debate agents use participate() instead
        return None
