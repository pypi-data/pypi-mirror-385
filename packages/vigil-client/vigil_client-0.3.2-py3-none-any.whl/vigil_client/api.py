"""API client for Vigil platform integration."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import httpx

from .api.artifacts import ArtifactsAPI
from .api.client import VigilClient as BaseVigilClient
from .api.links import LinksAPI
from .api.receipts import ReceiptsAPI
from .api.storage import StorageAPI
from .api.users import UsersAPI
from .models import Artifact, Link, PlatformConfig, Receipt


class VigilClient(BaseVigilClient):
    """Enhanced client for interacting with Vigil platform API."""

    def __init__(self, config: PlatformConfig):
        super().__init__(config)
        self.artifacts = ArtifactsAPI(self)
        self.receipts = ReceiptsAPI(self)
        self.links = LinksAPI(self)
        self.storage = StorageAPI(self)
        self.users = UsersAPI(self)

    # Artifact operations
    def create_artifact(self, artifact: Artifact) -> Artifact:
        """Create a new artifact in the platform."""
        response = self.client.post("/api/v1/artifacts", json=artifact.dict(exclude_unset=True))
        self._handle_response(response)
        return Artifact(**response.json())

    def get_artifact(self, artifact_id: str) -> Artifact:
        """Get an artifact by ID."""
        response = self.client.get(f"/api/v1/artifacts/{artifact_id}")
        self._handle_response(response)
        return Artifact(**response.json())

    def update_artifact(self, artifact_id: str, updates: dict[str, Any]) -> Artifact:
        """Update an existing artifact."""
        response = self.client.patch(f"/api/v1/artifacts/{artifact_id}", json=updates)
        self._handle_response(response)
        return Artifact(**response.json())

    def list_artifacts(self, project_id: str | None = None, type_filter: str | None = None) -> list[Artifact]:
        """List artifacts with optional filtering."""
        params = {}
        if project_id:
            params["project_id"] = project_id
        if type_filter:
            params["type"] = type_filter

        response = self.client.get("/api/v1/artifacts", params=params)
        self._handle_response(response)
        return [Artifact(**item) for item in response.json()]

    # Link operations
    def create_link(self, link: Link) -> Link:
        """Create a provenance link between artifacts."""
        response = self.client.post("/api/v1/links", json=link.dict(by_alias=True, exclude_unset=True))
        self._handle_response(response)
        return Link(**response.json())

    def get_links(self, artifact_id: str) -> list[Link]:
        """Get all links for an artifact."""
        response = self.client.get("/api/v1/links", params={"artifact_id": artifact_id})
        self._handle_response(response)
        return [Link(**item) for item in response.json()]

    # Receipt operations
    def push_receipt(self, receipt: Receipt) -> dict[str, Any]:
        """Push a receipt to the platform."""
        response = self.client.post("/api/v1/receipts", json=receipt.dict())
        self._handle_response(response)
        return response.json()

    def get_receipt(self, receipt_id: str) -> Receipt:
        """Get a receipt from the platform."""
        response = self.client.get(f"/api/v1/receipts/{receipt_id}")
        self._handle_response(response)
        return Receipt(**response.json())

    # Graph operations
    def get_provenance_graph(self, artifact_id: str) -> dict[str, Any]:
        """Get the full provenance graph for an artifact."""
        response = self.client.get(f"/api/v1/graph/{artifact_id}")
        self._handle_response(response)
        return response.json()

    # Storage operations
    def get_upload_url(self, filename: str, content_type: str = "application/octet-stream") -> dict[str, str]:
        """Get a presigned URL for uploading to storage."""
        response = self.client.post(
            "/api/v1/storage/upload-url",
            json={"filename": filename, "content_type": content_type}
        )
        self._handle_response(response)
        return response.json()

    def get_download_url(self, artifact_id: str) -> str:
        """Get a download URL for an artifact."""
        response = self.client.get(f"/api/v1/artifacts/{artifact_id}/download")
        self._handle_response(response)
        return response.json()["url"]

    def _handle_response(self, response: httpx.Response) -> None:
        """Handle HTTP response and raise appropriate errors."""
        if response.status_code >= 400:
            try:
                error_data = response.json()
                message = error_data.get("message", f"API error: {response.status_code}")
            except json.JSONDecodeError:
                message = f"API error: {response.status_code} - {response.text}"
            from .api.client import VigilAPIError
            raise VigilAPIError(message, response.status_code)

    # High-level convenience methods
    def push_artifact_with_file(self, artifact: Artifact, file_path: Path) -> Artifact:
        """Create artifact and upload associated file."""
        # Get upload URL
        upload_info = self.get_upload_url(artifact.name)

        # Upload file
        with file_path.open("rb") as f:
            upload_response = httpx.put(
                upload_info["url"],
                content=f,
                headers={"Content-Type": upload_info.get("content_type", "application/octet-stream")}
            )
            upload_response.raise_for_status()

        # Update artifact URI and create in platform
        artifact.uri = upload_info["final_uri"]
        return self.create_artifact(artifact)

    def register_local_receipt(self, receipt_path: Path) -> dict[str, Any]:
        """Register a local receipt file with the platform."""
        receipt_data = json.loads(receipt_path.read_text())
        receipt = Receipt(**receipt_data)
        return self.push_receipt(receipt)
