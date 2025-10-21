"""Pytest configuration: ensure `src` is importable without installing."""

from __future__ import annotations

import sys
from pathlib import Path


def _ensure_src_on_path() -> None:
    root = Path(__file__).parent.parent
    src = root / "src"
    src_str = str(src)

    sys.path.insert(0, src_str)


_ensure_src_on_path()
