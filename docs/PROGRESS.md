# CodeCourt - Progress Tracker

## Current Status

**Phase:** 2 - Multi-Agent Core (Complete)  
**Next Up:** Phase 3 - Advanced Features (CLI, Debate System)  
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

### 3.1 CLI
- [ ] Create `cli.py` module
- [ ] `codecourt review <diff-file>` command
- [ ] `codecourt review --repo <path>` for local repos
- [ ] Config file support

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

> **Continue with:** Phase 3.1 - CLI
> 
> Build the CLI module (`cli.py`) to make CodeCourt usable from the command line.
> The entrypoint is already defined in pyproject.toml as `codecourt = "codecourt.cli:main"`
