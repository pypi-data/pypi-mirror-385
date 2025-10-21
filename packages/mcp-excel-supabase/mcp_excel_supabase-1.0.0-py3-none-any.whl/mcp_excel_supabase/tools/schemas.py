"""
MCP 工具输入输出模式定义

定义所有 MCP 工具的输入参数和输出结果的 Pydantic 模型。
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


# ============================================================================
# Parse Excel Tool
# ============================================================================


class ParseExcelInput(BaseModel):
    """解析 Excel 文件的输入参数"""

    file_path: str = Field(..., description="Excel 文件路径（本地路径或 Supabase URL）")
    extract_formats: bool = Field(default=True, description="是否提取单元格格式信息")


class ParseExcelOutput(BaseModel):
    """解析 Excel 文件的输出结果"""

    success: bool = Field(..., description="操作是否成功")
    workbook: Optional[Dict[str, Any]] = Field(default=None, description="工作簿数据（JSON 格式）")
    error: Optional[str] = Field(default=None, description="错误信息（如果失败）")


# ============================================================================
# Create Excel Tool
# ============================================================================


class CreateExcelInput(BaseModel):
    """创建 Excel 文件的输入参数"""

    workbook_data: Dict[str, Any] = Field(..., description="工作簿数据（JSON 格式）")
    output_path: str = Field(..., description="输出文件路径")
    apply_formats: bool = Field(default=True, description="是否应用单元格格式")


class CreateExcelOutput(BaseModel):
    """创建 Excel 文件的输出结果"""

    success: bool = Field(..., description="操作是否成功")
    file_path: Optional[str] = Field(default=None, description="生成的文件路径")
    error: Optional[str] = Field(default=None, description="错误信息（如果失败）")


# ============================================================================
# Modify Cell Format Tool
# ============================================================================


class ModifyCellFormatInput(BaseModel):
    """修改单元格格式的输入参数"""

    file_path: str = Field(..., description="Excel 文件路径")
    sheet_name: str = Field(..., description="工作表名称")
    cell_range: str = Field(..., description="单元格范围，如 'A1' 或 'A1:B10'")
    format_data: Dict[str, Any] = Field(..., description="格式数据（JSON 格式）")
    output_path: Optional[str] = Field(default=None, description="输出文件路径（默认覆盖原文件）")


class ModifyCellFormatOutput(BaseModel):
    """修改单元格格式的输出结果"""

    success: bool = Field(..., description="操作是否成功")
    file_path: Optional[str] = Field(default=None, description="修改后的文件路径")
    cells_modified: Optional[int] = Field(default=None, description="修改的单元格数量")
    error: Optional[str] = Field(default=None, description="错误信息（如果失败）")


# ============================================================================
# Merge Cells Tool
# ============================================================================


class MergeCellsInput(BaseModel):
    """合并单元格的输入参数"""

    file_path: str = Field(..., description="Excel 文件路径")
    sheet_name: str = Field(..., description="工作表名称")
    cell_range: str = Field(..., description="要合并的单元格范围，如 'A1:B2'")
    output_path: Optional[str] = Field(default=None, description="输出文件路径（默认覆盖原文件）")


class MergeCellsOutput(BaseModel):
    """合并单元格的输出结果"""

    success: bool = Field(..., description="操作是否成功")
    file_path: Optional[str] = Field(default=None, description="修改后的文件路径")
    merged_range: Optional[str] = Field(default=None, description="合并的单元格范围")
    error: Optional[str] = Field(default=None, description="错误信息（如果失败）")


# ============================================================================
# Unmerge Cells Tool
# ============================================================================


class UnmergeCellsInput(BaseModel):
    """取消合并单元格的输入参数"""

    file_path: str = Field(..., description="Excel 文件路径")
    sheet_name: str = Field(..., description="工作表名称")
    cell_range: str = Field(..., description="要取消合并的单元格范围，如 'A1:B2'")
    output_path: Optional[str] = Field(default=None, description="输出文件路径（默认覆盖原文件）")


class UnmergeCellsOutput(BaseModel):
    """取消合并单元格的输出结果"""

    success: bool = Field(..., description="操作是否成功")
    file_path: Optional[str] = Field(default=None, description="修改后的文件路径")
    unmerged_range: Optional[str] = Field(default=None, description="取消合并的单元格范围")
    error: Optional[str] = Field(default=None, description="错误信息（如果失败）")


# ============================================================================
# Set Row Heights Tool
# ============================================================================


class RowHeightSpec(BaseModel):
    """行高规格"""

    row_number: int = Field(..., description="行号（从 1 开始）")
    height: float = Field(..., description="行高（单位：磅）")


class SetRowHeightsInput(BaseModel):
    """设置行高的输入参数"""

    file_path: str = Field(..., description="Excel 文件路径")
    sheet_name: str = Field(..., description="工作表名称")
    row_heights: List[RowHeightSpec] = Field(..., description="行高规格列表")
    output_path: Optional[str] = Field(default=None, description="输出文件路径（默认覆盖原文件）")


class SetRowHeightsOutput(BaseModel):
    """设置行高的输出结果"""

    success: bool = Field(..., description="操作是否成功")
    file_path: Optional[str] = Field(default=None, description="修改后的文件路径")
    rows_modified: Optional[int] = Field(default=None, description="修改的行数")
    error: Optional[str] = Field(default=None, description="错误信息（如果失败）")


# ============================================================================
# Set Column Widths Tool
# ============================================================================


class ColumnWidthSpec(BaseModel):
    """列宽规格"""

    column_letter: str = Field(..., description="列字母，如 'A', 'B', 'AA'")
    width: float = Field(..., description="列宽（单位：字符宽度）")


class SetColumnWidthsInput(BaseModel):
    """设置列宽的输入参数"""

    file_path: str = Field(..., description="Excel 文件路径")
    sheet_name: str = Field(..., description="工作表名称")
    column_widths: List[ColumnWidthSpec] = Field(..., description="列宽规格列表")
    output_path: Optional[str] = Field(default=None, description="输出文件路径（默认覆盖原文件）")


class SetColumnWidthsOutput(BaseModel):
    """设置列宽的输出结果"""

    success: bool = Field(..., description="操作是否成功")
    file_path: Optional[str] = Field(default=None, description="修改后的文件路径")
    columns_modified: Optional[int] = Field(default=None, description="修改的列数")
    error: Optional[str] = Field(default=None, description="错误信息（如果失败）")


# ============================================================================
# Manage Storage Tool
# ============================================================================


class ManageStorageInput(BaseModel):
    """管理 Supabase 存储的输入参数"""

    operation: str = Field(
        ...,
        description="操作类型：'upload', 'download', 'list', 'delete', 'search'",
    )
    file_path: Optional[str] = Field(
        default=None, description="本地文件路径（用于 upload/download）"
    )
    remote_path: Optional[str] = Field(
        default=None, description="远程文件路径（用于 upload/download/delete）"
    )
    bucket_name: Optional[str] = Field(default=None, description="存储桶名称")
    search_pattern: Optional[str] = Field(default=None, description="搜索模式（用于 search）")
    prefix: Optional[str] = Field(default=None, description="路径前缀（用于 list）")


class ManageStorageOutput(BaseModel):
    """管理 Supabase 存储的输出结果"""

    success: bool = Field(..., description="操作是否成功")
    operation: str = Field(..., description="执行的操作类型")
    result: Optional[Any] = Field(default=None, description="操作结果数据")
    error: Optional[str] = Field(default=None, description="错误信息（如果失败）")


# ============================================================================
# Set Formula Tool
# ============================================================================


class SetFormulaInput(BaseModel):
    """设置单元格公式的输入参数"""

    file_path: str = Field(..., description="Excel 文件路径")
    sheet_name: str = Field(..., description="工作表名称")
    cell: str = Field(..., description="单元格位置（如 'A1'）")
    formula: str = Field(..., description="公式字符串（如 '=SUM(A1:A10)'）")
    save: bool = Field(default=True, description="是否保存文件")


class SetFormulaOutput(BaseModel):
    """设置单元格公式的输出结果"""

    success: bool = Field(..., description="操作是否成功")
    cell: Optional[str] = Field(default=None, description="设置公式的单元格")
    formula: Optional[str] = Field(default=None, description="设置的公式")
    message: Optional[str] = Field(default=None, description="操作消息")
    error: Optional[str] = Field(default=None, description="错误信息（如果失败）")


# ============================================================================
# Recalculate Formulas Tool
# ============================================================================


class RecalculateFormulasInput(BaseModel):
    """重新计算公式的输入参数"""

    file_path: str = Field(..., description="Excel 文件路径")
    sheet_name: Optional[str] = Field(
        default=None, description="工作表名称（如果为空则计算所有工作表）"
    )


class RecalculateFormulasOutput(BaseModel):
    """重新计算公式的输出结果"""

    success: bool = Field(..., description="操作是否成功")
    count: Optional[int] = Field(default=None, description="计算的公式数量")
    results: Optional[Dict[str, Any]] = Field(default=None, description="计算结果")
    message: Optional[str] = Field(default=None, description="操作消息")
    error: Optional[str] = Field(default=None, description="错误信息（如果失败）")


# ============================================================================
# Manage Sheets Tool
# ============================================================================


class ManageSheetsInput(BaseModel):
    """管理工作表的输入参数"""

    file_path: str = Field(..., description="Excel 文件路径")
    operation: str = Field(
        ..., description="操作类型：'create', 'delete', 'rename', 'copy', 'move'"
    )
    sheet_name: Optional[str] = Field(default=None, description="工作表名称")
    new_name: Optional[str] = Field(default=None, description="新名称（用于 rename 和 copy）")
    position: Optional[int] = Field(default=None, description="位置（用于 create、copy 和 move）")


class ManageSheetsOutput(BaseModel):
    """管理工作表的输出结果"""

    success: bool = Field(..., description="操作是否成功")
    operation: str = Field(..., description="执行的操作类型")
    message: Optional[str] = Field(default=None, description="操作消息")
    error: Optional[str] = Field(default=None, description="错误信息（如果失败）")


# ============================================================================
# Merge Excel Files Tool
# ============================================================================


class MergeExcelFilesInput(BaseModel):
    """合并 Excel 文件的输入参数"""

    file_paths: List[str] = Field(..., description="要合并的 Excel 文件路径列表")
    output_path: str = Field(..., description="输出文件路径")
    handle_duplicates: str = Field(
        default="rename",
        description="重名处理策略：'rename'（重命名）、'skip'（跳过）、'overwrite'（覆盖）",
    )
    preserve_formats: bool = Field(default=True, description="是否保留格式信息")
    sheet_names: Optional[List[str]] = Field(
        default=None, description="要合并的工作表名称列表（None 表示全部）"
    )


class MergeExcelFilesOutput(BaseModel):
    """合并 Excel 文件的输出结果"""

    success: bool = Field(..., description="操作是否成功")
    merged_sheets: Optional[int] = Field(default=None, description="合并的工作表数量")
    skipped_sheets: Optional[int] = Field(default=None, description="跳过的工作表数量")
    renamed_sheets: Optional[int] = Field(default=None, description="重命名的工作表数量")
    output_path: Optional[str] = Field(default=None, description="输出文件路径")
    error: Optional[str] = Field(default=None, description="错误信息（如果失败）")
