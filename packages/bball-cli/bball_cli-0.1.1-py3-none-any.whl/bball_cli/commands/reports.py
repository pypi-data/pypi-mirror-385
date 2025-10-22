"""Report commands for the bball CLI (stub)."""

from __future__ import annotations

import typer

app = typer.Typer(help="Report generation")


@app.command()
def build():
    """Stub command to demonstrate Reports group is wired up."""
    typer.echo("Building report (stub)...")
