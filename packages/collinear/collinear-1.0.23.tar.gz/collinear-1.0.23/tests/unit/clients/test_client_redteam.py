"""Tests for Client.redteam orchestration convenience method."""

import pytest

from collinear.client import Client
from collinear.redteam.client import RedteamClient
from collinear.redteam.client import RedteamHandle


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


def test_redteam_starts_evaluation(monkeypatch: pytest.MonkeyPatch) -> None:
    """Redteam evaluation can be started without providing behaviors."""
    c = _client()
    monkeypatch.setattr(c, "redteam_orchestrator_cache", _StubOrchestrator())
    h = c.redteam()
    assert h.id == "E1"
    status_obj = h.status().get("status")
    assert isinstance(status_obj, str)
    assert status_obj in {"QUEUED", "COMPLETED"}
