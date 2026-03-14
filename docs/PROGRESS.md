# CodeCourt - Progress Tracker

## Current Status

**Phase:** 1 - Foundation  
**Checkpoint:** 1.1 - Project Setup  
**Last Updated:** 2026-03-14

---

## Phase 1: Foundation

### 1.1 Project Setup
- [x] Initialize monorepo structure
- [ ] Set up Python package with pyproject.toml
- [ ] Set up TypeScript package with package.json
- [x] Create docs/ROADMAP.md, PROGRESS.md, devlog/

### 1.2 LLM Provider Abstraction
- [ ] Create base provider interface (`providers/base.py`)
- [ ] Implement OpenAI provider
- [ ] Implement Anthropic provider
- [ ] Implement Ollama provider
- [ ] Add provider factory with config

### 1.3 Git/Diff Tools
- [ ] Parse git diff output
- [ ] Extract changed files and hunks
- [ ] Read file contents with context
- [ ] Create patch objects

### 1.4 Basic Code Review Agent
- [ ] Single agent that reviews a diff
- [ ] Returns structured feedback (file, line, severity, message)
- [ ] Test on sample PRs

---

## Blockers / Open Questions

_None currently_

---

## Next Session: Start Here

> **Continue with:** Checkpoint 1.1 - Project Setup
> 
> Set up Python package (pyproject.toml) and TypeScript package (package.json)
