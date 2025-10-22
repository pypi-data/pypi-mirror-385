"""
测试输入验证工具模块
"""

import pytest
from pathlib import Path
from mcp_excel_supabase.utils.validator import Validator, validate_excel_file
from mcp_excel_supabase.utils.errors import (
    FileNotFoundError,
    FileSizeError,
    InvalidParameterError,
    DataRangeError,
    InvalidCellRangeError,
    InvalidColorError,
    BatchLimitError,
)


class TestValidateFilePath:
    """测试文件路径验证"""

    def test_validate_existing_file(self, temp_file):
        """测试验证存在的文件"""
        result = Validator.validate_file_path(temp_file, must_exist=True)
        assert isinstance(result, Path)
        assert result == temp_file

    def test_validate_non_existing_file_allowed(self, temp_dir):
        """测试验证不存在的文件（允许）"""
        non_existing = temp_dir / "non_existing.txt"
        result = Validator.validate_file_path(non_existing, must_exist=False)
        assert isinstance(result, Path)

    def test_validate_non_existing_file_not_allowed(self, temp_dir):
        """测试验证不存在的文件（不允许）"""
        non_existing = temp_dir / "non_existing.txt"
        with pytest.raises(FileNotFoundError) as exc_info:
            Validator.validate_file_path(non_existing, must_exist=True)
        assert exc_info.value.error_code == "E101"

    def test_validate_file_with_extension(self, temp_dir):
        """测试验证文件扩展名"""
        xlsx_file = temp_dir / "test.xlsx"
        xlsx_file.write_text("test")

        result = Validator.validate_file_path(xlsx_file, extensions=[".xlsx", ".xls"])
        assert result == xlsx_file

    def test_validate_file_wrong_extension(self, temp_file):
        """测试验证错误的文件扩展名"""
        with pytest.raises(InvalidParameterError) as exc_info:
            Validator.validate_file_path(temp_file, extensions=[".xlsx", ".xls"])
        assert exc_info.value.error_code == "E204"

    def test_validate_empty_path(self):
        """测试验证空路径"""
        with pytest.raises(InvalidParameterError):
            Validator.validate_file_path("")


class TestValidateFileSize:
    """测试文件大小验证"""

    def test_validate_small_file(self, temp_file):
        """测试验证小文件"""
        size = Validator.validate_file_size(temp_file, max_size_mb=1.0)
        assert size < 1.0

    def test_validate_large_file(self, temp_dir):
        """测试验证大文件"""
        large_file = temp_dir / "large.txt"
        # 创建一个 2MB 的文件
        large_file.write_bytes(b"x" * (2 * 1024 * 1024))

        with pytest.raises(FileSizeError) as exc_info:
            Validator.validate_file_size(large_file, max_size_mb=1.0)
        assert exc_info.value.error_code == "E102"

    def test_validate_non_existing_file_size(self, temp_dir):
        """测试验证不存在文件的大小"""
        non_existing = temp_dir / "non_existing.txt"
        with pytest.raises(FileNotFoundError):
            Validator.validate_file_size(non_existing)


class TestValidateBatchSize:
    """测试批量操作数量验证"""

    def test_validate_within_limit(self):
        """测试在限制内的数量"""
        result = Validator.validate_batch_size(10, max_count=20)
        assert result == 10

    def test_validate_at_limit(self):
        """测试刚好达到限制的数量"""
        result = Validator.validate_batch_size(20, max_count=20)
        assert result == 20

    def test_validate_exceed_limit(self):
        """测试超过限制的数量"""
        with pytest.raises(BatchLimitError) as exc_info:
            Validator.validate_batch_size(25, max_count=20)
        assert exc_info.value.error_code == "E103"


class TestValidateType:
    """测试参数类型验证"""

    def test_validate_correct_type(self):
        """测试正确的类型"""
        result = Validator.validate_type("test", str, "param")
        assert result == "test"

    def test_validate_wrong_type(self):
        """测试错误的类型"""
        with pytest.raises(InvalidParameterError) as exc_info:
            Validator.validate_type(123, str, "param")
        assert exc_info.value.error_code == "E204"

    def test_validate_multiple_types(self):
        """测试多个允许的类型"""
        result1 = Validator.validate_type("test", (str, int), "param")
        assert result1 == "test"

        result2 = Validator.validate_type(123, (str, int), "param")
        assert result2 == 123


class TestValidateRange:
    """测试数值范围验证"""

    def test_validate_within_range(self):
        """测试在范围内的值"""
        result = Validator.validate_range(50, "value", min_val=0, max_val=100)
        assert result == 50

    def test_validate_at_min_boundary(self):
        """测试最小边界值"""
        result = Validator.validate_range(0, "value", min_val=0, max_val=100)
        assert result == 0

    def test_validate_at_max_boundary(self):
        """测试最大边界值"""
        result = Validator.validate_range(100, "value", min_val=0, max_val=100)
        assert result == 100

    def test_validate_below_min(self):
        """测试低于最小值"""
        with pytest.raises(DataRangeError) as exc_info:
            Validator.validate_range(-1, "value", min_val=0, max_val=100)
        assert exc_info.value.error_code == "E205"

    def test_validate_above_max(self):
        """测试高于最大值"""
        with pytest.raises(DataRangeError) as exc_info:
            Validator.validate_range(101, "value", min_val=0, max_val=100)
        assert exc_info.value.error_code == "E205"

    def test_validate_no_min(self):
        """测试无最小值限制"""
        result = Validator.validate_range(-1000, "value", max_val=100)
        assert result == -1000

    def test_validate_no_max(self):
        """测试无最大值限制"""
        result = Validator.validate_range(1000, "value", min_val=0)
        assert result == 1000


