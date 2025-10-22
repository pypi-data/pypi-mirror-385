"""Serialization utilities for vigil-client."""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any


class Serializer:
    """Canonical JSON serialization utilities."""

    @staticmethod
    def canonical_json(data: dict[str, Any]) -> str:
        """Serialize data to canonical JSON."""
        return json.dumps(data, sort_keys=True, separators=(",", ":"))

    @staticmethod
    def normalize_timestamp(timestamp: datetime) -> str:
        """Normalize timestamp to ISO format."""
        return timestamp.isoformat() + "Z"

    @staticmethod
    def serialize_receipt(receipt: dict[str, Any]) -> str:
        """Serialize receipt to canonical JSON."""
        # Ensure timestamps are normalized
        if "startedAt" in receipt and isinstance(receipt["startedAt"], datetime):
            receipt["startedAt"] = Serializer.normalize_timestamp(receipt["startedAt"])
        if "finishedAt" in receipt and isinstance(receipt["finishedAt"], datetime):
            receipt["finishedAt"] = Serializer.normalize_timestamp(receipt["finishedAt"])

        return Serializer.canonical_json(receipt)

    @staticmethod
    def serialize_artifact(artifact: dict[str, Any]) -> str:
        """Serialize artifact to canonical JSON."""
        # Ensure timestamps are normalized
        if "created_at" in artifact and isinstance(artifact["created_at"], datetime):
            artifact["created_at"] = Serializer.normalize_timestamp(artifact["created_at"])
        if "updated_at" in artifact and isinstance(artifact["updated_at"], datetime):
            artifact["updated_at"] = Serializer.normalize_timestamp(artifact["updated_at"])

        return Serializer.canonical_json(artifact)
