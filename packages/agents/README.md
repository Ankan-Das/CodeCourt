# CodeCourt - Python Agents

Core Python package containing the multi-agent system for PR reviews.

## Installation

```bash
# Development installation
pip install -e ".[dev]"
```

## Structure

```
src/codecourt/
├── agents/              # Agent implementations
│   ├── base.py          # Base agent class
│   ├── code_reviewer.py # General code review agent
│   ├── security.py      # Security/OWASP scanning agent
│   ├── coordinator.py   # Orchestrates multiple agents
│   └── models.py        # Finding, ReviewResult, Severity, etc.
├── providers/           # LLM provider abstractions
│   ├── base.py          # Provider interface
│   ├── openai.py        # OpenAI implementation
│   ├── anthropic.py     # Anthropic implementation
│   ├── ollama.py        # Ollama (local) implementation
│   └── factory.py       # Provider factory with config
├── tools/               # Utility tools
│   ├── git_diff.py      # Git diff parsing
│   ├── file_reader.py   # File content reader
│   └── models.py        # DiffFile, DiffHunk models
└── config.py            # Configuration management (pydantic-settings)
```

## Usage

```python
from codecourt.config import settings
from codecourt.providers import create_provider
from codecourt.agents.coordinator import ReviewCoordinator
from codecourt.tools.git_diff import parse_git_diff

# Create LLM provider
provider = create_provider(settings.default_provider)

# Parse a diff
diff_content = open("changes.diff").read()
diff_files = parse_git_diff(diff_content)

# Run coordinated review
coordinator = ReviewCoordinator(provider)
result = await coordinator.review(diff_files)

print(f"Approval: {result.approval}")
print(f"Findings: {len(result.findings)}")
```

## Implemented Agents

| Agent | Description |
|-------|-------------|
| **CodeReviewAgent** | General code quality, style, bugs, improvements |
| **SecurityAgent** | OWASP vulnerabilities, secrets detection |
| **ReviewCoordinator** | Orchestrates agents, deduplicates findings, consensus approval |

## Planned Agents

| Agent | Description |
|-------|-------------|
| **DefenderAgent** | Argues FOR the code changes |
| **ProsecutorAgent** | Challenges and finds problems |
| **JudgeAgent** | Synthesizes debate, delivers verdict |
| **AutoFixAgent** | Generates patches for issues |
