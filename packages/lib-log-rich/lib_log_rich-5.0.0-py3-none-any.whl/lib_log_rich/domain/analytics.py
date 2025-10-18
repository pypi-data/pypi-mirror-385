"""Severity analytics helpers for processed log events.

Purpose
-------
Provide thread-safe counters that track the highest severity observed
and per-level tallies without mixing analytics concerns into the ring
buffer implementation.

Contents
--------
* :class:`SeverityMonitor` accumulating level counts and thresholds.

System Role
-----------
Bound into the runtime pipeline so operators can quickly inspect
aggregate severities (e.g., deciding whether to ship a log dump) without
replaying buffered events.

Alignment Notes
---------------
Counter semantics align with ``docs/systemdesign/module_reference.md``
(``Diagnostics & Monitoring`` section). Future histogram ideas are noted
in architectural concepts instead of the executable code.
"""

from __future__ import annotations

from collections import Counter
from threading import RLock
from typing import Iterable, Mapping, Tuple

from .levels import LogLevel


class SeverityMonitor:
    """Accumulate per-level counts and expose the peak severity.

    Why
    ---
    Keeps analytics decoupled from the ring buffer while offering quick
    answers to "did we breach a threshold?" without scanning every
    buffered event.

    Parameters
    ----------
    thresholds:
        Optional iterable of :class:`LogLevel` used to maintain counts for
        "greater or equal" checks (defaults to ``WARNING`` and ``ERROR``).
    drop_reasons:
        Optional iterable initialising recognised drop reasons so snapshots
        always expose stable keys. Provide custom values when you want rich
        dashboards; otherwise common reasons (``rate_limited``/``queue_full``)
        are created lazily.

    Examples
    --------
    >>> monitor = SeverityMonitor()
    >>> monitor.highest() is None
    True
    >>> monitor.record(LogLevel.INFO)
    >>> monitor.record(LogLevel.ERROR)
    >>> monitor.highest() is LogLevel.ERROR
    True
    >>> monitor.counts()[LogLevel.INFO]
    1
    >>> monitor.threshold_counts()[LogLevel.WARNING]
    1
    >>> monitor.record_drop(LogLevel.ERROR, "queue_full")
    >>> monitor.total_events()
    2
    >>> monitor.dropped_total()
    1
    >>> monitor.drops_by_reason()["queue_full"]
    1
    >>> monitor.reset(); monitor.highest() is None
    True
    """

    def __init__(
        self,
        *,
        thresholds: Iterable[LogLevel] | None = None,
        drop_reasons: Iterable[str] | None = None,
    ) -> None:
        self._lock = RLock()
        self._highest: LogLevel | None = None
        self._total_events = 0
        self._level_counts: Counter[LogLevel] = Counter({level: 0 for level in LogLevel})
        if thresholds is None:
            thresholds = (LogLevel.WARNING, LogLevel.ERROR)
        unique_thresholds = {threshold for threshold in thresholds}
        if not unique_thresholds:
            unique_thresholds = {LogLevel.ERROR}
        self._thresholds = tuple(sorted(unique_thresholds, key=lambda lvl: lvl.value))
        self._threshold_counts: Counter[LogLevel] = Counter({level: 0 for level in self._thresholds})
        self._dropped_total = 0
        self._drops_by_reason: Counter[str] = Counter()
        if drop_reasons is not None:
            for reason in drop_reasons:
                canonical = self._normalise_reason(reason)
                self._drops_by_reason[canonical] += 0
        self._drops_by_level: Counter[LogLevel] = Counter({level: 0 for level in LogLevel})
        self._drops_by_reason_and_level: Counter[Tuple[str, LogLevel]] = Counter()

    def record(self, level: LogLevel) -> None:
        """Register an emitted event at ``level``.

        Side Effects
        ------------
        Increments internal counters and updates the cached peak level.
        """

        with self._lock:
            self._total_events += 1
            self._level_counts[level] += 1
            if self._highest is None or level.value > self._highest.value:
                self._highest = level
            for threshold in self._thresholds:
                if level.value >= threshold.value:
                    self._threshold_counts[threshold] += 1

    def record_drop(self, level: LogLevel, reason: str) -> None:
        """Register that an event of ``level`` was dropped for ``reason``."""

        canonical = self._normalise_reason(reason)
        with self._lock:
            self._dropped_total += 1
            self._drops_by_reason[canonical] += 1
            self._drops_by_level[level] += 1
            self._drops_by_reason_and_level[(canonical, level)] += 1

    def highest(self) -> LogLevel | None:
        """Return the highest severity observed so far."""

        with self._lock:
            return self._highest

    def counts(self) -> Mapping[LogLevel, int]:
        """Return a snapshot of per-level counts."""

        with self._lock:
            return dict(self._level_counts)

    def threshold_counts(self) -> Mapping[LogLevel, int]:
        """Return counts of events meeting configured thresholds."""

        with self._lock:
            return dict(self._threshold_counts)

    def total_events(self) -> int:
        """Return the total number of recorded events."""

        with self._lock:
            return self._total_events

    def dropped_total(self) -> int:
        """Return the total number of dropped events."""

        with self._lock:
            return self._dropped_total

    def drops_by_reason(self) -> Mapping[str, int]:
        """Return drop counts keyed by drop reason."""

        with self._lock:
            return dict(self._drops_by_reason)

    def drops_by_level(self) -> Mapping[LogLevel, int]:
        """Return drop counts grouped by severity level."""

        with self._lock:
            return dict(self._drops_by_level)

    def drops_by_reason_and_level(self) -> Mapping[Tuple[str, LogLevel], int]:
        """Return drop counts keyed by ``(reason, level)`` tuples."""

        with self._lock:
            return dict(self._drops_by_reason_and_level)

    def reset(self) -> None:
        """Clear counters and forget the current peak."""

        with self._lock:
            self._highest = None
            self._total_events = 0
            self._level_counts = Counter({level: 0 for level in LogLevel})
            self._threshold_counts = Counter({level: 0 for level in self._thresholds})
            self._dropped_total = 0
            self._drops_by_reason = Counter({reason: 0 for reason in self._drops_by_reason})
            self._drops_by_level = Counter({level: 0 for level in LogLevel})
            self._drops_by_reason_and_level = Counter()

    @staticmethod
    def _normalise_reason(reason: str) -> str:
        candidate = reason.strip().lower()
        return candidate or "unspecified"


__all__ = ["SeverityMonitor"]
