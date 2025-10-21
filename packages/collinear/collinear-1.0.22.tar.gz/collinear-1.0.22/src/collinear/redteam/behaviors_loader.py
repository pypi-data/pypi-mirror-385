"""Utilities for loading behaviors for red-team evaluation."""

from __future__ import annotations

import importlib
import json
from pathlib import Path
from typing import TYPE_CHECKING
from typing import Protocol
from typing import cast

if TYPE_CHECKING:
    # Imported for typing only; annotations are postponed via __future__.
    from collections.abc import Sequence

from pydantic import ValidationError

from collinear.redteam.schemas import Behavior


def load_behaviors(
    source: Sequence[dict[str, object]] | str | Path,
) -> list[dict[str, object]]:
    """Load and validate behavior inputs against schema.

    Args:
        source: Behaviors as inline list of dicts, or path to JSON/Parquet file

    Returns:
        List of validated behavior dictionaries

    Raises:
        FileNotFoundError: If file path doesn't exist
        ValueError: If file format is unsupported or behaviors don't match schema

    """
    if isinstance(source, (list, tuple)):
        behaviors = [cast("dict[str, object]", dict(item)) for item in source]
        return _validate_behaviors(behaviors)

    path = _existing_path(cast("str | Path", source))
    behaviors = _load_behaviors_from_path(path)
    return _validate_behaviors(behaviors)


def _existing_path(source: str | Path) -> Path:
    path = Path(source)
    if not path.exists():
        raise FileNotFoundError(f"Behaviors file not found: {path}")
    return path


def _load_behaviors_from_path(path: Path) -> list[dict[str, object]]:
    loader_map = {
        ".jsonl": _load_jsonl_behaviors,
        ".json": _load_json_behaviors,
        ".parquet": load_from_parquet,
    }
    loader = loader_map.get(path.suffix.lower())
    if loader is None:
        raise ValueError(
            f"Unsupported file extension: {path.suffix}. Use .json, .jsonl, or .parquet"
        )
    return loader(path)


def _load_jsonl_behaviors(path: Path) -> list[dict[str, object]]:
    behaviors: list[dict[str, object]] = []
    content = path.read_text(encoding="utf-8")
    for line_num, line in enumerate(content.splitlines(), start=1):
        line_stripped = line.strip()
        if not line_stripped:
            continue
        try:
            data_obj: object = json.loads(line_stripped)
            if not isinstance(data_obj, dict):
                raise TypeError(f"Line {line_num} must be a JSON object")
            behaviors.append(cast("dict[str, object]", data_obj))
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON on line {line_num}: {exc}") from exc
    return behaviors


def _load_json_behaviors(path: Path) -> list[dict[str, object]]:
    data_obj: object = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data_obj, list):
        raise TypeError("JSON file must contain a list of behaviors")
    if not all(isinstance(item, dict) for item in data_obj):
        raise TypeError("Each behavior entry must be a JSON object")
    return [cast("dict[str, object]", dict(item)) for item in data_obj]


def _validate_behaviors(behaviors: list[dict[str, object]]) -> list[dict[str, object]]:
    for index, behavior_data in enumerate(behaviors, start=1):
        try:
            Behavior.model_validate(behavior_data)
        except ValidationError as exc:
            msg = f"Behavior #{index} validation failed: {exc}"
            raise ValueError(msg) from exc
    return behaviors


def load_from_parquet(path: Path) -> list[dict[str, object]]:
    """Load behaviors from a Parquet file using ``pyarrow``.

    This function imports ``pyarrow`` at runtime to avoid introducing a hard
    dependency for users who do not need Parquet support.

    Args:
        path: Path to a Parquet file.

    Returns:
        List of behavior dictionaries parsed from the Parquet table.

    Raises:
        RuntimeError: If ``pyarrow`` is not installed.

    """
    try:
        pq = importlib.import_module("pyarrow.parquet")
    except Exception as exc:  # ImportError or other import-time failures
        msg = "Loading Parquet requires pyarrow: pip install pyarrow"
        raise RuntimeError(msg) from exc

    class _HasToPylist(Protocol):
        def to_pylist(self) -> list[dict[str, object]]: ...

    table = cast("_HasToPylist", pq.read_table(path))
    return table.to_pylist()
