"""Push commands for vigil-client."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from ..api import VigilClient
from ..auth import auth_manager

console = Console()


def push_command(
    receipt: Optional[Path] = typer.Argument(None, help="Path to receipt JSON file"),
    artifacts_dir: Optional[Path] = typer.Option(None, help="Directory containing artifacts to push"),
    receipts_only: bool = typer.Option(False, "--receipts-only", help="Upload receipts only"),
    project: Optional[str] = typer.Option(None, "--project", help="Push specific project"),
) -> None:
    """Upload receipts and artifacts to the platform."""
    try:
        config = auth_manager.get_client_config()

        with VigilClient(config.remote) as client:
            if receipt:
                # Push specific receipt
                result = client.register_local_receipt(receipt)
                console.print(f"[green]✅ Receipt pushed: {result.get('id', 'unknown')}[/green]")

            elif artifacts_dir:
                # Push all artifacts in directory
                if not artifacts_dir.exists():
                    console.print(f"[red]❌ Directory not found: {artifacts_dir}[/red]")
                    raise typer.Exit(1)

                pushed = 0
                for file_path in artifacts_dir.glob("*"):
                    if file_path.is_file():
                        try:
                            from ..models import Artifact, ArtifactType

                            artifact = Artifact(
                                name=file_path.name,
                                type=ArtifactType.DATASET,  # Default type
                                uri=str(file_path),
                                project_id=project or config.default_project
                            )

                            result = client.push_artifact_with_file(artifact, file_path)
                            console.print(f"[green]✅ Artifact pushed: {result.name}[/green]")
                            pushed += 1
                        except Exception as e:
                            console.print(f"[red]❌ Failed to push {file_path.name}: {e}[/red]")

                console.print(f"[blue]📊 Pushed {pushed} artifacts[/blue]")

            else:
                console.print("[red]❌ Specify either receipt path or --artifacts-dir[/red]")
                raise typer.Exit(1)

    except Exception as e:
        console.print(f"[red]❌ Push failed: {e}[/red]")
        raise typer.Exit(1)


# Create Typer app for push commands
push = typer.Typer(help="Upload receipts and artifacts to the platform")

push.command("push")(push_command)
