"""Users API endpoints for vigil-client."""

from __future__ import annotations

from typing import Any

from .client import VigilClient


class UsersAPI:
    """API client for user operations."""

    def __init__(self, client: VigilClient):
        self.client = client

    def get_current_user(self) -> dict[str, Any]:
        """Get current user information."""
        response = self.client.get("/api/v1/users/me")
        return response

    def list_users(
        self,
        organization_id: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        """List users."""
        params = {"limit": limit, "offset": offset}
        if organization_id:
            params["organization_id"] = str(organization_id)

        response = self.client.get("/api/v1/users", params=params)
        users = response.get("users", [])
        return users if isinstance(users, list) else []

    def get_user(self, user_id: str) -> dict[str, Any]:
        """Get user by ID."""
        response = self.client.get(f"/api/v1/users/{user_id}")
        return response

    def update_user(self, user_id: str, updates: dict[str, Any]) -> dict[str, Any]:
        """Update user."""
        response = self.client.put(f"/api/v1/users/{user_id}", data=updates)
        return response

    def get_organizations(self) -> list[dict[str, Any]]:
        """Get user's organizations."""
        response = self.client.get("/api/v1/users/me/organizations")
        orgs = response.get("organizations", [])
        return orgs if isinstance(orgs, list) else []

    def switch_organization(self, organization_id: str) -> dict[str, Any]:
        """Switch to different organization."""
        data = {"organization_id": organization_id}
        response = self.client.post("/api/v1/users/me/switch-organization", data=data)
        return response
