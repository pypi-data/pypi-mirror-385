"""Windows Event Log adapter.

Purpose
-------
Send structured events to the Windows Event Log via ``win32evtlogutil.ReportEvent``.

Contents
--------
* :data:`_DEFAULT_EVENT_IDS` - default per-level event IDs.
* :data:`_EVENT_TYPES` - Windows event type mapping.
* :class:`WindowsEventLogAdapter` - implementation of :class:`StructuredBackendPort`.

System Role
-----------
Supports Windows deployments by translating :class:`LogEvent` instances into the
native Event Log format.

Alignment Notes
---------------
ID mappings and string payloads mirror the Windows guidance in
``docs/systemdesign/module_reference.md``.
"""

from __future__ import annotations

from typing import Any, Callable, Mapping, Sequence, cast

from lib_log_rich.application.ports.structures import StructuredBackendPort
from lib_log_rich.domain.events import LogEvent
from lib_log_rich.domain.levels import LogLevel

Reporter = Callable[..., None]

_DEFAULT_EVENT_IDS: Mapping[LogLevel, int] = {
    LogLevel.INFO: 1000,
    LogLevel.WARNING: 2000,
    LogLevel.ERROR: 3000,
    LogLevel.CRITICAL: 4000,
}

"""Default event ID mapping used when callers do not override values."""

_EVENT_TYPES: Mapping[LogLevel, int] = {
    LogLevel.INFO: 0x0004,
    LogLevel.WARNING: 0x0002,
    LogLevel.ERROR: 0x0001,
    LogLevel.CRITICAL: 0x0001,
    LogLevel.DEBUG: 0x0004,
}

"""Windows event type constants keyed by :class:`LogLevel`."""


def _default_reporter(*, app_name: str, event_id: int, event_type: int, strings: list[str]) -> None:  # pragma: no cover
    """Call :func:`win32evtlogutil.ReportEvent`, raising when pywin32 is missing."""
    try:
        from win32evtlogutil import ReportEvent  # type: ignore[import-not-found]
    except ImportError as exc:
        raise RuntimeError("pywin32 is required for Windows Event Log support") from exc
    ReportEvent(app_name, event_id, eventCategory=0, eventType=event_type, strings=strings)


class WindowsEventLogAdapter(StructuredBackendPort):
    """Emit structured events to the Windows Event Log."""

    EVENT_TYPES = _EVENT_TYPES

    def __init__(
        self,
        *,
        reporter: Reporter | None = None,
        event_ids: Mapping[LogLevel, int] | None = None,
    ) -> None:
        """Initialise the adapter with an optional reporter and ID overrides."""
        self._reporter = reporter or _default_reporter
        self._event_ids = {**_DEFAULT_EVENT_IDS, **(event_ids or {})}

    def emit(self, event: LogEvent) -> None:
        """Report ``event`` to the Windows Event Log."""
        strings = self._build_strings(event)
        event_id = self._event_ids.get(event.level, self._event_ids[LogLevel.INFO])
        event_type = _EVENT_TYPES.get(event.level, 0x0004)
        self._reporter(
            app_name=event.context.service,
            event_id=event_id,
            event_type=event_type,
            strings=strings,
        )

    @staticmethod
    def _build_strings(event: LogEvent) -> list[str]:
        """Build the message string array consumed by ``ReportEvent``.

        Examples
        --------
        >>> from datetime import datetime, timezone
        >>> from lib_log_rich.domain.context import LogContext
        >>> ctx = LogContext(service='svc', environment='prod', job_id='job', process_id_chain=(1, 2))
        >>> event = LogEvent('id', datetime(2025, 9, 30, 12, 0, tzinfo=timezone.utc), 'svc', LogLevel.WARNING, 'msg', ctx, extra={'foo': 'bar'})
        >>> strings = WindowsEventLogAdapter._build_strings(event)
        >>> strings[0]
        'msg'
        >>> any('PROCESS_ID_CHAIN=1>2' == line for line in strings)
        True
        """
        context = event.context.to_dict()
        chain_raw = context.get("process_id_chain")
        if isinstance(chain_raw, (list, tuple)):
            chain_iter = cast(Sequence[object], chain_raw)
            chain_parts = [str(value) for value in chain_iter]
        elif chain_raw:
            chain_parts = [str(chain_raw)]
        else:
            chain_parts = []
        chain_str = ">".join(chain_parts) if chain_parts else ""
        lines: list[str] = [event.message]
        context_items = cast(Sequence[tuple[str, Any]], tuple(context.items()))
        for key, value in sorted(context_items):
            if key in {"extra", "process_id_chain"}:
                continue
            lines.append(f"{key}={value}")
        if chain_str:
            lines.append(f"PROCESS_ID_CHAIN={chain_str}")
        if event.extra:
            lines.append(f"EXTRA={event.extra}")
        return lines


__all__ = ["WindowsEventLogAdapter"]
