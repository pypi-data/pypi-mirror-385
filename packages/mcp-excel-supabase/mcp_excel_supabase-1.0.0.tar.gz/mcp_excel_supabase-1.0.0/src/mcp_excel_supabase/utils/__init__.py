"""
Utility modules

This module provides shared utilities for:
- Error handling and custom exceptions
- Logging configuration
- Input validation
- Caching mechanisms
- Concurrency and parallel processing
- Common helper functions
"""

from .cache import (
    LRUCache,
    CacheManager,
    get_cache_manager,
    lru_cache,
    parse_cache,
    format_cache,
)
from .concurrency import (
    ThreadPoolManager,
    ConcurrentExecutor,
    ProgressTracker,
    get_global_pool,
    shutdown_global_pool,
)
from .error_handler import (
    ErrorHandler,
    ErrorContext,
    RecoveryStrategy,
    get_error_handler,
    with_retry,
    with_fallback,
)
from .monitor import (
    PerformanceMonitor,
    ErrorRateMonitor,
    ResourceMonitor,
    MetricsExporter,
    get_performance_monitor,
    get_error_rate_monitor,
    get_resource_monitor,
    get_metrics_exporter,
    monitor_performance,
)

__all__ = [
    # Cache
    "LRUCache",
    "CacheManager",
    "get_cache_manager",
    "lru_cache",
    "parse_cache",
    "format_cache",
    # Concurrency
    "ThreadPoolManager",
    "ConcurrentExecutor",
    "ProgressTracker",
    "get_global_pool",
    "shutdown_global_pool",
    # Error Handler
    "ErrorHandler",
    "ErrorContext",
    "RecoveryStrategy",
    "get_error_handler",
    "with_retry",
    "with_fallback",
    # Monitor
    "PerformanceMonitor",
    "ErrorRateMonitor",
    "ResourceMonitor",
    "MetricsExporter",
    "get_performance_monitor",
    "get_error_rate_monitor",
    "get_resource_monitor",
    "get_metrics_exporter",
    "monitor_performance",
]
