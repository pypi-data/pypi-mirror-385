"""Artifacts API endpoints for vigil-client."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

from ..models import Artifact, ArtifactType
from .client import VigilClient


class ArtifactsAPI:
    """API client for artifact operations."""

    def __init__(self, client: VigilClient):
        self.client = client

    def list_artifacts(
        self,
        project_id: Optional[str] = None,
        type_filter: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Artifact]:
        """List artifacts."""
        params = {"limit": limit, "offset": offset}
        if project_id:
            params["project_id"] = project_id
        if type_filter:
            params["type"] = type_filter

        response = self.client.get("/api/v1/artifacts", params=params)
        return [Artifact(**item) for item in response.get("artifacts", [])]

    def get_artifact(self, artifact_id: str) -> Artifact:
        """Get artifact by ID."""
        response = self.client.get(f"/api/v1/artifacts/{artifact_id}")
        return Artifact(**response)

    def create_artifact(self, artifact: Artifact) -> Artifact:
        """Create new artifact."""
        data = artifact.model_dump(exclude={"id"})
        response = self.client.post("/api/v1/artifacts", data=data)
        return Artifact(**response)

    def update_artifact(self, artifact_id: str, updates: Dict[str, Any]) -> Artifact:
        """Update artifact."""
        response = self.client.put(f"/api/v1/artifacts/{artifact_id}", data=updates)
        return Artifact(**response)

    def delete_artifact(self, artifact_id: str) -> None:
        """Delete artifact."""
        self.client.delete(f"/api/v1/artifacts/{artifact_id}")

    def search_artifacts(self, query: str, project_id: Optional[str] = None) -> List[Artifact]:
        """Search artifacts by name or description."""
        params = {"q": query}
        if project_id:
            params["project_id"] = project_id

        response = self.client.get("/api/v1/artifacts/search", params=params)
        return [Artifact(**item) for item in response.get("artifacts", [])]

    def push_artifact_with_file(self, artifact: Artifact, file_path: Path) -> Artifact:
        """Upload artifact with file."""
        # First create the artifact
        created_artifact = self.create_artifact(artifact)

        # Then upload the file
        upload_url = self.client.get(f"/api/v1/storage/upload-url/{created_artifact.id}")

        # Upload file to presigned URL
        import httpx
        with file_path.open("rb") as f:
            with httpx.stream("PUT", upload_url["url"], content=f) as response:
                response.raise_for_status()

        return created_artifact
