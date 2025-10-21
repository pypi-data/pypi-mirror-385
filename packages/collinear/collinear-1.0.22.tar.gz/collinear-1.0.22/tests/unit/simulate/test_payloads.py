"""Tests for payload construction helpers."""

from typing import cast

import pytest

from collinear.schemas.traitmix import TraitMixCombination
from collinear.simulate.payloads import build_traitmix_payload
from collinear.simulate.payloads import level_to_label
from collinear.simulate.payloads import user_characteristics_from_combo


def make_combo() -> TraitMixCombination:
    """Return a sample trait mix combination for payload tests."""
    return TraitMixCombination(
        age="25-34",
        gender="female",
        occupation="Employed",
        intent="billing",
        traits={"impatience": "medium"},
        location="US",
        language="English",
        task="telecom",
    )


def test_build_traitmix_payload_normalizes_levels() -> None:
    """Levels are normalized to human-readable labels."""
    combo = make_combo()
    payload = build_traitmix_payload(
        trait_dict={"impatience": 2},
        conversation=[{"role": "user", "content": "hi"}],
        combo=combo,
        temperature=0.7,
        max_tokens=256,
        seed=-1,
    )
    assert payload["trait_dict"] == {"impatience": "high"}
    user_characteristics = cast("dict[str, object]", payload["user_characteristics"])
    assert user_characteristics["age"] == "25-34"
    messages = cast("list[dict[str, object]]", payload["messages"])
    assert messages[0]["role"] == "assistant"


def test_build_traitmix_payload_rejects_invalid_level() -> None:
    """Invalid trait levels raise a clear ValueError."""
    combo = make_combo()
    with pytest.raises(ValueError, match="Unknown trait level"):
        build_traitmix_payload(
            trait_dict={"impatience": "very"},
            conversation=[],
            combo=combo,
            temperature=0.7,
            max_tokens=256,
            seed=-1,
        )


@pytest.mark.parametrize("value", [3, "3", -1])
def test_level_to_label_rejects_out_of_range(value: int | str) -> None:
    """Out-of-range numeric levels raise ValueError."""
    combo = make_combo()
    with pytest.raises(ValueError):
        build_traitmix_payload(
            trait_dict={"impatience": value},
            conversation=[],
            combo=combo,
            temperature=0.7,
            max_tokens=256,
            seed=-1,
        )


def test_level_to_label_accepts_bool() -> None:
    """Boolean inputs are coerced to their numeric counterparts."""
    assert level_to_label(value=True) == "medium"


def test_level_to_label_trims_and_lowercases() -> None:
    """String inputs are trimmed and normalized to lowercase."""
    assert level_to_label(" High ") == "high"


def test_level_to_label_accepts_numeric_string() -> None:
    """Digit-only strings map to canonical labels."""
    assert level_to_label("0") == "low"
    assert level_to_label("2") == "high"


def test_user_characteristics_from_combo_omits_blank_values() -> None:
    """Optional persona attributes are trimmed and omitted when empty."""
    combo = TraitMixCombination(
        age=None,
        gender=" ",
        occupation="Engineer ",
        intent=None,
        traits={"impatience": "medium"},
        location="   ",
        language="English ",
        task="",
    )
    payload = user_characteristics_from_combo(combo)
    assert "gender" not in payload
    assert "location" not in payload
    assert "task" not in payload
    assert payload["occupation"] == "Engineer"
    assert payload["language"] == "English"
