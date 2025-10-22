"""Links API endpoints for vigil-client."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from ..models import Link, LinkType
from .client import VigilClient


class LinksAPI:
    """API client for link operations."""

    def __init__(self, client: VigilClient):
        self.client = client

    def list_links(
        self,
        artifact_id: Optional[str] = None,
        link_type: Optional[LinkType] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Link]:
        """List links."""
        params = {"limit": limit, "offset": offset}
        if artifact_id:
            params["artifact_id"] = artifact_id
        if link_type:
            params["type"] = link_type.value

        response = self.client.get("/api/v1/links", params=params)
        return [Link(**item) for item in response.get("links", [])]

    def get_link(self, link_id: str) -> Link:
        """Get link by ID."""
        response = self.client.get(f"/api/v1/links/{link_id}")
        return Link(**response)

    def create_link(self, link: Link) -> Link:
        """Create new link."""
        data = link.model_dump(exclude={"id"})
        response = self.client.post("/api/v1/links", data=data)
        return Link(**response)

    def update_link(self, link_id: str, updates: Dict[str, Any]) -> Link:
        """Update link."""
        response = self.client.put(f"/api/v1/links/{link_id}", data=updates)
        return Link(**response)

    def delete_link(self, link_id: str) -> None:
        """Delete link."""
        self.client.delete(f"/api/v1/links/{link_id}")

    def get_provenance_graph(self, artifact_id: str, max_depth: int = 3) -> Dict[str, Any]:
        """Get provenance graph for artifact."""
        params = {"max_depth": max_depth}
        response = self.client.get(f"/api/v1/artifacts/{artifact_id}/provenance", params=params)
        return response
