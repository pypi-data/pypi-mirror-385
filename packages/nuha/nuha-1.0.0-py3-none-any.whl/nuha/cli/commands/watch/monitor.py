"""Background monitoring script generation for watch command."""

from pathlib import Path


def generate_monitor_script(watch_file: Path, pid_file: Path) -> str:
    """Generate a simple monitoring script for subprocess."""
    return f'''
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from datetime import datetime

def monitor_commands():
    """Monitor shell commands and record them."""
    watch_file = Path("{watch_file}")
    pid_file = Path("{pid_file}")

    # Load existing commands
    commands = []
    if watch_file.exists():
        try:
            with open(watch_file) as f:
                commands = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError, OSError):
            commands = []

    print(f"Starting monitoring, watch_file: {{watch_file}}, pid_file: {{pid_file}}", file=sys.stderr)

    while pid_file.exists():
        try:
            # Get last command from history
            shell = os.environ.get("SHELL", "")
            if "zsh" in shell:
                result = subprocess.run(
                    ["zsh", "-c", "history | tail -1"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
            else:
                result = subprocess.run(
                    ["bash", "-c", "history 1"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )

            if result.returncode == 0:
                line = result.stdout.strip()
                if line:
                    # Extract command number and command
                    parts = line.split(None, 1)
                    if len(parts) > 1:
                        cmd_num = parts[0]
                        cmd = parts[1]

                        # Filter out nuha commands and history commands
                        if (cmd and
                            not cmd.startswith("nuha") and
                            not cmd.startswith("uv run nuha") and
                            not cmd.startswith("history") and
                            not cmd.startswith("fc -") and
                            len(cmd.strip()) > 0):

                            # Avoid duplicates
                            if not commands or commands[-1].get("command") != cmd:
                                commands.append({{
                                    "command": cmd,
                                    "timestamp": datetime.now().isoformat(),
                                    "exit_code": None
                                }})

                                # Keep only last 100 commands
                                if len(commands) > 100:
                                    commands = commands[-100:]

                                # Save commands
                                with open(watch_file, "w") as f:
                                    json.dump(commands, f, indent=2)

                                print(f"Recorded command: {{cmd}}", file=sys.stderr)

            time.sleep(2)  # Check every 2 seconds

        except (KeyboardInterrupt, SystemExit):
            break
        except Exception as e:
            print(f"Monitor error: {{e}}", file=sys.stderr)
            time.sleep(5)

    print("Monitoring stopped", file=sys.stderr)

if __name__ == "__main__":
    try:
        monitor_commands()
    except KeyboardInterrupt:
        pass
'''
