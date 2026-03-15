# CodeCourt

A multi-agent system for automated pull request reviews with auto-fix capabilities, security scanning, and a debate-based review process — where your code faces trial by AI.

> *"Every PR deserves a fair trial."*

## Features

- **The Court**: Multi-agent architecture with specialized roles
- **The Defender**: Advocates for the code changes
- **The Prosecutor**: Challenges and finds issues  
- **The Judge**: Synthesizes arguments and delivers the verdict
- **Auto-Fix**: Automatically generates patches for identified issues
- **Security Bailiff**: OWASP-aware vulnerability detection
- **Multiple LLM Support**: Works with OpenAI, Anthropic, and local models (Ollama)

## Project Status

🟢 **Phase 2 Complete** — Core review pipeline is working!

### What's Working
- ✅ LLM Providers (OpenAI, Anthropic, Ollama)
- ✅ Git diff parsing and file tools
- ✅ Code Review Agent
- ✅ Security Agent (OWASP, secrets detection)
- ✅ Coordinator (parallel execution, deduplication, consensus)
- ✅ CLI (`codecourt review`, `codecourt providers`, `codecourt parse`)

### Coming Next
- ⏳ Debate system (Defender/Prosecutor/Judge)
- ⏳ Auto-Fix agent
- ⏳ GitHub Action

See [docs/PROGRESS.md](docs/PROGRESS.md) for detailed status.

## Quick Start

```bash
# Install
cd packages/agents
pip install -e .

# Review a diff file
codecourt review changes.diff

# Review from git diff
git diff | codecourt review --stdin

# Review uncommitted changes
codecourt review --repo .

# Use a specific provider
codecourt review --provider ollama --repo .
```

## How It Works

```
┌─────────────────────────────────────────────────────────────────┐
│                         YOUR PR                                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  PHASE 1: Security Check                                        │
│  ┌─────────────┐                                                │
│  │  Security   │ → Scans for vulnerabilities, secrets           │
│  │   Bailiff   │ → Flags critical issues                        │
│  └─────────────┘                                                │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  PHASE 2: The Debate                                            │
│  ┌──────────┐    ┌────────────┐    ┌─────────┐                 │
│  │ Defender │ ←→ │ Prosecutor │ ←→ │  Judge  │                 │
│  └──────────┘    └────────────┘    └─────────┘                 │
│       │                │                │                       │
│  "Code is good    "But this has    "Verdict:                   │
│   because..."      these issues"    approve/reject"            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  PHASE 3: Auto-Fix                                              │
│  ┌─────────────┐                                                │
│  │  Auto-Fix   │ → Takes issues from above                      │
│  │   Agent     │ → Generates patches                            │
│  └─────────────┘ → Validates & outputs                          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  OUTPUT                                                          │
│  • PR Comment with verdict                                       │
│  • Inline comments on specific lines                            │
│  • Suggested fix patches                                        │
│  • (Optional) Auto-commit fixes                                 │
└─────────────────────────────────────────────────────────────────┘
```

## The Agents

| Agent | Role | What It Does |
|-------|------|--------------|
| **Security Bailiff** | First line of defense | Scans for secrets, OWASP vulnerabilities, dependency issues |
| **Defender** | Advocates FOR the code | Presents arguments why the changes are good |
| **Prosecutor** | Challenges the code | Finds bugs, style issues, potential problems |
| **Judge** | Final decision maker | Weighs both sides, delivers verdict with reasoning |
| **Auto-Fix** | Remediation | Generates actual code patches for identified issues |

## Development

See [docs/ROADMAP.md](docs/ROADMAP.md) for the development plan.

## License

MIT
