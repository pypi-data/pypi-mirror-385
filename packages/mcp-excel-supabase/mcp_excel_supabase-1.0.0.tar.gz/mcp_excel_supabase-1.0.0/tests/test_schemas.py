"""
测试 Excel 数据模型（schemas.py）
"""

import pytest
from pydantic import ValidationError

from mcp_excel_supabase.excel.schemas import (
    AlignmentFormat,
    BorderFormat,
    BorderSide,
    Cell,
    CellFormat,
    FillFormat,
    FontFormat,
    MergedCell,
    Row,
    Sheet,
    Workbook,
)


# ============================================================================
# 测试字体格式
# ============================================================================


class TestFontFormat:
    """测试 FontFormat 模型"""

    def test_create_font_format(self) -> None:
        """测试创建字体格式"""
        font = FontFormat(
            name="Arial", size=12, bold=True, italic=False, underline="single", color="#FF0000"
        )
        assert font.name == "Arial"
        assert font.size == 12
        assert font.bold is True
        assert font.italic is False
        assert font.underline == "single"
        assert font.color == "#FF0000"

    def test_font_format_optional_fields(self) -> None:
        """测试字体格式的可选字段"""
        font = FontFormat()
        assert font.name is None
        assert font.size is None
        assert font.bold is None

    def test_font_color_validation(self) -> None:
        """测试字体颜色验证（自动添加#）"""
        font = FontFormat(color="FF0000")
        assert font.color == "#FF0000"


# ============================================================================
# 测试填充格式
# ============================================================================


class TestFillFormat:
    """测试 FillFormat 模型"""

    def test_create_fill_format(self) -> None:
        """测试创建填充格式"""
        fill = FillFormat(background_color="#FFFF00", pattern_type="solid")
        assert fill.background_color == "#FFFF00"
        assert fill.pattern_type == "solid"

    def test_fill_color_validation(self) -> None:
        """测试填充颜色验证"""
        fill = FillFormat(background_color="FFFF00")
        assert fill.background_color == "#FFFF00"


# ============================================================================
# 测试边框格式
# ============================================================================


class TestBorderFormat:
    """测试 BorderFormat 模型"""

    def test_create_border_side(self) -> None:
        """测试创建边框单边"""
        side = BorderSide(style="thin", color="#000000")
        assert side.style == "thin"
        assert side.color == "#000000"

    def test_create_border_format(self) -> None:
        """测试创建边框格式"""
        border = BorderFormat(
            top=BorderSide(style="thin", color="#000000"),
            bottom=BorderSide(style="medium", color="#FF0000"),
        )
        assert border.top is not None
        assert border.top.style == "thin"
        assert border.bottom is not None
        assert border.bottom.style == "medium"


# ============================================================================
# 测试对齐格式
# ============================================================================


class TestAlignmentFormat:
    """测试 AlignmentFormat 模型"""

    def test_create_alignment_format(self) -> None:
        """测试创建对齐格式"""
        alignment = AlignmentFormat(horizontal="center", vertical="top", wrap_text=True)
        assert alignment.horizontal == "center"
        assert alignment.vertical == "top"
        assert alignment.wrap_text is True


# ============================================================================
# 测试单元格格式
# ============================================================================


class TestCellFormat:
    """测试 CellFormat 模型"""

    def test_create_cell_format(self) -> None:
        """测试创建单元格格式"""
        cell_format = CellFormat(
            font=FontFormat(name="Arial", size=12, bold=True),
            fill=FillFormat(background_color="#FFFF00"),
            border=BorderFormat(top=BorderSide(style="thin")),
            alignment=AlignmentFormat(horizontal="center"),
            number_format="0.00",
        )
        assert cell_format.font is not None
        assert cell_format.font.name == "Arial"
        assert cell_format.fill is not None
        assert cell_format.fill.background_color == "#FFFF00"
        assert cell_format.number_format == "0.00"


# ============================================================================
# 测试单元格
# ============================================================================


class TestCell:
    """测试 Cell 模型"""

    def test_create_cell_with_string(self) -> None:
        """测试创建字符串单元格"""
        cell = Cell(value="Hello", data_type="string", row=1, column=1)
        assert cell.value == "Hello"
        assert cell.data_type == "string"
        assert cell.row == 1
        assert cell.column == 1

    def test_create_cell_with_number(self) -> None:
        """测试创建数字单元格"""
        cell = Cell(value=123.45, data_type="number", row=2, column=3)
        assert cell.value == 123.45
        assert cell.data_type == "number"

    def test_create_cell_with_boolean(self) -> None:
        """测试创建布尔单元格"""
        cell = Cell(value=True, data_type="boolean", row=1, column=1)
        assert cell.value is True
        assert cell.data_type == "boolean"

    def test_create_cell_with_null(self) -> None:
        """测试创建空单元格"""
        cell = Cell(value=None, data_type="null", row=1, column=1)
        assert cell.value is None
        assert cell.data_type == "null"

    def test_cell_with_format(self) -> None:
        """测试带格式的单元格"""
        cell = Cell(
            value="Formatted",
            data_type="string",
            row=1,
            column=1,
            format=CellFormat(font=FontFormat(bold=True)),
        )
        assert cell.format is not None
        assert cell.format.font is not None
        assert cell.format.font.bold is True

    def test_invalid_data_type(self) -> None:
        """测试无效的数据类型"""
        with pytest.raises(ValidationError):
            Cell(value="test", data_type="invalid_type", row=1, column=1)


