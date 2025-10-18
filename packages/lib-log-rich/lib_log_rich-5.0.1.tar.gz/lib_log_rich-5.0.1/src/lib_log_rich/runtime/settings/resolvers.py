"""Functions that merge configuration inputs into runtime settings."""

from __future__ import annotations

import os
import sys
from typing import Mapping, Optional

from pydantic import ValidationError

from lib_log_rich.domain import LogLevel
from lib_log_rich.domain.palettes import CONSOLE_STYLE_THEMES

from .models import (  # pyright: ignore[reportPrivateUsage]
    ConsoleAppearance,
    DEFAULT_SCRUB_PATTERNS,
    DumpDefaults,
    FeatureFlags,
    GraylogSettings,
    PayloadLimits,
    RuntimeConfig,
    RuntimeSettings,
    coerce_console_styles_input,
)


def build_runtime_settings(*, config: RuntimeConfig) -> RuntimeSettings:
    """Blend a RuntimeConfig with environment overrides and platform guards."""

    service_value, environment_value = service_and_environment(config.service, config.environment)
    console_level_value, backend_level_value, graylog_level_value = resolve_levels(
        config.console_level,
        config.backend_level,
        config.graylog_level,
    )

    ring_buffer_env = os.getenv("LOG_RING_BUFFER_SIZE")
    if ring_buffer_env is not None:
        try:
            ring_size = int(ring_buffer_env)
        except ValueError as exc:  # pragma: no cover - defensive guards
            raise ValueError("LOG_RING_BUFFER_SIZE must be an integer") from exc
        source_label = "LOG_RING_BUFFER_SIZE"
    else:
        ring_size = config.ring_buffer_size
        source_label = "ring_buffer_size"
    if ring_size <= 0:
        raise ValueError(f"{source_label} must be positive")

    flags = resolve_feature_flags(
        enable_ring_buffer=config.enable_ring_buffer,
        enable_journald=config.enable_journald,
        enable_eventlog=config.enable_eventlog,
        queue_enabled=config.queue_enabled,
    )
    queue_size = resolve_queue_maxsize(config.queue_maxsize)
    queue_policy = resolve_queue_policy(config.queue_full_policy)
    queue_timeout_value = resolve_queue_timeout(config.queue_put_timeout)
    queue_stop_timeout_value = resolve_queue_stop_timeout(config.queue_stop_timeout)
    console_model = resolve_console(
        force_color=config.force_color,
        no_color=config.no_color,
        console_theme=config.console_theme,
        console_styles=config.console_styles,
        console_format_preset=config.console_format_preset,
        console_format_template=config.console_format_template,
        console_stream=config.console_stream,
        console_stream_target=config.console_stream_target,
    )
    dump_defaults = resolve_dump_defaults(
        dump_format_preset=config.dump_format_preset,
        dump_format_template=config.dump_format_template,
    )
    graylog_settings = resolve_graylog(
        enable_graylog=config.enable_graylog,
        graylog_endpoint=config.graylog_endpoint,
        graylog_protocol=config.graylog_protocol,
        graylog_tls=config.graylog_tls,
        graylog_level=graylog_level_value,
    )
    rate_limit_value = resolve_rate_limit(config.rate_limit)
    patterns = resolve_scrub_patterns(config.scrub_patterns)
    if config.payload_limits is None:
        limits_model = PayloadLimits()
    elif isinstance(config.payload_limits, PayloadLimits):
        limits_model = config.payload_limits
    else:
        limits_model = PayloadLimits(**dict(config.payload_limits))

    try:
        return RuntimeSettings(
            service=service_value,
            environment=environment_value,
            console_level=console_level_value,
            backend_level=backend_level_value,
            graylog_level=graylog_level_value,
            ring_buffer_size=ring_size,
            console=console_model,
            dump=dump_defaults,
            graylog=graylog_settings,
            flags=flags,
            rate_limit=rate_limit_value,
            limits=limits_model,
            scrub_patterns=patterns,
            diagnostic_hook=config.diagnostic_hook,
            console_factory=config.console_adapter_factory,
            queue_maxsize=queue_size,
            queue_full_policy=queue_policy,
            queue_put_timeout=queue_timeout_value,
            queue_stop_timeout=queue_stop_timeout_value,
        )
    except ValidationError as exc:
        raise ValueError(str(exc)) from exc


def service_and_environment(service: str, environment: str) -> tuple[str, str]:
    """Return service/environment after environment overrides."""

    return os.getenv("LOG_SERVICE", service), os.getenv("LOG_ENVIRONMENT", environment)


def resolve_levels(
    console_level: str | LogLevel,
    backend_level: str | LogLevel,
    graylog_level: str | LogLevel,
) -> tuple[str | LogLevel, str | LogLevel, str | LogLevel]:
    """Apply environment overrides to severity thresholds."""

    return (
        os.getenv("LOG_CONSOLE_LEVEL", console_level),
        os.getenv("LOG_BACKEND_LEVEL", backend_level),
        os.getenv("LOG_GRAYLOG_LEVEL", graylog_level),
    )


