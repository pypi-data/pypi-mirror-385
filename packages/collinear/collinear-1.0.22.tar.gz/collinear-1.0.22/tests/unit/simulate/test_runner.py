"""Tests exercising the conversation runner without network calls."""

from __future__ import annotations

import asyncio

import httpx
import pytest
from _pytest.monkeypatch import MonkeyPatch
from openai.types.chat import ChatCompletionMessageParam

from collinear.common.exceptions import BuildConversationError
from collinear.common.exceptions import InvalidTraitError
from collinear.schemas.traitmix import Role
from collinear.schemas.traitmix import SimulationResult
from collinear.schemas.traitmix import TraitMixCombination
from collinear.schemas.traitmix import TraitMixConfig
from collinear.simulate.runner import MAX_ALLOWED_CONCURRENCY
from collinear.simulate.runner import SimulationRunner
from tests.helpers.progress import FakeProgress
from tests.helpers.progress import make_progress_manager


def test_runner_exception_aliases() -> None:
    """SimulationRunner maintains aliases for legacy exception access."""
    assert SimulationRunner.InvalidTraitError is InvalidTraitError
    assert SimulationRunner.BuildConversationError is BuildConversationError


def test_simulation_runner_requires_model_name() -> None:
    """SimulationRunner validates required model name."""
    with pytest.raises(ValueError, match="model_name is required"):
        SimulationRunner(
            assistant_model_url="https://example.test",
            assistant_model_api_key="key",
            assistant_model_name="",
            collinear_api_key="demo-001",
        )


def test_simulation_runner_requires_collinear_api_key() -> None:
    """SimulationRunner validates the Collinear API key."""
    with pytest.raises(ValueError, match="COLLINEAR_API_KEY is required"):
        SimulationRunner(
            assistant_model_url="https://example.test",
            assistant_model_api_key="key",
            assistant_model_name="gpt-test",
            collinear_api_key="",
        )


def test_run_returns_empty_when_no_combinations() -> None:
    """Runner exits early when the configuration yields no combinations."""
    runner = SimulationRunner(
        assistant_model_url="https://example.test",
        assistant_model_api_key="test-key",
        assistant_model_name="gpt-test",
        collinear_api_key="demo-001",
    )
    config = TraitMixConfig()
    results = runner.run(config=config, num_exchanges=1, batch_delay=0.0, progress=False)
    assert results == []


def test_run_builds_conversation_and_returns_results(monkeypatch: MonkeyPatch) -> None:
    """Monkeypatch turn generation to validate run() behavior without network."""

    async def fake_generate(
        runner_instance: SimulationRunner,
        combo: TraitMixCombination,
        conversation: list[ChatCompletionMessageParam],
        role: Role,
    ) -> str:
        del runner_instance, combo, conversation
        return {Role.USER: "u", Role.ASSISTANT: "a"}[role]

    monkeypatch.setattr(SimulationRunner, "generate_turn", fake_generate)

    runner = SimulationRunner(
        assistant_model_url="https://example.test",
        assistant_model_api_key="test-key",
        assistant_model_name="gpt-test",
        collinear_api_key="demo-001",
    )

    config = TraitMixConfig(
        ages=["25-34"],
        genders=["female"],
        occupations=["Employed"],
        intents=["billing"],
        traits={"impatience": ["medium"]},
        tasks=["telecom"],
    )

    results = runner.run(
        config=config,
        k=1,
        num_exchanges=2,
        batch_delay=0.0,
        progress=False,
    )
    assert len(results) == 1
    res = results[0]

    assert [m["role"] for m in res.conv_prefix] == ["user", "assistant", "user"]
    assert res.response == "a"


