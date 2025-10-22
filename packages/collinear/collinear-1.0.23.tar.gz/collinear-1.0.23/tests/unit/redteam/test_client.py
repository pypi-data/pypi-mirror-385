"""Tests for the redteam HTTP client and handle utilities."""

import time
from typing import cast

import httpx
import pytest

from collinear.redteam.client import RedteamClient
from collinear.redteam.client import RedteamHandle
from collinear.redteam.client import classify_error
from collinear.redteam.client import normalize_base_url
from collinear.redteam.client import resolve_base_url


def test_classify_error_variants() -> None:
    """Different error messages map to expected categories."""
    cases = {
        "LLMRefusalError": "Model refusal to answer",
        "RetryError": "RetryError occurred after attempts",
        "MissingFieldError": "KeyError: 'approach' missing",
        "MissingStrategyError": "KeyError: strategy key missing",
        "KeyError": "KeyError: something else",
        "ValidationError": "ValidationError in payload",
        "TimeoutError": "operation timeout while waiting",
        "NetworkError": "connection error due to network",
        "UnknownError": "some other issue",
    }
    for expected, msg in cases.items():
        assert classify_error(msg) == expected


def test_normalize_base_url_forms() -> None:
    """normalize_base_url accepts various inputs and adds a trailing slash."""
    assert normalize_base_url("example.com").endswith("/")
    assert normalize_base_url("http://example.com").endswith("/")
    assert normalize_base_url("https://example.com/path").endswith("/")
    assert normalize_base_url("example.com/path").endswith("/")
    with pytest.raises(ValueError):
        normalize_base_url("   ")


def test_resolve_base_url_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Environment variables influence base URL resolution order."""
    monkeypatch.delenv("COLLINEAR_BACKEND_URL", raising=False)
    monkeypatch.delenv("COLLINEAR_BASE_URL", raising=False)
    # Fallback to localhost
    assert resolve_base_url().endswith(":8000/")
    # First valid wins
    monkeypatch.setenv("COLLINEAR_BASE_URL", "https://api.example.com")
    assert resolve_base_url().startswith("https://api.example.com")
    # Prefer COLLINEAR_BACKEND_URL over COLLINEAR_BASE_URL
    monkeypatch.setenv("COLLINEAR_BACKEND_URL", "https://backend.example.com")
    assert resolve_base_url().startswith("https://backend.example.com")


class _StubClient(RedteamClient):
    def __init__(self, snapshots: list[dict[str, object]]) -> None:
        super().__init__(timeout=0.1)
        self._snapshots = snapshots
        self._i = 0

    def get_result(self, _evaluation_id: str) -> dict[str, object]:
        snap = self._snapshots[min(self._i, len(self._snapshots) - 1)]
        self._i += 1
        return snap


def test_handle_status_summary_and_poll(monkeypatch: pytest.MonkeyPatch) -> None:
    """Handle summarizes results and polls until completion."""
    snapshots: list[dict[str, object]] = [
        {"status": "RUNNING", "behaviors": {"1": {"error": "ValidationError"}, "2": {}}},
        {"status": "COMPLETED", "behaviors": {"1": {"error": "ValidationError"}, "2": {}}},
    ]
    api = _StubClient(snapshots)
    h = RedteamHandle(
        api=api,
        evaluation_id="demo-run",
        initial=snapshots[0],
    )

    # status without refresh should return the initial snap
    assert h.status(refresh=False)["status"] == "RUNNING"
    # summary aggregates
    s = h.summary()
    expected_total = 2
    assert s["total_behaviors"] == expected_total
    assert s["failed"] == 1
    assert s["successful"] == 1

    # poll advances to terminal status
    def _sleep(_s: float) -> None:
        return None

    monkeypatch.setattr(time, "sleep", _sleep)
    final = h.poll(timeout=1.0, interval=0.001)
    assert final["status"] == "COMPLETED"


def test_client_request_error_json(monkeypatch: pytest.MonkeyPatch) -> None:
    """HTTPStatusError yields a RuntimeError with details."""

    # Stub httpx.Client to raise HTTPStatusError with a JSON body
    class FailingClient(httpx.Client):
        def request(self, *_: object, **__: object) -> httpx.Response:
            req = httpx.Request("GET", "http://test")
            resp = httpx.Response(
                400,
                request=req,
                content=b'{"detail":"bad"}',
                headers={"content-type": "application/json"},
            )
            raise httpx.HTTPStatusError("boom", request=req, response=resp)

    monkeypatch.setattr(httpx, "Client", cast("type[httpx.Client]", FailingClient))
    c = RedteamClient(timeout=0.1)
    payload: dict[str, object] = {}
    with pytest.raises(RuntimeError):
        c.start(payload)
