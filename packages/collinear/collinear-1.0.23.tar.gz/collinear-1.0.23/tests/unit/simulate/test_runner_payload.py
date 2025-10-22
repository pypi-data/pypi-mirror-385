"""Tests verifying TraitMix API payload shape and configurables."""

from __future__ import annotations

from typing import cast

import pytest

from collinear.schemas.traitmix import TraitMixCombination
from collinear.schemas.traitmix import TraitMixConfig
from tests.helpers.runners import CaptureRunner

DEFAULT_TRAITMIX_TEMP = 0.7
DEFAULT_TRAITMIX_MAX = 256
DEFAULT_TRAITMIX_SEED = -1
OVERRIDE_TRAITMIX_TEMP = 0.33
OVERRIDE_TRAITMIX_MAX = 128
OVERRIDE_SEED = 42


def payload_from_run(
    cfg: TraitMixConfig,
    runner: CaptureRunner | None = None,
) -> dict[str, object]:
    """Execute a minimal run and return the captured TraitMix payload."""
    runner = runner or CaptureRunner()
    runner.run(config=cfg, k=1, num_exchanges=1, batch_delay=0.0, progress=False)
    assert runner.captured_payloads, "expected payload to be captured"
    return runner.captured_payloads[-1][0]


def test_traitmix_payload_uses_trait_dict_and_defaults() -> None:
    """Default payload uses trait_dict, temperature=0.7, max_tokens=256."""
    cfg = TraitMixConfig(
        ages=["25-34"],
        genders=["female"],
        occupations=["Employed"],
        intents=["billing"],
        traits={"impatience": ["medium"]},
        locations=["San Francisco"],
        languages=["English"],
        tasks=["telecom"],
    )

    payload = payload_from_run(cfg)

    assert payload["trait_dict"] == {"impatience": "medium"}
    assert payload["temperature"] == DEFAULT_TRAITMIX_TEMP
    assert payload["max_tokens"] == DEFAULT_TRAITMIX_MAX
    assert payload["seed"] == DEFAULT_TRAITMIX_SEED
    assert payload["messages"] == []

    user_characteristics = cast("dict[str, object]", payload["user_characteristics"])
    assert user_characteristics == {
        "age": "25-34",
        "gender": "female",
        "occupation": "Employed",
        "intent": "billing",
        "location": "San Francisco",
        "language": "English",
        "task": "telecom",
    }


def test_traitmix_payload_respects_overrides() -> None:
    """Overridden runner settings propagate into the payload."""
    runner = CaptureRunner()
    runner.traitmix_temperature = OVERRIDE_TRAITMIX_TEMP
    runner.traitmix_max_tokens = OVERRIDE_TRAITMIX_MAX
    runner.traitmix_seed = OVERRIDE_SEED

    cfg = TraitMixConfig(
        ages=["18-24"],
        genders=["female"],
        occupations=["Employed"],
        intents=["billing"],
        traits={"skeptical": ["high"]},
        locations=["Austin"],
        languages=["English"],
        tasks=["telecom"],
    )

    payload = payload_from_run(cfg, runner)

    assert payload["trait_dict"] == {"skeptical": "high"}
    assert payload["temperature"] == OVERRIDE_TRAITMIX_TEMP
    assert payload["max_tokens"] == OVERRIDE_TRAITMIX_MAX
    assert payload["seed"] == OVERRIDE_SEED

    user_characteristics = cast("dict[str, object]", payload["user_characteristics"])
    assert user_characteristics["task"] == "telecom"


def test_payload_omits_missing_user_characteristics() -> None:
    """Absent user characteristics produce an empty dict."""
    cfg = TraitMixConfig(traits={"impatience": ["medium"]})

    payload = payload_from_run(cfg)

    assert payload["trait_dict"] == {"impatience": "medium"}
    assert payload["messages"] == []
    assert payload["user_characteristics"] == {}


def test_payload_swaps_user_assistant_roles_for_traitmix() -> None:
    """Conversation history sent to traitmix has user/assistant roles flipped."""
    runner = CaptureRunner()

    cfg = TraitMixConfig(
        traits={"impatience": ["medium"]},
        intents=["billing"],
        languages=["English"],
    )

    exchanges = 2
    runner.run(config=cfg, k=1, num_exchanges=exchanges, batch_delay=0.0, progress=False)
    assert len(runner.captured_payloads) >= exchanges

    # Second traitmix call sees the previous user/assistant pair.
    payload = runner.captured_payloads[1][0]
    assert payload["messages"] == [
        {"role": "assistant", "content": "ok"},
        {"role": "user", "content": "assistant"},
    ]


def test_user_characteristics_public_helper_matches_expected() -> None:
    """Public user_characteristics_payload helper returns expected mapping."""
    runner = CaptureRunner()
    combo = TraitMixCombination(
        age="25-34",
        gender="female",
        occupation="Support",
        intent="billing",
        traits={"patience": "low"},
        location="Austin",
        language="English",
        task="telecom",
    )

    expected = {
        "age": "25-34",
        "gender": "female",
        "occupation": "Support",
        "intent": "billing",
        "location": "Austin",
        "language": "English",
        "task": "telecom",
    }

    assert runner.user_characteristics_payload(combo) == expected


def test_invalid_age_range_rejected() -> None:
    """Non-canonical age values raise an error."""
    with pytest.raises(ValueError):
        TraitMixConfig.from_input({"ages": ["30"], "traits": {"impatience": ["medium"]}})


def test_invalid_occupation_rejected() -> None:
    """Occupations outside the approved set fail fast."""
    with pytest.raises(ValueError):
        TraitMixConfig.from_input(
            {
                "occupations": ["teacher"],
                "traits": {"impatience": ["medium"]},
            }
        )
