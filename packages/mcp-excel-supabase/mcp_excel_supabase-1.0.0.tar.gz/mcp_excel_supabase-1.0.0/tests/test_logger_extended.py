"""
Tests for extended logger functionality (structured logging and error tracking)
"""

import pytest
import json
import logging
from pathlib import Path

from src.mcp_excel_supabase.utils.logger import (
    JSONFormatter,
    StructuredLogger,
    ErrorTracker,
    structured_logger,
    error_tracker,
)


class TestJSONFormatter:
    """Test JSONFormatter class"""

    def test_json_formatter_basic(self):
        """Test basic JSON formatting"""
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        result = formatter.format(record)
        data = json.loads(result)

        assert data["level"] == "INFO"
        assert data["logger"] == "test"
        assert data["message"] == "Test message"
        assert data["module"] == "test"
        assert data["line"] == 10

    def test_json_formatter_with_exception(self):
        """Test JSON formatting with exception"""
        formatter = JSONFormatter()

        try:
            raise ValueError("Test error")
        except ValueError:
            record = logging.LogRecord(
                name="test",
                level=logging.ERROR,
                pathname="test.py",
                lineno=10,
                msg="Error occurred",
                args=(),
                exc_info=True,
            )
            # Manually set exc_info
            import sys

            record.exc_info = sys.exc_info()

            result = formatter.format(record)
            data = json.loads(result)

            assert "exception" in data
            assert data["exception"]["type"] == "ValueError"
            assert "Test error" in data["exception"]["message"]
            assert isinstance(data["exception"]["traceback"], list)

    def test_json_formatter_with_extra_fields(self):
        """Test JSON formatting with extra fields"""
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        # Add extra fields
        record.user_id = "user123"
        record.request_id = "req456"

        result = formatter.format(record)
        data = json.loads(result)

        assert data["user_id"] == "user123"
        assert data["request_id"] == "req456"


class TestStructuredLogger:
    """Test StructuredLogger class"""

    def test_structured_logger_creation(self):
        """Test creating structured logger"""
        logger = StructuredLogger()

        assert logger.logger is not None
        assert logger.logger.name == "structured"

    def test_structured_logger_log(self):
        """Test logging with structured logger"""
        logger = StructuredLogger()

        # Should not raise any exceptions
        logger.log("INFO", "Test message", user_id="user123", action="test")

    def test_structured_logger_debug(self):
        """Test debug level logging"""
        logger = StructuredLogger()

        logger.debug("Debug message", key="value")

        # Verify log file exists
        log_file = Path("logs/structured.jsonl")
        assert log_file.exists()

    def test_structured_logger_info(self):
        """Test info level logging"""
        logger = StructuredLogger()

        logger.info("Info message", key="value")

        # Verify log file exists
        log_file = Path("logs/structured.jsonl")
        assert log_file.exists()

    def test_structured_logger_warning(self):
        """Test warning level logging"""
        logger = StructuredLogger()

        logger.warning("Warning message", key="value")

        # Verify log file exists
        log_file = Path("logs/structured.jsonl")
        assert log_file.exists()

    def test_structured_logger_error(self):
        """Test error level logging"""
        logger = StructuredLogger()

        logger.error("Error message", key="value")

        # Verify log file exists
        log_file = Path("logs/structured.jsonl")
        assert log_file.exists()

    def test_structured_logger_critical(self):
        """Test critical level logging"""
        logger = StructuredLogger()

        logger.critical("Critical message", key="value")

        # Verify log file exists
        log_file = Path("logs/structured.jsonl")
        assert log_file.exists()

    def test_structured_logger_with_context(self):
        """Test logging with context fields"""
        logger = StructuredLogger()

        logger.info(
            "Operation completed",
            operation="test_op",
            duration_ms=123.45,
            success=True,
        )

        # Verify log file exists
        log_file = Path("logs/structured.jsonl")
        assert log_file.exists()


