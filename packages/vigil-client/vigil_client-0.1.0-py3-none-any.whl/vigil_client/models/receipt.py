"""Receipt model for vigil-client."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class Receipt(BaseModel):
    """Receipt model for Vigil platform."""

    id: Optional[str] = None
    schema_version: str = Field(default="1.0.0", alias="$schema")
    owner: str
    pipeline: str
    inputs: List[Dict[str, Any]] = Field(default_factory=list)
    outputs: List[Dict[str, Any]] = Field(default_factory=list)
    environment: Dict[str, Any] = Field(default_factory=dict)
    git: Dict[str, Any] = Field(default_factory=dict)
    policies: List[str] = Field(default_factory=list)
    started_at: datetime
    finished_at: datetime
    signature: str
    project_id: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        populate_by_name = True
