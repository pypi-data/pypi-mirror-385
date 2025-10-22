"""
MCP 工具包

提供 MCP 协议工具的输入输出模式定义。
"""

from mcp_excel_supabase.tools.schemas import (
    # Parse Excel
    ParseExcelInput,
    ParseExcelOutput,
    # Create Excel
    CreateExcelInput,
    CreateExcelOutput,
    # Modify Cell Format
    ModifyCellFormatInput,
    ModifyCellFormatOutput,
    # Merge Cells
    MergeCellsInput,
    MergeCellsOutput,
    # Unmerge Cells
    UnmergeCellsInput,
    UnmergeCellsOutput,
    # Set Row Heights
    SetRowHeightsInput,
    SetRowHeightsOutput,
    # Set Column Widths
    SetColumnWidthsInput,
    SetColumnWidthsOutput,
    # Manage Storage
    ManageStorageInput,
    ManageStorageOutput,
)

__all__ = [
    # Parse Excel
    "ParseExcelInput",
    "ParseExcelOutput",
    # Create Excel
    "CreateExcelInput",
    "CreateExcelOutput",
    # Modify Cell Format
    "ModifyCellFormatInput",
    "ModifyCellFormatOutput",
    # Merge Cells
    "MergeCellsInput",
    "MergeCellsOutput",
    # Unmerge Cells
    "UnmergeCellsInput",
    "UnmergeCellsOutput",
    # Set Row Heights
    "SetRowHeightsInput",
    "SetRowHeightsOutput",
    # Set Column Widths
    "SetColumnWidthsInput",
    "SetColumnWidthsOutput",
    # Manage Storage
    "ManageStorageInput",
    "ManageStorageOutput",
]
