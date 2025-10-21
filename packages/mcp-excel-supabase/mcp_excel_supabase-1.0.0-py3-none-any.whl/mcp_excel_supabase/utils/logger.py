"""
日志工具模块

提供统一的日志记录功能，支持：
- 多级别日志（DEBUG, INFO, WARNING, ERROR, CRITICAL）
- 文件和控制台双输出
- 日志轮转（按大小和时间）
- 结构化日志格式（JSON）
- 性能日志和审计日志
- 错误追踪和统计
"""

import json
import logging
import os
import sys
import traceback
from collections import defaultdict
from datetime import datetime
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from pathlib import Path
from typing import Any, Dict, List, Optional


# 日志目录
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

# 日志文件路径
MAIN_LOG_FILE = LOG_DIR / "mcp_excel.log"
ERROR_LOG_FILE = LOG_DIR / "error.log"
AUDIT_LOG_FILE = LOG_DIR / "audit.log"
PERFORMANCE_LOG_FILE = LOG_DIR / "performance.log"
STRUCTURED_LOG_FILE = LOG_DIR / "structured.jsonl"
ERROR_TRACKING_FILE = LOG_DIR / "error_tracking.jsonl"

# 日志格式
DETAILED_FORMAT = (
    "%(asctime)s - %(name)s - %(levelname)s - "
    "[%(filename)s:%(lineno)d] - %(funcName)s() - %(message)s"
)
SIMPLE_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
CONSOLE_FORMAT = "%(levelname)s - %(message)s"

# 日期格式
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


class Logger:
    """
    日志管理器类

    提供统一的日志记录接口，支持多种日志类型和输出方式。
    """

    _instances: dict[str, "Logger"] = {}

    def __new__(cls, name: str = "mcp_excel_supabase") -> "Logger":
        """单例模式，确保同名 logger 只创建一次"""
        if name not in cls._instances:
            instance = super().__new__(cls)
            cls._instances[name] = instance
        return cls._instances[name]

    def __init__(self, name: str = "mcp_excel_supabase") -> None:
        """
        初始化日志记录器

        Args:
            name: 日志记录器名称
        """
        # 避免重复初始化
        if hasattr(self, "_initialized"):
            return

        self.name = name
        self.logger = logging.getLogger(name)

        # 从环境变量获取日志级别，默认为 INFO
        log_level = os.getenv("LOG_LEVEL", "INFO").upper()
        self.logger.setLevel(getattr(logging, log_level, logging.INFO))

        # 避免日志重复
        self.logger.propagate = False

        # 清除已有的处理器
        self.logger.handlers.clear()

        # 添加处理器
        self._add_console_handler()
        self._add_file_handler()
        self._add_error_handler()

        self._initialized = True

    def _add_console_handler(self) -> None:
        """添加控制台处理器"""
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)

        formatter = logging.Formatter(CONSOLE_FORMAT, datefmt=DATE_FORMAT)
        console_handler.setFormatter(formatter)

        self.logger.addHandler(console_handler)

    def _add_file_handler(self) -> None:
        """添加文件处理器（带轮转）"""
        # 按大小轮转：每个文件最大 10MB，保留 5 个备份
        file_handler = RotatingFileHandler(
            MAIN_LOG_FILE, maxBytes=10 * 1024 * 1024, backupCount=5, encoding="utf-8"  # 10MB
        )
        file_handler.setLevel(logging.DEBUG)

        formatter = logging.Formatter(DETAILED_FORMAT, datefmt=DATE_FORMAT)
        file_handler.setFormatter(formatter)

        self.logger.addHandler(file_handler)

    def _add_error_handler(self) -> None:
        """添加错误日志处理器"""
        # 只记录 ERROR 及以上级别的日志
        error_handler = RotatingFileHandler(
            ERROR_LOG_FILE, maxBytes=10 * 1024 * 1024, backupCount=5, encoding="utf-8"  # 10MB
        )
        error_handler.setLevel(logging.ERROR)

        formatter = logging.Formatter(DETAILED_FORMAT, datefmt=DATE_FORMAT)
        error_handler.setFormatter(formatter)

        self.logger.addHandler(error_handler)

    def debug(self, message: str, **kwargs: Any) -> None:
        """记录 DEBUG 级别日志"""
        self.logger.debug(message, extra=kwargs)

    def info(self, message: str, **kwargs: Any) -> None:
        """记录 INFO 级别日志"""
        self.logger.info(message, extra=kwargs)

    def warning(self, message: str, **kwargs: Any) -> None:
        """记录 WARNING 级别日志"""
        self.logger.warning(message, extra=kwargs)

    def error(self, message: str, exc_info: bool = False, **kwargs: Any) -> None:
        """
        记录 ERROR 级别日志

        Args:
            message: 日志消息
            exc_info: 是否包含异常堆栈信息
            **kwargs: 额外的上下文信息
        """
        self.logger.error(message, exc_info=exc_info, extra=kwargs)

    def critical(self, message: str, exc_info: bool = False, **kwargs: Any) -> None:
        """
        记录 CRITICAL 级别日志

        Args:
            message: 日志消息
            exc_info: 是否包含异常堆栈信息
            **kwargs: 额外的上下文信息
        """
        self.logger.critical(message, exc_info=exc_info, extra=kwargs)

    def exception(self, message: str, **kwargs: Any) -> None:
        """
        记录异常日志（自动包含堆栈信息）

        Args:
            message: 日志消息
            **kwargs: 额外的上下文信息
        """
        self.logger.exception(message, extra=kwargs)


