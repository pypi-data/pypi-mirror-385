"""Vigil Client: Platform integration for artifact management and collaboration."""

__version__ = "0.3.2"

# Core models always available
from .models import Artifact, Link, Receipt

# API client only if dependencies are available
try:
    from .api import VigilClient
    _api_available = True
except ImportError:
    _api_available = False
    VigilClient = None  # type: ignore[misc]

__all__ = ["Artifact", "Link", "Receipt"]

if _api_available:
    __all__.append("VigilClient")
