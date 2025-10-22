"""Main platform CLI app."""

from __future__ import annotations

import typer
from rich.console import Console

from .artifacts import get_artifact, list_artifacts, search_artifacts
from .config import get_config, set_project
from .link import link_command
from .login import login_command
from .pull import pull_command
from .push import push_command

# Create platform CLI app - now exports individual commands for top-level integration
console = Console()

# Export individual commands for top-level integration
def login(base_url: str | None = typer.Option(None, help="Platform API base URL"),
          token: str | None = typer.Option(None, help="API token (if you have one)")) -> None:
    """Log into the Vigil platform via OAuth or API token."""
    login_command(base_url, token)

def logout() -> None:
    """Log out and remove local credentials."""
    from .login import logout as logout_func
    logout_func()

def whoami() -> None:
    """Display the currently authenticated user and organization."""
    from .login import whoami as whoami_func
    whoami_func()

def config_get() -> None:
    """Show current configuration."""
    get_config()



def push(receipt_path: str | None = typer.Option(None, help="Path to receipt file"),
        artifact_path: str | None = typer.Option(None, help="Path to artifact file"),
        project: str | None = typer.Option(None, help="Project ID"),
        force: bool = typer.Option(False, help="Force upload even if already exists")) -> None:
    """Upload receipts, artifacts, datasets, or models to the platform."""
    push_command(receipt_path, artifact_path, project, force)

def pull(artifact_id: str = typer.Argument(..., help="Artifact ID to download"),
        output_dir: str | None = typer.Option(None, help="Output directory"),
        verify: bool = typer.Option(True, help="Verify artifact integrity")) -> None:
    """Download verified artifacts or receipts from the platform."""
    pull_command(artifact_id, output_dir, verify)

def link(source_id: str = typer.Argument(..., help="Source artifact ID"),
         target_id: str = typer.Argument(..., help="Target artifact ID"),
         relationship: str = typer.Option("derived_from", help="Relationship type")) -> None:
    """Create or update provenance links between artifacts."""
    link_command(source_id, target_id, relationship)

def artifacts_list(project: str | None = typer.Option(None, help="Project ID"),
                   limit: int = typer.Option(50, help="Number of artifacts to show")) -> None:
    """List registered artifacts in a project."""
    list_artifacts(project, limit)

def artifacts_get(artifact_id: str = typer.Argument(..., help="Artifact ID")) -> None:
    """Retrieve artifact metadata from the registry."""
    get_artifact(artifact_id)

def artifacts_search(query: str = typer.Argument(..., help="Search query"),
                    project: str | None = typer.Option(None, help="Project ID"),
                    limit: int = typer.Option(20, help="Number of results")) -> None:
    """Search across artifacts, datasets, and receipts."""
    search_artifacts(query, project, limit)


def config_set(key: str = typer.Argument(..., help="Config key"),
               value: str = typer.Argument(..., help="Config value")) -> None:
    """Set a configuration value (e.g. default project, endpoint)."""
    if key == "project":
        set_project(value)
    else:
        typer.echo(f"Unknown config key: {key}")
        raise typer.Exit(1)


# Create platform CLI app for standalone use
platform_app = typer.Typer(help="Platform integration and artifact management.")

# Add commands to the app for standalone use
platform_app.command("login")(login)
platform_app.command("logout")(logout)
platform_app.command("whoami")(whoami)
platform_app.command("push")(push)
platform_app.command("pull")(pull)
platform_app.command("link")(link)
platform_app.command("artifacts")(artifacts_list)
platform_app.command("artifacts-get")(artifacts_get)
platform_app.command("artifacts-search")(artifacts_search)
platform_app.command("config")(config_get)
platform_app.command("config-set")(config_set)

def main() -> None:
    """Main CLI entry point."""
    platform_app()


if __name__ == "__main__":
    main()