def resolve_feature_flags(
    *,
    enable_ring_buffer: bool,
    enable_journald: bool,
    enable_eventlog: bool,
    queue_enabled: bool,
) -> FeatureFlags:
    """Determine adapter feature flags with platform guards."""

    ring_buffer = env_bool("LOG_RING_BUFFER_ENABLED", enable_ring_buffer)
    journald = env_bool("LOG_ENABLE_JOURNALD", enable_journald)
    eventlog = env_bool("LOG_ENABLE_EVENTLOG", enable_eventlog)
    queue = env_bool("LOG_QUEUE_ENABLED", queue_enabled)
    if sys.platform.startswith("win"):
        journald = False
    else:
        eventlog = False
    return FeatureFlags(queue=queue, ring_buffer=ring_buffer, journald=journald, eventlog=eventlog)


def resolve_console(
    *,
    force_color: bool,
    no_color: bool,
    console_theme: str | None,
    console_styles: Mapping[str, str] | Mapping[LogLevel, str] | None,
    console_format_preset: str | None,
    console_format_template: str | None,
    console_stream: str,
    console_stream_target: object | None,
) -> ConsoleAppearance:
    """Blend console formatting inputs with environment overrides."""

    force = env_bool("LOG_FORCE_COLOR", force_color)
    no = env_bool("LOG_NO_COLOR", no_color)
    env_styles = parse_console_styles(os.getenv("LOG_CONSOLE_STYLES"))
    theme_override = os.getenv("LOG_CONSOLE_THEME")
    theme = theme_override or console_theme
    preset = os.getenv("LOG_CONSOLE_FORMAT_PRESET") or console_format_preset
    template = os.getenv("LOG_CONSOLE_FORMAT_TEMPLATE") or console_format_template
    stream_candidate = os.getenv("LOG_CONSOLE_STREAM") or console_stream
    stream_value = stream_candidate.strip().lower() if stream_candidate else "stderr"
    if stream_value not in {"stdout", "stderr", "both", "custom", "none"}:
        raise ValueError("console stream must be one of 'stdout', 'stderr', 'both', 'custom', or 'none'")
    stream_target = console_stream_target if stream_value == "custom" else None
    if stream_value == "custom" and stream_target is None:
        raise ValueError("console_stream_target must be provided when console stream is 'custom'")
    explicit_styles = coerce_console_styles_input(console_styles)
    resolved_theme, resolved_styles = resolve_console_palette(theme, explicit_styles, env_styles)

    return ConsoleAppearance(
        force_color=force,
        no_color=no,
        theme=resolved_theme,
        styles=resolved_styles,
        format_preset=preset,
        format_template=template,
        stream=stream_value,
        stream_target=stream_target,
    )


def resolve_dump_defaults(
    *,
    dump_format_preset: str | None,
    dump_format_template: str | None,
) -> DumpDefaults:
    """Determine dump format defaults respecting environment overrides."""

    preset = os.getenv("LOG_DUMP_FORMAT_PRESET") or dump_format_preset or "full"
    template = os.getenv("LOG_DUMP_FORMAT_TEMPLATE") or dump_format_template
    return DumpDefaults(format_preset=preset, format_template=template)


def resolve_graylog(
    *,
    enable_graylog: bool,
    graylog_endpoint: tuple[str, int] | None,
    graylog_protocol: str,
    graylog_tls: bool,
    graylog_level: str | LogLevel,
) -> GraylogSettings:
    """Resolve Graylog adapter settings with environment overrides."""

    enabled = env_bool("LOG_ENABLE_GRAYLOG", enable_graylog)
    protocol = (os.getenv("LOG_GRAYLOG_PROTOCOL") or graylog_protocol).lower()
    tls = env_bool("LOG_GRAYLOG_TLS", graylog_tls)
    endpoint = coerce_graylog_endpoint(os.getenv("LOG_GRAYLOG_ENDPOINT"), graylog_endpoint)
    return GraylogSettings(enabled=enabled, endpoint=endpoint, protocol=protocol, tls=tls, level=graylog_level)


def resolve_queue_maxsize(default: int) -> int:
    """Return the configured queue capacity."""

    candidate = os.getenv("LOG_QUEUE_MAXSIZE")
    if candidate is None:
        return default
    try:
        value = int(candidate)
    except ValueError:
        return default
    return default if value <= 0 else value


def resolve_queue_policy(default: str) -> str:
    """Normalise queue full handling policy."""

    candidate = os.getenv("LOG_QUEUE_FULL_POLICY")
    policy = (candidate or default).strip().lower()
    return policy if policy in {"block", "drop"} else default.lower()


def resolve_queue_timeout(default: float | None) -> float | None:
    """Resolve queue put timeout from environment overrides."""

    candidate = os.getenv("LOG_QUEUE_PUT_TIMEOUT")
    if candidate is None:
        return default
    try:
        value = float(candidate)
    except ValueError:
        return default
    return None if value <= 0 else value


def resolve_queue_stop_timeout(default: float | None) -> float | None:
    """Resolve queue stop timeout from environment overrides."""

    candidate = os.getenv("LOG_QUEUE_STOP_TIMEOUT")
    if candidate is None:
        return default
    try:
        value = float(candidate)
    except ValueError:
        return default
    if value <= 0:
        return None
    return value


