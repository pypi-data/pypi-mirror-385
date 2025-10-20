"""Debug command implementation."""

import typer
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

from nuha.core.ai_client import AIClient
from nuha.core.config import Config

console = Console()


def debug_command(
    interactive: bool = typer.Option(
        False, "--interactive", "-i", help="Start interactive debugging session"
    ),
    trace: bool = typer.Option(False, "--trace", help="Show debug trace information"),
    query: str | None = typer.Argument(None, help="Debug query"),
) -> None:
    """
    Interactive debugging and troubleshooting assistant.

    Examples:
        nuha debug --interactive
        nuha debug "Docker container keeps crashing"
        nuha debug --trace
    """
    try:
        if trace:
            _show_trace_info()
            return

        if interactive:
            _run_interactive_session()
        elif query:
            _handle_query(query)
        else:
            console.print(
                "[yellow]Please provide a query or use --interactive flag[/yellow]"
            )
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


def _show_trace_info() -> None:
    """Show debug trace information."""
    import os
    import sys

    from nuha import __version__
    from nuha.core.terminal_reader import TerminalReader

    console.print("\n[bold blue]🔧 Nuha Debug Information[/bold blue]\n")

    # Version info
    console.print(f"[cyan]Version:[/cyan] {__version__}")
    console.print(f"[cyan]Python:[/cyan] {sys.version.split()[0]}")
    console.print(f"[cyan]Platform:[/cyan] {sys.platform}")

    # Configuration
    config = Config.load()
    console.print(f"\n[cyan]AI Provider:[/cyan] {config.ai.provider.value}")
    console.print(f"[cyan]AI Model:[/cyan] {config.ai.model}")

    # Terminal info
    terminal_reader = TerminalReader()
    console.print(f"\n[cyan]Shell:[/cyan] {terminal_reader.shell}")
    console.print(f"[cyan]Working Directory:[/cyan] {os.getcwd()}")

    # Config files
    config_dir = Config.get_config_dir()
    config_path = Config.get_config_path()
    console.print(f"\n[cyan]Config Directory:[/cyan] {config_dir}")
    console.print(f"[cyan]Config File:[/cyan] {config_path}")
    console.print(f"[cyan]Config Exists:[/cyan] {config_path.exists()}")

    # History file
    history_file = terminal_reader._get_history_file()
    if history_file:
        console.print(f"\n[cyan]History File:[/cyan] {history_file}")
        console.print(f"[cyan]History Exists:[/cyan] {history_file.exists()}")


def _run_interactive_session() -> None:
    """Run interactive debugging session."""
    config = Config.load()
    ai_client = AIClient(config)
    conversation_history: list[dict[str, str]] = []

    console.print(
        "\n[bold blue]🔧 Starting interactive debugging session...[/bold blue]"
    )
    console.print("[dim]Type 'exit' or 'quit' to end the session[/dim]\n")

    while True:
        try:
            # Get user input
            user_input = console.input("[bold green]Debug>[/bold green] ").strip()

            if not user_input:
                continue

            if user_input.lower() in ["exit", "quit", "q"]:
                console.print("\n[blue]👋 Ending debug session.[/blue]")
                break

            # Get AI response
            with console.status("[bold blue]🤖 Thinking..."):
                response = ai_client.interactive_debug(user_input, conversation_history)

            # Update conversation history
            conversation_history.append({"role": "user", "content": user_input})
            conversation_history.append({"role": "assistant", "content": response})

            # Display response
            console.print(Panel(Markdown(response), border_style="blue"))
            console.print()

        except KeyboardInterrupt:
            console.print("\n\n[blue]👋 Ending debug session.[/blue]")
            break
        except Exception as e:
            console.print(f"\n[bold red]Error:[/bold red] {e}\n")


def _handle_query(query: str) -> None:
    """Handle a single debug query."""
    config = Config.load()
    ai_client = AIClient(config)

    with console.status("[bold blue]🤖 Analyzing issue..."):
        response = ai_client.interactive_debug(query)

    console.print(
        Panel(
            Markdown(response),
            title="[bold blue]🤖 Debug Assistant[/bold blue]",
            border_style="blue",
        )
    )
