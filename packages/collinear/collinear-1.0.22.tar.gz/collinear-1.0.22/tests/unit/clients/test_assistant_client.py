"""Tests covering the assistant client retry behavior."""

from __future__ import annotations

import asyncio

import openai
import pytest

from collinear.clients.assistant_client import AssistantClient
from tests.helpers.logging import RecorderLogger
from tests.helpers.openai import DummyAsyncOpenAI
from tests.helpers.openai import DummyRateLimitError


@pytest.mark.asyncio
async def test_assistant_client_returns_content(monkeypatch: pytest.MonkeyPatch) -> None:
    """AssistantClient should return text when content is present."""

    def make_client(**kwargs: object) -> DummyAsyncOpenAI:
        return DummyAsyncOpenAI(responses=["ok"], **kwargs)

    monkeypatch.setattr(openai, "AsyncOpenAI", make_client)

    client = AssistantClient(
        base_url="https://example.test",
        api_key="test",
        model="gpt",
        timeout=1.0,
        max_retries=3,
        rate_limit_retries=1,
    )

    result = await client.complete([], "system", max_tokens=None, seed=None)
    assert result == "ok"


@pytest.mark.asyncio
async def test_assistant_client_retries_rate_limit(monkeypatch: pytest.MonkeyPatch) -> None:
    """AssistantClient retries rate-limited requests before succeeding."""
    monkeypatch.setattr(openai, "RateLimitError", DummyRateLimitError)

    rate_error = DummyRateLimitError()

    def make_client_rl(**kwargs: object) -> DummyAsyncOpenAI:
        return DummyAsyncOpenAI(responses=[rate_error, "final"], **kwargs)

    monkeypatch.setattr(openai, "AsyncOpenAI", make_client_rl)

    async def fake_sleep(delay_seconds: float) -> None:
        del delay_seconds

    monkeypatch.setattr(asyncio, "sleep", fake_sleep)

    client = AssistantClient(
        base_url="https://example.test",
        api_key="test",
        model="gpt",
        timeout=1.0,
        max_retries=3,
        rate_limit_retries=2,
    )

    result = await client.complete([], "system", max_tokens=None, seed=None)
    assert result == "final"


@pytest.mark.asyncio
async def test_assistant_client_fallback_on_empty(monkeypatch: pytest.MonkeyPatch) -> None:
    """AssistantClient falls back to default text after empty responses."""

    def make_client_empty(**kwargs: object) -> DummyAsyncOpenAI:
        return DummyAsyncOpenAI(responses=["   ", ""], **kwargs)

    monkeypatch.setattr(openai, "AsyncOpenAI", make_client_empty)

    client = AssistantClient(
        base_url="https://example.test",
        api_key="test",
        model="gpt",
        timeout=1.0,
        max_retries=3,
        rate_limit_retries=1,
    )

    result = await client.complete([], "system", max_tokens=None, seed=None, max_empty_retries=1)
    assert "don't have anything" in result


@pytest.mark.asyncio
async def test_assistant_client_rate_limit_exhausts_retries(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """AssistantClient re-raises after exhausting rate-limit retries and logs warnings."""
    monkeypatch.setattr(openai, "RateLimitError", DummyRateLimitError)

    def make_client(**kwargs: object) -> DummyAsyncOpenAI:
        return DummyAsyncOpenAI(responses=[DummyRateLimitError(), DummyRateLimitError()], **kwargs)

    monkeypatch.setattr(openai, "AsyncOpenAI", make_client)

    async def fake_sleep(seconds: float) -> None:
        del seconds

    monkeypatch.setattr(asyncio, "sleep", fake_sleep)

    logger = RecorderLogger()

    client = AssistantClient(
        base_url="https://example.test",
        api_key="test",
        model="gpt",
        timeout=1.0,
        max_retries=1,
        rate_limit_retries=1,
        logger=logger,  # type: ignore[arg-type]
    )

    with pytest.raises(DummyRateLimitError):
        await client.complete([], "system", max_tokens=None, seed=None)

    assert logger.warning_calls, "expected rate-limit warnings to be logged"
