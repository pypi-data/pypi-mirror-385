"""Artifact model for vigil-client."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

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

    id: Optional[str] = None
    name: str
    type: ArtifactType
    uri: str
    checksum: Optional[str] = None
    size: Optional[int] = None
    description: Optional[str] = None
    status: ArtifactStatus = ArtifactStatus.DRAFT
    project_id: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None

    class Config:
        use_enum_values = True
