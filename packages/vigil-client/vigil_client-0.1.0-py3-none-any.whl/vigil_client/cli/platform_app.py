"""Main platform CLI app."""

from __future__ import annotations

import typer
from rich.console import Console

from .login import login_command, logout, whoami
from .push import push_command
from .pull import pull_command
from .link import link_command
from .artifacts import list_artifacts, get_artifact, search_artifacts
from .config import get_config, set_project, set_remote

# Create platform CLI app
platform_app = typer.Typer(help="Platform integration and artifact management.")
console = Console()

# Add subcommands directly
platform_app.command("login")(login_command)
platform_app.command("logout")(logout)
platform_app.command("whoami")(whoami)
platform_app.command("push")(push_command)
platform_app.command("pull")(pull_command)
platform_app.command("link")(link_command)
platform_app.command("artifacts")(list_artifacts)
platform_app.command("artifacts-get")(get_artifact)
platform_app.command("artifacts-search")(search_artifacts)
platform_app.command("config")(get_config)
platform_app.command("config-set-project")(set_project)
platform_app.command("config-set-remote")(set_remote)


def main():
    """Main CLI entry point."""
    platform_app()


if __name__ == "__main__":
    main()
