"""
请求调度器测试

测试并发请求调度和负载均衡功能
"""

import pytest
import asyncio
import time
from unittest.mock import AsyncMock, MagicMock

from quickstock.core.scheduler import (
    RequestScheduler, ScheduledTask, TaskResult, TaskPriority
)


class TestScheduledTask:
    """调度任务测试"""
    
    def test_task_creation(self):
        """测试任务创建"""
        def dummy_func():
            return "test"
        
        task = ScheduledTask(
            id="test_task",
            func=dummy_func,
            args=(1, 2),
            kwargs={"key": "value"},
            priority=TaskPriority.HIGH
        )
        
        assert task.id == "test_task"
        assert task.func == dummy_func
        assert task.args == (1, 2)
        assert task.kwargs == {"key": "value"}
        assert task.priority == TaskPriority.HIGH
        assert task.retry_count == 0
        assert task.max_retries == 3
    
    def test_task_comparison(self):
        """测试任务优先级比较"""
        task1 = ScheduledTask(id="1", func=lambda: None, priority=TaskPriority.HIGH)
        task2 = ScheduledTask(id="2", func=lambda: None, priority=TaskPriority.LOW)
        task3 = ScheduledTask(id="3", func=lambda: None, priority=TaskPriority.HIGH)
        
        # 高优先级应该小于低优先级
        assert task1 < task2
        
        # 相同优先级按创建时间排序
        time.sleep(0.001)  # 确保时间差异
        task4 = ScheduledTask(id="4", func=lambda: None, priority=TaskPriority.HIGH)
        assert task1 < task4


class TestTaskResult:
    """任务结果测试"""
    
    def test_successful_result(self):
        """测试成功结果"""
        result = TaskResult(
            task_id="test",
            success=True,
            result="success_data",
            execution_time=1.5
        )
        
        assert result.task_id == "test"
        assert result.success is True
        assert result.result == "success_data"
        assert result.error is None
        assert result.execution_time == 1.5
    
    def test_failed_result(self):
        """测试失败结果"""
        error = ValueError("test error")
        result = TaskResult(
            task_id="test",
            success=False,
            error=error,
            execution_time=0.5,
            retry_count=2
        )
        
        assert result.task_id == "test"
        assert result.success is False
        assert result.result is None
        assert result.error == error
        assert result.retry_count == 2


