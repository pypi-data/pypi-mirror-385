"""Conversation helpers: role swap and stop checks."""

from __future__ import annotations

from typing import TYPE_CHECKING

from openai.types.chat import ChatCompletionMessageParam

if TYPE_CHECKING:  # pragma: no cover - typing-only import for ruff TC003
    from collections.abc import Mapping
    from collections.abc import Sequence

DEFAULT_ASSISTANT_PROMPT = (
    "You are the ASSISTANT. You are a helpful, respectful, and succinct "
    "customer support assistant.\n\n"
    "Respond only to the customer's most recent message. Write only the "
    "assistant's next message as plain text. Do not include role names, quotes, "
    "or any markup. Avoid lists unless the customer explicitly asks for step-by-step "
    "instructions. Keep the reply under 150 words.\n\n"
    "If key details are missing, ask one brief, specific follow-up question. "
    "If you are unsure, say so and suggest a practical next step."
)


def swap_roles(
    conversation: Sequence[Mapping[str, object]] | list[ChatCompletionMessageParam],
) -> list[dict[str, object]]:
    """Flip user/assistant roles for the Steering API while keeping others."""
    out: list[dict[str, object]] = []
    for msg in conversation:
        raw = dict(msg)
        role = str(raw.get("role"))
        if role == "user":
            swapped = "assistant"
        elif role == "assistant":
            swapped = "user"
        else:
            swapped = role
        content = raw.get("content")
        out.append({"role": swapped, "content": "" if content is None else str(content)})
    return out


def should_stop(response: str) -> bool:
    """Return True when a response signals the conversation should conclude."""
    return response == "###STOP###" or "###STOP###" in response
