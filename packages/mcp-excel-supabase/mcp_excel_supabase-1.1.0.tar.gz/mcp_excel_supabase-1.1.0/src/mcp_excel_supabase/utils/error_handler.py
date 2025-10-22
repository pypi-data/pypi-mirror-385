"""
Error Handler Module

Provides unified error handling, recovery mechanisms, and retry logic.
Includes decorators for automatic error handling and recovery.
"""

import functools
import time
import traceback
from typing import Any, Callable, Dict, List, Optional, Type, TypeVar, cast
from enum import Enum

from .errors import MCPExcelError, NetworkError, TimeoutError as CustomTimeoutError
from .logger import get_logger

logger = get_logger(__name__)

T = TypeVar("T")
F = TypeVar("F", bound=Callable[..., Any])


class RecoveryStrategy(Enum):
    """Error recovery strategies"""

    RETRY = "retry"  # Retry the operation
    FALLBACK = "fallback"  # Use fallback value/function
    IGNORE = "ignore"  # Ignore the error and continue
    PROPAGATE = "propagate"  # Re-raise the error
    LOG_AND_CONTINUE = "log_and_continue"  # Log error and return None


class ErrorContext:
    """
    Error context information for tracking and debugging

    Attributes:
        operation: Name of the operation that failed
        error: The exception that occurred
        attempt: Current attempt number (for retries)
        timestamp: When the error occurred
        stack_trace: Full stack trace
        metadata: Additional context metadata
    """

    def __init__(
        self,
        operation: str,
        error: Exception,
        attempt: int = 1,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.operation = operation
        self.error = error
        self.attempt = attempt
        self.timestamp = time.time()
        self.stack_trace = traceback.format_exc()
        self.metadata = metadata or {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging/serialization"""
        result: Dict[str, Any] = {
            "operation": self.operation,
            "error_type": type(self.error).__name__,
            "error_message": str(self.error),
            "attempt": self.attempt,
            "timestamp": self.timestamp,
            "metadata": self.metadata,
        }

        # Add error_code if it's a MCPExcelError
        if isinstance(self.error, MCPExcelError):
            result["error_code"] = self.error.error_code
            result["error_context"] = self.error.context
            result["suggestion"] = self.error.suggestion

        return result


class ErrorHandler:
    """
    Unified error handler with recovery mechanisms

    Features:
    - Automatic retry with exponential backoff
    - Fallback value/function support
    - Error logging and tracking
    - Configurable recovery strategies
    """

    def __init__(
        self,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        backoff_factor: float = 2.0,
        retryable_errors: Optional[List[Type[Exception]]] = None,
    ):
        """
        Initialize error handler

        Args:
            max_retries: Maximum number of retry attempts
            retry_delay: Initial delay between retries (seconds)
            backoff_factor: Multiplier for exponential backoff
            retryable_errors: List of exception types that should trigger retry
        """
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.backoff_factor = backoff_factor
        self.retryable_errors = retryable_errors or [NetworkError, CustomTimeoutError]
        self.error_history: List[ErrorContext] = []

    def is_retryable(self, error: Exception) -> bool:
        """Check if an error should trigger a retry"""
        return any(isinstance(error, err_type) for err_type in self.retryable_errors)

    def handle_error(
        self,
        error: Exception,
        operation: str,
        strategy: RecoveryStrategy = RecoveryStrategy.PROPAGATE,
        fallback: Any = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """
        Handle an error with specified recovery strategy

        Args:
            error: The exception to handle
            operation: Name of the operation that failed
            strategy: Recovery strategy to use
            fallback: Fallback value (for FALLBACK strategy)
            metadata: Additional context information

        Returns:
            Result based on recovery strategy

        Raises:
            Exception: If strategy is PROPAGATE or recovery fails
        """
        # Create error context
        context = ErrorContext(operation=operation, error=error, metadata=metadata)
        self.error_history.append(context)

        # Log the error
        logger.error(
            f"Error in {operation}: {error}",
            extra={"error_context": context.to_dict()},
        )

        # Apply recovery strategy
        if strategy == RecoveryStrategy.PROPAGATE:
            raise error
        elif strategy == RecoveryStrategy.FALLBACK:
            logger.info(f"Using fallback value for {operation}")
            return fallback
        elif strategy == RecoveryStrategy.IGNORE:
            logger.warning(f"Ignoring error in {operation}")
            return None
        elif strategy == RecoveryStrategy.LOG_AND_CONTINUE:
            logger.warning(f"Logged error in {operation}, continuing execution")
            return None
        else:
            raise ValueError(f"Unknown recovery strategy: {strategy}")

    def retry_operation(
        self,
        func: Callable[..., T],
        *args: Any,
        operation_name: Optional[str] = None,
        **kwargs: Any,
    ) -> T:
        """
        Retry an operation with exponential backoff

        Args:
            func: Function to retry
            *args: Positional arguments for func
            operation_name: Name of the operation (for logging)
            **kwargs: Keyword arguments for func

        Returns:
            Result of successful function call

        Raises:
            Exception: If all retries fail
        """
        op_name = operation_name or func.__name__
        last_error: Optional[Exception] = None

        for attempt in range(1, self.max_retries + 1):
            try:
                logger.debug(f"Attempting {op_name} (attempt {attempt}/{self.max_retries})")
                result = func(*args, **kwargs)
                if attempt > 1:
                    logger.info(f"{op_name} succeeded on attempt {attempt}")
                return result
            except Exception as e:
                last_error = e
                context = ErrorContext(
                    operation=op_name,
                    error=e,
                    attempt=attempt,
                    metadata={"max_retries": self.max_retries},
                )
                self.error_history.append(context)

                if not self.is_retryable(e):
                    logger.error(f"{op_name} failed with non-retryable error: {e}")
                    raise

                if attempt < self.max_retries:
                    delay = self.retry_delay * (self.backoff_factor ** (attempt - 1))
                    logger.warning(
                        f"{op_name} failed (attempt {attempt}/{self.max_retries}): {e}. "
                        f"Retrying in {delay:.1f}s..."
                    )
                    time.sleep(delay)
                else:
                    logger.error(f"{op_name} failed after {self.max_retries} attempts: {e}")

        # All retries failed
        if last_error:
            raise last_error
        raise RuntimeError(f"{op_name} failed after {self.max_retries} attempts")

    def get_error_stats(self) -> Dict[str, Any]:
        """Get statistics about handled errors"""
        if not self.error_history:
            return {"total_errors": 0}

        error_types: Dict[str, int] = {}
        operations: Dict[str, int] = {}
        error_codes: Dict[str, int] = {}

        for ctx in self.error_history:
            # Count by error type
            error_type = type(ctx.error).__name__
            error_types[error_type] = error_types.get(error_type, 0) + 1

            # Count by operation
            operations[ctx.operation] = operations.get(ctx.operation, 0) + 1

            # Count by error code (for MCPExcelError)
            if isinstance(ctx.error, MCPExcelError):
                code = ctx.error.error_code
                error_codes[code] = error_codes.get(code, 0) + 1

        return {
            "total_errors": len(self.error_history),
            "error_types": error_types,
            "operations": operations,
            "error_codes": error_codes,
            "recent_errors": [ctx.to_dict() for ctx in self.error_history[-10:]],
        }

    def clear_history(self) -> None:
        """Clear error history"""
        self.error_history.clear()


# Global error handler instance
_global_handler: Optional[ErrorHandler] = None


def get_error_handler() -> ErrorHandler:
    """Get or create global error handler instance"""
    global _global_handler
    if _global_handler is None:
        _global_handler = ErrorHandler()
    return _global_handler


def with_retry(
    max_retries: int = 3,
    retry_delay: float = 1.0,
    backoff_factor: float = 2.0,
    retryable_errors: Optional[List[Type[Exception]]] = None,
) -> Callable[[F], F]:
    """
    Decorator for automatic retry with exponential backoff

    Args:
        max_retries: Maximum number of retry attempts
        retry_delay: Initial delay between retries (seconds)
        backoff_factor: Multiplier for exponential backoff
        retryable_errors: List of exception types that should trigger retry

    Example:
        @with_retry(max_retries=3, retry_delay=1.0)
        def upload_file(path: str) -> bool:
            # ... upload logic ...
            return True
    """

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            handler = ErrorHandler(
                max_retries=max_retries,
                retry_delay=retry_delay,
                backoff_factor=backoff_factor,
                retryable_errors=retryable_errors,
            )
            return handler.retry_operation(func, *args, **kwargs)

        return cast(F, wrapper)

    return decorator


def with_fallback(fallback_value: Any) -> Callable[[F], F]:
    """
    Decorator to return fallback value on error

    Args:
        fallback_value: Value to return if function raises an exception

    Example:
        @with_fallback(fallback_value=[])
        def get_items() -> List[str]:
            # ... may raise exception ...
            return items
    """

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                handler = get_error_handler()
                return handler.handle_error(
                    error=e,
                    operation=func.__name__,
                    strategy=RecoveryStrategy.FALLBACK,
                    fallback=fallback_value,
                )

        return cast(F, wrapper)

    return decorator
