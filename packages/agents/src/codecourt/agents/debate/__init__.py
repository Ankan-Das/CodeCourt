"""CodeCourt Debate System.

The debate system implements a courtroom-style code review where
multiple AI agents argue about the code changes:

- Defender: Argues FOR the code changes
- Prosecutor: Challenges and finds problems  
- Judge: Delivers final verdict

Usage:
    from codecourt.agents.debate import DebateOrchestrator

    orchestrator = DebateOrchestrator(provider_name="openai")
    result = await orchestrator.run_debate(diff, initial_findings)
    print(result.verdict.approval)
"""

from codecourt.agents.debate.base import BaseDebateAgent
from codecourt.agents.debate.models import (
    DebateMessage,
    DebateResult,
    DebateRole,
    DebateRound,
    DebateState,
    DebateVerdict,
    RoundType,
)

__all__ = [
    # Models
    "DebateRole",
    "RoundType",
    "DebateMessage",
    "DebateRound",
    "DebateState",
    "DebateVerdict",
    "DebateResult",
    # Base
    "BaseDebateAgent",
]
