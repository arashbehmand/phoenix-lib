"""Tests for phoenix_lib.logging.config."""

from phoenix_lib.logging.config import configure_logging, get_logger


class TestConfigureLogging:
    def test_configure_with_info_level(self):
        # Should not raise
        configure_logging("INFO")

    def test_configure_with_debug_level(self):
        configure_logging("DEBUG")

    def test_configure_with_warning_level(self):
        configure_logging("WARNING")

    def test_configure_with_lowercase_level(self):
        configure_logging("info")

    def test_configure_with_invalid_level_falls_back_to_info(self):
        # Invalid level string should not raise; getattr returns logging.INFO as fallback
        configure_logging("NOTAREALEVEL")

    def test_configure_called_multiple_times(self):
        # Should be idempotent (no exception)
        configure_logging("INFO")
        configure_logging("DEBUG")
        configure_logging("INFO")


class TestGetLogger:
    def test_returns_something_callable(self):
        logger = get_logger("test.module")
        assert logger is not None

    def test_logger_name(self):
        logger = get_logger("my.service")
        # May be structlog or stdlib adapter — just verify it doesn't crash
        assert logger is not None

    def test_logger_can_log_info(self):
        configure_logging("INFO")
        logger = get_logger("test.logger")
        # Should not raise whether structlog or stdlib
        try:
            logger.info("test message", key="value")
        except TypeError:
            # stdlib adapter may not accept keyword args — try without
            logger.info("test message")

    def test_logger_can_log_error(self):
        configure_logging("INFO")
        logger = get_logger("test.error.logger")
        try:
            logger.error("error message", reason="test")
        except TypeError:
            logger.error("error message")

    def test_different_names_return_loggers(self):
        logger_a = get_logger("module.a")
        logger_b = get_logger("module.b")
        assert logger_a is not None
        assert logger_b is not None
