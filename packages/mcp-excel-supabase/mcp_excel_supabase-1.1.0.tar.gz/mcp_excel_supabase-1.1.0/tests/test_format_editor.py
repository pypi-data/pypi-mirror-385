"""
格式编辑器单元测试
"""

import pytest
from mcp_excel_supabase.excel import (
    Workbook,
    Sheet,
    Row,
    Cell,
    CellFormat,
    FormatEditor,
)
from mcp_excel_supabase.utils.errors import ValidationError


@pytest.fixture
def sample_workbook():
    """创建测试用工作簿"""
    cell1 = Cell(value="A1", data_type="string", row=1, column=1)
    cell2 = Cell(value="B1", data_type="string", row=1, column=2)
    cell3 = Cell(value="A2", data_type="number", row=2, column=1, format=CellFormat())

    row1 = Row(cells=[cell1, cell2])
    row2 = Row(cells=[cell3])

    sheet = Sheet(name="Sheet1", rows=[row1, row2])
    workbook = Workbook(sheets=[sheet])

    return workbook


class TestFormatEditor:
    """格式编辑器测试类"""

    def test_init(self, sample_workbook):
        """测试初始化"""
        editor = FormatEditor(sample_workbook)
        assert editor.workbook == sample_workbook
        assert editor.validator is not None

    def test_get_cell_success(self, sample_workbook):
        """测试获取单元格成功"""
        editor = FormatEditor(sample_workbook)
        cell = editor._get_cell("Sheet1", 1, 1)
        assert cell.value == "A1"
        assert cell.row == 1
        assert cell.column == 1

    def test_get_cell_invalid_sheet(self, sample_workbook):
        """测试获取单元格 - 工作表不存在"""
        editor = FormatEditor(sample_workbook)
        with pytest.raises(ValidationError) as exc_info:
            editor._get_cell("NonExistent", 1, 1)
        assert "不存在" in str(exc_info.value)

    def test_get_cell_invalid_coordinates(self, sample_workbook):
        """测试获取单元格 - 坐标无效"""
        editor = FormatEditor(sample_workbook)
        with pytest.raises(ValidationError):
            editor._get_cell("Sheet1", 10, 10)

    def test_modify_font(self, sample_workbook):
        """测试修改字体格式"""
        editor = FormatEditor(sample_workbook)
        editor.modify_font(
            "Sheet1", 1, 1, name="Arial", size=12.0, bold=True, italic=False, color="#FF0000"
        )

        cell = editor._get_cell("Sheet1", 1, 1)
        assert cell.format is not None
        assert cell.format.font is not None
        assert cell.format.font.name == "Arial"
        assert cell.format.font.size == 12.0
        assert cell.format.font.bold is True
        assert cell.format.font.italic is False
        assert cell.format.font.color == "#FF0000"

    def test_modify_font_partial(self, sample_workbook):
        """测试部分修改字体格式"""
        editor = FormatEditor(sample_workbook)
        editor.modify_font("Sheet1", 1, 1, bold=True)

        cell = editor._get_cell("Sheet1", 1, 1)
        assert cell.format.font.bold is True
        assert cell.format.font.name is None  # 未修改的属性保持 None

    def test_modify_fill(self, sample_workbook):
        """测试修改填充格式"""
        editor = FormatEditor(sample_workbook)
        editor.modify_fill("Sheet1", 1, 1, background_color="#FFFF00", pattern_type="solid")

        cell = editor._get_cell("Sheet1", 1, 1)
        assert cell.format is not None
        assert cell.format.fill is not None
        assert cell.format.fill.background_color == "#FFFF00"
        assert cell.format.fill.pattern_type == "solid"

    def test_modify_border(self, sample_workbook):
        """测试修改边框格式"""
        editor = FormatEditor(sample_workbook)
        editor.modify_border(
            "Sheet1",
            1,
            1,
            top={"style": "thin", "color": "#000000"},
            bottom={"style": "medium", "color": "#FF0000"},
        )

        cell = editor._get_cell("Sheet1", 1, 1)
        assert cell.format is not None
        assert cell.format.border is not None
        assert cell.format.border.top is not None
        assert cell.format.border.top.style == "thin"
        assert cell.format.border.top.color == "#000000"
        assert cell.format.border.bottom is not None
        assert cell.format.border.bottom.style == "medium"

    def test_modify_alignment(self, sample_workbook):
        """测试修改对齐格式"""
        editor = FormatEditor(sample_workbook)
        editor.modify_alignment(
            "Sheet1", 1, 1, horizontal="center", vertical="middle", wrap_text=True
        )

        cell = editor._get_cell("Sheet1", 1, 1)
        assert cell.format is not None
        assert cell.format.alignment is not None
        assert cell.format.alignment.horizontal == "center"
        assert cell.format.alignment.vertical == "middle"
        assert cell.format.alignment.wrap_text is True

    def test_modify_number_format(self, sample_workbook):
        """测试修改数字格式"""
        editor = FormatEditor(sample_workbook)
        editor.modify_number_format("Sheet1", 2, 1, "0.00")

        cell = editor._get_cell("Sheet1", 2, 1)
        assert cell.format is not None
        assert cell.format.number_format == "0.00"

    def test_modify_cell_format(self, sample_workbook):
        """测试一次性修改多个格式"""
        editor = FormatEditor(sample_workbook)
        editor.modify_cell_format(
            "Sheet1",
            1,
            1,
            font={"name": "Arial", "size": 12.0, "bold": True},
            fill={"background_color": "#FFFF00"},
            alignment={"horizontal": "center"},
            number_format="0.00",
        )

        cell = editor._get_cell("Sheet1", 1, 1)
        assert cell.format.font.name == "Arial"
        assert cell.format.font.size == 12.0
        assert cell.format.font.bold is True
        assert cell.format.fill.background_color == "#FFFF00"
        assert cell.format.alignment.horizontal == "center"
        assert cell.format.number_format == "0.00"

    def test_modify_cells_format(self, sample_workbook):
        """测试批量修改单元格格式"""
        editor = FormatEditor(sample_workbook)
        cells = [(1, 1), (1, 2), (2, 1)]
        editor.modify_cells_format("Sheet1", cells, font={"bold": True, "color": "#FF0000"})

        # 验证所有单元格都被修改
        for row, col in cells:
            cell = editor._get_cell("Sheet1", row, col)
            assert cell.format.font.bold is True
            assert cell.format.font.color == "#FF0000"

    def test_modify_font_preserves_existing_format(self, sample_workbook):
        """测试修改字体时保留现有格式"""
        editor = FormatEditor(sample_workbook)

        # 先设置填充格式
        editor.modify_fill("Sheet1", 2, 1, background_color="#FFFF00")

        # 再修改字体格式
        editor.modify_font("Sheet1", 2, 1, bold=True)

        # 验证两种格式都存在
        cell = editor._get_cell("Sheet1", 2, 1)
        assert cell.format.font.bold is True
        assert cell.format.fill.background_color == "#FFFF00"

    def test_modify_font_invalid_size(self, sample_workbook):
        """测试修改字体 - 无效的字体大小"""
        editor = FormatEditor(sample_workbook)
        with pytest.raises(ValidationError):
            editor.modify_font("Sheet1", 1, 1, size=500.0)  # 超过最大值 409

    def test_modify_cells_format_empty_list(self, sample_workbook):
        """测试批量修改 - 空列表"""
        editor = FormatEditor(sample_workbook)
        with pytest.raises(ValidationError):
            editor.modify_cells_format("Sheet1", [], font={"bold": True})
