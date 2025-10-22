"""Data models for vigil-client."""

from .artifact import Artifact, ArtifactStatus, ArtifactType
from .config import AuthConfig, ClientConfig, PlatformConfig
from .link import Link, LinkType
from .receipt import Receipt

__all__ = [
    "Artifact", "ArtifactType", "ArtifactStatus",
    "Receipt",
    "Link", "LinkType",
    "PlatformConfig", "AuthConfig", "ClientConfig"
]
