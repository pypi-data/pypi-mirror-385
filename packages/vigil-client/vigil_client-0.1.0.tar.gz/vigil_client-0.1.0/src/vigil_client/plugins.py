"""Plugin system for Vigil client extensions."""

from __future__ import annotations

import importlib
import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional, Protocol

from .models import Artifact, Link, Receipt


class RunContext:
    """Context information for a pipeline run."""

    def __init__(
        self,
        command: List[str],
        working_dir: Path,
        profile: Optional[str] = None,
        environment: Optional[Dict[str, str]] = None
    ):
        self.command = command
        self.working_dir = working_dir
        self.profile = profile
        self.environment = environment or {}


class VigilPlugin(Protocol):
    """Protocol for Vigil plugins."""

    name: str
    version: str

    def on_run_start(self, context: RunContext) -> None:
        """Called before a pipeline run starts."""
        ...

    def on_run_end(self, context: RunContext, success: bool) -> None:
        """Called after a pipeline run completes."""
        ...

    def extend_receipt(self, receipt: Receipt) -> Receipt:
        """Extend or modify a receipt before it's created."""
        return receipt

    def on_artifact_push(self, artifact: Artifact) -> None:
        """Called when an artifact is pushed to the platform."""
        ...

    def on_artifact_pull(self, artifact: Artifact) -> None:
        """Called when an artifact is pulled from the platform."""
        ...


class BasePlugin(ABC):
    """Base class for Vigil plugins."""

    def __init__(self, name: str, version: str = "1.0.0"):
        self.name = name
        self.version = version

    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize the plugin with configuration."""
        pass

    def on_run_start(self, context: RunContext) -> None:
        """Called before a pipeline run starts."""
        pass

    def on_run_end(self, context: RunContext, success: bool) -> None:
        """Called after a pipeline run completes."""
        pass

    def extend_receipt(self, receipt: Receipt) -> Receipt:
        """Extend or modify a receipt before it's created."""
        return receipt

    def on_artifact_push(self, artifact: Artifact) -> None:
        """Called when an artifact is pushed to the platform."""
        pass

    def on_artifact_pull(self, artifact: Artifact) -> None:
        """Called when an artifact is pulled from the platform."""
        pass


class PluginManager:
    """Manages loading and execution of Vigil plugins."""

    PLUGIN_CONFIG_DIR = Path.home() / ".vigil" / "plugins"
    PLUGIN_CONFIG_FILE = PLUGIN_CONFIG_DIR / "config.json"

    def __init__(self):
        self.plugins: Dict[str, VigilPlugin] = {}
        self.PLUGIN_CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    def load_plugin_config(self) -> Dict[str, Any]:
        """Load plugin configuration from disk."""
        if not self.PLUGIN_CONFIG_FILE.exists():
            return {}

        try:
            return json.loads(self.PLUGIN_CONFIG_FILE.read_text())
        except json.JSONDecodeError:
            return {}

    def save_plugin_config(self, config: Dict[str, Any]) -> None:
        """Save plugin configuration to disk."""
        self.PLUGIN_CONFIG_FILE.write_text(json.dumps(config, indent=2))

    def install_plugin(self, name: str, module_path: str, config: Optional[Dict[str, Any]] = None) -> None:
        """Install a plugin by name."""
        try:
            # Import the plugin module
            module = importlib.import_module(module_path)

            # Get the plugin class (assuming it's named like the module)
            plugin_class = getattr(module, f"{name.replace('-', '_').title()}Plugin")

            # Instantiate and initialize
            plugin = plugin_class()
            plugin.initialize(config or {})

            # Register the plugin
            self.plugins[name] = plugin

            # Update config
            plugin_config = self.load_plugin_config()
            plugin_config[name] = {
                "module": module_path,
                "config": config or {},
                "enabled": True
            }
            self.save_plugin_config(plugin_config)

        except Exception as e:
            raise ValueError(f"Failed to install plugin {name}: {e}")

    def uninstall_plugin(self, name: str) -> None:
        """Uninstall a plugin."""
        if name in self.plugins:
            del self.plugins[name]

        plugin_config = self.load_plugin_config()
        if name in plugin_config:
            del plugin_config[name]
            self.save_plugin_config(plugin_config)

    def load_installed_plugins(self) -> None:
        """Load all installed plugins from configuration."""
        plugin_config = self.load_plugin_config()

        for name, config in plugin_config.items():
            if config.get("enabled", True):
                try:
                    self.install_plugin(name, config["module"], config.get("config"))
                except Exception:
                    # Log error but continue loading other plugins
                    pass

    def get_plugin(self, name: str) -> Optional[VigilPlugin]:
        """Get a plugin by name."""
        return self.plugins.get(name)

    def list_plugins(self) -> List[Dict[str, Any]]:
        """List all installed plugins."""
        plugin_config = self.load_plugin_config()
        plugins = []

        for name, config in plugin_config.items():
            plugin_info = {
                "name": name,
                "module": config["module"],
                "enabled": config.get("enabled", True),
                "version": "unknown"
            }

            if name in self.plugins:
                plugin_info["version"] = getattr(self.plugins[name], "version", "unknown")

            plugins.append(plugin_info)

        return plugins

    # Plugin hook methods
    def notify_run_start(self, context: RunContext) -> None:
        """Notify all plugins that a run is starting."""
        for plugin in self.plugins.values():
            try:
                plugin.on_run_start(context)
            except Exception:
                # Plugin errors shouldn't break the run
                pass

    def notify_run_end(self, context: RunContext, success: bool) -> None:
        """Notify all plugins that a run has ended."""
        for plugin in self.plugins.values():
            try:
                plugin.on_run_end(context, success)
            except Exception:
                pass

    def extend_receipt(self, receipt: Receipt) -> Receipt:
        """Allow plugins to extend the receipt."""
        for plugin in self.plugins.values():
            try:
                receipt = plugin.extend_receipt(receipt)
            except Exception:
                pass
        return receipt

    def notify_artifact_push(self, artifact: Artifact) -> None:
        """Notify plugins when an artifact is pushed."""
        for plugin in self.plugins.values():
            try:
                plugin.on_artifact_push(artifact)
            except Exception:
                pass

    def notify_artifact_pull(self, artifact: Artifact) -> None:
        """Notify plugins when an artifact is pulled."""
        for plugin in self.plugins.values():
            try:
                plugin.on_artifact_pull(artifact)
            except Exception:
                pass


# Global plugin manager instance
plugin_manager = PluginManager()
