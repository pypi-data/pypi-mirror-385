"""Tests for the high-level Client wrapper."""

from __future__ import annotations

from types import SimpleNamespace
from typing import cast

import pytest

from collinear.client import Client
from collinear.schemas.traitmix import SimulationResult
from collinear.simulate.runner import SimulationRunner


def test_client_requires_model_name() -> None:
    """Client raises when model_name is missing or falsy."""
    with pytest.raises(ValueError, match="model_name is required"):
        Client(
            assistant_model_url="https://example.test",
            assistant_model_api_key="k",
            assistant_model_name="",
            collinear_api_key="demo-001",
        )


def test_client_requires_collinear_api_key() -> None:
    """Client raises when the Collinear API key is missing."""
    with pytest.raises(ValueError, match="COLLINEAR_API_KEY is required"):
        Client(
            assistant_model_url="https://example.test",
            assistant_model_api_key="k",
            assistant_model_name="gpt-test",
            collinear_api_key="",
        )


def test_simulation_runner_lazy_instantiation() -> None:
    """Accessing `simulation_runner` returns a SimulationRunner instance."""
    client = Client(
        assistant_model_url="https://example.test",
        assistant_model_api_key="test-key",
        assistant_model_name="gpt-test",
        collinear_api_key="demo-001",
    )
    runner = client.simulation_runner
    assert isinstance(runner, SimulationRunner)
    assert runner is client.simulation_runner


def test_simulate_passes_configuration(monkeypatch: pytest.MonkeyPatch) -> None:
    """simulate() converts config input and delegates to SimulationRunner.run."""
    captured: dict[str, object] = {}

    def fake_from_input(data: dict[str, object]) -> SimpleNamespace:
        captured["config"] = data
        return SimpleNamespace()

    monkeypatch.setattr("collinear.client.TraitMixConfig.from_input", fake_from_input)

    client = Client(
        assistant_model_url="https://example.test",
        assistant_model_api_key="test-key",
        assistant_model_name="gpt-test",
        collinear_api_key="demo-001",
    )

    def fake_run(
        runner_instance: SimulationRunner,
        config: object,
        k: int | None = None,
        num_exchanges: int = 2,
        batch_delay: float = 0.1,
        **kwargs: object,
    ) -> list[SimulationResult]:
        del runner_instance
        mix_traits = bool(kwargs.get("mix_traits", False))
        extra_kwargs: dict[str, object] = dict(kwargs)
        captured["run_kwargs"] = {
            "config": config,
            "k": k,
            "mix_traits": mix_traits,
            "num_exchanges": num_exchanges,
            "batch_delay": batch_delay,
            "progress": kwargs.get("progress", True),
            "max_concurrency": kwargs.get("max_concurrency", 1),
            "extra": extra_kwargs,
        }
        return [SimulationResult(conv_prefix=[], response="ok")]

    monkeypatch.setattr(SimulationRunner, "run", fake_run)

    result = client.simulate({"traits": {"patience": ["low"]}}, k=1, mix_traits=True)

    assert len(result) == 1
    assert result[0].response == "ok"
    assert captured["config"] == {"traits": {"patience": ["low"]}}
    run_kwargs = cast("dict[str, object]", captured["run_kwargs"])
    assert run_kwargs["k"] == 1
    assert run_kwargs["mix_traits"] is True
