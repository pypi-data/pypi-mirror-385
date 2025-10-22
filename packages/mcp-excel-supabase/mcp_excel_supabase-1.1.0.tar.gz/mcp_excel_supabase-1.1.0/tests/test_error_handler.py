"""
Tests for error_handler module
"""

import pytest
import time
from typing import Any

from src.mcp_excel_supabase.utils.error_handler import (
    ErrorHandler,
    ErrorContext,
    RecoveryStrategy,
    get_error_handler,
    with_retry,
    with_fallback,
)
from src.mcp_excel_supabase.utils.errors import (
    NetworkError,
    TimeoutError as CustomTimeoutError,
    FileOperationError,
)


class TestErrorContext:
    """Test ErrorContext class"""

    def test_error_context_creation(self):
        """Test creating error context"""
        error = ValueError("test error")
        context = ErrorContext(
            operation="test_op",
            error=error,
            attempt=1,
            metadata={"key": "value"},
        )

        assert context.operation == "test_op"
        assert context.error == error
        assert context.attempt == 1
        assert context.metadata == {"key": "value"}
        assert context.timestamp > 0
        assert len(context.stack_trace) > 0

    def test_error_context_to_dict(self):
        """Test converting error context to dict"""
        error = ValueError("test error")
        context = ErrorContext(
            operation="test_op",
            error=error,
            metadata={"key": "value"},
        )

        result = context.to_dict()

        assert result["operation"] == "test_op"
        assert result["error_type"] == "ValueError"
        assert result["error_message"] == "test error"
        assert result["attempt"] == 1
        assert result["metadata"] == {"key": "value"}

    def test_error_context_with_mcp_error(self):
        """Test error context with MCPExcelError"""
        error = FileOperationError(
            error_code="E101",
            message="File not found",
            context={"file": "test.xlsx"},
        )
        context = ErrorContext(operation="read_file", error=error)

        result = context.to_dict()

        assert result["error_code"] == "E101"
        assert result["error_context"] == {"file": "test.xlsx"}
        assert "suggestion" in result


class TestErrorHandler:
    """Test ErrorHandler class"""

    def test_error_handler_creation(self):
        """Test creating error handler"""
        handler = ErrorHandler(
            max_retries=5,
            retry_delay=2.0,
            backoff_factor=3.0,
        )

        assert handler.max_retries == 5
        assert handler.retry_delay == 2.0
        assert handler.backoff_factor == 3.0
        assert len(handler.error_history) == 0

    def test_is_retryable(self):
        """Test checking if error is retryable"""
        handler = ErrorHandler()

        # Retryable errors
        assert handler.is_retryable(NetworkError("E501", "Network error"))
        assert handler.is_retryable(CustomTimeoutError("test", 10))

        # Non-retryable errors
        assert not handler.is_retryable(ValueError("test"))
        assert not handler.is_retryable(FileOperationError("E101", "File error"))

    def test_handle_error_propagate(self):
        """Test error handling with PROPAGATE strategy"""
        handler = ErrorHandler()
        error = ValueError("test error")

        with pytest.raises(ValueError, match="test error"):
            handler.handle_error(
                error=error,
                operation="test_op",
                strategy=RecoveryStrategy.PROPAGATE,
            )

        assert len(handler.error_history) == 1

    def test_handle_error_fallback(self):
        """Test error handling with FALLBACK strategy"""
        handler = ErrorHandler()
        error = ValueError("test error")

        result = handler.handle_error(
            error=error,
            operation="test_op",
            strategy=RecoveryStrategy.FALLBACK,
            fallback="default_value",
        )

        assert result == "default_value"
        assert len(handler.error_history) == 1

    def test_handle_error_ignore(self):
        """Test error handling with IGNORE strategy"""
        handler = ErrorHandler()
        error = ValueError("test error")

        result = handler.handle_error(
            error=error,
            operation="test_op",
            strategy=RecoveryStrategy.IGNORE,
        )

        assert result is None
        assert len(handler.error_history) == 1

    def test_handle_error_log_and_continue(self):
        """Test error handling with LOG_AND_CONTINUE strategy"""
        handler = ErrorHandler()
        error = ValueError("test error")

        result = handler.handle_error(
            error=error,
            operation="test_op",
            strategy=RecoveryStrategy.LOG_AND_CONTINUE,
        )

        assert result is None
        assert len(handler.error_history) == 1

    def test_retry_operation_success(self):
        """Test successful retry operation"""
        handler = ErrorHandler(max_retries=3)
        call_count = 0

        def test_func() -> str:
            nonlocal call_count
            call_count += 1
            return "success"

        result = handler.retry_operation(test_func)

        assert result == "success"
        assert call_count == 1

    def test_retry_operation_success_after_failures(self):
        """Test retry operation succeeds after failures"""
        handler = ErrorHandler(max_retries=3, retry_delay=0.1)
        call_count = 0

        def test_func() -> str:
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise NetworkError("E501", "Network error")
            return "success"

        result = handler.retry_operation(test_func)

        assert result == "success"
        assert call_count == 3

    def test_retry_operation_all_failures(self):
        """Test retry operation fails after all attempts"""
        handler = ErrorHandler(max_retries=3, retry_delay=0.1)
        call_count = 0

        def test_func() -> str:
            nonlocal call_count
            call_count += 1
            raise NetworkError("E501", "Network error")

        with pytest.raises(NetworkError):
            handler.retry_operation(test_func)

        assert call_count == 3

    def test_retry_operation_non_retryable_error(self):
        """Test retry operation with non-retryable error"""
        handler = ErrorHandler(max_retries=3)
        call_count = 0

        def test_func() -> str:
            nonlocal call_count
            call_count += 1
            raise ValueError("Non-retryable error")

        with pytest.raises(ValueError):
            handler.retry_operation(test_func)

        assert call_count == 1  # Should not retry

    def test_get_error_stats(self):
        """Test getting error statistics"""
        handler = ErrorHandler()

        # No errors yet
        stats = handler.get_error_stats()
        assert stats["total_errors"] == 0

        # Add some errors
        handler.handle_error(
            ValueError("error1"),
            "op1",
            RecoveryStrategy.IGNORE,
        )
        handler.handle_error(
            ValueError("error2"),
            "op1",
            RecoveryStrategy.IGNORE,
        )
        handler.handle_error(
            TypeError("error3"),
            "op2",
            RecoveryStrategy.IGNORE,
        )

        stats = handler.get_error_stats()
        assert stats["total_errors"] == 3
        assert stats["error_types"]["ValueError"] == 2
        assert stats["error_types"]["TypeError"] == 1
        assert stats["operations"]["op1"] == 2
        assert stats["operations"]["op2"] == 1

    def test_clear_history(self):
        """Test clearing error history"""
        handler = ErrorHandler()

        handler.handle_error(
            ValueError("error"),
            "op",
            RecoveryStrategy.IGNORE,
        )

        assert len(handler.error_history) == 1

        handler.clear_history()

        assert len(handler.error_history) == 0