class TestErrorTracker:
    """Test ErrorTracker class"""

    def test_error_tracker_creation(self):
        """Test creating error tracker"""
        tracker = ErrorTracker()

        assert tracker.logger is not None
        assert len(tracker.error_counts) == 0
        assert len(tracker.error_history) == 0

    def test_track_error_basic(self):
        """Test tracking a basic error"""
        tracker = ErrorTracker()

        error = ValueError("Test error")
        tracker.track_error(error, "test_operation")

        assert tracker.error_counts["ValueError:test_operation"] == 1
        assert len(tracker.error_history) == 1

    def test_track_multiple_errors(self):
        """Test tracking multiple errors"""
        tracker = ErrorTracker()

        for i in range(5):
            error = ValueError(f"Error {i}")
            tracker.track_error(error, "test_operation")

        assert tracker.error_counts["ValueError:test_operation"] == 5
        assert len(tracker.error_history) == 5

    def test_track_different_error_types(self):
        """Test tracking different error types"""
        tracker = ErrorTracker()

        tracker.track_error(ValueError("error1"), "op1")
        tracker.track_error(TypeError("error2"), "op1")
        tracker.track_error(ValueError("error3"), "op2")

        assert tracker.error_counts["ValueError:op1"] == 1
        assert tracker.error_counts["TypeError:op1"] == 1
        assert tracker.error_counts["ValueError:op2"] == 1

    def test_track_error_with_context(self):
        """Test tracking error with context"""
        tracker = ErrorTracker()

        error = ValueError("Test error")
        context = {"file": "test.xlsx", "line": 10}

        tracker.track_error(error, "test_operation", context)

        assert len(tracker.error_history) == 1
        assert tracker.error_history[0]["context"] == context

    def test_get_error_stats(self):
        """Test getting error statistics"""
        tracker = ErrorTracker()

        # Track some errors
        tracker.track_error(ValueError("error1"), "op1")
        tracker.track_error(ValueError("error2"), "op1")
        tracker.track_error(TypeError("error3"), "op2")

        stats = tracker.get_error_stats()

        assert stats["total_errors"] == 3
        assert stats["unique_errors"] == 2
        assert stats["error_counts"]["ValueError:op1"] == 2
        assert stats["error_counts"]["TypeError:op2"] == 1
        assert len(stats["recent_errors"]) == 3

    def test_get_top_errors(self):
        """Test getting top errors"""
        tracker = ErrorTracker()

        # Track errors with different frequencies
        for _ in range(5):
            tracker.track_error(ValueError("error"), "op1")
        for _ in range(3):
            tracker.track_error(TypeError("error"), "op2")
        for _ in range(1):
            tracker.track_error(KeyError("error"), "op3")

        top_errors = tracker.get_top_errors(limit=2)

        assert len(top_errors) == 2
        assert top_errors[0][0] == "ValueError:op1"
        assert top_errors[0][1] == 5
        assert top_errors[1][0] == "TypeError:op2"
        assert top_errors[1][1] == 3

    def test_clear_stats(self):
        """Test clearing error statistics"""
        tracker = ErrorTracker()

        tracker.track_error(ValueError("error"), "op")

        assert len(tracker.error_counts) > 0
        assert len(tracker.error_history) > 0

        tracker.clear_stats()

        assert len(tracker.error_counts) == 0
        assert len(tracker.error_history) == 0

    def test_history_size_limit(self):
        """Test that history size is limited"""
        tracker = ErrorTracker()
        tracker.max_history_size = 10

        # Track more errors than max size
        for i in range(20):
            tracker.track_error(ValueError(f"error{i}"), "op")

        # Should only keep last 10
        assert len(tracker.error_history) == 10

        # But counts should still be accurate
        assert tracker.error_counts["ValueError:op"] == 20


class TestGlobalLoggerInstances:
    """Test global logger instances"""

    def test_structured_logger_instance(self):
        """Test global structured logger instance"""
        assert structured_logger is not None
        assert isinstance(structured_logger, StructuredLogger)

    def test_error_tracker_instance(self):
        """Test global error tracker instance"""
        assert error_tracker is not None
        assert isinstance(error_tracker, ErrorTracker)

    def test_structured_logger_usage(self):
        """Test using global structured logger"""
        # Should not raise any exceptions
        structured_logger.info("Test message", key="value")

    def test_error_tracker_usage(self):
        """Test using global error tracker"""
        error = ValueError("Test error")

        # Should not raise any exceptions
        error_tracker.track_error(error, "test_operation")


class TestLogFileCreation:
    """Test that log files are created correctly"""

    def test_structured_log_file_exists(self):
        """Test that structured log file is created"""
        logger = StructuredLogger()
        logger.info("Test message")

        log_file = Path("logs/structured.jsonl")
        assert log_file.exists()

    def test_error_tracking_file_exists(self):
        """Test that error tracking file is created"""
        tracker = ErrorTracker()
        tracker.track_error(ValueError("Test"), "op")

        log_file = Path("logs/error_tracking.jsonl")
        assert log_file.exists()

    def test_structured_log_format(self):
        """Test that structured log is in JSON format"""
        logger = StructuredLogger()
        logger.info("Test message", test_key="test_value")

        log_file = Path("logs/structured.jsonl")
        assert log_file.exists()

        # Read last line and verify it's valid JSON
        with open(log_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
            if lines:
                last_line = lines[-1]
                data = json.loads(last_line)
                assert "message" in data
                assert "timestamp" in data
                assert "level" in data

    def test_error_tracking_log_format(self):
        """Test that error tracking log is in JSON format"""
        tracker = ErrorTracker()
        tracker.track_error(ValueError("Test error"), "test_op")

        log_file = Path("logs/error_tracking.jsonl")
        assert log_file.exists()

        # Read last line and verify it's valid JSON
        with open(log_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
            if lines:
                last_line = lines[-1]
                data = json.loads(last_line)
                assert "message" in data
                assert "timestamp" in data
                assert "level" in data

