"""Analyze command implementation."""

import typer
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table

from nuha.core.ai_client import AIClient
from nuha.core.config import Config
from nuha.core.terminal_reader import TerminalReader

console = Console()


def analyze_command(
    session: bool = typer.Option(
        False, "--session", "-s", help="Analyze current session"
    ),
    pattern: str | None = typer.Option(
        None, "--pattern", "-p", help="Search for pattern in history"
    ),
    limit: int = typer.Option(
        50, "--limit", "-l", help="Number of commands to analyze"
    ),
) -> None:
    """
    Analyze command patterns and provide insights.

    Examples:
        nuha analyze --session
        nuha analyze --pattern "permission"
        nuha analyze --limit 100
    """
    try:
        # Load configuration
        config = Config.load()
        terminal_reader = TerminalReader(history_limit=limit)

        if pattern:
            # Search for pattern
            _analyze_pattern(terminal_reader, pattern, config)
        elif session:
            # Analyze session
            _analyze_session(terminal_reader, config)
        else:
            console.print("[yellow]Please specify --session or --pattern[/yellow]")
            raise typer.Exit(1)

    except ValueError as e:
        console.print(f"[bold red]Configuration Error:[/bold red] {e}")
        console.print(
            "\n[yellow]💡 Tip:[/yellow] Run [cyan]nuha setup[/cyan] to configure your API keys"
        )
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(1)


def _analyze_session(terminal_reader: TerminalReader, config: Config) -> None:
    """Analyze the current terminal session."""
    commands = terminal_reader.get_history()

    if not commands:
        console.print("[yellow]No commands found in history[/yellow]")
        raise typer.Exit(1)

    # Display statistics
    console.print("\n[bold blue]📊 Command Analysis Results[/bold blue]\n")

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")

    unique_commands = len({cmd.split()[0] if cmd.split() else "" for cmd in commands})

    table.add_row("Total Commands", str(len(commands)))
    table.add_row("Unique Commands", str(unique_commands))
    table.add_row("Session Shell", terminal_reader.shell)

    console.print(table)

    # Count most used commands
    from collections import Counter

    command_counts = Counter(cmd.split()[0] if cmd.split() else "" for cmd in commands)
    most_common = command_counts.most_common(5)

    if most_common:
        console.print("\n[bold]Most Used Commands:[/bold]")
        for i, (cmd, count) in enumerate(most_common, 1):
            console.print(f"  {i}. [cyan]{cmd}[/cyan] ({count} times)")

    # Get AI insights
    with console.status("[bold blue]🤖 Getting AI insights..."):
        ai_client = AIClient(config)
        insights = ai_client.analyze_patterns(commands)

    console.print(
        Panel(
            Markdown(insights),
            title="[bold blue]🤖 AI Insights[/bold blue]",
            border_style="blue",
        )
    )


def _analyze_pattern(
    terminal_reader: TerminalReader, pattern: str, config: Config
) -> None:
    """Analyze commands matching a pattern."""
    commands = terminal_reader.get_history()

    # Filter commands by pattern
    matching = [cmd for cmd in commands if pattern.lower() in cmd.lower()]

    if not matching:
        console.print(f"[yellow]No commands found matching pattern: {pattern}[/yellow]")
        raise typer.Exit(1)

    console.print(
        f"\n[bold blue]🔍 Found {len(matching)} matching commands:[/bold blue]\n"
    )

    for i, cmd in enumerate(matching[-10:], 1):  # Show last 10 matches
        console.print(f"  {i}. [cyan]{cmd}[/cyan]")

    # Get AI analysis of the pattern
    with console.status("[bold blue]🤖 Analyzing pattern..."):
        ai_client = AIClient(config)
        insights = ai_client.analyze_patterns(matching)

    console.print(
        Panel(
            Markdown(insights),
            title=f"[bold blue]🤖 Pattern Analysis: '{pattern}'[/bold blue]",
            border_style="blue",
        )
    )
