"""Type-safe unit tests for selected SimulationRunner helpers."""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import cast

import httpx
import openai
import pytest
from openai.types.chat import ChatCompletionMessageParam

from collinear.common.exceptions import InvalidTraitError
from collinear.schemas.traitmix import Role
from collinear.schemas.traitmix import TraitMixCombination
from collinear.simulate import progress as progress_mod
from collinear.simulate.runner import ASSISTANT_OPTS
from collinear.simulate.runner import MAX_ALLOWED_CONCURRENCY
from collinear.simulate.runner import SimulationRunner
from tests.helpers.logging import StubLogger
from tests.helpers.simulate_clients import ErroringSteeringClient
from tests.helpers.simulate_clients import ExplodingSteeringClient
from tests.helpers.simulate_clients import NullSteeringClient
from tests.helpers.simulate_clients import StubAssistantClient
from tests.helpers.simulate_clients import StubSteeringClient

if TYPE_CHECKING:
    from logging import Logger


class StubProgress(progress_mod.Progress):
    """Backwards-compatible progress recorder for a targeted assertion."""

    def __init__(self) -> None:
        """Initialize storage for update and adjustment calls."""
        self.updates: list[int] = []
        self.adjustments: list[int] = []

    def update(self, step: int) -> None:
        """Record a progress increment."""
        self.updates.append(step)

    def adjust_total(self, decrement: int) -> None:
        """Record a total adjustment for later verification."""
        self.adjustments.append(decrement)


def make_runner() -> SimulationRunner:
    """Construct a SimulationRunner instance with stubbed dependencies."""
    runner = SimulationRunner.__new__(SimulationRunner)
    runner.collinear_api_key = "abcd1234"
    runner.traitmix_temperature = 0.7
    runner.traitmix_max_tokens = 256
    runner.traitmix_seed = -1
    runner.logger = cast("Logger", StubLogger())
    runner.progress_handle = None
    runner.steering_client = StubSteeringClient(["known"])
    return runner


def make_combo(traits: dict[str, int | str]) -> TraitMixCombination:
    """Create a TraitMixCombination with only trait data populated."""
    return TraitMixCombination(
        age=None,
        gender=None,
        occupation=None,
        intent=None,
        traits=traits,
        location=None,
        language=None,
        task=None,
    )


def test_traitmix_settings_roundtrip() -> None:
    """TraitMix settings context manager restores previous values."""
    runner = make_runner()
    new_temperature = 0.4
    new_max_tokens = 128
    new_seed = 99
    original_temperature = runner.traitmix_temperature
    original_max_tokens = runner.traitmix_max_tokens
    original_seed = runner.traitmix_seed

    with runner.traitmix_settings(
        traitmix_temperature=new_temperature,
        traitmix_max_tokens=new_max_tokens,
        traitmix_seed=new_seed,
    ):
        assert runner.traitmix_temperature == new_temperature
        assert runner.traitmix_max_tokens == new_max_tokens
        assert runner.traitmix_seed == new_seed

    assert runner.traitmix_temperature == original_temperature
    assert runner.traitmix_max_tokens == original_max_tokens
    assert runner.traitmix_seed == original_seed


def test_assistant_settings_sets_context() -> None:
    """Assistant settings context manager exposes overrides via the context var."""
    runner = make_runner()
    override_tokens = 111
    override_seed = 5
    with runner.assistant_settings(
        assistant_max_tokens=override_tokens,
        assistant_seed=override_seed,
    ):
        opts = ASSISTANT_OPTS.get()
        assert opts is not None
        assert opts.max_tokens == override_tokens
        assert opts.seed == override_seed
    assert ASSISTANT_OPTS.get() is None


def test_mask_key_preview_short_and_long() -> None:
    """Masking helper reveals full key only when it is very short."""
    runner = make_runner()
    runner.collinear_api_key = "abcd"
    assert runner.mask_key_preview() == "abcd"
    runner.collinear_api_key = "abcdefghijkl"
    assert runner.mask_key_preview().startswith("ab***")


def test_log_if_unauthorized_logs_error() -> None:
    """Unauthorized responses emit an error log with key preview."""
    runner = make_runner()
    response = httpx.Response(
        status_code=401,
        request=httpx.Request("GET", "https://example.test/traits"),
        text="unauthorized",
    )
    runner.log_if_unauthorized(response)
    logger = cast("StubLogger", runner.logger)
    assert any("unauthorized" in msg for msg in logger.error_messages)


def test_list_traits_handles_exception() -> None:
    """list_traits guards against steering client failures."""
    runner = make_runner()

    class FailingClient(StubSteeringClient):
        def list_traits(self) -> list[str]:
            raise RuntimeError("boom")

    runner.steering_client = FailingClient([])
    assert runner.list_traits() == []


