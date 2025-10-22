"""Receipt model for vigil-client."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class Receipt(BaseModel):
    """Receipt model for Vigil platform."""

    id: str | None = None
    schema_version: str = Field(default="1.0.0", alias="$schema")
    owner: str
    pipeline: str
    inputs: list[dict[str, Any]] = Field(default_factory=list)
    outputs: list[dict[str, Any]] = Field(default_factory=list)
    environment: dict[str, Any] = Field(default_factory=dict)
    git: dict[str, Any] = Field(default_factory=dict)
    policies: list[str] = Field(default_factory=list)
    started_at: datetime
    finished_at: datetime
    signature: str
    project_id: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime | None = None
    updated_at: datetime | None = None

    class Config:
        populate_by_name = True