def resolve_rate_limit(value: Optional[tuple[int, float]]) -> Optional[tuple[int, float]]:
    """Return the effective rate limit tuple after env overrides."""

    return coerce_rate_limit(os.getenv("LOG_RATE_LIMIT"), value)


def resolve_scrub_patterns(custom: Optional[dict[str, str]]) -> dict[str, str]:
    """Combine default, custom, and environment-provided scrub patterns."""

    merged = dict(DEFAULT_SCRUB_PATTERNS)
    if custom:
        merged.update(custom)
    env_patterns = parse_scrub_patterns(os.getenv("LOG_SCRUB_PATTERNS"))
    if env_patterns:
        merged.update(env_patterns)
    return merged


def env_bool(name: str, default: bool) -> bool:
    """Interpret an environment variable as a boolean flag."""

    candidate = os.getenv(name)
    if candidate is None:
        return default
    value = candidate.strip().lower()
    if not value:
        return default
    if value in {"1", "true", "yes", "on"}:
        return True
    if value in {"0", "false", "no", "off"}:
        return False
    return default


def parse_console_styles(raw: str | None) -> dict[str, str] | None:
    """Parse environment-provided console styles."""

    if not raw:
        return None
    entries = [segment.strip() for segment in raw.split(",") if segment.strip()]
    mapping: dict[str, str] = {}
    for entry in entries:
        if "=" not in entry:
            continue
        key, value = entry.split("=", 1)
        key = key.strip().upper()
        if key:
            mapping[key] = value.strip()
    return mapping or None


def parse_scrub_patterns(raw: str | None) -> dict[str, str] | None:
    """Parse environment-provided scrub patterns.

    Format: ``field=regex`` pairs separated by commas.
    """

    if not raw:
        return None
    entries = [segment.strip() for segment in raw.split(",") if segment.strip()]
    mapping: dict[str, str] = {}
    for entry in entries:
        if "=" not in entry:
            continue
        key, value = entry.split("=", 1)
        key = key.strip()
        if key:
            mapping[key] = value.strip() or r".+"
    return mapping or None


def coerce_graylog_endpoint(env_value: str | None, fallback: tuple[str, int] | None) -> tuple[str, int] | None:
    """Coerce Graylog endpoint definitions from env or fallback."""

    value = env_value or None
    if value is None:
        return fallback
    if ":" not in value:
        raise ValueError("LOG_GRAYLOG_ENDPOINT must be HOST:PORT")
    host, port_text = value.split(":", 1)
    host = host.strip()
    try:
        port = int(port_text)
    except ValueError as exc:
        raise ValueError("LOG_GRAYLOG_ENDPOINT port must be an integer") from exc
    if port <= 0:
        raise ValueError("LOG_GRAYLOG_ENDPOINT port must be positive")
    return host, port


def coerce_rate_limit(env_value: str | None, fallback: Optional[tuple[int, float]]) -> Optional[tuple[int, float]]:
    """Coerce rate limit tuples from environment overrides."""

    if not env_value:
        return fallback
    if ":" not in env_value:
        raise ValueError("LOG_RATE_LIMIT must be MAX:WINDOW_SECONDS")
    max_text, window_text = env_value.split(":", 1)
    try:
        max_events = int(max_text)
        window = float(window_text)
    except ValueError as exc:
        raise ValueError("LOG_RATE_LIMIT must be MAX:WINDOW_SECONDS with numeric values") from exc
    if max_events <= 0 or window <= 0:
        raise ValueError("LOG_RATE_LIMIT values must be positive")
    return max_events, window


def resolve_console_palette(
    theme: str | None,
    explicit_styles: dict[str, str] | None,
    env_styles: dict[str, str] | None,
) -> tuple[str | None, dict[str, str] | None]:
    """Resolve final console theme and styles."""

    styles: dict[str, str] = {}
    if explicit_styles:
        styles.update(explicit_styles)
    if env_styles:
        styles.update(env_styles)

    resolved_theme = theme
    if not resolved_theme and not styles:
        session_theme = os.getenv("LOG_CONSOLE_THEME")
        resolved_theme = session_theme if session_theme else None

    if resolved_theme:
        theme_key = resolved_theme.strip().lower()
        palette = CONSOLE_STYLE_THEMES.get(theme_key)
        if palette:
            for level, value in palette.items():
                styles.setdefault(level.upper(), value)
    return resolved_theme, styles or None


__all__ = [
    "build_runtime_settings",
    "service_and_environment",
    "resolve_levels",
    "resolve_feature_flags",
    "resolve_console",
    "resolve_dump_defaults",
    "resolve_graylog",
    "resolve_queue_maxsize",
    "resolve_queue_policy",
    "resolve_queue_timeout",
    "resolve_queue_stop_timeout",
    "resolve_rate_limit",
    "resolve_scrub_patterns",
    "env_bool",
    "parse_console_styles",
    "parse_scrub_patterns",
    "coerce_graylog_endpoint",
    "coerce_rate_limit",
    "resolve_console_palette",
]
