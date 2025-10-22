"""Extension mechanism to integrate vigil-client with vigil-core CLI."""

from __future__ import annotations

from typing import Any

from .cli import platform_app


def extend_vigil_cli(app: Any) -> None:
    """Extend the main Vigil CLI with platform commands.

    This function should be called from vigil-core to register
    the platform commands with the main CLI application.

    Args:
        app: The main typer.Typer application instance
    """
    app.add_typer(platform_app, name="platform", help="Platform integration and artifact management.")


# Convenience function for users who install both packages
def init_vigil_platform() -> None:
    """Initialize Vigil platform integration.

    Call this function after importing to enable platform features.
    This is a convenience for users who want to use vigil-client
    alongside vigil-core.
    """
    try:
        # Try to import and extend the main vigil CLI
        from vigil.cli import app
        extend_vigil_cli(app)
    except ImportError:
        # vigil-core not available, that's ok
        pass
