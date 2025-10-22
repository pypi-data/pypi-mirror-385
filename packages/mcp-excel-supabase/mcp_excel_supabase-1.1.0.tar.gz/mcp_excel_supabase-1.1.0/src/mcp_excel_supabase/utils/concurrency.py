"""
并发处理模块

提供并发处理工具：
- 线程池管理器
- 批量操作并发化
- 异步I/O包装器
- 进度跟踪
"""

import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed, Future
from typing import Any, Callable, Dict, List, Optional, Tuple, TypeVar

from .logger import Logger

logger = Logger("concurrency")

T = TypeVar("T")
R = TypeVar("R")


class ThreadPoolManager:
    """
    线程池管理器

    管理线程池的创建、使用和销毁
    """

    def __init__(
        self, max_workers: Optional[int] = None, thread_name_prefix: str = "Worker"
    ) -> None:
        """
        初始化线程池管理器

        Args:
            max_workers: 最大工作线程数，None表示使用CPU核心数*5
            thread_name_prefix: 线程名称前缀
        """
        self.max_workers = max_workers
        self.thread_name_prefix = thread_name_prefix
        self._executor: Optional[ThreadPoolExecutor] = None
        self._lock = threading.Lock()

    def __enter__(self) -> "ThreadPoolManager":
        """上下文管理器入口"""
        self.start()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """上下文管理器出口"""
        self.shutdown()

    def start(self) -> None:
        """启动线程池"""
        with self._lock:
            if self._executor is None:
                self._executor = ThreadPoolExecutor(
                    max_workers=self.max_workers,
                    thread_name_prefix=self.thread_name_prefix,
                )
                logger.info(f"线程池已启动 (max_workers={self.max_workers or 'auto'})")

    def shutdown(self, wait: bool = True) -> None:
        """
        关闭线程池

        Args:
            wait: 是否等待所有任务完成
        """
        with self._lock:
            if self._executor is not None:
                self._executor.shutdown(wait=wait)
                self._executor = None
                logger.info("线程池已关闭")

    def submit(self, func: Callable[..., R], *args: Any, **kwargs: Any) -> Future[R]:
        """
        提交任务到线程池

        Args:
            func: 要执行的函数
            *args: 位置参数
            **kwargs: 关键字参数

        Returns:
            Future对象
        """
        if self._executor is None:
            self.start()
        assert self._executor is not None
        return self._executor.submit(func, *args, **kwargs)

    def map(
        self,
        func: Callable[[T], R],
        items: List[T],
        timeout: Optional[float] = None,
    ) -> List[R]:
        """
        并发映射操作

        Args:
            func: 映射函数
            items: 输入项列表
            timeout: 超时时间（秒）

        Returns:
            结果列表
        """
        if self._executor is None:
            self.start()
        assert self._executor is not None
        return list(self._executor.map(func, items, timeout=timeout))


