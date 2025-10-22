"""
Supabase Storage 文件下载模块

提供文件下载功能：
- 单文件下载
- 批量文件下载
- 断点续传支持
"""

from pathlib import Path
from typing import Optional, List, Dict, Any, Callable

from .client import get_client
from ..utils.errors import (
    SupabaseNetworkError,
)
from ..utils.validator import Validator
from ..utils.logger import Logger

# 创建日志记录器
logger = Logger("storage.downloader")


class FileDownloader:
    """
    文件下载器

    提供单文件和批量文件下载功能，支持断点续传。

    Attributes:
        client: Supabase 客户端实例
        validator: 输入验证器
    """

    def __init__(self) -> None:
        """初始化文件下载器"""
        self.client = get_client()
        self.validator = Validator()
        logger.info("文件下载器初始化完成")

    def download_file(
        self,
        remote_path: str,
        local_path: str,
        bucket_name: str,
        resume: bool = False,
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ) -> Dict[str, Any]:
        """
        从 Supabase Storage 下载单个文件

        Args:
            remote_path: 远程文件路径
            local_path: 本地保存路径
            bucket_name: 存储桶名称
            resume: 是否支持断点续传
            progress_callback: 进度回调函数 callback(current, total)

        Returns:
            dict: 下载结果，包含 path、size、bucket 等信息

        Raises:
            SupabaseNetworkError: 下载失败
        """
        logger.info(f"开始下载文件: {bucket_name}/{remote_path} -> {local_path}")

        # 验证非空
        self.validator.validate_non_empty(remote_path, "remote_path")
        self.validator.validate_non_empty(local_path, "local_path")
        self.validator.validate_non_empty(bucket_name, "bucket_name")

        # 创建本地目录
        local_path_obj = Path(local_path)
        local_path_obj.parent.mkdir(parents=True, exist_ok=True)

        # 检查是否支持断点续传
        start_byte = 0
        if resume and local_path_obj.exists():
            start_byte = local_path_obj.stat().st_size
            logger.info(f"断点续传：从字节 {start_byte} 开始")

        try:
            # 下载文件
            storage = self.client.get_storage()

            # 调用进度回调（开始）
            if progress_callback:
                progress_callback(0, 100)

            # 下载文件内容
            response = storage.from_(bucket_name).download(remote_path)

            # 写入文件
            mode = "ab" if resume and start_byte > 0 else "wb"
            with open(local_path, mode) as f:
                f.write(response)

            file_size = len(response)

            # 调用进度回调（完成）
            if progress_callback:
                progress_callback(file_size, file_size)

            logger.info(f"文件下载成功: {local_path} ({file_size / 1024 / 1024:.2f} MB)")

            return {
                "path": local_path,
                "remote_path": remote_path,
                "size": file_size,
                "bucket": bucket_name,
            }

        except Exception as e:
            logger.error(f"文件下载失败: {e}")
            raise SupabaseNetworkError(str(e))

    def download_files(
        self,
        remote_paths: List[str],
        local_dir: str,
        bucket_name: str,
        max_batch_size: int = 100,
        resume: bool = False,
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ) -> List[Dict[str, Any]]:
        """
        批量下载文件从 Supabase Storage

        Args:
            remote_paths: 远程文件路径列表
            local_dir: 本地保存目录
            bucket_name: 存储桶名称
            max_batch_size: 最大批量大小，默认 100
            resume: 是否支持断点续传
            progress_callback: 进度回调函数 callback(current, total)

        Returns:
            list[dict]: 下载结果列表

        Raises:
            BatchLimitError: 批量大小超限
            SupabaseNetworkError: 下载失败
        """
        logger.info(f"开始批量下载 {len(remote_paths)} 个文件到 {local_dir}")

        # 验证批量大小
        self.validator.validate_batch_size(len(remote_paths), max_batch_size)

        # 创建本地目录
        local_dir_obj = Path(local_dir)
        local_dir_obj.mkdir(parents=True, exist_ok=True)

        results = []
        total_files = len(remote_paths)

        for index, remote_path in enumerate(remote_paths):
            # 确定本地路径
            file_name = Path(remote_path).name
            local_path = str(local_dir_obj / file_name)

            # 下载单个文件
            try:
                result = self.download_file(
                    remote_path=remote_path,
                    local_path=local_path,
                    bucket_name=bucket_name,
                    resume=resume,
                )
                results.append(result)

                # 调用进度回调
                if progress_callback:
                    progress_callback(index + 1, total_files)

                logger.debug(f"进度: {index + 1}/{total_files}")

            except Exception as e:
                logger.error(f"下载文件失败 {remote_path}: {e}")
                results.append(
                    {
                        "remote_path": remote_path,
                        "error": str(e),
                        "success": False,
                    }
                )

        success_count = sum(1 for r in results if "error" not in r)
        logger.info(f"批量下载完成: {success_count}/{total_files} 成功")

        return results

    def get_file_info(
        self,
        remote_path: str,
        bucket_name: str,
    ) -> Dict[str, Any]:
        """
        获取远程文件信息（不下载）

        Args:
            remote_path: 远程文件路径
            bucket_name: 存储桶名称

        Returns:
            dict: 文件信息

        Raises:
            SupabaseNetworkError: 获取失败
        """
        logger.debug(f"获取文件信息: {bucket_name}/{remote_path}")

        try:
            storage = self.client.get_storage()

            # 获取文件列表（包含该文件）
            files: list[dict[str, Any]] = storage.from_(bucket_name).list(
                path=str(Path(remote_path).parent)
            )

            # 查找目标文件
            file_name = Path(remote_path).name
            for file_info in files:
                if file_info.get("name") == file_name:
                    logger.debug(f"文件信息: {file_info}")
                    return file_info

            raise SupabaseNetworkError(f"文件不存在: {remote_path}")

        except Exception as e:
            logger.error(f"获取文件信息失败: {e}")
            raise SupabaseNetworkError(str(e))


# 全局下载器实例
_global_downloader: Optional[FileDownloader] = None


def get_downloader() -> FileDownloader:
    """
    获取全局文件下载器实例

    Returns:
        FileDownloader: 全局下载器实例
    """
    global _global_downloader
    if _global_downloader is None:
        _global_downloader = FileDownloader()
    return _global_downloader
