# Debate System - Implementation Progress

## Overview

The Debate System implements a courtroom-style code review where multiple AI agents argue about the code:
- **Defender**: Argues FOR the code changes
- **Prosecutor**: Challenges and finds problems
- **Judge**: Delivers final verdict based on the debate

## Commit Plan

| # | Commit | Status | Description |
|---|--------|--------|-------------|
| 1 | Foundation models | ✅ Complete | DebateMessage, DebateRound, DebateState |
| 2 | Defender agent | 🔄 In Progress | Agent that argues for the code |
| 3 | Prosecutor agent | ⏳ Pending | Agent that challenges the code |
| 4 | Judge agent | ⏳ Pending | Agent that delivers verdict |
| 5 | Debate orchestrator | ⏳ Pending | Manages the debate flow |
| 6 | Integration + tests | ⏳ Pending | Wire into Coordinator, CLI, tests |

## Architecture

```
debate/
├── __init__.py          # Exports
├── PROGRESS.md          # This file
├── models.py            # DebateMessage, DebateRound, DebateState
├── base.py              # BaseDebateAgent
├── defender.py          # DefenderAgent
├── prosecutor.py        # ProsecutorAgent
├── judge.py             # JudgeAgent
└── orchestrator.py      # DebateOrchestrator
```

## Debate Flow

```
Input: ParsedDiff + Initial Findings (from CodeReviewer/Security)
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│  Round 1: OPENING STATEMENT                                  │
│  Defender presents case for the code                        │
└─────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│  Round 2: PROSECUTION                                        │
│  Prosecutor challenges, presents counter-arguments          │
└─────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│  Round 3: DEFENSE REBUTTAL                                   │
│  Defender responds to prosecution's points                  │
└─────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│  Round 4: VERDICT                                            │
│  Judge weighs arguments and delivers final ruling           │
└─────────────────────────────────────────────────────────────┘
         │
         ▼
Output: DebateResult with verdict, reasoning, findings

```

## Current Status

**Commit 1: Foundation Models** ✅
- [x] Create debate/models.py with DebateMessage, DebateRound, DebateState
- [x] Create debate/base.py with BaseDebateAgent
- [x] Create debate/__init__.py with exports

**Commit 2: Defender Agent** 🔄
- [ ] Create debate/defender.py with DefenderAgent
- [ ] System prompt that argues FOR code changes
- [ ] Opening statement and rebuttal logic
