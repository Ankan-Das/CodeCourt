"""Factory for creating LLM providers."""

from codecourt.providers.anthropic import AnthropicProvider
from codecourt.providers.base import BaseLLMProvider
from codecourt.providers.ollama import OllamaProvider
from codecourt.providers.openai import OpenAIProvider

PROVIDERS: dict[str, type[BaseLLMProvider]] = {
    "openai": OpenAIProvider,
    "anthropic": AnthropicProvider,
    "ollama": OllamaProvider,
}


def get_provider(name: str, **kwargs) -> BaseLLMProvider:
    """
    Get an LLM provider by name.

    Args:
        name: "openai", "anthropic", or "ollama"

    Example:
        >>> provider = get_provider("ollama")
        >>> response = await provider.complete([{"role": "user", "content": "Hi"}])
    """
    name = name.lower()
    if name not in PROVIDERS:
        available = ", ".join(PROVIDERS.keys())
        raise ValueError(f"Unknown provider: {name}. Available: {available}")
    return PROVIDERS[name](**kwargs)


def list_providers() -> list[str]:
    """List all available provider names."""
    return list(PROVIDERS.keys())
