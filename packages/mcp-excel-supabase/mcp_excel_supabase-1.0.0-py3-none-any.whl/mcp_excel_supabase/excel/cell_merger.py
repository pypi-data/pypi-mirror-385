"""
单元格合并器模块

提供单元格合并和取消合并功能，包括：
- 合并单元格范围
- 取消合并单元格
- 检查单元格是否已合并
- 获取单元格所在的合并范围
- 验证合并范围的有效性
"""

from typing import Optional, Tuple
from ..utils.logger import Logger
from ..utils.validator import Validator
from ..utils.errors import ValidationError
from .schemas import Workbook, Sheet, MergedCell

logger = Logger("cell_merger")


class CellMerger:
    """单元格合并器类

    用于管理 Workbook 对象中的单元格合并操作。
    所有操作都直接修改传入的 Workbook 对象。
    """

    def __init__(self, workbook: Workbook) -> None:
        """初始化单元格合并器

        Args:
            workbook: 要编辑的工作簿对象
        """
        self.workbook = workbook
        self.validator = Validator()
        logger.info(f"单元格合并器初始化完成，工作簿包含 {len(workbook.sheets)} 个工作表")

    def _get_sheet(self, sheet_name: str) -> Sheet:
        """获取指定工作表

        Args:
            sheet_name: 工作表名称

        Returns:
            Sheet: 工作表对象

        Raises:
            ValidationError: 工作表不存在
        """
        self.validator.validate_non_empty(sheet_name, "sheet_name")

        for sheet in self.workbook.sheets:
            if sheet.name == sheet_name:
                return sheet

        raise ValidationError(
            error_code="E201",
            message=f"工作表 '{sheet_name}' 不存在",
            context={
                "sheet_name": sheet_name,
                "available_sheets": [s.name for s in self.workbook.sheets],
            },
        )

    def _validate_merge_range(
        self,
        start_row: int,
        start_column: int,
        end_row: int,
        end_column: int,
    ) -> None:
        """验证合并范围的有效性

        Args:
            start_row: 起始行号（1-based）
            start_column: 起始列号（1-based）
            end_row: 结束行号（1-based）
            end_column: 结束列号（1-based）

        Raises:
            ValidationError: 范围无效
        """
        # 验证坐标为正整数
        self.validator.validate_range(start_row, "start_row", min_val=1)
        self.validator.validate_range(start_column, "start_column", min_val=1)
        self.validator.validate_range(end_row, "end_row", min_val=1)
        self.validator.validate_range(end_column, "end_column", min_val=1)

        # 验证结束坐标大于等于起始坐标
        if end_row < start_row:
            raise ValidationError(
                error_code="E201",
                message=f"结束行号 {end_row} 必须大于等于起始行号 {start_row}",
                context={"start_row": start_row, "end_row": end_row},
            )

        if end_column < start_column:
            raise ValidationError(
                error_code="E201",
                message=f"结束列号 {end_column} 必须大于等于起始列号 {start_column}",
                context={"start_column": start_column, "end_column": end_column},
            )

        # 验证不是单个单元格（至少要合并2个单元格）
        if start_row == end_row and start_column == end_column:
            raise ValidationError(
                error_code="E201",
                message="合并范围必须包含至少2个单元格",
                context={"start_row": start_row, "start_column": start_column},
            )

    def _check_overlap(
        self,
        sheet: Sheet,
        start_row: int,
        start_column: int,
        end_row: int,
        end_column: int,
    ) -> Optional[MergedCell]:
        """检查合并范围是否与现有合并单元格重叠

        Args:
            sheet: 工作表对象
            start_row: 起始行号（1-based）
            start_column: 起始列号（1-based）
            end_row: 结束行号（1-based）
            end_column: 结束列号（1-based）

        Returns:
            Optional[MergedCell]: 如果重叠，返回重叠的合并单元格；否则返回 None
        """
        for merged_cell in sheet.merged_cells:
            # 检查是否有重叠
            # 两个矩形重叠的条件：
            # 1. A的左边 <= B的右边
            # 2. A的右边 >= B的左边
            # 3. A的上边 <= B的下边
            # 4. A的下边 >= B的上边
            if (
                start_column <= merged_cell.end_column
                and end_column >= merged_cell.start_column
                and start_row <= merged_cell.end_row
                and end_row >= merged_cell.start_row
            ):
                return merged_cell

        return None

    def merge_cells(
        self,
        sheet_name: str,
        start_row: int,
        start_column: int,
        end_row: int,
        end_column: int,
    ) -> None:
        """合并单元格范围

        Args:
            sheet_name: 工作表名称
            start_row: 起始行号（1-based）
            start_column: 起始列号（1-based）
            end_row: 结束行号（1-based）
            end_column: 结束列号（1-based）

        Raises:
            ValidationError: 范围无效或与现有合并单元格重叠
        """
        # 验证范围
        self._validate_merge_range(start_row, start_column, end_row, end_column)

        # 获取工作表
        sheet = self._get_sheet(sheet_name)

        # 检查重叠
        overlap = self._check_overlap(sheet, start_row, start_column, end_row, end_column)
        if overlap is not None:
            raise ValidationError(
                error_code="E201",
                message="合并范围与现有合并单元格重叠",
                context={
                    "new_range": f"({start_row},{start_column}):({end_row},{end_column})",
                    "existing_range": f"({overlap.start_row},{overlap.start_column}):({overlap.end_row},{overlap.end_column})",
                },
            )

        # 添加合并单元格
        merged_cell = MergedCell(
            start_row=start_row,
            start_column=start_column,
            end_row=end_row,
            end_column=end_column,
        )
        sheet.merged_cells.append(merged_cell)

        logger.info(
            f"合并单元格: 工作表='{sheet_name}', "
            f"范围=({start_row},{start_column}):({end_row},{end_column})"
        )

    def unmerge_cells(
        self,
        sheet_name: str,
        row: int,
        column: int,
    ) -> bool:
        """取消单元格所在的合并范围

        Args:
            sheet_name: 工作表名称
            row: 单元格行号（1-based）
            column: 单元格列号（1-based）

        Returns:
            bool: 如果找到并取消了合并，返回 True；否则返回 False
        """
        # 验证坐标
        self.validator.validate_range(row, "row", min_val=1)
        self.validator.validate_range(column, "column", min_val=1)

        # 获取工作表
        sheet = self._get_sheet(sheet_name)

        # 查找包含该单元格的合并范围
        for i, merged_cell in enumerate(sheet.merged_cells):
            if (
                merged_cell.start_row <= row <= merged_cell.end_row
                and merged_cell.start_column <= column <= merged_cell.end_column
            ):
                # 找到了，删除该合并单元格
                del sheet.merged_cells[i]
                logger.info(
                    f"取消合并: 工作表='{sheet_name}', "
                    f"范围=({merged_cell.start_row},{merged_cell.start_column}):"
                    f"({merged_cell.end_row},{merged_cell.end_column})"
                )
                return True

        # 未找到
        logger.debug(f"单元格 ({row},{column}) 未合并")
        return False

    def is_merged(
        self,
        sheet_name: str,
        row: int,
        column: int,
    ) -> bool:
        """检查单元格是否已合并

        Args:
            sheet_name: 工作表名称
            row: 单元格行号（1-based）
            column: 单元格列号（1-based）

        Returns:
            bool: 如果单元格已合并，返回 True；否则返回 False
        """
        # 验证坐标
        self.validator.validate_range(row, "row", min_val=1)
        self.validator.validate_range(column, "column", min_val=1)

        # 获取工作表
        sheet = self._get_sheet(sheet_name)

        # 查找包含该单元格的合并范围
        for merged_cell in sheet.merged_cells:
            if (
                merged_cell.start_row <= row <= merged_cell.end_row
                and merged_cell.start_column <= column <= merged_cell.end_column
            ):
                return True

        return False

    def get_merged_range(
        self,
        sheet_name: str,
        row: int,
        column: int,
    ) -> Optional[Tuple[int, int, int, int]]:
        """获取单元格所在的合并范围

        Args:
            sheet_name: 工作表名称
            row: 单元格行号（1-based）
            column: 单元格列号（1-based）

        Returns:
            Optional[Tuple[int, int, int, int]]: 如果单元格已合并，返回 (start_row, start_column, end_row, end_column)；
                                                  否则返回 None
        """
        # 验证坐标
        self.validator.validate_range(row, "row", min_val=1)
        self.validator.validate_range(column, "column", min_val=1)

        # 获取工作表
        sheet = self._get_sheet(sheet_name)

        # 查找包含该单元格的合并范围
        for merged_cell in sheet.merged_cells:
            if (
                merged_cell.start_row <= row <= merged_cell.end_row
                and merged_cell.start_column <= column <= merged_cell.end_column
            ):
                return (
                    merged_cell.start_row,
                    merged_cell.start_column,
                    merged_cell.end_row,
                    merged_cell.end_column,
                )

        return None
