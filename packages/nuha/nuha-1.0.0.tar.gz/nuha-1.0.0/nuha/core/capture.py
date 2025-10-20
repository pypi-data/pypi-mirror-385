"""Capture module for logging terminal commands."""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


def capture_event(event_type: str, *args: Any) -> None:
    """Capture a terminal event and log it to the appropriate file."""
    # Filter out nuha commands to avoid recording them
    if event_type == "cmd" and args:
        command = args[0]
        if (
            command.startswith("nuha")
            or command.startswith("uv run nuha")
            or command.startswith("history")
            or command.startswith("fc -")
        ):
            return  # Skip recording nuha commands and history commands

    # Try to get log path from environment, fall back to config directory
    log_path = os.environ.get("NUHA_WATCH_LOG")
    if not log_path:
        # Fallback to user's config directory
        config_dir = Path.home() / ".nuha"
        config_dir.mkdir(exist_ok=True)
        log_path = str(config_dir / "watch_history.jsonl")

    event = {
        "timestamp": datetime.now().isoformat(),
        "type": event_type,
        "data": args,
        "pid": os.getpid(),
        "cwd": os.getcwd(),
    }

    try:
        with open(log_path, "a") as f:
            f.write(json.dumps(event) + "\n")
    except OSError:
        # Silent fail to avoid breaking shell functionality
        pass


def read_events(log_path: str, limit: int = 100) -> list[dict[str, Any]]:
    """Read events from the log file."""
    if not os.path.exists(log_path):
        return []

    events = []
    try:
        with open(log_path) as f:
            lines = f.readlines()
            # Get last N lines (more efficient for large files)
            for line in lines[-limit:]:
                try:
                    events.append(json.loads(line.strip()))
                except (json.JSONDecodeError, ValueError):
                    continue
    except OSError:
        pass

    return events


def parse_legacy_history(watch_file: Path) -> list[dict[str, Any]]:
    """Parse legacy JSON array format for backward compatibility."""
    if not watch_file.exists():
        return []

    try:
        with open(watch_file) as f:
            commands = json.load(f)
        if isinstance(commands, list):
            return commands
    except (json.JSONDecodeError, FileNotFoundError, ValueError):
        pass

    return []


def convert_legacy_to_jsonl(legacy_file: Path, jsonl_file: Path) -> None:
    """Convert legacy JSON array format to JSONL format."""
    commands = parse_legacy_history(legacy_file)
    if not commands:
        return

    try:
        with open(jsonl_file, "w") as f:
            for cmd in commands:
                # Convert to new event format
                event = {
                    "timestamp": cmd.get("timestamp", datetime.now().isoformat()),
                    "type": "cmd",
                    "data": [cmd.get("command", "")],
                    "pid": os.getpid(),
                    "cwd": cmd.get("cwd", os.getcwd()),
                }
                f.write(json.dumps(event) + "\n")

                # Add result event if exit code exists
                if cmd.get("exit_code") is not None:
                    result_event = {
                        "timestamp": cmd.get("timestamp", datetime.now().isoformat()),
                        "type": "result",
                        "data": [str(cmd.get("exit_code"))],
                        "pid": os.getpid(),
                        "cwd": cmd.get("cwd", os.getcwd()),
                    }
                    f.write(json.dumps(result_event) + "\n")
    except OSError:
        pass


if __name__ == "__main__":
    if len(sys.argv) > 1:
        capture_event(sys.argv[1], *sys.argv[2:])
