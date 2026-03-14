"""Factory for creating LLM providers."""

from codecourt.providers.anthropic import AnthropicProvider
from codecourt.providers.base import BaseLLMProvider
from codecourt.providers.ollama import OllamaProvider
from codecourt.providers.openai import OpenAIProvider

# Registry of available providers
PROVIDERS: dict[str, type[BaseLLMProvider]] = {
    "openai": OpenAIProvider,
    "anthropic": AnthropicProvider,
    "ollama": OllamaProvider,
}


def get_provider(name: str, **kwargs) -> BaseLLMProvider:
    """
    Get an LLM provider by name.

    Args:
        name: Provider name ("openai", "anthropic", or "ollama")
        **kwargs: Additional arguments passed to the provider constructor

    Returns:
        An instance of the requested provider.

    Raises:
        ValueError: If the provider name is not recognized.

    Example:
        >>> provider = get_provider("openai")
        >>> response = await provider.complete([{"role": "user", "content": "Hello!"}])

        >>> # With custom settings
        >>> provider = get_provider("ollama", host="http://remote-server:11434")
    """
    name = name.lower()

    if name not in PROVIDERS:
        available = ", ".join(PROVIDERS.keys())
        raise ValueError(f"Unknown provider: {name}. Available: {available}")

    return PROVIDERS[name](**kwargs)


def list_providers() -> list[str]:
    """List all available provider names."""
    return list(PROVIDERS.keys())
