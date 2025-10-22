"""Tests for k selection behavior in SimulationRunner.run.

Covers default k=None (all combos, deterministic order),
k >= total (all combos, deterministic order), and k < total
which should use random.sample to select a random subset.
"""

from __future__ import annotations

import random
from typing import cast

from _pytest.monkeypatch import MonkeyPatch
from openai.types.chat import ChatCompletionMessageParam

from collinear.schemas.traitmix import Role
from collinear.schemas.traitmix import TraitMixCombination
from collinear.schemas.traitmix import TraitMixConfig
from collinear.simulate.runner import SimulationRunner


async def fake_generate(
    runner_instance: SimulationRunner,
    combo: TraitMixCombination,
    conversation: list[ChatCompletionMessageParam],
    role: Role,
) -> str:
    """Return deterministic user/assistant placeholders for testing."""
    del runner_instance, combo, conversation
    return "u" if role is Role.USER else "a"


def build_runner(monkeypatch: MonkeyPatch) -> SimulationRunner:
    """Create a SimulationRunner wired to the fake generate helper."""
    monkeypatch.setattr(SimulationRunner, "generate_turn", fake_generate)
    return SimulationRunner(
        assistant_model_url="https://example.test",
        assistant_model_api_key="k",
        assistant_model_name="gpt-test",
        collinear_api_key="demo-001",
    )


def build_config() -> TraitMixConfig:
    """Return a sample TraitMixConfig with multiple axes."""
    return TraitMixConfig(
        ages=["18-24", "25-34"],
        genders=["female"],
        occupations=["Employed"],
        intents=["billing", "cancel"],
        traits={"impatience": ["medium"], "skeptical": ["high"]},
        locations=["US"],
        languages=["English"],
        tasks=["telecom"],
    )


def signature_for(c: TraitMixCombination) -> tuple[str, str, str, str, str, str]:
    """Convert a combination into a tuple signature for comparisons."""
    assert c.trait is not None
    assert c.intensity is not None
    intensity = str(c.intensity)
    return (
        str(c.age),
        cast("str", c.gender),
        cast("str", c.occupation),
        cast("str", c.intent),
        c.trait,
        intensity,
    )


def test_k_none_runs_all_combinations_in_order(monkeypatch: MonkeyPatch) -> None:
    """Default k=None runs all combos in deterministic order."""
    runner = build_runner(monkeypatch)
    cfg = build_config()

    combos = cfg.combinations()
    results = runner.run(config=cfg, k=None, num_exchanges=1, batch_delay=0.0)

    assert len(results) == len(combos)
    expected = [signature_for(c) for c in combos]
    got = [signature_for(r.traitmix) for r in results if r.traitmix is not None]
    assert got == expected


def test_k_ge_total_runs_all_combinations_in_order(monkeypatch: MonkeyPatch) -> None:
    """K >= total returns all combos in deterministic order."""
    runner = build_runner(monkeypatch)
    cfg = build_config()
    combos = cfg.combinations()
    k = len(combos) + 5

    results = runner.run(config=cfg, k=k, num_exchanges=1, batch_delay=0.0)
    assert len(results) == len(combos)
    expected = [signature_for(c) for c in combos]
    got = [signature_for(r.traitmix) for r in results if r.traitmix is not None]
    assert got == expected


def test_k_lt_total_uses_random_sample(monkeypatch: MonkeyPatch) -> None:
    """K < total uses random.sample(pop, k)."""
    runner = build_runner(monkeypatch)
    cfg = build_config()
    combos = cfg.combinations()

    calls: list[tuple[list[TraitMixCombination], int]] = []

    def fake_sample(pop: list[TraitMixCombination], count: int) -> list[TraitMixCombination]:
        calls.append((pop, count))

        return pop[:count]

    monkeypatch.setattr(random, "sample", fake_sample)

    k = 3
    results = runner.run(config=cfg, k=k, num_exchanges=1, batch_delay=0.0)
    assert len(calls) == 1
    assert calls[0][1] == k
    assert calls[0][0] == combos
    assert len(results) == k
    got = [signature_for(r.traitmix) for r in results if r.traitmix is not None]
    expected = [signature_for(c) for c in combos[:k]]
    assert got == expected
