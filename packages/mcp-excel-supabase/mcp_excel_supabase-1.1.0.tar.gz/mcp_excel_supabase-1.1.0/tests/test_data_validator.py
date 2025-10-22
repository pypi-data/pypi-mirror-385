"""
测试数据验证器模块
"""

import pytest
from pydantic import ValidationError as PydanticValidationError

from src.mcp_excel_supabase.excel.data_validator import DataValidator
from src.mcp_excel_supabase.excel.schemas import (
    Workbook,
    Sheet,
    Cell,
    CellFormat,
    FontFormat,
    MergedCell,
)
from src.mcp_excel_supabase.utils.errors import ValidationError


class TestDataValidator:
    """测试 DataValidator 类"""

    def test_validate_workbook_with_dict(self):
        """测试验证工作簿数据（字典输入）"""
        data = {
            "sheets": [
                {
                    "name": "Sheet1",
                    "rows": [],
                }
            ],
            "metadata": {},
        }

        workbook = DataValidator.validate_workbook(data)
        assert isinstance(workbook, Workbook)
        assert len(workbook.sheets) == 1
        assert workbook.sheets[0].name == "Sheet1"

    def test_validate_workbook_with_object(self):
        """测试验证工作簿数据（Workbook 对象输入）"""
        sheet = Sheet(name="Sheet1", rows=[])
        workbook = Workbook(sheets=[sheet])

        result = DataValidator.validate_workbook(workbook)
        assert result is workbook

    def test_validate_workbook_invalid_data(self):
        """测试验证无效的工作簿数据"""
        data = {
            "sheets": [],  # 工作簿必须至少包含一个工作表
            "metadata": {},
        }

        with pytest.raises(ValidationError) as exc_info:
            DataValidator.validate_workbook(data)

        assert exc_info.value.error_code == "E201"
        assert "工作簿数据验证失败" in exc_info.value.message

    def test_validate_sheet_with_dict(self):
        """测试验证工作表数据（字典输入）"""
        data = {
            "name": "TestSheet",
            "rows": [],
        }

        sheet = DataValidator.validate_sheet(data)
        assert isinstance(sheet, Sheet)
        assert sheet.name == "TestSheet"

    def test_validate_sheet_with_object(self):
        """测试验证工作表数据（Sheet 对象输入）"""
        sheet = Sheet(name="TestSheet", rows=[])

        result = DataValidator.validate_sheet(sheet)
        assert result is sheet

    def test_validate_sheet_invalid_name(self):
        """测试验证无效的工作表名称"""
        data = {
            "name": "Sheet:Invalid",  # 包含非法字符
            "rows": [],
        }

        with pytest.raises(ValidationError) as exc_info:
            DataValidator.validate_sheet(data)

        assert exc_info.value.error_code == "E201"

    def test_validate_cell_with_dict(self):
        """测试验证单元格数据（字典输入）"""
        data = {
            "value": "Test",
            "data_type": "string",
            "row": 1,
            "column": 1,
        }

        cell = DataValidator.validate_cell(data)
        assert isinstance(cell, Cell)
        assert cell.value == "Test"
        assert cell.data_type == "string"

    def test_validate_cell_with_object(self):
        """测试验证单元格数据（Cell 对象输入）"""
        cell = Cell(value="Test", data_type="string", row=1, column=1)

        result = DataValidator.validate_cell(cell)
        assert result is cell

    def test_validate_cell_invalid_data_type(self):
        """测试验证无效的数据类型"""
        data = {
            "value": "Test",
            "data_type": "invalid_type",  # 无效的数据类型
            "row": 1,
            "column": 1,
        }

        with pytest.raises(ValidationError) as exc_info:
            DataValidator.validate_cell(data)

        assert exc_info.value.error_code == "E201"

    def test_validate_cell_format_with_dict(self):
        """测试验证单元格格式数据（字典输入）"""
        data = {
            "font": {
                "name": "Arial",
                "size": 12,
                "bold": True,
            }
        }

        cell_format = DataValidator.validate_cell_format(data)
        assert isinstance(cell_format, CellFormat)
        assert cell_format.font.name == "Arial"

    def test_validate_cell_format_with_object(self):
        """测试验证单元格格式数据（CellFormat 对象输入）"""
        font = FontFormat(name="Arial", size=12)
        cell_format = CellFormat(font=font)

        result = DataValidator.validate_cell_format(cell_format)
        assert result is cell_format

    def test_validate_merged_cell_with_dict(self):
        """测试验证合并单元格数据（字典输入）"""
        data = {
            "start_row": 1,
            "start_column": 1,
            "end_row": 2,
            "end_column": 2,
        }

        merged_cell = DataValidator.validate_merged_cell(data)
        assert isinstance(merged_cell, MergedCell)
        assert merged_cell.start_row == 1
        assert merged_cell.end_row == 2

    def test_validate_merged_cell_invalid_range(self):
        """测试验证无效的合并单元格范围"""
        data = {
            "start_row": 2,
            "start_column": 1,
            "end_row": 1,  # 结束行小于起始行
            "end_column": 2,
        }

        with pytest.raises(ValidationError) as exc_info:
            DataValidator.validate_merged_cell(data)

        assert exc_info.value.error_code == "E201"

    def test_validate_data_type_null(self):
        """测试验证 null 数据类型"""
        assert DataValidator.validate_data_type(None, "null") is True
        assert DataValidator.validate_data_type("test", "null") is False

    def test_validate_data_type_string(self):
        """测试验证 string 数据类型"""
        assert DataValidator.validate_data_type("test", "string") is True
        assert DataValidator.validate_data_type(123, "string") is False

    def test_validate_data_type_number(self):
        """测试验证 number 数据类型"""
        assert DataValidator.validate_data_type(123, "number") is True
        assert DataValidator.validate_data_type(123.45, "number") is True
        assert DataValidator.validate_data_type(True, "number") is False  # bool 不是 number
        assert DataValidator.validate_data_type("123", "number") is False

    def test_validate_data_type_boolean(self):
        """测试验证 boolean 数据类型"""
        assert DataValidator.validate_data_type(True, "boolean") is True
        assert DataValidator.validate_data_type(False, "boolean") is True
        assert DataValidator.validate_data_type(1, "boolean") is False

    def test_validate_data_type_formula(self):
        """测试验证 formula 数据类型"""
        assert DataValidator.validate_data_type("=SUM(A1:A10)", "formula") is True
        assert DataValidator.validate_data_type("SUM(A1:A10)", "formula") is False  # 不以 = 开头

    def test_validate_data_type_date(self):
        """测试验证 date 数据类型"""
        assert DataValidator.validate_data_type("2023-01-01", "date") is True
        assert DataValidator.validate_data_type(44927, "date") is True  # Excel 日期序列号
        assert DataValidator.validate_data_type(None, "date") is False

    def test_format_validation_error(self):
        """测试格式化验证错误"""
        try:
            # 触发一个验证错误
            Cell(value="test", data_type="invalid", row=1, column=1)
        except PydanticValidationError as e:
            formatted = DataValidator._format_validation_error(e)
            assert isinstance(formatted, list)
            assert len(formatted) > 0
            assert "field" in formatted[0]
            assert "message" in formatted[0]
            assert "type" in formatted[0]
