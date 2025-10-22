"""Authentication commands for vigil-client."""

from __future__ import annotations

import typer
from rich.console import Console

from ..utils.auth import AuthManager

console = Console()


def login_command(
    base_url: str | None = typer.Option(None, help="Platform API base URL"),
    token: str | None = typer.Option(None, help="API token (if you have one)"),
) -> None:
    """Authenticate with Vigil platform."""
    auth_manager = AuthManager()

    # Check if already authenticated
    if auth_manager.is_authenticated():
        config = auth_manager.load_config()
        if config:
            console.print(f"\n[green]✅ Already authenticated as {config.auth.username}[/green]")
            console.print(f"   Platform: {config.remote.base_url}")
            console.print("   Run 'vigil logout' to sign out, or 'vigil whoami' for details")
        return

    try:
        if token:
            auth_manager.login_token(token, base_url)
            console.print("[green]✅ Token authentication successful[/green]")
        else:
            auth_manager.login_interactive(base_url)
    except Exception as e:
        console.print(f"[red]❌ Login failed: {e}[/red]")
        raise typer.Exit(1) from e


def logout() -> None:
    """Log out and clear stored credentials."""
    auth_manager = AuthManager()
    auth_manager.logout()


def whoami() -> None:
    """Show current user information with improved formatting."""
    auth_manager = AuthManager()

    if not auth_manager.is_authenticated():
        console.print("\n[red]❌ Not authenticated[/red]")
        console.print("   Run 'vigil login' to authenticate with the platform")
        raise typer.Exit(1)

    try:
        config = auth_manager.load_config()
        if not config:
            console.print("[red]❌ Not authenticated. Run 'vigil login' first.[/red]")
            raise typer.Exit(1)

        # Display user information with better formatting
        console.print("\n[bold blue]👤 Current User Information[/bold blue]")
        console.print("=" * 40)
        console.print(f"[green]User:[/green] {config.auth.username}")
        if config.auth.organization:
            console.print(f"[green]Organization:[/green] {config.auth.organization}")
        console.print(f"[green]Platform:[/green] {config.remote.base_url}")
        console.print(f"[green]Config File:[/green] {auth_manager.CONFIG_FILE}")

        # Show token status
        if config.auth.token:
            console.print("[green]Token Status:[/green] ✅ Active")
            try:
                import time

                import jwt
                payload = jwt.decode(config.auth.token or "", options={"verify_signature": False})
                if payload.get('exp'):
                    expires_in = payload.get('exp') - time.time()
                    if expires_in > 0:
                        hours = int(expires_in / 3600)
                        minutes = int((expires_in % 3600) / 60)
                        console.print(f"[green]Token Expires:[/green] {hours}h {minutes}m")
                    else:
                        console.print("[red]Token Expires:[/red] ❌ Expired")
            except Exception:
                console.print("[green]Token Status:[/green] ✅ Active (expiry unknown)")

        console.print("=" * 40)

    except Exception as e:
        console.print(f"\n[red]❌ Failed to get user info: {e}[/red]")
        console.print("   Try running 'vigil logout' then 'vigil login' to refresh credentials")
        raise typer.Exit(1) from e


# Create Typer app for login commands
login = typer.Typer(help="Authentication commands")

login.command("login")(login_command)
login.command("logout")(logout)
login.command("whoami")(whoami)
