"""
缓存模块测试
"""

import time
import threading

from mcp_excel_supabase.utils.cache import (
    LRUCache,
    CacheManager,
    get_cache_manager,
    lru_cache,
    parse_cache,
    format_cache,
)


class TestLRUCache:
    """测试LRUCache类"""

    def test_basic_get_set(self):
        """测试基本的get和set操作"""
        cache = LRUCache(max_size=3)
        cache.set("key1", "value1")
        cache.set("key2", "value2")

        found1, value1 = cache.get("key1")
        assert found1 is True
        assert value1 == "value1"

        found2, value2 = cache.get("key2")
        assert found2 is True
        assert value2 == "value2"

        found3, value3 = cache.get("key3")
        assert found3 is False
        assert value3 is None

    def test_lru_eviction(self):
        """测试LRU淘汰策略"""
        cache = LRUCache(max_size=3)
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")

        # 访问key1，使其成为最近使用
        _ = cache.get("key1")

        # 添加key4，应该淘汰key2（最久未使用）
        cache.set("key4", "value4")

        found1, value1 = cache.get("key1")
        assert found1 is True
        assert value1 == "value1"

        found2, _ = cache.get("key2")
        assert found2 is False  # 已被淘汰

        found3, value3 = cache.get("key3")
        assert found3 is True
        assert value3 == "value3"

        found4, value4 = cache.get("key4")
        assert found4 is True
        assert value4 == "value4"

    def test_ttl_expiration(self):
        """测试TTL过期"""
        cache = LRUCache(max_size=10, ttl=0.1)  # 0.1秒过期
        cache.set("key1", "value1")

        # 立即获取应该成功
        found1, value1 = cache.get("key1")
        assert found1 is True
        assert value1 == "value1"

        # 等待过期
        time.sleep(0.15)

        # 过期后应该返回False
        found2, _ = cache.get("key1")
        assert found2 is False

    def test_update_existing_key(self):
        """测试更新已存在的键"""
        cache = LRUCache(max_size=3)
        cache.set("key1", "value1")
        cache.set("key1", "value2")

        found, value = cache.get("key1")
        assert found is True
        assert value == "value2"
        assert len(cache) == 1

    def test_clear(self):
        """测试清空缓存"""
        cache = LRUCache(max_size=3)
        cache.set("key1", "value1")
        cache.set("key2", "value2")

        cache.clear()

        found1, _ = cache.get("key1")
        assert found1 is False

        found2, _ = cache.get("key2")
        assert found2 is False

        assert len(cache) == 0

    def test_stats(self):
        """测试缓存统计"""
        cache = LRUCache(max_size=10, ttl=60)
        cache.set("key1", "value1")
        cache.set("key2", "value2")

        # 命中
        _ = cache.get("key1")
        _ = cache.get("key1")

        # 未命中
        _ = cache.get("key3")

        stats = cache.get_stats()

        assert stats["size"] == 2
        assert stats["max_size"] == 10
        assert stats["hits"] == 2
        assert stats["misses"] == 1
        assert stats["hit_rate"] == 2 / 3
        assert stats["ttl"] == 60

    def test_thread_safety(self):
        """测试线程安全"""
        cache = LRUCache(max_size=100)
        errors = []

        def worker(thread_id: int):
            try:
                for i in range(100):
                    key = f"key_{thread_id}_{i}"
                    cache.set(key, f"value_{thread_id}_{i}")
                    found, value = cache.get(key)
                    if not found or value != f"value_{thread_id}_{i}":
                        errors.append(f"Thread {thread_id}: value mismatch")
            except Exception as e:
                errors.append(f"Thread {thread_id}: {str(e)}")

        threads = [threading.Thread(target=worker, args=(i,)) for i in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0, f"Thread safety errors: {errors}"


class TestCacheManager:
    """测试CacheManager类"""

    def test_get_cache(self):
        """测试获取缓存"""
        manager = CacheManager()
        cache1 = manager.get_cache("test_cache", max_size=10)
        cache2 = manager.get_cache("test_cache")

        # 应该返回同一个实例
        assert cache1 is cache2

    def test_clear_cache(self):
        """测试清空指定缓存"""
        manager = CacheManager()
        cache = manager.get_cache("test_cache")
        cache.set("key1", "value1")

        manager.clear_cache("test_cache")

        found, _ = cache.get("key1")
        assert found is False

    def test_clear_all(self):
        """测试清空所有缓存"""
        manager = CacheManager()
        cache1 = manager.get_cache("cache1")
        cache2 = manager.get_cache("cache2")

        cache1.set("key1", "value1")
        cache2.set("key2", "value2")

        manager.clear_all()

        found1, _ = cache1.get("key1")
        assert found1 is False

        found2, _ = cache2.get("key2")
        assert found2 is False

    def test_get_all_stats(self):
        """测试获取所有缓存统计"""
        manager = CacheManager()
        cache1 = manager.get_cache("cache1", max_size=10)
        cache2 = manager.get_cache("cache2", max_size=20)

        cache1.set("key1", "value1")
        cache2.set("key2", "value2")

        stats = manager.get_all_stats()

        assert "cache1" in stats
        assert "cache2" in stats
        assert stats["cache1"]["size"] == 1
        assert stats["cache2"]["size"] == 1


class TestLRUCacheDecorator:
    """测试lru_cache装饰器"""

    def test_basic_caching(self):
        """测试基本缓存功能"""
        call_count = 0

        @lru_cache(max_size=10)
        def expensive_function(x: int, y: int) -> int:
            nonlocal call_count
            call_count += 1
            return x + y

        # 第一次调用
        result1 = expensive_function(1, 2)
        assert result1 == 3
        assert call_count == 1

        # 第二次调用相同参数，应该使用缓存
        result2 = expensive_function(1, 2)
        assert result2 == 3
        assert call_count == 1  # 没有增加

        # 不同参数，应该重新计算
        result3 = expensive_function(2, 3)
        assert result3 == 5
        assert call_count == 2

    def test_cache_with_kwargs(self):
        """测试带关键字参数的缓存"""
        call_count = 0

        @lru_cache(max_size=10)
        def function_with_kwargs(x: int, y: int = 0) -> int:
            nonlocal call_count
            call_count += 1
            return x + y

        result1 = function_with_kwargs(1, y=2)
        result2 = function_with_kwargs(1, y=2)

        assert result1 == result2 == 3
        assert call_count == 1

    def test_cache_clear(self):
        """测试缓存清空"""
        call_count = 0

        @lru_cache(max_size=10)
        def cached_function(x: int) -> int:
            nonlocal call_count
            call_count += 1
            return x * 2

        _ = cached_function(5)
        assert call_count == 1

        # 清空缓存
        cached_function.cache_clear()  # type: ignore

        # 再次调用应该重新计算
        _ = cached_function(5)
        assert call_count == 2

    def test_cache_stats(self):
        """测试缓存统计"""

        @lru_cache(max_size=10, cache_name="test_stats_cache")
        def cached_function(x: int) -> int:
            return x * 2

        # 清空缓存统计
        cached_function.cache_clear()  # type: ignore

        _ = cached_function(1)
        _ = cached_function(1)  # 命中
        _ = cached_function(2)

        stats = cached_function.cache_stats()  # type: ignore

        assert stats["hits"] == 1
        assert stats["misses"] == 2


class TestPredefinedCaches:
    """测试预定义的缓存实例"""

    def test_parse_cache(self):
        """测试parse_cache"""
        parse_cache.clear()
        parse_cache.set("test_file.xlsx", {"data": "parsed"})

        found, result = parse_cache.get("test_file.xlsx")
        assert found is True
        assert result == {"data": "parsed"}

    def test_format_cache(self):
        """测试format_cache"""
        format_cache.clear()
        format_cache.set("format_key", {"font": "Arial"})

        found, result = format_cache.get("format_key")
        assert found is True
        assert result == {"font": "Arial"}


class TestGlobalCacheManager:
    """测试全局缓存管理器"""

    def test_get_cache_manager(self):
        """测试获取全局缓存管理器"""
        manager1 = get_cache_manager()
        manager2 = get_cache_manager()

        # 应该返回同一个实例
        assert manager1 is manager2
