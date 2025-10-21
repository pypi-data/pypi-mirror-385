"""
行列尺寸调整器单元测试
"""

import pytest
from mcp_excel_supabase.excel import (
    Workbook,
    Sheet,
    Row,
    Cell,
    DimensionAdjuster,
)
from mcp_excel_supabase.utils.errors import ValidationError


@pytest.fixture
def sample_workbook():
    """创建测试用工作簿"""
    cells = []
    for row in range(1, 4):
        for col in range(1, 4):
            value = f"Cell{row}{col}"
            if col == 1:
                value = "Short"
            elif col == 2:
                value = "Medium Length"
            else:
                value = "Very Long Content Here"
            cells.append(Cell(value=value, data_type="string", row=row, column=col))

    rows = []
    for row_num in range(1, 4):
        row_cells = [c for c in cells if c.row == row_num]
        rows.append(Row(cells=row_cells))

    sheet = Sheet(name="Sheet1", rows=rows)
    workbook = Workbook(sheets=[sheet])

    return workbook


class TestDimensionAdjuster:
    """行列尺寸调整器测试类"""

    def test_init(self, sample_workbook):
        """测试初始化"""
        adjuster = DimensionAdjuster(sample_workbook)
        assert adjuster.workbook == sample_workbook
        assert adjuster.validator is not None

    def test_get_sheet_success(self, sample_workbook):
        """测试获取工作表成功"""
        adjuster = DimensionAdjuster(sample_workbook)
        sheet = adjuster._get_sheet("Sheet1")
        assert sheet.name == "Sheet1"

    def test_get_sheet_not_found(self, sample_workbook):
        """测试获取工作表 - 不存在"""
        adjuster = DimensionAdjuster(sample_workbook)
        with pytest.raises(ValidationError) as exc_info:
            adjuster._get_sheet("NonExistent")
        assert "不存在" in str(exc_info.value)

    def test_get_row_success(self, sample_workbook):
        """测试获取行对象成功"""
        adjuster = DimensionAdjuster(sample_workbook)
        sheet = adjuster._get_sheet("Sheet1")
        row = adjuster._get_row(sheet, 1)
        assert row.cells[0].row == 1

    def test_get_row_not_found(self, sample_workbook):
        """测试获取行对象 - 不存在"""
        adjuster = DimensionAdjuster(sample_workbook)
        sheet = adjuster._get_sheet("Sheet1")
        with pytest.raises(ValidationError) as exc_info:
            adjuster._get_row(sheet, 10)
        assert "不存在" in str(exc_info.value)

    def test_set_row_height_success(self, sample_workbook):
        """测试设置行高成功"""
        adjuster = DimensionAdjuster(sample_workbook)
        adjuster.set_row_height("Sheet1", 1, 20.0)

        sheet = adjuster._get_sheet("Sheet1")
        row = adjuster._get_row(sheet, 1)
        assert row.height == 20.0

    def test_set_row_height_invalid_height(self, sample_workbook):
        """测试设置行高 - 无效高度"""
        adjuster = DimensionAdjuster(sample_workbook)

        # 高度过大
        with pytest.raises(ValidationError):
            adjuster.set_row_height("Sheet1", 1, 500.0)

        # 高度为负
        with pytest.raises(ValidationError):
            adjuster.set_row_height("Sheet1", 1, -10.0)

    def test_set_row_heights_batch(self, sample_workbook):
        """测试批量设置行高"""
        adjuster = DimensionAdjuster(sample_workbook)
        heights = {1: 20.0, 2: 25.0, 3: 30.0}
        adjuster.set_row_heights("Sheet1", heights)

        sheet = adjuster._get_sheet("Sheet1")
        for row_num, expected_height in heights.items():
            row = adjuster._get_row(sheet, row_num)
            assert row.height == expected_height

    def test_set_row_heights_empty(self, sample_workbook):
        """测试批量设置行高 - 空字典"""
        adjuster = DimensionAdjuster(sample_workbook)
        with pytest.raises(ValidationError):
            adjuster.set_row_heights("Sheet1", {})

    def test_set_column_width_success(self, sample_workbook):
        """测试设置列宽成功"""
        adjuster = DimensionAdjuster(sample_workbook)
        adjuster.set_column_width("Sheet1", 1, 15.0)

        sheet = adjuster._get_sheet("Sheet1")
        assert sheet.column_widths[1] == 15.0

    def test_set_column_width_invalid_width(self, sample_workbook):
        """测试设置列宽 - 无效宽度"""
        adjuster = DimensionAdjuster(sample_workbook)

        # 宽度过大
        with pytest.raises(ValidationError):
            adjuster.set_column_width("Sheet1", 1, 300.0)

        # 宽度为负
        with pytest.raises(ValidationError):
            adjuster.set_column_width("Sheet1", 1, -5.0)

    def test_set_column_widths_batch(self, sample_workbook):
        """测试批量设置列宽"""
        adjuster = DimensionAdjuster(sample_workbook)
        widths = {1: 10.0, 2: 15.0, 3: 20.0}
        adjuster.set_column_widths("Sheet1", widths)

        sheet = adjuster._get_sheet("Sheet1")
        for col_num, expected_width in widths.items():
            assert sheet.column_widths[col_num] == expected_width

    def test_set_column_widths_empty(self, sample_workbook):
        """测试批量设置列宽 - 空字典"""
        adjuster = DimensionAdjuster(sample_workbook)
        with pytest.raises(ValidationError):
            adjuster.set_column_widths("Sheet1", {})

    def test_auto_fit_column(self, sample_workbook):
        """测试自动调整列宽"""
        adjuster = DimensionAdjuster(sample_workbook)

        # 列1: "Short" (5个字符)
        adjuster.auto_fit_column("Sheet1", 1)
        sheet = adjuster._get_sheet("Sheet1")
        width1 = sheet.column_widths[1]
        assert 8.43 <= width1 <= 10.0  # 应该接近最小宽度

        # 列2: "Medium Length" (13个字符)
        adjuster.auto_fit_column("Sheet1", 2)
        width2 = sheet.column_widths[2]
        assert width2 > width1  # 应该比列1宽

        # 列3: "Very Long Content Here" (22个字符)
        adjuster.auto_fit_column("Sheet1", 3)
        width3 = sheet.column_widths[3]
        assert width3 > width2  # 应该比列2宽

    def test_auto_fit_column_empty(self, sample_workbook):
        """测试自动调整列宽 - 空列"""
        adjuster = DimensionAdjuster(sample_workbook)

        # 添加一个空列（列4）
        adjuster.auto_fit_column("Sheet1", 4)

        sheet = adjuster._get_sheet("Sheet1")
        # 空列应该使用最小宽度
        assert sheet.column_widths[4] == 8.43

    def test_auto_fit_columns_batch(self, sample_workbook):
        """测试批量自动调整列宽"""
        adjuster = DimensionAdjuster(sample_workbook)
        adjuster.auto_fit_columns("Sheet1", [1, 2, 3])

        sheet = adjuster._get_sheet("Sheet1")
        assert 1 in sheet.column_widths
        assert 2 in sheet.column_widths
        assert 3 in sheet.column_widths

    def test_auto_fit_columns_empty_list(self, sample_workbook):
        """测试批量自动调整列宽 - 空列表"""
        adjuster = DimensionAdjuster(sample_workbook)
        with pytest.raises(ValidationError):
            adjuster.auto_fit_columns("Sheet1", [])

    def test_column_width_max_limit(self, sample_workbook):
        """测试列宽最大限制"""
        adjuster = DimensionAdjuster(sample_workbook)

        # 创建一个非常长的内容
        sheet = adjuster._get_sheet("Sheet1")
        long_content = "A" * 300  # 300个字符
        sheet.rows[0].cells[0].value = long_content

        # 自动调整应该限制在255
        adjuster.auto_fit_column("Sheet1", 1)
        assert sheet.column_widths[1] == 255.0
