"""
Monitoring Module

Provides comprehensive monitoring capabilities:
- Performance monitoring (response time, throughput)
- Error rate monitoring (error statistics, trends)
- Resource monitoring (CPU, memory, disk)
- Metrics export (Prometheus format)
"""

import functools
import psutil
import time
from collections import defaultdict, deque
from datetime import datetime, timedelta
from typing import Any, Callable, Deque, Dict, List, Optional, TypeVar, cast
from dataclasses import dataclass, field

from .logger import get_logger, performance_logger

logger = get_logger(__name__)

F = TypeVar("F", bound=Callable[..., Any])


@dataclass
class PerformanceMetric:
    """Performance metric data"""

    operation: str
    duration_ms: float
    timestamp: datetime
    success: bool
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ResourceSnapshot:
    """Resource usage snapshot"""

    timestamp: datetime
    cpu_percent: float
    memory_mb: float
    memory_percent: float
    disk_usage_percent: float


class PerformanceMonitor:
    """
    Performance monitoring system

    Tracks operation performance metrics including:
    - Response times
    - Throughput
    - Success/failure rates
    - Percentile statistics
    """

    def __init__(self, window_size: int = 1000):
        """
        Initialize performance monitor

        Args:
            window_size: Number of recent metrics to keep in memory
        """
        self.window_size = window_size
        self.metrics: Dict[str, Deque[PerformanceMetric]] = defaultdict(
            lambda: deque(maxlen=window_size)
        )
        self.operation_counts: Dict[str, int] = defaultdict(int)
        self.success_counts: Dict[str, int] = defaultdict(int)
        self.failure_counts: Dict[str, int] = defaultdict(int)

    def record_metric(
        self,
        operation: str,
        duration_ms: float,
        success: bool = True,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Record a performance metric

        Args:
            operation: Name of the operation
            duration_ms: Duration in milliseconds
            success: Whether the operation succeeded
            metadata: Additional metadata
        """
        metric = PerformanceMetric(
            operation=operation,
            duration_ms=duration_ms,
            timestamp=datetime.now(),
            success=success,
            metadata=metadata or {},
        )

        self.metrics[operation].append(metric)
        self.operation_counts[operation] += 1

        if success:
            self.success_counts[operation] += 1
        else:
            self.failure_counts[operation] += 1

        # Log to performance logger (only log basic info, not metadata)
        performance_logger.log_performance(
            operation=operation,
            duration_ms=duration_ms,
            success=success,
        )

    def get_stats(self, operation: str) -> Dict[str, Any]:
        """
        Get statistics for an operation

        Args:
            operation: Name of the operation

        Returns:
            Dictionary with statistics
        """
        if operation not in self.metrics or not self.metrics[operation]:
            return {"operation": operation, "count": 0}

        metrics_list = list(self.metrics[operation])
        durations = [m.duration_ms for m in metrics_list]
        durations.sort()

        count = len(durations)
        total_count = self.operation_counts[operation]
        success_count = self.success_counts[operation]
        failure_count = self.failure_counts[operation]

        return {
            "operation": operation,
            "count": count,
            "total_count": total_count,
            "success_count": success_count,
            "failure_count": failure_count,
            "success_rate": success_count / total_count if total_count > 0 else 0,
            "avg_duration_ms": sum(durations) / count,
            "min_duration_ms": durations[0],
            "max_duration_ms": durations[-1],
            "p50_duration_ms": durations[count // 2],
            "p95_duration_ms": durations[int(count * 0.95)],
            "p99_duration_ms": durations[int(count * 0.99)],
        }

    def get_all_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics for all operations"""
        return {op: self.get_stats(op) for op in self.metrics.keys()}

    def clear_metrics(self, operation: Optional[str] = None) -> None:
        """
        Clear metrics

        Args:
            operation: Specific operation to clear, or None to clear all
        """
        if operation:
            if operation in self.metrics:
                self.metrics[operation].clear()
                self.operation_counts[operation] = 0
                self.success_counts[operation] = 0
                self.failure_counts[operation] = 0
        else:
            self.metrics.clear()
            self.operation_counts.clear()
            self.success_counts.clear()
            self.failure_counts.clear()


class ErrorRateMonitor:
    """
    Error rate monitoring system

    Tracks error rates and trends over time
    """

    def __init__(self, window_minutes: int = 60):
        """
        Initialize error rate monitor

        Args:
            window_minutes: Time window for rate calculation (minutes)
        """
        self.window_minutes = window_minutes
        self.error_timestamps: Dict[str, Deque[datetime]] = defaultdict(lambda: deque())

    def record_error(self, error_type: str) -> None:
        """
        Record an error occurrence

        Args:
            error_type: Type/category of the error
        """
        self.error_timestamps[error_type].append(datetime.now())
        self._cleanup_old_errors(error_type)

    def _cleanup_old_errors(self, error_type: str) -> None:
        """Remove errors outside the time window"""
        cutoff_time = datetime.now() - timedelta(minutes=self.window_minutes)
        timestamps = self.error_timestamps[error_type]

        while timestamps and timestamps[0] < cutoff_time:
            timestamps.popleft()

    def get_error_rate(self, error_type: str) -> float:
        """
        Get error rate (errors per minute)

        Args:
            error_type: Type/category of the error

        Returns:
            Error rate (errors per minute)
        """
        self._cleanup_old_errors(error_type)
        count = len(self.error_timestamps[error_type])
        return count / self.window_minutes

    def get_all_error_rates(self) -> Dict[str, float]:
        """Get error rates for all error types"""
        return {
            error_type: self.get_error_rate(error_type)
            for error_type in self.error_timestamps.keys()
        }

    def get_total_errors(self, error_type: Optional[str] = None) -> int:
        """
        Get total error count in the time window

        Args:
            error_type: Specific error type, or None for all errors

        Returns:
            Total error count
        """
        if error_type:
            self._cleanup_old_errors(error_type)
            return len(self.error_timestamps[error_type])
        else:
            total = 0
            for et in self.error_timestamps.keys():
                self._cleanup_old_errors(et)
                total += len(self.error_timestamps[et])
            return total


class ResourceMonitor:
    """
    System resource monitoring

    Tracks CPU, memory, and disk usage
    """

    def __init__(self, history_size: int = 100):
        """
        Initialize resource monitor

        Args:
            history_size: Number of snapshots to keep in history
        """
        self.history_size = history_size
        self.snapshots: Deque[ResourceSnapshot] = deque(maxlen=history_size)
        self.process = psutil.Process()

    def take_snapshot(self) -> ResourceSnapshot:
        """
        Take a resource usage snapshot

        Returns:
            ResourceSnapshot with current usage
        """
        snapshot = ResourceSnapshot(
            timestamp=datetime.now(),
            cpu_percent=self.process.cpu_percent(interval=0.1),
            memory_mb=self.process.memory_info().rss / 1024 / 1024,
            memory_percent=self.process.memory_percent(),
            disk_usage_percent=psutil.disk_usage("/").percent,
        )

        self.snapshots.append(snapshot)
        return snapshot

    def get_current_usage(self) -> Dict[str, Any]:
        """Get current resource usage"""
        snapshot = self.take_snapshot()
        return {
            "timestamp": snapshot.timestamp.isoformat(),
            "cpu_percent": snapshot.cpu_percent,
            "memory_mb": snapshot.memory_mb,
            "memory_percent": snapshot.memory_percent,
            "disk_usage_percent": snapshot.disk_usage_percent,
        }

    def get_average_usage(self, minutes: int = 5) -> Dict[str, Any]:
        """
        Get average resource usage over time period

        Args:
            minutes: Time period in minutes

        Returns:
            Average usage statistics
        """
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        recent_snapshots = [s for s in self.snapshots if s.timestamp >= cutoff_time]

        if not recent_snapshots:
            return self.get_current_usage()

        return {
            "period_minutes": minutes,
            "avg_cpu_percent": sum(s.cpu_percent for s in recent_snapshots) / len(recent_snapshots),
            "avg_memory_mb": sum(s.memory_mb for s in recent_snapshots) / len(recent_snapshots),
            "avg_memory_percent": sum(s.memory_percent for s in recent_snapshots)
            / len(recent_snapshots),
            "avg_disk_usage_percent": sum(s.disk_usage_percent for s in recent_snapshots)
            / len(recent_snapshots),
        }


class MetricsExporter:
    """
    Metrics exporter for monitoring systems

    Supports Prometheus text format
    """

    def __init__(
        self,
        performance_monitor: PerformanceMonitor,
        error_rate_monitor: ErrorRateMonitor,
        resource_monitor: ResourceMonitor,
    ):
        self.performance_monitor = performance_monitor
        self.error_rate_monitor = error_rate_monitor
        self.resource_monitor = resource_monitor

    def export_prometheus(self) -> str:
        """
        Export metrics in Prometheus text format

        Returns:
            Metrics in Prometheus format
        """
        lines: List[str] = []

        # Performance metrics
        lines.append("# HELP operation_duration_ms Operation duration in milliseconds")
        lines.append("# TYPE operation_duration_ms summary")
        for op, stats in self.performance_monitor.get_all_stats().items():
            safe_op = op.replace(" ", "_").replace("-", "_")
            lines.append(
                f'operation_duration_ms{{operation="{safe_op}",quantile="0.5"}} {stats["p50_duration_ms"]}'
            )
            lines.append(
                f'operation_duration_ms{{operation="{safe_op}",quantile="0.95"}} {stats["p95_duration_ms"]}'
            )
            lines.append(
                f'operation_duration_ms{{operation="{safe_op}",quantile="0.99"}} {stats["p99_duration_ms"]}'
            )

        # Operation counts
        lines.append("# HELP operation_total Total number of operations")
        lines.append("# TYPE operation_total counter")
        for op, stats in self.performance_monitor.get_all_stats().items():
            safe_op = op.replace(" ", "_").replace("-", "_")
            lines.append(f'operation_total{{operation="{safe_op}"}} {stats["total_count"]}')

        # Error rates
        lines.append("# HELP error_rate_per_minute Error rate per minute")
        lines.append("# TYPE error_rate_per_minute gauge")
        for error_type, rate in self.error_rate_monitor.get_all_error_rates().items():
            safe_type = error_type.replace(" ", "_").replace("-", "_")
            lines.append(f'error_rate_per_minute{{error_type="{safe_type}"}} {rate}')

        # Resource usage
        usage = self.resource_monitor.get_current_usage()
        lines.append("# HELP process_cpu_percent Process CPU usage percent")
        lines.append("# TYPE process_cpu_percent gauge")
        lines.append(f'process_cpu_percent {usage["cpu_percent"]}')

        lines.append("# HELP process_memory_mb Process memory usage in MB")
        lines.append("# TYPE process_memory_mb gauge")
        lines.append(f'process_memory_mb {usage["memory_mb"]}')

        return "\n".join(lines) + "\n"


# Global monitor instances
_performance_monitor: Optional[PerformanceMonitor] = None
_error_rate_monitor: Optional[ErrorRateMonitor] = None
_resource_monitor: Optional[ResourceMonitor] = None
_metrics_exporter: Optional[MetricsExporter] = None


def get_performance_monitor() -> PerformanceMonitor:
    """Get or create global performance monitor"""
    global _performance_monitor
    if _performance_monitor is None:
        _performance_monitor = PerformanceMonitor()
    return _performance_monitor


def get_error_rate_monitor() -> ErrorRateMonitor:
    """Get or create global error rate monitor"""
    global _error_rate_monitor
    if _error_rate_monitor is None:
        _error_rate_monitor = ErrorRateMonitor()
    return _error_rate_monitor


def get_resource_monitor() -> ResourceMonitor:
    """Get or create global resource monitor"""
    global _resource_monitor
    if _resource_monitor is None:
        _resource_monitor = ResourceMonitor()
    return _resource_monitor


def get_metrics_exporter() -> MetricsExporter:
    """Get or create global metrics exporter"""
    global _metrics_exporter
    if _metrics_exporter is None:
        _metrics_exporter = MetricsExporter(
            get_performance_monitor(),
            get_error_rate_monitor(),
            get_resource_monitor(),
        )
    return _metrics_exporter


def monitor_performance(operation_name: Optional[str] = None) -> Callable[[F], F]:
    """
    Decorator to monitor function performance

    Args:
        operation_name: Custom operation name (defaults to function name)

    Example:
        @monitor_performance()
        def process_file(path: str) -> bool:
            # ... processing logic ...
            return True
    """

    def decorator(func: F) -> F:
        op_name = operation_name or func.__name__

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            start_time = time.time()
            success = True
            error: Optional[Exception] = None

            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                success = False
                error = e
                raise
            finally:
                duration_ms = (time.time() - start_time) * 1000
                monitor = get_performance_monitor()
                monitor.record_metric(
                    operation=op_name,
                    duration_ms=duration_ms,
                    success=success,
                )

                if error:
                    error_monitor = get_error_rate_monitor()
                    error_monitor.record_error(type(error).__name__)

        return cast(F, wrapper)

    return decorator
