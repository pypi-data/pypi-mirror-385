"""Deterministic progress helpers for tests."""

from __future__ import annotations

from contextlib import AbstractContextManager
from contextlib import contextmanager
from typing import TYPE_CHECKING
from typing import Protocol

if TYPE_CHECKING:  # typing-only to satisfy ruff TC003
    from collections.abc import Callable
    from collections.abc import Iterator


class FakeProgress:
    """Lightweight progress bar alternative for deterministic assertions."""

    def __init__(self, total: int) -> None:
        """Initialize totals and call tracking for assertions."""
        self.total = total
        self.n = 0
        self.update_calls: list[int] = []
        self.adjust_calls: list[int] = []
        self.closed = False

    def update(self, value: int) -> None:
        """Record an update and accumulate the total advanced."""
        self.n += value
        self.update_calls.append(value)

    def adjust_total(self, decrement: int) -> None:
        """Reduce the remaining total while never dropping below current n."""
        if decrement <= 0:
            return
        self.total = max(self.n, self.total - decrement)
        self.adjust_calls.append(decrement)

    def close(self) -> None:
        """Mark the progress bar as closed for assertions."""
        self.closed = True


class ProgressManagerFactory(Protocol):
    """Protocol for functions that create a progress context manager."""

    def __call__(
        self, *, enabled: bool, total: int, logger: object
    ) -> AbstractContextManager[FakeProgress]:
        """Return a context manager yielding a FakeProgress handle."""
        ...


def make_progress_manager(
    collector: Callable[[FakeProgress], None] | None = None,
) -> ProgressManagerFactory:
    """Return a factory for a context manager yielding FakeProgress instances."""

    @contextmanager
    def progress_manager(*, enabled: bool, total: int, logger: object) -> Iterator[FakeProgress]:
        assert enabled
        del logger
        handle = FakeProgress(total)
        if collector is not None:
            collector(handle)
        try:
            yield handle
        finally:
            handle.close()

    return progress_manager
