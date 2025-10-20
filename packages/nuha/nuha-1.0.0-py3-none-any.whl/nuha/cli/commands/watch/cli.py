"""CLI interface for watch command."""

import typer

from nuha.core.config import Config

from .core import CommandWatcher
from .display import console, follow_commands, show_commands
from .hooks import generate_shell_hooks


def watch_command(
    start: bool = typer.Option(False, "--start", help="Start monitoring commands"),
    stop: bool = typer.Option(False, "--stop", help="Stop monitoring commands"),
    status: bool = typer.Option(False, "--status", help="Show watch status"),
    show: bool = typer.Option(False, "--show", help="Show recent commands"),
    follow: bool = typer.Option(
        False, "--follow", "-f", help="Follow command output in real-time"
    ),
    background: bool = typer.Option(
        False, "--background", "-b", help="Use background process mode (legacy)"
    ),
) -> None:
    """
    Monitor and record terminal commands.

    Examples:
        nuha watch --start          # Start monitoring in current shell
        nuha watch --stop           # Stop monitoring
        nuha watch --status         # Show status
        nuha watch --show           # Show recent commands
        nuha watch --show --follow  # Follow commands in real-time

    Current Session Monitoring (Recommended):
        nuha watch --start          # Start monitoring in current shell
        nuha watch --stop           # Stop monitoring

    Background Mode Usage (Legacy):
        nuha watch --start --background  # Start background process
        nuha watch --stop                 # Stop background process
    """
    try:
        config = Config.load()
        watcher = CommandWatcher(config.get_config_dir())

        # Count flags
        flags_count = sum([start, stop, status, show])

        if flags_count == 0:
            # Default to status if no flags provided
            watcher.get_status()
        elif flags_count > 1:
            console.print(
                "[red]Error:[/red] Only one action can be specified at a time"
            )
            console.print(
                "Available options: --start, --stop, --status, --show, --follow, --background"
            )
            raise typer.Exit(1)
        elif start:
            if background:
                # Legacy background mode
                watcher.start_watching()
            else:
                # Current session monitoring - output shell hooks for eval
                shell = watcher.detect_shell()
                hooks = generate_shell_hooks(
                    shell, watcher.watch_jsonl_file, stop=False
                )
                console.print(hooks)
        elif stop:
            if background:
                # Legacy background mode
                watcher.stop_watching()
            else:
                # Current session monitoring - output stop hooks for eval
                shell = watcher.detect_shell()
                hooks = generate_shell_hooks(shell, watcher.watch_jsonl_file, stop=True)
                console.print(hooks)
        elif status:
            watcher.get_status()
        elif show:
            if follow:
                follow_commands(watcher)
            else:
                show_commands(watcher)

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(1)