class ConcurrentExecutor:
    """
    并发执行器

    提供批量操作并发化的高级接口
    """

    @staticmethod
    def map_concurrent(
        func: Callable[[T], R],
        items: List[T],
        max_workers: Optional[int] = None,
        timeout: Optional[float] = None,
        show_progress: bool = False,
    ) -> List[R]:
        """
        并发映射操作

        Args:
            func: 映射函数
            items: 输入项列表
            max_workers: 最大工作线程数
            timeout: 超时时间（秒）
            show_progress: 是否显示进度

        Returns:
            结果列表（保持输入顺序）

        Example:
            results = ConcurrentExecutor.map_concurrent(
                process_file,
                file_list,
                max_workers=4
            )
        """
        if not items:
            return []

        start_time = time.time()

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 提交所有任务，保持索引映射
            future_to_index = {executor.submit(func, item): i for i, item in enumerate(items)}

            # 使用字典存储结果，保持顺序
            results_dict: Dict[int, R] = {}
            completed = 0
            total = len(items)

            for future in as_completed(future_to_index, timeout=timeout):
                try:
                    result = future.result()
                    index = future_to_index[future]
                    results_dict[index] = result
                    completed += 1

                    if show_progress:
                        progress = (completed / total) * 100
                        logger.info(f"进度: {completed}/{total} ({progress:.1f}%)")

                except Exception as e:
                    index = future_to_index[future]
                    item = items[index]
                    logger.error(f"处理项目失败: {item}, 错误: {str(e)}")
                    raise

        elapsed = time.time() - start_time
        logger.info(
            f"并发处理完成: {total}个项目, 耗时{elapsed:.2f}秒, " f"平均{elapsed/total:.3f}秒/项"
        )

        # 按索引顺序返回结果
        return [results_dict[i] for i in range(len(items))]

    @staticmethod
    def map_concurrent_with_errors(
        func: Callable[[T], R],
        items: List[T],
        max_workers: Optional[int] = None,
        timeout: Optional[float] = None,
    ) -> Tuple[List[R], List[Tuple[T, Exception]]]:
        """
        并发映射操作（容错版本）

        Args:
            func: 映射函数
            items: 输入项列表
            max_workers: 最大工作线程数
            timeout: 超时时间（秒）

        Returns:
            (成功结果列表（保持输入顺序）, 失败项目列表)

        Example:
            results, errors = ConcurrentExecutor.map_concurrent_with_errors(
                process_file,
                file_list
            )
        """
        if not items:
            return [], []

        results_dict: Dict[int, R] = {}
        errors: List[Tuple[T, Exception]] = []

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_index = {executor.submit(func, item): i for i, item in enumerate(items)}

            for future in as_completed(future_to_index, timeout=timeout):
                index = future_to_index[future]
                item = items[index]
                try:
                    result = future.result()
                    results_dict[index] = result
                except Exception as e:
                    logger.warning(f"处理项目失败: {item}, 错误: {str(e)}")
                    errors.append((item, e))

        logger.info(f"并发处理完成: 成功{len(results_dict)}个, 失败{len(errors)}个")

        # 按索引顺序返回成功的结果
        results = [results_dict[i] for i in sorted(results_dict.keys())]
        return results, errors

    @staticmethod
    def batch_process(
        func: Callable[[List[T]], R],
        items: List[T],
        batch_size: int,
        max_workers: Optional[int] = None,
    ) -> List[R]:
        """
        批量并发处理

        将大列表分批处理，每批并发执行

        Args:
            func: 批处理函数（接受列表，返回结果）
            items: 输入项列表
            batch_size: 每批大小
            max_workers: 最大工作线程数

        Returns:
            结果列表

        Example:
            results = ConcurrentExecutor.batch_process(
                process_batch,
                large_list,
                batch_size=100,
                max_workers=4
            )
        """
        if not items:
            return []

        # 分批
        batches = [items[i : i + batch_size] for i in range(0, len(items), batch_size)]

        logger.info(f"批量处理: {len(items)}个项目, 分为{len(batches)}批, " f"每批{batch_size}个")

        # 并发处理每批
        return ConcurrentExecutor.map_concurrent(func, batches, max_workers=max_workers)


class ProgressTracker:
    """
    进度跟踪器

    跟踪并发任务的进度
    """

    def __init__(self, total: int, description: str = "Processing") -> None:
        """
        初始化进度跟踪器

        Args:
            total: 总任务数
            description: 任务描述
        """
        self.total = total
        self.description = description
        self.completed = 0
        self.failed = 0
        self._lock = threading.Lock()
        self.start_time = time.time()

    def update(self, success: bool = True) -> None:
        """
        更新进度

        Args:
            success: 是否成功
        """
        with self._lock:
            if success:
                self.completed += 1
            else:
                self.failed += 1

            total_processed = self.completed + self.failed
            progress = (total_processed / self.total) * 100
            elapsed = time.time() - self.start_time
            rate = total_processed / elapsed if elapsed > 0 else 0

            logger.info(
                f"{self.description}: {total_processed}/{self.total} "
                f"({progress:.1f}%), 成功{self.completed}, 失败{self.failed}, "
                f"速率{rate:.1f}项/秒"
            )

    def get_stats(self) -> Dict[str, Any]:
        """
        获取统计信息

        Returns:
            统计信息字典
        """
        with self._lock:
            elapsed = time.time() - self.start_time
            total_processed = self.completed + self.failed
            rate = total_processed / elapsed if elapsed > 0 else 0

            return {
                "total": self.total,
                "completed": self.completed,
                "failed": self.failed,
                "progress": (total_processed / self.total) * 100,
                "elapsed": elapsed,
                "rate": rate,
            }


# 全局线程池管理器
_global_pool: Optional[ThreadPoolManager] = None
_global_pool_lock = threading.Lock()


def get_global_pool(max_workers: Optional[int] = None) -> ThreadPoolManager:
    """
    获取全局线程池管理器

    Args:
        max_workers: 最大工作线程数

    Returns:
        ThreadPoolManager实例
    """
    global _global_pool
    with _global_pool_lock:
        if _global_pool is None:
            _global_pool = ThreadPoolManager(max_workers=max_workers)
            _global_pool.start()
        return _global_pool


def shutdown_global_pool(wait: bool = True) -> None:
    """
    关闭全局线程池

    Args:
        wait: 是否等待所有任务完成
    """
    global _global_pool
    with _global_pool_lock:
        if _global_pool is not None:
            _global_pool.shutdown(wait=wait)
            _global_pool = None
