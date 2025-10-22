"""Base HTTP client for vigil-client."""

from __future__ import annotations

import json
from typing import Any

import httpx

from ..models import PlatformConfig


class VigilAPIError(Exception):
    """Error from Vigil platform API."""

    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code


class VigilClient:
    """Base client for interacting with Vigil platform API."""

    def __init__(self, config: PlatformConfig) -> None:
        self.config = config
        self.client = httpx.Client(
            base_url=config.base_url,
            timeout=config.timeout,
            headers=self._get_headers(),
        )

    def _get_headers(self) -> dict[str, str]:
        """Get HTTP headers for API requests following AUTH.md spec."""
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "vigil-client/0.1.0",
        }
        if self.config.api_key:
            headers["Authorization"] = f"Bearer {self.config.api_key}"

        # Add organization header if available (following AUTH.md spec)
        if hasattr(self.config, 'organization') and self.config.organization:
            headers["X-Org"] = self.config.organization

        return headers

    def close(self) -> None:
        """Close the HTTP client."""
        self.client.close()

    def __enter__(self) -> VigilClient:
        return self

    def __exit__(self, _exc_type: object, _exc_val: object, _exc_tb: object) -> None:
        self.close()

    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Make HTTP request to API."""
        try:
            response = self.client.request(
                method=method,
                url=endpoint,
                json=data,
                params=params,
            )
            response.raise_for_status()
            return dict(response.json()) if isinstance(response.json(), dict) else {}
        except httpx.HTTPStatusError as e:
            raise VigilAPIError(f"API request failed: {e.response.text}", e.response.status_code) from e
        except httpx.RequestError as e:
            raise VigilAPIError(f"Request failed: {e}") from e
        except json.JSONDecodeError as e:
            raise VigilAPIError(f"Invalid JSON response: {e}") from e

    def get(self, endpoint: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """Make GET request."""
        return self._make_request("GET", endpoint, params=params)

    def post(self, endpoint: str, data: dict[str, Any] | None = None) -> dict[str, Any]:
        """Make POST request."""
        return self._make_request("POST", endpoint, data=data)

    def put(self, endpoint: str, data: dict[str, Any] | None = None) -> dict[str, Any]:
        """Make PUT request."""
        return self._make_request("PUT", endpoint, data=data)

    def delete(self, endpoint: str) -> dict[str, Any]:
        """Make DELETE request."""
        return self._make_request("DELETE", endpoint)
