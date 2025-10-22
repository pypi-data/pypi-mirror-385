"""
自定义异常类模块

定义了项目中使用的所有自定义异常类，包括错误代码体系和错误消息模板。
所有异常都继承自 MCPExcelError 基类。

错误代码体系：
- E001-E099: 配置和认证错误
- E101-E199: 文件操作错误
- E201-E299: 数据验证错误
- E301-E399: 公式相关错误
- E401-E499: Sheet 操作错误
- E501-E599: 网络和超时错误
"""

from typing import Optional, Dict, Any


class MCPExcelError(Exception):
    """
    所有自定义异常的基类

    Attributes:
        error_code: 错误代码（如 E001）
        message: 错误消息
        context: 错误上下文信息
        suggestion: 建议的解决方案
    """

    def __init__(
        self,
        error_code: str,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        suggestion: Optional[str] = None,
    ):
        self.error_code = error_code
        self.message = message
        self.context = context or {}
        self.suggestion = suggestion

        # 构建完整的错误消息
        full_message = f"[{error_code}] {message}"
        if context:
            context_str = ", ".join(f"{k}={v}" for k, v in context.items())
            full_message += f" (上下文: {context_str})"
        if suggestion:
            full_message += f"\n建议: {suggestion}"

        super().__init__(full_message)

    def to_dict(self) -> Dict[str, Any]:
        """将异常转换为字典格式，便于序列化"""
        return {
            "error_code": self.error_code,
            "message": self.message,
            "context": self.context,
            "suggestion": self.suggestion,
        }


# ============================================================================
# 配置和认证错误 (E001-E099)
# ============================================================================


class ConfigError(MCPExcelError):
    """配置错误基类"""

    pass


class EnvironmentVariableNotSetError(ConfigError):
    """环境变量未设置错误 - E001"""

    def __init__(self, var_name: str):
        super().__init__(
            error_code="E001",
            message=f"环境变量 '{var_name}' 未设置",
            context={"variable": var_name},
            suggestion=f"请在 .env 文件中设置 {var_name}，或通过环境变量传入",
        )


class AuthError(MCPExcelError):
    """认证错误基类"""

    pass


class SupabaseAuthError(AuthError):
    """Supabase 认证失败错误 - E002"""

    def __init__(self, details: Optional[str] = None):
        super().__init__(
            error_code="E002",
            message="Supabase 认证失败",
            context={"details": details} if details else {},
            suggestion="请检查 SUPABASE_URL 和 SUPABASE_KEY 是否正确配置",
        )


# ============================================================================
# 文件操作错误 (E101-E199)
# ============================================================================


class FileOperationError(MCPExcelError):
    """文件操作错误基类"""

    pass


class FileNotFoundError(FileOperationError):
    """文件不存在错误 - E101"""

    def __init__(self, file_path: str):
        super().__init__(
            error_code="E101",
            message=f"文件不存在: {file_path}",
            context={"file_path": file_path},
            suggestion="请检查文件路径是否正确，或文件是否已被删除",
        )


class FileSizeError(FileOperationError):
    """文件大小超限错误 - E102"""

    def __init__(self, file_path: str, size_mb: float, limit_mb: float = 1.0):
        super().__init__(
            error_code="E102",
            message=f"文件大小 {size_mb:.2f}MB 超过限制 {limit_mb}MB",
            context={"file_path": file_path, "size_mb": size_mb, "limit_mb": limit_mb},
            suggestion=f"请使用小于 {limit_mb}MB 的文件，或联系管理员调整限制",
        )


class BatchLimitError(FileOperationError):
    """批量操作超限错误 - E103"""

    def __init__(self, count: int, limit: int = 20):
        super().__init__(
            error_code="E103",
            message=f"批量操作文件数 {count} 超过限制 {limit}",
            context={"count": count, "limit": limit},
            suggestion=f"请将文件分批处理，每批不超过 {limit} 个文件",
        )


