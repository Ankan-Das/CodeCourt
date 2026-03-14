"""Tests for configuration management."""

import pytest


def test_settings_defaults() -> None:
    """Test that settings have sensible defaults."""
    from codecourt.config import Settings

    settings = Settings()
    assert settings.api_port == 8000
    assert settings.log_level == "INFO"
    assert settings.ollama_host == "http://localhost:11434"


def test_settings_can_be_imported() -> None:
    """Test that settings singleton can be imported."""
    from codecourt import settings

    assert settings is not None
