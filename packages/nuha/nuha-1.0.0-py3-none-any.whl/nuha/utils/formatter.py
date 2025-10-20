"""Output formatting utilities."""

from typing import Any

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table

console = Console()


class Formatter:
    """Format output for different contexts."""

    @staticmethod
    def format_command(command: str, highlight: bool = True) -> str:
        """Format a command with syntax highlighting."""
        if highlight:
            return f"[cyan]{command}[/cyan]"
        return command

    @staticmethod
    def format_error(error: str) -> str:
        """Format error message."""
        return f"[bold red]Error:[/bold red] {error}"

    @staticmethod
    def format_success(message: str) -> str:
        """Format success message."""
        return f"[bold green]✓[/bold green] {message}"

    @staticmethod
    def format_warning(message: str) -> str:
        """Format warning message."""
        return f"[bold yellow]⚠️[/bold yellow] {message}"

    @staticmethod
    def format_info(message: str) -> str:
        """Format info message."""
        return f"[bold blue]ℹ️[/bold blue] {message}"

    @staticmethod
    def format_markdown(
        content: str, title: str | None = None, border_style: str = "blue"
    ) -> Panel:
        """Format markdown content in a panel."""
        md = Markdown(content)
        if title:
            return Panel(md, title=title, border_style=border_style)
        return Panel(md, border_style=border_style)

    @staticmethod
    def format_code(
        code: str, language: str = "bash", theme: str = "monokai"
    ) -> Syntax:
        """Format code with syntax highlighting."""
        return Syntax(code, language, theme=theme, line_numbers=False)

    @staticmethod
    def create_table(
        title: str,
        columns: list[tuple[str, str]],
        rows: list[list[str]],
        show_header: bool = True,
    ) -> Table:
        """Create a formatted table."""
        table = Table(title=title, show_header=show_header, header_style="bold magenta")

        for col_name, col_style in columns:
            table.add_column(col_name, style=col_style)

        for row in rows:
            table.add_row(*row)

        return table

    @staticmethod
    def format_dict(data: dict[str, Any], title: str | None = None) -> Table:
        """Format a dictionary as a table."""
        table = Table(title=title, show_header=True, header_style="bold magenta")
        table.add_column("Key", style="cyan")
        table.add_column("Value", style="green")

        for key, value in data.items():
            table.add_row(str(key), str(value))

        return table

    @staticmethod
    def print_divider(char: str = "─", style: str = "dim") -> None:
        """Print a divider line."""
        console.print(char * console.width, style=style)
