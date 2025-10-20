"""Tests for configuration module."""

import pytest

from nuha.core.config import AIConfig, AIProvider, Config


def test_default_config() -> None:
    """Test default configuration values."""
    config = Config()

    assert config.ai.provider == AIProvider.ZHIPUAI
    assert config.ai.model == "glm-4.5-flash"
    assert config.ai.temperature == 0.3
    assert config.ai.max_tokens == 2000

    assert config.terminal.history_limit == 50
    assert config.terminal.auto_analyze is True
    assert config.terminal.include_context is True

    assert config.output.format == "rich"
    assert config.output.color is True
    assert config.output.verbose is False


def test_ai_provider_enum() -> None:
    """Test AI provider enum values."""
    assert AIProvider.ZHIPUAI.value == "zhipuai"
    assert AIProvider.OPENAI.value == "openai"
    assert AIProvider.CLAUDE.value == "claude"
    assert AIProvider.DEEPSEEK.value == "deepseek"


def test_set_api_key() -> None:
    """Test setting API keys."""
    config = Config()

    config.set_api_key(AIProvider.OPENAI, "test-key-123")
    assert config.openai_api_key == "test-key-123"

    config.set_api_key(AIProvider.CLAUDE, "claude-key-456")
    assert config.anthropic_api_key == "claude-key-456"


def test_get_api_key() -> None:
    """Test getting API keys."""
    config = Config()

    config.zhipuai_api_key = "zhipu-key"
    assert config.get_api_key(AIProvider.ZHIPUAI) == "zhipu-key"

    config.openai_api_key = "openai-key"
    assert config.get_api_key(AIProvider.OPENAI) == "openai-key"


def test_reset_config() -> None:
    """Test configuration reset."""
    config = Config()

    # Modify config
    config.ai.temperature = 0.8
    config.terminal.history_limit = 100

    # Reset
    config.reset()

    # Check defaults
    assert config.ai.temperature == 0.3
    assert config.terminal.history_limit == 50


def test_config_validation() -> None:
    """Test configuration validation."""
    # Temperature should be between 0 and 2
    with pytest.raises(ValueError):
        AIConfig(temperature=3.0)

    # Max tokens should be positive
    with pytest.raises(ValueError):
        AIConfig(max_tokens=-1)

    # Valid values should work
    config = AIConfig(temperature=1.0, max_tokens=1000)
    assert config.temperature == 1.0
    assert config.max_tokens == 1000
