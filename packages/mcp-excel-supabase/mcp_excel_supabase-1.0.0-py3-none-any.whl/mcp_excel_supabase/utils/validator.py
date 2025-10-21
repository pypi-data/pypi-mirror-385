"""
输入验证工具模块

提供各种输入验证功能，包括：
- 文件路径验证
- 参数类型验证
- 数据范围验证
- Excel 相关验证（单元格范围、颜色格式等）
"""

import re
from pathlib import Path
from typing import Any, Optional, List, Union, Type
from .errors import (
    FileNotFoundError,
    FileSizeError,
    InvalidParameterError,
    DataRangeError,
    InvalidCellRangeError,
    InvalidColorError,
    BatchLimitError,
)
from .logger import logger


class Validator:
    """输入验证器类"""

    # 单元格范围正则表达式（如 A1, A1:B10, Sheet1!A1:B10）
    CELL_RANGE_PATTERN = re.compile(r"^(?:([^!]+)!)?([A-Z]+\d+)(?::([A-Z]+\d+))?$", re.IGNORECASE)

    # 十六进制颜色正则表达式（如 #FF0000, #F00）
    HEX_COLOR_PATTERN = re.compile(r"^#(?:[0-9a-fA-F]{3}){1,2}$")

    # 常见颜色名称
    COLOR_NAMES = {
        "red",
        "green",
        "blue",
        "yellow",
        "orange",
        "purple",
        "pink",
        "black",
        "white",
        "gray",
        "grey",
        "brown",
        "cyan",
        "magenta",
        "lime",
        "navy",
        "teal",
        "olive",
        "maroon",
        "aqua",
        "silver",
    }

    @staticmethod
    def validate_file_path(
        file_path: Union[str, Path], must_exist: bool = True, extensions: Optional[List[str]] = None
    ) -> Path:
        """
        验证文件路径

        Args:
            file_path: 文件路径
            must_exist: 文件是否必须存在
            extensions: 允许的文件扩展名列表（如 ['.xlsx', '.xls']）

        Returns:
            Path 对象

        Raises:
            InvalidParameterError: 路径无效
            FileNotFoundError: 文件不存在（当 must_exist=True 时）
        """
        if not file_path:
            raise InvalidParameterError(
                param_name="file_path", param_value=file_path, expected="非空字符串或 Path 对象"
            )

        path = Path(file_path)

        # 检查文件是否存在
        if must_exist and not path.exists():
            raise FileNotFoundError(str(path))

        # 检查文件扩展名
        if extensions:
            if path.suffix.lower() not in [ext.lower() for ext in extensions]:
                raise InvalidParameterError(
                    param_name="file_path",
                    param_value=str(path),
                    expected=f"文件扩展名为 {', '.join(extensions)} 之一",
                )

        logger.debug(f"文件路径验证通过: {path}")
        return path

    @staticmethod
    def validate_file_size(file_path: Union[str, Path], max_size_mb: float = 1.0) -> float:
        """
        验证文件大小

        Args:
            file_path: 文件路径
            max_size_mb: 最大文件大小（MB）

        Returns:
            文件大小（MB）

        Raises:
            FileNotFoundError: 文件不存在
            FileSizeError: 文件超过大小限制
        """
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(str(path))

        size_bytes = path.stat().st_size
        size_mb = size_bytes / (1024 * 1024)

        if size_mb > max_size_mb:
            raise FileSizeError(str(path), size_mb, max_size_mb)

        logger.debug(f"文件大小验证通过: {size_mb:.2f}MB")
        return size_mb

    @staticmethod
    def validate_batch_size(count: int, max_count: int = 20, param_name: str = "文件数量") -> int:
        """
        验证批量操作数量

        Args:
            count: 实际数量
            max_count: 最大允许数量
            param_name: 参数名称（用于错误消息）

        Returns:
            验证后的数量

        Raises:
            BatchLimitError: 超过批量限制
        """
        if count > max_count:
            raise BatchLimitError(count, max_count)

        logger.debug(f"{param_name}验证通过: {count}/{max_count}")
        return count

    @staticmethod
    def validate_type(value: Any, expected_type: Union[Type, tuple], param_name: str) -> Any:
        """
        验证参数类型

        Args:
            value: 参数值
            expected_type: 期望的类型（可以是单个类型或类型元组）
            param_name: 参数名称

        Returns:
            验证后的值

        Raises:
            InvalidParameterError: 类型不匹配
        """
        if not isinstance(value, expected_type):
            if isinstance(expected_type, tuple):
                type_names = " 或 ".join(t.__name__ for t in expected_type)
            else:
                type_names = expected_type.__name__

            raise InvalidParameterError(
                param_name=param_name, param_value=value, expected=type_names
            )

        return value

    @staticmethod
    def validate_range(
        value: Union[int, float],
        param_name: str,
        min_val: Optional[Union[int, float]] = None,
        max_val: Optional[Union[int, float]] = None,
        inclusive: bool = True,
    ) -> Union[int, float]:
        """
        验证数值范围

        Args:
            value: 数值
            param_name: 参数名称
            min_val: 最小值（None 表示无限制）
            max_val: 最大值（None 表示无限制）
            inclusive: 是否包含边界值

        Returns:
            验证后的值

        Raises:
            DataRangeError: 超出范围
        """
        if min_val is not None:
            if inclusive and value < min_val:
                raise DataRangeError(param_name, value, min_val, max_val)
            elif not inclusive and value <= min_val:
                raise DataRangeError(param_name, value, min_val, max_val)

        if max_val is not None:
            if inclusive and value > max_val:
                raise DataRangeError(param_name, value, min_val, max_val)
            elif not inclusive and value >= max_val:
                raise DataRangeError(param_name, value, min_val, max_val)

        return value

    @staticmethod
    def validate_cell_range(cell_range: str) -> dict:
        """
        验证 Excel 单元格范围格式

        Args:
            cell_range: 单元格范围字符串（如 'A1', 'A1:B10', 'Sheet1!A1:B10'）

        Returns:
            包含解析结果的字典:
            {
                'sheet': str or None,  # Sheet 名称
                'start_cell': str,      # 起始单元格
                'end_cell': str or None # 结束单元格
            }

        Raises:
            InvalidCellRangeError: 单元格范围格式无效
        """
        if not cell_range or not isinstance(cell_range, str):
            raise InvalidCellRangeError(str(cell_range))

        match = Validator.CELL_RANGE_PATTERN.match(cell_range.strip())
        if not match:
            raise InvalidCellRangeError(cell_range)

        sheet_name, start_cell, end_cell = match.groups()

        result = {
            "sheet": sheet_name,
            "start_cell": start_cell.upper(),
            "end_cell": end_cell.upper() if end_cell else None,
        }

        logger.debug(f"单元格范围验证通过: {result}")
        return result

    @staticmethod
    def validate_color(color: str) -> str:
        """
        验证颜色格式

        Args:
            color: 颜色字符串（十六进制如 '#FF0000' 或颜色名称如 'red'）

        Returns:
            标准化的颜色字符串

        Raises:
            InvalidColorError: 颜色格式无效
        """
        if not color or not isinstance(color, str):
            raise InvalidColorError(str(color))

        color = color.strip()

        # 检查十六进制格式
        if Validator.HEX_COLOR_PATTERN.match(color):
            # 将 3 位十六进制扩展为 6 位
            if len(color) == 4:  # #RGB
                color = f"#{color[1]*2}{color[2]*2}{color[3]*2}"
            return color.upper()

        # 检查颜色名称
        if color.lower() in Validator.COLOR_NAMES:
            return color.lower()

        raise InvalidColorError(color)

    @staticmethod
    def validate_sheet_name(sheet_name: str) -> str:
        """
        验证 Sheet 名称

        Args:
            sheet_name: Sheet 名称

        Returns:
            验证后的 Sheet 名称

        Raises:
            InvalidParameterError: Sheet 名称无效
        """
        if not sheet_name or not isinstance(sheet_name, str):
            raise InvalidParameterError(
                param_name="sheet_name", param_value=sheet_name, expected="非空字符串"
            )

        sheet_name = sheet_name.strip()

        # Sheet 名称不能为空
        if not sheet_name:
            raise InvalidParameterError(
                param_name="sheet_name", param_value=sheet_name, expected="非空字符串"
            )

        # Sheet 名称不能包含特殊字符
        invalid_chars = [":", "\\", "/", "?", "*", "[", "]"]
        for char in invalid_chars:
            if char in sheet_name:
                raise InvalidParameterError(
                    param_name="sheet_name",
                    param_value=sheet_name,
                    expected=f"不包含以下字符: {', '.join(invalid_chars)}",
                )

        # Sheet 名称长度限制（Excel 限制为 31 个字符）
        if len(sheet_name) > 31:
            raise InvalidParameterError(
                param_name="sheet_name", param_value=sheet_name, expected="长度不超过 31 个字符"
            )

        logger.debug(f"Sheet 名称验证通过: {sheet_name}")
        return sheet_name

    @staticmethod
    def validate_non_empty(value: Any, param_name: str) -> Any:
        """
        验证值非空

        Args:
            value: 要验证的值
            param_name: 参数名称

        Returns:
            验证后的值

        Raises:
            InvalidParameterError: 值为空
        """
        if value is None or (isinstance(value, (str, list, dict)) and not value):
            raise InvalidParameterError(param_name=param_name, param_value=value, expected="非空值")

        return value


# ============================================================================
# 便捷函数
# ============================================================================


def validate_excel_file(file_path: Union[str, Path], max_size_mb: float = 1.0) -> Path:
    """
    验证 Excel 文件（组合验证）

    Args:
        file_path: 文件路径
        max_size_mb: 最大文件大小（MB）

    Returns:
        Path 对象

    Raises:
        相关验证错误
    """
    path = Validator.validate_file_path(
        file_path, must_exist=True, extensions=[".xlsx", ".xls", ".xlsm"]
    )
    Validator.validate_file_size(path, max_size_mb)
    return path
