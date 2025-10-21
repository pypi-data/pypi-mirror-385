"""
文件管理功能测试
"""

import pytest
from unittest.mock import Mock, patch

from src.mcp_excel_supabase.storage.manager import FileManager, get_manager
from src.mcp_excel_supabase.utils.errors import (
    BatchLimitError,
    SupabaseNetworkError,
)


class TestFileManager:
    """测试 FileManager 类"""

    @patch("src.mcp_excel_supabase.storage.manager.get_client")
    def test_initialization(self, mock_get_client):
        """测试管理器初始化"""
        mock_client = Mock()
        mock_get_client.return_value = mock_client

        manager = FileManager()
        assert manager.client == mock_client
        assert manager.validator is not None

    @patch("src.mcp_excel_supabase.storage.manager.get_client")
    def test_list_files_success(self, mock_get_client):
        """测试列出文件成功"""
        mock_client = Mock()
        mock_storage = Mock()
        mock_bucket = Mock()
        mock_bucket.list.return_value = [
            {"name": "file1.txt", "size": 1024},
            {"name": "file2.txt", "size": 2048},
        ]
        mock_storage.from_.return_value = mock_bucket
        mock_client.get_storage.return_value = mock_storage
        mock_get_client.return_value = mock_client

        manager = FileManager()

        files = manager.list_files(bucket_name="test_bucket", path="test/")

        # 验证结果
        assert len(files) == 2
        assert files[0]["name"] == "file1.txt"
        assert files[1]["name"] == "file2.txt"

        # 验证调用
        mock_storage.from_.assert_called_once_with("test_bucket")
        mock_bucket.list.assert_called_once_with(path="test/", limit=100, offset=0)

    @patch("src.mcp_excel_supabase.storage.manager.get_client")
    def test_list_files_with_pagination(self, mock_get_client):
        """测试带分页的列出文件"""
        mock_client = Mock()
        mock_storage = Mock()
        mock_bucket = Mock()
        mock_bucket.list.return_value = []
        mock_storage.from_.return_value = mock_bucket
        mock_client.get_storage.return_value = mock_storage
        mock_get_client.return_value = mock_client

        manager = FileManager()

        manager.list_files(bucket_name="test_bucket", limit=50, offset=100)

        # 验证调用参数
        mock_bucket.list.assert_called_once_with(path="", limit=50, offset=100)

    @patch("src.mcp_excel_supabase.storage.manager.get_client")
    def test_list_files_failure(self, mock_get_client):
        """测试列出文件失败"""
        mock_client = Mock()
        mock_storage = Mock()
        mock_bucket = Mock()
        mock_bucket.list.side_effect = Exception("List failed")
        mock_storage.from_.return_value = mock_bucket
        mock_client.get_storage.return_value = mock_storage
        mock_get_client.return_value = mock_client

        manager = FileManager()

        with pytest.raises(SupabaseNetworkError):
            manager.list_files(bucket_name="test_bucket")

    @patch("src.mcp_excel_supabase.storage.manager.get_client")
    def test_delete_file_success(self, mock_get_client):
        """测试删除单个文件成功"""
        mock_client = Mock()
        mock_storage = Mock()
        mock_bucket = Mock()
        mock_storage.from_.return_value = mock_bucket
        mock_client.get_storage.return_value = mock_storage
        mock_get_client.return_value = mock_client

        manager = FileManager()

        result = manager.delete_file(
            remote_path="test/file.txt",
            bucket_name="test_bucket",
        )

        # 验证结果
        assert result is True

        # 验证调用
        mock_storage.from_.assert_called_once_with("test_bucket")
        mock_bucket.remove.assert_called_once_with(["test/file.txt"])

    @patch("src.mcp_excel_supabase.storage.manager.get_client")
    def test_delete_file_failure(self, mock_get_client):
        """测试删除文件失败"""
        mock_client = Mock()
        mock_storage = Mock()
        mock_bucket = Mock()
        mock_bucket.remove.side_effect = Exception("Delete failed")
        mock_storage.from_.return_value = mock_bucket
        mock_client.get_storage.return_value = mock_storage
        mock_get_client.return_value = mock_client

        manager = FileManager()

        with pytest.raises(SupabaseNetworkError):
            manager.delete_file(
                remote_path="test/file.txt",
                bucket_name="test_bucket",
            )

    @patch("src.mcp_excel_supabase.storage.manager.get_client")
    def test_delete_files_success(self, mock_get_client):
        """测试批量删除文件成功"""
        mock_client = Mock()
        mock_storage = Mock()
        mock_bucket = Mock()
        mock_storage.from_.return_value = mock_bucket
        mock_client.get_storage.return_value = mock_storage
        mock_get_client.return_value = mock_client

        manager = FileManager()

        paths = ["file1.txt", "file2.txt", "file3.txt"]
        result = manager.delete_files(
            remote_paths=paths,
            bucket_name="test_bucket",
        )

        # 验证结果
        assert result["success"] is True
        assert result["deleted_count"] == 3
        assert result["paths"] == paths

        # 验证调用
        mock_bucket.remove.assert_called_once_with(paths)

    @patch("src.mcp_excel_supabase.storage.manager.get_client")
    def test_delete_files_batch_limit_exceeded(self, mock_get_client):
        """测试批量删除超限"""
        mock_client = Mock()
        mock_get_client.return_value = mock_client

        manager = FileManager()

        # 创建超过限制的文件列表
        paths = [f"file{i}.txt" for i in range(150)]

        with pytest.raises(BatchLimitError):
            manager.delete_files(
                remote_paths=paths,
                bucket_name="test_bucket",
                max_batch_size=100,
            )

    @patch("src.mcp_excel_supabase.storage.manager.get_client")
    def test_file_exists_true(self, mock_get_client):
        """测试文件存在检查（存在）"""
        mock_client = Mock()
        mock_storage = Mock()
        mock_bucket = Mock()
        mock_bucket.list.return_value = [
            {"name": "test.txt", "size": 1024},
            {"name": "other.txt", "size": 2048},
        ]
        mock_storage.from_.return_value = mock_bucket
        mock_client.get_storage.return_value = mock_storage
        mock_get_client.return_value = mock_client

        manager = FileManager()

        exists = manager.file_exists(
            remote_path="folder/test.txt",
            bucket_name="test_bucket",
        )

        assert exists is True

    @patch("src.mcp_excel_supabase.storage.manager.get_client")
    def test_file_exists_false(self, mock_get_client):
        """测试文件存在检查（不存在）"""
        mock_client = Mock()
        mock_storage = Mock()
        mock_bucket = Mock()
        mock_bucket.list.return_value = [
            {"name": "other.txt", "size": 2048},
        ]
        mock_storage.from_.return_value = mock_bucket
        mock_client.get_storage.return_value = mock_storage
        mock_get_client.return_value = mock_client

        manager = FileManager()

        exists = manager.file_exists(
            remote_path="folder/nonexistent.txt",
            bucket_name="test_bucket",
        )

        assert exists is False

    @patch("src.mcp_excel_supabase.storage.manager.get_client")
    def test_file_exists_error(self, mock_get_client):
        """测试文件存在检查出错"""
        mock_client = Mock()
        mock_storage = Mock()
        mock_bucket = Mock()
        mock_bucket.list.side_effect = Exception("List failed")
        mock_storage.from_.return_value = mock_bucket
        mock_client.get_storage.return_value = mock_storage
        mock_get_client.return_value = mock_client

        manager = FileManager()

        exists = manager.file_exists(
            remote_path="folder/test.txt",
            bucket_name="test_bucket",
        )

        # 出错时返回 False
        assert exists is False

    @patch("src.mcp_excel_supabase.storage.manager.get_client")
    def test_search_files_success(self, mock_get_client):
        """测试搜索文件成功"""
        mock_client = Mock()
        mock_storage = Mock()
        mock_bucket = Mock()
        mock_bucket.list.return_value = [
            {"name": "test1.txt", "size": 1024},
            {"name": "test2.txt", "size": 2048},
            {"name": "other.xlsx", "size": 3072},
        ]
        mock_storage.from_.return_value = mock_bucket
        mock_client.get_storage.return_value = mock_storage
        mock_get_client.return_value = mock_client

        manager = FileManager()

        # 搜索 .txt 文件
        results = manager.search_files(
            bucket_name="test_bucket",
            pattern="*.txt",
        )

        # 验证结果
        assert len(results) == 2
        assert all(".txt" in r["name"] for r in results)

    @patch("src.mcp_excel_supabase.storage.manager.get_client")
    def test_search_files_no_match(self, mock_get_client):
        """测试搜索文件无匹配"""
        mock_client = Mock()
        mock_storage = Mock()
        mock_bucket = Mock()
        mock_bucket.list.return_value = [
            {"name": "test1.txt", "size": 1024},
            {"name": "test2.txt", "size": 2048},
        ]
        mock_storage.from_.return_value = mock_bucket
        mock_client.get_storage.return_value = mock_storage
        mock_get_client.return_value = mock_client

        manager = FileManager()

        # 搜索 .xlsx 文件
        results = manager.search_files(
            bucket_name="test_bucket",
            pattern="*.xlsx",
        )

        # 验证结果
        assert len(results) == 0

    @patch("src.mcp_excel_supabase.storage.manager.get_client")
    def test_get_file_metadata_success(self, mock_get_client):
        """测试获取文件元数据成功"""
        mock_client = Mock()
        mock_storage = Mock()
        mock_bucket = Mock()
        mock_bucket.list.return_value = [
            {"name": "test.txt", "size": 1024, "created_at": "2025-01-01"},
            {"name": "other.txt", "size": 2048, "created_at": "2025-01-02"},
        ]
        mock_storage.from_.return_value = mock_bucket
        mock_client.get_storage.return_value = mock_storage
        mock_get_client.return_value = mock_client

        manager = FileManager()

        metadata = manager.get_file_metadata(
            remote_path="folder/test.txt",
            bucket_name="test_bucket",
        )

        # 验证结果
        assert metadata["name"] == "test.txt"
        assert metadata["size"] == 1024

    @patch("src.mcp_excel_supabase.storage.manager.get_client")
    def test_get_file_metadata_not_found(self, mock_get_client):
        """测试获取不存在文件的元数据"""
        mock_client = Mock()
        mock_storage = Mock()
        mock_bucket = Mock()
        mock_bucket.list.return_value = [
            {"name": "other.txt", "size": 2048},
        ]
        mock_storage.from_.return_value = mock_bucket
        mock_client.get_storage.return_value = mock_storage
        mock_get_client.return_value = mock_client

        manager = FileManager()

        with pytest.raises(SupabaseNetworkError) as exc_info:
            manager.get_file_metadata(
                remote_path="folder/nonexistent.txt",
                bucket_name="test_bucket",
            )
        assert "文件不存在" in str(exc_info.value)

    @patch("src.mcp_excel_supabase.storage.manager.get_client")
    def test_get_manager_function(self, mock_get_client):
        """测试全局 get_manager 函数"""
        mock_client = Mock()
        mock_get_client.return_value = mock_client

        manager1 = get_manager()
        manager2 = get_manager()

        assert manager1 is manager2
        assert isinstance(manager1, FileManager)
