"""Data models for the debate system.

These models define the structure of a code review debate,
including messages, rounds, and the final verdict.
"""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from codecourt.agents.models import Approval, Finding, Severity


class DebateRole(str, Enum):
    """Role of a participant in the debate."""

    DEFENDER = "defender"      # Argues FOR the code
    PROSECUTOR = "prosecutor"  # Argues AGAINST / finds issues
    JUDGE = "judge"            # Makes final verdict


class RoundType(str, Enum):
    """Type of debate round."""

    OPENING = "opening"        # Defender presents initial case
    CHALLENGE = "challenge"    # Prosecutor presents counter-arguments
    REBUTTAL = "rebuttal"      # Defender responds to challenges
    VERDICT = "verdict"        # Judge delivers final ruling


class DebateMessage(BaseModel):
    """A single message in the debate."""

    role: DebateRole = Field(description="Who is speaking")
    round_type: RoundType = Field(description="What type of round this is")
    content: str = Field(description="The argument/statement content")
    
    # Structured arguments (optional, for better tracking)
    key_points: list[str] = Field(
        default_factory=list,
        description="Main points made in this message",
    )
    evidence: list[str] = Field(
        default_factory=list,
        description="Code references or evidence cited",
    )
    
    # Metadata
    timestamp: datetime = Field(default_factory=datetime.now)
    confidence: float = Field(default=0.8, ge=0.0, le=1.0)


class DebateRound(BaseModel):
    """A single round of the debate."""

    round_number: int = Field(description="Round number (1-indexed)")
    round_type: RoundType = Field(description="Type of this round")
    speaker: DebateRole = Field(description="Who speaks this round")
    message: DebateMessage | None = Field(
        default=None,
        description="The message delivered in this round",
    )
    completed: bool = Field(default=False)


class DebateState(BaseModel):
    """Current state of an ongoing debate."""

    # Debate identification
    debate_id: str = Field(default="", description="Unique debate identifier")
    
    # Context
    diff_summary: str = Field(default="", description="Summary of code changes")
    initial_findings: list[Finding] = Field(
        default_factory=list,
        description="Findings from Code Review + Security agents",
    )
    
    # Debate progress
    rounds: list[DebateRound] = Field(default_factory=list)
    messages: list[DebateMessage] = Field(default_factory=list)
    current_round: int = Field(default=0)
    
    # Status
    is_complete: bool = Field(default=False)
    
    @property
    def transcript(self) -> str:
        """Get the full debate transcript as text."""
        lines = []
        for msg in self.messages:
            speaker = msg.role.value.upper()
            round_name = msg.round_type.value.upper()
            lines.append(f"[{round_name}] {speaker}:")
            lines.append(msg.content)
            lines.append("")
        return "\n".join(lines)
    
    def add_message(self, message: DebateMessage) -> None:
        """Add a message to the debate."""
        self.messages.append(message)
    
    def get_context_for_next_speaker(self) -> str:
        """Get context string for the next speaker."""
        return self.transcript


class DebateVerdict(BaseModel):
    """The judge's final verdict."""

    approval: Approval = Field(description="Final approval decision")
    reasoning: str = Field(description="Judge's reasoning")
    
    # Summary of arguments
    defense_strengths: list[str] = Field(
        default_factory=list,
        description="Strong points made by defense",
    )
    prosecution_strengths: list[str] = Field(
        default_factory=list,
        description="Strong points made by prosecution",
    )
    
    # Final findings (may differ from initial)
    upheld_findings: list[Finding] = Field(
        default_factory=list,
        description="Findings upheld after debate",
    )
    dismissed_findings: list[Finding] = Field(
        default_factory=list,
        description="Findings dismissed after debate",
    )
    new_findings: list[Finding] = Field(
        default_factory=list,
        description="New findings discovered during debate",
    )
    
    # Confidence
    confidence: float = Field(default=0.8, ge=0.0, le=1.0)


class DebateResult(BaseModel):
    """Complete result of a debate."""

    # The debate itself
    state: DebateState = Field(description="Full debate state")
    verdict: DebateVerdict = Field(description="Judge's verdict")
    
    # Summary
    total_rounds: int = Field(default=4)
    
    # Final approval (convenience)
    @property
    def approval(self) -> Approval:
        return self.verdict.approval
    
    @property
    def final_findings(self) -> list[Finding]:
        """Get the final list of findings after debate."""
        return self.verdict.upheld_findings + self.verdict.new_findings
    
    @property
    def summary(self) -> str:
        """Get a summary of the debate result."""
        approval_text = {
            Approval.APPROVE: "✅ APPROVED",
            Approval.REQUEST_CHANGES: "❌ CHANGES REQUESTED",
            Approval.COMMENT: "💬 NEEDS DISCUSSION",
        }
        status = approval_text.get(self.verdict.approval, str(self.verdict.approval))
        return f"{status}: {self.verdict.reasoning[:100]}..."
