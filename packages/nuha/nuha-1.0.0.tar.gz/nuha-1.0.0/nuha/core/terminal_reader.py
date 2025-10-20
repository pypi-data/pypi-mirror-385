"""Terminal history reader for different shells."""

import contextlib
import os
import subprocess
from pathlib import Path


class TerminalReader:
    """Read terminal history from various shells."""

    def __init__(self, shell: str | None = None, history_limit: int = 50):
        """Initialize terminal reader."""
        self.shell = shell or self._detect_shell()
        self.history_limit = history_limit

    @staticmethod
    def _detect_shell() -> str:
        """Detect the current shell."""
        shell = os.environ.get("SHELL", "")
        if "bash" in shell:
            return "bash"
        elif "zsh" in shell:
            return "zsh"
        elif "fish" in shell:
            return "fish"
        elif "tcsh" in shell or "csh" in shell:
            return "csh"
        return "unknown"

    def _get_history_file(self) -> Path | None:
        """Get the history file path for the current shell."""
        home = Path.home()

        history_files = {
            "bash": home / ".bash_history",
            "zsh": home / ".zsh_history",
            "fish": home / ".local" / "share" / "fish" / "fish_history",
            "csh": home / ".history",
            "tcsh": home / ".history",
        }

        return history_files.get(self.shell)

    def get_history(self, limit: int | None = None) -> list[str]:
        """Get command history."""
        limit = limit or self.history_limit

        # For zsh, force history to be written to file first
        if self.shell == "zsh":
            with contextlib.suppress(Exception):
                subprocess.run(
                    ["zsh", "-c", "fc -W"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )

        # Try reading from file first (more reliable for recent history)
        history_file = self._get_history_file()
        if history_file and history_file.exists():
            file_history = self._read_history_file(history_file, limit)
            if file_history:
                return file_history

        # Fallback to shell-specific commands (may not have current session history)
        shell_history = self._read_history_command(limit)
        if shell_history:
            return shell_history

        return []

    def _read_history_file(self, history_file: Path, limit: int) -> list[str]:
        """Read history from file."""
        try:
            with open(history_file, encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()

            # Parse based on shell format
            if self.shell == "zsh":
                # zsh format: : timestamp:0;command
                commands = []
                for line in lines:
                    if line.startswith(":"):
                        parts = line.split(";", 1)
                        if len(parts) > 1:
                            commands.append(parts[1].strip())
                    else:
                        commands.append(line.strip())
            elif self.shell == "fish":
                # fish format: - cmd: command\n  when: timestamp
                commands = []
                for line in lines:
                    if line.strip().startswith("- cmd:"):
                        cmd = line.split("- cmd:", 1)[1].strip()
                        commands.append(cmd)
            else:
                # bash, csh: simple line-by-line format
                commands = [line.strip() for line in lines if line.strip()]

            # Return last N commands
            return commands[-limit:] if len(commands) > limit else commands

        except Exception as e:
            print(f"Warning: Could not read history file: {e}")
            return []

    def _read_history_command(self, limit: int) -> list[str]:
        """Read history using shell command."""
        try:
            if self.shell == "bash":
                result = subprocess.run(
                    ["bash", "-c", f"history {limit}"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
            elif self.shell == "zsh":
                result = subprocess.run(
                    ["zsh", "-c", f"history -{limit}"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
            elif self.shell == "fish":
                result = subprocess.run(
                    ["fish", "-c", f"history --max={limit}"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
            else:
                return []

            if result.returncode == 0:
                lines = result.stdout.strip().split("\n")
                # Remove line numbers from history output
                commands = []
                for line in lines:
                    # Skip empty lines
                    if not line.strip():
                        continue
                    # Remove leading numbers (bash format: "  123  command")
                    parts = line.strip().split(None, 1)
                    if len(parts) > 1 and parts[0].isdigit():
                        commands.append(parts[1])
                    else:
                        commands.append(line.strip())
                return commands

        except Exception as e:
            print(f"Warning: Could not read history via command: {e}")

        return []

    def get_last_command(self) -> str | None:
        """Get the last executed command (excluding the current nuha command)."""
        history = self.get_history(
            limit=10
        )  # Get more commands to find the previous one
        if not history:
            return None

        # Filter out nuha commands and internal fc commands
        for cmd in reversed(history):
            if (
                not cmd.startswith("nuha")
                and not cmd.startswith("uv run nuha")
                and cmd != "fc -W"
            ):
                return cmd

        # If no suitable commands found, return the second-to-last command
        return history[-2] if len(history) > 1 else None

    def get_last_failed_command(self) -> tuple[str, str | None] | None:
        """
        Get the last failed command and its error output.
        Returns (command, error_output) tuple or None.
        """
        # This is a simplified version - in production, you'd need to track
        # command exit codes and output, which requires shell integration
        last_cmd = self.get_last_command()
        if last_cmd:
            # Try to detect common error patterns
            return (last_cmd, None)
        return None

    def get_working_directory(self) -> str:
        """Get current working directory."""
        return os.getcwd()

    def get_context(self) -> dict[str, str | list[str]]:
        """Get terminal context information."""
        return {
            "shell": self.shell,
            "cwd": self.get_working_directory(),
            "recent_commands": self.get_history(limit=10),
            "user": os.environ.get("USER", "unknown"),
            "home": str(Path.home()),
        }
