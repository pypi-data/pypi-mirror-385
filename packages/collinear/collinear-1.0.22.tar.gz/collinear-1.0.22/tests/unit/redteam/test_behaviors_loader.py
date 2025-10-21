"""Tests for behavior loading utilities (JSON and Parquet)."""

import importlib
import json
from pathlib import Path

import pytest

from collinear.redteam.behaviors_loader import load_behaviors
from collinear.redteam.behaviors_loader import load_from_parquet


def _valid_behaviors() -> list[dict[str, object]]:
    sets: dict[str, dict[str, object]] = {}
    for s in range(1, 6):
        strategies: dict[str, object] = {}
        for i in range(1, 11):
            strategies[f"strategy_{i}"] = {
                "conversation_plan": {"turn_1": "hi", "final_turn": "bye"},
                "approach": "direct",
            }
        sets[f"Set_{s}"] = strategies
    behavior = {
        "behavior_number": 1,
        "behavior_details": {"intent": "test"},
        "attack_strategies": sets,
    }
    return [behavior]


def test_load_behaviors_list_valid() -> None:
    """Valid list input passes schema validation."""
    data = _valid_behaviors()
    out = load_behaviors(data)
    assert isinstance(out, list)
    assert out[0]["behavior_number"] == 1


def test_load_behaviors_file_json(tmp_path: Path) -> None:
    """Behaviors can be loaded from a JSON file path."""
    data = _valid_behaviors()
    p = tmp_path / "behaviors.json"
    p.write_text(json.dumps(data), encoding="utf-8")
    out = load_behaviors(str(p))
    assert out
    first = out[0]
    assert isinstance(first, dict)
    details_obj = first.get("behavior_details")
    assert isinstance(details_obj, dict)
    val = details_obj.get("intent")
    assert isinstance(val, str)
    assert val == "test"


def test_load_behaviors_file_errors(tmp_path: Path) -> None:
    """Missing file and unsupported extension raise appropriate errors."""
    with pytest.raises(FileNotFoundError):
        load_behaviors(tmp_path / "missing.json")
    bad = tmp_path / "behaviors.txt"
    bad.write_text("[]", encoding="utf-8")
    with pytest.raises(ValueError):
        load_behaviors(str(bad))


def test_load_from_parquet_via_importlib(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Parquet support is imported lazily via importlib and returns rows."""

    # Create a fake pyarrow.parquet module that returns our data
    class _Table:
        def to_pylist(self) -> list[dict[str, object]]:
            return _valid_behaviors()

    class _Parquet:
        def read_table(self, _p: Path) -> _Table:
            return _Table()

    def _fake_import(name: str) -> object:
        assert name == "pyarrow.parquet"
        return _Parquet()

    monkeypatch.setattr(importlib, "import_module", _fake_import)
    parquet_path = tmp_path / "b.parquet"
    parquet_path.write_bytes(b"")
    out = load_from_parquet(parquet_path)
    assert out
    assert out[0]["behavior_number"] == 1
