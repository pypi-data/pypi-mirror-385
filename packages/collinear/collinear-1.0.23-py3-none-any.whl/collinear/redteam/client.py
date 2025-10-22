"""Redteam client for SDK endpoints.

Endpoints:
  - POST /api/v2/sdk/redteam/evaluate
  - GET  /api/v2/sdk/redteam/{evaluation_id}
"""

from __future__ import annotations

import os
import time
from typing import cast
from urllib.parse import urlsplit
from urllib.parse import urlunsplit

import httpx

TERMINAL_STATUSES = {"COMPLETED", "FAILED"}
BASE_URL_ENV_VARS = (
    "COLLINEAR_BACKEND_URL",
    "COLLINEAR_BASE_URL",
    "COLLINEAR_PLATFORM_BASE_URL",
    "COLLINEAR_PLATFORM_URL",
    "COLLINEAR_DASHBOARD_BASE_URL",
    "COLLINEAR_DASHBOARD_URL",
)


def classify_error(error_msg: str) -> str:
    """Classify an error message into a coarse-grained category.

    Args:
        error_msg: The error message string.

    Returns:
        One of: ``LLMRefusalError``, ``RetryError``, ``MissingFieldError``,
        ``MissingStrategyError``, ``KeyError``, ``ValidationError``,
        ``TimeoutError``, ``NetworkError``, or ``UnknownError``.

    """
    error_lower = error_msg.lower()

    result = "UnknownError"
    if "llmrefusalerror" in error_lower or "refusal" in error_lower:
        result = "LLMRefusalError"
    elif "retryerror" in error_lower:
        result = "RetryError"
    elif "keyerror" in error_lower:
        if "approach" in error_lower:
            result = "MissingFieldError"
        elif "strategy" in error_lower:
            result = "MissingStrategyError"
        else:
            result = "KeyError"
    elif "validationerror" in error_lower:
        result = "ValidationError"
    elif "timeout" in error_lower:
        result = "TimeoutError"
    elif "connection" in error_lower or "network" in error_lower:
        result = "NetworkError"
    return result


class RedteamHandle:
    """Handle for polling an SDK redteam evaluation.

    This lightweight wrapper fetches status snapshots from the server and
    exposes helpers to summarize or inspect errors.
    """

    def __init__(
        self,
        *,
        api: RedteamClient,
        evaluation_id: str,
        initial: dict[str, object],
    ) -> None:
        """Create a handle.

        Args:
            api: Underlying transport client.
            evaluation_id: Evaluation identifier.
            initial: Initial payload returned from the create call.

        """
        self.api = api
        self.evaluation_id = str(evaluation_id)
        self.last: dict[str, object] | None = dict(initial)

    @property
    def id(self) -> str:
        """Return the evaluation identifier."""
        return self.evaluation_id

    def status(self, *, refresh: bool = True) -> dict[str, object]:
        """Return the latest status, optionally refreshing from the API."""
        if refresh or self.last is None:
            self.last = self.api.get_result(self.evaluation_id)
        if self.last is None:
            return {}
        return dict(self.last)

    def poll(self, *, timeout: float | None = None, interval: float = 2.0) -> dict[str, object]:
        """Poll until a terminal status or timeout.

        Args:
            timeout: Maximum seconds to wait; ``None`` to wait indefinitely.
            interval: Seconds between polls; must be positive.

        """
        if interval <= 0:
            raise ValueError("interval must be positive")
        start = time.monotonic()
        while True:
            snap = self.status(refresh=True)
            st = str(snap.get("status", "")).upper()
            if st in TERMINAL_STATUSES:
                return snap
            if timeout is not None and (time.monotonic() - start) >= timeout:
                return snap
            time.sleep(interval)

    def get_errors(self) -> dict[str, str]:
        """Get all behavior errors from the last status check.

        Returns:
            Dictionary mapping behavior numbers to error messages.

        """
        result = self.status(refresh=False)
        raw_behaviors = result.get("behaviors", {})
        errors: dict[str, str] = {}
        if isinstance(raw_behaviors, dict):
            for behavior_num, behavior_data in raw_behaviors.items():
                if isinstance(behavior_data, dict):
                    err = behavior_data.get("error")
                    if isinstance(err, str):
                        errors[str(behavior_num)] = err
        return errors

    def has_errors(self) -> bool:
        """Check if any behaviors have errors.

        Returns:
            True if any behavior has an error, False otherwise.

        """
        return len(self.get_errors()) > 0

    def summary(self) -> dict[str, object]:
        """Get a summary of the evaluation results.

        Returns:
            Dictionary containing:
            - total_behaviors: Total number of behaviors evaluated
            - successful: Number of behaviors without errors
            - failed: Number of behaviors with errors
            - errors_by_type: Count of errors grouped by error type
            - status: Overall evaluation status

        """
        result = self.status(refresh=False)
        raw_behaviors = result.get("behaviors", {})
        if isinstance(raw_behaviors, dict):
            behaviors_map: dict[object, object] = cast("dict[object, object]", raw_behaviors)
        else:
            behaviors_map = {}
        total = len(behaviors_map)
        errors = self.get_errors()
        failed = len(errors)
        successful = total - failed

        errors_by_type: dict[str, int] = {}
        for error_msg in errors.values():
            error_type = classify_error(error_msg)
            errors_by_type[error_type] = errors_by_type.get(error_type, 0) + 1

        return {
            "total_behaviors": total,
            "successful": successful,
            "failed": failed,
            "errors_by_type": errors_by_type,
            "status": result.get("status", "UNKNOWN"),
        }


