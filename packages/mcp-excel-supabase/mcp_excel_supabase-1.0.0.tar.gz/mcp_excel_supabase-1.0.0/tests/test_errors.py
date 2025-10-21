"""
测试自定义异常类模块
"""

from mcp_excel_supabase.utils.errors import (
    MCPExcelError,
    EnvironmentVariableNotSetError,
    SupabaseAuthError,
    FileNotFoundError,
    FileSizeError,
    BatchLimitError,
    FileExistsError,
    FileReadError,
    FileWriteError,
    InvalidJSONError,
    InvalidCellRangeError,
    InvalidColorError,
    InvalidParameterError,
    DataRangeError,
    UnsupportedFormulaError,
    FormulaSyntaxError,
    FormulaCalculationError,
    SheetNotFoundError,
    SheetAlreadyExistsError,
    SupabaseNetworkError,
    TimeoutError,
    get_error_message,
    ERROR_MESSAGES,
)


class TestMCPExcelError:
    """测试基础异常类"""

    def test_basic_error(self):
        """测试基本错误创建"""
        error = MCPExcelError(error_code="E999", message="Test error")
        assert error.error_code == "E999"
        assert error.message == "Test error"
        assert error.context == {}
        assert error.suggestion is None

    def test_error_with_context(self):
        """测试带上下文的错误"""
        error = MCPExcelError(error_code="E999", message="Test error", context={"key": "value"})
        assert error.context == {"key": "value"}
        assert "key=value" in str(error)

    def test_error_with_suggestion(self):
        """测试带建议的错误"""
        error = MCPExcelError(error_code="E999", message="Test error", suggestion="Try this")
        assert error.suggestion == "Try this"
        assert "建议: Try this" in str(error)

    def test_to_dict(self):
        """测试转换为字典"""
        error = MCPExcelError(
            error_code="E999", message="Test error", context={"key": "value"}, suggestion="Try this"
        )
        error_dict = error.to_dict()
        assert error_dict["error_code"] == "E999"
        assert error_dict["message"] == "Test error"
        assert error_dict["context"] == {"key": "value"}
        assert error_dict["suggestion"] == "Try this"


class TestConfigErrors:
    """测试配置和认证错误"""

    def test_environment_variable_not_set_error(self):
        """测试环境变量未设置错误"""
        error = EnvironmentVariableNotSetError("TEST_VAR")
        assert error.error_code == "E001"
        assert "TEST_VAR" in error.message
        assert error.context["variable"] == "TEST_VAR"

    def test_supabase_auth_error(self):
        """测试 Supabase 认证错误"""
        error = SupabaseAuthError("Invalid credentials")
        assert error.error_code == "E002"
        assert error.context["details"] == "Invalid credentials"


class TestFileOperationErrors:
    """测试文件操作错误"""

    def test_file_not_found_error(self):
        """测试文件不存在错误"""
        error = FileNotFoundError("/path/to/file.xlsx")
        assert error.error_code == "E101"
        assert "/path/to/file.xlsx" in error.message

    def test_file_size_error(self):
        """测试文件大小超限错误"""
        error = FileSizeError("/path/to/file.xlsx", 2.5, 1.0)
        assert error.error_code == "E102"
        assert error.context["size_mb"] == 2.5
        assert error.context["limit_mb"] == 1.0

    def test_batch_limit_error(self):
        """测试批量操作超限错误"""
        error = BatchLimitError(25, 20)
        assert error.error_code == "E103"
        assert error.context["count"] == 25
        assert error.context["limit"] == 20

    def test_file_exists_error(self):
        """测试文件已存在错误"""
        error = FileExistsError("/path/to/file.xlsx")
        assert error.error_code == "E104"
        assert "/path/to/file.xlsx" in error.message

    def test_file_read_error(self):
        """测试文件读取错误"""
        error = FileReadError("/path/to/file.xlsx", "Permission denied")
        assert error.error_code == "E105"
        assert error.context["details"] == "Permission denied"

    def test_file_write_error(self):
        """测试文件写入错误"""
        error = FileWriteError("/path/to/file.xlsx", "Disk full")
        assert error.error_code == "E106"
        assert error.context["details"] == "Disk full"


