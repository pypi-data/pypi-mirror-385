"""Tests for conversation helper utilities."""

from collinear.simulate.conversation import DEFAULT_ASSISTANT_PROMPT
from collinear.simulate.conversation import should_stop
from collinear.simulate.conversation import swap_roles


def test_swap_roles_flips_user_and_assistant() -> None:
    """Swapping roles reverses user/assistant while keeping others."""
    conversation = [
        {"role": "system", "content": "rules"},
        {"role": "user", "content": "hi"},
        {"role": "assistant", "content": "hello"},
    ]
    swapped = swap_roles(conversation)
    assert swapped == [
        {"role": "system", "content": "rules"},
        {"role": "assistant", "content": "hi"},
        {"role": "user", "content": "hello"},
    ]


def test_should_stop_detects_marker() -> None:
    """Stop detection triggers on explicit markers."""
    assert should_stop("###STOP###")
    assert should_stop("keep going ###STOP### please")
    assert not should_stop("continue")


def test_default_prompt_is_non_empty() -> None:
    """Default assistant prompt contains instructive text."""
    assert "You are the ASSISTANT" in DEFAULT_ASSISTANT_PROMPT