class AuditLogger:
    """
    审计日志记录器

    用于记录重要的操作审计信息，如文件上传、下载、删除等。
    """

    def __init__(self) -> None:
        self.logger = logging.getLogger("audit")
        self.logger.setLevel(logging.INFO)
        self.logger.propagate = False

        # 清除已有的处理器
        self.logger.handlers.clear()

        # 按天轮转审计日志
        handler = TimedRotatingFileHandler(
            AUDIT_LOG_FILE,
            when="midnight",
            interval=1,
            backupCount=30,  # 保留 30 天
            encoding="utf-8",
        )
        handler.setLevel(logging.INFO)

        formatter = logging.Formatter("%(asctime)s - %(message)s", datefmt=DATE_FORMAT)
        handler.setFormatter(formatter)

        self.logger.addHandler(handler)

    def log_operation(
        self,
        operation: str,
        user: Optional[str] = None,
        resource: Optional[str] = None,
        status: str = "success",
        details: Optional[str] = None,
    ) -> None:
        """
        记录操作审计日志

        Args:
            operation: 操作类型（如 'upload', 'download', 'delete'）
            user: 用户标识
            resource: 资源标识（如文件路径）
            status: 操作状态（'success' 或 'failed'）
            details: 详细信息
        """
        log_parts = [f"OPERATION={operation}"]

        if user:
            log_parts.append(f"USER={user}")
        if resource:
            log_parts.append(f"RESOURCE={resource}")

        log_parts.append(f"STATUS={status}")

        if details:
            log_parts.append(f"DETAILS={details}")

        self.logger.info(" | ".join(log_parts))


class PerformanceLogger:
    """
    性能日志记录器

    用于记录操作的性能指标，如执行时间、文件大小等。
    """

    def __init__(self) -> None:
        self.logger = logging.getLogger("performance")
        self.logger.setLevel(logging.INFO)
        self.logger.propagate = False

        # 清除已有的处理器
        self.logger.handlers.clear()

        # 按天轮转性能日志
        handler = TimedRotatingFileHandler(
            PERFORMANCE_LOG_FILE,
            when="midnight",
            interval=1,
            backupCount=7,  # 保留 7 天
            encoding="utf-8",
        )
        handler.setLevel(logging.INFO)

        formatter = logging.Formatter("%(asctime)s - %(message)s", datefmt=DATE_FORMAT)
        handler.setFormatter(formatter)

        self.logger.addHandler(handler)

    def log_performance(
        self,
        operation: str,
        duration_ms: float,
        file_size_mb: Optional[float] = None,
        record_count: Optional[int] = None,
        success: bool = True,
    ) -> None:
        """
        记录性能指标

        Args:
            operation: 操作类型
            duration_ms: 执行时间（毫秒）
            file_size_mb: 文件大小（MB）
            record_count: 记录数量
            success: 是否成功
        """
        log_parts = [
            f"OPERATION={operation}",
            f"DURATION={duration_ms:.2f}ms",
            f"STATUS={'success' if success else 'failed'}",
        ]

        if file_size_mb is not None:
            log_parts.append(f"FILE_SIZE={file_size_mb:.2f}MB")

        if record_count is not None:
            log_parts.append(f"RECORDS={record_count}")

        self.logger.info(" | ".join(log_parts))


# ============================================================================
# 便捷函数
# ============================================================================


def get_logger(name: str = "mcp_excel_supabase") -> Logger:
    """
    获取日志记录器实例

    Args:
        name: 日志记录器名称

    Returns:
        Logger 实例
    """
    return Logger(name)


def log_function_call(func: Any) -> Any:
    """
    装饰器：自动记录函数调用日志

    使用示例:
        @log_function_call
        def my_function(arg1, arg2):
            pass
    """

    def wrapper(*args: Any, **kwargs: Any) -> Any:
        logger.debug(f"调用函数: {func.__name__}, args={args}, kwargs={kwargs}")
        try:
            result = func(*args, **kwargs)
            logger.debug(f"函数 {func.__name__} 执行成功")
            return result
        except Exception as e:
            logger.error(f"函数 {func.__name__} 执行失败: {str(e)}", exc_info=True)
            raise

    return wrapper