class TestValidationErrors:
    """测试数据验证错误"""

    def test_invalid_json_error(self):
        """测试 JSON 格式错误"""
        error = InvalidJSONError("Missing closing brace")
        assert error.error_code == "E201"
        assert error.context["details"] == "Missing closing brace"

    def test_invalid_cell_range_error(self):
        """测试单元格范围无效错误"""
        error = InvalidCellRangeError("Z99999")
        assert error.error_code == "E202"
        assert "Z99999" in error.message

    def test_invalid_color_error(self):
        """测试颜色格式错误"""
        error = InvalidColorError("not-a-color")
        assert error.error_code == "E203"
        assert "not-a-color" in error.message

    def test_invalid_parameter_error(self):
        """测试参数无效错误"""
        error = InvalidParameterError("test_param", "invalid", "string")
        assert error.error_code == "E204"
        assert error.context["param_name"] == "test_param"
        assert error.context["param_value"] == "invalid"
        assert error.context["expected"] == "string"

    def test_data_range_error(self):
        """测试数据范围错误"""
        error = DataRangeError("age", 150, min_val=0, max_val=120)
        assert error.error_code == "E205"
        assert error.context["value"] == 150
        assert error.context["min"] == 0
        assert error.context["max"] == 120


class TestFormulaErrors:
    """测试公式相关错误"""

    def test_unsupported_formula_error(self):
        """测试不支持的公式错误"""
        error = UnsupportedFormulaError("=CUSTOM_FUNC()")
        assert error.error_code == "E301"
        assert "CUSTOM_FUNC" in error.message

    def test_formula_syntax_error(self):
        """测试公式语法错误"""
        error = FormulaSyntaxError("=SUM(A1:B2", "Missing closing parenthesis")
        assert error.error_code == "E302"
        assert error.context["details"] == "Missing closing parenthesis"

    def test_formula_calculation_error(self):
        """测试公式计算错误"""
        error = FormulaCalculationError("=A1/B1", "Division by zero")
        assert error.error_code == "E303"
        assert error.context["details"] == "Division by zero"


class TestSheetOperationErrors:
    """测试 Sheet 操作错误"""

    def test_sheet_not_found_error(self):
        """测试 Sheet 不存在错误"""
        error = SheetNotFoundError("NonExistent", ["Sheet1", "Sheet2"])
        assert error.error_code == "E401"
        assert "NonExistent" in error.message
        assert error.context["available_sheets"] == ["Sheet1", "Sheet2"]

    def test_sheet_already_exists_error(self):
        """测试 Sheet 已存在错误"""
        error = SheetAlreadyExistsError("Sheet1")
        assert error.error_code == "E402"
        assert "Sheet1" in error.message


class TestNetworkErrors:
    """测试网络和超时错误"""

    def test_supabase_network_error(self):
        """测试 Supabase 网络错误"""
        error = SupabaseNetworkError("Connection timeout")
        assert error.error_code == "E501"
        assert error.context["details"] == "Connection timeout"

    def test_timeout_error(self):
        """测试操作超时错误"""
        error = TimeoutError("upload_file", 30)
        assert error.error_code == "E502"
        assert error.context["operation"] == "upload_file"
        assert error.context["timeout_seconds"] == 30


class TestErrorMessages:
    """测试错误消息模板"""

    def test_error_messages_dict(self):
        """测试错误消息字典完整性"""
        # 确保所有错误代码都有对应的消息
        expected_codes = [
            "E001",
            "E002",
            "E101",
            "E102",
            "E103",
            "E104",
            "E105",
            "E106",
            "E201",
            "E202",
            "E203",
            "E204",
            "E205",
            "E301",
            "E302",
            "E303",
            "E401",
            "E402",
            "E501",
            "E502",
        ]

        for code in expected_codes:
            assert code in ERROR_MESSAGES
            assert isinstance(ERROR_MESSAGES[code], str)
            assert len(ERROR_MESSAGES[code]) > 0

    def test_get_error_message(self):
        """测试获取错误消息函数"""
        assert get_error_message("E001") == "环境变量未设置"
        assert get_error_message("E101") == "文件不存在"
        assert get_error_message("E999") == "未知错误"
