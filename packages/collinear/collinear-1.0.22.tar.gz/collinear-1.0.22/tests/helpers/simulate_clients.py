"""Shared client stubs for simulation/runner tests."""

from __future__ import annotations

from types import SimpleNamespace
from typing import cast

import httpx
import openai
from openai.types.chat import ChatCompletionMessageParam

from collinear.clients.assistant_client import AssistantClient
from collinear.clients.steering_client import SteeringClient


class StubSteeringClient(SteeringClient):
    """Steering client stub satisfying the runner interface."""

    def __init__(self, traits: list[str], responses: list[str] | None = None) -> None:
        """Initialize with known traits and canned batch responses."""
        self.traits = traits
        self.responses: list[str] = ["ok"] if responses is None else list(responses)
        self.api_key = "stub-key"
        self.timeout = 1.0
        self.base_url = "https://example.test/"

    def list_traits(self) -> list[str]:
        """Return the configured trait list."""
        return list(self.traits)

    async def post_json(
        self, url: str, headers: dict[str, str], payload: object
    ) -> tuple[httpx.Response | None, str | None]:
        """Return a canned HTTPX response containing stubbed TraitMix outputs."""
        del url, headers, payload
        responses_value = cast("list[object]", list(self.responses))
        response_payload = {"responses": responses_value}
        response = httpx.Response(
            200, json=response_payload, request=httpx.Request("POST", "https://example.test")
        )
        return response, None


class ErroringSteeringClient(StubSteeringClient):
    """Stub steering client that produces an explicit error string."""

    async def post_json(
        self, url: str, headers: dict[str, str], payload: object
    ) -> tuple[httpx.Response | None, str | None]:
        """Return ``None`` plus an error string."""
        del url, headers, payload
        return None, "failure"


class ExplodingSteeringClient(StubSteeringClient):
    """Stub steering client that raises an exception when posting."""

    async def post_json(
        self, url: str, headers: dict[str, str], payload: object
    ) -> tuple[httpx.Response | None, str | None]:
        """Raise a runtime error to simulate network failures."""
        del url, headers, payload
        raise RuntimeError("boom")


class NullSteeringClient(StubSteeringClient):
    """Stub steering client returning no response and no error."""

    async def post_json(
        self, url: str, headers: dict[str, str], payload: object
    ) -> tuple[httpx.Response | None, str | None]:
        """Return ``None`` for both response and error fields."""
        del url, headers, payload
        return None, None


class StubAssistantClient(AssistantClient):
    """Assistant client stub exposing an async complete method."""

    def __init__(self) -> None:
        """Populate attributes accessed by the tests that consume this stub."""
        self.model = "stub-assistant"
        self.max_retries = 0
        self.rate_limit_retries = 0
        self.logger = None
        self.client = cast("openai.AsyncOpenAI", SimpleNamespace())

    async def complete(
        self,
        messages: list[ChatCompletionMessageParam],
        system_prompt: str,
        *,
        max_tokens: int | None,
        seed: int | None,
        temperature: float = 0.8,
        max_empty_retries: int = 2,
    ) -> str:
        """Return a canned assistant response."""
        del messages, system_prompt, max_tokens, seed, temperature, max_empty_retries
        return "assistant"
