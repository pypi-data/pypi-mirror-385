"""Shared OpenAI client test doubles (sync + async)."""

from __future__ import annotations

from types import SimpleNamespace
from typing import Protocol
from typing import cast


class DummyCompletions:
    """Minimal stub for the chat completions interface (async)."""

    def __init__(self, responses: list[object]) -> None:
        """Initialize with a queue of canned responses or exceptions."""
        self.responses = list(responses)

    async def create(self, **unused_kwargs: object) -> object:
        """Return the next response as an OpenAI-like result object."""
        del unused_kwargs
        if not self.responses:
            raise AssertionError("No more responses configured")
        result = self.responses.pop(0)
        if isinstance(result, Exception):
            raise result
        choices: list[object] = [SimpleNamespace(message=SimpleNamespace(content=result))]
        return SimpleNamespace(choices=choices)


class DummyChat:
    """Container exposing the async completions stub."""

    def __init__(self, responses: list[object]) -> None:
        """Attach a DummyCompletions instance for the given responses."""
        self.completions = DummyCompletions(responses)


class DummyAsyncOpenAI:
    """Drop-in replacement for ``openai.AsyncOpenAI`` during tests."""

    def __init__(self, *, responses: list[object], **unused_kwargs: object) -> None:
        """Expose an attribute `chat` with a DummyChat instance."""
        del unused_kwargs
        self.chat = DummyChat(responses)


class CreateCallable(Protocol):
    """Protocol for the fake completion factory used in sync tests."""

    def __call__(self, **kwargs: object) -> SimpleNamespace:
        """Create a completion result namespace."""


class DummyOpenAI:
    """Simplified ``openai.OpenAI`` stand-in for sync paths."""

    def __init__(self, *, base_url: str, api_key: str, timeout: float) -> None:
        """Record constructor args and prepare a fixed scoring response."""
        self.kwargs = {"base_url": base_url, "api_key": api_key, "timeout": timeout}
        content = '{"score": 5, "rationale": "clear"}'
        message = SimpleNamespace(content=content)
        choice = SimpleNamespace(message=message)
        choices_list: list[SimpleNamespace] = [choice]
        completions = SimpleNamespace(create=self.create_factory(choices_list))
        self.chat = SimpleNamespace(completions=completions)

    @staticmethod
    def create_factory(choices: list[SimpleNamespace]) -> CreateCallable:
        """Return a function that mimics `chat.completions.create`.

        The returned function validates parameters and returns the prepared choices.
        """

        def create(**kwargs: object) -> SimpleNamespace:
            params: dict[str, object] = dict(kwargs)
            messages = cast("list[dict[str, object]]", params["messages"])
            assert messages[0]["role"] == "system"
            assert messages[1]["role"] == "user"
            # Many tests expect specific model names to make it into the call.
            assert params.get("model") is not None
            choices_copy: list[SimpleNamespace] = list(choices)
            return SimpleNamespace(choices=choices_copy)

        return create


class DummyRateLimitError(Exception):
    """Simple exception used to stand in for ``openai.RateLimitError``."""
