"""Structured logging configuration shared across Phoenix services."""

import logging
import sys


def configure_logging(log_level: str = "INFO") -> None:
    """Configure structured logging using structlog (with stdlib fallback).

    Call this once at application startup, before any loggers are created.

    Args:
        log_level: Log level string (e.g. "INFO", "DEBUG"). Defaults to "INFO".
    """
    level_int = getattr(logging, log_level.upper(), logging.INFO)

    try:
        import structlog  # pylint: disable=import-outside-toplevel
    except Exception:  # pylint: disable=broad-exception-caught
        # Fallback: plain stdlib logging when structlog is unavailable
        logging.basicConfig(format="%(message)s", stream=sys.stdout, level=level_int)
        return

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(level_int),
        cache_logger_on_first_use=True,
    )

    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=level_int,
    )


def get_logger(name: str):
    """Return a structured logger for the given module name.

    Uses structlog when available, falling back to a stdlib adapter that
    accepts arbitrary keyword arguments.

    Args:
        name: Logger name (typically ``__name__``).

    Returns:
        structlog bound logger or a stdlib LoggerAdapter.
    """
    try:
        import structlog  # pylint: disable=import-outside-toplevel

        return structlog.get_logger(name)
    except Exception:  # pylint: disable=broad-exception-caught
        base = logging.getLogger(name)

        class _StdlibAdapter(logging.LoggerAdapter):
            def process(self, msg, kwargs):
                extra = kwargs.pop("extra", {}) or {}
                for k in list(kwargs.keys()):
                    if k not in ("exc_info", "stack_info", "stacklevel"):
                        extra[k] = kwargs.pop(k)
                kwargs["extra"] = extra
                return msg, kwargs

        return _StdlibAdapter(base, {})
