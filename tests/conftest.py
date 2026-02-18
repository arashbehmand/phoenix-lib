"""Shared pytest fixtures and configuration for phoenix_lib test suite."""

import pytest


@pytest.fixture
def tmp_yaml(tmp_path):
    """Factory fixture: write a YAML file and return its path."""

    def _write(name: str, content: str):
        p = tmp_path / name
        p.write_text(content, encoding="utf-8")
        return p

    return _write
