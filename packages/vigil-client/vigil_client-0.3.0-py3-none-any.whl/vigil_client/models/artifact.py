"""Artifact model for vigil-client."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class ArtifactType(str, Enum):
    """Types of artifacts in the Vigil ecosystem."""

    DATASET = "dataset"
    MODEL = "model"
    NOTE = "note"
    RECEIPT = "receipt"
    CODE = "code"
    ENVIRONMENT = "environment"
    RUN = "run"


class ArtifactStatus(str, Enum):
    """Status of an artifact."""

    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    DEPRECATED = "deprecated"


class Artifact(BaseModel):
    """Universal artifact model for Vigil platform."""

    id: str | None = None
    name: str
    type: ArtifactType
    uri: str
    checksum: str | None = None
    size: int | None = None
    description: str | None = None
    status: ArtifactStatus = ArtifactStatus.DRAFT
    project_id: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime | None = None
    updated_at: datetime | None = None
    created_by: str | None = None

    class Config:
        use_enum_values = True
