"""Runtime state container and access helpers."""

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
from threading import RLock
from typing import Any, Awaitable, Callable, Iterator, Mapping

from lib_log_rich.adapters.queue import QueueAdapter
from lib_log_rich.domain import ContextBinder, LogLevel, SeverityMonitor
from ._settings import PayloadLimits

_DUPLICATE_INIT_ERROR = "lib_log_rich.init() cannot be called twice without shutdown(); call lib_log_rich.shutdown() first"

_IN_PROGRESS_INIT_ERROR = "lib_log_rich.init() is already running in another thread"


@dataclass(slots=True)
class LoggingRuntime:
    """Aggregate of live collaborators assembled by the composition root."""

    binder: ContextBinder
    process: Callable[..., dict[str, Any]]
    capture_dump: Callable[..., str]
    shutdown_async: Callable[[], Awaitable[None] | None]
    queue: QueueAdapter | None
    service: str
    environment: str
    console_level: LogLevel
    backend_level: LogLevel
    graylog_level: LogLevel
    severity_monitor: SeverityMonitor
    theme: str | None
    console_styles: Mapping[str, str] | None
    limits: PayloadLimits


_runtime_state: LoggingRuntime | None = None
_runtime_lock = RLock()
_initialising = False


def set_runtime(runtime: LoggingRuntime) -> None:
    """Install ``runtime`` as the active singleton."""

    with runtime_initialisation() as install:
        install(runtime)


def clear_runtime() -> None:
    """Remove the active runtime if present."""

    with _runtime_lock:
        global _runtime_state
        _runtime_state = None


def current_runtime() -> LoggingRuntime:
    """Return the active runtime or raise when uninitialised."""

    with _runtime_lock:
        if _runtime_state is None:
            raise RuntimeError("lib_log_rich.init() must be called before using the logging API")
        return _runtime_state


def is_initialised() -> bool:
    """Return ``True`` when :func:`lib_log_rich.init` has been called."""

    with _runtime_lock:
        return _runtime_state is not None


@contextmanager
def runtime_initialisation() -> Iterator[Callable[[LoggingRuntime], None]]:
    """Yield a setter that installs the runtime atomically."""

    global _initialising

    with _runtime_lock:
        if _runtime_state is not None:
            raise RuntimeError(_DUPLICATE_INIT_ERROR)
        if _initialising:
            raise RuntimeError(_IN_PROGRESS_INIT_ERROR)
        _initialising = True

    installed = False

    def _install(runtime: LoggingRuntime) -> None:
        nonlocal installed
        with _runtime_lock:
            global _runtime_state, _initialising
            if _runtime_state is not None:
                raise RuntimeError(_DUPLICATE_INIT_ERROR)
            _runtime_state = runtime
            _initialising = False
            installed = True

    try:
        yield _install
    except Exception:  # pragma: no cover - defensive clean-up
        with _runtime_lock:
            if not installed:
                _initialising = False
        raise
    else:
        if not installed:
            with _runtime_lock:
                _initialising = False
            raise RuntimeError("Runtime initialisation guard exited without installing a runtime")


__all__ = [
    "LoggingRuntime",
    "clear_runtime",
    "current_runtime",
    "is_initialised",
    "runtime_initialisation",
    "set_runtime",
    "_DUPLICATE_INIT_ERROR",
]
