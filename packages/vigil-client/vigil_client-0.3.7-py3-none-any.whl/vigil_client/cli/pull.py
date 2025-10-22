"""Pull commands for vigil-client."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console

from ..api import VigilClient
from ..auth import auth_manager

console = Console()


def pull_command(
    _artifact_type: str = typer.Argument(..., help="Type of artifact (receipt, dataset, model, etc.)"),
    artifact_id: str = typer.Argument(..., help="Artifact ID to download"),
    output: Path | None = typer.Option(None, help="Output path (defaults to artifact name)"),
) -> None:
    """Download an artifact from the platform."""
    try:
        config = auth_manager.get_client_config()

        from ..models.config import PlatformConfig
        platform_config = PlatformConfig(base_url=config.remote.base_url)
        with VigilClient(platform_config) as client:
            # Get artifact info
            artifact = client.get_artifact(artifact_id)

            # Get download URL
            download_url = client.get_download_url(artifact_id)

            # Download file
            import httpx
            with httpx.stream("GET", download_url) as response:
                response.raise_for_status()

                output_path = output or Path(artifact.name)
                with output_path.open("wb") as f:
                    for chunk in response.iter_bytes():
                        f.write(chunk)

            console.print(f"[green]✅ Downloaded: {output_path}[/green]")

    except Exception as e:
        console.print(f"[red]❌ Failed to download artifact: {e}[/red]")
        raise typer.Exit(1) from None


# Create Typer app for pull commands
pull = typer.Typer(help="Download artifacts from the platform")

pull.command("pull")(pull_command)