def test_progress_updates_per_user_turn(monkeypatch: MonkeyPatch) -> None:
    """Progress bar receives one update per user turn when enabled."""
    bars: list[FakeProgress] = []
    pm = make_progress_manager(lambda h: bars.append(h))
    monkeypatch.setattr("collinear.simulate.progress.progress_manager", pm)

    async def fake_generate(
        runner_instance: SimulationRunner,
        combo: TraitMixCombination,
        conversation: list[ChatCompletionMessageParam],
        role: Role,
    ) -> str:
        del runner_instance, combo, conversation
        return {Role.USER: "u", Role.ASSISTANT: "a"}[role]

    monkeypatch.setattr(SimulationRunner, "generate_turn", fake_generate)

    runner = SimulationRunner(
        assistant_model_url="https://example.test",
        assistant_model_api_key="test-key",
        assistant_model_name="gpt-test",
        collinear_api_key="demo-001",
    )

    config = TraitMixConfig(
        ages=["25-34"],
        genders=["female"],
        occupations=["Employed"],
        intents=["billing"],
        traits={"impatience": ["medium"]},
        tasks=["telecom"],
    )

    results = runner.run(
        config=config,
        k=1,
        num_exchanges=2,
        batch_delay=0.0,
    )

    assert len(results) == 1
    assert [b.total for b in bars] == [2]
    assert bars[0].update_calls == [1, 1]
    assert bars[0].closed is True


def test_progress_adjusts_when_simulation_skipped(monkeypatch: MonkeyPatch) -> None:
    """Progress total shrinks when a simulation aborts early."""
    bars: list[FakeProgress] = []
    pm = make_progress_manager(lambda h: bars.append(h))
    monkeypatch.setattr("collinear.simulate.progress.progress_manager", pm)

    def failing_generate(
        runner_instance: SimulationRunner,
        combo: TraitMixCombination,
        conversation: list[ChatCompletionMessageParam],
        role: Role,
    ) -> str:
        del runner_instance, combo, conversation
        if role is Role.USER:
            raise InvalidTraitError("bad trait")
        return "a"

    monkeypatch.setattr(SimulationRunner, "generate_turn", failing_generate)

    runner = SimulationRunner(
        assistant_model_url="https://example.test",
        assistant_model_api_key="test-key",
        assistant_model_name="gpt-test",
        collinear_api_key="demo-001",
    )

    config = TraitMixConfig(
        ages=["25-34"],
        genders=["female"],
        occupations=["Employed"],
        intents=["billing"],
        traits={"impatience": ["medium"]},
        tasks=["telecom"],
    )

    results = runner.run(
        config=config,
        k=1,
        num_exchanges=2,
        batch_delay=0.0,
    )

    assert results == []
    assert len(bars) == 1
    assert bars[0].total == 1


def test_progress_adjustment_with_parallel_failures(monkeypatch: MonkeyPatch) -> None:
    """Verify progress total shrinks correctly when parallel tasks fail."""
    bars: list[FakeProgress] = []
    pm = make_progress_manager(lambda h: bars.append(h))
    monkeypatch.setattr("collinear.simulate.progress.progress_manager", pm)

    async def partially_failing_build_conversation(
        self: SimulationRunner, combo: TraitMixCombination, num_exchanges: int
    ) -> tuple[list[ChatCompletionMessageParam], str]:
        del num_exchanges
        self.advance_progress(1)
        if "bad" in str(combo.traits):
            raise BuildConversationError(1, invalid_trait=True, trait="bad_trait")
        return [], "success"

    monkeypatch.setattr(
        SimulationRunner, "build_conversation", partially_failing_build_conversation
    )

    runner = SimulationRunner(
        assistant_model_url="https://example.test",
        assistant_model_api_key="test-key",
        assistant_model_name="gpt-test",
        collinear_api_key="demo-001",
    )

    config = TraitMixConfig(
        ages=["25-34"],
        genders=["female"],
        occupations=["Employed"],
        intents=["billing"],
        traits={"impatience": ["medium"], "bad_trait": ["medium"]},
    )

    runner.run(config, k=2, num_exchanges=2, max_concurrency=2)

    assert len(bars) == 1
    assert bars[0].total == 2 * 2 - 1


