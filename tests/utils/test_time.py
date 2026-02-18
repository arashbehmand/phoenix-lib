"""Tests for phoenix_lib.utils.time."""

from datetime import datetime, timezone

from phoenix_lib.utils.time import utc_timestamp


class TestUtcTimestamp:
    def test_returns_string(self):
        assert isinstance(utc_timestamp(), str)

    def test_is_iso_format(self):
        ts = utc_timestamp()
        # Should be parseable as ISO 8601
        parsed = datetime.fromisoformat(ts)
        assert parsed is not None

    def test_is_utc(self):
        ts = utc_timestamp()
        parsed = datetime.fromisoformat(ts)
        # Must have timezone info
        assert parsed.tzinfo is not None
        assert parsed.utcoffset().total_seconds() == 0

    def test_recent_timestamp(self):
        before = datetime.now(timezone.utc)
        ts = utc_timestamp()
        after = datetime.now(timezone.utc)
        parsed = datetime.fromisoformat(ts)
        assert before <= parsed <= after

    def test_successive_calls_are_ordered(self):
        ts1 = utc_timestamp()
        ts2 = utc_timestamp()
        parsed1 = datetime.fromisoformat(ts1)
        parsed2 = datetime.fromisoformat(ts2)
        assert parsed1 <= parsed2
