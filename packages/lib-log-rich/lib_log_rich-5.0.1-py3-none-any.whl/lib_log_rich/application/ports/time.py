"""Ports for time, identifiers, and unit-of-work semantics.

Alignment Notes
---------------
Codifies the ancillary ports referenced in ``docs/systemdesign/module_reference.md``
for timekeeping and transactional orchestration.
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
from typing import Protocol, TypeVar, runtime_checkable

T = TypeVar("T")


@runtime_checkable
class ClockPort(Protocol):
    """Provide the current timestamp.

    Examples
    --------
    >>> class FixedClock:
    ...     def now(self) -> datetime:
    ...         return datetime(2025, 9, 30, 12, 0)
    >>> isinstance(FixedClock(), ClockPort)
    True
    """

    def now(self) -> datetime:
        """Return the current timestamp according to the implementation.

        Returns
        -------
        datetime
            Timestamp used for log event creation.
        """
        ...


@runtime_checkable
class IdProvider(Protocol):
    """Generate unique identifiers for log events.

    Examples
    --------
    >>> class Incremental:
    ...     def __init__(self):
    ...         self.counter = 0
    ...     def __call__(self) -> str:
    ...         self.counter += 1
    ...         return str(self.counter)
    >>> isinstance(Incremental(), IdProvider)
    True
    """

    def __call__(self) -> str:
        """Return a unique identifier for log events.

        Returns
        -------
        str
            Identifier suitable for ``LogEvent.event_id``.
        """
        ...


@runtime_checkable
class UnitOfWork(Protocol[T]):
    """Execute a callable within an adapter-managed transactional scope.

    Why
    ---
    Supports future persistence integrations that need begin/commit semantics.

    Examples
    --------
    >>> class Immediate(UnitOfWork[int]):
    ...     def run(self, fn: Callable[[], int]) -> int:
    ...         return fn()
    >>> isinstance(Immediate(), UnitOfWork)
    True
    """

    def run(self, fn: Callable[[], T]) -> T:
        """Execute ``fn`` inside the adapter-managed transactional context.

        Parameters
        ----------
        fn:
            Callable representing the work to execute.

        Returns
        -------
        T
            Result of invoking ``fn``.
        """
        ...


__all__ = ["ClockPort", "IdProvider", "UnitOfWork"]
