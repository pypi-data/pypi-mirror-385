"""Tests for the simulate.progress utilities."""

from __future__ import annotations

import sys
import types

from _pytest.monkeypatch import MonkeyPatch

from collinear.simulate import progress

ADJUSTED_TOTAL = 2


def test_progress_manager_disabled() -> None:
    """Return NoopProgress when progress tracking is disabled."""
    with progress.progress_manager(enabled=False, total=5, logger=ProgressLogger()) as handle:
        assert isinstance(handle, progress.NoopProgress)


def test_progress_manager_missing_tqdm(monkeypatch: MonkeyPatch) -> None:
    """Fallback to NoopProgress when tqdm import fails."""

    def fake_import(module_name: str) -> types.ModuleType:
        del module_name
        raise ImportError("missing module")

    monkeypatch.setattr(progress, "import_module", fake_import)

    with progress.progress_manager(enabled=True, total=3, logger=ProgressLogger()) as handle:
        assert isinstance(handle, progress.NoopProgress)


def test_progress_manager_returns_tqdm_handle(monkeypatch: MonkeyPatch) -> None:
    """Return a progress handle backed by a fake tqdm implementation."""
    created: list[FakeBar] = []

    def fake_tqdm(*, total: int, desc: str, unit: str) -> FakeBar:
        bar = FakeBar(total=total, desc=desc, unit=unit)
        created.append(bar)
        return bar

    module = types.SimpleNamespace(tqdm=fake_tqdm)
    monkeypatch.setitem(sys.modules, "tqdm.auto", module)

    logger = ProgressLogger()
    with progress.progress_manager(enabled=True, total=4, logger=logger) as handle:
        handle.update(1)
        handle.adjust_total(2)
        handle.adjust_total(-1)

    assert created[0].updated == [1]
    assert created[0].total == ADJUSTED_TOTAL
    assert logger.debug_calls == []


def test_tqdm_progress_logs_update_errors() -> None:
    """Log debug messages when tqdm operations raise exceptions."""
    bar = ExplodingBar()
    logger = ProgressLogger()
    handle = progress.TqdmProgress(bar, logger)

    handle.update(1)
    handle.adjust_total(1)
    handle.close()

    assert logger.debug_calls  # debug called for update and adjust_total and close failures


def test_tqdm_progress_ignores_non_positive_updates() -> None:
    """Non-positive updates and adjustments are ignored without touching the bar."""
    initial_total = 3
    bar = FakeBar(total=initial_total, desc="desc", unit="query")
    logger = ProgressLogger()
    handle = progress.TqdmProgress(bar, logger)

    handle.update(0)
    handle.adjust_total(0)

    assert bar.updated == []
    assert bar.total == initial_total


def test_tqdm_progress_adjust_total_no_change() -> None:
    """Adjusting when current >= total keeps the total unchanged."""
    initial_total = 3
    bar = FakeBar(total=initial_total, desc="desc", unit="query")
    bar.n = initial_total
    logger = ProgressLogger()
    handle = progress.TqdmProgress(bar, logger)

    handle.adjust_total(1)

    assert bar.total == initial_total


def test_progress_manager_handles_tqdm_failure(monkeypatch: MonkeyPatch) -> None:
    """Initialization failures fall back to the noop progress handle."""

    def fake_tqdm(**unused_kwargs: object) -> object:
        del unused_kwargs
        raise RuntimeError("boom")

    module = types.SimpleNamespace(tqdm=fake_tqdm)
    monkeypatch.setitem(sys.modules, "tqdm.auto", module)

    logger = ProgressLogger()
    with progress.progress_manager(enabled=True, total=2, logger=logger) as handle:
        assert isinstance(handle, progress.NoopProgress)
    assert logger.exception_calls


class ProgressLogger:
    """Minimal logger capturing debug/exception calls."""

    def __init__(self) -> None:
        """Initialize storage for recorded log messages."""
        self.debug_calls: list[str] = []
        self.exception_calls: list[str] = []

    def debug(self, msg: object, *args: object, **kwargs: object) -> None:  # pragma: no cover
        """Record debug messages emitted by the progress adapter."""
        del args, kwargs
        self.debug_calls.append(str(msg))

    def exception(self, msg: object, *args: object, **kwargs: object) -> None:  # pragma: no cover
        """Record exception messages emitted by the progress adapter."""
        del args, kwargs
        self.exception_calls.append(str(msg))


class FakeBar:
    """Fake tqdm bar that records calls for deterministic assertions."""

    def __init__(self, *, total: int, desc: str, unit: str) -> None:
        """Capture the creation arguments and initialize counters."""
        self.total = total
        self.desc = desc
        self.unit = unit
        self.n = 0
        self.updated: list[int] = []
        self.totals: list[int] = []

    def update(self, value: int) -> None:
        """Record update amounts for later verification."""
        self.n += value
        self.updated.append(value)

    def refresh(self) -> None:  # pragma: no cover - trivial
        """No-op refresh implementation for compatibility."""

    def close(self) -> None:  # pragma: no cover - trivial
        """No-op close implementation for compatibility."""


class ExplodingBar:
    """Fake tqdm bar whose methods raise to test logging paths."""

    total = 10
    n = 0

    def update(self, value: int) -> None:
        """Raise an error to simulate tqdm update failure."""
        del value
        raise RuntimeError("boom")

    def refresh(self) -> None:
        """Raise an error to simulate tqdm refresh failure."""
        raise RuntimeError("boom")

    def close(self) -> None:
        """Raise an error to simulate tqdm close failure."""
        raise RuntimeError("boom")
