"""
Excel 格式提取器

从 openpyxl 的 Cell 对象中提取格式信息，转换为 schemas 定义的格式模型。
"""

from typing import Any, Optional
from openpyxl.cell.cell import Cell as OpenpyxlCell
from openpyxl.styles import Color

from .schemas import (
    AlignmentFormat,
    BorderFormat,
    BorderSide,
    CellFormat,
    FillFormat,
    FontFormat,
)
from ..utils.logger import get_logger

logger = get_logger(__name__)


class FormatExtractor:
    """Excel 格式提取器"""

    @staticmethod
    def _color_to_hex(color: Optional[Color]) -> Optional[str]:
        """
        将 openpyxl 的 Color 对象转换为十六进制字符串

        Args:
            color: openpyxl Color 对象

        Returns:
            十六进制颜色字符串（如 '#FF0000'），如果颜色为 None 则返回 None
        """
        if color is None:
            return None

        # 获取 RGB 值
        rgb = color.rgb
        if rgb is None:
            return None

        # openpyxl 的 rgb 格式可能是 'AARRGGBB' 或 'RRGGBB'
        if isinstance(rgb, str):
            # 移除 alpha 通道（前两位）
            if len(rgb) == 8:
                rgb = rgb[2:]
            # 确保是 6 位
            if len(rgb) == 6:
                return f"#{rgb}"

        return None

    @staticmethod
    def extract_font_format(cell: OpenpyxlCell) -> Optional[FontFormat]:
        """
        提取字体格式

        Args:
            cell: openpyxl Cell 对象

        Returns:
            FontFormat 对象，如果没有字体格式则返回 None
        """
        # openpyxl 的 cell.font 可能是代理对象，需要检查是否有实际值
        try:
            font = cell.font
            if font is None:
                return None
        except AttributeError:
            return None

        # 提取字体颜色
        try:
            color = FormatExtractor._color_to_hex(font.color)
        except AttributeError:
            color = None

        # 提取下划线类型
        underline = None
        try:
            if font.underline:
                underline = font.underline if isinstance(font.underline, str) else "single"
        except AttributeError:
            underline = None

        # 提取其他字体属性（使用 try-except 防止代理对象问题）
        try:
            name = font.name
        except AttributeError:
            name = None

        try:
            size = font.size
        except AttributeError:
            size = None

        try:
            bold = font.bold
        except AttributeError:
            bold = None

        try:
            italic = font.italic
        except AttributeError:
            italic = None

        # 创建 FontFormat 对象
        font_format = FontFormat(
            name=name,
            size=size,
            bold=bold,
            italic=italic,
            underline=underline,
            color=color,
        )

        # 如果所有字段都是 None，返回 None
        if all(
            getattr(font_format, field) is None
            for field in ["name", "size", "bold", "italic", "underline", "color"]
        ):
            return None

        return font_format

    @staticmethod
    def extract_fill_format(cell: OpenpyxlCell) -> Optional[FillFormat]:
        """
        提取填充格式

        Args:
            cell: openpyxl Cell 对象

        Returns:
            FillFormat 对象，如果没有填充格式则返回 None
        """
        try:
            fill = cell.fill
            if fill is None:
                return None
        except AttributeError:
            return None

        # 提取背景颜色
        background_color = None
        if hasattr(fill, "fgColor") and fill.fgColor:
            try:
                background_color = FormatExtractor._color_to_hex(fill.fgColor)
            except AttributeError:
                background_color = None

        # 提取图案类型
        pattern_type = fill.patternType if hasattr(fill, "patternType") else None

        # 如果没有有效的填充信息，返回 None
        if background_color is None and pattern_type is None:
            return None

        return FillFormat(background_color=background_color, pattern_type=pattern_type)

    @staticmethod
    def extract_border_format(cell: OpenpyxlCell) -> Optional[BorderFormat]:
        """
        提取边框格式

        Args:
            cell: openpyxl Cell 对象

        Returns:
            BorderFormat 对象，如果没有边框格式则返回 None
        """
        try:
            border = cell.border
            if border is None:
                return None
        except AttributeError:
            return None

        # 提取四个方向的边框
        def extract_side(side: Optional[Any]) -> Optional[BorderSide]:
            """提取单边边框"""
            if side is None or not hasattr(side, "style") or side.style is None:
                return None

            color = FormatExtractor._color_to_hex(side.color) if hasattr(side, "color") else None
            return BorderSide(style=side.style, color=color)

        top = extract_side(border.top) if hasattr(border, "top") else None
        bottom = extract_side(border.bottom) if hasattr(border, "bottom") else None
        left = extract_side(border.left) if hasattr(border, "left") else None
        right = extract_side(border.right) if hasattr(border, "right") else None

        # 如果所有边框都是 None，返回 None
        if all(side is None for side in [top, bottom, left, right]):
            return None

        return BorderFormat(top=top, bottom=bottom, left=left, right=right)

    @staticmethod
    def extract_alignment_format(cell: OpenpyxlCell) -> Optional[AlignmentFormat]:
        """
        提取对齐格式

        Args:
            cell: openpyxl Cell 对象

        Returns:
            AlignmentFormat 对象，如果没有对齐格式则返回 None
        """
        try:
            alignment = cell.alignment
            if alignment is None:
                return None
        except AttributeError:
            return None

        horizontal = alignment.horizontal if hasattr(alignment, "horizontal") else None
        vertical = alignment.vertical if hasattr(alignment, "vertical") else None
        wrap_text = alignment.wrap_text if hasattr(alignment, "wrap_text") else None

        # 如果所有字段都是 None，返回 None
        if all(field is None for field in [horizontal, vertical, wrap_text]):
            return None

        return AlignmentFormat(horizontal=horizontal, vertical=vertical, wrap_text=wrap_text)

    @staticmethod
    def extract_number_format(cell: OpenpyxlCell) -> Optional[str]:
        """
        提取数字格式

        Args:
            cell: openpyxl Cell 对象

        Returns:
            数字格式字符串，如果是默认格式则返回 None
        """
        try:
            number_format = cell.number_format
            if number_format is None:
                return None

            # 默认格式是 'General'，不需要记录
            if number_format == "General":
                return None

            return str(number_format)
        except AttributeError:
            return None

    @staticmethod
    def extract_cell_format(cell: OpenpyxlCell) -> Optional[CellFormat]:
        """
        提取单元格的所有格式信息

        Args:
            cell: openpyxl Cell 对象

        Returns:
            CellFormat 对象，如果没有任何格式则返回 None
        """
        font = FormatExtractor.extract_font_format(cell)
        fill = FormatExtractor.extract_fill_format(cell)
        border = FormatExtractor.extract_border_format(cell)
        alignment = FormatExtractor.extract_alignment_format(cell)
        number_format = FormatExtractor.extract_number_format(cell)

        # 如果所有格式都是 None，返回 None
        if all(fmt is None for fmt in [font, fill, border, alignment, number_format]):
            return None

        return CellFormat(
            font=font,
            fill=fill,
            border=border,
            alignment=alignment,
            number_format=number_format,
        )


# ============================================================================
# 导出
# ============================================================================

__all__ = ["FormatExtractor"]
