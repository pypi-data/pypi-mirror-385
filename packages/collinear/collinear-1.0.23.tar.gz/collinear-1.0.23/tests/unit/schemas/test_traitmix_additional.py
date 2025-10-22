"""Additional coverage for traitmix schema helpers."""

from __future__ import annotations

from typing import cast

import pytest
from pydantic import ValidationError

from collinear.schemas.traitmix import TraitMixCombination
from collinear.schemas.traitmix import TraitMixConfig

EXPECTED_MIXED_COUNT = 2


def test_traitmix_config_mixed_generation() -> None:
    """Generate mixed trait combinations covering all trait pairs."""
    cfg = TraitMixConfig(
        ages=["25-34"],
        traits={"patience": ["low", "high"], "empathy": ["medium"]},
    )
    combos = cfg.combinations(mix_traits=True)
    assert len(combos) == EXPECTED_MIXED_COUNT
    for combo in combos:
        assert set(combo.traits) == {"patience", "empathy"}


def test_traitmix_config_mixed_requires_two_traits() -> None:
    """Require at least two traits when mix_traits is enabled."""
    cfg = TraitMixConfig(traits={"patience": ["low"]})
    with pytest.raises(ValueError, match="requires at least two traits"):
        cfg.combinations(mix_traits=True)


def test_traitmix_config_filters_retired_age() -> None:
    """Filter out retired personas with unsupported age ranges."""
    cfg = TraitMixConfig(
        ages=["18-24", "35-44"],
        occupations=["Retired"],
        traits={"patience": ["low"]},
    )
    combos = cfg.combinations()
    assert all(combo.age == "35-44" for combo in combos)


def test_traitmix_from_input_handles_tasks_and_locations() -> None:
    """Support both task and tasks keys during config construction."""
    cfg = TraitMixConfig.from_input(
        {
            "task": "support",
            "locations": ["Austin"],
            "traits": {"patience": [0]},
        }
    )
    assert cfg.tasks == ["support"]
    assert cfg.locations == ["Austin"]
    combos = cfg.combinations()
    assert isinstance(combos[0], TraitMixCombination)


def test_trait_levels_accept_supported_types() -> None:
    """Accept multiple representations of trait levels."""
    cfg = TraitMixConfig(traits={"kind": [True, "2", "low"]})
    levels = {combo.traits["kind"] for combo in cfg.combinations()}
    assert levels == {1, 2, "low"}


def test_trait_levels_reject_invalid_inputs() -> None:
    """Reject unsupported trait levels with informative errors."""
    with pytest.raises(ValueError):
        TraitMixConfig(traits={"kind": ["extreme"]}).combinations()
    invalid_level = cast("int | str", object())
    with pytest.raises(ValidationError):
        TraitMixConfig(traits={"kind": [invalid_level]})
