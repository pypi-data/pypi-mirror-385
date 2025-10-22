"""Configuration management commands for vigil-client."""

from __future__ import annotations

import typer
from rich.console import Console
from rich.table import Table

from ..auth import auth_manager

console = Console()


def get_config() -> None:
    """Show current configuration."""
    config = auth_manager.load_config()

    if not config:
        console.print("[yellow]⚠️  No configuration found[/yellow]")
        return

    table = Table(title="Vigil Configuration")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("Platform URL", config.remote.base_url if config.remote else "Unknown")
    table.add_row("User", config.auth.username or "Unknown")
    table.add_row("Organization", config.auth.organization or "Unknown")
    table.add_row("Default Project", config.default_project or "None")
    table.add_row("Authenticated", "✅ Yes" if auth_manager.is_authenticated() else "❌ No")

    console.print(table)


def set_project(project_id: str) -> None:
    """Set default project ID."""
    try:
        auth_manager.set_default_project(project_id)
        console.print(f"[green]✅ Default project set to: {project_id}[/green]")
    except Exception as e:
        console.print(f"[red]❌ Failed to set project: {e}[/red]")
        raise typer.Exit(1) from None


def set_remote(remote_url: str) -> None:
    """Set remote platform URL."""
    try:
        auth_manager.set_remote_url(remote_url)
        console.print(f"[green]✅ Remote URL set to: {remote_url}[/green]")
    except Exception as e:
        console.print(f"[red]❌ Failed to set remote URL: {e}[/red]")
        raise typer.Exit(1) from None


# Create Typer app for config commands
config = typer.Typer(help="Manage vigil-client configuration")

config.command("get")(get_config)
config.command("set-project")(set_project)
config.command("set-remote")(set_remote)
