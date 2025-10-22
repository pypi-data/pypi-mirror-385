"""Storage API endpoints for vigil-client."""

from __future__ import annotations

from typing import Any, Dict, Optional

from .client import VigilClient


class StorageAPI:
    """API client for storage operations."""

    def __init__(self, client: VigilClient):
        self.client = client

    def get_upload_url(self, artifact_id: str, filename: str) -> Dict[str, Any]:
        """Get presigned upload URL."""
        data = {"filename": filename}
        response = self.client.post(f"/api/v1/storage/upload-url/{artifact_id}", data=data)
        return response

    def get_download_url(self, artifact_id: str) -> str:
        """Get presigned download URL."""
        response = self.client.get(f"/api/v1/storage/download-url/{artifact_id}")
        return response["url"]

    def upload_file(self, upload_url: str, file_path: str) -> None:
        """Upload file to presigned URL."""
        import httpx

        with open(file_path, "rb") as f:
            with httpx.stream("PUT", upload_url, content=f) as response:
                response.raise_for_status()

    def download_file(self, download_url: str, output_path: str) -> None:
        """Download file from presigned URL."""
        import httpx

        with httpx.stream("GET", download_url) as response:
            response.raise_for_status()

            with open(output_path, "wb") as f:
                for chunk in response.iter_bytes():
                    f.write(chunk)
