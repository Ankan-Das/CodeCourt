# CodeCourt - Development Roadmap

## Overview

Multi-agent PR review system with auto-fix, security scanning, and debate features.

---

## Phase 1: Foundation

### 1.1 Project Setup
- [ ] Initialize monorepo structure
- [ ] Set up Python package with pyproject.toml
- [ ] Set up TypeScript package with package.json
- [ ] Create docs/ROADMAP.md, PROGRESS.md, devlog/

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

## Phase 2: Multi-Agent Core

### 2.1 Coordinator Agent
- [ ] Orchestrates multiple specialist agents
- [ ] Aggregates and deduplicates findings
- [ ] Prioritizes issues by severity

### 2.2 Security Agent
- [ ] OWASP vulnerability detection
- [ ] Secrets/credential scanning
- [ ] Dependency vulnerability awareness
- [ ] Security-specific prompts and rules

### 2.3 Agent Communication
- [ ] Define message format between agents
- [ ] Implement handoff protocol
- [ ] Add logging for debugging agent interactions

---

## Phase 3: Advanced Features

### 3.1 Debate System
- [ ] Advocate agent: argues FOR the code changes
- [ ] Critic agent: argues AGAINST / finds problems
- [ ] Judge agent: synthesizes and makes final call
- [ ] Structured debate rounds (2-3 exchanges)

### 3.2 Auto-Fix Agent
- [ ] Generate fix suggestions as patches
- [ ] Validate patches apply cleanly
- [ ] Run basic syntax checks on fixes
- [ ] Output unified diff format

### 3.3 Review Report Generator
- [ ] Aggregate all agent outputs
- [ ] Generate markdown summary
- [ ] Include confidence scores
- [ ] Format for PR comment

---

## Phase 4: CLI + GitHub Action

### 4.1 FastAPI Server
- [ ] REST API for triggering reviews
- [ ] Async processing with status polling
- [ ] Webhook support for GitHub

### 4.2 TypeScript CLI
- [ ] `pr-review analyze <repo> <pr-number>`
- [ ] `pr-review review --local` (for local diffs)
- [ ] Config file support (.pr-reviewrc)

### 4.3 GitHub Action
- [ ] action.yml with inputs
- [ ] Trigger on PR open/update
- [ ] Post comments via GitHub API
- [ ] Optional auto-fix commit

---

## Phase 5: Polish

### 5.1 Testing
- [ ] Unit tests for each agent
- [ ] Integration tests with mock LLMs
- [ ] End-to-end test on real repo

### 5.2 Documentation
- [ ] README with setup instructions
- [ ] Architecture documentation
- [ ] Demo GIFs/screenshots

### 5.3 Demo & Deploy
- [ ] Deploy to a sample repo
- [ ] Record demo video
- [ ] Write blog post / case study
