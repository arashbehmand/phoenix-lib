"""Tests for phoenix_lib.observability.sentry."""

from unittest.mock import patch

import pytest

from phoenix_lib.observability.sentry import init_sentry


class TestInitSentry:
    def test_no_dsn_does_not_init(self):
        with patch("sentry_sdk.init") as mock_init:
            init_sentry(dsn=None, service_name="test-service")
            mock_init.assert_not_called()

    def test_empty_dsn_does_not_init(self):
        with patch("sentry_sdk.init") as mock_init:
            init_sentry(dsn="", service_name="test-service")
            mock_init.assert_not_called()

    def test_disabled_does_not_init(self):
        with patch("sentry_sdk.init") as mock_init:
            init_sentry(
                dsn="https://key@sentry.io/123",
                service_name="test-service",
                enabled=False,
            )
            mock_init.assert_not_called()

    def test_valid_dsn_calls_init(self):
        with (
            patch("sentry_sdk.init") as mock_init,
            patch("sentry_sdk.set_tag"),
        ):
            init_sentry(dsn="https://key@sentry.io/123", service_name="test-service")
            mock_init.assert_called_once()

    def test_sets_service_tag(self):
        with (
            patch("sentry_sdk.init"),
            patch("sentry_sdk.set_tag") as mock_tag,
        ):
            init_sentry(dsn="https://key@sentry.io/123", service_name="my-service")
            mock_tag.assert_called_once_with("service", "my-service")

    def test_passes_environment(self):
        with (
            patch("sentry_sdk.init") as mock_init,
            patch("sentry_sdk.set_tag"),
        ):
            init_sentry(
                dsn="https://key@sentry.io/123",
                service_name="svc",
                environment="staging",
            )
            call_kwargs = mock_init.call_args.kwargs
            assert call_kwargs["environment"] == "staging"

    def test_passes_release(self):
        with (
            patch("sentry_sdk.init") as mock_init,
            patch("sentry_sdk.set_tag"),
        ):
            init_sentry(
                dsn="https://key@sentry.io/123",
                service_name="svc",
                release="v1.2.3",
            )
            call_kwargs = mock_init.call_args.kwargs
            assert call_kwargs["release"] == "v1.2.3"

    def test_gdpr_settings_applied(self):
        with (
            patch("sentry_sdk.init") as mock_init,
            patch("sentry_sdk.set_tag"),
        ):
            init_sentry(dsn="https://key@sentry.io/123", service_name="svc")
            call_kwargs = mock_init.call_args.kwargs
            assert call_kwargs["send_default_pii"] is False
            assert call_kwargs["attach_stacktrace"] is True

    def test_sample_rates_passed(self):
        with (
            patch("sentry_sdk.init") as mock_init,
            patch("sentry_sdk.set_tag"),
        ):
            init_sentry(
                dsn="https://key@sentry.io/123",
                service_name="svc",
                traces_sample_rate=0.5,
                profiles_sample_rate=0.25,
            )
            call_kwargs = mock_init.call_args.kwargs
            assert call_kwargs["traces_sample_rate"] == 0.5
            assert call_kwargs["profiles_sample_rate"] == 0.25

    def test_default_integrations_include_fastapi_and_logging(self):
        with (
            patch("sentry_sdk.init") as mock_init,
            patch("sentry_sdk.set_tag"),
        ):
            init_sentry(
                dsn="https://key@sentry.io/123", service_name="svc", use_aiohttp=False
            )
            integrations = mock_init.call_args.kwargs["integrations"]
            class_names = [type(i).__name__ for i in integrations]
            assert "FastApiIntegration" in class_names
            assert "StarletteIntegration" in class_names
            assert "LoggingIntegration" in class_names

    def test_use_aiohttp_adds_aiohttp_integration(self):
        with (
            patch("sentry_sdk.init") as mock_init,
            patch("sentry_sdk.set_tag"),
        ):
            init_sentry(
                dsn="https://key@sentry.io/123", service_name="svc", use_aiohttp=True
            )
            integrations = mock_init.call_args.kwargs["integrations"]
            class_names = [type(i).__name__ for i in integrations]
            assert "AioHttpIntegration" in class_names

    def test_use_aiohttp_false_omits_aiohttp(self):
        with (
            patch("sentry_sdk.init") as mock_init,
            patch("sentry_sdk.set_tag"),
        ):
            init_sentry(
                dsn="https://key@sentry.io/123", service_name="svc", use_aiohttp=False
            )
            integrations = mock_init.call_args.kwargs["integrations"]
            class_names = [type(i).__name__ for i in integrations]
            assert "AioHttpIntegration" not in class_names

    @pytest.mark.skipif(
        not __import__("importlib").util.find_spec("asyncpg"),
        reason="asyncpg not installed",
    )
    def test_use_asyncpg_adds_asyncpg_integration(self):
        with (
            patch("sentry_sdk.init") as mock_init,
            patch("sentry_sdk.set_tag"),
        ):
            init_sentry(
                dsn="https://key@sentry.io/123",
                service_name="svc",
                use_asyncpg=True,
                use_aiohttp=False,
            )
            integrations = mock_init.call_args.kwargs["integrations"]
            class_names = [type(i).__name__ for i in integrations]
            assert "AsyncPGIntegration" in class_names

    def test_use_asyncpg_false_omits_asyncpg(self):
        with (
            patch("sentry_sdk.init") as mock_init,
            patch("sentry_sdk.set_tag"),
        ):
            init_sentry(
                dsn="https://key@sentry.io/123",
                service_name="svc",
                use_asyncpg=False,
                use_aiohttp=False,
            )
            integrations = mock_init.call_args.kwargs["integrations"]
            class_names = [type(i).__name__ for i in integrations]
            assert "AsyncPGIntegration" not in class_names
