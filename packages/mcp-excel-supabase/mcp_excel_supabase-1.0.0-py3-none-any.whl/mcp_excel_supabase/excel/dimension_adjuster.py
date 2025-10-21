"""
行列尺寸调整器模块

提供行高和列宽调整功能，包括：
- 设置单行高度
- 批量设置行高
- 设置单列宽度
- 批量设置列宽
- 自动调整列宽（基于内容长度估算）
"""

from typing import Dict, List
from ..utils.logger import Logger
from ..utils.validator import Validator
from ..utils.errors import ValidationError
from .schemas import Workbook, Sheet, Row

logger = Logger("dimension_adjuster")


class DimensionAdjuster:
    """行列尺寸调整器类

    用于调整 Workbook 对象中的行高和列宽。
    所有操作都直接修改传入的 Workbook 对象。
    """

    def __init__(self, workbook: Workbook) -> None:
        """初始化行列尺寸调整器

        Args:
            workbook: 要编辑的工作簿对象
        """
        self.workbook = workbook
        self.validator = Validator()
        logger.info(f"行列尺寸调整器初始化完成，工作簿包含 {len(workbook.sheets)} 个工作表")

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

    def _get_row(self, sheet: Sheet, row_number: int) -> Row:
        """获取指定行对象

        Args:
            sheet: 工作表对象
            row_number: 行号（1-based）

        Returns:
            Row: 行对象

        Raises:
            ValidationError: 行不存在
        """
        for row in sheet.rows:
            if row.cells and row.cells[0].row == row_number:
                return row

        raise ValidationError(
            error_code="E201",
            message=f"行 {row_number} 在工作表 '{sheet.name}' 中不存在",
            context={"sheet_name": sheet.name, "row_number": row_number},
        )

    def set_row_height(
        self,
        sheet_name: str,
        row_number: int,
        height: float,
    ) -> None:
        """设置单行高度

        Args:
            sheet_name: 工作表名称
            row_number: 行号（1-based）
            height: 行高（单位：磅）

        Raises:
            ValidationError: 工作表或行不存在，或高度无效
        """
        # 验证输入
        self.validator.validate_range(row_number, "row_number", min_val=1)
        self.validator.validate_range(height, "height", min_val=0.0, max_val=409.0)

        # 获取工作表和行
        sheet = self._get_sheet(sheet_name)
        row = self._get_row(sheet, row_number)

        # 设置行高
        row.height = height

        logger.info(f"设置行高: 工作表='{sheet_name}', 行={row_number}, 高度={height}")

    def set_row_heights(
        self,
        sheet_name: str,
        heights: Dict[int, float],
    ) -> None:
        """批量设置行高

        Args:
            sheet_name: 工作表名称
            heights: 行高字典，键为行号（1-based），值为高度（单位：磅）

        Raises:
            ValidationError: 工作表或行不存在，或高度无效
        """
        self.validator.validate_non_empty(heights, "heights")

        for row_number, height in heights.items():
            self.set_row_height(sheet_name, row_number, height)

        logger.info(f"批量设置 {len(heights)} 行的行高")

    def set_column_width(
        self,
        sheet_name: str,
        column_number: int,
        width: float,
    ) -> None:
        """设置单列宽度

        Args:
            sheet_name: 工作表名称
            column_number: 列号（1-based）
            width: 列宽（单位：字符宽度）

        Raises:
            ValidationError: 工作表不存在或宽度无效
        """
        # 验证输入
        self.validator.validate_range(column_number, "column_number", min_val=1)
        self.validator.validate_range(width, "width", min_val=0.0, max_val=255.0)

        # 获取工作表
        sheet = self._get_sheet(sheet_name)

        # 设置列宽
        sheet.column_widths[column_number] = width

        logger.info(f"设置列宽: 工作表='{sheet_name}', 列={column_number}, 宽度={width}")

    def set_column_widths(
        self,
        sheet_name: str,
        widths: Dict[int, float],
    ) -> None:
        """批量设置列宽

        Args:
            sheet_name: 工作表名称
            widths: 列宽字典，键为列号（1-based），值为宽度（单位：字符宽度）

        Raises:
            ValidationError: 工作表不存在或宽度无效
        """
        self.validator.validate_non_empty(widths, "widths")

        for column_number, width in widths.items():
            self.set_column_width(sheet_name, column_number, width)

        logger.info(f"批量设置 {len(widths)} 列的列宽")

    def auto_fit_column(
        self,
        sheet_name: str,
        column_number: int,
    ) -> None:
        """自动调整列宽（基于内容长度估算）

        Args:
            sheet_name: 工作表名称
            column_number: 列号（1-based）

        Raises:
            ValidationError: 工作表不存在
        """
        # 验证输入
        self.validator.validate_range(column_number, "column_number", min_val=1)

        # 获取工作表
        sheet = self._get_sheet(sheet_name)

        # 计算该列所有单元格的最大内容长度
        max_length = 0
        for row in sheet.rows:
            for cell in row.cells:
                if cell.column == column_number and cell.value is not None:
                    # 估算内容长度（字符数）
                    content_length = len(str(cell.value))
                    max_length = max(max_length, content_length)

        # 根据内容长度估算列宽
        # Excel 的列宽单位是字符宽度，通常 1 个字符约等于 1 个单位
        # 添加一些额外空间（10%）以避免内容被截断
        estimated_width = max_length * 1.1

        # 限制在合理范围内（最小 8.43，最大 255）
        estimated_width = max(8.43, min(estimated_width, 255.0))

        # 设置列宽
        sheet.column_widths[column_number] = estimated_width

        logger.info(
            f"自动调整列宽: 工作表='{sheet_name}', 列={column_number}, "
            f"最大内容长度={max_length}, 估算宽度={estimated_width:.2f}"
        )

    def auto_fit_columns(
        self,
        sheet_name: str,
        column_numbers: List[int],
    ) -> None:
        """批量自动调整列宽

        Args:
            sheet_name: 工作表名称
            column_numbers: 列号列表（1-based）

        Raises:
            ValidationError: 工作表不存在
        """
        self.validator.validate_non_empty(column_numbers, "column_numbers")

        for column_number in column_numbers:
            self.auto_fit_column(sheet_name, column_number)

        logger.info(f"批量自动调整 {len(column_numbers)} 列的列宽")
