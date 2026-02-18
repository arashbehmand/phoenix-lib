"""Sentry SDK initialization shared across Phoenix services."""

import logging
from typing import Optional


def init_sentry(
    dsn: Optional[str],
    service_name: str,
    environment: str = "production",
    release: Optional[str] = None,
    traces_sample_rate: float = 1.0,
    profiles_sample_rate: float = 1.0,
    enabled: bool = True,
    use_asyncpg: bool = False,
    use_aiohttp: bool = True,
) -> None:
    """Initialize Sentry SDK with parameterized integrations.

    GDPR-safe defaults: ``send_default_pii=False``, ``attach_stacktrace=True``.
    ``LoggingIntegration`` is always included.

    Args:
        dsn: Sentry DSN for the project. If falsy, Sentry is skipped.
        service_name: Human-readable service tag (e.g. "job-assistant").
        environment: Deployment environment name (production, staging, development).
        release: Release version identifier.
        traces_sample_rate: Fraction of transactions to sample (0.0–1.0).
        profiles_sample_rate: Fraction of profiles to sample (0.0–1.0).
        enabled: Set to False to disable Sentry even when a DSN is provided.
        use_asyncpg: Add AsyncPGIntegration (for services using asyncpg/PostgreSQL).
        use_aiohttp: Add AioHttpIntegration (True by default for async services).
    """
    if not dsn or not enabled:
        return

    import sentry_sdk  # pylint: disable=import-outside-toplevel
    from sentry_sdk.integrations.fastapi import \
        FastApiIntegration  # pylint: disable=import-outside-toplevel
    from sentry_sdk.integrations.logging import \
        LoggingIntegration  # pylint: disable=import-outside-toplevel
    from sentry_sdk.integrations.starlette import \
        StarletteIntegration  # pylint: disable=import-outside-toplevel

    integrations = [
        FastApiIntegration(transaction_style="endpoint"),
        StarletteIntegration(transaction_style="endpoint"),
        LoggingIntegration(
            level=logging.INFO,
            event_level=logging.ERROR,
        ),
    ]

    if use_asyncpg:
        from sentry_sdk.integrations.asyncpg import \
            AsyncPGIntegration  # pylint: disable=import-outside-toplevel

        integrations.append(AsyncPGIntegration())

    if use_aiohttp:
        from sentry_sdk.integrations.aiohttp import \
            AioHttpIntegration  # pylint: disable=import-outside-toplevel

        integrations.append(AioHttpIntegration())

    sentry_sdk.init(
        dsn=dsn,
        environment=environment,
        release=release,
        traces_sample_rate=traces_sample_rate,
        profiles_sample_rate=profiles_sample_rate,
        integrations=integrations,
        send_default_pii=False,  # GDPR compliance
        attach_stacktrace=True,
    )

    sentry_sdk.set_tag("service", service_name)
