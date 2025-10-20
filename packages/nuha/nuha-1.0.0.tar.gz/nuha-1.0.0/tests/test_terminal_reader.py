"""Tests for terminal reader module."""

from nuha.core.terminal_reader import TerminalReader


def test_detect_shell() -> None:
    """Test shell detection."""
    reader = TerminalReader()
    assert reader.shell in ["bash", "zsh", "fish", "csh", "tcsh", "unknown"]


def test_get_working_directory() -> None:
    """Test getting working directory."""
    reader = TerminalReader()
    cwd = reader.get_working_directory()
    assert cwd is not None
    assert len(cwd) > 0


def test_get_context() -> None:
    """Test getting terminal context."""
    reader = TerminalReader()
    context = reader.get_context()

    assert "shell" in context
    assert "cwd" in context
    assert "recent_commands" in context
    assert "user" in context
    assert "home" in context

    assert isinstance(context["recent_commands"], list)
