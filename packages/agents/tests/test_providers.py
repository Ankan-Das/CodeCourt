"""Tests for LLM providers."""

import pytest

from codecourt.providers import (
    AnthropicProvider,
    BaseLLMProvider,
    OllamaProvider,
    OpenAIProvider,
    get_provider,
    list_providers,
)


class TestProviderFactory:
    """Tests for the provider factory."""

    def test_list_providers(self) -> None:
        """Test that all providers are listed."""
        providers = list_providers()
        assert "openai" in providers
        assert "anthropic" in providers
        assert "ollama" in providers

    def test_get_openai_provider(self) -> None:
        """Test getting OpenAI provider."""
        provider = get_provider("openai")
        assert isinstance(provider, OpenAIProvider)
        assert isinstance(provider, BaseLLMProvider)
        assert provider.name == "openai"

    def test_get_anthropic_provider(self) -> None:
        """Test getting Anthropic provider."""
        provider = get_provider("anthropic")
        assert isinstance(provider, AnthropicProvider)
        assert provider.name == "anthropic"

    def test_get_ollama_provider(self) -> None:
        """Test getting Ollama provider."""
        provider = get_provider("ollama")
        assert isinstance(provider, OllamaProvider)
        assert provider.name == "ollama"

    def test_get_provider_case_insensitive(self) -> None:
        """Test that provider names are case-insensitive."""
        assert isinstance(get_provider("OpenAI"), OpenAIProvider)
        assert isinstance(get_provider("ANTHROPIC"), AnthropicProvider)
        assert isinstance(get_provider("Ollama"), OllamaProvider)

    def test_get_unknown_provider_raises(self) -> None:
        """Test that unknown provider raises ValueError."""
        with pytest.raises(ValueError, match="Unknown provider"):
            get_provider("unknown_provider")


class TestProviderInterface:
    """Tests to verify all providers implement the interface correctly."""

    @pytest.mark.parametrize("provider_name", ["openai", "anthropic", "ollama"])
    def test_provider_has_name(self, provider_name: str) -> None:
        """Test that all providers have a name property."""
        provider = get_provider(provider_name)
        assert hasattr(provider, "name")
        assert isinstance(provider.name, str)

    @pytest.mark.parametrize("provider_name", ["openai", "anthropic", "ollama"])
    def test_provider_has_complete_method(self, provider_name: str) -> None:
        """Test that all providers have a complete method."""
        provider = get_provider(provider_name)
        assert hasattr(provider, "complete")
        assert callable(provider.complete)

    @pytest.mark.parametrize("provider_name", ["openai", "anthropic", "ollama"])
    def test_provider_has_complete_json_method(self, provider_name: str) -> None:
        """Test that all providers have a complete_json method."""
        provider = get_provider(provider_name)
        assert hasattr(provider, "complete_json")
        assert callable(provider.complete_json)
