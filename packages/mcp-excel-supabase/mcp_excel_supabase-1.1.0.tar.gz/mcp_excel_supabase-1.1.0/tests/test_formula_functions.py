"""
测试 Excel 公式函数

测试 20+ 个常用公式函数的计算准确性
"""

import pytest
import tempfile
import os
from openpyxl import Workbook

from mcp_excel_supabase.excel.formula_engine import FormulaEngine


class TestFormulaFunctions:
    """测试各类公式函数"""

    @pytest.fixture
    def engine(self):
        """创建公式引擎实例"""
        return FormulaEngine()

    def create_excel_with_formulas(self, formulas_dict):
        """
        创建包含指定公式的 Excel 文件

        Args:
            formulas_dict: 字典，键为单元格位置，值为公式或数据

        Returns:
            str: 临时文件路径
        """
        wb = Workbook()
        ws = wb.active
        ws.title = "Test"

        for cell, value in formulas_dict.items():
            ws[cell] = value

        temp_file = tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False)
        temp_file.close()
        wb.save(temp_file.name)

        return temp_file.name

    def get_cell_value(self, results, cell_ref):
        """从结果中获取指定单元格的值"""
        for key, value in results.items():
            if cell_ref in key:
                return value
        return None

    # ========== 数学函数测试 ==========

    def test_sum_function(self, engine):
        """测试 SUM 函数"""
        file_path = self.create_excel_with_formulas(
            {"A1": 10, "A2": 20, "A3": 30, "B1": "=SUM(A1:A3)"}
        )

        try:
            results = engine.calculate_from_file(file_path)
            value = self.get_cell_value(results, "B1")
            assert value == 60.0
        finally:
            os.unlink(file_path)

    def test_average_function(self, engine):
        """测试 AVERAGE 函数"""
        file_path = self.create_excel_with_formulas(
            {"A1": 10, "A2": 20, "A3": 30, "B1": "=AVERAGE(A1:A3)"}
        )

        try:
            results = engine.calculate_from_file(file_path)
            value = self.get_cell_value(results, "B1")
            assert value == 20.0
        finally:
            os.unlink(file_path)

    def test_max_function(self, engine):
        """测试 MAX 函数"""
        file_path = self.create_excel_with_formulas(
            {"A1": 10, "A2": 50, "A3": 30, "B1": "=MAX(A1:A3)"}
        )

        try:
            results = engine.calculate_from_file(file_path)
            value = self.get_cell_value(results, "B1")
            assert value == 50
        finally:
            os.unlink(file_path)

    def test_min_function(self, engine):
        """测试 MIN 函数"""
        file_path = self.create_excel_with_formulas(
            {"A1": 10, "A2": 50, "A3": 30, "B1": "=MIN(A1:A3)"}
        )

        try:
            results = engine.calculate_from_file(file_path)
            value = self.get_cell_value(results, "B1")
            assert value == 10
        finally:
            os.unlink(file_path)

    def test_count_function(self, engine):
        """测试 COUNT 函数"""
        file_path = self.create_excel_with_formulas(
            {"A1": 10, "A2": 20, "A3": 30, "A4": "text", "B1": "=COUNT(A1:A4)"}
        )

        try:
            results = engine.calculate_from_file(file_path)
            value = self.get_cell_value(results, "B1")
            assert value == 3  # 只计数数字
        finally:
            os.unlink(file_path)

    def test_round_function(self, engine):
        """测试 ROUND 函数"""
        file_path = self.create_excel_with_formulas({"A1": 3.14159, "B1": "=ROUND(A1, 2)"})

        try:
            results = engine.calculate_from_file(file_path)
            value = self.get_cell_value(results, "B1")
            assert abs(value - 3.14) < 0.01
        finally:
            os.unlink(file_path)

    # ========== 逻辑函数测试 ==========

    def test_if_function(self, engine):
        """测试 IF 函数"""
        file_path = self.create_excel_with_formulas(
            {"A1": 10, "A2": 5, "B1": '=IF(A1>A2, "大", "小")'}
        )

        try:
            results = engine.calculate_from_file(file_path)
            value = self.get_cell_value(results, "B1")
            assert value == "大"
        finally:
            os.unlink(file_path)

    def test_and_function(self, engine):
        """测试 AND 函数"""
        file_path = self.create_excel_with_formulas({"A1": 10, "A2": 20, "B1": "=AND(A1>5, A2>15)"})

        try:
            results = engine.calculate_from_file(file_path)
            value = self.get_cell_value(results, "B1")
            assert value is True or value == 1 or value == "TRUE"
        finally:
            os.unlink(file_path)

    def test_or_function(self, engine):
        """测试 OR 函数"""
        file_path = self.create_excel_with_formulas({"A1": 10, "A2": 20, "B1": "=OR(A1>15, A2>15)"})

        try:
            results = engine.calculate_from_file(file_path)
            value = self.get_cell_value(results, "B1")
            assert value is True or value == 1 or value == "TRUE"
        finally:
            os.unlink(file_path)

    def test_not_function(self, engine):
        """测试 NOT 函数"""
        file_path = self.create_excel_with_formulas({"A1": 10, "B1": "=NOT(A1>15)"})

        try:
            results = engine.calculate_from_file(file_path)
            value = self.get_cell_value(results, "B1")
            assert value is True or value == 1 or value == "TRUE"
        finally:
            os.unlink(file_path)

    # ========== 文本函数测试 ==========

    def test_concatenate_function(self, engine):
        """测试 CONCATENATE 函数"""
        file_path = self.create_excel_with_formulas(
            {"A1": "Hello", "A2": "World", "B1": '=CONCATENATE(A1, " ", A2)'}
        )

        try:
            results = engine.calculate_from_file(file_path)
            value = self.get_cell_value(results, "B1")
            assert value == "Hello World"
        finally:
            os.unlink(file_path)

    def test_len_function(self, engine):
        """测试 LEN 函数"""
        file_path = self.create_excel_with_formulas({"A1": "Hello", "B1": "=LEN(A1)"})

        try:
            results = engine.calculate_from_file(file_path)
            value = self.get_cell_value(results, "B1")
            assert value == 5
        finally:
            os.unlink(file_path)

    def test_left_function(self, engine):
        """测试 LEFT 函数"""
        file_path = self.create_excel_with_formulas({"A1": "Hello World", "B1": "=LEFT(A1, 5)"})

        try:
            results = engine.calculate_from_file(file_path)
            value = self.get_cell_value(results, "B1")
            assert value == "Hello"
        finally:
            os.unlink(file_path)

    def test_right_function(self, engine):
        """测试 RIGHT 函数"""
        file_path = self.create_excel_with_formulas({"A1": "Hello World", "B1": "=RIGHT(A1, 5)"})

        try:
            results = engine.calculate_from_file(file_path)
            value = self.get_cell_value(results, "B1")
            assert value == "World"
        finally:
            os.unlink(file_path)

    def test_mid_function(self, engine):
        """测试 MID 函数"""
        file_path = self.create_excel_with_formulas({"A1": "Hello World", "B1": "=MID(A1, 7, 5)"})

        try:
            results = engine.calculate_from_file(file_path)
            value = self.get_cell_value(results, "B1")
            assert value == "World"
        finally:
            os.unlink(file_path)

    # ========== 组合测试 ==========

    def test_complex_formula(self, engine):
        """测试复杂公式"""
        file_path = self.create_excel_with_formulas(
            {
                "A1": 10,
                "A2": 20,
                "A3": 30,
                "B1": 5,
                "B2": 15,
                "B3": 25,
                "C1": "=SUM(A1:A3)+SUM(B1:B3)",
            }
        )

        try:
            results = engine.calculate_from_file(file_path)
            value = self.get_cell_value(results, "C1")
            # SUM(A1:A3) = 60, SUM(B1:B3) = 45, 总和 = 105
            assert value == 105.0
        finally:
            os.unlink(file_path)

    def test_nested_formula(self, engine):
        """测试嵌套公式"""
        file_path = self.create_excel_with_formulas(
            {"A1": 10, "A2": 20, "A3": 30, "B1": '=IF(AVERAGE(A1:A3)>15, "高", "低")'}
        )

        try:
            results = engine.calculate_from_file(file_path)
            value = self.get_cell_value(results, "B1")
            assert value == "高"  # AVERAGE = 20 > 15
        finally:
            os.unlink(file_path)
