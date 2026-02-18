"""Time utility functions."""

from datetime import datetime, timezone


def utc_timestamp() -> str:
    """Return current UTC timestamp in ISO format."""
    return datetime.now(timezone.utc).isoformat()
