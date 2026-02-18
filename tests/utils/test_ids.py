"""Tests for phoenix_lib.utils.ids."""

import string

from phoenix_lib.utils.ids import short_id


class TestShortId:
    def test_default_length(self):
        result = short_id()
        assert len(result) == 8

    def test_custom_length(self):
        assert len(short_id(length=4)) == 4
        assert len(short_id(length=16)) == 16
        assert len(short_id(length=1)) == 1

    def test_zero_length(self):
        assert short_id(length=0) == ""

    def test_only_lowercase_and_digits(self):
        allowed = set(string.ascii_lowercase + string.digits)
        for _ in range(20):
            result = short_id(12)
            assert set(result).issubset(allowed), f"Unexpected chars in: {result}"

    def test_returns_string(self):
        assert isinstance(short_id(), str)

    def test_randomness(self):
        # Generate 100 IDs; they should not all be identical
        ids = {short_id() for _ in range(100)}
        assert len(ids) > 1, "short_id() generated the same value 100 times"

    def test_large_length(self):
        result = short_id(length=128)
        assert len(result) == 128
        assert result.isalnum()
        assert result == result.lower()
