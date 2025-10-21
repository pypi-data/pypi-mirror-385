"""Progress utilities used by SimulationRunner."""

from __future__ import annotations

from contextlib import contextmanager
from importlib import import_module
from typing import TYPE_CHECKING
from typing import Protocol
from typing import cast

if TYPE_CHECKING:  # pragma: no cover - typing-only imports for ruff TC003
    from collections.abc import Iterator
    from collections.abc import Mapping
    from types import TracebackType

    ExcInfo = (
        tuple[type[BaseException], BaseException, TracebackType | None]
        | tuple[None, None, None]
        | BaseException
        | None
    )


class LoggerProtocol(Protocol):
    """Subset of logging.Logger used by the progress utilities."""

    def debug(
        self,
        msg: object,
        *args: object,
        exc_info: ExcInfo | bool = ...,
        stack_info: bool = ...,
        stacklevel: int = ...,
        extra: Mapping[str, object] | None = ...,
    ) -> None:
        """Log a debug message."""

    def exception(
        self,
        msg: object,
        *args: object,
        exc_info: ExcInfo | bool = ...,
        stack_info: bool = ...,
        stacklevel: int = ...,
        extra: Mapping[str, object] | None = ...,
    ) -> None:
        """Log an exception message."""


class Progress(Protocol):
    """Protocol defining the minimal hooks needed by SimulationRunner."""

    def update(self, step: int) -> None:
        """Advance the underlying progress indicator."""

    def adjust_total(self, decrement: int) -> None:
        """Reduce the total count when some work is skipped."""


class NoopProgress:
    """No-op implementation when progress is disabled."""

    def update(self, _step: int) -> None:
        """Ignore progress updates when tracking is disabled."""

    def adjust_total(self, _decrement: int) -> None:
        """Ignore adjustment requests when tracking is disabled."""

    def close(self) -> None:
        """Nothing to close for the no-op progress implementation."""


class TqdmLike(Protocol):
    """Minimal subset of the tqdm API used by the SDK."""

    total: int
    n: int

    def update(self, n: int) -> None:
        """Advance the progress bar by ``n`` units."""
        ...

    def refresh(self) -> None:
        """Redraw the progress bar UI."""
        ...

    def close(self) -> None:
        """Release any resources held by the bar."""
        ...


class TqdmFactory(Protocol):
    """Callable creating a ``TqdmLike`` instance with named args."""

    def __call__(self, *, total: int, desc: str, unit: str) -> TqdmLike:
        """Create a progress bar with named parameters."""
        ...


class TqdmProgress:
    """Progress adapter that defers to a tqdm progress bar instance."""

    def __init__(self, bar: TqdmLike, logger: LoggerProtocol) -> None:
        """Store the wrapped tqdm bar and logger."""
        self._bar = bar
        self._logger = logger

    def update(self, step: int) -> None:
        """Advance the wrapped tqdm bar, logging failures."""
        if step <= 0:
            return
        try:
            self._bar.update(step)
        except Exception:
            self._logger.debug("Progress update failed", exc_info=True)

    def adjust_total(self, decrement: int) -> None:
        """Reduce the total size of the tqdm bar when work is skipped."""
        if decrement <= 0:
            return
        try:
            current_total = self._bar.total
            new_total = max(self._bar.n, current_total - decrement)
            if new_total != current_total:
                self._bar.total = new_total
                self._bar.refresh()
        except Exception:
            self._logger.debug("Progress total adjustment failed", exc_info=True)

    def close(self) -> None:
        """Close the tqdm bar, ignoring any cleanup errors."""
        try:
            self._bar.close()
        except Exception:
            self._logger.debug("Failed to close progress bar", exc_info=True)


@contextmanager
def progress_manager(
    *,
    enabled: bool,
    total: int,
    logger: LoggerProtocol,
) -> Iterator[Progress]:
    """Yield a progress handle backed by tqdm when available."""
    if not enabled or total <= 0:
        yield NoopProgress()
        return
    try:
        tqdm_mod = import_module("tqdm.auto")
        tqdm_factory = cast("TqdmFactory", tqdm_mod.tqdm)
    except Exception:
        logger.debug("tqdm not available; progress disabled.")
        yield NoopProgress()
        return
    try:
        bar = tqdm_factory(
            total=total,
            desc="User/Assistant turns",
            unit="query",
        )
    except Exception:
        logger.exception("Failed to initialize progress bar; continuing without it.")
        yield NoopProgress()
        return
    handle = TqdmProgress(bar, logger)
    try:
        yield handle
    finally:
        handle.close()
