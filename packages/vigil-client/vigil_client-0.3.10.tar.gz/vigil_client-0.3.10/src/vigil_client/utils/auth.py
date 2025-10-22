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

import jwt  # noqa: F401
import keyring  # noqa: F401
from pydantic import BaseModel

from ..models.config import AuthConfig, ClientConfig, PlatformConfig
from .jwt_validator import JWTValidator


class PlatformAuthConfig(BaseModel):
    """Platform authentication configuration."""

    api_url: str
    redirect_uri: str = "http://localhost:3002/auth/callback"


# ClientConfig is imported from models.config


class AuthManager:
    """Manages authentication and configuration for Vigil client."""

    CONFIG_DIR = Path.home() / ".vigil"
    CONFIG_FILE = CONFIG_DIR / "config.json"
    KEYRING_SERVICE = "vigil-client"

    def __init__(self) -> None:
        self.CONFIG_DIR.mkdir(exist_ok=True)
        self._load_platform_config()
        self._jwt_validator: JWTValidator | None = None

    def _load_platform_config(self) -> None:
        """Load platform configuration from environment or config."""
        # Default to localhost for development
        api_url = os.environ.get("VIGIL_API_URL", "http://localhost:3002")

        self.platform_config = PlatformAuthConfig(
            api_url=api_url,
        )

    def _start_callback_server(self, port: int = 3002) -> tuple[str, threading.Thread]:
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
            base_url = self.platform_config.api_url

        # Get user info from platform using token
        try:
            import requests
            user_response = requests.get(
                f"{base_url}/auth/me",
                headers={'Authorization': f'Bearer {token}'}
            )
            user_response.raise_for_status()
            user_info = user_response.json()

            # Extract user and organization from platform response
            username = user_info.get('username') or user_info.get('email', '').split('@')[0]
            organization = user_info.get('organization_id') or user_info.get('organization', '')

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

    def login_device_flow(self, base_url: str | None = None) -> None:
        """Device code flow authentication - no callback URL needed."""
        if not base_url:
            base_url = self.platform_config.api_url

        import time

        import requests

        # Step 1: Request device code from platform
        try:
            device_response = requests.post(f"{base_url}/auth/device", json={
                "client_id": "vigil-cli",
                "scope": "openid email profile"
            })
            device_response.raise_for_status()
            device_data = device_response.json()
        except Exception as e:
            print(f"❌ Failed to get device code: {e}")
            raise

        # Step 2: Display instructions to user
        print("\n🔐 Vigil Platform Authentication")
        print("=" * 40)
        print(f"Visit: {device_data['verification_uri']}")
        print(f"Enter code: {device_data['user_code']}")
        print("\n⏳ Waiting for authentication...")

        # Step 3: Poll for completion
        device_code = device_data["device_code"]
        interval = device_data.get("interval", 5)
        expires_in = device_data.get("expires_in", 1800)

        start_time = time.time()

        while time.time() - start_time < expires_in:
            try:
                token_response = requests.post(f"{base_url}/auth/device/token", json={
                    "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
                    "device_code": device_code,
                    "client_id": "vigil-cli"
                })

                if token_response.status_code == 200:
                    tokens = token_response.json()
                    # Get user info and save config
                    self._handle_device_flow_success(tokens, base_url)
                    return

                elif token_response.status_code == 400:
                    error_data = token_response.json()
                    if error_data.get("error") == "authorization_pending":
                        time.sleep(interval)
                        continue
                    elif error_data.get("error") == "slow_down":
                        interval += 5
                        time.sleep(interval)
                        continue
                    else:
                        print(f"❌ Authentication failed: {error_data.get('error_description', 'Unknown error')}")
                        return
                else:
                    print(f"❌ Unexpected response: {token_response.status_code}")
                    return

            except KeyboardInterrupt:
                print("\n❌ Authentication cancelled")
                return
            except Exception as e:
                print(f"❌ Authentication error: {e}")
                return

        print("❌ Authentication timed out")

    def _handle_device_flow_success(self, tokens: dict, base_url: str) -> None:
        """Handle successful device flow authentication."""
        access_token = tokens["access_token"]

        # Get user info from platform
        try:
            import requests
            user_response = requests.get(
                f"{base_url}/auth/me",
                headers={'Authorization': f'Bearer {access_token}'}
            )
            user_response.raise_for_status()
            user_info = user_response.json()
        except Exception as e:
            print(f"❌ Failed to get user info: {e}")
            raise

        # Save configuration
        config = ClientConfig(
            auth=AuthConfig(
                token=access_token,
                user_id=user_info["id"],
                username=f"@{user_info['email'].split('@')[0]}",
                organization=f"~{user_info.get('organization_id', 'default')}" if user_info.get('organization_id') else None,
            ),
            remote=PlatformConfig(base_url=base_url),
        )

        self.save_config(config)
        print("✅ Device flow authentication successful!")
        print(f"👤 User: {user_info['email']}")
        if user_info.get('organization_id'):
            print(f"🏢 Organization: {user_info['organization_id']}")
        print(f"🌐 Platform: {base_url}")

    def login_interactive(self, base_url: str | None = None) -> None:
        """Interactive login via platform OAuth with improved UX."""
        if not base_url:
            base_url = self.platform_config.api_url

        # Platform handles OAuth configuration - no client credentials needed

        # Use platform's redirect URI
        redirect_uri = "http://localhost:3002/auth/callback"

        # Get authorization URL from platform
        import requests
        auth_response = requests.get(f"{base_url}/auth/login", params={
            "redirect_uri": redirect_uri,
            "client": "vigil-cli"
        })
        auth_response.raise_for_status()
        auth_data = auth_response.json()
        auth_url = auth_data["auth_url"]

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

                if "localhost:3002/auth/callback" not in callback_url:
                    print("❌ Invalid callback URL. Must contain 'localhost:3002/auth/callback'")
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

            # Exchange code for token via platform
            import requests
            token_data = {
                'code': auth_code,
                'redirect_uri': redirect_uri,
            }

            response = requests.post(
                f"{base_url}/auth/callback",
                json=token_data
            )
            response.raise_for_status()
            token_response = response.json()

            print("✅ Token exchange successful")

            # Use access token as the main token (following AUTH.md spec)
            access_token = token_response.get('access_token')
            if access_token:
                show_spinner("Fetching user information", 0.3)

                # Get user info from platform
                try:
                    user_response = requests.get(
                        f"{base_url}/auth/me",
                        headers={'Authorization': f'Bearer {access_token}'}
                    )
                    user_response.raise_for_status()
                    user_info = user_response.json()

                    # Extract user and organization from platform user info
                    username = user_info.get('username') or user_info.get('email', '').split('@')[0]
                    organization = user_info.get('organization_id') or user_info.get('organization', '')

                    print("✅ User information retrieved")

                except Exception as e:
                    print(f"⚠️  Could not fetch user info: {e}")
                    # Fallback to basic info
                    username = "user"
                    organization = ""

                # Create client config following AUTH.md spec
                from ..models.config import AuthConfig, PlatformConfig
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
            print("   • Verify platform is running and accessible")
            print("   • Ensure redirect URI matches: http://localhost:3002/auth/callback")
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
