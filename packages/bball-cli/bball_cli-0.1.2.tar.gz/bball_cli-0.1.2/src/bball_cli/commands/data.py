"""Data commands for the bball CLI (stub)."""

from __future__ import annotations

import typer

app = typer.Typer(help="Data operations")


@app.command()
def fetch():
    """Stub command to demonstrate Data group is wired up."""
    typer.echo("Fetching data (stub)...")
