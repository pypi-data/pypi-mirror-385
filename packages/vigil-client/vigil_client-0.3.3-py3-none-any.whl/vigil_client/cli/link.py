"""Provenance linking commands for vigil-client."""

from __future__ import annotations

import typer
from rich.console import Console

from ..api import VigilClient
from ..auth import auth_manager
from ..models import Link, LinkType

console = Console()


def link_command(
    from_id: str = typer.Argument(..., help="Source artifact ID"),
    to_id: str = typer.Argument(..., help="Target artifact ID"),
    relation: LinkType = typer.Argument(..., help="Link type (input_of, output_of, etc.)"),
) -> None:
    """Create a provenance link between artifacts."""
    try:
        config = auth_manager.get_client_config()

        from ..models.config import PlatformConfig
        platform_config = PlatformConfig(base_url=config.remote.base_url)
        with VigilClient(platform_config) as client:
            link_obj = Link(
                from_artifact_id=from_id,
                to_artifact_id=to_id,
                type=relation
            )

            result = client.create_link(link_obj)
            console.print(f"[green]✅ Link created: {result.id}[/green]")
            console.print(f"   {from_id} --[{relation.value}]--> {to_id}")

    except Exception as e:
        console.print(f"[red]❌ Failed to create link: {e}[/red]")
        raise typer.Exit(1) from None


# Create Typer app for link commands
link = typer.Typer(help="Create provenance links between artifacts")

link.command("link")(link_command)
