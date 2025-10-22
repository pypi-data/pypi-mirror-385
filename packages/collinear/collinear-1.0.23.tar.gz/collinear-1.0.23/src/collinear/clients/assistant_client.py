"""Thin wrapper around an OpenAI-compatible Chat Completions client."""

from __future__ import annotations

import asyncio
import random
from typing import TYPE_CHECKING

import openai
from openai.types.chat import ChatCompletionMessageParam

if TYPE_CHECKING:
    import logging


class AssistantClient:
    """Async assistant client with simple retry and empty-response handling."""

    def __init__(
        self,
        *,
        base_url: str,
        api_key: str,
        model: str,
        timeout: float,
        max_retries: int,
        rate_limit_retries: int,
        logger: logging.Logger | None = None,
    ) -> None:
        """Initialize the assistant client wrapper."""
        self.model = model
        self.max_retries = int(max_retries)
        self.rate_limit_retries = int(rate_limit_retries)
        self.logger = logger
        self.client = openai.AsyncOpenAI(
            base_url=base_url,
            api_key=api_key,
            timeout=timeout,
            max_retries=max_retries,
        )

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
        """Create a completion with small conveniences for robustness."""
        sys_msg: ChatCompletionMessageParam = {"role": "system", "content": system_prompt}
        full: list[ChatCompletionMessageParam] = [sys_msg, *messages]

        attempt = 0
        while True:
            try:
                resp = await self.client.chat.completions.create(
                    model=self.model,
                    messages=full,
                    temperature=temperature,
                    max_tokens=(max_tokens if max_tokens is not None else openai.NOT_GIVEN),
                    seed=(seed if seed is not None else openai.NOT_GIVEN),
                )
            except openai.RateLimitError as exc:
                attempt += 1
                if self.logger is not None:
                    self.logger.warning("Rate limit hit, attempt %s: %s", attempt, exc)
                if attempt > self.rate_limit_retries:
                    raise
                delay = min(60.0, max(1.0, (2.0 ** (attempt - 1)) + random.random()))
                await asyncio.sleep(delay)
            else:
                content = resp.choices[0].message.content or ""
                if content.strip():
                    return content
                # Empty content: retry a couple times before returning fallback
                if max_empty_retries <= 0:
                    return "I'm sorry, I don't have anything to add right now."
                max_empty_retries -= 1