class TestGlobalErrorHandler:
    """Test global error handler"""

    def test_get_error_handler(self):
        """Test getting global error handler"""
        handler1 = get_error_handler()
        handler2 = get_error_handler()

        # Should return the same instance
        assert handler1 is handler2


class TestWithRetryDecorator:
    """Test with_retry decorator"""

    def test_with_retry_success(self):
        """Test decorator with successful function"""
        call_count = 0

        @with_retry(max_retries=3)
        def test_func() -> str:
            nonlocal call_count
            call_count += 1
            return "success"

        result = test_func()

        assert result == "success"
        assert call_count == 1

    def test_with_retry_success_after_failures(self):
        """Test decorator succeeds after failures"""
        call_count = 0

        @with_retry(max_retries=3, retry_delay=0.1)
        def test_func() -> str:
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise NetworkError("E501", "Network error")
            return "success"

        result = test_func()

        assert result == "success"
        assert call_count == 3

    def test_with_retry_all_failures(self):
        """Test decorator fails after all attempts"""
        call_count = 0

        @with_retry(max_retries=3, retry_delay=0.1)
        def test_func() -> str:
            nonlocal call_count
            call_count += 1
            raise NetworkError("E501", "Network error")

        with pytest.raises(NetworkError):
            test_func()

        assert call_count == 3


class TestWithFallbackDecorator:
    """Test with_fallback decorator"""

    def test_with_fallback_success(self):
        """Test decorator with successful function"""

        @with_fallback(fallback_value="default")
        def test_func() -> str:
            return "success"

        result = test_func()

        assert result == "success"

    def test_with_fallback_on_error(self):
        """Test decorator returns fallback on error"""

        @with_fallback(fallback_value="default")
        def test_func() -> str:
            raise ValueError("error")

        result = test_func()

        assert result == "default"

    def test_with_fallback_list(self):
        """Test decorator with list fallback"""

        @with_fallback(fallback_value=[])
        def test_func() -> list:
            raise ValueError("error")

        result = test_func()

        assert result == []
        assert isinstance(result, list)

