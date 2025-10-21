"""Unit tests for traitmix configuration helpers."""

from __future__ import annotations

import pytest

from collinear.schemas.traitmix import TraitMixCombination
from collinear.schemas.traitmix import TraitMixConfig
from collinear.schemas.traitmix import TraitMixConfigFactory


def test_combinations_count_and_contents() -> None:
    """Generate all combinations and validate counts and fields."""
    config = TraitMixConfig(
        ages=["18-24", "25-34"],
        genders=["female"],
        occupations=["Employed"],
        intents=["billing"],
        traits={"impatience": ["medium"], "skeptical": ["medium"]},
        tasks=["telecom"],
    )

    combos = config.combinations()

    expected_count = 2 * 1 * 1 * 1 * (1 + 1)
    assert len(combos) == expected_count

    assert {c.age for c in combos} == {"18-24", "25-34"}
    assert {c.trait for c in combos} == {"impatience", "skeptical"}
    assert {c.task for c in combos} == {"telecom"}

    assert all(c.intensity is not None for c in combos)
    assert {c.intensity for c in combos} == {"medium"}


def test_invalid_trait_level_raises() -> None:
    """Unknown trait levels should fail fast."""
    data = {
        "traits": {
            "impatience": ["very_high"],
        }
    }

    with pytest.raises(ValueError, match="invalid level"):
        TraitMixConfig.from_input(data)


def test_integer_trait_level_is_accepted() -> None:
    """Integer levels in [-2,2] are accepted alongside labels."""
    data = {
        "traits": {
            "impatience": [1],
        }
    }

    cfg = TraitMixConfig.from_input(data)
    assert cfg.traits == {"impatience": [1]}


def test_retired_combination_dropped_for_young_age() -> None:
    """Retired personas under 35-44 are excluded from combinations."""
    config = TraitMixConfig(
        ages=["25-34", "35-44"],
        genders=["female"],
        occupations=["Employed", "Retired"],
        intents=["billing"],
        traits={"impatience": ["medium"]},
    )

    combos = config.combinations()
    combo_length = 3

    assert all(not (combo.occupation == "Retired" and combo.age == "25-34") for combo in combos)
    assert any(combo.occupation == "Retired" and combo.age == "35-44" for combo in combos)
    assert len(combos) == combo_length


def test_from_input_collects_task_fields() -> None:
    """Single and plural task keys are normalized into the config."""
    data = {
        "traits": {"impatience": ["medium"]},
        "task": "telecom",
        "tasks": ["retail", ""],
    }

    cfg = TraitMixConfig.from_input(data)
    assert cfg.tasks == ["retail", "telecom"]


def test_traitmix_combination_multi_trait_properties_return_none() -> None:
    """TraitMixCombination properties return None with multiple traits."""
    combo = TraitMixCombination(
        age=None,
        gender=None,
        occupation=None,
        intent=None,
        traits={"impatience": "medium", "skeptical": "high"},
        location=None,
        language=None,
        task=None,
    )
    assert combo.trait is None
    assert combo.intensity is None


def test_traitmix_from_input_requires_mapping() -> None:
    """from_input rejects non-mapping inputs."""
    with pytest.raises(TypeError, match="mapping-like"):
        TraitMixConfig.from_input("not-a-mapping")  # type: ignore[arg-type]


def test_bool_trait_level_is_normalized() -> None:
    """Boolean trait levels are accepted via the public config API."""
    cfg = TraitMixConfig.from_input({"traits": {"curious": [True]}})
    assert cfg.traits == {"curious": [1]}


def test_out_of_range_int_trait_level_rejected() -> None:
    """Out-of-range integers trigger a ValueError through from_input."""
    with pytest.raises(ValueError):
        TraitMixConfig.from_input({"traits": {"curious": [5]}})


def test_out_of_range_string_trait_level_rejected() -> None:
    """Numeric strings beyond the allowed range trigger a ValueError."""
    with pytest.raises(ValueError):
        TraitMixConfig.from_input({"traits": {"curious": ["5"]}})


def test_unknown_label_trait_level_rejected() -> None:
    """Unknown labels raise ValueError via the standard constructor."""
    with pytest.raises(ValueError, match="invalid level"):
        TraitMixConfig.from_input({"traits": {"curious": ["Very High"]}})


def test_unsupported_trait_level_type_rejected() -> None:
    """Unsupported value types raise TypeError via from_input."""
    with pytest.raises(TypeError):
        TraitMixConfig.from_input({"traits": {"curious": [{"bad": 1}]}})


def test_traitmix_factory_get_occupations_type_error() -> None:
    """get_occupations raises when provided a non-list."""
    with pytest.raises(TypeError):
        TraitMixConfigFactory.get_occupations({"occupations": "not-a-list"}, "occupations")


def test_traitmix_factory_get_tasks_trims_inputs() -> None:
    """get_tasks normalizes both plural and singular fields."""
    data = {"tasks": [" retail ", 0, ""], "task": "  sales  "}
    assert TraitMixConfigFactory.get_tasks(data) == ["retail", "sales"]