class FileExistsError(FileOperationError):
    """文件已存在错误 - E104"""

    def __init__(self, file_path: str):
        super().__init__(
            error_code="E104",
            message=f"文件已存在: {file_path}",
            context={"file_path": file_path},
            suggestion="请设置 overwrite=True 以覆盖现有文件，或使用不同的文件名",
        )


class FileReadError(FileOperationError):
    """文件读取错误 - E105"""

    def __init__(self, file_path: str, details: Optional[str] = None):
        super().__init__(
            error_code="E105",
            message=f"无法读取文件: {file_path}",
            context=(
                {"file_path": file_path, "details": details}
                if details
                else {"file_path": file_path}
            ),
            suggestion="请检查文件是否损坏，或是否有读取权限",
        )


class FileWriteError(FileOperationError):
    """文件写入错误 - E106"""

    def __init__(self, file_path: str, details: Optional[str] = None):
        super().__init__(
            error_code="E106",
            message=f"无法写入文件: {file_path}",
            context=(
                {"file_path": file_path, "details": details}
                if details
                else {"file_path": file_path}
            ),
            suggestion="请检查是否有写入权限，或磁盘空间是否充足",
        )


# ============================================================================
# 数据验证错误 (E201-E299)
# ============================================================================


class ValidationError(MCPExcelError):
    """数据验证错误基类"""

    pass


class InvalidJSONError(ValidationError):
    """JSON 格式错误 - E201"""

    def __init__(self, details: Optional[str] = None):
        super().__init__(
            error_code="E201",
            message="JSON 格式错误",
            context={"details": details} if details else {},
            suggestion="请检查 JSON 格式是否正确，确保所有括号和引号匹配",
        )


class InvalidCellRangeError(ValidationError):
    """单元格范围无效错误 - E202"""

    def __init__(self, cell_range: str):
        super().__init__(
            error_code="E202",
            message=f"单元格范围无效: {cell_range}",
            context={"cell_range": cell_range},
            suggestion="请使用正确的单元格范围格式，如 'A1:B10' 或 'Sheet1!A1:B10'",
        )


class InvalidColorError(ValidationError):
    """颜色格式错误 - E203"""

    def __init__(self, color: str):
        super().__init__(
            error_code="E203",
            message=f"颜色格式错误: {color}",
            context={"color": color},
            suggestion="请使用十六进制颜色格式（如 '#FF0000'）或颜色名称（如 'red'）",
        )


class InvalidParameterError(ValidationError):
    """参数无效错误 - E204"""

    def __init__(self, param_name: str, param_value: Any, expected: str):
        super().__init__(
            error_code="E204",
            message=f"参数 '{param_name}' 的值无效",
            context={"param_name": param_name, "param_value": param_value, "expected": expected},
            suggestion=f"参数 '{param_name}' 应该是 {expected}",
        )


class DataRangeError(ValidationError):
    """数据范围错误 - E205"""

    def __init__(self, param_name: str, value: Any, min_val: Any = None, max_val: Any = None):
        range_desc = []
        if min_val is not None:
            range_desc.append(f"最小值: {min_val}")
        if max_val is not None:
            range_desc.append(f"最大值: {max_val}")
        range_str = ", ".join(range_desc)

        super().__init__(
            error_code="E205",
            message=f"参数 '{param_name}' 的值 {value} 超出有效范围",
            context={"param_name": param_name, "value": value, "min": min_val, "max": max_val},
            suggestion=f"请确保 '{param_name}' 在有效范围内 ({range_str})",
        )


# ============================================================================
# 公式相关错误 (E301-E399)
# ============================================================================


class FormulaError(MCPExcelError):
    """公式错误基类"""

    pass


class UnsupportedFormulaError(FormulaError):
    """不支持的公式错误 - E301"""

    def __init__(self, formula: str):
        super().__init__(
            error_code="E301",
            message=f"不支持的公式: {formula}",
            context={"formula": formula},
            suggestion="请查看文档了解支持的公式列表，或使用其他等效公式",
        )


