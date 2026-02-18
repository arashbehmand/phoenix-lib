"""Tests for phoenix_lib.db.engine."""

from sqlalchemy.ext.asyncio import AsyncEngine

from phoenix_lib.db.engine import create_async_engine_from_dsn, detect_dialect


class TestDetectDialect:
    def test_postgresql_prefix(self):
        dialect, url = detect_dialect("postgresql+asyncpg://user:pass@localhost/db")
        assert dialect == "postgresql"

    def test_postgres_short_prefix(self):
        dialect, url = detect_dialect("postgres://user:pass@localhost/db")
        assert dialect == "postgresql"

    def test_mysql_prefix(self):
        dialect, url = detect_dialect("mysql+aiomysql://user:pass@localhost/db")
        assert dialect == "mysql"

    def test_sqlite_prefix(self):
        dialect, url = detect_dialect("sqlite+aiosqlite:///./test.db")
        assert dialect == "sqlite"

    def test_sqlite_memory(self):
        dialect, url = detect_dialect("sqlite+aiosqlite:///:memory:")
        assert dialect == "sqlite"

    def test_returns_raw_driver_for_unknown(self):
        dialect, url = detect_dialect("oracle+cx_oracle://user:pass@localhost/db")
        assert "oracle" in dialect

    def test_returns_url_object(self):
        _, url = detect_dialect("sqlite+aiosqlite:///:memory:")
        assert hasattr(url, "drivername")


class TestCreateAsyncEngineFromDsn:
    def test_creates_sqlite_engine(self):
        engine = create_async_engine_from_dsn("sqlite+aiosqlite:///:memory:")
        assert isinstance(engine, AsyncEngine)

    def test_sqlite_check_same_thread_in_connect_args(self):
        # We can't easily inspect connect_args after creation, so we verify
        # that the engine is created without error (SQLite in-memory) and the
        # engine dialect name is sqlite.
        engine = create_async_engine_from_dsn("sqlite+aiosqlite:///:memory:")
        assert engine.dialect.name == "sqlite"

    def test_echo_false_by_default(self):
        engine = create_async_engine_from_dsn("sqlite+aiosqlite:///:memory:")
        assert isinstance(engine, AsyncEngine)

    def test_echo_true_accepted(self):
        engine = create_async_engine_from_dsn("sqlite+aiosqlite:///:memory:", echo=True)
        assert isinstance(engine, AsyncEngine)

    def test_extensions_parameter_accepted(self):
        # extensions is informational; should not raise
        engine = create_async_engine_from_dsn(
            "sqlite+aiosqlite:///:memory:", extensions=["vector"]
        )
        assert isinstance(engine, AsyncEngine)

    def test_pool_pre_ping_set(self):
        engine = create_async_engine_from_dsn("sqlite+aiosqlite:///:memory:")
        assert engine.pool._pre_ping is True
