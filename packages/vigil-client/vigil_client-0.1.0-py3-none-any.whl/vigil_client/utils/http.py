"""HTTP utilities for vigil-client."""

from __future__ import annotations

import time
from typing import Any, Dict, Optional

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
        params: Optional[Dict[str, Any]] = None,
        retries: int = 3,
        backoff_factor: float = 0.5,
    ) -> Dict[str, Any]:
        """Make GET request with retry logic."""
        url = f"{self.base_url}{endpoint}"

        for attempt in range(retries + 1):
            try:
                response = self.client.get(url, params=params)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                if attempt == retries or e.response.status_code < 500:
                    raise
                time.sleep(backoff_factor * (2 ** attempt))
            except httpx.RequestError as e:
                if attempt == retries:
                    raise
                time.sleep(backoff_factor * (2 ** attempt))

    def post(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        retries: int = 3,
        backoff_factor: float = 0.5,
    ) -> Dict[str, Any]:
        """Make POST request with retry logic."""
        url = f"{self.base_url}{endpoint}"

        for attempt in range(retries + 1):
            try:
                response = self.client.post(url, json=data)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                if attempt == retries or e.response.status_code < 500:
                    raise
                time.sleep(backoff_factor * (2 ** attempt))
            except httpx.RequestError as e:
                if attempt == retries:
                    raise
                time.sleep(backoff_factor * (2 ** attempt))

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

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()
