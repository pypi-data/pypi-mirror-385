"""Data models for vigil-client."""

from .artifact import Artifact, ArtifactType, ArtifactStatus
from .receipt import Receipt
from .link import Link, LinkType
from .config import PlatformConfig, AuthConfig, ClientConfig

__all__ = [
    "Artifact", "ArtifactType", "ArtifactStatus",
    "Receipt",
    "Link", "LinkType",
    "PlatformConfig", "AuthConfig", "ClientConfig"
]
