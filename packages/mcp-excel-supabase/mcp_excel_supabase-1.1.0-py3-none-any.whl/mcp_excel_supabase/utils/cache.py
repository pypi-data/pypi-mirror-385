"""
缓存机制模块

提供多种缓存策略和工具：
- LRU缓存装饰器
- 解析结果缓存
- 格式信息缓存
- 缓存统计和管理
"""

import threading
import time
from collections import OrderedDict
from functools import wraps
from typing import Any, Callable, Dict, Optional, Tuple, TypeVar, cast

from .logger import Logger

logger = Logger("cache")

T = TypeVar("T")


class LRUCache:
    """
    线程安全的LRU（Least Recently Used）缓存实现

    特性：
    - 自动淘汰最久未使用的条目
    - 线程安全
    - 支持过期时间
    - 提供缓存统计
    """

    def __init__(self, max_size: int = 128, ttl: Optional[float] = None) -> None:
        """
        初始化LRU缓存

        Args:
            max_size: 最大缓存条目数
            ttl: 缓存条目的生存时间（秒），None表示永不过期
        """
        self.max_size = max_size
        self.ttl = ttl
        self._cache: OrderedDict[Any, Tuple[Any, float]] = OrderedDict()
        self._lock = threading.Lock()
        self._hits = 0
        self._misses = 0

    def get(self, key: Any, default: Any = None) -> Tuple[bool, Any]:
        """
        获取缓存值

        Args:
            key: 缓存键
            default: 默认值

        Returns:
            (found, value) 元组，found表示是否找到，value是缓存值或默认值
        """
        with self._lock:
            if key not in self._cache:
                self._misses += 1
                return (False, default)

            value, timestamp = self._cache[key]

            # 检查是否过期
            if self.ttl is not None and time.time() - timestamp > self.ttl:
                del self._cache[key]
                self._misses += 1
                return (False, default)

            # 移到末尾（最近使用）
            self._cache.move_to_end(key)
            self._hits += 1
            return (True, value)

    def set(self, key: Any, value: Any) -> None:
        """
        设置缓存值

        Args:
            key: 缓存键
            value: 缓存值
        """
        with self._lock:
            # 如果键已存在，先删除
            if key in self._cache:
                del self._cache[key]

            # 添加新条目
            self._cache[key] = (value, time.time())
            self._cache.move_to_end(key)

            # 如果超过最大大小，删除最旧的条目
            if len(self._cache) > self.max_size:
                oldest_key = next(iter(self._cache))
                del self._cache[oldest_key]
                logger.debug(f"缓存已满，淘汰最旧条目: {oldest_key}")

    def clear(self) -> None:
        """清空缓存"""
        with self._lock:
            self._cache.clear()
            self._hits = 0
            self._misses = 0
            logger.info("缓存已清空")

    def get_stats(self) -> Dict[str, Any]:
        """
        获取缓存统计信息

        Returns:
            包含统计信息的字典
        """
        with self._lock:
            total_requests = self._hits + self._misses
            hit_rate = self._hits / total_requests if total_requests > 0 else 0.0

            return {
                "size": len(self._cache),
                "max_size": self.max_size,
                "hits": self._hits,
                "misses": self._misses,
                "hit_rate": hit_rate,
                "ttl": self.ttl,
            }

    def __len__(self) -> int:
        """返回缓存中的条目数"""
        with self._lock:
            return len(self._cache)


class CacheManager:
    """
    缓存管理器

    管理多个命名缓存实例
    """

    def __init__(self) -> None:
        """初始化缓存管理器"""
        self._caches: Dict[str, LRUCache] = {}
        self._lock = threading.Lock()

    def get_cache(self, name: str, max_size: int = 128, ttl: Optional[float] = None) -> LRUCache:
        """
        获取或创建命名缓存

        Args:
            name: 缓存名称
            max_size: 最大缓存大小
            ttl: 生存时间（秒）

        Returns:
            LRUCache实例
        """
        with self._lock:
            if name not in self._caches:
                self._caches[name] = LRUCache(max_size=max_size, ttl=ttl)
                logger.info(f"创建新缓存: {name} (max_size={max_size}, ttl={ttl})")
            return self._caches[name]

    def clear_cache(self, name: str) -> None:
        """
        清空指定缓存

        Args:
            name: 缓存名称
        """
        with self._lock:
            if name in self._caches:
                self._caches[name].clear()

    def clear_all(self) -> None:
        """清空所有缓存"""
        with self._lock:
            for cache in self._caches.values():
                cache.clear()
            logger.info("所有缓存已清空")

    def get_all_stats(self) -> Dict[str, Dict[str, Any]]:
        """
        获取所有缓存的统计信息

        Returns:
            包含所有缓存统计信息的字典
        """
        with self._lock:
            return {name: cache.get_stats() for name, cache in self._caches.items()}


# 全局缓存管理器实例
_cache_manager = CacheManager()


def get_cache_manager() -> CacheManager:
    """
    获取全局缓存管理器实例

    Returns:
        CacheManager实例
    """
    return _cache_manager


def lru_cache(
    max_size: int = 128, ttl: Optional[float] = None, cache_name: Optional[str] = None
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    LRU缓存装饰器

    Args:
        max_size: 最大缓存大小
        ttl: 生存时间（秒）
        cache_name: 缓存名称，如果为None则使用函数名

    Returns:
        装饰器函数

    Example:
        @lru_cache(max_size=100, ttl=300)
        def expensive_function(arg1, arg2):
            # 耗时操作
            return result
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        name = cache_name or f"{func.__module__}.{func.__name__}"
        cache = _cache_manager.get_cache(name, max_size=max_size, ttl=ttl)

        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            # 生成缓存键
            cache_key = (args, tuple(sorted(kwargs.items())))

            # 尝试从缓存获取
            found, cached_value = cache.get(cache_key)
            if found:
                logger.debug(f"缓存命中: {name}")
                return cast(T, cached_value)

            # 执行函数并缓存结果
            logger.debug(f"缓存未命中: {name}")
            result = func(*args, **kwargs)
            cache.set(cache_key, result)
            return result

        # 添加缓存管理方法
        wrapper.cache_clear = cache.clear  # type: ignore
        wrapper.cache_stats = cache.get_stats  # type: ignore

        return wrapper

    return decorator


# 预定义的缓存实例
parse_cache = _cache_manager.get_cache("excel_parse", max_size=50, ttl=3600)
format_cache = _cache_manager.get_cache("format_info", max_size=200, ttl=1800)
