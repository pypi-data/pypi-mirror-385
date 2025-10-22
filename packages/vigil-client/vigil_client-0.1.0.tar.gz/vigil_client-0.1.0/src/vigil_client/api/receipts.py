"""Receipts API endpoints for vigil-client."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

from ..models import Receipt
from .client import VigilClient


class ReceiptsAPI:
    """API client for receipt operations."""

    def __init__(self, client: VigilClient):
        self.client = client

    def list_receipts(
        self,
        project_id: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Receipt]:
        """List receipts."""
        params = {"limit": limit, "offset": offset}
        if project_id:
            params["project_id"] = project_id

        response = self.client.get("/api/v1/receipts", params=params)
        return [Receipt(**item) for item in response.get("receipts", [])]

    def get_receipt(self, receipt_id: str) -> Receipt:
        """Get receipt by ID."""
        response = self.client.get(f"/api/v1/receipts/{receipt_id}")
        return Receipt(**response)

    def push_receipt(self, receipt: Receipt) -> Receipt:
        """Push receipt to platform."""
        data = receipt.model_dump(exclude={"id"})
        response = self.client.post("/api/v1/receipts", data=data)
        return Receipt(**response)

    def register_local_receipt(self, receipt_path: Path) -> Dict[str, Any]:
        """Register local receipt file."""
        import json

        with receipt_path.open("r") as f:
            receipt_data = json.load(f)

        response = self.client.post("/api/v1/receipts", data=receipt_data)
        return response

    def update_receipt(self, receipt_id: str, updates: Dict[str, Any]) -> Receipt:
        """Update receipt."""
        response = self.client.put(f"/api/v1/receipts/{receipt_id}", data=updates)
        return Receipt(**response)

    def delete_receipt(self, receipt_id: str) -> None:
        """Delete receipt."""
        self.client.delete(f"/api/v1/receipts/{receipt_id}")

    def verify_receipt(self, receipt_id: str) -> Dict[str, Any]:
        """Verify receipt signature and integrity."""
        response = self.client.post(f"/api/v1/receipts/{receipt_id}/verify")
        return response
