"""
Tests for monitor module
"""

import pytest
import time
from datetime import datetime, timedelta

from src.mcp_excel_supabase.utils.monitor import (
    PerformanceMetric,
    ResourceSnapshot,
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


class TestPerformanceMetric:
    """Test PerformanceMetric dataclass"""

    def test_performance_metric_creation(self):
        """Test creating performance metric"""
        metric = PerformanceMetric(
            operation="test_op",
            duration_ms=123.45,
            timestamp=datetime.now(),
            success=True,
            metadata={"key": "value"},
        )

        assert metric.operation == "test_op"
        assert metric.duration_ms == 123.45
        assert metric.success is True
        assert metric.metadata == {"key": "value"}


class TestResourceSnapshot:
    """Test ResourceSnapshot dataclass"""

    def test_resource_snapshot_creation(self):
        """Test creating resource snapshot"""
        snapshot = ResourceSnapshot(
            timestamp=datetime.now(),
            cpu_percent=25.5,
            memory_mb=100.0,
            memory_percent=10.0,
            disk_usage_percent=50.0,
        )

        assert snapshot.cpu_percent == 25.5
        assert snapshot.memory_mb == 100.0
        assert snapshot.memory_percent == 10.0
        assert snapshot.disk_usage_percent == 50.0


class TestPerformanceMonitor:
    """Test PerformanceMonitor class"""

    def test_performance_monitor_creation(self):
        """Test creating performance monitor"""
        monitor = PerformanceMonitor(window_size=100)

        assert monitor.window_size == 100
        assert len(monitor.metrics) == 0
        assert len(monitor.operation_counts) == 0

    def test_record_metric(self):
        """Test recording a metric"""
        monitor = PerformanceMonitor()

        monitor.record_metric(
            operation="test_op",
            duration_ms=100.0,
            success=True,
            metadata={"key": "value"},
        )

        assert len(monitor.metrics["test_op"]) == 1
        assert monitor.operation_counts["test_op"] == 1
        assert monitor.success_counts["test_op"] == 1
        assert monitor.failure_counts["test_op"] == 0

    def test_record_multiple_metrics(self):
        """Test recording multiple metrics"""
        monitor = PerformanceMonitor()

        for i in range(10):
            monitor.record_metric(
                operation="test_op",
                duration_ms=100.0 + i,
                success=True,
            )

        assert len(monitor.metrics["test_op"]) == 10
        assert monitor.operation_counts["test_op"] == 10

    def test_record_success_and_failure(self):
        """Test recording success and failure metrics"""
        monitor = PerformanceMonitor()

        monitor.record_metric("test_op", 100.0, success=True)
        monitor.record_metric("test_op", 200.0, success=True)
        monitor.record_metric("test_op", 150.0, success=False)

        assert monitor.success_counts["test_op"] == 2
        assert monitor.failure_counts["test_op"] == 1

    def test_get_stats(self):
        """Test getting statistics"""
        monitor = PerformanceMonitor()

        # Record some metrics
        for i in range(100):
            monitor.record_metric("test_op", 100.0 + i, success=True)

        stats = monitor.get_stats("test_op")

        assert stats["operation"] == "test_op"
        assert stats["count"] == 100
        assert stats["total_count"] == 100
        assert stats["success_count"] == 100
        assert stats["failure_count"] == 0
        assert stats["success_rate"] == 1.0
        assert stats["avg_duration_ms"] == 149.5  # Average of 100-199
        assert stats["min_duration_ms"] == 100.0
        assert stats["max_duration_ms"] == 199.0
        assert 140 < stats["p50_duration_ms"] < 160
        assert 180 < stats["p95_duration_ms"] < 200
        assert 190 < stats["p99_duration_ms"] < 200

    def test_get_stats_empty(self):
        """Test getting stats for non-existent operation"""
        monitor = PerformanceMonitor()

        stats = monitor.get_stats("non_existent")

        assert stats["operation"] == "non_existent"
        assert stats["count"] == 0

    def test_get_all_stats(self):
        """Test getting all statistics"""
        monitor = PerformanceMonitor()

        monitor.record_metric("op1", 100.0, success=True)
        monitor.record_metric("op2", 200.0, success=True)

        all_stats = monitor.get_all_stats()

        assert "op1" in all_stats
        assert "op2" in all_stats
        assert all_stats["op1"]["count"] == 1
        assert all_stats["op2"]["count"] == 1

    def test_clear_metrics_specific(self):
        """Test clearing metrics for specific operation"""
        monitor = PerformanceMonitor()

        monitor.record_metric("op1", 100.0, success=True)
        monitor.record_metric("op2", 200.0, success=True)

        monitor.clear_metrics("op1")

        assert len(monitor.metrics["op1"]) == 0
        assert len(monitor.metrics["op2"]) == 1

    def test_clear_metrics_all(self):
        """Test clearing all metrics"""
        monitor = PerformanceMonitor()

        monitor.record_metric("op1", 100.0, success=True)
        monitor.record_metric("op2", 200.0, success=True)

        monitor.clear_metrics()

        assert len(monitor.metrics) == 0
        assert len(monitor.operation_counts) == 0

    def test_window_size_limit(self):
        """Test that window size is respected"""
        monitor = PerformanceMonitor(window_size=10)

        # Record more metrics than window size
        for i in range(20):
            monitor.record_metric("test_op", 100.0 + i, success=True)

        # Should only keep last 10
        assert len(monitor.metrics["test_op"]) == 10
        # But total count should be 20
        assert monitor.operation_counts["test_op"] == 20


class TestErrorRateMonitor:
    """Test ErrorRateMonitor class"""

    def test_error_rate_monitor_creation(self):
        """Test creating error rate monitor"""
        monitor = ErrorRateMonitor(window_minutes=30)

        assert monitor.window_minutes == 30
        assert len(monitor.error_timestamps) == 0

    def test_record_error(self):
        """Test recording an error"""
        monitor = ErrorRateMonitor()

        monitor.record_error("ValueError")

        assert len(monitor.error_timestamps["ValueError"]) == 1

    def test_record_multiple_errors(self):
        """Test recording multiple errors"""
        monitor = ErrorRateMonitor()

        for _ in range(5):
            monitor.record_error("ValueError")

        assert len(monitor.error_timestamps["ValueError"]) == 5

    def test_get_error_rate(self):
        """Test getting error rate"""
        monitor = ErrorRateMonitor(window_minutes=60)

        # Record 10 errors
        for _ in range(10):
            monitor.record_error("ValueError")

        rate = monitor.get_error_rate("ValueError")

        # 10 errors in 60 minutes = 0.167 errors/minute
        assert 0.15 < rate < 0.20

    def test_get_all_error_rates(self):
        """Test getting all error rates"""
        monitor = ErrorRateMonitor()

        monitor.record_error("ValueError")
        monitor.record_error("TypeError")

        rates = monitor.get_all_error_rates()

        assert "ValueError" in rates
        assert "TypeError" in rates

    def test_get_total_errors(self):
        """Test getting total error count"""
        monitor = ErrorRateMonitor()

        monitor.record_error("ValueError")
        monitor.record_error("ValueError")
        monitor.record_error("TypeError")

        total = monitor.get_total_errors()
        assert total == 3

        total_value_error = monitor.get_total_errors("ValueError")
        assert total_value_error == 2


class TestResourceMonitor:
    """Test ResourceMonitor class"""

    def test_resource_monitor_creation(self):
        """Test creating resource monitor"""
        monitor = ResourceMonitor(history_size=50)

        assert monitor.history_size == 50
        assert len(monitor.snapshots) == 0

    def test_take_snapshot(self):
        """Test taking a resource snapshot"""
        monitor = ResourceMonitor()

        snapshot = monitor.take_snapshot()

        assert snapshot.cpu_percent >= 0
        assert snapshot.memory_mb > 0
        assert snapshot.memory_percent >= 0
        assert snapshot.disk_usage_percent >= 0
        assert len(monitor.snapshots) == 1

    def test_get_current_usage(self):
        """Test getting current usage"""
        monitor = ResourceMonitor()

        usage = monitor.get_current_usage()

        assert "timestamp" in usage
        assert "cpu_percent" in usage
        assert "memory_mb" in usage
        assert "memory_percent" in usage
        assert "disk_usage_percent" in usage

    def test_get_average_usage(self):
        """Test getting average usage"""
        monitor = ResourceMonitor()

        # Take multiple snapshots
        for _ in range(5):
            monitor.take_snapshot()
            time.sleep(0.1)

        avg_usage = monitor.get_average_usage(minutes=5)

        assert "avg_cpu_percent" in avg_usage
        assert "avg_memory_mb" in avg_usage
        assert "avg_memory_percent" in avg_usage
        assert "avg_disk_usage_percent" in avg_usage

    def test_history_size_limit(self):
        """Test that history size is respected"""
        monitor = ResourceMonitor(history_size=10)

        # Take more snapshots than history size
        for _ in range(20):
            monitor.take_snapshot()

        # Should only keep last 10
        assert len(monitor.snapshots) == 10


class TestMetricsExporter:
    """Test MetricsExporter class"""

    def test_metrics_exporter_creation(self):
        """Test creating metrics exporter"""
        perf_monitor = PerformanceMonitor()
        error_monitor = ErrorRateMonitor()
        resource_monitor = ResourceMonitor()

        exporter = MetricsExporter(perf_monitor, error_monitor, resource_monitor)

        assert exporter.performance_monitor is perf_monitor
        assert exporter.error_rate_monitor is error_monitor
        assert exporter.resource_monitor is resource_monitor

    def test_export_prometheus(self):
        """Test exporting metrics in Prometheus format"""
        perf_monitor = PerformanceMonitor()
        error_monitor = ErrorRateMonitor()
        resource_monitor = ResourceMonitor()

        # Add some metrics
        perf_monitor.record_metric("test_op", 100.0, success=True)
        error_monitor.record_error("ValueError")
        resource_monitor.take_snapshot()

        exporter = MetricsExporter(perf_monitor, error_monitor, resource_monitor)
        prometheus_text = exporter.export_prometheus()

        # Check that output contains expected metrics
        assert "operation_duration_ms" in prometheus_text
        assert "operation_total" in prometheus_text
        assert "error_rate_per_minute" in prometheus_text
        assert "process_cpu_percent" in prometheus_text
        assert "process_memory_mb" in prometheus_text


class TestGlobalMonitors:
    """Test global monitor instances"""

    def test_get_performance_monitor(self):
        """Test getting global performance monitor"""
        monitor1 = get_performance_monitor()
        monitor2 = get_performance_monitor()

        # Should return the same instance
        assert monitor1 is monitor2

    def test_get_error_rate_monitor(self):
        """Test getting global error rate monitor"""
        monitor1 = get_error_rate_monitor()
        monitor2 = get_error_rate_monitor()

        # Should return the same instance
        assert monitor1 is monitor2

    def test_get_resource_monitor(self):
        """Test getting global resource monitor"""
        monitor1 = get_resource_monitor()
        monitor2 = get_resource_monitor()

        # Should return the same instance
        assert monitor1 is monitor2

    def test_get_metrics_exporter(self):
        """Test getting global metrics exporter"""
        exporter1 = get_metrics_exporter()
        exporter2 = get_metrics_exporter()

        # Should return the same instance
        assert exporter1 is exporter2


class TestMonitorPerformanceDecorator:
    """Test monitor_performance decorator"""

    def test_monitor_performance_success(self):
        """Test decorator with successful function"""

        @monitor_performance()
        def test_func() -> str:
            time.sleep(0.1)
            return "success"

        result = test_func()

        assert result == "success"

        # Check that metric was recorded
        monitor = get_performance_monitor()
        stats = monitor.get_stats("test_func")
        assert stats["count"] >= 1
        assert stats["success_count"] >= 1

    def test_monitor_performance_with_custom_name(self):
        """Test decorator with custom operation name"""

        @monitor_performance(operation_name="custom_operation")
        def test_func() -> str:
            return "success"

        result = test_func()

        assert result == "success"

        # Check that metric was recorded with custom name
        monitor = get_performance_monitor()
        stats = monitor.get_stats("custom_operation")
        assert stats["count"] >= 1

    def test_monitor_performance_on_error(self):
        """Test decorator records failure on error"""

        @monitor_performance()
        def test_func() -> str:
            raise ValueError("test error")

        with pytest.raises(ValueError):
            test_func()

        # Check that failure was recorded
        monitor = get_performance_monitor()
        stats = monitor.get_stats("test_func")
        assert stats["failure_count"] >= 1

