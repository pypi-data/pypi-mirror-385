"""
文件下载功能测试
"""

import pytest
from unittest.mock import Mock, patch, mock_open

from src.mcp_excel_supabase.storage.downloader import FileDownloader, get_downloader
from src.mcp_excel_supabase.utils.errors import (
    BatchLimitError,
    SupabaseNetworkError,
)


class TestFileDownloader:
    """测试 FileDownloader 类"""

    @patch("src.mcp_excel_supabase.storage.downloader.get_client")
    def test_initialization(self, mock_get_client):
        """测试下载器初始化"""
        mock_client = Mock()
        mock_get_client.return_value = mock_client

        downloader = FileDownloader()
        assert downloader.client == mock_client
        assert downloader.validator is not None

    @patch("src.mcp_excel_supabase.storage.downloader.get_client")
    @patch("builtins.open", new_callable=mock_open)
    @patch("pathlib.Path.mkdir")
    def test_download_file_success(self, mock_mkdir, mock_file, mock_get_client):
        """测试单文件下载成功"""
        # 设置 mock
        mock_client = Mock()
        mock_storage = Mock()
        mock_bucket = Mock()
        mock_bucket.download.return_value = b"test content"
        mock_storage.from_.return_value = mock_bucket
        mock_client.get_storage.return_value = mock_storage
        mock_get_client.return_value = mock_client

        # 创建下载器
        downloader = FileDownloader()

        # 下载文件
        result = downloader.download_file(
            remote_path="remote/test.txt",
            local_path="local/test.txt",
            bucket_name="test_bucket",
        )

        # 验证结果
        assert result["path"] == "local/test.txt"
        assert result["remote_path"] == "remote/test.txt"
        assert result["bucket"] == "test_bucket"
        assert result["size"] == 12  # len(b"test content")

        # 验证调用
        mock_storage.from_.assert_called_once_with("test_bucket")
        mock_bucket.download.assert_called_once_with("remote/test.txt")
        mock_file.assert_called_once_with("local/test.txt", "wb")

    @patch("src.mcp_excel_supabase.storage.downloader.get_client")
    @patch("builtins.open", new_callable=mock_open)
    @patch("pathlib.Path.mkdir")
    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.stat")
    def test_download_file_with_resume(
        self, mock_stat, mock_exists, mock_mkdir, mock_file, mock_get_client
    ):
        """测试断点续传下载"""
        mock_client = Mock()
        mock_storage = Mock()
        mock_bucket = Mock()
        mock_bucket.download.return_value = b"remaining content"
        mock_storage.from_.return_value = mock_bucket
        mock_client.get_storage.return_value = mock_storage
        mock_get_client.return_value = mock_client

        # 模拟文件已存在
        mock_exists.return_value = True
        mock_stat_result = Mock()
        mock_stat_result.st_size = 100  # 已下载100字节
        mock_stat.return_value = mock_stat_result

        downloader = FileDownloader()

        downloader.download_file(
            remote_path="remote/test.txt",
            local_path="local/test.txt",
            bucket_name="test_bucket",
            resume=True,
        )

        # 验证使用追加模式
        mock_file.assert_called_once_with("local/test.txt", "ab")

    @patch("src.mcp_excel_supabase.storage.downloader.get_client")
    @patch("builtins.open", new_callable=mock_open)
    @patch("pathlib.Path.mkdir")
    def test_download_file_with_progress_callback(self, mock_mkdir, mock_file, mock_get_client):
        """测试带进度回调的下载"""
        mock_client = Mock()
        mock_storage = Mock()
        mock_bucket = Mock()
        mock_bucket.download.return_value = b"test content"
        mock_storage.from_.return_value = mock_bucket
        mock_client.get_storage.return_value = mock_storage
        mock_get_client.return_value = mock_client

        downloader = FileDownloader()

        # 创建进度回调 mock
        progress_callback = Mock()

        downloader.download_file(
            remote_path="remote/test.txt",
            local_path="local/test.txt",
            bucket_name="test_bucket",
            progress_callback=progress_callback,
        )

        # 验证进度回调被调用
        assert progress_callback.call_count == 2  # 开始和结束
        progress_callback.assert_any_call(0, 100)  # 开始
        progress_callback.assert_any_call(12, 12)  # 完成

    @patch("src.mcp_excel_supabase.storage.downloader.get_client")
    @patch("pathlib.Path.mkdir")
    def test_download_file_failure(self, mock_mkdir, mock_get_client):
        """测试下载失败"""
        mock_client = Mock()
        mock_storage = Mock()
        mock_bucket = Mock()
        mock_bucket.download.side_effect = Exception("Download failed")
        mock_storage.from_.return_value = mock_bucket
        mock_client.get_storage.return_value = mock_storage
        mock_get_client.return_value = mock_client

        downloader = FileDownloader()

        with pytest.raises(SupabaseNetworkError):
            downloader.download_file(
                remote_path="remote/test.txt",
                local_path="local/test.txt",
                bucket_name="test_bucket",
            )

    @patch("src.mcp_excel_supabase.storage.downloader.get_client")
    @patch("src.mcp_excel_supabase.storage.downloader.FileDownloader.download_file")
    @patch("pathlib.Path.mkdir")
    def test_download_files_success(self, mock_mkdir, mock_download_file, mock_get_client):
        """测试批量下载成功"""
        mock_client = Mock()
        mock_get_client.return_value = mock_client

        # 模拟单文件下载成功
        mock_download_file.return_value = {
            "path": "local/test.txt",
            "remote_path": "remote/test.txt",
            "size": 1024,
            "bucket": "test_bucket",
        }

        downloader = FileDownloader()

        results = downloader.download_files(
            remote_paths=["file1.txt", "file2.txt", "file3.txt"],
            local_dir="local",
            bucket_name="test_bucket",
        )

        # 验证结果
        assert len(results) == 3
        assert mock_download_file.call_count == 3

    @patch("src.mcp_excel_supabase.storage.downloader.get_client")
    @patch("pathlib.Path.mkdir")
    def test_download_files_batch_limit_exceeded(self, mock_mkdir, mock_get_client):
        """测试批量下载超限"""
        mock_client = Mock()
        mock_get_client.return_value = mock_client

        downloader = FileDownloader()

        # 创建超过限制的文件列表
        remote_paths = [f"file{i}.txt" for i in range(150)]

        with pytest.raises(BatchLimitError):
            downloader.download_files(
                remote_paths=remote_paths,
                local_dir="local",
                bucket_name="test_bucket",
                max_batch_size=100,
            )

    @patch("src.mcp_excel_supabase.storage.downloader.get_client")
    @patch("src.mcp_excel_supabase.storage.downloader.FileDownloader.download_file")
    @patch("pathlib.Path.mkdir")
    def test_download_files_with_progress_callback(
        self, mock_mkdir, mock_download_file, mock_get_client
    ):
        """测试批量下载带进度回调"""
        mock_client = Mock()
        mock_get_client.return_value = mock_client

        mock_download_file.return_value = {"path": "local/test.txt", "size": 1024}

        downloader = FileDownloader()
        progress_callback = Mock()

        downloader.download_files(
            remote_paths=["file1.txt", "file2.txt"],
            local_dir="local",
            bucket_name="test_bucket",
            progress_callback=progress_callback,
        )

        # 验证进度回调被调用
        assert progress_callback.call_count == 2
        progress_callback.assert_any_call(1, 2)
        progress_callback.assert_any_call(2, 2)

    @patch("src.mcp_excel_supabase.storage.downloader.get_client")
    @patch("src.mcp_excel_supabase.storage.downloader.FileDownloader.download_file")
    @patch("pathlib.Path.mkdir")
    def test_download_files_partial_failure(self, mock_mkdir, mock_download_file, mock_get_client):
        """测试批量下载部分失败"""
        mock_client = Mock()
        mock_get_client.return_value = mock_client

        # 第二个文件下载失败
        mock_download_file.side_effect = [
            {"path": "local/file1.txt", "size": 1024},
            Exception("Download failed"),
            {"path": "local/file3.txt", "size": 1024},
        ]

        downloader = FileDownloader()

        results = downloader.download_files(
            remote_paths=["file1.txt", "file2.txt", "file3.txt"],
            local_dir="local",
            bucket_name="test_bucket",
        )

        # 验证结果
        assert len(results) == 3
        assert "error" not in results[0]
        assert "error" in results[1]
        assert "error" not in results[2]

    @patch("src.mcp_excel_supabase.storage.downloader.get_client")
    def test_get_file_info_success(self, mock_get_client):
        """测试获取文件信息成功"""
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

        downloader = FileDownloader()

        info = downloader.get_file_info(
            remote_path="remote/test.txt",
            bucket_name="test_bucket",
        )

        # 验证结果
        assert info["name"] == "test.txt"
        assert info["size"] == 1024

    @patch("src.mcp_excel_supabase.storage.downloader.get_client")
    def test_get_file_info_not_found(self, mock_get_client):
        """测试获取不存在文件的信息"""
        mock_client = Mock()
        mock_storage = Mock()
        mock_bucket = Mock()
        mock_bucket.list.return_value = [
            {"name": "other.txt", "size": 2048},
        ]
        mock_storage.from_.return_value = mock_bucket
        mock_client.get_storage.return_value = mock_storage
        mock_get_client.return_value = mock_client

        downloader = FileDownloader()

        with pytest.raises(SupabaseNetworkError) as exc_info:
            downloader.get_file_info(
                remote_path="remote/nonexistent.txt",
                bucket_name="test_bucket",
            )
        assert "文件不存在" in str(exc_info.value)

    @patch("src.mcp_excel_supabase.storage.downloader.get_client")
    def test_get_downloader_function(self, mock_get_client):
        """测试全局 get_downloader 函数"""
        mock_client = Mock()
        mock_get_client.return_value = mock_client

        downloader1 = get_downloader()
        downloader2 = get_downloader()

        assert downloader1 is downloader2
        assert isinstance(downloader1, FileDownloader)
