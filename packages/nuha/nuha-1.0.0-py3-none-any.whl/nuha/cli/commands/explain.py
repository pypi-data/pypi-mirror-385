"""Explain command implementation."""

import typer
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

from nuha.cli.commands.watch.core import CommandWatcher
from nuha.core.ai_client import AIClient
from nuha.core.config import Config
from nuha.core.terminal_reader import TerminalReader

console = Console()


def explain_command(
    command: str | None = typer.Argument(None, help="Command to explain"),
    auto: bool = typer.Option(False, "--auto", "-a", help="Auto-explain last command"),
    error: str | None = typer.Option(
        None, "--error", "-e", help="Include error output"
    ),
    context: bool = typer.Option(
        True, "--context/--no-context", help="Include terminal context"
    ),
) -> None:
    """
    Explain a command and provide solutions for errors.

    Examples:
        nuha explain "git push"
        nuha explain --auto
        nuha explain "npm install" --error "EACCES: permission denied"
    """
    try:
        # Load configuration
        config = Config.load()

        # Get command to explain
        if auto:
            # First try to get command from watch history if monitoring is active
            watcher = CommandWatcher(config.get_config_dir())

            if watcher.is_monitoring_active():
                last_cmd_data = watcher.get_last_command()

                if last_cmd_data:
                    command = last_cmd_data.get("command")
                    if command:
                        console.print(
                            f"[dim]🔍 Found last command from watch:[/dim] [cyan]{command}[/cyan]\n"
                        )
                    else:
                        console.print(
                            "[yellow]No valid command found in watch history[/yellow]"
                        )
                        raise typer.Exit(1)
                else:
                    console.print(
                        "[yellow]No commands recorded in watch history yet[/yellow]"
                    )
                    raise typer.Exit(1)
            else:
                # Fallback to terminal history when watch is not active
                terminal_reader = TerminalReader(
                    history_limit=config.terminal.history_limit
                )
                last_cmd = terminal_reader.get_last_command()
                if not last_cmd:
                    console.print(
                        "[yellow]No recent commands found in history[/yellow]"
                    )
                    console.print(
                        '[dim]💡 Tip: Run \'eval "$(nuha watch --start)" to enable watch monitoring for real-time command tracking[/dim]'
                    )
                    raise typer.Exit(1)
                command = last_cmd
                console.print(
                    f"[dim]🔍 Found last command from history:[/dim] [cyan]{command}[/cyan]\n"
                )
        elif not command:
            console.print(
                "[red]Error:[/red] Please provide a command or use --auto flag"
            )
            raise typer.Exit(1)

        # Get context if enabled
        context_data: dict[str, str | list[str]] | None = None
        if context and config.terminal.include_context:
            terminal_reader = TerminalReader(
                history_limit=config.terminal.history_limit
            )
            context_data = terminal_reader.get_context()

        # Get AI explanation
        with console.status("[bold blue]🤖 Analyzing command..."):
            ai_client = AIClient(config)
            explanation = ai_client.explain_command(
                command=command, error=error, context=context_data
            )

        # Display result
        console.print(
            Panel(
                Markdown(explanation),
                title="[bold blue]🤖 AI Assistant[/bold blue]",
                border_style="blue",
            )
        )

    except ValueError as e:
        console.print(f"[bold red]Configuration Error:[/bold red] {e}")
        console.print(
            "\n[yellow]💡 Tip:[/yellow] Run [cyan]nuha setup[/cyan] to configure your API keys"
        )
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(1)
