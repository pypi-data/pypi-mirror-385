"""Logging formatter."""

from __future__ import annotations

import sys
from datetime import datetime
from typing import Any, Mapping, MutableMapping

import structlog


def iso_datetime_processor(_: Any, __: str, event_dict: MutableMapping[str, Any]) -> Mapping[str, Any]:
    """
    Scan the event_dict for datetime values and convert them to ISO strings.
    """
    for key, value in list(event_dict.items()):
        if isinstance(value, datetime):
            event_dict[key] = value.isoformat()
    return event_dict


def configure_logger(*args: Any, **initial_values: Any) -> None:
    """Configure structlog."""

    if not structlog.is_configured():
        structlog.configure_once(
            processors=[
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.dict_tracebacks,
                structlog.processors.format_exc_info,
                structlog.processors.TimeStamper(fmt="iso", utc=True),
                iso_datetime_processor,
                structlog.dev.ConsoleRenderer() if sys.stdout.isatty() else structlog.processors.JSONRenderer(),
            ],
            cache_logger_on_first_use=True,
        )


logger = structlog.get_logger()
