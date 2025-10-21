"""Tests for Client.redteam orchestration convenience method."""

import json
from pathlib import Path

import pytest

from collinear.client import Client
from collinear.redteam.client import RedteamClient
from collinear.redteam.client import RedteamHandle


def _valid_behavior() -> dict[str, object]:
    sets: dict[str, dict[str, object]] = {}
    for s in range(1, 6):
        strategies: dict[str, object] = {}
        for i in range(1, 11):
            strategies[f"strategy_{i}"] = {
                "conversation_plan": {"turn_1": "hi", "final_turn": "bye"},
                "approach": "direct",
            }
        sets[f"Set_{s}"] = strategies
    return {
        "behavior_number": 1,
        "behavior_details": {"intent": "test"},
        "attack_strategies": sets,
    }


class _StubClient(RedteamClient):
    def __init__(self) -> None:
        super().__init__(timeout=0.1)

    def get_result(self, evaluation_id: str) -> dict[str, object]:
        assert evaluation_id == "E1"
        return {"status": "COMPLETED"}


class _StubOrchestrator:
    def run(self, _config: object) -> RedteamHandle:
        return RedteamHandle(api=_StubClient(), evaluation_id="E1", initial={"status": "QUEUED"})


def _client() -> Client:
    return Client(
        assistant_model_url="http://localhost",
        assistant_model_api_key="key",
        assistant_model_name="gpt-x",
        collinear_api_key="ck",
    )


def test_redteam_with_inline_behaviors(monkeypatch: pytest.MonkeyPatch) -> None:
    """Inline behaviors are validated and passed to the orchestrator."""
    c = _client()
    monkeypatch.setattr(c, "redteam_orchestrator_cache", _StubOrchestrator())
    h = c.redteam(behaviors=[_valid_behavior()])
    assert h.id == "E1"
    status_obj = h.status().get("status")
    assert isinstance(status_obj, str)
    assert status_obj in {"QUEUED", "COMPLETED"}


def test_redteam_with_input_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Behaviors can be loaded from a JSON file path."""
    c = _client()
    monkeypatch.setattr(c, "redteam_orchestrator_cache", _StubOrchestrator())
    p = tmp_path / "behaviors.json"
    payload_list: list[dict[str, object]] = [_valid_behavior()]
    p.write_text(json.dumps(payload_list), encoding="utf-8")
    h = c.redteam(input_file=p)
    assert h.id == "E1"
