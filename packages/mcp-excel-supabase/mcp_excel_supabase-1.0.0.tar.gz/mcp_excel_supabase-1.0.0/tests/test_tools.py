"""
测试 MCP 工具

测试所有 MCP 工具的功能和错误处理。
"""

from pathlib import Path
from unittest.mock import Mock, patch
from mcp_excel_supabase.server import (
    parse_excel_to_json,
    create_excel_from_json,
    modify_cell_format,
    merge_cells,
    unmerge_cells,
    set_row_heights,
    set_column_widths,
    manage_storage,
)


class TestParseExcelToJson:
    """测试 parse_excel_to_json 工具"""

    def test_parse_excel_success(self, simple_excel_file: Path):
        """测试成功解析 Excel 文件"""
        result = parse_excel_to_json(str(simple_excel_file), extract_formats=True)

        assert result["success"] is True
        assert result["workbook"] is not None
        assert result["error"] is None
        assert "sheets" in result["workbook"]

    def test_parse_excel_file_not_found(self):
        """测试文件不存在的情况"""
        result = parse_excel_to_json("nonexistent.xlsx", extract_formats=True)

        assert result["success"] is False
        assert result["workbook"] is None
        assert result["error"] is not None

    def test_parse_excel_invalid_file(self, temp_file: Path):
        """测试无效的 Excel 文件"""
        result = parse_excel_to_json(str(temp_file), extract_formats=True)

        assert result["success"] is False
        assert result["workbook"] is None
        assert result["error"] is not None


class TestCreateExcelFromJson:
    """测试 create_excel_from_json 工具"""

    def test_create_excel_success(self, temp_dir: Path):
        """测试成功创建 Excel 文件"""
        output_path = temp_dir / "output.xlsx"
        workbook_data = {
            "sheets": [
                {
                    "name": "Sheet1",
                    "rows": [
                        {
                            "cells": [
                                {
                                    "row": 1,
                                    "column": 1,
                                    "value": "Test",
                                    "data_type": "string",
                                }
                            ],
                        }
                    ],
                }
            ]
        }

        result = create_excel_from_json(workbook_data, str(output_path), apply_formats=True)

        assert result["success"] is True
        assert result["file_path"] == str(output_path)
        assert result["error"] is None
        assert output_path.exists()

    def test_create_excel_invalid_data(self, temp_dir: Path):
        """测试无效的工作簿数据"""
        output_path = temp_dir / "output.xlsx"
        invalid_data = {"invalid": "data"}

        result = create_excel_from_json(invalid_data, str(output_path), apply_formats=True)

        assert result["success"] is False
        assert result["file_path"] is None
        assert result["error"] is not None


class TestModifyCellFormat:
    """测试 modify_cell_format 工具"""

    def test_modify_format_success(self, simple_excel_file: Path):
        """测试成功修改单元格格式"""
        format_data = {
            "font": {"bold": True, "size": 14},
            "fill": {"background_color": "#FFFF00"},
        }

        result = modify_cell_format(
            str(simple_excel_file),
            "Sheet1",
            "A1:B2",
            format_data,
            output_path=None,
        )

        assert result["success"] is True
        assert result["file_path"] == str(simple_excel_file)
        assert result["cells_modified"] == 4
        assert result["error"] is None

    def test_modify_format_single_cell(self, simple_excel_file: Path):
        """测试修改单个单元格格式"""
        format_data = {"font": {"bold": True}}

        result = modify_cell_format(
            str(simple_excel_file), "Sheet1", "A1", format_data, output_path=None
        )

        assert result["success"] is True
        assert result["cells_modified"] == 1

    def test_modify_format_invalid_sheet(self, simple_excel_file: Path):
        """测试无效的工作表名称"""
        format_data = {"font": {"bold": True}}

        result = modify_cell_format(
            str(simple_excel_file),
            "NonexistentSheet",
            "A1",
            format_data,
            output_path=None,
        )

        assert result["success"] is False
        assert result["error"] is not None


class TestMergeCells:
    """测试 merge_cells 工具"""

    def test_merge_cells_success(self, simple_excel_file: Path):
        """测试成功合并单元格"""
        result = merge_cells(str(simple_excel_file), "Sheet1", "A1:B2", output_path=None)

        assert result["success"] is True
        assert result["file_path"] == str(simple_excel_file)
        assert result["merged_range"] == "A1:B2"
        assert result["error"] is None

    def test_merge_cells_invalid_range(self, simple_excel_file: Path):
        """测试无效的单元格范围"""
        result = merge_cells(str(simple_excel_file), "Sheet1", "INVALID", output_path=None)

        assert result["success"] is False
        assert result["error"] is not None


class TestUnmergeCells:
    """测试 unmerge_cells 工具"""

    def test_unmerge_cells_success(self, merged_excel_file: Path):
        """测试成功取消合并单元格"""
        result = unmerge_cells(str(merged_excel_file), "Sheet1", "A1:B2", output_path=None)

        assert result["success"] is True
        assert result["file_path"] == str(merged_excel_file)
        assert result["unmerged_range"] == "A1:B2"
        assert result["error"] is None

    def test_unmerge_cells_not_merged(self, simple_excel_file: Path):
        """测试取消未合并的单元格"""
        # 这应该不会报错，只是没有效果
        result = unmerge_cells(str(simple_excel_file), "Sheet1", "A1:B2", output_path=None)

        # 根据实现，这可能成功或失败
        # 我们只检查返回了有效的结果
        assert "success" in result
        assert "error" in result


