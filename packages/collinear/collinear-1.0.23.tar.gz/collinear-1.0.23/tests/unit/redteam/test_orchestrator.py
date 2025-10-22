"""Unit tests for the redteam orchestrator components."""

import pytest

from collinear.redteam.orchestrator import RedteamOrchestrator
from collinear.redteam.schemas import ModelConfig
from collinear.redteam.schemas import RedteamConfig


def _config() -> RedteamConfig:
    attacker = ModelConfig(model="a")
    target = ModelConfig(model="b")
    evaluation = ModelConfig(model="c")
    return RedteamConfig(attacker=attacker, target=target, evaluation=evaluation)


def test_orchestrator_success(monkeypatch: pytest.MonkeyPatch) -> None:
    """Happy-path orchestration returns a handle with an id."""
    orch = RedteamOrchestrator(timeout=0.1)

    class _FakeClient:
        def start(self, payload: dict[str, object]) -> dict[str, object]:
            assert "attacker_config" in payload
            return {"evaluation_id": "123"}

        def get_result(self, evaluation_id: str) -> dict[str, object]:
            assert evaluation_id == "123"
            return {"status": "COMPLETED"}

    monkeypatch.setattr(orch, "client", _FakeClient())
    handle = orch.run(_config())
    assert handle.id == "123"
    status = handle.status().get("status")
    assert isinstance(status, str)
    assert status == "COMPLETED"


def test_orchestrator_missing_eval_id(monkeypatch: pytest.MonkeyPatch) -> None:
    """Missing evaluation_id raises an error."""
    orch = RedteamOrchestrator(timeout=0.1)

    class _NoIdClient:
        def start(self, payload: dict[str, object]) -> dict[str, object]:
            assert isinstance(payload, dict)
            return {"ok": True}

    monkeypatch.setattr(orch, "client", _NoIdClient())
    with pytest.raises(RuntimeError):
        orch.run(_config())
