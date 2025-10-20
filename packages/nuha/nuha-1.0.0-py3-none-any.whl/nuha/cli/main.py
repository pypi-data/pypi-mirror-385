"""Main CLI application entry point."""

import sys

import typer
from rich.console import Console

from nuha.cli.commands import analyze, config, debug, explain, setup
from nuha.cli.commands.watch import watch_command
from nuha.core.config import Config

app = typer.Typer(
    name="nuha",
    help="🤖 AI-Powered Terminal Assistant That Understands Your Commands",
    add_completion=True,
    invoke_without_command=True,
)

# Add subcommands
app.command(name="explain")(explain.explain_command)
app.command(name="analyze")(analyze.analyze_command)
app.command(name="debug")(debug.debug_command)
app.command(name="setup")(setup.setup_command)
app.command(name="config")(config.config_command)
app.command(name="watch")(watch_command)

console = Console()


@app.callback()
def callback(
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose output"
    ),
    version: bool = typer.Option(False, "--version", help="Show version and exit"),
) -> None:
    """
    Nuha - AI-Powered Terminal Assistant

    Get AI-powered explanations and solutions for your terminal commands.
    """
    if version:
        from nuha import __version__

        console.print(f"[bold blue]Nuha[/bold blue] version {__version__}")
        raise typer.Exit()

    if verbose:
        # Set verbose mode in config
        config_obj = Config.load()
        config_obj.output.verbose = verbose


def main() -> None:
    """Main entry point for the CLI application."""
    try:
        app()
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user[/yellow]")
        sys.exit(130)
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
