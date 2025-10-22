"""HTTP utilities for vigil-client."""

from __future__ import annotations

import time
from typing import Any

import httpx


class HTTPClient:
    """Enhanced HTTP client with retry and backoff."""

    def __init__(self, base_url: str, timeout: int = 30):
        self.base_url = base_url
        self.timeout = timeout
        self.client = httpx.Client(timeout=timeout)

    def get(
        self,
        endpoint: str,
        params: dict[str, Any] | None = None,
        retries: int = 3,
        backoff_factor: float = 0.5,
    ) -> dict[str, Any]:
        """Make GET request with retry logic."""
        url = f"{self.base_url}{endpoint}"

        for attempt in range(retries + 1):
            try:
                response = self.client.get(url, params=params)
                response.raise_for_status()
                return dict(response.json()) if isinstance(response.json(), dict) else {}
            except httpx.HTTPStatusError as e:
                if attempt == retries or e.response.status_code < 500:
                    raise
                time.sleep(backoff_factor * (2 ** attempt))
            except httpx.RequestError:
                if attempt == retries:
                    raise
                time.sleep(backoff_factor * (2 ** attempt))

        # This should never be reached, but mypy needs it
        raise httpx.RequestError("Max retries exceeded")

    def post(
        self,
        endpoint: str,
        data: dict[str, Any] | None = None,
        retries: int = 3,
        backoff_factor: float = 0.5,
    ) -> dict[str, Any]:
        """Make POST request with retry logic."""
        url = f"{self.base_url}{endpoint}"

        for attempt in range(retries + 1):
            try:
                response = self.client.post(url, json=data)
                response.raise_for_status()
                return dict(response.json()) if isinstance(response.json(), dict) else {}
            except httpx.HTTPStatusError as e:
                if attempt == retries or e.response.status_code < 500:
                    raise
                time.sleep(backoff_factor * (2 ** attempt))
            except httpx.RequestError:
                if attempt == retries:
                    raise
                time.sleep(backoff_factor * (2 ** attempt))

        # This should never be reached, but mypy needs it
        raise httpx.RequestError("Max retries exceeded")

    def stream_download(self, url: str, output_path: str) -> None:
        """Stream download with progress."""
        with self.client.stream("GET", url) as response:
            response.raise_for_status()

            with open(output_path, "wb") as f:
                for chunk in response.iter_bytes():
                    f.write(chunk)

    def close(self) -> None:
        """Close the HTTP client."""
        self.client.close()

    def __enter__(self) -> HTTPClient:
        return self

    def __exit__(self, _exc_type: object, _exc_val: object, _exc_tb: object) -> None:
        self.close()
