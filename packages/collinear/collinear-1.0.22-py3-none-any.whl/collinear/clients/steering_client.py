"""HTTP client for the Steering (TraitMix) API."""

from __future__ import annotations

import os
from typing import cast
from urllib.parse import urlsplit
from urllib.parse import urlunsplit

import httpx


def normalize_base_url(raw: str | None) -> str:
    """Normalize the configured base URL, falling back to production.

    Historically the SDK ignored any query string or fragment supplied via
    COLLINEAR_TRAITMIX_{BASE,}URL so that endpoint resolution would append
    paths like "/traits" to the host and path only. Some proxy/staging
    environments attach signed query parameters (e.g., "?token=abc").
    If we were to keep those when joining, we'd emit URLs like
    ".../steer?token=abc/traits" which many servers treat as distinct paths
    and return 404. To preserve the previous behavior, strip query/fragment
    and ensure a single trailing slash.
    """
    base = (raw or "").strip()
    if not base:
        return "https://steer.collinear.ai/"

    parts = urlsplit(base)
    # Drop query and fragment; keep scheme, netloc, and path as-is.
    base_no_qf = urlunsplit((parts.scheme, parts.netloc, parts.path, "", ""))
    if not base_no_qf.endswith("/"):
        base_no_qf += "/"
    return base_no_qf


class SteeringClient:
    """Minimal client for Steering API endpoints used by the SDK."""

    def __init__(self, *, api_key: str, timeout: float) -> None:
        """Store shared connection settings for subsequent requests."""
        base = os.getenv("COLLINEAR_TRAITMIX_BASE_URL") or os.getenv("COLLINEAR_TRAITMIX_URL")
        self.base_url = normalize_base_url(base)
        self.api_key = api_key
        self.timeout = timeout

    def list_traits(self) -> list[str]:
        """Fetch the trait list, returning [] on errors."""
        url = self.resolve("traits")
        try:
            with httpx.Client(timeout=self.timeout) as client:
                resp = client.get(url, headers={"API-Key": self.api_key})
                resp.raise_for_status()
                raw = cast("object", resp.json())
        except Exception as exc:
            message = (
                "Failed to fetch TraitMix traits. "
                f"Details: {exc!s}. Check COLLINEAR_API_KEY and connection settings."
            )
            raise RuntimeError(message) from exc
        if isinstance(raw, dict):
            traits_field = cast("object", raw.get("traits"))
            if isinstance(traits_field, list):
                return [str(t) for t in traits_field]
        if isinstance(raw, list):
            return [str(t) for t in cast("list[object]", raw)]
        return []

    async def post_json(
        self, url: str, headers: dict[str, str], payload: object
    ) -> tuple[httpx.Response | None, str | None]:
        """POST JSON to an arbitrary URL. Maintains the SDK's tuple contract."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.post(url, headers=headers, json=payload)
                return resp, None
        except Exception as e:
            return None, (
                "Error: TraitMix API call failed. Details: "
                f"{e!s}. Check COLLINEAR_API_KEY and COLLINEAR_TRAITMIX_URL."
            )

    def resolve(self, endpoint: str) -> str:
        """Build a fully-qualified URL for the given endpoint."""
        endpoint = endpoint.lstrip("/")
        return f"{self.base_url}{endpoint}"