def test_should_skip_trait_for_422_missing_trait() -> None:
    """Missing traits should be flagged for skipping after a 422 response."""
    runner = make_runner()
    runner.steering_client = StubSteeringClient(["known"])
    should_skip, available = runner.should_skip_trait_for_422("unknown")
    assert should_skip
    assert "known" in available


def test_should_skip_trait_for_422_when_available() -> None:
    """Known traits should not be skipped when available list is populated."""
    runner = make_runner()
    runner.steering_client = StubSteeringClient(["known"])
    should_skip, available = runner.should_skip_trait_for_422("known")
    assert not should_skip
    assert available == ["known"]


def test_handle_unprocessable_payloads_single_trait() -> None:
    """Single-trait payloads trigger the single-trait handler on 422."""
    runner = make_runner()
    runner.steering_client = StubSteeringClient([])
    payloads: list[dict[str, object]] = [{"trait_dict": {"mystery": "low"}}]
    with pytest.raises(InvalidTraitError):
        runner.handle_unprocessable_payloads(payloads, httpx.Response(422))


def test_handle_unprocessable_payloads_mixed_missing_trait() -> None:
    """Mixed trait payloads route to the mixed handler when traits missing."""
    runner = make_runner()
    runner.steering_client = StubSteeringClient(["known"])
    payloads: list[dict[str, object]] = [{"trait_dict": {"known": "low", "other": "high"}}]
    with pytest.raises(InvalidTraitError):
        runner.handle_unprocessable_payloads(payloads, httpx.Response(422))


def test_handle_unprocessable_payloads_multiple_entries() -> None:
    """Multiple payload entries aggregate trait names for mixed handling."""
    runner = make_runner()
    runner.steering_client = StubSteeringClient(["known"])
    payloads: list[dict[str, object]] = [
        {"trait_dict": {"known": "low"}},
        {"trait_dict": {"other": "medium"}},
    ]
    with pytest.raises(InvalidTraitError):
        runner.handle_unprocessable_payloads(payloads, httpx.Response(422))


def test_handle_unprocessable_or_skip_mixed_all_available() -> None:
    """No error is raised when all provided traits are recognized."""
    runner = make_runner()
    runner.steering_client = StubSteeringClient(["kind", "curious"])
    runner.handle_unprocessable_or_skip_mixed({"kind", "curious"}, httpx.Response(422))


def test_handle_unprocessable_or_skip_mixed_no_available_traits() -> None:
    """Missing availability information results in an InvalidTraitError."""
    runner = make_runner()
    runner.steering_client = StubSteeringClient([])
    with pytest.raises(InvalidTraitError):
        runner.handle_unprocessable_or_skip_mixed({"kind", "curious"}, httpx.Response(422))


def test_read_json_or_error_success() -> None:
    """read_json_or_error returns data when response JSON parsing succeeds."""
    runner = make_runner()
    payload_ok: dict[str, bool] = {"ok": True}
    response = httpx.Response(
        200, json=payload_ok, request=httpx.Request("GET", "https://example.test")
    )
    data, err = runner.read_json_or_error(response)
    assert data == {"ok": True}
    assert err is None


def test_read_json_or_error_failure_logs() -> None:
    """read_json_or_error logs and returns error details on exceptions."""
    runner = make_runner()
    payload_error: dict[str, object] = {}
    response = httpx.Response(
        500, json=payload_error, request=httpx.Request("GET", "https://example.test")
    )
    data, err = runner.read_json_or_error(response)
    assert data is None
    assert err is not None
    logger = cast("StubLogger", runner.logger)
    assert logger.error_messages


def test_parse_batch_responses_normalizes_values() -> None:
    """parse_batch_responses converts values to strings and blanks."""
    runner = make_runner()
    payload_mixed: dict[str, list[object]] = {"responses": [1, None, "ok"]}
    response = httpx.Response(
        200, json=payload_mixed, request=httpx.Request("POST", "https://example.test")
    )
    output = runner.parse_batch_responses(response, 3)
    assert output == ["1", "", "ok"]


def test_parse_batch_responses_mismatch_raises() -> None:
    """parse_batch_responses raises when counts mismatch."""
    runner = make_runner()
    payload_only: dict[str, list[str]] = {"responses": ["only"]}
    response = httpx.Response(
        200, json=payload_only, request=httpx.Request("POST", "https://example.test")
    )
    with pytest.raises(RuntimeError):
        runner.parse_batch_responses(response, 2)


