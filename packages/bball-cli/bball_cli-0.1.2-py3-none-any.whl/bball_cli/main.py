"""Command-line interface for bball."""

import importlib.util

import typer

from rich.console import Console
from rich.table import Table

app = typer.Typer(
    name="bball",
    help="NBA Analytics Platform CLI",
    add_completion=False,
)
console = Console()


def check_module(module_name: str) -> bool:
    """Check if a module is installed."""
    spec = importlib.util.find_spec(module_name)
    return spec is not None


@app.command()
def info():
    """Show information about installed bball components."""
    table = Table(title="bball Components", show_header=True)
    table.add_column("Component", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Description")

    components = [
        ("bball_core", "Core", "Core models and utilities"),
        ("bball_cli", "CLI", "Command-line interface"),
        ("bball_api", "API", "REST/GraphQL API server"),
        ("bball_data", "Data", "Data fetching and processing"),
        ("bball_strategies", "Strategies", "Analysis strategies"),
        ("bball_reports", "Reports", "Report generation"),
    ]

    for module, name, description in components:
        if check_module(module):
            status = "✓ Installed"
            style = "green"
        else:
            status = "✗ Not installed"
            style = "red"
        table.add_row(name, f"[{style}]{status}[/{style}]", description)

    console.print(table)
    console.print("\n[yellow]Install missing components with:[/yellow]")
    console.print("[cyan]pip install bball[all][/cyan] - Install everything")
    console.print("[cyan]pip install bball[api][/cyan] - Install specific component")


@app.command()
def version():
    """Show version information."""
    import bball_cli  # noqa: PLC0415

    console.print(f"[cyan]bball-cli version:[/cyan] {bball_cli.__version__}")


# Conditional command groups based on installed packages
if check_module("bball_api"):
    from .commands import api
    app.add_typer(api.app, name="api", help="API server commands")

if check_module("bball_data"):
    from .commands import data
    app.add_typer(data.app, name="data", help="Data operations")

if check_module("bball_strategies"):
    from .commands import strategies
    app.add_typer(strategies.app, name="strategies", help="Analysis strategies")

if check_module("bball_reports"):
    from .commands import reports
    app.add_typer(reports.app, name="reports", help="Report generation")


@app.callback()
def main(
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),  # noqa: FBT001, FBT003
):
    """Bball - NBA Analytics Platform.

    A comprehensive platform for NBA data analysis, strategies, and reporting.
    """
    if verbose:
        console.print("[dim]Verbose mode enabled[/dim]")


if __name__ == "__main__":
    app()
