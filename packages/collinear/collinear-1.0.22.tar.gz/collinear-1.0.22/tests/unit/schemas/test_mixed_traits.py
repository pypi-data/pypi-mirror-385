"""Tests for pairwise trait mixing (mix_traits=True)."""

from __future__ import annotations

from typing import cast

import pytest

from collinear.schemas.traitmix import TraitMixConfig
from tests.helpers.runners import CaptureRunner


def make_runner() -> CaptureRunner:
    """Create a CaptureRunner for mix-traits tests."""
    return CaptureRunner()


def test_mixed_combinations_count_and_contents() -> None:
    """When mix_traits=True, generate pairwise combinations of intensities."""
    cfg = TraitMixConfig(
        ages=["18-24", "25-34"],
        genders=["female"],
        occupations=["Employed"],
        intents=["billing", "cancel"],
        traits={
            "confusion": ["high"],
            "impatience": ["medium", "high"],
            "skeptical": ["medium"],
        },
    )

    combos = cfg.combinations(mix_traits=True)

    base = 2 * 1 * 1 * 2
    pair_intensity_products = 5
    assert len(combos) == base * pair_intensity_products

    pair_size = 2
    assert all(len(c.traits) == pair_size for c in combos)


def test_mixed_payload_sends_two_traits() -> None:
    """Runner payload contains exactly two traits when mix_traits=True."""
    runner = make_runner()
    cfg = TraitMixConfig(
        ages=["25-34"],
        genders=["female"],
        occupations=["Employed"],
        intents=["billing"],
        traits={"confusion": ["high"], "impatience": ["medium", "high"]},
        locations=["US"],
        languages=["English"],
        tasks=["telecom"],
    )

    runner.run(config=cfg, k=1, num_exchanges=1, batch_delay=0.0, mix_traits=True, progress=False)
    assert runner.captured_payloads
    payload = runner.captured_payloads[-1][0]

    td = cast("dict[str, str]", payload["trait_dict"])
    assert set(td.keys()) == {"confusion", "impatience"}

    def normalize_level(level: int | str) -> str:
        mapping = {0: "low", 1: "medium", 2: "high"}
        if isinstance(level, int):
            return mapping[level]
        return level.lower()

    expected_confusion_levels = {normalize_level(level) for level in cfg.traits["confusion"]}
    expected_impatience_levels = {normalize_level(level) for level in cfg.traits["impatience"]}
    assert td["confusion"] in expected_confusion_levels
    assert td["impatience"] in expected_impatience_levels


def test_mixing_requires_two_traits() -> None:
    """mix_traits=True requires at least two distinct traits."""
    cfg = TraitMixConfig(
        ages=["25-34"],
        genders=["female"],
        occupations=["Employed"],
        intents=["billing"],
        traits={"confusion": ["high"]},
    )
    with pytest.raises(ValueError, match="at least two traits"):
        cfg.combinations(mix_traits=True)