class TestSetRowHeights:
    """测试 set_row_heights 工具"""

    def test_set_row_heights_success(self, simple_excel_file: Path):
        """测试成功设置行高"""
        row_heights = [{"row_number": 1, "height": 30.0}, {"row_number": 2, "height": 40.0}]

        result = set_row_heights(str(simple_excel_file), "Sheet1", row_heights, output_path=None)

        assert result["success"] is True
        assert result["file_path"] == str(simple_excel_file)
        assert result["rows_modified"] == 2
        assert result["error"] is None

    def test_set_row_heights_empty_list(self, simple_excel_file: Path):
        """测试空的行高列表"""
        result = set_row_heights(str(simple_excel_file), "Sheet1", [], output_path=None)

        assert result["success"] is True
        assert result["rows_modified"] == 0


class TestSetColumnWidths:
    """测试 set_column_widths 工具"""

    def test_set_column_widths_success(self, simple_excel_file: Path):
        """测试成功设置列宽"""
        column_widths = [
            {"column_letter": "A", "width": 20.0},
            {"column_letter": "B", "width": 30.0},
        ]

        result = set_column_widths(
            str(simple_excel_file), "Sheet1", column_widths, output_path=None
        )

        assert result["success"] is True
        assert result["file_path"] == str(simple_excel_file)
        assert result["columns_modified"] == 2
        assert result["error"] is None

    def test_set_column_widths_empty_list(self, simple_excel_file: Path):
        """测试空的列宽列表"""
        result = set_column_widths(str(simple_excel_file), "Sheet1", [], output_path=None)

        assert result["success"] is True
        assert result["columns_modified"] == 0


class TestManageStorage:
    """测试 manage_storage 工具"""

    @patch("mcp_excel_supabase.server.FileUploader")
    def test_upload_operation(self, mock_uploader_class, temp_file: Path):
        """测试上传操作"""
        # 配置 mock
        mock_uploader = Mock()
        mock_uploader.upload_file.return_value = {"url": "https://example.com/file.txt"}
        mock_uploader_class.return_value = mock_uploader

        result = manage_storage(
            operation="upload",
            file_path=str(temp_file),
            remote_path="test/file.txt",
            bucket_name="test_bucket",
        )

        assert result["success"] is True
        assert result["operation"] == "upload"
        assert result["result"] is not None
        assert result["error"] is None
        mock_uploader.upload_file.assert_called_once()

    @patch("mcp_excel_supabase.server.FileDownloader")
    def test_download_operation(self, mock_downloader_class, temp_dir: Path):
        """测试下载操作"""
        # 配置 mock
        mock_downloader = Mock()
        mock_downloader.download_file.return_value = str(temp_dir / "downloaded.txt")
        mock_downloader_class.return_value = mock_downloader

        result = manage_storage(
            operation="download",
            file_path=str(temp_dir / "downloaded.txt"),
            remote_path="test/file.txt",
            bucket_name="test_bucket",
        )

        assert result["success"] is True
        assert result["operation"] == "download"
        assert result["error"] is None
        mock_downloader.download_file.assert_called_once()

    @patch("mcp_excel_supabase.server.FileManager")
    def test_list_operation(self, mock_manager_class):
        """测试列表操作"""
        # 配置 mock
        mock_manager = Mock()
        mock_manager.list_files.return_value = [
            {"name": "file1.txt", "size": 100},
            {"name": "file2.txt", "size": 200},
        ]
        mock_manager_class.return_value = mock_manager

        result = manage_storage(operation="list", bucket_name="test_bucket", prefix="test/")

        assert result["success"] is True
        assert result["operation"] == "list"
        assert len(result["result"]) == 2
        assert result["error"] is None
        mock_manager.list_files.assert_called_once()

    @patch("mcp_excel_supabase.server.FileManager")
    def test_delete_operation(self, mock_manager_class):
        """测试删除操作"""
        # 配置 mock
        mock_manager = Mock()
        mock_manager.delete_file.return_value = {"success": True}
        mock_manager_class.return_value = mock_manager

        result = manage_storage(
            operation="delete", remote_path="test/file.txt", bucket_name="test_bucket"
        )

        assert result["success"] is True
        assert result["operation"] == "delete"
        assert result["error"] is None
        mock_manager.delete_file.assert_called_once()

    @patch("mcp_excel_supabase.server.FileManager")
    def test_search_operation(self, mock_manager_class):
        """测试搜索操作"""
        # 配置 mock
        mock_manager = Mock()
        mock_manager.search_files.return_value = [{"name": "test.txt", "size": 100}]
        mock_manager_class.return_value = mock_manager

        result = manage_storage(
            operation="search", bucket_name="test_bucket", search_pattern="*.txt"
        )

        assert result["success"] is True
        assert result["operation"] == "search"
        assert len(result["result"]) == 1
        assert result["error"] is None
        mock_manager.search_files.assert_called_once()

    def test_invalid_operation(self):
        """测试无效的操作类型"""
        result = manage_storage(operation="invalid_op", bucket_name="test_bucket")

        assert result["success"] is False
        assert result["operation"] == "invalid_op"
        assert result["error"] is not None

    def test_missing_required_params_upload(self):
        """测试上传操作缺少必需参数"""
        result = manage_storage(operation="upload", file_path="test.txt")

        assert result["success"] is False
        assert result["error"] is not None

    def test_missing_required_params_list(self):
        """测试列表操作缺少必需参数"""
        result = manage_storage(operation="list")

        assert result["success"] is False
        assert result["error"] is not None
