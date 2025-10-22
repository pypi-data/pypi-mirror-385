"""
Excel 数据模型定义

使用 Pydantic 定义 Excel 数据的 JSON 表示结构，包括：
- CellFormat: 单元格格式（字体、颜色、边框、对齐等）
- Cell: 单元格数据
- Row: 行数据
- MergedCell: 合并单元格
- Sheet: 工作表
- Workbook: 工作簿
"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field, field_validator


# ============================================================================
# 格式相关模型
# ============================================================================


class FontFormat(BaseModel):
    """字体格式"""

    name: Optional[str] = Field(default=None, description="字体名称，如 'Arial'")
    size: Optional[float] = Field(default=None, description="字体大小")
    bold: Optional[bool] = Field(default=None, description="是否粗体")
    italic: Optional[bool] = Field(default=None, description="是否斜体")
    underline: Optional[str] = Field(default=None, description="下划线类型")
    color: Optional[str] = Field(default=None, description="字体颜色（十六进制，如 '#FF0000'）")

    @field_validator("color")
    @classmethod
    def validate_color(cls, v: Optional[str]) -> Optional[str]:
        """验证颜色格式"""
        if v is not None and not v.startswith("#"):
            return f"#{v}"
        return v


class FillFormat(BaseModel):
    """填充格式"""

    background_color: Optional[str] = Field(
        default=None, description="背景颜色（十六进制，如 '#FFFF00'）"
    )
    pattern_type: Optional[str] = Field(default=None, description="填充图案类型")

    @field_validator("background_color")
    @classmethod
    def validate_color(cls, v: Optional[str]) -> Optional[str]:
        """验证颜色格式"""
        if v is not None and not v.startswith("#"):
            return f"#{v}"
        return v


class BorderSide(BaseModel):
    """边框单边"""

    style: Optional[str] = Field(default=None, description="边框样式，如 'thin', 'medium', 'thick'")
    color: Optional[str] = Field(default=None, description="边框颜色（十六进制）")

    @field_validator("color")
    @classmethod
    def validate_color(cls, v: Optional[str]) -> Optional[str]:
        """验证颜色格式"""
        if v is not None and not v.startswith("#"):
            return f"#{v}"
        return v


class BorderFormat(BaseModel):
    """边框格式"""

    top: Optional[BorderSide] = Field(default=None, description="上边框")
    bottom: Optional[BorderSide] = Field(default=None, description="下边框")
    left: Optional[BorderSide] = Field(default=None, description="左边框")
    right: Optional[BorderSide] = Field(default=None, description="右边框")


class AlignmentFormat(BaseModel):
    """对齐格式"""

    horizontal: Optional[str] = Field(
        default=None, description="水平对齐，如 'left', 'center', 'right'"
    )
    vertical: Optional[str] = Field(
        default=None, description="垂直对齐，如 'top', 'center', 'bottom'"
    )
    wrap_text: Optional[bool] = Field(default=None, description="是否自动换行")


class CellFormat(BaseModel):
    """单元格格式（整合所有格式信息）"""

    font: Optional[FontFormat] = Field(default=None, description="字体格式")
    fill: Optional[FillFormat] = Field(default=None, description="填充格式")
    border: Optional[BorderFormat] = Field(default=None, description="边框格式")
    alignment: Optional[AlignmentFormat] = Field(default=None, description="对齐格式")
    number_format: Optional[str] = Field(
        default=None, description="数字格式，如 '0.00', 'yyyy-mm-dd'"
    )


# ============================================================================
# 单元格和行模型
# ============================================================================


class Cell(BaseModel):
    """单元格数据"""

    value: Optional[Union[str, int, float, bool]] = Field(default=None, description="单元格值")
    data_type: str = Field(
        default="null", description="数据类型：string, number, boolean, formula, date, null"
    )
    format: Optional[CellFormat] = Field(default=None, description="单元格格式")
    row: int = Field(description="行号（1-based）")
    column: int = Field(description="列号（1-based）")

    @field_validator("data_type")
    @classmethod
    def validate_data_type(cls, v: str) -> str:
        """验证数据类型"""
        valid_types = {"string", "number", "boolean", "formula", "date", "null"}
        if v not in valid_types:
            raise ValueError(f"数据类型必须是 {valid_types} 之一，当前值: {v}")
        return v


class Row(BaseModel):
    """行数据"""

    cells: List[Cell] = Field(default_factory=list, description="单元格列表")
    height: Optional[float] = Field(default=None, description="行高")


# ============================================================================
# 合并单元格模型
# ============================================================================


class MergedCell(BaseModel):
    """合并单元格"""

    start_row: int = Field(description="起始行号（1-based）")
    start_column: int = Field(description="起始列号（1-based）")
    end_row: int = Field(description="结束行号（1-based）")
    end_column: int = Field(description="结束列号（1-based）")

    @field_validator("end_row")
    @classmethod
    def validate_end_row(cls, v: int, info: Any) -> int:
        """验证结束行号必须大于等于起始行号"""
        if "start_row" in info.data and v < info.data["start_row"]:
            raise ValueError(f"结束行号 {v} 必须大于等于起始行号 {info.data['start_row']}")
        return v

    @field_validator("end_column")
    @classmethod
    def validate_end_column(cls, v: int, info: Any) -> int:
        """验证结束列号必须大于等于起始列号"""
        if "start_column" in info.data and v < info.data["start_column"]:
            raise ValueError(f"结束列号 {v} 必须大于等于起始列号 {info.data['start_column']}")
        return v


# ============================================================================
# 工作表模型
# ============================================================================


class Sheet(BaseModel):
    """工作表数据"""

    name: str = Field(description="工作表名称")
    rows: List[Row] = Field(default_factory=list, description="行列表")
    merged_cells: List[MergedCell] = Field(default_factory=list, description="合并单元格列表")
    column_widths: Dict[int, float] = Field(
        default_factory=dict, description="列宽字典，键为列号（1-based），值为宽度"
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """验证工作表名称"""
        if not v or not v.strip():
            raise ValueError("工作表名称不能为空")
        if len(v) > 31:
            raise ValueError(f"工作表名称长度不能超过31个字符，当前长度: {len(v)}")
        # Excel 不允许的字符
        invalid_chars = [":", "\\", "/", "?", "*", "[", "]"]
        for char in invalid_chars:
            if char in v:
                raise ValueError(f"工作表名称不能包含字符: {char}")
        return v


# ============================================================================
# 工作簿模型
# ============================================================================


class Workbook(BaseModel):
    """工作簿数据"""

    sheets: List[Sheet] = Field(default_factory=list, description="工作表列表")
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="元数据（文件名、创建时间等）"
    )

    @field_validator("sheets")
    @classmethod
    def validate_sheets(cls, v: List[Sheet]) -> List[Sheet]:
        """验证工作表列表"""
        if not v:
            raise ValueError("工作簿必须至少包含一个工作表")
        # 检查工作表名称是否重复
        names = [sheet.name for sheet in v]
        if len(names) != len(set(names)):
            raise ValueError("工作表名称不能重复")
        return v


# ============================================================================
# 导出所有模型
# ============================================================================

__all__ = [
    "FontFormat",
    "FillFormat",
    "BorderSide",
    "BorderFormat",
    "AlignmentFormat",
    "CellFormat",
    "Cell",
    "Row",
    "MergedCell",
    "Sheet",
    "Workbook",
]
