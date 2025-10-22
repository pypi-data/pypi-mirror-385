"""End-to-end, black box testing with mocked clients."""

from typing import cast

import httpx
import pytest

from collinear.schemas.traitmix import SimulationResult
from collinear.schemas.traitmix import TraitMixConfig
from collinear.simulate.runner import SimulationRunner
from tests.helpers.progress import FakeProgress
from tests.helpers.progress import make_progress_manager

collector: list[FakeProgress] = []
fake_progress_manager = make_progress_manager(lambda h: collector.append(h))


async def fake_request_traitmix(
    runner_instance: SimulationRunner,
    url: str,
    headers: dict[str, str],
    payload: dict[str, object],
) -> tuple[httpx.Response | None, str | None]:
    """Stub out the steering API call with canned JSON."""
    del runner_instance, headers, payload
    req = httpx.Request("POST", url)
    resp = httpx.Response(200, request=req, json=cast("dict[str, str]", {"response": "mock-user"}))
    return resp, None


async def fake_call_with_retry(
    runner_instance: SimulationRunner,
    messages: list[dict[str, object]],
    system_prompt: str,
) -> str:
    """Return a deterministic assistant response."""
    del runner_instance, messages, system_prompt
    return "mock-assistant"


def to_trait_items(result: SimulationResult) -> tuple[tuple[str, str], ...]:
    """Normalize traitmix data to tuples for set equality."""
    traitmix = result.traitmix
    assert traitmix is not None
    return tuple(sorted((name, str(level)) for name, level in traitmix.traits.items()))


def assert_results_equivalent(
    serial: list[SimulationResult],
    parallel: list[SimulationResult],
    *,
    num_exchanges: int,
) -> None:
    """Ensure serial and parallel runs produce the same outputs."""
    assert len(serial) == len(parallel)
    expected_turns = max(0, (num_exchanges * 2) - 1)
    for res in serial + parallel:
        assert len(res.conv_prefix) == expected_turns
        assert any(m["content"] == "mock-user" for m in res.conv_prefix if m["role"] == "user")
        assert res.response == "mock-assistant"
    serial_traits = {to_trait_items(res) for res in serial}
    parallel_traits = {to_trait_items(res) for res in parallel}
    assert serial_traits == parallel_traits


@pytest.mark.asyncio
async def test_parallel_integration_with_mocks(monkeypatch: pytest.MonkeyPatch) -> None:
    """End-to-end: traitmix and assistant calls are mocked."""
    monkeypatch.setattr("collinear.simulate.progress.progress_manager", fake_progress_manager)
    monkeypatch.setattr(SimulationRunner, "request_traitmix", fake_request_traitmix)
    monkeypatch.setattr(SimulationRunner, "call_with_retry", fake_call_with_retry)

    runner = SimulationRunner(
        assistant_model_url="https://example.test",
        assistant_model_api_key="test-key",
        assistant_model_name="gpt-test",
        collinear_api_key="ci-001",
    )

    config = TraitMixConfig(
        ages=["25-34"],
        genders=["female"],
        occupations=["Employed"],
        intents=["billing"],
        traits={"impatience": ["medium", "high"]},
    )

    exchanges = 2
    serial = await runner.run_async(
        config, k=2, num_exchanges=exchanges, max_concurrency=1, batch_delay=0.0
    )
    parallel = await runner.run_async(
        config, k=2, num_exchanges=exchanges, max_concurrency=2, batch_delay=0.0
    )

    assert_results_equivalent(serial, parallel, num_exchanges=exchanges)
