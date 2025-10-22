"""Unit tests for the SteeringClient helper."""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Literal

import httpx
import pytest
from _pytest.monkeypatch import MonkeyPatch
from typing_extensions import Self

if TYPE_CHECKING:
    from types import TracebackType

from collinear.clients.steering_client import SteeringClient
from collinear.clients.steering_client import normalize_base_url


class DummyResponse:
    """Lightweight httpx.Response stand-in for unit tests."""

    def __init__(self, payload: object) -> None:
        """Store the JSON payload returned by ``json()``."""
        self.payload = payload
        self.status_code = 200
        self.text = "payload"

    def raise_for_status(self) -> None:  # pragma: no cover - tiny shim
        """Mimic httpx.Response.raise_for_status (no-op for 200)."""

    def json(self) -> object:
        """Return the canned payload for assertions."""
        return self.payload


class DummyClient:
    """Context manager that returns canned responses."""

    def __init__(self, response: DummyResponse | None, *, exc: Exception | None = None) -> None:
        """Capture either a response or an exception to raise later."""
        self.response = response
        self.error = exc
        self.calls: list[tuple[str, dict[str, str]]] = []

    def __enter__(self) -> Self:
        """Enter the context manager, returning ``self``."""
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> Literal[False]:  # pragma: no cover - trivial
        """Propagate exceptions when leaving the context manager."""
        return False

    def get(self, url: str, headers: dict[str, str]) -> DummyResponse:
        """Return the configured response while tracking the request."""
        self.calls.append((url, headers))
        if self.error is not None:
            raise self.error
        assert self.response is not None
        return self.response


class DummyAsyncClient:
    """Async client stand-in used to exercise post_json."""

    def __init__(self, response: httpx.Response | None, *, exc: Exception | None = None) -> None:
        """Capture the canned response or exception for the async client."""
        self.response = response
        self.error = exc
        self.calls: list[tuple[str, dict[str, str], object]] = []

    async def __aenter__(self) -> Self:
        """Enter the async context manager, returning ``self``."""
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> Literal[False]:  # pragma: no cover - trivial
        """Propagate exceptions when leaving the async context."""
        return False

    async def post(self, url: str, headers: dict[str, str], json: object) -> httpx.Response:
        """Record the POST invocation and return the canned response."""
        self.calls.append((url, headers, json))
        if self.error is not None:
            raise self.error
        assert self.response is not None
        return self.response


EXPECTED_TIMEOUT = 1.5


def test_normalize_base_url_strips_query() -> None:
    """Normalize base URLs by removing query and fragment components."""
    url = "https://example.test/api?token=demo-token#frag"
    assert normalize_base_url(url) == "https://example.test/api/"


def test_normalize_base_url_defaults() -> None:
    """Return production default when input is empty or None."""
    assert normalize_base_url(None) == "https://steer.collinear.ai/"
    assert normalize_base_url("   ") == "https://steer.collinear.ai/"


def test_list_traits_handles_dict_payload(monkeypatch: MonkeyPatch) -> None:
    """Handle trait lists embedded within dictionaries."""
    response = DummyResponse({"traits": ["kind", 2, None]})
    dummy = DummyClient(response)

    def fake_client(*, timeout: float) -> DummyClient:
        assert timeout == EXPECTED_TIMEOUT
        return dummy

    monkeypatch.setattr(httpx, "Client", fake_client)
    client = SteeringClient(api_key="demo-key", timeout=1.5)

    traits = client.list_traits()

    assert traits == ["kind", "2", "None"]
    assert dummy.calls[0][0].endswith("/traits")
    assert dummy.calls[0][1]["API-Key"] == "demo-key"


def test_list_traits_accepts_list_payload(monkeypatch: MonkeyPatch) -> None:
    """Handle raw list responses by stringifying results."""
    response = DummyResponse(["direct", 17])
    dummy = DummyClient(response)

    def constant_client(*, timeout: float) -> DummyClient:
        del timeout
        return dummy

    monkeypatch.setattr(httpx, "Client", constant_client)
    client = SteeringClient(api_key="demo-key", timeout=1.0)

    traits = client.list_traits()

    assert traits == ["direct", "17"]


def test_list_traits_wraps_errors(monkeypatch: MonkeyPatch) -> None:
    """Wrap HTTP errors in a RuntimeError with helpful messaging."""
    dummy = DummyClient(
        None,
        exc=httpx.TransportError("boom"),
    )

    def error_client(*, timeout: float) -> DummyClient:
        del timeout
        return dummy

    monkeypatch.setattr(httpx, "Client", error_client)
    client = SteeringClient(api_key="demo-key", timeout=1.0)

    with pytest.raises(RuntimeError) as excinfo:
        client.list_traits()

    assert "Failed to fetch TraitMix traits" in str(excinfo.value)


@pytest.mark.asyncio
async def test_post_json_returns_response(monkeypatch: MonkeyPatch) -> None:
    """Return the httpx response when POST succeeds."""
    response = httpx.Response(200)
    dummy = DummyAsyncClient(response)

    def async_client(*, timeout: float) -> DummyAsyncClient:
        del timeout
        return dummy

    monkeypatch.setattr(httpx, "AsyncClient", async_client)
    client = SteeringClient(api_key="demo-key", timeout=1.0)

    resp, err = await client.post_json("https://example", {"h": "v"}, {"field": 1})

    assert err is None
    assert resp is response
    url, headers, payload = dummy.calls[0]
    assert url == "https://example"
    assert headers == {"h": "v"}
    assert payload == {"field": 1}


@pytest.mark.asyncio
async def test_post_json_returns_error_message(monkeypatch: MonkeyPatch) -> None:
    """Surface error messages when the async POST raises an exception."""
    dummy = DummyAsyncClient(None, exc=httpx.TimeoutException("late"))

    def failing_async_client(*, timeout: float) -> DummyAsyncClient:
        del timeout
        return dummy

    monkeypatch.setattr(httpx, "AsyncClient", failing_async_client)
    client = SteeringClient(api_key="demo-key", timeout=1.0)

    resp, err = await client.post_json("https://example", {"h": "v"}, {"field": 1})

    assert resp is None
    assert "TraitMix API call failed" in str(err)


def test_resolve_uses_normalized_env(monkeypatch: MonkeyPatch) -> None:
    """Honor environment overrides when resolving URLs."""
    monkeypatch.setenv("COLLINEAR_TRAITMIX_BASE_URL", "https://stage.collinear.ai/demo")
    client = SteeringClient(api_key="demo-key", timeout=1.0)
    assert client.resolve("/traits") == "https://stage.collinear.ai/demo/traits"
