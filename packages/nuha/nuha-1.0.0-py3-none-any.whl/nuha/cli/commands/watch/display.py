"""Display functionality for watch command."""

import time
from datetime import datetime
from typing import Any

from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.table import Table

from nuha.core.capture import parse_legacy_history, read_events

console = Console()


def show_status_table(commands: list[dict[str, Any]]) -> None:
    """Show status table with recent commands."""
    table = Table(title="Recent Commands")
    table.add_column("Time", style="dim")
    table.add_column("Command", style="cyan")
    table.add_column("Exit Code", style="red")

    for cmd in commands:
        exit_code = str(cmd.get("exit_code", "N/A"))
        if cmd.get("exit_code") == 0:
            exit_code = "[green]0[/green]"
        elif cmd.get("exit_code") is not None:
            exit_code = f"[red]{exit_code}[/red]"

        table.add_row(
            cmd.get("timestamp", "N/A"),
            cmd.get("command", "N/A"),
            exit_code,
        )

    console.print(table)


def show_commands(watcher, limit: int = 20) -> None:
    """Show recent commands."""
    # Try to read from JSONL format first (new format)
    if watcher.watch_jsonl_file.exists():
        events = read_events(
            str(watcher.watch_jsonl_file), limit * 2
        )  # Get more to filter

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
            elif event.get("type") == "result" and current_cmd and event.get("data"):
                current_cmd["exit_code"] = (
                    int(event["data"][0])
                    if event["data"] and event["data"][0].isdigit()
                    else None
                )
                commands.append(current_cmd)
                current_cmd = None

        # If no commands from JSONL, try legacy format
        if not commands and watcher.watch_file.exists():
            commands = parse_legacy_history(watcher.watch_file)
    else:
        # Fallback to legacy format
        commands = parse_legacy_history(watcher.watch_file)

    if not commands:
        console.print("[yellow]No commands recorded yet[/yellow]")
        console.print(
            '[dim]Use \'eval "$(nuha watch --start)" to start monitoring[/dim]'
        )
        return

    # Limit commands
    commands = commands[-limit:] if len(commands) > limit else commands

    table = Table(title=f"Last {len(commands)} Commands")
    table.add_column("#", style="dim")
    table.add_column("Time", style="dim")
    table.add_column("Command", style="cyan")
    table.add_column("Exit Code", style="red")

    for i, cmd in enumerate(reversed(commands), 1):
        exit_code = str(cmd.get("exit_code", "N/A"))
        if cmd.get("exit_code") == 0:
            exit_code = "[green]0[/green]"
        elif cmd.get("exit_code") is not None:
            exit_code = f"[red]{exit_code}[/red]"

        # Format timestamp
        timestamp = cmd.get("timestamp", "")
        if timestamp:
            try:
                dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                timestamp = dt.strftime("%H:%M:%S")
            except (ValueError, TypeError):
                timestamp = timestamp[:8]  # Just take time part

        table.add_row(str(i), timestamp, cmd.get("command", "N/A"), exit_code)

    console.print(table)


def follow_commands(watcher) -> None:
    """Follow commands in real-time."""
    console.print("[blue]🔍 Following commands in real-time...[/blue]")
    console.print("[dim]Press Ctrl+C to stop[/dim]\n")

    last_count = 0

    with Live(console=console, refresh_per_second=1) as live:
        try:
            while True:
                commands = watcher.get_recent_commands(10)

                if len(commands) > last_count:
                    # Show new commands
                    new_commands = commands[last_count:]

                    for cmd in new_commands:
                        timestamp = cmd.get("timestamp", "")
                        if timestamp:
                            try:
                                dt = datetime.fromisoformat(
                                    timestamp.replace("Z", "+00:00")
                                )
                                timestamp = dt.strftime("%H:%M:%S")
                            except (ValueError, TypeError):
                                timestamp = timestamp[:8]

                        exit_code = cmd.get("exit_code")
                        if exit_code == 0:
                            status = "[green]✓[/green]"
                        elif exit_code is not None:
                            status = f"[red]✗ ({exit_code})[/red]"
                        else:
                            status = "[dim]?[/dim]"

                        panel = Panel(
                            f"[cyan]{cmd.get('command', 'N/A')}[/cyan]",
                            title=f"{timestamp} {status}",
                            border_style="blue",
                        )
                        live.update(panel)
                        time.sleep(0.5)

                    last_count = len(commands)

                time.sleep(1)

        except KeyboardInterrupt:
            console.print("\n[yellow]Stopped following commands[/yellow]")
