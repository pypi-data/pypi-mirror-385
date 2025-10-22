"""CLI extensions for Vigil platform integration."""

from __future__ import annotations

import typer
from rich.console import Console

from .cli import login, push, pull, link, artifacts, config

# Create platform CLI app
platform_app = typer.Typer(help="Platform integration and artifact management.")
console = Console()

# Add subcommands
platform_app.add_typer(login, name="login")
platform_app.add_typer(push, name="push")
platform_app.add_typer(pull, name="pull")
platform_app.add_typer(link, name="link")
platform_app.add_typer(artifacts, name="artifacts")
platform_app.add_typer(config, name="config")


def main():
    """Main CLI entry point."""
    platform_app()


if __name__ == "__main__":
    main()