class FormulaSyntaxError(FormulaError):
    """公式语法错误 - E302"""

    def __init__(self, formula: str, details: Optional[str] = None):
        super().__init__(
            error_code="E302",
            message=f"公式语法错误: {formula}",
            context={"formula": formula, "details": details} if details else {"formula": formula},
            suggestion="请检查公式语法是否正确，确保所有括号匹配且函数名正确",
        )


class FormulaCalculationError(FormulaError):
    """公式计算错误 - E303"""

    def __init__(self, formula: str, details: Optional[str] = None):
        super().__init__(
            error_code="E303",
            message=f"公式计算失败: {formula}",
            context={"formula": formula, "details": details} if details else {"formula": formula},
            suggestion="请检查公式引用的单元格是否存在，以及数据类型是否正确",
        )


# ============================================================================
# Sheet 操作错误 (E401-E499)
# ============================================================================


class SheetOperationError(MCPExcelError):
    """Sheet 操作错误基类"""

    pass


class SheetNotFoundError(SheetOperationError):
    """Sheet 不存在错误 - E401"""

    def __init__(self, sheet_name: str, available_sheets: Optional[list] = None):
        context: Dict[str, Any] = {"sheet_name": sheet_name}
        suggestion = "请检查 Sheet 名称是否正确"

        if available_sheets:
            context["available_sheets"] = available_sheets
            suggestion += f"。可用的 Sheet: {', '.join(str(s) for s in available_sheets)}"

        super().__init__(
            error_code="E401",
            message=f"Sheet 不存在: {sheet_name}",
            context=context,
            suggestion=suggestion,
        )


class SheetAlreadyExistsError(SheetOperationError):
    """Sheet 已存在错误 - E402"""

    def __init__(self, sheet_name: str):
        super().__init__(
            error_code="E402",
            message=f"Sheet 已存在: {sheet_name}",
            context={"sheet_name": sheet_name},
            suggestion="请使用不同的 Sheet 名称，或先删除现有的 Sheet",
        )


# ============================================================================
# 网络和超时错误 (E501-E599)
# ============================================================================


class NetworkError(MCPExcelError):
    """网络错误基类"""

    pass


class SupabaseNetworkError(NetworkError):
    """Supabase 网络错误 - E501"""

    def __init__(self, details: Optional[str] = None):
        super().__init__(
            error_code="E501",
            message="Supabase 网络连接失败",
            context={"details": details} if details else {},
            suggestion="请检查网络连接，或稍后重试",
        )


class TimeoutError(NetworkError):
    """操作超时错误 - E502"""

    def __init__(self, operation: str, timeout_seconds: int):
        super().__init__(
            error_code="E502",
            message=f"操作超时: {operation}",
            context={"operation": operation, "timeout_seconds": timeout_seconds},
            suggestion=f"操作在 {timeout_seconds} 秒内未完成，请检查网络或增加超时时间",
        )


# ============================================================================
# 错误消息模板
# ============================================================================

ERROR_MESSAGES = {
    "E001": "环境变量未设置",
    "E002": "Supabase 认证失败",
    "E101": "文件不存在",
    "E102": "文件大小超限",
    "E103": "批量操作超限",
    "E104": "文件已存在",
    "E105": "文件读取错误",
    "E106": "文件写入错误",
    "E201": "JSON 格式错误",
    "E202": "单元格范围无效",
    "E203": "颜色格式错误",
    "E204": "参数无效",
    "E205": "数据范围错误",
    "E301": "不支持的公式",
    "E302": "公式语法错误",
    "E303": "公式计算错误",
    "E401": "Sheet 不存在",
    "E402": "Sheet 已存在",
    "E501": "Supabase 网络错误",
    "E502": "操作超时",
}


def get_error_message(error_code: str) -> str:
    """
    根据错误代码获取错误消息模板

    Args:
        error_code: 错误代码（如 'E001'）

    Returns:
        错误消息模板
    """
    return ERROR_MESSAGES.get(error_code, "未知错误")
