"""Data models for Vigil platform integration."""

from __future__ import annotations

# Re-export from models for backward compatibility
from .models import (
    Artifact, ArtifactType, ArtifactStatus,
    Receipt,
    Link, LinkType,
    PlatformConfig, AuthConfig, ClientConfig
)

__all__ = [
    "Artifact", "ArtifactType", "ArtifactStatus",
    "Receipt",
    "Link", "LinkType",
    "PlatformConfig", "AuthConfig", "ClientConfig"
]