# ============================================================================
# 测试行
# ============================================================================


class TestRow:
    """测试 Row 模型"""

    def test_create_row(self) -> None:
        """测试创建行"""
        row = Row(
            cells=[
                Cell(value="A", data_type="string", row=1, column=1),
                Cell(value="B", data_type="string", row=1, column=2),
            ],
            height=20.0,
        )
        assert len(row.cells) == 2
        assert row.height == 20.0

    def test_empty_row(self) -> None:
        """测试空行"""
        row = Row()
        assert len(row.cells) == 0
        assert row.height is None


# ============================================================================
# 测试合并单元格
# ============================================================================


class TestMergedCell:
    """测试 MergedCell 模型"""

    def test_create_merged_cell(self) -> None:
        """测试创建合并单元格"""
        merged = MergedCell(start_row=1, start_column=1, end_row=3, end_column=3)
        assert merged.start_row == 1
        assert merged.start_column == 1
        assert merged.end_row == 3
        assert merged.end_column == 3

    def test_invalid_end_row(self) -> None:
        """测试无效的结束行号"""
        with pytest.raises(ValidationError):
            MergedCell(start_row=3, start_column=1, end_row=1, end_column=3)

    def test_invalid_end_column(self) -> None:
        """测试无效的结束列号"""
        with pytest.raises(ValidationError):
            MergedCell(start_row=1, start_column=3, end_row=3, end_column=1)


# ============================================================================
# 测试工作表
# ============================================================================


class TestSheet:
    """测试 Sheet 模型"""

    def test_create_sheet(self) -> None:
        """测试创建工作表"""
        sheet = Sheet(
            name="Sheet1",
            rows=[
                Row(cells=[Cell(value="A1", data_type="string", row=1, column=1)]),
            ],
            merged_cells=[MergedCell(start_row=1, start_column=1, end_row=2, end_column=2)],
            column_widths={1: 15.0, 2: 20.0},
        )
        assert sheet.name == "Sheet1"
        assert len(sheet.rows) == 1
        assert len(sheet.merged_cells) == 1
        assert sheet.column_widths[1] == 15.0

    def test_empty_sheet_name(self) -> None:
        """测试空工作表名称"""
        with pytest.raises(ValidationError):
            Sheet(name="")

    def test_sheet_name_too_long(self) -> None:
        """测试工作表名称过长"""
        with pytest.raises(ValidationError):
            Sheet(name="A" * 32)

    def test_sheet_name_invalid_chars(self) -> None:
        """测试工作表名称包含无效字符"""
        invalid_names = ["Sheet:1", "Sheet\\1", "Sheet/1", "Sheet?1", "Sheet*1", "Sheet[1]"]
        for name in invalid_names:
            with pytest.raises(ValidationError):
                Sheet(name=name)


# ============================================================================
# 测试工作簿
# ============================================================================


class TestWorkbook:
    """测试 Workbook 模型"""

    def test_create_workbook(self) -> None:
        """测试创建工作簿"""
        workbook = Workbook(
            sheets=[
                Sheet(name="Sheet1"),
                Sheet(name="Sheet2"),
            ],
            metadata={"filename": "test.xlsx", "created_at": "2025-10-18"},
        )
        assert len(workbook.sheets) == 2
        assert workbook.metadata["filename"] == "test.xlsx"

    def test_empty_workbook(self) -> None:
        """测试空工作簿（必须至少有一个工作表）"""
        with pytest.raises(ValidationError):
            Workbook(sheets=[])

    def test_duplicate_sheet_names(self) -> None:
        """测试重复的工作表名称"""
        with pytest.raises(ValidationError):
            Workbook(
                sheets=[
                    Sheet(name="Sheet1"),
                    Sheet(name="Sheet1"),
                ]
            )

    def test_workbook_serialization(self) -> None:
        """测试工作簿序列化"""
        workbook = Workbook(
            sheets=[Sheet(name="Sheet1")],
            metadata={"filename": "test.xlsx"},
        )
        data = workbook.model_dump()
        assert "sheets" in data
        assert len(data["sheets"]) == 1
        assert data["sheets"][0]["name"] == "Sheet1"
