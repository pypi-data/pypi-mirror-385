"""Configuration models for vigil-client."""

from __future__ import annotations

from pydantic import BaseModel


class PlatformConfig(BaseModel):
    """Platform configuration."""

    base_url: str
    api_key: str | None = None
    timeout: int = 30


class AuthConfig(BaseModel):
    """Authentication configuration."""

    token: str | None = None
    refresh_token: str | None = None
    user_id: str | None = None
    username: str | None = None
    organization: str | None = None
    expires_at: str | None = None


class ClientConfig(BaseModel):
    """Complete client configuration."""

    auth: AuthConfig = AuthConfig()
    remote: PlatformConfig
    default_project: str | None = None
