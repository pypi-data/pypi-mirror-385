"""
格式编辑器模块

提供单元格格式编辑功能，包括：
- 修改字体格式（名称、大小、颜色、粗体、斜体、下划线）
- 修改填充格式（背景色、图案）
- 修改边框格式（上下左右边框）
- 修改对齐格式（水平、垂直、自动换行）
- 修改数字格式
- 支持单个和批量操作
"""

from typing import Any, Dict, List, Optional, Tuple
from ..utils.logger import Logger
from ..utils.validator import Validator
from ..utils.errors import ValidationError
from .schemas import (
    Workbook,
    Sheet,
    Cell,
    CellFormat,
    FontFormat,
    FillFormat,
    BorderFormat,
    BorderSide,
    AlignmentFormat,
)

logger = Logger("format_editor")


class FormatEditor:
    """格式编辑器类

    用于修改 Workbook 对象中单元格的格式信息。
    所有操作都直接修改传入的 Workbook 对象。
    """

    def __init__(self, workbook: Workbook) -> None:
        """初始化格式编辑器

        Args:
            workbook: 要编辑的工作簿对象
        """
        self.workbook = workbook
        self.validator = Validator()
        logger.info(f"格式编辑器初始化完成，工作簿包含 {len(workbook.sheets)} 个工作表")

    def _get_cell(self, sheet_name: str, row: int, column: int) -> Cell:
        """获取指定单元格

        Args:
            sheet_name: 工作表名称
            row: 行号（1-based）
            column: 列号（1-based）

        Returns:
            Cell: 单元格对象

        Raises:
            ValidationError: 工作表不存在或单元格坐标无效
        """
        # 验证输入
        self.validator.validate_non_empty(sheet_name, "sheet_name")
        self.validator.validate_range(row, "row", min_val=1)
        self.validator.validate_range(column, "column", min_val=1)

        # 查找工作表
        sheet: Optional[Sheet] = None
        for s in self.workbook.sheets:
            if s.name == sheet_name:
                sheet = s
                break

        if sheet is None:
            raise ValidationError(
                error_code="E201",
                message=f"工作表 '{sheet_name}' 不存在",
                context={
                    "sheet_name": sheet_name,
                    "available_sheets": [s.name for s in self.workbook.sheets],
                },
            )

        # 查找单元格
        for row_obj in sheet.rows:
            for cell in row_obj.cells:
                if cell.row == row and cell.column == column:
                    return cell

        # 单元格不存在
        raise ValidationError(
            error_code="E201",
            message=f"单元格 ({row}, {column}) 在工作表 '{sheet_name}' 中不存在",
            context={"sheet_name": sheet_name, "row": row, "column": column},
        )

    def modify_font(
        self,
        sheet_name: str,
        row: int,
        column: int,
        name: Optional[str] = None,
        size: Optional[float] = None,
        bold: Optional[bool] = None,
        italic: Optional[bool] = None,
        underline: Optional[str] = None,
        color: Optional[str] = None,
    ) -> None:
        """修改单元格字体格式

        Args:
            sheet_name: 工作表名称
            row: 行号（1-based）
            column: 列号（1-based）
            name: 字体名称，如 'Arial'
            size: 字体大小
            bold: 是否粗体
            italic: 是否斜体
            underline: 下划线类型
            color: 字体颜色（十六进制，如 '#FF0000'）
        """
        cell = self._get_cell(sheet_name, row, column)

        # 确保单元格有格式对象
        if cell.format is None:
            cell.format = CellFormat()

        # 确保有字体格式对象
        if cell.format.font is None:
            cell.format.font = FontFormat()

        # 更新字体属性
        if name is not None:
            cell.format.font.name = name
        if size is not None:
            self.validator.validate_range(size, "font_size", min_val=1.0, max_val=409.0)
            cell.format.font.size = size
        if bold is not None:
            cell.format.font.bold = bold
        if italic is not None:
            cell.format.font.italic = italic
        if underline is not None:
            cell.format.font.underline = underline
        if color is not None:
            self.validator.validate_color(color)
            cell.format.font.color = color

        logger.debug(f"修改单元格 ({row}, {column}) 字体格式: {cell.format.font}")

    def modify_fill(
        self,
        sheet_name: str,
        row: int,
        column: int,
        background_color: Optional[str] = None,
        pattern_type: Optional[str] = None,
    ) -> None:
        """修改单元格填充格式

        Args:
            sheet_name: 工作表名称
            row: 行号（1-based）
            column: 列号（1-based）
            background_color: 背景颜色（十六进制，如 '#FFFF00'）
            pattern_type: 填充图案类型
        """
        cell = self._get_cell(sheet_name, row, column)

        # 确保单元格有格式对象
        if cell.format is None:
            cell.format = CellFormat()

        # 确保有填充格式对象
        if cell.format.fill is None:
            cell.format.fill = FillFormat()

        # 更新填充属性
        if background_color is not None:
            self.validator.validate_color(background_color)
            cell.format.fill.background_color = background_color
        if pattern_type is not None:
            cell.format.fill.pattern_type = pattern_type

        logger.debug(f"修改单元格 ({row}, {column}) 填充格式: {cell.format.fill}")

    def modify_border(
        self,
        sheet_name: str,
        row: int,
        column: int,
        top: Optional[Dict[str, Optional[str]]] = None,
        bottom: Optional[Dict[str, Optional[str]]] = None,
        left: Optional[Dict[str, Optional[str]]] = None,
        right: Optional[Dict[str, Optional[str]]] = None,
    ) -> None:
        """修改单元格边框格式

        Args:
            sheet_name: 工作表名称
            row: 行号（1-based）
            column: 列号（1-based）
            top: 上边框，格式为 {"style": "thin", "color": "#000000"}
            bottom: 下边框
            left: 左边框
            right: 右边框
        """
        cell = self._get_cell(sheet_name, row, column)

        # 确保单元格有格式对象
        if cell.format is None:
            cell.format = CellFormat()

        # 确保有边框格式对象
        if cell.format.border is None:
            cell.format.border = BorderFormat()

        # 更新边框属性
        if top is not None:
            cell.format.border.top = BorderSide(**top)
        if bottom is not None:
            cell.format.border.bottom = BorderSide(**bottom)
        if left is not None:
            cell.format.border.left = BorderSide(**left)
        if right is not None:
            cell.format.border.right = BorderSide(**right)

        logger.debug(f"修改单元格 ({row}, {column}) 边框格式: {cell.format.border}")

    def modify_alignment(
        self,
        sheet_name: str,
        row: int,
        column: int,
        horizontal: Optional[str] = None,
        vertical: Optional[str] = None,
        wrap_text: Optional[bool] = None,
    ) -> None:
        """修改单元格对齐格式

        Args:
            sheet_name: 工作表名称
            row: 行号（1-based）
            column: 列号（1-based）
            horizontal: 水平对齐，如 'left', 'center', 'right'
            vertical: 垂直对齐，如 'top', 'center', 'bottom'
            wrap_text: 是否自动换行
        """
        cell = self._get_cell(sheet_name, row, column)

        # 确保单元格有格式对象
        if cell.format is None:
            cell.format = CellFormat()

        # 确保有对齐格式对象
        if cell.format.alignment is None:
            cell.format.alignment = AlignmentFormat()

        # 更新对齐属性
        if horizontal is not None:
            cell.format.alignment.horizontal = horizontal
        if vertical is not None:
            cell.format.alignment.vertical = vertical
        if wrap_text is not None:
            cell.format.alignment.wrap_text = wrap_text

        logger.debug(f"修改单元格 ({row}, {column}) 对齐格式: {cell.format.alignment}")

    def modify_number_format(
        self,
        sheet_name: str,
        row: int,
        column: int,
        number_format: str,
    ) -> None:
        """修改单元格数字格式

        Args:
            sheet_name: 工作表名称
            row: 行号（1-based）
            column: 列号（1-based）
            number_format: 数字格式，如 '0.00', 'yyyy-mm-dd'
        """
        cell = self._get_cell(sheet_name, row, column)

        # 确保单元格有格式对象
        if cell.format is None:
            cell.format = CellFormat()

        # 更新数字格式
        self.validator.validate_non_empty(number_format, "number_format")
        cell.format.number_format = number_format

        logger.debug(f"修改单元格 ({row}, {column}) 数字格式: {number_format}")

    def modify_cell_format(
        self,
        sheet_name: str,
        row: int,
        column: int,
        font: Optional[Dict[str, Any]] = None,
        fill: Optional[Dict[str, Any]] = None,
        border: Optional[Dict[str, Any]] = None,
        alignment: Optional[Dict[str, Any]] = None,
        number_format: Optional[str] = None,
    ) -> None:
        """一次性修改单元格的多个格式属性

        Args:
            sheet_name: 工作表名称
            row: 行号（1-based）
            column: 列号（1-based）
            font: 字体格式字典
            fill: 填充格式字典
            border: 边框格式字典
            alignment: 对齐格式字典
            number_format: 数字格式
        """
        if font is not None:
            self.modify_font(sheet_name, row, column, **font)
        if fill is not None:
            self.modify_fill(sheet_name, row, column, **fill)
        if border is not None:
            self.modify_border(sheet_name, row, column, **border)
        if alignment is not None:
            self.modify_alignment(sheet_name, row, column, **alignment)
        if number_format is not None:
            self.modify_number_format(sheet_name, row, column, number_format)

        logger.info(f"修改单元格 ({row}, {column}) 完整格式")

    def modify_cells_format(
        self,
        sheet_name: str,
        cells: List[Tuple[int, int]],
        font: Optional[Dict[str, Any]] = None,
        fill: Optional[Dict[str, Any]] = None,
        border: Optional[Dict[str, Any]] = None,
        alignment: Optional[Dict[str, Any]] = None,
        number_format: Optional[str] = None,
    ) -> None:
        """批量修改多个单元格的格式

        Args:
            sheet_name: 工作表名称
            cells: 单元格坐标列表，每个元素为 (row, column) 元组
            font: 字体格式字典
            fill: 填充格式字典
            border: 边框格式字典
            alignment: 对齐格式字典
            number_format: 数字格式
        """
        self.validator.validate_non_empty(cells, "cells")

        for row, column in cells:
            self.modify_cell_format(
                sheet_name=sheet_name,
                row=row,
                column=column,
                font=font,
                fill=fill,
                border=border,
                alignment=alignment,
                number_format=number_format,
            )

        logger.info(f"批量修改 {len(cells)} 个单元格格式")
