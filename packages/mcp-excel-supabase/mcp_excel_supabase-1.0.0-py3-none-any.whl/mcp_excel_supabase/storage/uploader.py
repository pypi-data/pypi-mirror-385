"""
Supabase Storage 文件上传模块

提供文件上传功能：
- 单文件上传
- 批量文件上传
- 上传进度跟踪
"""

from pathlib import Path
from typing import Optional, List, Dict, Any, Callable

from .client import get_client
from ..utils.errors import (
    FileNotFoundError as CustomFileNotFoundError,
    SupabaseNetworkError,
)
from ..utils.validator import Validator
from ..utils.logger import Logger

# 创建日志记录器
logger = Logger("storage.uploader")


class FileUploader:
    """
    文件上传器

    提供单文件和批量文件上传功能，支持进度跟踪。

    Attributes:
        client: Supabase 客户端实例
        validator: 输入验证器
    """

    def __init__(self) -> None:
        """初始化文件上传器"""
        self.client = get_client()
        self.validator = Validator()
        logger.info("文件上传器初始化完成")

    def upload_file(
        self,
        file_path: str,
        bucket_name: str,
        remote_path: Optional[str] = None,
        max_size_mb: float = 100.0,
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ) -> Dict[str, Any]:
        """
        上传单个文件到 Supabase Storage

        Args:
            file_path: 本地文件路径
            bucket_name: 存储桶名称
            remote_path: 远程文件路径（可选，默认使用文件名）
            max_size_mb: 最大文件大小（MB），默认 100MB
            progress_callback: 进度回调函数 callback(current, total)

        Returns:
            dict: 上传结果，包含 path、size、bucket 等信息

        Raises:
            FileNotFoundError: 文件不存在
            FileSizeError: 文件大小超限
            SupabaseNetworkError: 上传失败
        """
        logger.info(f"开始上传文件: {file_path} -> {bucket_name}/{remote_path}")

        # 验证文件路径
        self.validator.validate_file_path(file_path)

        # 验证文件大小
        self.validator.validate_file_size(file_path, max_size_mb)

        # 验证非空
        self.validator.validate_non_empty(bucket_name, "bucket_name")

        # 确定远程路径
        if remote_path is None:
            remote_path = Path(file_path).name

        # 读取文件内容
        try:
            with open(file_path, "rb") as f:
                file_content = f.read()
                file_size = len(file_content)

            logger.debug(f"文件大小: {file_size / 1024 / 1024:.2f} MB")

            # 调用进度回调（开始）
            if progress_callback:
                progress_callback(0, file_size)

            # 上传文件
            storage = self.client.get_storage()
            result = storage.from_(bucket_name).upload(
                path=remote_path,
                file=file_content,
                file_options={"content-type": self._get_content_type(file_path)},
            )

            # 调用进度回调（完成）
            if progress_callback:
                progress_callback(file_size, file_size)

            logger.info(f"文件上传成功: {remote_path}")

            return {
                "path": remote_path,
                "size": file_size,
                "bucket": bucket_name,
                "result": result,
            }

        except FileNotFoundError:
            raise CustomFileNotFoundError(file_path)
        except Exception as e:
            logger.error(f"文件上传失败: {e}")
            raise SupabaseNetworkError(str(e))

    def upload_files(
        self,
        file_paths: List[str],
        bucket_name: str,
        remote_dir: str = "",
        max_batch_size: int = 100,
        max_size_mb: float = 100.0,
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ) -> List[Dict[str, Any]]:
        """
        批量上传文件到 Supabase Storage

        Args:
            file_paths: 本地文件路径列表
            bucket_name: 存储桶名称
            remote_dir: 远程目录路径（可选）
            max_batch_size: 最大批量大小，默认 100
            max_size_mb: 单个文件最大大小（MB），默认 100MB
            progress_callback: 进度回调函数 callback(current, total)

        Returns:
            list[dict]: 上传结果列表

        Raises:
            BatchLimitError: 批量大小超限
            FileNotFoundError: 文件不存在
            FileSizeError: 文件大小超限
            SupabaseNetworkError: 上传失败
        """
        logger.info(f"开始批量上传 {len(file_paths)} 个文件到 {bucket_name}")

        # 验证批量大小
        self.validator.validate_batch_size(len(file_paths), max_batch_size)

        results = []
        total_files = len(file_paths)

        for index, file_path in enumerate(file_paths):
            # 确定远程路径
            file_name = Path(file_path).name
            if remote_dir:
                remote_path = f"{remote_dir.rstrip('/')}/{file_name}"
            else:
                remote_path = file_name

            # 上传单个文件
            try:
                result = self.upload_file(
                    file_path=file_path,
                    bucket_name=bucket_name,
                    remote_path=remote_path,
                    max_size_mb=max_size_mb,
                )
                results.append(result)

                # 调用进度回调
                if progress_callback:
                    progress_callback(index + 1, total_files)

                logger.debug(f"进度: {index + 1}/{total_files}")

            except Exception as e:
                logger.error(f"上传文件失败 {file_path}: {e}")
                results.append(
                    {
                        "path": file_path,
                        "error": str(e),
                        "success": False,
                    }
                )

        success_count = sum(1 for r in results if "error" not in r)
        logger.info(f"批量上传完成: {success_count}/{total_files} 成功")

        return results

    def _get_content_type(self, file_path: str) -> str:
        """
        根据文件扩展名获取 Content-Type

        Args:
            file_path: 文件路径

        Returns:
            str: Content-Type
        """
        ext = Path(file_path).suffix.lower()

        content_types = {
            ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            ".xls": "application/vnd.ms-excel",
            ".csv": "text/csv",
            ".json": "application/json",
            ".txt": "text/plain",
            ".pdf": "application/pdf",
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
        }

        return content_types.get(ext, "application/octet-stream")


# 全局上传器实例
_global_uploader: Optional[FileUploader] = None


def get_uploader() -> FileUploader:
    """
    获取全局文件上传器实例

    Returns:
        FileUploader: 全局上传器实例
    """
    global _global_uploader
    if _global_uploader is None:
        _global_uploader = FileUploader()
    return _global_uploader
