"""Shared async database engine factory for Phoenix services."""

from typing import List, Optional, Tuple

from sqlalchemy.engine import URL
from sqlalchemy.engine.url import make_url
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine


def detect_dialect(dsn: str) -> Tuple[str, URL]:
    """Parse a DSN string and return a normalised dialect name plus the parsed URL.

    Returns:
        Tuple of (dialect, URL) where dialect is one of "postgresql", "mysql",
        "sqlite", or the raw drivername prefix for unknown drivers.
    """
    url = make_url(dsn)
    driver = (url.drivername or "").lower()
    if driver.startswith("postgres"):
        return "postgresql", url
    if driver.startswith("mysql"):
        return "mysql", url
    if driver.startswith("sqlite"):
        return "sqlite", url
    return driver, url


def create_async_engine_from_dsn(
    dsn: str,
    echo: bool = False,
    extensions: Optional[List[str]] = None,
) -> AsyncEngine:
    """Create an ``AsyncEngine`` from a DSN string.

    Applies dialect-specific ``connect_args`` automatically:
    - SQLite: ``check_same_thread=False``
    - PostgreSQL with ``extensions=["vector"]``: pgvector is enabled after
      first connection (caller is responsible for running the DDL).

    Args:
        dsn: Database DSN / URL string.
        echo: If True, SQL statements are logged (useful for debugging).
        extensions: Optional list of PostgreSQL extensions to note (informational
                    for callers; DDL must be executed separately).

    Returns:
        Configured ``AsyncEngine`` instance.
    """
    dialect, url = detect_dialect(dsn if isinstance(dsn, str) else str(dsn))

    connect_args = {}
    if dialect == "sqlite" or (url.drivername or "").startswith("sqlite"):
        connect_args = {"check_same_thread": False}

    engine = create_async_engine(
        str(url),
        echo=echo,
        pool_pre_ping=True,
        connect_args=connect_args,
    )
    return engine
