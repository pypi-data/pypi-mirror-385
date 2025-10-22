"""Strategies commands for the bball CLI (stub)."""

from __future__ import annotations

import typer

app = typer.Typer(help="Analysis strategies")


@app.command()
def train():
    """Stub command to demonstrate Strategies group is wired up."""
    typer.echo("Training strategy (stub)...")
