"""Setup command implementation."""

import typer
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt

from nuha.core.config import AIProvider, Config

console = Console()


def setup_command(
    provider: str | None = typer.Option(
        None, "--provider", "-p", help="AI provider to configure"
    ),
    reset: bool = typer.Option(
        False, "--reset", help="Reset configuration to defaults"
    ),
) -> None:
    """
    Setup and configure Nuha.

    Examples:
        nuha setup
        nuha setup --provider openai
        nuha setup --reset
    """
    try:
        if reset:
            _reset_config()
            return

        if provider:
            _setup_provider(provider)
        else:
            _interactive_setup()

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(1)


def _reset_config() -> None:
    """Reset configuration to defaults."""
    if Confirm.ask("[yellow]⚠️  Reset configuration to defaults?[/yellow]"):
        config = Config.load()
        config.reset()
        console.print("[green]✓[/green] Configuration reset to defaults")
    else:
        console.print("[dim]Reset cancelled[/dim]")


def _setup_provider(provider_name: str) -> None:
    """Setup a specific provider."""
    try:
        provider = AIProvider(provider_name.lower())
    except ValueError:
        console.print(f"[red]Invalid provider:[/red] {provider_name}")
        console.print(
            f"[yellow]Valid providers:[/yellow] {', '.join([p.value for p in AIProvider])}"
        )
        raise typer.Exit(1)

    config = Config.load()

    # Get API key
    api_key = Prompt.ask(f"Enter {provider.value.upper()} API key", password=True)

    if not api_key:
        console.print("[red]Error:[/red] API key cannot be empty")
        raise typer.Exit(1)

    # Save API key
    config.set_api_key(provider, api_key)
    config.ai.provider = provider

    # Get model if not default
    model = _get_default_model(provider)
    use_default = Confirm.ask(f"Use default model ({model})?", default=True)

    if not use_default:
        custom_model = Prompt.ask("Enter model name")
        if custom_model:
            config.ai.model = custom_model
            config.save()

    console.print(
        f"\n[green]✓[/green] {provider.value.upper()} configured successfully!"
    )
    console.print(f"[dim]Provider:[/dim] [cyan]{provider.value}[/cyan]")
    console.print(f"[dim]Model:[/dim] [cyan]{config.ai.model}[/cyan]")


def _interactive_setup() -> None:
    """Interactive setup wizard."""
    console.print(
        Panel.fit(
            "[bold blue]🤖 Welcome to Nuha Setup![/bold blue]\n\n"
            "Let's configure your AI assistant.\n"
            "You can choose from multiple AI providers.",
            border_style="blue",
        )
    )

    config = Config.load()

    # Choose provider
    console.print("\n[bold]Available AI Providers:[/bold]")
    providers = list(AIProvider)
    for i, provider in enumerate(providers, 1):
        console.print(f"  {i}. [cyan]{provider.value}[/cyan]")

    provider_choice = Prompt.ask(
        "\nSelect provider",
        choices=[str(i) for i in range(1, len(providers) + 1)],
        default="1",
    )

    selected_provider = providers[int(provider_choice) - 1]

    # Get API key
    console.print(f"\n[bold]Setting up {selected_provider.value.upper()}[/bold]")

    api_key_url = _get_api_key_url(selected_provider)
    if api_key_url:
        console.print(f"[dim]Get your API key from: {api_key_url}[/dim]\n")

    api_key = Prompt.ask("Enter API key", password=True)

    if not api_key:
        console.print("[red]Error:[/red] API key cannot be empty")
        raise typer.Exit(1)

    # Save configuration
    config.set_api_key(selected_provider, api_key)
    config.ai.provider = selected_provider

    # Configure model
    default_model = _get_default_model(selected_provider)
    config.ai.model = default_model

    use_default = Confirm.ask(f"\nUse default model ({default_model})?", default=True)

    if not use_default:
        custom_model = Prompt.ask("Enter model name")
        if custom_model:
            config.ai.model = custom_model

    # Configure other settings
    if Confirm.ask("\nConfigure advanced settings?", default=False):
        _configure_advanced_settings(config)

    config.save()

    # Success message
    console.print(
        Panel.fit(
            "[bold green]✓ Setup Complete![/bold green]\n\n"
            f"Provider: [cyan]{config.ai.provider.value}[/cyan]\n"
            f"Model: [cyan]{config.ai.model}[/cyan]\n\n"
            "[dim]Try it out:[/dim] [cyan]nuha explain --auto[/cyan]",
            border_style="green",
        )
    )


def _configure_advanced_settings(config: Config) -> None:
    """Configure advanced settings."""
    console.print("\n[bold]Advanced Settings:[/bold]")

    # Temperature
    temp_str = Prompt.ask(
        f"Temperature (0.0-2.0, current: {config.ai.temperature})",
        default=str(config.ai.temperature),
    )
    try:
        config.ai.temperature = float(temp_str)
    except ValueError:
        console.print("[yellow]Invalid temperature, keeping current value[/yellow]")

    # Max tokens
    tokens_str = Prompt.ask(
        f"Max tokens (current: {config.ai.max_tokens})",
        default=str(config.ai.max_tokens),
    )
    try:
        config.ai.max_tokens = int(tokens_str)
    except ValueError:
        console.print("[yellow]Invalid token count, keeping current value[/yellow]")

    # History limit
    history_str = Prompt.ask(
        f"Command history limit (current: {config.terminal.history_limit})",
        default=str(config.terminal.history_limit),
    )
    try:
        config.terminal.history_limit = int(history_str)
    except ValueError:
        console.print("[yellow]Invalid history limit, keeping current value[/yellow]")


def _get_default_model(provider: AIProvider) -> str:
    """Get default model for provider."""
    defaults = {
        AIProvider.ZHIPUAI: "glm-4.5-flash",
        AIProvider.OPENAI: "gpt-4-turbo-preview",
        AIProvider.CLAUDE: "claude-3-5-sonnet-20241022",
        AIProvider.DEEPSEEK: "deepseek-chat",
    }
    return defaults.get(provider, "glm-4.5-flash")


def _get_api_key_url(provider: AIProvider) -> str | None:
    """Get API key URL for provider."""
    urls = {
        AIProvider.ZHIPUAI: "https://open.bigmodel.cn/",
        AIProvider.OPENAI: "https://platform.openai.com/api-keys",
        AIProvider.CLAUDE: "https://console.anthropic.com/",
        AIProvider.DEEPSEEK: "https://platform.deepseek.com/api_keys",
    }
    return urls.get(provider)
