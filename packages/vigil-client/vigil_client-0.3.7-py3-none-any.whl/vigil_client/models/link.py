"""Link model for vigil-client."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel


class LinkType(str, Enum):
    """Types of links between artifacts."""

    INPUT_OF = "input_of"
    OUTPUT_OF = "output_of"
    DERIVED_FROM = "derived_from"
    REFERENCES = "references"
    VERSION_OF = "version_of"
    DEFINES = "defines"
    EXECUTED_IN = "executed_in"
    PRODUCED = "produced"


class Link(BaseModel):
    """Link model for Vigil platform."""

    id: str | None = None
    from_artifact_id: str
    to_artifact_id: str
    type: LinkType
    metadata: dict[str, Any] = {}
    created_at: datetime | None = None
    created_by: str | None = None

    class Config:
        use_enum_values = True
