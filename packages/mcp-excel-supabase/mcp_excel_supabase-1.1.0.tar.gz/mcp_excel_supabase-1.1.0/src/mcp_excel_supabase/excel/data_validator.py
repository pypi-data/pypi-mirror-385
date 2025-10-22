"""
数据验证器模块

提供 JSON 数据验证功能，确保数据符合 Excel 生成要求。
利用 Pydantic 模型进行结构验证，并提供友好的错误信息。
"""

from typing import Any, Dict, List, Union
from pydantic import ValidationError

from .schemas import (
    Workbook,
    Sheet,
    Cell,
    CellFormat,
    MergedCell,
)
from ..utils.errors import ValidationError as MCPValidationError
from ..utils.logger import Logger

logger = Logger("data_validator")


class DataValidator:
    """
    数据验证器类

    提供 JSON 数据验证功能，确保数据符合 Excel 生成要求。
    """

    @staticmethod
    def validate_workbook(data: Union[Dict[str, Any], Workbook]) -> Workbook:
        """
        验证工作簿数据

        Args:
            data: 工作簿数据（字典或 Workbook 对象）

        Returns:
            Workbook: 验证后的 Workbook 对象

        Raises:
            MCPValidationError: 数据验证失败
        """
        try:
            if isinstance(data, Workbook):
                return data

            logger.debug(f"验证工作簿数据，包含 {len(data.get('sheets', []))} 个工作表")
            workbook = Workbook(**data)
            logger.info(f"工作簿数据验证成功，包含 {len(workbook.sheets)} 个工作表")
            return workbook

        except ValidationError as e:
            error_details = DataValidator._format_validation_error(e)
            logger.error(f"工作簿数据验证失败: {error_details}")
            raise MCPValidationError(
                error_code="E201",
                message="工作簿数据验证失败",
                context={"errors": error_details},
                suggestion="请检查数据格式是否符合 Workbook 模型要求",
            ) from e

    @staticmethod
    def validate_sheet(data: Union[Dict[str, Any], Sheet]) -> Sheet:
        """
        验证工作表数据

        Args:
            data: 工作表数据（字典或 Sheet 对象）

        Returns:
            Sheet: 验证后的 Sheet 对象

        Raises:
            MCPValidationError: 数据验证失败
        """
        try:
            if isinstance(data, Sheet):
                return data

            logger.debug(f"验证工作表数据: {data.get('name', 'Unknown')}")
            sheet = Sheet(**data)
            logger.info(f"工作表 '{sheet.name}' 数据验证成功")
            return sheet

        except ValidationError as e:
            error_details = DataValidator._format_validation_error(e)
            logger.error(f"工作表数据验证失败: {error_details}")
            raise MCPValidationError(
                error_code="E201",
                message="工作表数据验证失败",
                context={"errors": error_details},
                suggestion="请检查数据格式是否符合 Sheet 模型要求",
            ) from e

    @staticmethod
    def validate_cell(data: Union[Dict[str, Any], Cell]) -> Cell:
        """
        验证单元格数据

        Args:
            data: 单元格数据（字典或 Cell 对象）

        Returns:
            Cell: 验证后的 Cell 对象

        Raises:
            MCPValidationError: 数据验证失败
        """
        try:
            if isinstance(data, Cell):
                return data

            cell = Cell(**data)
            return cell

        except ValidationError as e:
            error_details = DataValidator._format_validation_error(e)
            logger.error(f"单元格数据验证失败: {error_details}")
            raise MCPValidationError(
                error_code="E201",
                message="单元格数据验证失败",
                context={"errors": error_details},
                suggestion="请检查数据格式是否符合 Cell 模型要求",
            ) from e

    @staticmethod
    def validate_cell_format(data: Union[Dict[str, Any], CellFormat]) -> CellFormat:
        """
        验证单元格格式数据

        Args:
            data: 单元格格式数据（字典或 CellFormat 对象）

        Returns:
            CellFormat: 验证后的 CellFormat 对象

        Raises:
            MCPValidationError: 数据验证失败
        """
        try:
            if isinstance(data, CellFormat):
                return data

            cell_format = CellFormat(**data)
            return cell_format

        except ValidationError as e:
            error_details = DataValidator._format_validation_error(e)
            logger.error(f"单元格格式数据验证失败: {error_details}")
            raise MCPValidationError(
                error_code="E201",
                message="单元格格式数据验证失败",
                context={"errors": error_details},
                suggestion="请检查数据格式是否符合 CellFormat 模型要求",
            ) from e

    @staticmethod
    def validate_merged_cell(data: Union[Dict[str, Any], MergedCell]) -> MergedCell:
        """
        验证合并单元格数据

        Args:
            data: 合并单元格数据（字典或 MergedCell 对象）

        Returns:
            MergedCell: 验证后的 MergedCell 对象

        Raises:
            MCPValidationError: 数据验证失败
        """
        try:
            if isinstance(data, MergedCell):
                return data

            merged_cell = MergedCell(**data)
            return merged_cell

        except ValidationError as e:
            error_details = DataValidator._format_validation_error(e)
            logger.error(f"合并单元格数据验证失败: {error_details}")
            raise MCPValidationError(
                error_code="E201",
                message="合并单元格数据验证失败",
                context={"errors": error_details},
                suggestion="请检查数据格式是否符合 MergedCell 模型要求",
            ) from e

    @staticmethod
    def validate_data_type(value: Any, expected_type: str) -> bool:
        """
        验证数据类型是否匹配

        Args:
            value: 要验证的值
            expected_type: 期望的数据类型（string, number, boolean, formula, date, null）

        Returns:
            bool: 是否匹配
        """
        if expected_type == "null":
            return value is None
        elif expected_type == "string":
            return isinstance(value, str)
        elif expected_type == "number":
            return isinstance(value, (int, float)) and not isinstance(value, bool)
        elif expected_type == "boolean":
            return isinstance(value, bool)
        elif expected_type == "formula":
            return isinstance(value, str) and value.startswith("=")
        elif expected_type == "date":
            # 日期类型可以是字符串或数字（Excel 日期序列号）
            return isinstance(value, (str, int, float))
        else:
            return False

    @staticmethod
    def _format_validation_error(error: ValidationError) -> List[Dict[str, Any]]:
        """
        格式化 Pydantic 验证错误

        Args:
            error: Pydantic ValidationError

        Returns:
            List[Dict[str, Any]]: 格式化后的错误列表
        """
        formatted_errors = []
        for err in error.errors():
            formatted_errors.append(
                {
                    "field": " -> ".join(str(loc) for loc in err["loc"]),
                    "message": err["msg"],
                    "type": err["type"],
                }
            )
        return formatted_errors


# ============================================================================
# 导出
# ============================================================================

__all__ = ["DataValidator"]