class RedteamClient:
    """HTTP client for Collinear redteam SDK endpoints."""

    def __init__(self, *, timeout: float = 30.0) -> None:
        """Initialize the client with a request timeout."""
        self.timeout = timeout
        self.base_url = resolve_base_url()

    def start(self, payload: dict[str, object]) -> dict[str, object]:
        """Start a redteam evaluation and return the server response."""
        return self.request("POST", "api/v2/sdk/redteam/evaluate", json=payload)

    def get_result(self, evaluation_id: str) -> dict[str, object]:
        """Fetch the current result for an evaluation by id."""
        path = f"api/v2/sdk/redteam/{evaluation_id}"
        return self.request("GET", path)

    def request(
        self,
        method: str,
        path: str,
        *,
        json: dict[str, object] | None = None,
    ) -> dict[str, object]:
        """Send an HTTP request to the redteam API.

        Args:
            method: HTTP method (e.g., "GET", "POST").
            path: API path relative to the base URL.
            json: Optional JSON body.

        Returns:
            JSON-decoded response payload.

        """
        url = f"{self.base_url}{path.lstrip('/')}"
        headers = {"Accept": "application/json"}
        if json is not None:
            headers["Content-Type"] = "application/json"
        try:
            with httpx.Client(timeout=self.timeout) as client:
                resp = client.request(method, url, headers=headers, json=json)
                resp.raise_for_status()
        except httpx.HTTPStatusError as exc:
            try:
                detail_obj: object = exc.response.json()
            except ValueError:
                detail_obj = exc.response.text
            msg = (
                f"SDK redteam request to {path} failed with status "
                f"{exc.response.status_code}: {detail_obj}"
            )
            raise RuntimeError(msg) from exc
        except httpx.HTTPError as exc:
            raise RuntimeError(f"SDK redteam request to {path} failed: {exc!s}") from exc

        if not resp.content:
            return {}
        try:
            return cast("dict[str, object]", resp.json())
        except ValueError as exc:
            raise RuntimeError("SDK redteam response was not valid JSON.") from exc


def resolve_base_url() -> str:
    """Resolve the base URL from environment variables, or default to localhost."""
    for key in BASE_URL_ENV_VARS:
        raw = os.getenv(key)
        if raw:
            try:
                return normalize_base_url(raw)
            except ValueError:
                continue
    # Default to local dev server
    return normalize_base_url("http://localhost:8000/")


def normalize_base_url(raw: str) -> str:
    """Normalize a base URL string, ensuring a scheme and trailing slash."""
    stripped = raw.strip()
    if not stripped:
        raise ValueError("Base URL must be non-empty.")
    parts = urlsplit(stripped)
    scheme = parts.scheme or "http"
    netloc = parts.netloc
    path = parts.path
    if netloc:
        normalized = urlunsplit((scheme, netloc, path, "", ""))
    elif "/" in stripped:
        host, _, remainder = stripped.partition("/")
        normalized = urlunsplit((scheme, host, remainder, "", ""))
    else:
        normalized = urlunsplit((scheme, stripped, "", "", ""))
    if not normalized.endswith("/"):
        normalized += "/"
    return normalized
