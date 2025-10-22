"""Tests for local assess flow (no platform calls)."""

from __future__ import annotations

import pytest
from _pytest.monkeypatch import MonkeyPatch

from collinear.assess.local import LocalSafetyAssessor
from collinear.client import Client
from collinear.schemas.assessment import Score
from collinear.schemas.traitmix import SimulationResult


def test_assess_local_returns_scores(monkeypatch: MonkeyPatch) -> None:
    """Client.assess uses LocalSafetyAssessor and returns expected shape."""

    def fake_score_one(
        assessor_instance: LocalSafetyAssessor,
        conv_prefix: list[dict[str, object]],
        response_text: str,
    ) -> Score:
        del assessor_instance, conv_prefix, response_text
        return Score(score=4.0, rationale="ok")

    monkeypatch.setattr(LocalSafetyAssessor, "score_one", fake_score_one)

    client = Client(
        assistant_model_url="https://example.test/v1",
        assistant_model_api_key="key",
        assistant_model_name="gpt-test",
        collinear_api_key="demo-001",
    )

    sims: list[SimulationResult] = [
        SimulationResult(conv_prefix=[{"role": "user", "content": "hi"}], response="a"),
        SimulationResult(conv_prefix=[{"role": "user", "content": "hi2"}], response="b"),
    ]

    res = client.assess(dataset=sims)

    expected_count = 2
    expected_score = 4.0

    assert res.message == "Conversation evaluated"
    assert len(res.evaluation_result) == expected_count

    score0 = next(iter(res.evaluation_result[0].values()))
    score1 = next(iter(res.evaluation_result[1].values()))
    assert isinstance(score0, Score)
    assert isinstance(score1, Score)
    assert score0.score == expected_score
    assert score1.score == expected_score
    assert score0.rationale == "ok"
    assert score1.rationale == "ok"


def test_assess_local_raises_on_empty() -> None:
    """Empty datasets are rejected."""
    client = Client(
        assistant_model_url="https://example.test/v1",
        assistant_model_api_key="key",
        assistant_model_name="gpt-test",
        collinear_api_key="demo-001",
    )
    with pytest.raises(ValueError, match="Dataset cannot be empty"):
        client.assess(dataset=[])
