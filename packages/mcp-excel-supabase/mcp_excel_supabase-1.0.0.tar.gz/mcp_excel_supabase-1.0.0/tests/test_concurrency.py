"""
并发处理模块测试
"""

import time
import threading

from mcp_excel_supabase.utils.concurrency import (
    ThreadPoolManager,
    ConcurrentExecutor,
    ProgressTracker,
    get_global_pool,
    shutdown_global_pool,
)


class TestThreadPoolManager:
    """测试ThreadPoolManager类"""

    def test_context_manager(self):
        """测试上下文管理器"""
        with ThreadPoolManager(max_workers=2) as pool:
            future = pool.submit(lambda x: x * 2, 5)
            result = future.result()
            assert result == 10

    def test_manual_start_shutdown(self):
        """测试手动启动和关闭"""
        pool = ThreadPoolManager(max_workers=2)
        pool.start()

        future = pool.submit(lambda x: x + 1, 10)
        result = future.result()
        assert result == 11

        pool.shutdown()

    def test_submit_multiple_tasks(self):
        """测试提交多个任务"""
        with ThreadPoolManager(max_workers=4) as pool:
            futures = [pool.submit(lambda x: x**2, i) for i in range(10)]
            results = [f.result() for f in futures]
            expected = [i**2 for i in range(10)]
            assert results == expected

    def test_map_operation(self):
        """测试map操作"""
        with ThreadPoolManager(max_workers=4) as pool:
            items = list(range(10))
            results = pool.map(lambda x: x * 3, items)
            expected = [i * 3 for i in range(10)]
            assert results == expected

    def test_auto_start(self):
        """测试自动启动"""
        pool = ThreadPoolManager(max_workers=2)
        # 不手动调用start，submit应该自动启动
        future = pool.submit(lambda: "test")
        result = future.result()
        assert result == "test"
        pool.shutdown()


class TestConcurrentExecutor:
    """测试ConcurrentExecutor类"""

    def test_map_concurrent_basic(self):
        """测试基本并发映射"""

        def square(x: int) -> int:
            return x**2

        items = list(range(10))
        results = ConcurrentExecutor.map_concurrent(square, items, max_workers=4)
        expected = [i**2 for i in range(10)]
        assert results == expected

    def test_map_concurrent_empty_list(self):
        """测试空列表"""
        results = ConcurrentExecutor.map_concurrent(lambda x: x, [], max_workers=2)
        assert results == []

    def test_map_concurrent_with_progress(self):
        """测试带进度显示的并发映射"""

        def slow_square(x: int) -> int:
            time.sleep(0.01)
            return x**2

        items = list(range(5))
        results = ConcurrentExecutor.map_concurrent(
            slow_square, items, max_workers=2, show_progress=True
        )
        expected = [i**2 for i in range(5)]
        assert results == expected

    def test_map_concurrent_with_errors_all_success(self):
        """测试容错版本（全部成功）"""

        def safe_divide(x: int) -> float:
            return 10 / x

        items = [1, 2, 5]
        results, errors = ConcurrentExecutor.map_concurrent_with_errors(
            safe_divide, items, max_workers=2
        )

        assert len(results) == 3
        assert len(errors) == 0
        assert results == [10.0, 5.0, 2.0]

    def test_map_concurrent_with_errors_some_failures(self):
        """测试容错版本（部分失败）"""

        def safe_divide(x: int) -> float:
            return 10 / x

        items = [1, 0, 2, 0, 5]  # 包含会导致除零错误的项
        results, errors = ConcurrentExecutor.map_concurrent_with_errors(
            safe_divide, items, max_workers=2
        )

        assert len(results) == 3  # 1, 2, 5成功
        assert len(errors) == 2  # 两个0失败
        assert all(isinstance(e, ZeroDivisionError) for _, e in errors)

    def test_map_concurrent_with_errors_empty_list(self):
        """测试容错版本（空列表）"""
        results, errors = ConcurrentExecutor.map_concurrent_with_errors(
            lambda x: x, [], max_workers=2
        )
        assert results == []
        assert errors == []

    def test_batch_process(self):
        """测试批量处理"""

        def process_batch(batch: list[int]) -> int:
            return sum(batch)

        items = list(range(100))
        results = ConcurrentExecutor.batch_process(
            process_batch, items, batch_size=10, max_workers=4
        )

        # 应该有10批，每批10个数字
        assert len(results) == 10
        # 总和应该等于0+1+2+...+99
        assert sum(results) == sum(range(100))

    def test_batch_process_empty_list(self):
        """测试批量处理（空列表）"""
        results = ConcurrentExecutor.batch_process(lambda x: x, [], batch_size=10, max_workers=2)
        assert results == []

    def test_concurrent_performance(self):
        """测试并发性能提升"""

        def slow_task(x: int) -> int:
            time.sleep(0.05)  # 模拟耗时操作
            return x * 2

        items = list(range(10))

        # 串行执行
        start = time.time()
        serial_results = [slow_task(x) for x in items]
        serial_time = time.time() - start

        # 并发执行
        start = time.time()
        concurrent_results = ConcurrentExecutor.map_concurrent(slow_task, items, max_workers=4)
        concurrent_time = time.time() - start

        # 结果应该相同
        assert serial_results == concurrent_results

        # 并发应该更快（至少快1.5倍）
        assert concurrent_time < serial_time / 1.5


