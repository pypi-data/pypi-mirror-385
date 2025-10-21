"""
Supabase Storage 文件管理模块

提供文件管理功能：
- 列出文件
- 删除文件（单个/批量）
- 搜索文件
- 获取文件元数据
- 检查文件是否存在
"""

from typing import Optional, List, Dict, Any

from .client import get_client
from ..utils.errors import (
    SupabaseNetworkError,
)
from ..utils.validator import Validator
from ..utils.logger import Logger

# 创建日志记录器
logger = Logger("storage.manager")


class FileManager:
    """
    文件管理器

    提供文件列表、删除、搜索等管理功能。

    Attributes:
        client: Supabase 客户端实例
        validator: 输入验证器
    """

    def __init__(self) -> None:
        """初始化文件管理器"""
        self.client = get_client()
        self.validator = Validator()
        logger.info("文件管理器初始化完成")

    def list_files(
        self,
        bucket_name: str,
        path: str = "",
        limit: int = 100,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """
        列出存储桶中的文件

        Args:
            bucket_name: 存储桶名称
            path: 路径前缀，默认为根目录
            limit: 返回结果数量限制，默认 100
            offset: 偏移量，默认 0

        Returns:
            list[dict]: 文件列表

        Raises:
            SupabaseNetworkError: 列出文件失败
        """
        logger.info(f"列出文件: bucket={bucket_name}, path={path}")

        # 验证非空
        self.validator.validate_non_empty(bucket_name, "bucket_name")

        try:
            storage = self.client.get_storage()

            # 列出文件
            # 注意：部分 supabase-py 版本的 list() 不支持 limit/offset 关键字参数
            files: list[dict[str, Any]] = storage.from_(bucket_name).list(
                path=path
            )

            logger.info(f"找到 {len(files)} 个文件")
            return files

        except Exception as e:
            logger.error(f"列出文件失败: {e}")
            raise SupabaseNetworkError(str(e))

    def delete_file(
        self,
        remote_path: str,
        bucket_name: str,
    ) -> bool:
        """
        删除单个文件

        Args:
            remote_path: 远程文件路径
            bucket_name: 存储桶名称

        Returns:
            bool: 删除是否成功

        Raises:
            SupabaseNetworkError: 删除失败
        """
        logger.info(f"删除文件: {bucket_name}/{remote_path}")

        # 验证非空
        self.validator.validate_non_empty(remote_path, "remote_path")
        self.validator.validate_non_empty(bucket_name, "bucket_name")

        try:
            storage = self.client.get_storage()

            # 删除文件
            storage.from_(bucket_name).remove([remote_path])

            logger.info(f"文件删除成功: {remote_path}")
            return True

        except Exception as e:
            logger.error(f"文件删除失败: {e}")
            raise SupabaseNetworkError(str(e))

    def delete_files(
        self,
        remote_paths: List[str],
        bucket_name: str,
        max_batch_size: int = 100,
    ) -> Dict[str, Any]:
        """
        批量删除文件

        Args:
            remote_paths: 远程文件路径列表
            bucket_name: 存储桶名称
            max_batch_size: 最大批量大小，默认 100

        Returns:
            dict: 删除结果，包含成功和失败的文件列表

        Raises:
            BatchLimitError: 批量大小超限
            SupabaseNetworkError: 删除失败
        """
        logger.info(f"批量删除 {len(remote_paths)} 个文件")

        # 验证批量大小
        self.validator.validate_batch_size(len(remote_paths), max_batch_size)

        try:
            storage = self.client.get_storage()

            # 批量删除
            storage.from_(bucket_name).remove(remote_paths)

            logger.info(f"批量删除成功: {len(remote_paths)} 个文件")

            return {
                "success": True,
                "deleted_count": len(remote_paths),
                "paths": remote_paths,
            }

        except Exception as e:
            logger.error(f"批量删除失败: {e}")
            raise SupabaseNetworkError(str(e))

    def file_exists(
        self,
        remote_path: str,
        bucket_name: str,
    ) -> bool:
        """
        检查文件是否存在

        Args:
            remote_path: 远程文件路径
            bucket_name: 存储桶名称

        Returns:
            bool: 文件是否存在
        """
        logger.debug(f"检查文件是否存在: {bucket_name}/{remote_path}")

        try:
            # 获取文件所在目录的文件列表
            from pathlib import Path

            parent_path = str(Path(remote_path).parent)
            file_name = Path(remote_path).name

            # 如果是根目录
            if parent_path == ".":
                parent_path = ""

            files = self.list_files(bucket_name=bucket_name, path=parent_path)

            # 检查文件是否在列表中
            for file_info in files:
                if file_info.get("name") == file_name:
                    logger.debug(f"文件存在: {remote_path}")
                    return True

            logger.debug(f"文件不存在: {remote_path}")
            return False

        except Exception as e:
            logger.error(f"检查文件存在性失败: {e}")
            return False

    def search_files(
        self,
        bucket_name: str,
        pattern: str,
        path: str = "",
    ) -> List[Dict[str, Any]]:
        """
        搜索文件（按文件名模式）

        Args:
            bucket_name: 存储桶名称
            pattern: 搜索模式（支持通配符）
            path: 搜索路径，默认为根目录

        Returns:
            list[dict]: 匹配的文件列表
        """
        logger.info(f"搜索文件: pattern={pattern}, path={path}")

        try:
            # 列出所有文件
            all_files = self.list_files(bucket_name=bucket_name, path=path)

            # 简单的模式匹配（支持 * 通配符）
            import re

            regex_pattern = pattern.replace("*", ".*")
            regex = re.compile(regex_pattern, re.IGNORECASE)

            # 过滤匹配的文件
            matched_files = [
                file_info for file_info in all_files if regex.search(file_info.get("name", ""))
            ]

            logger.info(f"找到 {len(matched_files)} 个匹配文件")
            return matched_files

        except Exception as e:
            logger.error(f"搜索文件失败: {e}")
            raise SupabaseNetworkError(str(e))

    def get_file_metadata(
        self,
        remote_path: str,
        bucket_name: str,
    ) -> Dict[str, Any]:
        """
        获取文件元数据

        Args:
            remote_path: 远程文件路径
            bucket_name: 存储桶名称

        Returns:
            dict: 文件元数据

        Raises:
            SupabaseNetworkError: 获取失败或文件不存在
        """
        logger.debug(f"获取文件元数据: {bucket_name}/{remote_path}")

        try:
            from pathlib import Path

            parent_path = str(Path(remote_path).parent)
            file_name = Path(remote_path).name

            # 如果是根目录
            if parent_path == ".":
                parent_path = ""

            files = self.list_files(bucket_name=bucket_name, path=parent_path)

            # 查找目标文件
            for file_info in files:
                if file_info.get("name") == file_name:
                    logger.debug(f"文件元数据: {file_info}")
                    return file_info

            raise SupabaseNetworkError(f"文件不存在: {remote_path}")

        except Exception as e:
            logger.error(f"获取文件元数据失败: {e}")
            raise SupabaseNetworkError(str(e))


# 全局管理器实例
_global_manager: Optional[FileManager] = None


def get_manager() -> FileManager:
    """
    获取全局文件管理器实例

    Returns:
        FileManager: 全局管理器实例
    """
    global _global_manager
    if _global_manager is None:
        _global_manager = FileManager()
    return _global_manager
