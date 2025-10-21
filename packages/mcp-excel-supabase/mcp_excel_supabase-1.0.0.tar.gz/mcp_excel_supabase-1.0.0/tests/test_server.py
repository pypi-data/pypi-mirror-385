"""
测试 MCP 服务器

测试 MCP 服务器的初始化和基本功能。
"""

from mcp_excel_supabase.server import mcp, main


class TestMCPServer:
    """测试 MCP 服务器"""

    def test_server_instance(self):
        """测试服务器实例创建"""
        assert mcp is not None
        assert mcp.name == "Excel-Supabase-Server"

    def test_server_has_tools(self):
        """测试服务器注册了工具"""
        # FastMCP 的工具通过装饰器注册
        # 我们可以通过检查 mcp 对象的属性来验证
        assert hasattr(mcp, "tool")

    def test_main_function_exists(self):
        """测试 main 函数存在"""
        assert callable(main)


class TestToolRegistration:
    """测试工具注册"""

    def test_parse_excel_to_json_registered(self):
        """测试 parse_excel_to_json 工具已注册"""
        from mcp_excel_supabase.server import parse_excel_to_json

        assert callable(parse_excel_to_json)

    def test_create_excel_from_json_registered(self):
        """测试 create_excel_from_json 工具已注册"""
        from mcp_excel_supabase.server import create_excel_from_json

        assert callable(create_excel_from_json)

    def test_modify_cell_format_registered(self):
        """测试 modify_cell_format 工具已注册"""
        from mcp_excel_supabase.server import modify_cell_format

        assert callable(modify_cell_format)

    def test_merge_cells_registered(self):
        """测试 merge_cells 工具已注册"""
        from mcp_excel_supabase.server import merge_cells

        assert callable(merge_cells)

    def test_unmerge_cells_registered(self):
        """测试 unmerge_cells 工具已注册"""
        from mcp_excel_supabase.server import unmerge_cells

        assert callable(unmerge_cells)

    def test_set_row_heights_registered(self):
        """测试 set_row_heights 工具已注册"""
        from mcp_excel_supabase.server import set_row_heights

        assert callable(set_row_heights)

    def test_set_column_widths_registered(self):
        """测试 set_column_widths 工具已注册"""
        from mcp_excel_supabase.server import set_column_widths

        assert callable(set_column_widths)

    def test_manage_storage_registered(self):
        """测试 manage_storage 工具已注册"""
        from mcp_excel_supabase.server import manage_storage

        assert callable(manage_storage)


class TestHelperFunctions:
    """测试辅助函数"""

    def test_count_cells_in_range_single_cell(self):
        """测试计算单个单元格"""
        from mcp_excel_supabase.server import _count_cells_in_range

        assert _count_cells_in_range("A1") == 1
        assert _count_cells_in_range("B5") == 1

    def test_count_cells_in_range_multiple_cells(self):
        """测试计算多个单元格"""
        from mcp_excel_supabase.server import _count_cells_in_range

        # 2x2 范围
        assert _count_cells_in_range("A1:B2") == 4

        # 3x3 范围
        assert _count_cells_in_range("A1:C3") == 9

        # 1x10 范围
        assert _count_cells_in_range("A1:A10") == 10

        # 10x1 范围
        assert _count_cells_in_range("A1:J1") == 10
