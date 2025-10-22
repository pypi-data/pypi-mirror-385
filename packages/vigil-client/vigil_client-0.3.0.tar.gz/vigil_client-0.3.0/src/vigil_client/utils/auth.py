"""Authentication utilities for vigil-client."""

from __future__ import annotations

import json
import os
import socket
import threading
import time
import webbrowser
from pathlib import Path
from typing import Any

import jwt
import keyring
from pydantic import BaseModel
from requests_oauthlib import OAuth2Session

from .jwt_validator import JWTValidator, create_clerk_validator
from ..models.config import ClientConfig


class ClerkConfig(BaseModel):
    """Clerk configuration."""

    client_id: str
    client_secret: str
    domain: str
    redirect_uri: str = "http://localhost:8080/callback"
    scope: list[str] = ["openid", "email", "profile"]


# ClientConfig is imported from models.config


class AuthManager:
    """Manages authentication and configuration for Vigil client."""

    CONFIG_DIR = Path.home() / ".vigil"
    CONFIG_FILE = CONFIG_DIR / "config.json"
    KEYRING_SERVICE = "vigil-client"

    def __init__(self) -> None:
        self.CONFIG_DIR.mkdir(exist_ok=True)
        self._load_clerk_config()
        self._jwt_validator: JWTValidator | None = None

    def _load_clerk_config(self) -> None:
        """Load Clerk configuration from environment or config."""
        self.clerk_config = ClerkConfig(
            client_id=os.environ.get("CLERK_CLIENT_ID", ""),
            client_secret=os.environ.get("CLERK_CLIENT_SECRET", ""),
            domain=os.environ.get("CLERK_DOMAIN", "https://clerk.dev"),
        )

    def _start_callback_server(self, port: int = 8080) -> tuple[str, threading.Thread]:
        """Start a local server to handle OAuth callback."""
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind(('localhost', port))
        server_socket.listen(1)

        callback_url = None
        callback_thread = None

        def handle_callback() -> None:
            nonlocal callback_url
            try:
                client_socket, _ = server_socket.accept()
                request = client_socket.recv(1024).decode('utf-8')

                # Extract callback URL from request
                if 'GET /callback' in request:
                    lines = request.split('\n')
                    for line in lines:
                        if line.startswith('GET /callback'):
                            callback_url = f"http://localhost:{port}{line.split()[1]}"
                            break

                # Send success response
                response = """HTTP/1.1 200 OK
Content-Type: text/html

<html>
<body>
<h1>Authentication Successful!</h1>
<p>You can close this window and return to the terminal.</p>
</body>
</html>"""
                client_socket.send(response.encode())
                client_socket.close()
            except Exception as e:
                print(f"Callback server error: {e}")
            finally:
                server_socket.close()

        callback_thread = threading.Thread(target=handle_callback)
        callback_thread.daemon = True
        callback_thread.start()

        return f"http://localhost:{port}/callback", callback_thread

    def load_config(self) -> ClientConfig | None:
        """Load configuration from disk."""
        if not self.CONFIG_FILE.exists():
            return None

        try:
            with self.CONFIG_FILE.open("r") as f:
                data = json.load(f)

            # Load token from keyring if available
            if data.get("user"):
                try:
                    token = keyring.get_password(self.KEYRING_SERVICE, data["user"])
                    if token:
                        data["token"] = token
                except Exception:
                    pass  # Keyring not available

            return ClientConfig(**data)
        except Exception:
            return None

    def save_config(self, config: ClientConfig) -> None:
        """Save configuration to disk."""
        data = config.model_dump()

        # Store token in keyring if available
        if config.auth.token and config.auth.username:
            try:
                keyring.set_password(self.KEYRING_SERVICE, config.auth.username, config.auth.token)
                # Remove token from config file for security
                data["auth"]["token"] = None
            except Exception:
                pass  # Keyring not available

        with self.CONFIG_FILE.open("w") as f:
            json.dump(data, f, indent=2)

    def is_authenticated(self) -> bool:
        """Check if user is authenticated and token is valid."""
        config = self.load_config()
        if not config or not config.auth.token:
            return False

        # Basic JWT expiration check (optional, since Clerk handles this)
        try:
            payload = jwt.decode(config.auth.token or "", options={"verify_signature": False})
            if payload.get('exp') and time.time() > payload.get('exp'):
                return False
        except Exception:
            # If we can't decode, assume valid (Clerk will reject if invalid)
            pass

        return True

    def refresh_token(self) -> bool:
        """Refresh access token using refresh token."""
        # According to AUTH.md, tokens are short-lived (1-24 hours) and renewable transparently
        # For now, we'll rely on Clerk's automatic refresh or require re-login
        print("Token refresh not implemented - please run 'vigil login' again")
        return False

    def get_user_info(self) -> dict[str, Any]:
        """Get current user information from stored config."""
        config = self.load_config()
        if not config or not config.auth.token:
            raise ValueError("Not authenticated")

        # Extract user info from stored config (following AUTH.md spec)
        return {
            'sub': config.auth.username,
            'org_id': config.auth.organization,
            'username': config.auth.username,
            'organization': config.auth.organization,
        }

    def login_token(self, token: str, base_url: str | None = None) -> None:
        """Login with provided JWT token."""
        if not base_url:
            base_url = os.environ.get("VIGIL_API_URL", "https://api.cofactor.app")

        # Decode token to get user info
        try:
            # Try to verify signature first
            try:
                if not self._jwt_validator:
                    self._jwt_validator = create_clerk_validator(self.clerk_config.domain)
                user_info = self._jwt_validator.verify_token(token)
            except Exception:
                # Fallback to unverified decoding for development
                user_info = jwt.decode(token or "", options={"verify_signature": False})

            # Extract user and organization from token (following AUTH.md spec)
            username = user_info.get('preferred_username') or user_info.get('email', '').split('@')[0]
            organization = user_info.get('org_id') or user_info.get('organization', '')

            from ..models.config import AuthConfig, PlatformConfig
            config = ClientConfig(
                auth=AuthConfig(
                    token=token,
                    username=f"@{username}",
                    organization=f"~{organization}" if organization else None,
                ),
                remote=PlatformConfig(base_url=base_url),
            )

            self.save_config(config)
            print("✅ Token authentication successful!")

        except Exception as e:
            print(f"❌ Token authentication failed: {e}")
            raise

    def login_interactive(self, base_url: str | None = None) -> None:
        """Interactive login via Clerk OAuth with improved UX."""
        if not base_url:
            base_url = os.environ.get("VIGIL_API_URL", "https://api.cofactor.app")

        if not self.clerk_config.client_id:
            raise ValueError("CLERK_CLIENT_ID environment variable not set")

        # Use Clerk's development-friendly redirect URI
        redirect_uri = "http://localhost:8080/callback"

        # Create OAuth2 session
        oauth = OAuth2Session(
            client_id=self.clerk_config.client_id,
            redirect_uri=redirect_uri,
            scope=self.clerk_config.scope
        )

        # Generate authorization URL
        auth_url, state = oauth.authorization_url(
            f"{self.clerk_config.domain}/oauth/authorize",
            state="vigil-cli-auth"
        )

        # Improved UI with better formatting
        print("\n🔐 Vigil Platform Authentication")
        print("=" * 40)
        print("Opening browser for authentication...")
        print(f"Platform: {base_url}")
        print(f"Redirect URI: {redirect_uri}")
        print()

        try:
            webbrowser.open(auth_url)
            print("✅ Browser opened successfully")
        except Exception:
            print("⚠️  Could not open browser automatically")

        print("\n📋 If browser doesn't open, visit this URL:")
        print(f"   {auth_url}")
        print("\n🔄 After authentication, you'll be redirected to:")
        print(f"   {redirect_uri}")
        print("\n📥 Copy the full URL from your browser and paste it below:")
        print("   (The URL should contain 'code=' and 'state=' parameters)")

        # Get callback URL from user input with validation
        while True:
            try:
                callback_url = input("\n🔗 Callback URL: ").strip()

                if not callback_url:
                    print("❌ Please provide a callback URL")
                    continue

                if "localhost:8080/callback" not in callback_url:
                    print("❌ Invalid callback URL. Must contain 'localhost:8080/callback'")
                    continue

                if "code=" not in callback_url:
                    print("❌ Invalid callback URL. Must contain 'code=' parameter")
                    continue

                break

            except KeyboardInterrupt:
                print("\n\n❌ Authentication cancelled by user")
                import sys
                sys.exit(1)
            except EOFError:
                print("\n\n❌ Authentication cancelled")
                import sys
                sys.exit(1)

        # Exchange authorization code for tokens
        print("\n🔄 Exchanging authorization code for access token...")

        try:
            # Add a simple spinner for better UX
            import sys
            import time

            def show_spinner(message: str, duration: float = 1.0) -> None:
                """Show a simple spinner for the given duration."""
                spinner_chars = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
                end_time = time.time() + duration
                i = 0
                while time.time() < end_time:
                    sys.stdout.write(f"\r{message} {spinner_chars[i % len(spinner_chars)]}")
                    sys.stdout.flush()
                    time.sleep(0.1)
                    i += 1
                sys.stdout.write(f"\r{message} ✅\n")
                sys.stdout.flush()

            show_spinner("Exchanging code for token", 0.5)
            # Extract code from callback URL manually
            from urllib.parse import parse_qs, urlparse
            parsed_url = urlparse(callback_url)
            query_params = parse_qs(parsed_url.query)
            auth_code = query_params.get('code', [None])[0]

            if not auth_code:
                raise ValueError("No authorization code found in callback URL")

            # Make direct token request
            import requests
            token_data = {
                'grant_type': 'authorization_code',
                'code': auth_code,
                'redirect_uri': redirect_uri,
                'client_id': self.clerk_config.client_id,
                'client_secret': self.clerk_config.client_secret,
            }

            response = requests.post(
                f"{self.clerk_config.domain}/oauth/token",
                data=token_data,
                headers={'Content-Type': 'application/x-www-form-urlencoded'}
            )
            response.raise_for_status()
            token_response = response.json()

            print("✅ Token exchange successful")

            # Use access token as the main token (following AUTH.md spec)
            access_token = token_response.get('access_token')
            if access_token:
                show_spinner("Fetching user information", 0.3)

                # Get user info from Clerk OAuth userinfo endpoint
                try:
                    user_response = requests.get(
                        f"{self.clerk_config.domain}/oauth/userinfo",
                        headers={'Authorization': f'Bearer {access_token}'}
                    )
                    user_response.raise_for_status()
                    user_info = user_response.json()

                    # Extract user and organization from Clerk user info
                    username = user_info.get('preferred_username') or user_info.get('email', '').split('@')[0]
                    organization = user_info.get('org_id') or user_info.get('organization', '')

                    print("✅ User information retrieved")

                except Exception as e:
                    print(f"⚠️  Could not fetch user info: {e}")
                    # Fallback to basic info
                    username = "user"
                    organization = ""

                # Create client config following AUTH.md spec
                from .config import ConfigManager
                from ..models.config import AuthConfig, PlatformConfig
                config_manager = ConfigManager()
                config = ClientConfig(
                    auth=AuthConfig(
                        token=access_token,
                        username=f"@{username}",
                        organization=f"~{organization}" if organization else None,
                    ),
                    remote=PlatformConfig(base_url=base_url),
                )

                self.save_config(config)

                # Success message with better formatting
                print("\n🎉 Authentication successful!")
                print("=" * 40)
                print(f"👤 User: @{username}")
                if organization:
                    print(f"🏢 Organization: ~{organization}")
                print(f"🌐 Platform: {base_url}")
                print(f"💾 Configuration saved to: {self.CONFIG_FILE}")
                print("=" * 40)
                print("\n✨ You can now use vigil-client commands!")
                print("   Try: vigil whoami, vigil config get, vigil artifacts list")

        except Exception as e:
            print(f"\n❌ Authentication failed: {e}")
            print("\n🔧 Troubleshooting tips:")
            print("   • Check your internet connection")
            print("   • Verify Clerk OAuth application settings")
            print("   • Ensure redirect URI matches: http://localhost:8080/callback")
            print("   • Try running: vigil logout (to clear any cached credentials)")
            raise

    def logout(self) -> None:
        """Log out and clear stored credentials with improved UX."""
        config = self.load_config()

        if not config:
            print("ℹ️  No active session found")
            return

        print("\n🚪 Logging out...")

        # Clear keyring credentials
        if config.auth.username:
            try:
                keyring.delete_password(self.KEYRING_SERVICE, config.auth.username)
                print("✅ Keyring credentials cleared")
            except Exception:
                print("⚠️  Could not clear keyring credentials")

        # Remove config file
        if self.CONFIG_FILE.exists():
            self.CONFIG_FILE.unlink()
            print("✅ Configuration file removed")

        print(f"\n👋 Goodbye, {config.auth.username}!")
        print("   You have been logged out successfully")
        print("   Run 'vigil client login' to authenticate again")

    def get_client_config(self) -> ClientConfig:
        """Get client configuration."""
        config = self.load_config()
        if not config:
            raise ValueError("Not authenticated. Run 'vigil client login' first.")

        # Check if token needs refresh (basic check)
        try:
            payload = jwt.decode(config.auth.token or "", options={"verify_signature": False})
            if payload.get('exp') and time.time() > payload.get('exp'):
                if not self.refresh_token():
                    raise ValueError("Token expired and refresh failed. Please login again.")
                config = self.load_config()
        except Exception:
            # If we can't decode, assume valid (Clerk will reject if invalid)
            pass

        return config  # type: ignore[return-value]

    def set_default_project(self, project_id: str) -> None:
        """Set default project."""
        config = self.load_config()
        if config:
            config.default_project = project_id
            self.save_config(config)

    def get_default_project(self) -> str | None:
        """Get default project."""
        config = self.load_config()
        return config.default_project if config else None

    def set_remote_url(self, remote_url: str) -> None:
        """Set remote URL."""
        config = self.load_config()
        if config:
            config.remote.base_url = remote_url
            self.save_config(config)
