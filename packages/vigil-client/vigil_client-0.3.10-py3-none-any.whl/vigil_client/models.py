"""Data models for Vigil platform integration."""

from __future__ import annotations

# Re-export from models for backward compatibility
from .models import (
    Artifact,
    ArtifactStatus,
    ArtifactType,
    AuthConfig,
    ClientConfig,
    Link,
    LinkType,
    PlatformConfig,
    Receipt,
)

__all__ = [
    "Artifact", "ArtifactType", "ArtifactStatus",
    "Receipt",
    "Link", "LinkType",
    "PlatformConfig", "AuthConfig", "ClientConfig"
]
