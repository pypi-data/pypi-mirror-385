"""API server commands for the bball CLI (stub)."""

from __future__ import annotations

import typer

app = typer.Typer(help="API server commands")


@app.command()
def run(host: str = "127.0.0.1", port: int = 8000):
    """Stub command to demonstrate API group is wired up."""
    typer.echo(f"Starting API server (stub) on {host}:{port}...")
