"""Artifact management commands for vigil-client."""

from __future__ import annotations

from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from ..api import VigilClient
from ..auth import auth_manager

console = Console()


def list_artifacts(
    project: Optional[str] = typer.Option(None, help="Filter by project ID"),
    type_filter: Optional[str] = typer.Option(None, help="Filter by artifact type"),
) -> None:
    """List artifacts in the platform."""
    try:
        config = auth_manager.get_client_config()
        project_id = project or config.default_project

        with VigilClient(config.remote) as client:
            artifacts_list = client.list_artifacts(project_id=project_id, type_filter=type_filter)

            if not artifacts_list:
                console.print("[yellow]📭 No artifacts found[/yellow]")
                return

            table = Table(title="Platform Artifacts")
            table.add_column("ID", style="cyan", no_wrap=True)
            table.add_column("Name", style="green")
            table.add_column("Type", style="blue")
            table.add_column("Status", style="yellow")
            table.add_column("Updated", style="dim")

            for artifact in artifacts_list:
                updated = artifact.updated_at.strftime("%Y-%m-%d") if artifact.updated_at else "Never"
                table.add_row(
                    artifact.id or "unknown",
                    artifact.name,
                    artifact.type,
                    artifact.status,
                    updated
                )

            console.print(table)

    except Exception as e:
        console.print(f"[red]❌ Failed to list artifacts: {e}[/red]")
        raise typer.Exit(1)


def get_artifact(artifact_id: str) -> None:
    """Get detailed information about a specific artifact."""
    try:
        config = auth_manager.get_client_config()

        with VigilClient(config.remote) as client:
            artifact = client.get_artifact(artifact_id)

            console.print(f"[bold cyan]Artifact: {artifact.name}[/bold cyan]")
            console.print(f"ID: {artifact.id}")
            console.print(f"Type: {artifact.type}")
            console.print(f"Status: {artifact.status}")
            console.print(f"URI: {artifact.uri}")
            if artifact.description:
                console.print(f"Description: {artifact.description}")
            if artifact.updated_at:
                console.print(f"Updated: {artifact.updated_at}")

    except Exception as e:
        console.print(f"[red]❌ Failed to get artifact: {e}[/red]")
        raise typer.Exit(1)


def search_artifacts(query: str) -> None:
    """Search for artifacts by name or description."""
    try:
        config = auth_manager.get_client_config()

        with VigilClient(config.remote) as client:
            # This would need to be implemented in the API client
            console.print(f"[yellow]⚠️  Search not yet implemented[/yellow]")
            console.print(f"Would search for: {query}")

    except Exception as e:
        console.print(f"[red]❌ Failed to search artifacts: {e}[/red]")
        raise typer.Exit(1)


# Create Typer app for artifacts commands
artifacts = typer.Typer(help="Manage artifacts in the platform")

artifacts.command("list")(list_artifacts)
artifacts.command("get")(get_artifact)
artifacts.command("search")(search_artifacts)
