"""
Excel operations module

This module provides functionality for:
- Parsing Excel files to JSON format
- Generating Excel files from JSON data
- Editing cell formats and styles
- Managing formulas and calculations
- Multi-sheet operations
- Stream processing for large files
"""

from .schemas import (
    Workbook,
    Sheet,
    Row,
    Cell,
    CellFormat,
    FontFormat,
    FillFormat,
    BorderFormat,
    BorderSide,
    AlignmentFormat,
    MergedCell,
)
from .parser import ExcelParser
from .generator import ExcelGenerator
from .format_extractor import FormatExtractor
from .format_applier import FormatApplier
from .data_validator import DataValidator
from .format_editor import FormatEditor
from .cell_merger import CellMerger
from .dimension_adjuster import DimensionAdjuster
from .formula_engine import FormulaEngine
from .formula_manager import FormulaManager
from .sheet_manager import SheetManager
from .file_merger import FileMerger
from .stream_processor import (
    MemoryMonitor,
    StreamReader,
    StreamWriter,
    stream_copy,
)

__all__ = [
    # Schemas
    "Workbook",
    "Sheet",
    "Row",
    "Cell",
    "CellFormat",
    "FontFormat",
    "FillFormat",
    "BorderFormat",
    "BorderSide",
    "AlignmentFormat",
    "MergedCell",
    # Core classes
    "ExcelParser",
    "ExcelGenerator",
    "FormatExtractor",
    "FormatApplier",
    "DataValidator",
    # Editing classes
    "FormatEditor",
    "CellMerger",
    "DimensionAdjuster",
    # Formula classes
    "FormulaEngine",
    "FormulaManager",
    # Sheet management classes
    "SheetManager",
    "FileMerger",
    # Stream processing classes
    "MemoryMonitor",
    "StreamReader",
    "StreamWriter",
    "stream_copy",
]