def test_build_conversation_failed_carries_metadata(monkeypatch: MonkeyPatch) -> None:
    """Verify BuildConversationFailed carries user turn count and trait info."""
    caught_exceptions = []

    async def failing_build_conversation(
        self: SimulationRunner, combo: TraitMixCombination, num_exchanges: int
    ) -> tuple[list[ChatCompletionMessageParam], str]:
        del combo
        del num_exchanges
        self.advance_progress(1)
        raise BuildConversationError(1, invalid_trait=True, trait="bad_trait")

    monkeypatch.setattr(SimulationRunner, "build_conversation", failing_build_conversation)

    runner = SimulationRunner(
        assistant_model_url="https://example.test",
        assistant_model_api_key="test-key",
        assistant_model_name="gpt-test",
        collinear_api_key="demo-001",
    )

    config = TraitMixConfig(
        ages=["25-34"],
        genders=["female"],
        occupations=["Employed"],
        intents=["billing"],
        traits={"impatience": ["medium"]},
    )

    async def capture_exceptions(
        self: SimulationRunner,
        samples: list[TraitMixCombination],
        num_exchanges: int,
        batch_delay: float,
        max_concurrency: int = 8,
    ) -> list[SimulationResult]:
        assert max_concurrency >= 1
        del batch_delay

        async def run_one(index: int, combo: TraitMixCombination) -> None:
            del index
            try:
                await self.build_conversation(combo, num_exchanges)
            except BuildConversationError as e:
                caught_exceptions.append(e)

        await asyncio.gather(*(run_one(i, combo) for i, combo in enumerate(samples)))
        return []

    monkeypatch.setattr(SimulationRunner, "execute_samples", capture_exceptions)
    runner.run(config, k=1, num_exchanges=2)

    assert len(caught_exceptions) == 1
    exc = caught_exceptions[0]
    assert exc.completed_user_turns == 1
    assert exc.invalid_trait is True
    assert exc.trait == "bad_trait"


def test_calculate_semaphore_limit() -> None:
    """Test semaphore limit calculation respects bounds."""
    runner = SimulationRunner(
        assistant_model_url="https://example.test",
        assistant_model_api_key="test-key",
        assistant_model_name="gpt-test",
        collinear_api_key="demo-001",
    )

    near_min_request = 3
    moderate_request = 5
    above_max_request = 100

    assert runner.calculate_semaphore_limit(0) == 1
    assert runner.calculate_semaphore_limit(-5) == 1
    assert runner.calculate_semaphore_limit(near_min_request) == near_min_request
    assert runner.calculate_semaphore_limit(moderate_request) == moderate_request
    assert runner.calculate_semaphore_limit(MAX_ALLOWED_CONCURRENCY) == MAX_ALLOWED_CONCURRENCY
    assert runner.calculate_semaphore_limit(above_max_request) == MAX_ALLOWED_CONCURRENCY