class TestRequestScheduler:
    """请求调度器测试"""
    
    @pytest.fixture
    def scheduler(self):
        """调度器实例"""
        return RequestScheduler(max_concurrent=3, max_queue_size=10)
    
    @pytest.mark.asyncio
    async def test_scheduler_start_stop(self):
        """测试调度器启动和停止"""
        scheduler = RequestScheduler(max_concurrent=2)
        
        assert not scheduler._running
        
        await scheduler.start()
        assert scheduler._running
        assert scheduler._scheduler_task is not None
        
        await scheduler.stop()
        assert not scheduler._running
    
    @pytest.mark.asyncio
    async def test_simple_task_execution(self, scheduler):
        """测试简单任务执行"""
        await scheduler.start()
        try:
            def simple_task(x, y):
                return x + y
            
            # 提交任务
            success = await scheduler.submit_task(
                "add_task",
                simple_task,
                1, 2
            )
            assert success
            
            # 等待结果
            result = await scheduler.wait_for_task("add_task", timeout=5.0)
            assert result.success
            assert result.result == 3
            assert result.retry_count == 0
        finally:
            await scheduler.stop()
    
    @pytest.mark.asyncio
    async def test_async_task_execution(self, scheduler):
        """测试异步任务执行"""
        async def async_task(delay, value):
            await asyncio.sleep(delay)
            return value * 2
        
        # 提交异步任务
        success = await scheduler.submit_task(
            "async_task",
            async_task,
            0.1, 5
        )
        assert success
        
        # 等待结果
        result = await scheduler.wait_for_task("async_task", timeout=5.0)
        assert result.success
        assert result.result == 10
    
    @pytest.mark.asyncio
    async def test_task_priority(self, scheduler):
        """测试任务优先级"""
        results = []
        
        def priority_task(task_id):
            results.append(task_id)
            return task_id
        
        # 提交不同优先级的任务
        await scheduler.submit_task("low", priority_task, "low", priority=TaskPriority.LOW)
        await scheduler.submit_task("high", priority_task, "high", priority=TaskPriority.HIGH)
        await scheduler.submit_task("urgent", priority_task, "urgent", priority=TaskPriority.URGENT)
        await scheduler.submit_task("normal", priority_task, "normal", priority=TaskPriority.NORMAL)
        
        # 等待所有任务完成
        await scheduler.wait_for_task("low", timeout=5.0)
        await scheduler.wait_for_task("high", timeout=5.0)
        await scheduler.wait_for_task("urgent", timeout=5.0)
        await scheduler.wait_for_task("normal", timeout=5.0)
        
        # 检查执行顺序（紧急任务应该先执行）
        assert results[0] == "urgent"
        assert results[1] == "high"
        # normal和low的顺序可能因并发而变化
    
    @pytest.mark.asyncio
    async def test_task_retry(self, scheduler):
        """测试任务重试"""
        call_count = 0
        
        def failing_task():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError(f"Attempt {call_count} failed")
            return "success"
        
        # 提交会失败的任务
        success = await scheduler.submit_task(
            "retry_task",
            failing_task,
            max_retries=3
        )
        assert success
        
        # 等待结果
        result = await scheduler.wait_for_task("retry_task", timeout=10.0)
        assert result.success
        assert result.result == "success"
        assert result.retry_count == 2  # 失败2次后成功
        assert call_count == 3
    
    @pytest.mark.asyncio
    async def test_task_max_retries_exceeded(self, scheduler):
        """测试超过最大重试次数"""
        def always_failing_task():
            raise ValueError("Always fails")
        
        # 提交总是失败的任务
        success = await scheduler.submit_task(
            "fail_task",
            always_failing_task,
            max_retries=2
        )
        assert success
        
        # 等待结果
        result = await scheduler.wait_for_task("fail_task", timeout=10.0)
        assert not result.success
        assert isinstance(result.error, ValueError)
        assert result.retry_count == 2
    
    @pytest.mark.asyncio
    async def test_delayed_task(self, scheduler):
        """测试延迟任务"""
        def delayed_task():
            return time.time()
        
        start_time = time.time()
        
        # 提交延迟任务
        success = await scheduler.submit_task(
            "delayed_task",
            delayed_task,
            delay=0.5  # 延迟0.5秒
        )
        assert success
        
        # 等待结果
        result = await scheduler.wait_for_task("delayed_task", timeout=5.0)
        assert result.success
        
        # 检查执行时间
        execution_time = result.result
        elapsed = execution_time - start_time
        assert elapsed >= 0.4  # 应该至少延迟了0.4秒
    
    @pytest.mark.asyncio
    async def test_concurrent_execution(self, scheduler):
        """测试并发执行"""
        async def concurrent_task(task_id, duration):
            await asyncio.sleep(duration)
            return task_id
        
        start_time = time.time()
        
        # 提交多个并发任务
        task_ids = []
        for i in range(3):  # 调度器最大并发数为3
            task_id = f"concurrent_{i}"
            task_ids.append(task_id)
            await scheduler.submit_task(
                task_id,
                concurrent_task,
                task_id, 0.5
            )
        
        # 等待所有任务完成
        results = []
        for task_id in task_ids:
            result = await scheduler.wait_for_task(task_id, timeout=5.0)
            results.append(result)
        
        elapsed = time.time() - start_time
        
        # 并发执行应该比串行快
        assert elapsed < 1.0  # 3个0.5秒的任务并发执行应该在1秒内完成
        assert all(result.success for result in results)
    
    @pytest.mark.asyncio
    async def test_queue_full_rejection(self):
        """测试队列满时的拒绝"""
        scheduler = RequestScheduler(max_concurrent=1, max_queue_size=2)
        await scheduler.start()
        
        try:
            def dummy_task():
                time.sleep(1)  # 阻塞任务
                return "done"
            
            # 填满队列
            success1 = await scheduler.submit_task("task1", dummy_task)
            success2 = await scheduler.submit_task("task2", dummy_task)
            success3 = await scheduler.submit_task("task3", dummy_task)
            
            assert success1
            assert success2
            
            # 第四个任务应该被拒绝
            success4 = await scheduler.submit_task("task4", dummy_task)
            assert not success4
            
        finally:
            await scheduler.stop()
    
    @pytest.mark.asyncio
    async def test_get_task_result_timeout(self, scheduler):
        """测试获取任务结果超时"""
        async def slow_task():
            await asyncio.sleep(2.0)
            return "slow_result"
        
        await scheduler.submit_task("slow_task", slow_task)
        
        # 短超时应该返回None
        result = await scheduler.get_task_result("slow_task", timeout=0.1)
        assert result is None
        
        # 长超时应该获得结果
        result = await scheduler.get_task_result("slow_task", timeout=3.0)
        assert result is not None
        assert result.success
        assert result.result == "slow_result"
    
    @pytest.mark.asyncio
    async def test_scheduler_stats(self, scheduler):
        """测试调度器统计信息"""
        def simple_task():
            return "done"
        
        # 初始统计
        stats = scheduler.get_stats()
        assert stats['total_tasks'] == 0
        assert stats['completed_tasks'] == 0
        assert stats['failed_tasks'] == 0
        
        # 提交并执行任务
        await scheduler.submit_task("stats_task", simple_task)
        await scheduler.wait_for_task("stats_task", timeout=5.0)
        
        # 检查更新后的统计
        stats = scheduler.get_stats()
        assert stats['total_tasks'] == 1
        assert stats['completed_tasks'] == 1
        assert stats['failed_tasks'] == 0
        assert stats['average_execution_time'] > 0
    
    @pytest.mark.asyncio
    async def test_provider_stats(self, scheduler):
        """测试数据提供者统计"""
        # 更新提供者统计
        scheduler.update_provider_stats("provider1", success=True, response_time=1.0)
        scheduler.update_provider_stats("provider1", success=False, response_time=2.0)
        scheduler.update_provider_stats("provider2", success=True, response_time=0.5)
        
        # 获取统计信息
        stats = scheduler.get_provider_stats()
        
        assert "provider1" in stats
        assert "provider2" in stats
        
        provider1_stats = stats["provider1"]
        assert provider1_stats['total_requests'] == 2
        assert provider1_stats['successful_requests'] == 1
        assert provider1_stats['failed_requests'] == 1
        
        provider2_stats = stats["provider2"]
        assert provider2_stats['total_requests'] == 1
        assert provider2_stats['successful_requests'] == 1
        assert provider2_stats['failed_requests'] == 0
    
    @pytest.mark.asyncio
    async def test_best_provider_selection(self, scheduler):
        """测试最佳提供者选择"""
        # 更新不同提供者的统计信息
        scheduler.update_provider_stats("fast_provider", success=True, response_time=0.5)
        scheduler.update_provider_stats("fast_provider", success=True, response_time=0.6)
        
        scheduler.update_provider_stats("slow_provider", success=True, response_time=2.0)
        scheduler.update_provider_stats("slow_provider", success=True, response_time=1.8)
        
        scheduler.update_provider_stats("unreliable_provider", success=True, response_time=1.0)
        scheduler.update_provider_stats("unreliable_provider", success=False, response_time=1.0)
        
        # 选择最佳提供者
        providers = ["fast_provider", "slow_provider", "unreliable_provider"]
        best = scheduler.get_best_provider(providers)
        
        # 快速且可靠的提供者应该被选中
        assert best == "fast_provider"
        
        # 测试空列表
        assert scheduler.get_best_provider([]) is None
        
        # 测试单个提供者
        assert scheduler.get_best_provider(["only_one"]) == "only_one"
    
    @pytest.mark.asyncio
    async def test_context_manager(self):
        """测试异步上下文管理器"""
        async with RequestScheduler(max_concurrent=2) as scheduler:
            assert scheduler._running
            
            # 在上下文中使用调度器
            await scheduler.submit_task("ctx_task", lambda: "test")
            result = await scheduler.wait_for_task("ctx_task", timeout=5.0)
            assert result.success
        
        # 退出上下文后应该停止
        assert not scheduler._running


@pytest.mark.asyncio
async def test_scheduler_performance():
    """测试调度器性能"""
    scheduler = RequestScheduler(max_concurrent=10, max_queue_size=1000)
    await scheduler.start()
    
    try:
        def fast_task(i):
            return i * 2
        
        # 提交大量任务
        start_time = time.time()
        task_count = 100
        
        for i in range(task_count):
            await scheduler.submit_task(f"perf_task_{i}", fast_task, i)
        
        submit_time = time.time() - start_time
        
        # 等待所有任务完成
        start_time = time.time()
        for i in range(task_count):
            result = await scheduler.wait_for_task(f"perf_task_{i}", timeout=10.0)
            assert result.success
            assert result.result == i * 2
        
        execution_time = time.time() - start_time
        
        # 性能检查
        assert submit_time < 1.0  # 提交100个任务应该在1秒内完成
        assert execution_time < 5.0  # 执行100个任务应该在5秒内完成
        
        # 检查统计信息
        stats = scheduler.get_stats()
        assert stats['total_tasks'] == task_count
        assert stats['completed_tasks'] == task_count
        assert stats['failed_tasks'] == 0
        
    finally:
        await scheduler.stop()


if __name__ == "__main__":
    pytest.main([__file__])