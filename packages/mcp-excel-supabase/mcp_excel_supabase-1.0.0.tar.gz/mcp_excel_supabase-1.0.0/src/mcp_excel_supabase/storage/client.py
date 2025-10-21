"""
Supabase Storage 客户端模块

提供 Supabase Storage 的客户端封装，使用单例模式确保全局唯一实例。
支持连接初始化、验证和重试机制。
"""

import os
import time
from typing import Optional, Any, Callable

from supabase import create_client, Client
from dotenv import load_dotenv

from ..utils.errors import (
    EnvironmentVariableNotSetError,
    SupabaseAuthError,
    SupabaseNetworkError,
)
from ..utils.logger import Logger

# 加载环境变量
load_dotenv()

# 创建日志记录器
logger = Logger("storage.client")


class SupabaseClient:
    """
    Supabase Storage 客户端（单例模式）

    提供 Supabase Storage 的连接管理和基础操作。
    使用单例模式确保全局只有一个客户端实例。

    Attributes:
        url: Supabase 项目 URL
        key: Supabase Service Role Key
        client: Supabase 客户端实例
        default_bucket: 默认存储桶名称
    """

    _instance: Optional["SupabaseClient"] = None
    _initialized: bool = False

    def __new__(cls) -> "SupabaseClient":
        """单例模式：确保只创建一个实例"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """初始化 Supabase 客户端"""
        # 避免重复初始化
        if self._initialized:
            return

        logger.info("初始化 Supabase 客户端")

        # 从环境变量读取配置
        self.url = os.getenv("SUPABASE_URL")
        self.key = os.getenv("SUPABASE_KEY")
        self.default_bucket = os.getenv("DEFAULT_BUCKET", "")

        # 验证必需的环境变量
        if not self.url:
            raise EnvironmentVariableNotSetError("SUPABASE_URL")
        if not self.key:
            raise EnvironmentVariableNotSetError("SUPABASE_KEY")

        # 创建客户端
        try:
            self.client: Client = create_client(self.url, self.key)
            logger.info(f"Supabase 客户端创建成功: {self.url}")
        except Exception as e:
            logger.error(f"创建 Supabase 客户端失败: {e}")
            raise SupabaseAuthError(str(e))

        self._initialized = True

    def verify_connection(self) -> bool:
        """
        验证 Supabase 连接是否正常

        Returns:
            bool: 连接正常返回 True，否则返回 False
        """
        try:
            logger.debug("验证 Supabase 连接")
            # 尝试列出存储桶来验证连接
            buckets = self.client.storage.list_buckets()
            logger.info(f"连接验证成功，找到 {len(buckets)} 个存储桶")
            return True
        except Exception as e:
            logger.error(f"连接验证失败: {e}")
            return False

    def get_bucket_list(self) -> list[dict[str, Any]]:
        """
        获取所有存储桶列表

        Returns:
            list[dict]: 存储桶信息列表

        Raises:
            SupabaseNetworkError: 网络请求失败
        """
        try:
            logger.debug("获取存储桶列表")
            buckets: list[dict[str, Any]] = self.client.storage.list_buckets()
            logger.info(f"成功获取 {len(buckets)} 个存储桶")
            return buckets
        except Exception as e:
            logger.error(f"获取存储桶列表失败: {e}")
            raise SupabaseNetworkError(str(e))

    def bucket_exists(self, bucket_name: str) -> bool:
        """
        检查存储桶是否存在

        Args:
            bucket_name: 存储桶名称

        Returns:
            bool: 存储桶存在返回 True，否则返回 False
        """
        try:
            logger.debug(f"检查存储桶是否存在: {bucket_name}")
            buckets = self.get_bucket_list()
            exists = any(bucket.get("name") == bucket_name for bucket in buckets)
            logger.debug(f"存储桶 {bucket_name} {'存在' if exists else '不存在'}")
            return exists
        except Exception as e:
            logger.error(f"检查存储桶失败: {e}")
            return False

    def retry_operation(
        self,
        operation: Callable[..., Any],
        max_retries: int = 3,
        retry_delay: float = 1.0,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """
        带重试机制的操作执行

        Args:
            operation: 要执行的操作（可调用对象）
            max_retries: 最大重试次数
            retry_delay: 重试延迟（秒）
            *args: 操作的位置参数
            **kwargs: 操作的关键字参数

        Returns:
            操作的返回值

        Raises:
            Exception: 重试次数用尽后仍然失败
        """
        last_exception = None

        for attempt in range(max_retries):
            try:
                logger.debug(f"执行操作（尝试 {attempt + 1}/{max_retries}）")
                result = operation(*args, **kwargs)
                if attempt > 0:
                    logger.info(f"操作在第 {attempt + 1} 次尝试后成功")
                return result
            except Exception as e:
                last_exception = e
                logger.warning(f"操作失败（尝试 {attempt + 1}/{max_retries}）: {e}")

                if attempt < max_retries - 1:
                    logger.debug(f"等待 {retry_delay} 秒后重试")
                    time.sleep(retry_delay)
                    # 指数退避：每次重试延迟加倍
                    retry_delay *= 2

        # 所有重试都失败
        logger.error(f"操作在 {max_retries} 次尝试后仍然失败")
        if last_exception:
            raise last_exception
        raise Exception("操作失败但未捕获到异常")

    def get_storage(self) -> Any:
        """
        获取 Storage 对象

        Returns:
            Supabase Storage 对象
        """
        return self.client.storage

    @classmethod
    def reset_instance(cls) -> None:
        """
        重置单例实例（主要用于测试）

        警告：此方法会清除现有实例，仅在测试环境中使用
        """
        cls._instance = None
        cls._initialized = False
        logger.warning("Supabase 客户端实例已重置")


# 全局客户端实例
_global_client: Optional[SupabaseClient] = None


def get_client() -> SupabaseClient:
    """
    获取全局 Supabase 客户端实例

    Returns:
        SupabaseClient: 全局客户端实例
    """
    global _global_client
    if _global_client is None:
        _global_client = SupabaseClient()
    return _global_client