def test_all_user_turns_hit_batch_endpoint(monkeypatch: MonkeyPatch) -> None:
    """Even single-turn conversations should use the batch traitmix endpoint."""
    called_payloads: list[tuple[str, object]] = []

    async def fake_request_traitmix(
        runner_instance: SimulationRunner,
        url: str,
        headers: dict[str, str],
        payload: object,
    ) -> tuple[httpx.Response | None, str | None]:
        called_payloads.append((url, payload))
        del runner_instance, headers
        req = httpx.Request("POST", url)
        assert isinstance(payload, list)
        body: object = {"responses": ["mock-user"] * len(payload)}
        resp = httpx.Response(200, request=req, json=body)
        return resp, None

    async def fake_call_with_retry(
        runner_instance: SimulationRunner,
        messages: list[dict[str, object]],
        system_prompt: str,
    ) -> str:
        del runner_instance, messages, system_prompt
        return "mock-assistant"

    monkeypatch.setattr(SimulationRunner, "request_traitmix", fake_request_traitmix)
    monkeypatch.setattr(SimulationRunner, "call_with_retry", fake_call_with_retry)

    runner = SimulationRunner(
        assistant_model_url="https://example.test",
        assistant_model_api_key="test-key",
        assistant_model_name="gpt-test",
        collinear_api_key="demo-001",
    )

    config = TraitMixConfig(
        ages=["25-34"],
        genders=["female"],
        occupations=["Employed"],
        intents=["billing"],
        traits={"impatience": ["medium"]},
    )

    asyncio.run(
        runner.run_async(
            config,
            k=1,
            num_exchanges=1,
            max_concurrency=1,
            batch_delay=0.0,
        )
    )

    assert called_payloads, "Expected traitmix request to be issued"
    assert all("steer_batch" in entry[0] for entry in called_payloads)
    assert all(isinstance(entry[1], list) and len(entry[1]) == 1 for entry in called_payloads)


def test_concurrency_above_one_uses_batch(monkeypatch: MonkeyPatch) -> None:
    """Verify concurrency > 1 routes to /steer_batch endpoint."""
    called_urls: list[tuple[str, object]] = []

    async def fake_request_traitmix(
        runner_instance: SimulationRunner,
        url: str,
        headers: dict[str, str],
        payload: object,
    ) -> tuple[httpx.Response | None, str | None]:
        called_urls.append((url, payload))
        del runner_instance, headers
        req = httpx.Request("POST", url)
        assert isinstance(payload, list)
        body: object = {"responses": ["mock-user"] * len(payload)}
        resp = httpx.Response(200, request=req, json=body)
        return resp, None

    async def fake_call_with_retry(
        runner_instance: SimulationRunner,
        messages: list[dict[str, object]],
        system_prompt: str,
    ) -> str:
        del runner_instance, messages, system_prompt
        return "mock-assistant"

    monkeypatch.setattr(SimulationRunner, "request_traitmix", fake_request_traitmix)
    monkeypatch.setattr(SimulationRunner, "call_with_retry", fake_call_with_retry)

    runner = SimulationRunner(
        assistant_model_url="https://example.test",
        assistant_model_api_key="test-key",
        assistant_model_name="gpt-test",
        collinear_api_key="demo-001",
    )

    config = TraitMixConfig(
        ages=["18-24", "25-34"],
        genders=["female"],
        occupations=["Employed"],
        intents=["billing"],
        traits={"impatience": ["medium", "high"]},
    )

    asyncio.run(
        runner.run_async(
            config,
            k=2,
            num_exchanges=1,
            max_concurrency=2,
            batch_delay=0.0,
        )
    )

    assert called_urls, "Expected traitmix request to be issued"
    assert all("steer_batch" in entry[0] for entry in called_urls)
    assert all(isinstance(entry[1], list) for entry in called_urls)


_INTENSITY_FROM_INDEX = {0: "low", 1: "medium", 2: "high"}
_INTENSITY_ORDER = {"low": 0, "medium": 1, "high": 2}


def _normalize_intensity(combo: TraitMixCombination) -> tuple[str, int]:
    """Return intensity label and ordering index for a combination."""
    value = combo.intensity if combo.intensity is not None else "medium"
    if isinstance(value, int):
        try:
            label = _INTENSITY_FROM_INDEX[value]
        except KeyError as exc:
            raise ValueError(f"Unsupported intensity index: {value}") from exc
    else:
        label = str(value)

    try:
        order = _INTENSITY_ORDER[label]
    except KeyError as exc:
        raise ValueError(f"Unknown intensity label: {label}") from exc

    return label, order