def test_parse_batch_responses_requires_dict() -> None:
    """parse_batch_responses rejects non-dict JSON payloads."""
    runner = make_runner()
    invalid_payload: list[str] = ["invalid"]
    response = httpx.Response(
        200,
        json=invalid_payload,
        request=httpx.Request("POST", "https://example.test"),
    )
    with pytest.raises(TypeError):
        runner.parse_batch_responses(response, 1)


def test_parse_batch_responses_requires_list() -> None:
    """parse_batch_responses requires a list of responses."""
    runner = make_runner()
    bad_payload: dict[str, object] = {"responses": "bad"}
    response = httpx.Response(
        200,
        json=bad_payload,
        request=httpx.Request("POST", "https://example.test"),
    )
    with pytest.raises(TypeError):
        runner.parse_batch_responses(response, 1)


def test_select_samples_respects_k() -> None:
    """Selecting samples with k less than total should return k items."""
    runner = make_runner()
    combos = [make_combo({f"t{i}": "low"}) for i in range(3)]
    target_count = 2
    selected = runner.select_samples(combos, k=target_count)
    assert len(selected) == target_count
    for combo in selected:
        assert combo in combos


def test_calculate_semaphore_limit_bounds() -> None:
    """calculate_semaphore_limit clamps values within allowed bounds."""
    runner = make_runner()
    baseline_limit = 1
    inline_limit = 5
    high_limit = 99
    assert runner.calculate_semaphore_limit(0) == baseline_limit
    assert runner.calculate_semaphore_limit(inline_limit) == inline_limit
    assert runner.calculate_semaphore_limit(high_limit) == MAX_ALLOWED_CONCURRENCY


def test_progress_helpers_ignore_without_handle() -> None:
    """Progress helpers are no-ops when no handle is active."""
    runner = make_runner()
    runner.advance_progress(0)
    runner.advance_progress(1)
    runner.adjust_progress_total(0)
    runner.adjust_progress_total(1)
    assert runner.progress_handle is None


@pytest.mark.asyncio
async def test_call_batch_endpoint_no_payloads_returns_empty() -> None:
    """Empty payload lists short-circuit call_batch_endpoint."""
    runner = make_runner()
    result = await runner.call_batch_endpoint(
        "https://example.test/steer_batch", [], headers={"API-Key": "key"}
    )
    assert result == []


@pytest.mark.asyncio
async def test_call_batch_endpoint_raises_when_response_missing() -> None:
    """Missing response from steering client raises a runtime error."""
    runner = make_runner()
    runner.steering_client = NullSteeringClient(["kind"])

    bad_payloads: list[dict[str, object]] = [{}]
    with pytest.raises(RuntimeError, match="batch API call failed"):
        await runner.call_batch_endpoint("https://example", bad_payloads, headers={})


@pytest.mark.asyncio
async def test_request_traitmix_logs_and_reraises() -> None:
    """Exceptions from steering client propagate with logged message."""
    runner = make_runner()
    runner.steering_client = ExplodingSteeringClient(["kind"])

    with pytest.raises(RuntimeError, match="boom"):
        await runner.request_traitmix("https://example", {}, {})
    logger = cast("StubLogger", runner.logger)
    assert any("User service error" in msg for msg in logger.error_messages)


def test_progress_helpers_update_and_adjust() -> None:
    """Progress helpers forward updates when a handle is active."""
    runner = make_runner()
    recorder = StubProgress()
    runner.progress_handle = cast("progress_mod.Progress", recorder)
    runner.advance_progress(2)
    runner.adjust_progress_total(1)
    assert recorder.updates == [2]
    assert recorder.adjustments == [1]


@pytest.mark.asyncio
async def test_call_batch_endpoint_success() -> None:
    """Successful batch endpoint call returns normalized responses."""
    runner = make_runner()
    runner.steering_client = StubSteeringClient(["kind"])
    payload: list[dict[str, object]] = [{"body": 1}]
    responses = await runner.call_batch_endpoint(
        "https://example.test", payload, headers={"API-Key": "key"}
    )
    assert responses == ["ok"]


@pytest.mark.asyncio
async def test_call_batch_endpoint_error_message() -> None:
    """Error strings from steering client surface as RuntimeError."""
    runner = make_runner()
    runner.steering_client = ErroringSteeringClient([])
    payload: list[dict[str, object]] = [{"body": 1}]
    with pytest.raises(RuntimeError, match="failure"):
        await runner.call_batch_endpoint("https://example.test", payload, headers={})


@pytest.mark.asyncio
async def test_request_traitmix_returns_error_string() -> None:
    """request_traitmix returns provided error details."""
    runner = make_runner()
    runner.steering_client = ErroringSteeringClient([])
    resp, err = await runner.request_traitmix("https://example", {}, {})
    assert resp is None
    assert err == "failure"


