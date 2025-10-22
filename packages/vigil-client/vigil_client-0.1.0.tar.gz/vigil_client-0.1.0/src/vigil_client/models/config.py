"""Configuration models for vigil-client."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class PlatformConfig(BaseModel):
    """Platform configuration."""

    base_url: str
    api_key: Optional[str] = None
    timeout: int = 30


class AuthConfig(BaseModel):
    """Authentication configuration."""

    token: Optional[str] = None
    refresh_token: Optional[str] = None
    user_id: Optional[str] = None
    username: Optional[str] = None
    organization: Optional[str] = None
    expires_at: Optional[str] = None


class ClientConfig(BaseModel):
    """Complete client configuration."""

    auth: AuthConfig = AuthConfig()
    remote: PlatformConfig
    default_project: Optional[str] = None
