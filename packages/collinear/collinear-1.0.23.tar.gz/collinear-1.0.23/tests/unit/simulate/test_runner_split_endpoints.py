"""Tests for split user/assistant endpoints in SimulationRunner.

Verifies USER turns are generated via the Collinear TraitMix API,
while ASSISTANT turns still use the OpenAI-compatible assistant model.
Network calls are monkeypatched.
"""

from __future__ import annotations

from _pytest.monkeypatch import MonkeyPatch
from openai.types.chat import ChatCompletionMessageParam

from collinear.schemas.traitmix import TraitMixCombination
from collinear.schemas.traitmix import TraitMixConfig
from collinear.simulate.runner import SimulationRunner


def test_split_endpoints_traitmix_api_is_used(monkeypatch: MonkeyPatch) -> None:
    """USER turns route to Collinear TraitMix API; assistant via OpenAI path."""

    async def fake_call_collinear_traitmix_api(
        runner_instance: SimulationRunner,
        *,
        conversation: list[ChatCompletionMessageParam],
        trait: str,
        intensity: str,
        combo: TraitMixCombination,
        **kwargs: object,
    ) -> str:
        del runner_instance, kwargs
        assert trait in {"impatience", "skeptical"}
        assert intensity in {"low", "medium", "high"}
        assert combo.language == "English"
        assert combo.task == "telecom"
        assert isinstance(conversation, list)

        return "u"

    async def fake_call_with_retry(
        runner_instance: SimulationRunner,
        messages: list[ChatCompletionMessageParam],
        system_prompt: str,
    ) -> str:
        del runner_instance, messages
        return {True: "a", False: "u"}["ASSISTANT" in system_prompt]

    monkeypatch.setattr(
        SimulationRunner,
        "call_collinear_traitmix_api",
        fake_call_collinear_traitmix_api,
    )
    monkeypatch.setattr(SimulationRunner, "call_with_retry", fake_call_with_retry)

    runner = SimulationRunner(
        assistant_model_url="https://example.test",
        assistant_model_api_key="k",
        assistant_model_name="gpt-test",
        collinear_api_key="demo-001",
    )

    config = TraitMixConfig(
        ages=["25-34"],
        genders=["female"],
        occupations=["Employed"],
        intents=["billing"],
        traits={"impatience": ["medium"], "skeptical": ["high"]},
        locations=["Austin"],
        languages=["English"],
        tasks=["telecom"],
    )

    results = runner.run(
        config=config,
        k=1,
        num_exchanges=2,
        batch_delay=0.0,
    )

    assert len(results) == 1
    res = results[0]

    roles = [m["role"] for m in res.conv_prefix]
    contents = [m["content"] for m in res.conv_prefix]
    assert roles == ["user", "assistant", "user"]
    assert contents == ["u", "a", "u"]
    assert res.response == "a"
