"""Tests targeting the local safety assessor helpers."""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import cast

from _pytest.monkeypatch import MonkeyPatch

from collinear.assess import local
from collinear.assess.local import LocalGuardConfig
from collinear.assess.local import LocalSafetyAssessor
from collinear.schemas.assessment import AssessmentResponse
from collinear.schemas.assessment import Score
from collinear.schemas.traitmix import SimulationResult
from tests.helpers.openai import DummyOpenAI

PARSE_ATTR = "_parse_guard_output"
RENDER_ATTR_NAME = "_render_user_prompt"
if TYPE_CHECKING:
    from collections.abc import Callable


PARSE_GUARD_OUTPUT = cast(
    "Callable[[str], dict[str, object]]",
    getattr(local, PARSE_ATTR),
)
RENDER_USER_PROMPT = cast(
    "Callable[[list[dict[str, object]], str], str]",
    getattr(local, RENDER_ATTR_NAME),
)
EXPECTED_FALLBACK_SCORE = 2
EXPECTED_OPENAI_SCORE = 5
EXPECTED_DATASET_SIZE = 2


def test_parse_guard_output_prefers_json() -> None:
    """Parse JSON output with score, rationale, and category."""
    payload = '{"score": 4.6, "rationale": "okay", "category": "safe"}'
    parsed = PARSE_GUARD_OUTPUT(payload)
    assert parsed == {"score": 4, "rationale": "okay", "category": "safe"}


def test_parse_guard_output_result_fallback() -> None:
    """Accept [RESULT] fallback syntax when JSON is absent."""
    payload = "some notes before\n[RESULT] 2"
    parsed = PARSE_GUARD_OUTPUT(payload)
    assert parsed["score"] == EXPECTED_FALLBACK_SCORE
    assert parsed["rationale"] == "some notes before"
    assert parsed["category"] == "Not Applicable"


def test_parse_guard_output_empty_defaults() -> None:
    """Empty strings yield the zero score fallback mapping."""
    parsed = PARSE_GUARD_OUTPUT("  ")
    assert parsed == {"score": 0, "rationale": "", "category": "unknown"}


def test_parse_guard_output_handles_malformed_json() -> None:
    """Malformed JSON payloads fall back to the unknown default."""
    payload = 'leading text {"score": "bad",}'
    parsed = PARSE_GUARD_OUTPUT(payload)
    assert parsed == {"score": 0, "rationale": "", "category": "unknown"}


def test_parse_guard_output_invalid_result_score_defaults() -> None:
    """Overflowing numeric [RESULT] suffixes fall back to zero score."""
    payload = "notes before [RESULT] " + "9" * 400
    parsed = PARSE_GUARD_OUTPUT(payload)
    assert parsed["score"] == 0
    assert parsed["rationale"] == "notes before"
    assert parsed["category"] == "Not Applicable"


def test_render_user_prompt_includes_conversation() -> None:
    """Ensure the rendered prompt includes context and evaluation target."""
    conv: list[dict[str, object]] = [
        {"role": "user", "content": "hello"},
        {"role": "assistant", "content": "hi"},
    ]
    prompt = RENDER_USER_PROMPT(conv, "final")
    assert "role: content" in prompt
    assert "assistant: final" in prompt
    assert "assistant: hi" in prompt


def test_score_one_uses_openai(monkeypatch: MonkeyPatch) -> None:
    """Construct LocalSafetyAssessor and ensure score_one parses output."""
    monkeypatch.setattr("collinear.assess.local.openai.OpenAI", DummyOpenAI)

    cfg = LocalGuardConfig(
        api_url="https://judge.test",
        api_key="secret",
        model="judge",
        temperature=0.1,
        max_tokens=64,
        timeout=12.0,
    )
    assessor = LocalSafetyAssessor(cfg)

    score = assessor.score_one([], "text")
    assert isinstance(score, Score)
    assert score.score == EXPECTED_OPENAI_SCORE
    assert score.rationale == "clear"


def test_score_dataset_batches(monkeypatch: MonkeyPatch) -> None:
    """score_dataset delegates to score_one for each simulation result."""
    calls: list[str] = []

    def fake_score_one(
        assessor_instance: LocalSafetyAssessor,
        conv: list[dict[str, str]],
        response_text: str,
    ) -> Score:
        del assessor_instance, conv
        calls.append(response_text)
        return Score(score=1.0, rationale=response_text)

    monkeypatch.setattr(LocalSafetyAssessor, "score_one", fake_score_one)

    cfg = LocalGuardConfig(
        api_url="https://judge.test",
        api_key="secret",
        model="judge",
    )
    assessor = LocalSafetyAssessor(cfg)
    dataset = [
        SimulationResult(conv_prefix=[], response="a"),
        SimulationResult(conv_prefix=[], response="b"),
    ]

    result = assessor.score_dataset(dataset)

    assert isinstance(result, AssessmentResponse)
    assert calls == ["a", "b"]
    assert len(result.evaluation_result) == EXPECTED_DATASET_SIZE
    first_score = next(iter(result.evaluation_result[0].values()))
    assert first_score.rationale == "a"
