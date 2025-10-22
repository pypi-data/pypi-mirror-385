"""Configuration utilities for vigil-client."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

from ..models.config import ClientConfig, PlatformConfig, AuthConfig


class ConfigManager:
    """Manages vigil-client configuration."""

    CONFIG_DIR = Path.home() / ".vigil"
    CONFIG_FILE = CONFIG_DIR / "config.json"

    def __init__(self):
        self.CONFIG_DIR.mkdir(exist_ok=True)

    def load_config(self) -> Optional[ClientConfig]:
        """Load configuration from disk."""
        if not self.CONFIG_FILE.exists():
            return None

        try:
            with self.CONFIG_FILE.open("r") as f:
                data = json.load(f)
            return ClientConfig(**data)
        except Exception:
            return None

    def save_config(self, config: ClientConfig) -> None:
        """Save configuration to disk."""
        with self.CONFIG_FILE.open("w") as f:
            json.dump(config.model_dump(), f, indent=2)

    def get_default_remote_url(self) -> str:
        """Get default remote URL from environment or default."""
        return os.environ.get("VIGIL_API_URL", "https://api.cofactor.app")

    def create_default_config(self) -> ClientConfig:
        """Create default configuration."""
        return ClientConfig(
            auth=AuthConfig(),
            remote=PlatformConfig(base_url=self.get_default_remote_url())
        )

    def update_config(self, **kwargs: Any) -> None:
        """Update configuration with new values."""
        config = self.load_config() or self.create_default_config()

        # Update fields
        for key, value in kwargs.items():
            if hasattr(config, key):
                setattr(config, key, value)
            elif hasattr(config.auth, key):
                setattr(config.auth, key, value)
            elif hasattr(config.remote, key):
                setattr(config.remote, key, value)

        self.save_config(config)