class TestValidateCellRange:
    """测试单元格范围验证"""

    def test_validate_single_cell(self):
        """测试单个单元格"""
        result = Validator.validate_cell_range("A1")
        assert result["sheet"] is None
        assert result["start_cell"] == "A1"
        assert result["end_cell"] is None

    def test_validate_cell_range(self):
        """测试单元格范围"""
        result = Validator.validate_cell_range("A1:B10")
        assert result["sheet"] is None
        assert result["start_cell"] == "A1"
        assert result["end_cell"] == "B10"

    def test_validate_cell_range_with_sheet(self):
        """测试带 Sheet 名称的单元格范围"""
        result = Validator.validate_cell_range("Sheet1!A1:B10")
        assert result["sheet"] == "Sheet1"
        assert result["start_cell"] == "A1"
        assert result["end_cell"] == "B10"

    def test_validate_lowercase_cell_range(self):
        """测试小写单元格范围"""
        result = Validator.validate_cell_range("a1:b10")
        assert result["start_cell"] == "A1"
        assert result["end_cell"] == "B10"

    def test_validate_invalid_cell_range(self):
        """测试无效的单元格范围"""
        with pytest.raises(InvalidCellRangeError) as exc_info:
            Validator.validate_cell_range("invalid")
        assert exc_info.value.error_code == "E202"

    def test_validate_empty_cell_range(self):
        """测试空单元格范围"""
        with pytest.raises(InvalidCellRangeError):
            Validator.validate_cell_range("")


class TestValidateColor:
    """测试颜色格式验证"""

    def test_validate_hex_color_6_digits(self):
        """测试 6 位十六进制颜色"""
        result = Validator.validate_color("#FF0000")
        assert result == "#FF0000"

    def test_validate_hex_color_3_digits(self):
        """测试 3 位十六进制颜色"""
        result = Validator.validate_color("#F00")
        assert result == "#FF0000"

    def test_validate_lowercase_hex_color(self):
        """测试小写十六进制颜色"""
        result = Validator.validate_color("#ff0000")
        assert result == "#FF0000"

    def test_validate_color_name(self):
        """测试颜色名称"""
        result = Validator.validate_color("red")
        assert result == "red"

    def test_validate_uppercase_color_name(self):
        """测试大写颜色名称"""
        result = Validator.validate_color("RED")
        assert result == "red"

    def test_validate_invalid_color(self):
        """测试无效颜色"""
        with pytest.raises(InvalidColorError) as exc_info:
            Validator.validate_color("not-a-color")
        assert exc_info.value.error_code == "E203"

    def test_validate_invalid_hex_color(self):
        """测试无效的十六进制颜色"""
        with pytest.raises(InvalidColorError):
            Validator.validate_color("#GGGGGG")


class TestValidateSheetName:
    """测试 Sheet 名称验证"""

    def test_validate_valid_sheet_name(self):
        """测试有效的 Sheet 名称"""
        result = Validator.validate_sheet_name("Sheet1")
        assert result == "Sheet1"

    def test_validate_sheet_name_with_spaces(self):
        """测试带空格的 Sheet 名称"""
        result = Validator.validate_sheet_name("  Sheet 1  ")
        assert result == "Sheet 1"

    def test_validate_empty_sheet_name(self):
        """测试空 Sheet 名称"""
        with pytest.raises(InvalidParameterError):
            Validator.validate_sheet_name("")

    def test_validate_sheet_name_with_invalid_chars(self):
        """测试包含无效字符的 Sheet 名称"""
        invalid_chars = [":", "\\", "/", "?", "*", "[", "]"]
        for char in invalid_chars:
            with pytest.raises(InvalidParameterError):
                Validator.validate_sheet_name(f"Sheet{char}1")

    def test_validate_long_sheet_name(self):
        """测试过长的 Sheet 名称"""
        long_name = "A" * 32
        with pytest.raises(InvalidParameterError):
            Validator.validate_sheet_name(long_name)

    def test_validate_max_length_sheet_name(self):
        """测试最大长度的 Sheet 名称"""
        max_name = "A" * 31
        result = Validator.validate_sheet_name(max_name)
        assert result == max_name


class TestValidateNonEmpty:
    """测试非空验证"""

    def test_validate_non_empty_string(self):
        """测试非空字符串"""
        result = Validator.validate_non_empty("test", "param")
        assert result == "test"

    def test_validate_empty_string(self):
        """测试空字符串"""
        with pytest.raises(InvalidParameterError):
            Validator.validate_non_empty("", "param")

    def test_validate_none(self):
        """测试 None 值"""
        with pytest.raises(InvalidParameterError):
            Validator.validate_non_empty(None, "param")

    def test_validate_empty_list(self):
        """测试空列表"""
        with pytest.raises(InvalidParameterError):
            Validator.validate_non_empty([], "param")

    def test_validate_non_empty_list(self):
        """测试非空列表"""
        result = Validator.validate_non_empty([1, 2, 3], "param")
        assert result == [1, 2, 3]


class TestValidateExcelFile:
    """测试 Excel 文件验证（组合验证）"""

    def test_validate_valid_excel_file(self, simple_excel_file):
        """测试有效的 Excel 文件"""
        result = validate_excel_file(simple_excel_file)
        assert isinstance(result, Path)
        assert result == simple_excel_file

    def test_validate_non_excel_file(self, temp_file):
        """测试非 Excel 文件"""
        with pytest.raises(InvalidParameterError):
            validate_excel_file(temp_file)

    def test_validate_non_existing_excel_file(self, temp_dir):
        """测试不存在的 Excel 文件"""
        non_existing = temp_dir / "non_existing.xlsx"
        with pytest.raises(FileNotFoundError):
            validate_excel_file(non_existing)
