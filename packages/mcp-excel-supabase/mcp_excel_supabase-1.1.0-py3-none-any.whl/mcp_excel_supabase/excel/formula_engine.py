"""
公式引擎模块

提供 Excel 公式解析和计算功能，基于 formulas 库实现。
"""

from typing import Any, Dict, List, Optional
import formulas
from formulas import Parser

from ..utils.errors import (
    FormulaError,
    FileReadError,
)
from ..utils.logger import logger
from ..utils.validator import Validator, validate_excel_file


class FormulaEngine:
    """
    公式引擎类

    提供 Excel 公式的解析、计算和依赖分析功能。
    基于 formulas 库实现，支持 Excel 标准公式。
    """

    def __init__(self) -> None:
        """初始化公式引擎"""
        self.parser = Parser()
        self.validator = Validator()
        logger.info("FormulaEngine 初始化完成")

    def is_formula(self, text: str) -> bool:
        """
        检查文本是否为公式

        Args:
            text: 要检查的文本

        Returns:
            bool: 如果是公式返回 True，否则返回 False
        """
        if not text or not isinstance(text, str):
            return False
        return bool(self.parser.is_formula(text))

    def parse_formula(self, formula: str) -> Any:
        """
        解析公式

        Args:
            formula: Excel 公式字符串（如 "=SUM(A1:A10)"）

        Returns:
            Any: 解析后的 AST（抽象语法树）

        Raises:
            FormulaError: 公式解析失败
        """
        try:
            self.validator.validate_non_empty(formula, "formula")

            if not self.is_formula(formula):
                raise FormulaError(
                    error_code="E301",
                    message=f"无效的公式格式: {formula}",
                    context={"formula": formula},
                    suggestion="公式必须以 = 开头",
                )

            ast, builder = self.parser.ast(formula)
            logger.debug(f"公式解析成功: {formula}")
            return ast

        except Exception as e:
            if isinstance(e, FormulaError):
                raise
            raise FormulaError(
                error_code="E302",
                message=f"公式解析失败: {str(e)}",
                context={"formula": formula, "error": str(e)},
            )

    def get_formula_dependencies(self, formula: str) -> List[str]:
        """
        获取公式依赖的单元格引用

        Args:
            formula: Excel 公式字符串

        Returns:
            List[str]: 依赖的单元格引用列表（如 ['A1', 'B2:B10']）
        """
        try:
            ast, builder = self.parser.ast(formula)

            # 从 AST 中提取单元格引用
            dependencies = []
            for token in ast:
                token_str = str(token)
                if "<Range>" in token_str:
                    # 提取范围引用（如 "A1 <Range>" -> "A1"）
                    ref = token_str.split("<")[0].strip()
                    if ref and ref not in dependencies:
                        dependencies.append(ref)

            logger.debug(f"公式依赖: {formula} -> {dependencies}")
            return dependencies

        except Exception as e:
            logger.warning(f"无法提取公式依赖: {formula} - {e}")
            return []

    def calculate_from_file(
        self,
        file_path: str,
        inputs: Optional[Dict[str, Any]] = None,
        outputs: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        从 Excel 文件加载并计算所有公式

        Args:
            file_path: Excel 文件路径
            inputs: 可选的输入值字典，用于覆盖默认值
                   格式: {"'[file.xlsx]Sheet'!A1": 10}
            outputs: 可选的输出单元格列表，只计算指定的单元格
                    格式: ["'[file.xlsx]Sheet'!C1"]

        Returns:
            Dict[str, Any]: 计算结果字典
                           键: 单元格引用（如 "'[file.xlsx]Sheet'!A1"）
                           值: 计算结果

        Raises:
            FileReadError: 文件读取失败
            FormulaError: 公式计算失败
        """
        try:
            # 验证文件
            validate_excel_file(file_path)

            logger.info(f"开始加载 Excel 文件: {file_path}")

            # 使用 formulas 库加载文件
            xl_model = formulas.ExcelModel().loads(file_path).finish()
            logger.info("Excel 模型加载完成")

            # 计算公式
            if inputs or outputs:
                result = xl_model.calculate(inputs=inputs, outputs=outputs)
            else:
                result = xl_model.calculate()

            logger.info(f"公式计算完成，共 {len(result)} 个结果")

            # 转换结果为简单字典
            results_dict = {}
            for key, value in result.items():
                # 提取实际值
                if hasattr(value, "value"):
                    # Ranges 对象
                    actual_value = value.value
                    # 如果是数组，取第一个元素
                    if hasattr(actual_value, "tolist"):
                        actual_value = actual_value.tolist()
                        if isinstance(actual_value, list) and len(actual_value) > 0:
                            if isinstance(actual_value[0], list) and len(actual_value[0]) > 0:
                                actual_value = actual_value[0][0]
                    results_dict[key] = actual_value
                else:
                    results_dict[key] = value

            return results_dict

        except Exception as e:
            if isinstance(e, (FileReadError, FormulaError)):
                raise
            raise FormulaError(
                error_code="E303",
                message=f"公式计算失败: {str(e)}",
                context={"file_path": file_path, "error": str(e)},
            )

    def detect_circular_reference(self, file_path: str) -> bool:
        """
        检测文件中是否存在循环引用

        Args:
            file_path: Excel 文件路径

        Returns:
            bool: 如果存在循环引用返回 True，否则返回 False

        Note:
            formulas 库会自动处理循环引用，这个方法主要用于检测
        """
        try:
            xl_model = formulas.ExcelModel().loads(file_path).finish()

            # 尝试计算，如果有循环引用会抛出异常
            try:
                xl_model.calculate()
                return False
            except Exception as e:
                error_msg = str(e).lower()
                if "circular" in error_msg or "cycle" in error_msg:
                    logger.warning(f"检测到循环引用: {file_path}")
                    return True
                # 其他错误不算循环引用
                return False

        except Exception as e:
            logger.error(f"循环引用检测失败: {e}")
            return False

    def get_supported_functions(self) -> List[str]:
        """
        获取支持的函数列表

        Returns:
            List[str]: 支持的函数名称列表
        """
        try:
            functions = formulas.get_functions()
            return sorted(functions.keys())
        except Exception as e:
            logger.error(f"获取函数列表失败: {e}")
            return []

    def compile_formula(self, formula: str, context: Dict[str, Any]) -> Any:
        """
        编译并执行单个公式

        Args:
            formula: 公式字符串（如 "=A1+B1"）
            context: 上下文字典，提供单元格值（如 {"A1": 10, "B1": 20}）

        Returns:
            Any: 计算结果

        Raises:
            FormulaError: 公式编译或执行失败
        """
        try:
            # 解析公式
            ast, builder = self.parser.ast(formula)

            # 编译公式
            func = builder.compile()

            # 获取输入参数
            inputs = list(func.inputs)

            # 准备参数值
            args = []
            for inp in inputs:
                if inp in context:
                    args.append(context[inp])
                else:
                    raise FormulaError(
                        error_code="E304",
                        message=f"缺少必需的输入: {inp}",
                        context={"formula": formula, "missing_input": inp},
                    )

            # 执行公式
            result = func(*args)

            logger.debug(f"公式执行成功: {formula} = {result}")
            return result

        except Exception as e:
            if isinstance(e, FormulaError):
                raise
            raise FormulaError(
                error_code="E305",
                message=f"公式执行失败: {str(e)}",
                context={"formula": formula, "context": context, "error": str(e)},
            )