@pytest.mark.asyncio
async def test_call_with_retry_handles_exception() -> None:
    """call_with_retry returns an error string when AssistantClient fails."""
    runner = make_runner()

    class FailingAssistant(StubAssistantClient):
        async def complete(
            self,
            messages: list[ChatCompletionMessageParam],
            system_prompt: str,
            *,
            max_tokens: int | None,
            seed: int | None,
            temperature: float = 0.8,
            max_empty_retries: int = 2,
        ) -> str:
            del messages, system_prompt, max_tokens, seed, temperature, max_empty_retries
            raise RuntimeError("boom")

    runner.assistant_client = FailingAssistant()
    result = await runner.call_with_retry([], "system")
    assert result.startswith("Error: boom")


@pytest.mark.asyncio
async def test_call_with_retry_reraises_rate_limit() -> None:
    """Rate limit errors are propagated from call_with_retry."""
    runner = make_runner()

    class RateLimitedAssistant(StubAssistantClient):
        async def complete(
            self,
            messages: list[ChatCompletionMessageParam],
            system_prompt: str,
            *,
            max_tokens: int | None,
            seed: int | None,
            temperature: float = 0.8,
            max_empty_retries: int = 2,
        ) -> str:
            del messages, system_prompt, max_tokens, seed, temperature, max_empty_retries
            response = httpx.Response(
                429,
                request=httpx.Request("POST", "https://assistant.test"),
            )
            raise openai.RateLimitError("rate", response=response, body=None)

    runner.assistant_client = RateLimitedAssistant()
    with pytest.raises(openai.RateLimitError):
        await runner.call_with_retry([], "system")


@pytest.mark.asyncio
async def test_call_with_retry_contextvar_guard(monkeypatch: pytest.MonkeyPatch) -> None:
    """ContextVar lookup failures should not crash call_with_retry."""
    runner = make_runner()

    class SimpleAssistant(StubAssistantClient):
        async def complete(
            self,
            messages: list[ChatCompletionMessageParam],
            system_prompt: str,
            *,
            max_tokens: int | None,
            seed: int | None,
            temperature: float = 0.8,
            max_empty_retries: int = 2,
        ) -> str:
            del messages, system_prompt, max_tokens, seed, temperature, max_empty_retries
            return "ok"

    runner.assistant_client = SimpleAssistant()

    class FailingContextVar:
        def get(self) -> object:
            raise LookupError("missing context")

        def set(self, *args: object, **kwargs: object) -> object:
            del args, kwargs
            return None

        def reset(self, token: object) -> None:
            del token

    monkeypatch.setattr("collinear.simulate.runner.ASSISTANT_OPTS", FailingContextVar())
    result = await runner.call_with_retry([], "system")
    assert result == "ok"


@pytest.mark.asyncio
async def test_run_user_turn_stop_removes_message() -> None:
    """run_user_turn removes a stop marker and indicates termination."""
    runner = make_runner()

    async def fake_generate(
        combo: TraitMixCombination,
        conversation: list[object],
        role: Role,
    ) -> str:
        del combo, conversation
        assert role is Role.USER
        return "###STOP###"

    runner.generate_turn = fake_generate  # type: ignore[assignment]
    conversation: list[ChatCompletionMessageParam] = [{"role": "assistant", "content": "hi"}]

    stop, response = await runner.run_user_turn(make_combo({"kind": "low"}), conversation)

    assert stop is True
    assert response == "###STOP###"
    assert conversation == [{"role": "assistant", "content": "hi"}]


@pytest.mark.asyncio
async def test_call_collinear_traitmix_api_returns_response() -> None:
    """call_collinear_traitmix_api relays the first batch response."""
    runner = make_runner()
    runner.steering_client = StubSteeringClient(["kind"], responses=["hello"])
    result = await runner.call_collinear_traitmix_api(
        trait="kind",
        intensity="low",
        combo=make_combo({"kind": "low"}),
        conversation=[],
    )
    assert result == "hello"


@pytest.mark.asyncio
async def test_call_collinear_traitmix_api_raises_on_empty() -> None:
    """Empty TraitMix responses raise the expected error type."""
    runner = make_runner()
    runner.steering_client = StubSteeringClient(["kind"], responses=[""])
    with pytest.raises(SimulationRunner.EmptyTraitMixResponseError):
        await runner.call_collinear_traitmix_api(
            trait="kind",
            intensity="low",
            combo=make_combo({"kind": "low"}),
            conversation=[],
        )