def _build_ordered_messages(
    level_label: str, num_exchanges: int
) -> list[ChatCompletionMessageParam]:
    """Assemble alternating user/assistant messages for the given intensity."""
    total_turns = num_exchanges * 2
    messages: list[ChatCompletionMessageParam] = []
    for turn in range(1, total_turns + 1):
        if turn % 2 == 1:
            messages.append(
                {
                    "role": Role.USER.value,
                    "content": f"user-{level_label}-{turn}",
                }
            )
            continue

        suffix = "final" if turn == total_turns else str(turn)
        messages.append(
            {
                "role": Role.ASSISTANT.value,
                "content": f"assistant-{level_label}-{suffix}",
            }
        )
    return messages


async def _order_preserving_build_conversation(
    runner_instance: SimulationRunner,
    combo: TraitMixCombination,
    num_exchanges: int,
) -> tuple[list[ChatCompletionMessageParam], str]:
    del runner_instance
    level_label, level = _normalize_intensity(combo)
    await asyncio.sleep(0.01 * (2 - level))
    messages = _build_ordered_messages(level_label, num_exchanges)
    return messages, str(messages[-1]["content"])


def _intensities_from_results(results: list[SimulationResult]) -> list[str]:
    """Collect trait intensity labels, asserting they are present."""
    intensities: list[str] = []
    for result in results:
        traitmix = result.traitmix
        if traitmix is None or traitmix.intensity is None:
            raise AssertionError("Missing traitmix intensity in result")
        intensities.append(str(traitmix.intensity))
    return intensities


def test_concurrent_run_preserves_result_order(monkeypatch: MonkeyPatch) -> None:
    """Results stay aligned with configured sample order under concurrency."""
    monkeypatch.setattr(
        SimulationRunner, "build_conversation", _order_preserving_build_conversation
    )

    runner = SimulationRunner(
        assistant_model_url="https://example.test",
        assistant_model_api_key="test-key",
        assistant_model_name="gpt-test",
        collinear_api_key="demo-001",
    )

    config = TraitMixConfig(
        traits={"patience": ["low", "medium", "high"]},
    )

    results = runner.run(
        config=config,
        num_exchanges=2,
        batch_delay=0.0,
        progress=False,
        max_concurrency=3,
    )

    intensities = _intensities_from_results(results)
    assert intensities == ["low", "medium", "high"]

    responses = [res.response for res in results]
    assert responses == [
        "assistant-low-final",
        "assistant-medium-final",
        "assistant-high-final",
    ]


def test_batch_endpoint_raises_on_empty_response() -> None:
    """Empty traitmix responses trigger an explicit error."""

    class EmptyBatchRunner(SimulationRunner):
        def __init__(self) -> None:
            super().__init__(
                assistant_model_url="https://example.test",
                assistant_model_api_key="test-key",
                assistant_model_name="gpt-test",
                collinear_api_key="demo-001",
            )

        async def call_batch_endpoint(
            self,
            url: str,
            payloads: list[dict[str, object]],
            *,
            headers: dict[str, str],
        ) -> list[str]:
            """Return empty responses while recording the URL."""
            del payloads, headers
            assert url.endswith("steer_batch")
            return [""]

        async def call_with_retry(
            self,
            messages: list[ChatCompletionMessageParam],
            system_prompt: str,
        ) -> str:
            """Return a canned assistant response."""
            del messages, system_prompt
            return "assistant"

        async def invoke_trait_dict(
            self,
            *,
            trait_dict: dict[str, int | str],
            combo: TraitMixCombination,
        ) -> str:
            return await super().call_collinear_traitmix_api_trait_dict(
                trait_dict=trait_dict,
                combo=combo,
                conversation=[],
            )

    runner = EmptyBatchRunner()

    with pytest.raises(SimulationRunner.EmptyTraitMixResponseError):
        asyncio.run(
            runner.invoke_trait_dict(
                trait_dict={"impatience": "medium"},
                combo=TraitMixCombination(
                    age=None,
                    gender=None,
                    occupation=None,
                    intent=None,
                    traits={"impatience": "medium"},
                    location=None,
                    language=None,
                    task=None,
                ),
            )
        )
