"""Config command implementation."""

import typer
from rich.console import Console
from rich.table import Table

from nuha.core.config import Config

console = Console()


def config_command(
    show: bool = typer.Option(False, "--show", "-s", help="Show current configuration"),
    edit: bool = typer.Option(False, "--edit", "-e", help="Edit configuration file"),
    get: str | None = typer.Option(
        None, "--get", "-g", help="Get specific config value"
    ),
    reset: bool = typer.Option(False, "--reset", help="Reset to defaults"),
) -> None:
    """
    Manage Nuha configuration.

    Examples:
        nuha config --show
        nuha config --edit
        nuha config --get ai.provider
        nuha config --reset
    """
    try:
        if reset:
            from nuha.cli.commands.setup import _reset_config

            _reset_config()
            return

        if edit:
            _edit_config()
        elif get:
            _get_config_value(get)
        elif show:
            _show_config()
        else:
            console.print(
                "[yellow]Please specify an option. Use --help for more information.[/yellow]"
            )
            raise typer.Exit(1)

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(1)


def _show_config() -> None:
    """Show current configuration."""
    config = Config.load()

    console.print("\n[bold blue]⚙️  Nuha Configuration[/bold blue]\n")

    # AI Settings
    table = Table(title="AI Settings", show_header=True, header_style="bold magenta")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("Provider", config.ai.provider.value)
    table.add_row("Model", config.ai.model)
    table.add_row("Temperature", str(config.ai.temperature))
    table.add_row("Max Tokens", str(config.ai.max_tokens))

    console.print(table)

    # Terminal Settings
    table = Table(
        title="Terminal Settings", show_header=True, header_style="bold magenta"
    )
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("History Limit", str(config.terminal.history_limit))
    table.add_row("Auto Analyze", "✓" if config.terminal.auto_analyze else "✗")
    table.add_row("Include Context", "✓" if config.terminal.include_context else "✗")

    console.print(table)

    # Output Settings
    table = Table(
        title="Output Settings", show_header=True, header_style="bold magenta"
    )
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("Format", config.output.format)
    table.add_row("Color", "✓" if config.output.color else "✗")
    table.add_row("Verbose", "✓" if config.output.verbose else "✗")

    console.print(table)

    # Behavior Settings
    table = Table(
        title="Behavior Settings", show_header=True, header_style="bold magenta"
    )
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")

    table.add_row(
        "Auto Explain Errors", "✓" if config.behavior.auto_explain_errors else "✗"
    )
    table.add_row("Interactive Mode", "✓" if config.behavior.interactive_mode else "✗")
    table.add_row("Save Analysis", "✓" if config.behavior.save_analysis else "✗")

    console.print(table)

    # Config file location
    console.print(f"\n[dim]Config file:[/dim] [cyan]{Config.get_config_path()}[/cyan]")


def _edit_config() -> None:
    """Edit configuration file."""
    import os
    import subprocess

    config_path = Config.get_config_path()

    if not config_path.exists():
        console.print("[yellow]Config file doesn't exist. Creating default...[/yellow]")
        config = Config.load()
        config.save()

    # Try to open with editor
    editor = os.environ.get("EDITOR", os.environ.get("VISUAL", "vi"))

    try:
        subprocess.run([editor, str(config_path)], check=True)
        console.print("[green]✓[/green] Configuration updated")
    except subprocess.CalledProcessError:
        console.print(
            f"[yellow]Could not open editor. Edit manually:[/yellow] {config_path}"
        )
    except FileNotFoundError:
        console.print(
            f"[yellow]Editor not found. Edit manually:[/yellow] {config_path}"
        )


def _get_config_value(key: str) -> None:
    """Get a specific configuration value."""
    config = Config.load()

    parts = key.split(".")
    value = config

    try:
        for part in parts:
            if hasattr(value, part):
                value = getattr(value, part)
            else:
                console.print(f"[red]Invalid config key:[/red] {key}")
                raise typer.Exit(1)

        console.print(f"[cyan]{key}:[/cyan] {value}")

    except Exception as e:
        console.print(f"[red]Error getting config value:[/red] {e}")
        raise typer.Exit(1)
