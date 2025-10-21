"""
单元格合并器单元测试
"""

import pytest
from mcp_excel_supabase.excel import (
    Workbook,
    Sheet,
    Row,
    Cell,
    MergedCell,
    CellMerger,
)
from mcp_excel_supabase.utils.errors import ValidationError


@pytest.fixture
def sample_workbook():
    """创建测试用工作簿"""
    cells = []
    for row in range(1, 6):
        for col in range(1, 6):
            cells.append(Cell(value=f"{row},{col}", data_type="string", row=row, column=col))

    rows = []
    for row_num in range(1, 6):
        row_cells = [c for c in cells if c.row == row_num]
        rows.append(Row(cells=row_cells))

    sheet = Sheet(name="Sheet1", rows=rows)
    workbook = Workbook(sheets=[sheet])

    return workbook


class TestCellMerger:
    """单元格合并器测试类"""

    def test_init(self, sample_workbook):
        """测试初始化"""
        merger = CellMerger(sample_workbook)
        assert merger.workbook == sample_workbook
        assert merger.validator is not None

    def test_get_sheet_success(self, sample_workbook):
        """测试获取工作表成功"""
        merger = CellMerger(sample_workbook)
        sheet = merger._get_sheet("Sheet1")
        assert sheet.name == "Sheet1"

    def test_get_sheet_not_found(self, sample_workbook):
        """测试获取工作表 - 不存在"""
        merger = CellMerger(sample_workbook)
        with pytest.raises(ValidationError) as exc_info:
            merger._get_sheet("NonExistent")
        assert "不存在" in str(exc_info.value)

    def test_validate_merge_range_success(self, sample_workbook):
        """测试验证合并范围 - 成功"""
        merger = CellMerger(sample_workbook)
        # 不应抛出异常
        merger._validate_merge_range(1, 1, 2, 2)

    def test_validate_merge_range_invalid_end_row(self, sample_workbook):
        """测试验证合并范围 - 结束行小于起始行"""
        merger = CellMerger(sample_workbook)
        with pytest.raises(ValidationError) as exc_info:
            merger._validate_merge_range(2, 1, 1, 2)
        assert "结束行号" in str(exc_info.value)

    def test_validate_merge_range_invalid_end_column(self, sample_workbook):
        """测试验证合并范围 - 结束列小于起始列"""
        merger = CellMerger(sample_workbook)
        with pytest.raises(ValidationError) as exc_info:
            merger._validate_merge_range(1, 2, 2, 1)
        assert "结束列号" in str(exc_info.value)

    def test_validate_merge_range_single_cell(self, sample_workbook):
        """测试验证合并范围 - 单个单元格"""
        merger = CellMerger(sample_workbook)
        with pytest.raises(ValidationError) as exc_info:
            merger._validate_merge_range(1, 1, 1, 1)
        assert "至少2个单元格" in str(exc_info.value)

    def test_merge_cells_success(self, sample_workbook):
        """测试合并单元格成功"""
        merger = CellMerger(sample_workbook)
        merger.merge_cells("Sheet1", 1, 1, 2, 2)

        sheet = merger._get_sheet("Sheet1")
        assert len(sheet.merged_cells) == 1
        merged = sheet.merged_cells[0]
        assert merged.start_row == 1
        assert merged.start_column == 1
        assert merged.end_row == 2
        assert merged.end_column == 2

    def test_merge_cells_overlap(self, sample_workbook):
        """测试合并单元格 - 重叠"""
        merger = CellMerger(sample_workbook)

        # 先合并 (1,1):(2,2)
        merger.merge_cells("Sheet1", 1, 1, 2, 2)

        # 尝试合并重叠的范围 (2,2):(3,3)
        with pytest.raises(ValidationError) as exc_info:
            merger.merge_cells("Sheet1", 2, 2, 3, 3)
        assert "重叠" in str(exc_info.value)

    def test_check_overlap_no_overlap(self, sample_workbook):
        """测试检查重叠 - 无重叠"""
        merger = CellMerger(sample_workbook)
        sheet = merger._get_sheet("Sheet1")

        # 添加一个合并单元格
        sheet.merged_cells.append(MergedCell(start_row=1, start_column=1, end_row=2, end_column=2))

        # 检查不重叠的范围
        overlap = merger._check_overlap(sheet, 3, 3, 4, 4)
        assert overlap is None

    def test_check_overlap_with_overlap(self, sample_workbook):
        """测试检查重叠 - 有重叠"""
        merger = CellMerger(sample_workbook)
        sheet = merger._get_sheet("Sheet1")

        # 添加一个合并单元格
        existing = MergedCell(start_row=1, start_column=1, end_row=2, end_column=2)
        sheet.merged_cells.append(existing)

        # 检查重叠的范围
        overlap = merger._check_overlap(sheet, 2, 2, 3, 3)
        assert overlap == existing

    def test_unmerge_cells_success(self, sample_workbook):
        """测试取消合并成功"""
        merger = CellMerger(sample_workbook)

        # 先合并
        merger.merge_cells("Sheet1", 1, 1, 2, 2)

        # 取消合并
        result = merger.unmerge_cells("Sheet1", 1, 1)
        assert result is True

        sheet = merger._get_sheet("Sheet1")
        assert len(sheet.merged_cells) == 0

    def test_unmerge_cells_not_merged(self, sample_workbook):
        """测试取消合并 - 单元格未合并"""
        merger = CellMerger(sample_workbook)

        result = merger.unmerge_cells("Sheet1", 1, 1)
        assert result is False

    def test_is_merged_true(self, sample_workbook):
        """测试检查是否合并 - 已合并"""
        merger = CellMerger(sample_workbook)

        # 合并单元格
        merger.merge_cells("Sheet1", 1, 1, 2, 2)

        # 检查范围内的单元格
        assert merger.is_merged("Sheet1", 1, 1) is True
        assert merger.is_merged("Sheet1", 1, 2) is True
        assert merger.is_merged("Sheet1", 2, 1) is True
        assert merger.is_merged("Sheet1", 2, 2) is True

    def test_is_merged_false(self, sample_workbook):
        """测试检查是否合并 - 未合并"""
        merger = CellMerger(sample_workbook)

        # 合并单元格
        merger.merge_cells("Sheet1", 1, 1, 2, 2)

        # 检查范围外的单元格
        assert merger.is_merged("Sheet1", 3, 3) is False

    def test_get_merged_range_success(self, sample_workbook):
        """测试获取合并范围 - 成功"""
        merger = CellMerger(sample_workbook)

        # 合并单元格
        merger.merge_cells("Sheet1", 1, 1, 2, 2)

        # 获取合并范围
        range_tuple = merger.get_merged_range("Sheet1", 1, 1)
        assert range_tuple == (1, 1, 2, 2)

    def test_get_merged_range_not_merged(self, sample_workbook):
        """测试获取合并范围 - 未合并"""
        merger = CellMerger(sample_workbook)

        range_tuple = merger.get_merged_range("Sheet1", 1, 1)
        assert range_tuple is None

    def test_multiple_merge_ranges(self, sample_workbook):
        """测试多个合并范围"""
        merger = CellMerger(sample_workbook)

        # 合并多个不重叠的范围
        merger.merge_cells("Sheet1", 1, 1, 2, 2)
        merger.merge_cells("Sheet1", 3, 3, 4, 4)

        sheet = merger._get_sheet("Sheet1")
        assert len(sheet.merged_cells) == 2

        # 验证每个范围
        assert merger.is_merged("Sheet1", 1, 1) is True
        assert merger.is_merged("Sheet1", 3, 3) is True
        assert merger.is_merged("Sheet1", 2, 3) is False  # 中间的单元格未合并
