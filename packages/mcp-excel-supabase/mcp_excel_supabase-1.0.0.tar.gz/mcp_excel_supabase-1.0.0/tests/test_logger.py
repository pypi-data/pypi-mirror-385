"""
测试日志工具模块
"""

import logging
from mcp_excel_supabase.utils.logger import (
    Logger,
    AuditLogger,
    PerformanceLogger,
    logger,
    audit_logger,
    performance_logger,
    get_logger,
    LOG_DIR,
    MAIN_LOG_FILE,
    AUDIT_LOG_FILE,
    PERFORMANCE_LOG_FILE,
)


class TestLogger:
    """测试主日志记录器"""

    def test_logger_singleton(self):
        """测试日志记录器单例模式"""
        logger1 = Logger("test")
        logger2 = Logger("test")
        assert logger1 is logger2

    def test_logger_different_names(self):
        """测试不同名称的日志记录器"""
        logger1 = Logger("test1")
        logger2 = Logger("test2")
        assert logger1 is not logger2

    def test_logger_debug(self):
        """测试 DEBUG 级别日志"""
        test_logger = Logger("test_debug")
        test_logger.logger.setLevel(logging.DEBUG)

        # 测试方法存在且可调用
        test_logger.debug("Debug message")
        assert True  # 如果没有异常，测试通过

    def test_logger_info(self):
        """测试 INFO 级别日志"""
        test_logger = Logger("test_info")

        # 测试方法存在且可调用
        test_logger.info("Info message")
        assert True

    def test_logger_warning(self):
        """测试 WARNING 级别日志"""
        test_logger = Logger("test_warning")

        # 测试方法存在且可调用
        test_logger.warning("Warning message")
        assert True

    def test_logger_error(self):
        """测试 ERROR 级别日志"""
        test_logger = Logger("test_error")

        # 测试方法存在且可调用
        test_logger.error("Error message")
        assert True

    def test_logger_critical(self):
        """测试 CRITICAL 级别日志"""
        test_logger = Logger("test_critical")

        # 测试方法存在且可调用
        test_logger.critical("Critical message")
        assert True

    def test_logger_exception(self):
        """测试异常日志"""
        test_logger = Logger("test_exception")

        try:
            raise ValueError("Test exception")
        except ValueError:
            # 测试方法存在且可调用
            test_logger.exception("Exception occurred")
            assert True

    def test_logger_with_extra_context(self):
        """测试带额外上下文的日志"""
        test_logger = Logger("test_context")

        # 测试方法存在且可调用
        test_logger.info("Message with context", user="alice", action="upload")
        assert True

    def test_log_files_created(self):
        """测试日志文件是否创建"""
        # 创建一个新的 logger 实例以触发文件创建
        test_logger = Logger("test_files")
        test_logger.info("Test message")

        # 检查日志目录是否存在
        assert LOG_DIR.exists()
        assert LOG_DIR.is_dir()

        # 检查主日志文件是否存在
        assert MAIN_LOG_FILE.exists()


class TestAuditLogger:
    """测试审计日志记录器"""

    def test_audit_logger_creation(self):
        """测试审计日志记录器创建"""
        audit = AuditLogger()
        assert audit.logger is not None
        assert audit.logger.name == "audit"

    def test_log_operation_basic(self):
        """测试基本操作日志"""
        audit = AuditLogger()

        # 测试方法存在且可调用
        audit.log_operation(operation="upload", status="success")
        assert True

    def test_log_operation_with_user(self):
        """测试带用户信息的操作日志"""
        audit = AuditLogger()

        # 测试方法存在且可调用
        audit.log_operation(operation="download", user="alice", status="success")
        assert True

    def test_log_operation_with_resource(self):
        """测试带资源信息的操作日志"""
        audit = AuditLogger()

        # 测试方法存在且可调用
        audit.log_operation(operation="delete", resource="/path/to/file.xlsx", status="success")
        assert True

    def test_log_operation_with_details(self):
        """测试带详细信息的操作日志"""
        audit = AuditLogger()

        # 测试方法存在且可调用
        audit.log_operation(
            operation="upload",
            user="bob",
            resource="file.xlsx",
            status="failed",
            details="File too large",
        )
        assert True

    def test_audit_log_file_created(self):
        """测试审计日志文件是否创建"""
        audit = AuditLogger()
        audit.log_operation("test", status="success")

        # 检查审计日志文件是否存在
        assert AUDIT_LOG_FILE.exists()


class TestPerformanceLogger:
    """测试性能日志记录器"""

    def test_performance_logger_creation(self):
        """测试性能日志记录器创建"""
        perf = PerformanceLogger()
        assert perf.logger is not None
        assert perf.logger.name == "performance"

    def test_log_performance_basic(self):
        """测试基本性能日志"""
        perf = PerformanceLogger()

        # 测试方法存在且可调用
        perf.log_performance(operation="parse_excel", duration_ms=1500.5)
        assert True

    def test_log_performance_with_file_size(self):
        """测试带文件大小的性能日志"""
        perf = PerformanceLogger()

        # 测试方法存在且可调用
        perf.log_performance(operation="upload", duration_ms=2000.0, file_size_mb=0.5)
        assert True

    def test_log_performance_with_record_count(self):
        """测试带记录数的性能日志"""
        perf = PerformanceLogger()

        # 测试方法存在且可调用
        perf.log_performance(operation="generate_excel", duration_ms=3000.0, record_count=1000)
        assert True

    def test_log_performance_failed(self):
        """测试失败的性能日志"""
        perf = PerformanceLogger()

        # 测试方法存在且可调用
        perf.log_performance(operation="parse_excel", duration_ms=500.0, success=False)
        assert True

    def test_performance_log_file_created(self):
        """测试性能日志文件是否创建"""
        perf = PerformanceLogger()
        perf.log_performance("test", 100.0)

        # 检查性能日志文件是否存在
        assert PERFORMANCE_LOG_FILE.exists()


class TestGlobalLoggerInstances:
    """测试全局日志实例"""

    def test_global_logger_exists(self):
        """测试全局 logger 实例存在"""
        assert logger is not None
        assert isinstance(logger, Logger)

    def test_global_audit_logger_exists(self):
        """测试全局 audit_logger 实例存在"""
        assert audit_logger is not None
        assert isinstance(audit_logger, AuditLogger)

    def test_global_performance_logger_exists(self):
        """测试全局 performance_logger 实例存在"""
        assert performance_logger is not None
        assert isinstance(performance_logger, PerformanceLogger)


class TestGetLogger:
    """测试 get_logger 函数"""

    def test_get_logger_default(self):
        """测试获取默认日志记录器"""
        log = get_logger()
        assert log is not None
        assert isinstance(log, Logger)

    def test_get_logger_custom_name(self):
        """测试获取自定义名称的日志记录器"""
        log = get_logger("custom")
        assert log is not None
        assert log.name == "custom"

    def test_get_logger_singleton(self):
        """测试 get_logger 返回单例"""
        log1 = get_logger("test")
        log2 = get_logger("test")
        assert log1 is log2


class TestLogDirectory:
    """测试日志目录"""

    def test_log_directory_exists(self):
        """测试日志目录存在"""
        assert LOG_DIR.exists()
        assert LOG_DIR.is_dir()

    def test_log_directory_path(self):
        """测试日志目录路径"""
        assert LOG_DIR.name == "logs"
