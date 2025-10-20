"""Tests for command parser module."""

from nuha.core.command_parser import CommandParser


def test_parse_simple_command() -> None:
    """Test parsing a simple command."""
    parser = CommandParser()
    result = parser.parse_command("ls -la /home")

    assert result["base_command"] == "ls"
    assert "-la" in result["flags"]
    assert "/home" in result["args"]
    assert result["is_sudo"] is False


def test_parse_sudo_command() -> None:
    """Test parsing a sudo command."""
    parser = CommandParser()
    result = parser.parse_command("sudo apt install vim")

    assert result["base_command"] == "sudo"
    assert result["is_sudo"] is True


def test_parse_piped_command() -> None:
    """Test parsing a piped command."""
    parser = CommandParser()
    result = parser.parse_command("cat file.txt | grep error")

    assert result["is_piped"] is True


def test_dangerous_command_detection() -> None:
    """Test dangerous command detection."""
    parser = CommandParser()

    is_dangerous, _ = parser.is_dangerous("rm -rf /")
    assert is_dangerous is True

    is_dangerous, _ = parser.is_dangerous("ls -la")
    assert is_dangerous is False


def test_error_type_detection() -> None:
    """Test error type detection."""
    parser = CommandParser()

    error_type = parser.detect_error_type("bash: command not found")
    assert error_type == "command_not_found"

    error_type = parser.detect_error_type("Permission denied")
    assert error_type == "permission_denied"


def test_command_category() -> None:
    """Test command categorization."""
    parser = CommandParser()

    assert parser.get_command_category("ls -la") == "file_operations"
    assert parser.get_command_category("git status") == "version_control"
    assert parser.get_command_category("grep pattern file") == "text_processing"
    assert parser.get_command_category("ping google.com") == "network"


def test_analyze_command_chain() -> None:
    """Test command chain analysis."""
    parser = CommandParser()

    analysis = parser.analyze_command_chain("ls | grep test")
    assert analysis["has_pipe"] is True
    assert len(analysis["commands"]) == 2

    analysis = parser.analyze_command_chain("echo hello > file.txt")
    assert analysis["has_redirect"] is True
