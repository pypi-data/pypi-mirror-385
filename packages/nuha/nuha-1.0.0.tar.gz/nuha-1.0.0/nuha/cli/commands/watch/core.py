"""Core command watcher functionality."""

import os
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

import psutil

from nuha.core.capture import parse_legacy_history, read_events


class CommandWatcher:
    """Monitors terminal commands and records them."""

    def __init__(self, config_dir: Path):
        """Initialize the command watcher."""
        self.config_dir = config_dir
        self.watch_file = config_dir / "watch_history.json"
        self.watch_jsonl_file = config_dir / "watch_history.jsonl"
        self.pid_file = config_dir / "watch.pid"
        self.is_running = False
        self.process: subprocess.Popen[Any] | None = None

    def detect_shell(self) -> str:
        """Detect the current shell."""
        shell = os.environ.get("SHELL", "")

        # Try to get the actual shell by walking up the process tree
        try:
            # Get current process PID
            current_pid = os.getpid()

            # Walk up the process tree to find a shell
            for _ in range(5):  # Check up to 5 levels up
                try:
                    # Get parent PID
                    parent_pid = (
                        os.popen(f"ps -p {current_pid} -o ppid=").read().strip()
                    )
                    if not parent_pid or parent_pid == current_pid:
                        break

                    # Get parent command
                    parent_cmd = (
                        os.popen(f"ps -p {parent_pid} -o comm=").read().strip().lower()
                    )

                    # Check if it's a shell
                    if parent_cmd in [
                        "bash",
                        "zsh",
                        "sh",
                        "ksh",
                        "fish",
                        "csh",
                        "tcsh",
                    ]:
                        return parent_cmd

                    # Check if it's a terminal or VS Code (skip these)
                    if any(
                        x in parent_cmd for x in ["code", "vscode", "terminal", "iterm"]
                    ):
                        current_pid = int(parent_pid)
                        continue

                    # Move up to parent
                    current_pid = int(parent_pid)

                except (ValueError, OSError, AttributeError):
                    break

        except Exception:
            pass

        # Fallback to SHELL environment variable
        if shell:
            # Extract just the shell name from the path
            shell_name = Path(shell).name.lower()
            if shell_name in ["bash", "zsh", "sh", "ksh", "fish", "csh", "tcsh"]:
                return shell_name

        return "bash"  # Default fallback

    def is_watch_active(self) -> bool:
        """Check if watch process is currently running."""
        if not self.pid_file.exists():
            return False

        try:
            with open(self.pid_file) as f:
                pid = int(f.read().strip())

            # Check if process is still running
            return psutil.pid_exists(pid)
        except (ValueError, FileNotFoundError, psutil.NoSuchProcess):
            return False

    def is_monitoring_active(self) -> bool:
        """Check if watch monitoring is active in the current shell session."""
        # Check if the environment variable is set (indicates hooks are active)
        return os.environ.get("NUHA_WATCH_ACTIVE") == "1"

    def start_watching(self) -> None:
        """Start the command monitoring process."""
        if self.is_watch_active():
            from .display import console

            console.print("[yellow]⚠️  Watch is already running[/yellow]")
            return

        from .display import console

        console.print("[blue]🔍 Starting command watcher...[/blue]")

        # Start monitoring in background
        self.process = subprocess.Popen(
            [sys.executable, "-c", self._monitor_script()],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )

        # Save PID
        with open(self.pid_file, "w") as f:
            f.write(str(self.process.pid))

        console.print("[green]✅ Watch started successfully[/green]")
        console.print("[dim]Commands will now be recorded automatically[/dim]")

    def stop_watching(self) -> None:
        """Stop the command monitoring process."""
        if not self.is_watch_active():
            from .display import console

            console.print("[yellow]⚠️  Watch is not running[/yellow]")
            return

        from .display import console

        try:
            with open(self.pid_file) as f:
                pid = int(f.read().strip())

            # Terminate the process
            os.kill(pid, signal.SIGTERM)

            # Wait a bit and force kill if still running
            time.sleep(1)
            if psutil.pid_exists(pid):
                os.kill(pid, signal.SIGKILL)

            # Remove PID file
            self.pid_file.unlink(missing_ok=True)

            console.print("[green]✅ Watch stopped successfully[/green]")
        except (
            ValueError,
            FileNotFoundError,
            psutil.NoSuchProcess,
            ProcessLookupError,
        ):
            console.print("[yellow]⚠️  Watch process not found[/yellow]")
            self.pid_file.unlink(missing_ok=True)

    def get_status(self) -> None:
        """Display current watch status."""
        from .display import console, show_status_table

        if self.is_watch_active():
            console.print("[green]🟢 Watch is currently running[/green]")

            # Show recent commands
            commands = self.get_recent_commands(5)
            if commands:
                show_status_table(commands)
            else:
                console.print("[dim]No commands recorded yet[/dim]")
        else:
            console.print("[red]🔴 Watch is not running[/red]")
            console.print("[dim]Run 'nuha watch --start' to begin monitoring[/dim]")

    def get_recent_commands(self, limit: int = 10) -> list[dict[str, Any]]:
        """Get recent commands from watch history."""
        # Try to read from JSONL format first (new format)
        if self.watch_jsonl_file.exists():
            # Read more events to ensure we get complete cmd/result pairs
            # For small limits, we need to read more events to find complete pairs
            read_limit = max(limit * 4, 20)  # Read at least 20 events or 4x the limit
            events = read_events(str(self.watch_jsonl_file), read_limit)

            # Convert events to command format
            commands: list[dict[str, Any]] = []
            current_cmd: dict[str, Any] | None = None

            for event in events:
                if event.get("type") == "cmd" and event.get("data"):
                    current_cmd = {
                        "command": event["data"][0] if event["data"] else "",
                        "timestamp": event.get("timestamp", ""),
                        "exit_code": None,
                        "cwd": event.get("cwd", ""),
                    }
                elif (
                    event.get("type") == "result" and current_cmd and event.get("data")
                ):
                    current_cmd["exit_code"] = (
                        int(event["data"][0])
                        if event["data"] and event["data"][0].isdigit()
                        else None
                    )
                    commands.append(current_cmd)
                    current_cmd = None

            # If no commands from JSONL, try legacy format
            if not commands and self.watch_file.exists():
                commands = parse_legacy_history(self.watch_file)
        else:
            # Fallback to legacy format
            commands = parse_legacy_history(self.watch_file)

        # Limit commands
        return commands[-limit:] if len(commands) > limit else commands

    def get_last_command(self) -> dict[str, Any] | None:
        """Get the last recorded command."""
        commands = self.get_recent_commands(1)
        return commands[-1] if commands else None

    def _monitor_script(self) -> str:
        """Generate a simple monitoring script for subprocess."""
        from .monitor import generate_monitor_script

        return generate_monitor_script(self.watch_file, self.pid_file)