class JSONFormatter(logging.Formatter):
    """
    JSON格式化器，将日志输出为JSON格式

    每条日志记录为一行JSON（JSONL格式），便于日志分析工具处理
    """

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON"""
        log_data: Dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                "traceback": traceback.format_exception(*record.exc_info),
            }

        # Add extra fields from 'extra' parameter
        for key, value in record.__dict__.items():
            if key not in [
                "name",
                "msg",
                "args",
                "created",
                "filename",
                "funcName",
                "levelname",
                "levelno",
                "lineno",
                "module",
                "msecs",
                "message",
                "pathname",
                "process",
                "processName",
                "relativeCreated",
                "thread",
                "threadName",
                "exc_info",
                "exc_text",
                "stack_info",
            ]:
                log_data[key] = value

        return json.dumps(log_data, ensure_ascii=False)


class StructuredLogger:
    """
    结构化日志记录器

    以JSON格式记录日志，便于日志分析和监控系统集成
    """

    def __init__(self) -> None:
        self.logger = logging.getLogger("structured")
        self.logger.setLevel(logging.DEBUG)
        self.logger.propagate = False

        # Clear existing handlers
        self.logger.handlers.clear()

        # Add JSON file handler
        handler = RotatingFileHandler(
            STRUCTURED_LOG_FILE,
            maxBytes=50 * 1024 * 1024,  # 50MB
            backupCount=10,
            encoding="utf-8",
        )
        handler.setLevel(logging.DEBUG)
        handler.setFormatter(JSONFormatter())

        self.logger.addHandler(handler)

    def log(
        self,
        level: str,
        message: str,
        **context: Any,
    ) -> None:
        """
        Log a structured message

        Args:
            level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            message: Log message
            **context: Additional context fields
        """
        log_level = getattr(logging, level.upper(), logging.INFO)
        self.logger.log(log_level, message, extra=context)

    def debug(self, message: str, **context: Any) -> None:
        """Log DEBUG level structured message"""
        self.log("DEBUG", message, **context)

    def info(self, message: str, **context: Any) -> None:
        """Log INFO level structured message"""
        self.log("INFO", message, **context)

    def warning(self, message: str, **context: Any) -> None:
        """Log WARNING level structured message"""
        self.log("WARNING", message, **context)

    def error(self, message: str, **context: Any) -> None:
        """Log ERROR level structured message"""
        self.log("ERROR", message, **context)

    def critical(self, message: str, **context: Any) -> None:
        """Log CRITICAL level structured message"""
        self.log("CRITICAL", message, **context)


class ErrorTracker:
    """
    错误追踪器

    统计和追踪系统中的错误，提供错误分析功能
    """

    def __init__(self) -> None:
        self.logger = logging.getLogger("error_tracker")
        self.logger.setLevel(logging.ERROR)
        self.logger.propagate = False

        # Clear existing handlers
        self.logger.handlers.clear()

        # Add JSON file handler for error tracking
        handler = RotatingFileHandler(
            ERROR_TRACKING_FILE,
            maxBytes=50 * 1024 * 1024,  # 50MB
            backupCount=10,
            encoding="utf-8",
        )
        handler.setLevel(logging.ERROR)
        handler.setFormatter(JSONFormatter())

        self.logger.addHandler(handler)

        # In-memory error statistics
        self.error_counts: Dict[str, int] = defaultdict(int)
        self.error_history: List[Dict[str, Any]] = []
        self.max_history_size = 1000

    def track_error(
        self,
        error: Exception,
        operation: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Track an error occurrence

        Args:
            error: The exception that occurred
            operation: Name of the operation that failed
            context: Additional context information
        """
        error_type = type(error).__name__
        error_key = f"{error_type}:{operation}"

        # Update statistics
        self.error_counts[error_key] += 1

        # Create error record
        error_record: Dict[str, Any] = {
            "timestamp": datetime.now().isoformat(),
            "error_type": error_type,
            "error_message": str(error),
            "operation": operation,
            "count": self.error_counts[error_key],
        }

        if context:
            error_record["context"] = context

        # Add to history (with size limit)
        self.error_history.append(error_record)
        if len(self.error_history) > self.max_history_size:
            self.error_history.pop(0)

        # Log to file
        self.logger.error(
            f"Error in {operation}: {error}",
            extra=error_record,
            exc_info=True,
        )

    def get_error_stats(self) -> Dict[str, Any]:
        """Get error statistics"""
        return {
            "total_errors": sum(self.error_counts.values()),
            "unique_errors": len(self.error_counts),
            "error_counts": dict(self.error_counts),
            "recent_errors": self.error_history[-10:],
        }

    def get_top_errors(self, limit: int = 10) -> List[tuple[str, int]]:
        """Get top N most frequent errors"""
        sorted_errors = sorted(self.error_counts.items(), key=lambda x: x[1], reverse=True)
        return sorted_errors[:limit]

    def clear_stats(self) -> None:
        """Clear error statistics"""
        self.error_counts.clear()
        self.error_history.clear()


# ============================================================================
# 全局日志实例
# ============================================================================

# 主日志记录器
logger = Logger()

# 审计日志记录器
audit_logger = AuditLogger()

# 性能日志记录器
performance_logger = PerformanceLogger()

# 结构化日志记录器
structured_logger = StructuredLogger()

# 错误追踪器
error_tracker = ErrorTracker()
