"""
测试 Excel 生成器模块
"""

import pytest
from pathlib import Path
import tempfile
import shutil

from src.mcp_excel_supabase.excel.generator import ExcelGenerator
from src.mcp_excel_supabase.excel.parser import ExcelParser
from src.mcp_excel_supabase.excel.schemas import (
    Workbook,
    Sheet,
    Row,
    Cell,
    CellFormat,
    FontFormat,
    FillFormat,
    AlignmentFormat,
    MergedCell,
)
from src.mcp_excel_supabase.utils.errors import FileWriteError


class TestExcelGenerator:
    """测试 ExcelGenerator 类"""

    @pytest.fixture
    def temp_dir(self):
        """创建临时目录"""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def generator(self):
        """创建生成器实例"""
        return ExcelGenerator()

    @pytest.fixture
    def parser(self):
        """创建解析器实例"""
        return ExcelParser()

    @pytest.fixture
    def simple_workbook(self):
        """创建简单的工作簿"""
        cell1 = Cell(value="Name", data_type="string", row=1, column=1)
        cell2 = Cell(value="Age", data_type="string", row=1, column=2)
        cell3 = Cell(value="Alice", data_type="string", row=2, column=1)
        cell4 = Cell(value=30, data_type="number", row=2, column=2)

        row1 = Row(cells=[cell1, cell2])
        row2 = Row(cells=[cell3, cell4])

        sheet = Sheet(name="People", rows=[row1, row2])
        workbook = Workbook(sheets=[sheet])

        return workbook

    def test_generate_simple_file(self, generator, temp_dir, simple_workbook):
        """测试生成简单的 Excel 文件"""
        output_path = temp_dir / "simple.xlsx"

        result_path = generator.generate_file(simple_workbook, output_path)

        assert result_path.exists()
        assert result_path == output_path

    def test_generate_file_overwrite_false(self, generator, temp_dir, simple_workbook):
        """测试生成文件（不覆盖已存在的文件）"""
        output_path = temp_dir / "test.xlsx"

        # 第一次生成
        generator.generate_file(simple_workbook, output_path)

        # 第二次生成（不覆盖）
        with pytest.raises(FileWriteError) as exc_info:
            generator.generate_file(simple_workbook, output_path, overwrite=False)

        assert "文件已存在" in str(exc_info.value)

    def test_generate_file_overwrite_true(self, generator, temp_dir, simple_workbook):
        """测试生成文件（覆盖已存在的文件）"""
        output_path = temp_dir / "test.xlsx"

        # 第一次生成
        generator.generate_file(simple_workbook, output_path)

        # 第二次生成（覆盖）
        result_path = generator.generate_file(simple_workbook, output_path, overwrite=True)

        assert result_path.exists()

    def test_generate_file_with_formats(self, generator, temp_dir):
        """测试生成带格式的 Excel 文件"""
        # 创建带格式的单元格
        cell_format = CellFormat(
            font=FontFormat(name="Arial", size=14, bold=True, color="#FF0000"),
            fill=FillFormat(background_color="#FFFF00", pattern_type="solid"),
            alignment=AlignmentFormat(horizontal="center", vertical="center"),
        )

        cell = Cell(
            value="Formatted Cell",
            data_type="string",
            row=1,
            column=1,
            format=cell_format,
        )

        row = Row(cells=[cell])
        sheet = Sheet(name="Formatted", rows=[row])
        workbook = Workbook(sheets=[sheet])

        output_path = temp_dir / "formatted.xlsx"
        result_path = generator.generate_file(workbook, output_path)

        assert result_path.exists()

    def test_generate_file_with_merged_cells(self, generator, temp_dir):
        """测试生成包含合并单元格的 Excel 文件"""
        cell = Cell(value="Merged", data_type="string", row=1, column=1)
        row = Row(cells=[cell])

        merged_cell = MergedCell(start_row=1, start_column=1, end_row=2, end_column=2)

        sheet = Sheet(name="Merged", rows=[row], merged_cells=[merged_cell])
        workbook = Workbook(sheets=[sheet])

        output_path = temp_dir / "merged.xlsx"
        result_path = generator.generate_file(workbook, output_path)

        assert result_path.exists()

    def test_generate_file_with_column_widths(self, generator, temp_dir):
        """测试生成包含列宽设置的 Excel 文件"""
        cell = Cell(value="Wide Column", data_type="string", row=1, column=1)
        row = Row(cells=[cell])

        column_widths = {1: 20.0, 2: 15.0}

        sheet = Sheet(name="Widths", rows=[row], column_widths=column_widths)
        workbook = Workbook(sheets=[sheet])

        output_path = temp_dir / "widths.xlsx"
        result_path = generator.generate_file(workbook, output_path)

        assert result_path.exists()

    def test_generate_file_with_row_heights(self, generator, temp_dir):
        """测试生成包含行高设置的 Excel 文件"""
        cell = Cell(value="Tall Row", data_type="string", row=1, column=1)
        row = Row(cells=[cell], height=30.0)

        sheet = Sheet(name="Heights", rows=[row])
        workbook = Workbook(sheets=[sheet])

        output_path = temp_dir / "heights.xlsx"
        result_path = generator.generate_file(workbook, output_path)

        assert result_path.exists()

    def test_generate_file_with_formula(self, generator, temp_dir):
        """测试生成包含公式的 Excel 文件"""
        cell1 = Cell(value=10, data_type="number", row=1, column=1)
        cell2 = Cell(value=20, data_type="number", row=2, column=1)
        cell3 = Cell(value="=SUM(A1:A2)", data_type="formula", row=3, column=1)

        row1 = Row(cells=[cell1])
        row2 = Row(cells=[cell2])
        row3 = Row(cells=[cell3])

        sheet = Sheet(name="Formula", rows=[row1, row2, row3])
        workbook = Workbook(sheets=[sheet])

        output_path = temp_dir / "formula.xlsx"
        result_path = generator.generate_file(workbook, output_path)

        assert result_path.exists()

    def test_generate_multi_sheet_file(self, generator, temp_dir):
        """测试生成多工作表 Excel 文件"""
        sheet1 = Sheet(
            name="Sheet1",
            rows=[Row(cells=[Cell(value="Data1", data_type="string", row=1, column=1)])],
        )
        sheet2 = Sheet(
            name="Sheet2",
            rows=[Row(cells=[Cell(value="Data2", data_type="string", row=1, column=1)])],
        )

        workbook = Workbook(sheets=[sheet1, sheet2])

        output_path = temp_dir / "multi_sheet.xlsx"
        result_path = generator.generate_file(workbook, output_path)

        assert result_path.exists()

    def test_roundtrip_simple(self, generator, parser, temp_dir, simple_workbook):
        """测试往返转换（简单数据）"""
        output_path = temp_dir / "roundtrip_simple.xlsx"

        # 生成 Excel 文件
        generator.generate_file(simple_workbook, output_path)

        # 解析 Excel 文件
        parsed_workbook = parser.parse_file(output_path)

        # 验证数据
        assert len(parsed_workbook.sheets) == 1
        assert parsed_workbook.sheets[0].name == "People"
        assert len(parsed_workbook.sheets[0].rows) == 2

        # 验证第一行数据
        row1_cells = parsed_workbook.sheets[0].rows[0].cells
        assert len(row1_cells) == 2
        assert row1_cells[0].value == "Name"
        assert row1_cells[1].value == "Age"

    def test_roundtrip_with_formats(self, generator, parser, temp_dir):
        """测试往返转换（带格式）"""
        # 创建带格式的工作簿
        cell_format = CellFormat(
            font=FontFormat(name="Arial", size=14, bold=True, color="#FF0000"),
            fill=FillFormat(background_color="#FFFF00"),
        )

        cell = Cell(
            value="Formatted",
            data_type="string",
            row=1,
            column=1,
            format=cell_format,
        )

        row = Row(cells=[cell])
        sheet = Sheet(name="Test", rows=[row])
        workbook = Workbook(sheets=[sheet])

        output_path = temp_dir / "roundtrip_format.xlsx"

        # 生成并解析
        generator.generate_file(workbook, output_path)
        parsed_workbook = parser.parse_file(output_path)

        # 验证格式
        parsed_cell = parsed_workbook.sheets[0].rows[0].cells[0]
        assert parsed_cell.format is not None
        assert parsed_cell.format.font is not None
        assert parsed_cell.format.font.name == "Arial"
        assert parsed_cell.format.font.size == 14
        assert parsed_cell.format.font.bold is True
        assert parsed_cell.format.fill is not None
        assert parsed_cell.format.fill.background_color == "#FFFF00"

    def test_roundtrip_with_merged_cells(self, generator, parser, temp_dir):
        """测试往返转换（合并单元格）"""
        cell = Cell(value="Merged", data_type="string", row=1, column=1)
        row = Row(cells=[cell])
        merged_cell = MergedCell(start_row=1, start_column=1, end_row=2, end_column=2)

        sheet = Sheet(name="Test", rows=[row], merged_cells=[merged_cell])
        workbook = Workbook(sheets=[sheet])

        output_path = temp_dir / "roundtrip_merged.xlsx"

        # 生成并解析
        generator.generate_file(workbook, output_path)
        parsed_workbook = parser.parse_file(output_path)

        # 验证合并单元格
        assert len(parsed_workbook.sheets[0].merged_cells) == 1
        parsed_merged = parsed_workbook.sheets[0].merged_cells[0]
        assert parsed_merged.start_row == 1
        assert parsed_merged.start_column == 1
        assert parsed_merged.end_row == 2
        assert parsed_merged.end_column == 2
