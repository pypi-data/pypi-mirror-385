"""Simple logging doubles for tests."""

from __future__ import annotations


class StubLogger:
    """Logger capturing error/debug messages for assertions."""

    def __init__(self) -> None:
        """Initialize internal storage for emitted messages."""
        self.error_messages: list[str] = []
        self.debug_messages: list[str] = []

    def error(self, msg: object, *args: object, **unused_kwargs: object) -> None:
        """Record formatted error messages."""
        del unused_kwargs
        text = str(msg)
        if args:
            text = text % args
        self.error_messages.append(text)

    def debug(self, msg: object, *args: object, **unused_kwargs: object) -> None:
        """Record formatted debug messages."""
        del unused_kwargs
        text = str(msg)
        if args:
            text = text % args
        self.debug_messages.append(text)

    def exception(self, msg: object, *args: object, **unused_kwargs: object) -> None:
        """Record exception log entries."""
        del unused_kwargs
        text = str(msg)
        if args:
            text = text % args
        self.error_messages.append(text)

    def info(self, msg: object, *args: object, **unused_kwargs: object) -> None:
        """Record info messages as debug entries for simplicity."""
        del unused_kwargs
        text = str(msg)
        if args:
            text = text % args
        self.debug_messages.append(text)

    def warning(self, msg: object, *args: object, **unused_kwargs: object) -> None:
        """Record warnings as error entries to simplify assertions."""
        del unused_kwargs
        text = str(msg)
        if args:
            text = text % args
        self.error_messages.append(text)


class RecorderLogger:
    """Minimal logger that records warning calls used in tests."""

    def __init__(self) -> None:
        """Initialize a list to store all warning call tuples."""
        self.warning_calls: list[tuple[object, ...]] = []

    def warning(self, msg: object, *args: object, **kwargs: object) -> None:
        """Append a record of the warning call arguments for later checks."""
        self.warning_calls.append((msg, *args, *kwargs.values()))
