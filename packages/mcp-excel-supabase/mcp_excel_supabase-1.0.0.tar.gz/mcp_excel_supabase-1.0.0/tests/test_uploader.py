"""
文件上传功能测试
"""

import pytest
from unittest.mock import Mock, patch, mock_open

from src.mcp_excel_supabase.storage.uploader import FileUploader, get_uploader
from src.mcp_excel_supabase.utils.errors import (
    FileNotFoundError as CustomFileNotFoundError,
    FileSizeError,
    BatchLimitError,
)


class TestFileUploader:
    """测试 FileUploader 类"""

    @patch("src.mcp_excel_supabase.storage.uploader.get_client")
    def test_initialization(self, mock_get_client):
        """测试上传器初始化"""
        mock_client = Mock()
        mock_get_client.return_value = mock_client

        uploader = FileUploader()
        assert uploader.client == mock_client
        assert uploader.validator is not None

    @patch("src.mcp_excel_supabase.storage.uploader.get_client")
    @patch("builtins.open", new_callable=mock_open, read_data=b"test content")
    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.stat")
    def test_upload_file_success(self, mock_stat, mock_exists, mock_file, mock_get_client):
        """测试单文件上传成功"""
        # 设置 mock
        mock_client = Mock()
        mock_storage = Mock()
        mock_bucket = Mock()
        mock_bucket.upload.return_value = {"path": "test.txt"}
        mock_storage.from_.return_value = mock_bucket
        mock_client.get_storage.return_value = mock_storage
        mock_get_client.return_value = mock_client

        # 模拟文件存在且大小合适
        mock_exists.return_value = True
        mock_stat_result = Mock()
        mock_stat_result.st_size = 1024  # 1KB
        mock_stat.return_value = mock_stat_result

        # 创建上传器
        uploader = FileUploader()

        # 上传文件
        result = uploader.upload_file(
            file_path="test.txt",
            bucket_name="test_bucket",
            remote_path="remote/test.txt",
        )

        # 验证结果
        assert result["path"] == "remote/test.txt"
        assert result["bucket"] == "test_bucket"
        assert "size" in result

        # 验证调用
        mock_storage.from_.assert_called_once_with("test_bucket")
        mock_bucket.upload.assert_called_once()

    @patch("src.mcp_excel_supabase.storage.uploader.get_client")
    @patch("pathlib.Path.exists")
    def test_upload_file_not_found(self, mock_exists, mock_get_client):
        """测试上传不存在的文件"""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_exists.return_value = False

        uploader = FileUploader()

        with pytest.raises(CustomFileNotFoundError):
            uploader.upload_file(
                file_path="nonexistent.txt",
                bucket_name="test_bucket",
            )

    @patch("src.mcp_excel_supabase.storage.uploader.get_client")
    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.stat")
    def test_upload_file_size_exceeded(self, mock_stat, mock_exists, mock_get_client):
        """测试上传超大文件"""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_exists.return_value = True
        mock_stat_result = Mock()
        mock_stat_result.st_size = 200 * 1024 * 1024  # 200MB
        mock_stat.return_value = mock_stat_result

        uploader = FileUploader()

        with pytest.raises(FileSizeError):
            uploader.upload_file(
                file_path="large.txt",
                bucket_name="test_bucket",
                max_size_mb=100.0,
            )

    @patch("src.mcp_excel_supabase.storage.uploader.get_client")
    @patch("builtins.open", new_callable=mock_open, read_data=b"test content")
    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.stat")
    def test_upload_file_with_progress_callback(
        self, mock_stat, mock_exists, mock_file, mock_get_client
    ):
        """测试带进度回调的上传"""
        mock_client = Mock()
        mock_storage = Mock()
        mock_bucket = Mock()
        mock_bucket.upload.return_value = {"path": "test.txt"}
        mock_storage.from_.return_value = mock_bucket
        mock_client.get_storage.return_value = mock_storage
        mock_get_client.return_value = mock_client

        mock_exists.return_value = True
        mock_stat_result = Mock()
        mock_stat_result.st_size = 1024
        mock_stat.return_value = mock_stat_result

        uploader = FileUploader()

        # 创建进度回调 mock
        progress_callback = Mock()

        uploader.upload_file(
            file_path="test.txt",
            bucket_name="test_bucket",
            progress_callback=progress_callback,
        )

        # 验证进度回调被调用
        assert progress_callback.call_count == 2  # 开始和结束
        progress_callback.assert_any_call(0, 12)  # 开始
        progress_callback.assert_any_call(12, 12)  # 完成

    @patch("src.mcp_excel_supabase.storage.uploader.get_client")
    @patch("builtins.open", new_callable=mock_open, read_data=b"test content")
    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.stat")
    def test_upload_file_default_remote_path(
        self, mock_stat, mock_exists, mock_file, mock_get_client
    ):
        """测试使用默认远程路径"""
        mock_client = Mock()
        mock_storage = Mock()
        mock_bucket = Mock()
        mock_bucket.upload.return_value = {"path": "test.txt"}
        mock_storage.from_.return_value = mock_bucket
        mock_client.get_storage.return_value = mock_storage
        mock_get_client.return_value = mock_client

        mock_exists.return_value = True
        mock_stat_result = Mock()
        mock_stat_result.st_size = 1024
        mock_stat.return_value = mock_stat_result

        uploader = FileUploader()

        result = uploader.upload_file(
            file_path="test.txt",
            bucket_name="test_bucket",
            # 不指定 remote_path
        )

        # 应该使用文件名作为远程路径
        assert result["path"] == "test.txt"

    @patch("src.mcp_excel_supabase.storage.uploader.get_client")
    @patch("src.mcp_excel_supabase.storage.uploader.FileUploader.upload_file")
    def test_upload_files_success(self, mock_upload_file, mock_get_client):
        """测试批量上传成功"""
        mock_client = Mock()
        mock_get_client.return_value = mock_client

        # 模拟单文件上传成功
        mock_upload_file.return_value = {
            "path": "test.txt",
            "size": 1024,
            "bucket": "test_bucket",
        }

        uploader = FileUploader()

        results = uploader.upload_files(
            file_paths=["file1.txt", "file2.txt", "file3.txt"],
            bucket_name="test_bucket",
            remote_dir="uploads",
        )

        # 验证结果
        assert len(results) == 3
        assert mock_upload_file.call_count == 3

    @patch("src.mcp_excel_supabase.storage.uploader.get_client")
    def test_upload_files_batch_limit_exceeded(self, mock_get_client):
        """测试批量上传超限"""
        mock_client = Mock()
        mock_get_client.return_value = mock_client

        uploader = FileUploader()

        # 创建超过限制的文件列表
        file_paths = [f"file{i}.txt" for i in range(150)]

        with pytest.raises(BatchLimitError):
            uploader.upload_files(
                file_paths=file_paths,
                bucket_name="test_bucket",
                max_batch_size=100,
            )

    @patch("src.mcp_excel_supabase.storage.uploader.get_client")
    @patch("src.mcp_excel_supabase.storage.uploader.FileUploader.upload_file")
    def test_upload_files_with_progress_callback(self, mock_upload_file, mock_get_client):
        """测试批量上传带进度回调"""
        mock_client = Mock()
        mock_get_client.return_value = mock_client

        mock_upload_file.return_value = {"path": "test.txt", "size": 1024}

        uploader = FileUploader()
        progress_callback = Mock()

        uploader.upload_files(
            file_paths=["file1.txt", "file2.txt"],
            bucket_name="test_bucket",
            progress_callback=progress_callback,
        )

        # 验证进度回调被调用
        assert progress_callback.call_count == 2
        progress_callback.assert_any_call(1, 2)
        progress_callback.assert_any_call(2, 2)

    @patch("src.mcp_excel_supabase.storage.uploader.get_client")
    @patch("src.mcp_excel_supabase.storage.uploader.FileUploader.upload_file")
    def test_upload_files_partial_failure(self, mock_upload_file, mock_get_client):
        """测试批量上传部分失败"""
        mock_client = Mock()
        mock_get_client.return_value = mock_client

        # 第二个文件上传失败
        mock_upload_file.side_effect = [
            {"path": "file1.txt", "size": 1024},
            Exception("Upload failed"),
            {"path": "file3.txt", "size": 1024},
        ]

        uploader = FileUploader()

        results = uploader.upload_files(
            file_paths=["file1.txt", "file2.txt", "file3.txt"],
            bucket_name="test_bucket",
        )

        # 验证结果
        assert len(results) == 3
        assert "error" not in results[0]
        assert "error" in results[1]
        assert "error" not in results[2]

    @patch("src.mcp_excel_supabase.storage.uploader.get_client")
    def test_get_content_type(self, mock_get_client):
        """测试获取 Content-Type"""
        mock_client = Mock()
        mock_get_client.return_value = mock_client

        uploader = FileUploader()

        assert (
            uploader._get_content_type("test.xlsx")
            == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        assert uploader._get_content_type("test.xls") == "application/vnd.ms-excel"
        assert uploader._get_content_type("test.csv") == "text/csv"
        assert uploader._get_content_type("test.json") == "application/json"
        assert uploader._get_content_type("test.txt") == "text/plain"
        assert uploader._get_content_type("test.unknown") == "application/octet-stream"

    @patch("src.mcp_excel_supabase.storage.uploader.get_client")
    def test_get_uploader_function(self, mock_get_client):
        """测试全局 get_uploader 函数"""
        mock_client = Mock()
        mock_get_client.return_value = mock_client

        uploader1 = get_uploader()
        uploader2 = get_uploader()

        assert uploader1 is uploader2
        assert isinstance(uploader1, FileUploader)
