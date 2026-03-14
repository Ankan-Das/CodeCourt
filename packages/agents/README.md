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
├── agents/          # Agent implementations
│   ├── base.py      # Base agent class
│   ├── defender.py  # Advocates for code changes
│   ├── prosecutor.py # Challenges code changes
│   ├── judge.py     # Final verdict
│   └── security.py  # Security scanning
├── providers/       # LLM provider abstractions
│   ├── base.py      # Provider interface
│   ├── openai.py    # OpenAI implementation
│   ├── anthropic.py # Anthropic implementation
│   └── ollama.py    # Ollama (local) implementation
├── tools/           # Utility tools
│   ├── git_diff.py  # Git diff parsing
│   ├── file_reader.py
│   └── patch_applier.py
└── config.py        # Configuration management
```

## Usage

```python
from codecourt import settings
from codecourt.agents import BaseAgent

# Configuration is loaded from environment variables
print(settings.openai_api_key)
```
