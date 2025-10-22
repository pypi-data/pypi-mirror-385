"""Authentication and configuration management for Vigil platform."""

from __future__ import annotations

# Re-export from utils for backward compatibility
from .utils.auth import AuthManager, ClientConfig

__all__ = ["AuthManager", "ClientConfig"]

# Create global instance for backward compatibility
auth_manager = AuthManager()
