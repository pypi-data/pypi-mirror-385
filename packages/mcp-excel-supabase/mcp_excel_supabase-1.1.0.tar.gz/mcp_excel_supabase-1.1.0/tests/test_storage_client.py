"""
Supabase Storage 客户端测试
"""

import os
import pytest
from unittest.mock import Mock, patch

from src.mcp_excel_supabase.storage.client import SupabaseClient, get_client
from src.mcp_excel_supabase.utils.errors import (
    EnvironmentVariableNotSetError,
    SupabaseAuthError,
    SupabaseNetworkError,
)


class TestSupabaseClient:
    """测试 SupabaseClient 类"""

    def setup_method(self):
        """每个测试方法前重置单例"""
        SupabaseClient.reset_instance()

    def teardown_method(self):
        """每个测试方法后重置单例"""
        SupabaseClient.reset_instance()

    def test_singleton_pattern(self):
        """测试单例模式"""
        client1 = SupabaseClient()
        client2 = SupabaseClient()
        assert client1 is client2

    def test_missing_url_raises_error(self):
        """测试缺少 SUPABASE_URL 时抛出异常"""
        with patch.dict(os.environ, {"SUPABASE_KEY": "test_key"}, clear=True):
            with pytest.raises(EnvironmentVariableNotSetError) as exc_info:
                SupabaseClient()
            assert "SUPABASE_URL" in str(exc_info.value)

    def test_missing_key_raises_error(self):
        """测试缺少 SUPABASE_KEY 时抛出异常"""
        with patch.dict(os.environ, {"SUPABASE_URL": "http://test.com"}, clear=True):
            with pytest.raises(EnvironmentVariableNotSetError) as exc_info:
                SupabaseClient()
            assert "SUPABASE_KEY" in str(exc_info.value)

    @patch("src.mcp_excel_supabase.storage.client.create_client")
    def test_successful_initialization(self, mock_create_client):
        """测试成功初始化"""
        mock_client = Mock()
        mock_create_client.return_value = mock_client

        with patch.dict(
            os.environ,
            {
                "SUPABASE_URL": "http://test.com",
                "SUPABASE_KEY": "test_key",
                "DEFAULT_BUCKET": "test_bucket",
            },
        ):
            client = SupabaseClient()
            assert client.url == "http://test.com"
            assert client.key == "test_key"
            assert client.default_bucket == "test_bucket"
            assert client.client == mock_client
            mock_create_client.assert_called_once_with("http://test.com", "test_key")

    @patch("src.mcp_excel_supabase.storage.client.create_client")
    def test_initialization_failure(self, mock_create_client):
        """测试初始化失败"""
        mock_create_client.side_effect = Exception("Connection failed")

        with patch.dict(
            os.environ,
            {"SUPABASE_URL": "http://test.com", "SUPABASE_KEY": "test_key"},
        ):
            with pytest.raises(SupabaseAuthError) as exc_info:
                SupabaseClient()
            assert "Connection failed" in str(exc_info.value)

    @patch("src.mcp_excel_supabase.storage.client.create_client")
    def test_verify_connection_success(self, mock_create_client):
        """测试连接验证成功"""
        mock_client = Mock()
        mock_storage = Mock()
        mock_storage.list_buckets.return_value = [{"name": "bucket1"}, {"name": "bucket2"}]
        mock_client.storage = mock_storage
        mock_create_client.return_value = mock_client

        with patch.dict(
            os.environ,
            {"SUPABASE_URL": "http://test.com", "SUPABASE_KEY": "test_key"},
        ):
            client = SupabaseClient()
            result = client.verify_connection()
            assert result is True
            mock_storage.list_buckets.assert_called_once()

    @patch("src.mcp_excel_supabase.storage.client.create_client")
    def test_verify_connection_failure(self, mock_create_client):
        """测试连接验证失败"""
        mock_client = Mock()
        mock_storage = Mock()
        mock_storage.list_buckets.side_effect = Exception("Network error")
        mock_client.storage = mock_storage
        mock_create_client.return_value = mock_client

        with patch.dict(
            os.environ,
            {"SUPABASE_URL": "http://test.com", "SUPABASE_KEY": "test_key"},
        ):
            client = SupabaseClient()
            result = client.verify_connection()
            assert result is False

    @patch("src.mcp_excel_supabase.storage.client.create_client")
    def test_get_bucket_list_success(self, mock_create_client):
        """测试获取存储桶列表成功"""
        mock_client = Mock()
        mock_storage = Mock()
        test_buckets = [{"name": "bucket1"}, {"name": "bucket2"}]
        mock_storage.list_buckets.return_value = test_buckets
        mock_client.storage = mock_storage
        mock_create_client.return_value = mock_client

        with patch.dict(
            os.environ,
            {"SUPABASE_URL": "http://test.com", "SUPABASE_KEY": "test_key"},
        ):
            client = SupabaseClient()
            buckets = client.get_bucket_list()
            assert buckets == test_buckets
            assert len(buckets) == 2

    @patch("src.mcp_excel_supabase.storage.client.create_client")
    def test_get_bucket_list_failure(self, mock_create_client):
        """测试获取存储桶列表失败"""
        mock_client = Mock()
        mock_storage = Mock()
        mock_storage.list_buckets.side_effect = Exception("Network error")
        mock_client.storage = mock_storage
        mock_create_client.return_value = mock_client

        with patch.dict(
            os.environ,
            {"SUPABASE_URL": "http://test.com", "SUPABASE_KEY": "test_key"},
        ):
            client = SupabaseClient()
            with pytest.raises(SupabaseNetworkError):
                client.get_bucket_list()

    @patch("src.mcp_excel_supabase.storage.client.create_client")
    def test_bucket_exists_true(self, mock_create_client):
        """测试存储桶存在"""
        mock_client = Mock()
        mock_storage = Mock()
        mock_storage.list_buckets.return_value = [
            {"name": "bucket1"},
            {"name": "bucket2"},
        ]
        mock_client.storage = mock_storage
        mock_create_client.return_value = mock_client

        with patch.dict(
            os.environ,
            {"SUPABASE_URL": "http://test.com", "SUPABASE_KEY": "test_key"},
        ):
            client = SupabaseClient()
            assert client.bucket_exists("bucket1") is True
            assert client.bucket_exists("bucket2") is True

    @patch("src.mcp_excel_supabase.storage.client.create_client")
    def test_bucket_exists_false(self, mock_create_client):
        """测试存储桶不存在"""
        mock_client = Mock()
        mock_storage = Mock()
        mock_storage.list_buckets.return_value = [{"name": "bucket1"}]
        mock_client.storage = mock_storage
        mock_create_client.return_value = mock_client

        with patch.dict(
            os.environ,
            {"SUPABASE_URL": "http://test.com", "SUPABASE_KEY": "test_key"},
        ):
            client = SupabaseClient()
            assert client.bucket_exists("nonexistent") is False

    @patch("src.mcp_excel_supabase.storage.client.create_client")
    def test_retry_operation_success_first_try(self, mock_create_client):
        """测试重试机制：第一次尝试成功"""
        mock_client = Mock()
        mock_create_client.return_value = mock_client

        with patch.dict(
            os.environ,
            {"SUPABASE_URL": "http://test.com", "SUPABASE_KEY": "test_key"},
        ):
            client = SupabaseClient()

            mock_operation = Mock(return_value="success")
            result = client.retry_operation(mock_operation, max_retries=3)

            assert result == "success"
            assert mock_operation.call_count == 1

    @patch("src.mcp_excel_supabase.storage.client.create_client")
    @patch("src.mcp_excel_supabase.storage.client.time.sleep")
    def test_retry_operation_success_after_retries(self, mock_sleep, mock_create_client):
        """测试重试机制：重试后成功"""
        mock_client = Mock()
        mock_create_client.return_value = mock_client

        with patch.dict(
            os.environ,
            {"SUPABASE_URL": "http://test.com", "SUPABASE_KEY": "test_key"},
        ):
            client = SupabaseClient()

            # 前两次失败，第三次成功
            mock_operation = Mock(
                side_effect=[Exception("Error 1"), Exception("Error 2"), "success"]
            )
            result = client.retry_operation(mock_operation, max_retries=3, retry_delay=0.1)

            assert result == "success"
            assert mock_operation.call_count == 3
            assert mock_sleep.call_count == 2  # 两次重试之间的延迟

    @patch("src.mcp_excel_supabase.storage.client.create_client")
    @patch("src.mcp_excel_supabase.storage.client.time.sleep")
    def test_retry_operation_all_failures(self, mock_sleep, mock_create_client):
        """测试重试机制：所有尝试都失败"""
        mock_client = Mock()
        mock_create_client.return_value = mock_client

        with patch.dict(
            os.environ,
            {"SUPABASE_URL": "http://test.com", "SUPABASE_KEY": "test_key"},
        ):
            client = SupabaseClient()

            mock_operation = Mock(side_effect=Exception("Persistent error"))

            with pytest.raises(Exception) as exc_info:
                client.retry_operation(mock_operation, max_retries=3, retry_delay=0.1)

            assert "Persistent error" in str(exc_info.value)
            assert mock_operation.call_count == 3
            assert mock_sleep.call_count == 2

    @patch("src.mcp_excel_supabase.storage.client.create_client")
    def test_get_storage(self, mock_create_client):
        """测试获取 Storage 对象"""
        mock_client = Mock()
        mock_storage = Mock()
        mock_client.storage = mock_storage
        mock_create_client.return_value = mock_client

        with patch.dict(
            os.environ,
            {"SUPABASE_URL": "http://test.com", "SUPABASE_KEY": "test_key"},
        ):
            client = SupabaseClient()
            storage = client.get_storage()
            assert storage == mock_storage

    @patch("src.mcp_excel_supabase.storage.client.create_client")
    def test_get_client_function(self, mock_create_client):
        """测试全局 get_client 函数"""
        mock_client = Mock()
        mock_create_client.return_value = mock_client

        with patch.dict(
            os.environ,
            {"SUPABASE_URL": "http://test.com", "SUPABASE_KEY": "test_key"},
        ):
            client1 = get_client()
            client2 = get_client()
            assert client1 is client2
            assert isinstance(client1, SupabaseClient)
