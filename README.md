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

🚧 **Under Development**

See [docs/PROGRESS.md](docs/PROGRESS.md) for current status.

## Quick Start

```bash
# Install Python dependencies
cd packages/agents
pip install -e .

# Install CLI dependencies
cd packages/cli
npm install
```

## Architecture

```
                    ┌─────────────────┐
                    │   Clerk         │  ← CLI / GitHub Action
                    │   (Intake)      │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │   Bailiff       │  ← Security Scanner
                    │   (Security)    │
                    └────────┬────────┘
                             │
         ┌───────────────────┼───────────────────┐
         ▼                   ▼                   ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│    Defender     │ │   Prosecutor    │ │   Code Review   │
│  (Advocates)    │ │  (Challenges)   │ │    (Analyzes)   │
└────────┬────────┘ └────────┬────────┘ └────────┬────────┘
         │                   │                   │
         └───────────────────┼───────────────────┘
                             ▼
                    ┌─────────────────┐
                    │     Judge       │  ← Final Verdict
                    │   (Decides)     │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │   Auto-Fix      │  ← Generates Patches
                    │   (Remediation) │
                    └─────────────────┘
```

## Development

See [docs/ROADMAP.md](docs/ROADMAP.md) for the development plan.

## License

MIT