class TestProgressTracker:
    """测试ProgressTracker类"""

    def test_basic_tracking(self):
        """测试基本进度跟踪"""
        tracker = ProgressTracker(total=10, description="Test")

        for i in range(10):
            tracker.update(success=True)

        stats = tracker.get_stats()
        assert stats["total"] == 10
        assert stats["completed"] == 10
        assert stats["failed"] == 0
        assert stats["progress"] == 100.0

    def test_tracking_with_failures(self):
        """测试带失败的进度跟踪"""
        tracker = ProgressTracker(total=10)

        for i in range(7):
            tracker.update(success=True)

        for i in range(3):
            tracker.update(success=False)

        stats = tracker.get_stats()
        assert stats["completed"] == 7
        assert stats["failed"] == 3
        assert stats["progress"] == 100.0

    def test_thread_safety(self):
        """测试线程安全"""
        tracker = ProgressTracker(total=100)
        errors = []

        def worker():
            try:
                for _ in range(10):
                    tracker.update(success=True)
            except Exception as e:
                errors.append(str(e))

        threads = [threading.Thread(target=worker) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0
        stats = tracker.get_stats()
        assert stats["completed"] == 100

    def test_rate_calculation(self):
        """测试速率计算"""
        tracker = ProgressTracker(total=10)

        for i in range(5):
            tracker.update(success=True)
            time.sleep(0.01)

        stats = tracker.get_stats()
        assert stats["rate"] > 0  # 应该有正的处理速率


class TestGlobalPool:
    """测试全局线程池"""

    def test_get_global_pool(self):
        """测试获取全局线程池"""
        pool1 = get_global_pool(max_workers=4)
        pool2 = get_global_pool()

        # 应该返回同一个实例
        assert pool1 is pool2

        # 清理
        shutdown_global_pool()

    def test_global_pool_submit(self):
        """测试全局线程池提交任务"""
        pool = get_global_pool(max_workers=2)
        future = pool.submit(lambda x: x * 2, 21)
        result = future.result()
        assert result == 42

        # 清理
        shutdown_global_pool()

    def test_shutdown_and_restart(self):
        """测试关闭后重新启动"""
        pool1 = get_global_pool(max_workers=2)
        shutdown_global_pool()

        pool2 = get_global_pool(max_workers=4)
        # 应该是新的实例
        assert pool1 is not pool2

        # 清理
        shutdown_global_pool()


class TestIntegration:
    """集成测试"""

    def test_concurrent_file_processing_simulation(self):
        """模拟并发文件处理"""

        def process_file(file_id: int) -> dict:
            """模拟文件处理"""
            time.sleep(0.01)  # 模拟I/O操作
            return {"file_id": file_id, "status": "processed", "size": file_id * 100}

        file_ids = list(range(20))

        # 使用并发执行器处理
        results = ConcurrentExecutor.map_concurrent(process_file, file_ids, max_workers=4)

        assert len(results) == 20
        assert all(r["status"] == "processed" for r in results)
        assert sum(r["size"] for r in results) == sum(i * 100 for i in range(20))

    def test_batch_processing_with_tracker(self):
        """测试批量处理与进度跟踪"""
        tracker = ProgressTracker(total=10, description="Batch Processing")

        def process_with_tracking(x: int) -> int:
            result = x**2
            tracker.update(success=True)
            return result

        items = list(range(10))
        results = ConcurrentExecutor.map_concurrent(process_with_tracking, items, max_workers=4)

        assert results == [i**2 for i in range(10)]

        stats = tracker.get_stats()
        assert stats["completed"] == 10
        assert stats["progress"] == 100.0
