# CodeCourt - Progress Tracker

## Current Status

**Phase:** 3 - Advanced Features (In Progress)  
**Next Up:** Debate System (Defender/Prosecutor/Judge)  
**Last Updated:** 2026-03-15

---

## Phase 1: Foundation ✅

### 1.1 Project Setup
- [x] Initialize monorepo structure
- [x] Set up Python package with pyproject.toml
- [ ] Set up TypeScript package with package.json
- [x] Create docs/ROADMAP.md, PROGRESS.md, devlog/

### 1.2 LLM Provider Abstraction
- [x] Create base provider interface (`providers/base.py`)
- [x] Implement OpenAI provider
- [x] Implement Anthropic provider
- [x] Implement Ollama provider
- [x] Add provider factory with config

### 1.3 Git/Diff Tools
- [x] Parse git diff output
- [x] Extract changed files and hunks
- [x] Read file contents with context
- [x] Create patch/diff models

### 1.4 Basic Code Review Agent
- [x] Single agent that reviews a diff (`code_reviewer.py`)
- [x] Returns structured feedback (file, line, severity, message)
- [x] Test on sample PRs

---

## Phase 2: Multi-Agent Core ✅

### 2.1 Coordinator Agent
- [x] Orchestrates multiple specialist agents
- [x] Parallel execution of agents
- [x] Aggregates and deduplicates findings
- [x] Prioritizes issues by severity
- [x] Consensus-based approval decision

### 2.2 Security Agent
- [x] OWASP vulnerability detection
- [x] Secrets/credential scanning
- [x] Security-specific prompts and rules
- [ ] Dependency vulnerability awareness (future)

### 2.3 Agent Communication
- [x] Define message format between agents (Finding, ReviewResult models)
- [x] Implement handoff protocol via Coordinator
- [x] Structured logging for debugging

---

## Phase 3: Advanced Features (In Progress)

### 3.1 CLI ✅
- [x] Create `cli.py` module
- [x] `codecourt review <diff-file>` command
- [x] `codecourt review --stdin` for piped input
- [x] `codecourt review --repo <path>` for local repos
- [x] Provider/model selection flags
- [x] Multiple output formats (rich, json, markdown)
- [x] `codecourt providers` command
- [x] `codecourt parse` command (debugging)
- [ ] Config file support (.codecourtrc)

### 3.2 Debate System
- [ ] Defender agent: argues FOR the code changes
- [ ] Prosecutor agent: argues AGAINST / finds problems
- [ ] Judge agent: synthesizes and makes final call
- [ ] Structured debate rounds

### 3.3 Auto-Fix Agent
- [ ] Generate fix suggestions as patches
- [ ] Validate patches apply cleanly
- [ ] Output unified diff format

---

## Blockers / Open Questions

_None currently_

---

## Next Session: Start Here

> **Continue with:** Phase 3.2 - Debate System
> 
> Implement the debate-based review system:
> - Defender agent: argues FOR the code changes
> - Prosecutor agent: argues AGAINST / finds problems  
> - Judge agent: synthesizes arguments, delivers verdict
> - Structured debate rounds (2-3 exchanges)
