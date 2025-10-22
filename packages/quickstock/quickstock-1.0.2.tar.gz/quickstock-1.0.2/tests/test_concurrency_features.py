"""
并发功能集成测试

测试连接池、调度器和数据管理器的集成功能
"""

import pytest
import asyncio
import time
import pandas as pd
from unittest.mock import AsyncMock, MagicMock, patch

from quickstock.config import Config
from quickstock.core.data_manager import DataManager
from quickstock.core.scheduler import TaskPriority
from quickstock.models import DataRequest
from quickstock.core.connection_pool import ConnectionPoolManager


class TestConcurrencyIntegration:
    """并发功能集成测试"""
    
    @pytest.fixture
    def config(self):
        """测试配置"""
        return Config(
            max_concurrent_requests=5,
            connection_pool_size=20,
            connection_pool_per_host=10,
            cache_enabled=True,
            request_timeout=10
        )
    
    @pytest.fixture
    async def data_manager(self, config):
        """数据管理器实例"""
        manager = DataManager(config)
        yield manager
        await manager.close()
    
    @pytest.mark.asyncio
    async def test_data_manager_initialization(self, data_manager):
        """测试数据管理器初始化"""
        assert data_manager.config is not None
        assert data_manager.scheduler is not None
        assert not data_manager._scheduler_started
    
    @pytest.mark.asyncio
    async def test_scheduler_integration(self, data_manager):
        """测试调度器集成"""
        # 创建模拟数据请求
        request = DataRequest(
            data_type="stock_basic",
            ts_code="000001.SZ"
        )
        
        # 模拟数据获取
        with patch.object(data_manager, 'get_data', new_callable=AsyncMock) as mock_get_data:
            mock_get_data.return_value = pd.DataFrame({"test": [1, 2, 3]})
            
            # 使用调度器获取数据
            result = await data_manager.get_data_with_scheduler(request, TaskPriority.HIGH)
            
            assert isinstance(result, pd.DataFrame)
            assert len(result) == 3
            assert data_manager._scheduler_started
            mock_get_data.assert_called_once_with(request)
    
    @pytest.mark.asyncio
    async def test_batch_scheduled_requests(self, data_manager):
        """测试批量调度请求"""
        # 创建多个数据请求
        requests = [
            DataRequest(data_type="stock_basic", ts_code=f"00000{i}.SZ")
            for i in range(1, 4)
        ]
        
        priorities = [TaskPriority.HIGH, TaskPriority.NORMAL, TaskPriority.LOW]
        
        # 模拟数据获取
        with patch.object(data_manager, 'get_data', new_callable=AsyncMock) as mock_get_data:
            mock_get_data.return_value = pd.DataFrame({"test": [1, 2, 3]})
            
            # 批量获取数据
            results = await data_manager.get_data_batch_scheduled(requests, priorities)
            
            assert len(results) == 3
            assert all(isinstance(result, pd.DataFrame) for result in results)
            assert all(len(result) == 3 for result in results)
            assert mock_get_data.call_count == 3
    
    @pytest.mark.asyncio
    async def test_concurrent_performance(self, data_manager):
        """测试并发性能"""
        # 创建多个数据请求
        requests = [
            DataRequest(data_type="stock_daily", ts_code=f"00000{i}.SZ", 
                       start_date="20240101", end_date="20240131")
            for i in range(1, 11)  # 10个请求
        ]
        
        # 模拟慢速数据获取
        async def slow_get_data(request):
            await asyncio.sleep(0.1)  # 模拟100ms的数据获取时间
            return pd.DataFrame({"date": ["20240101"], "close": [10.0]})
        
        with patch.object(data_manager, 'get_data', side_effect=slow_get_data):
            # 测试串行执行时间
            start_time = time.time()
            serial_results = []
            for request in requests[:3]:  # 只测试3个请求以节省时间
                result = await data_manager.get_data(request)
                serial_results.append(result)
            serial_time = time.time() - start_time
            
            # 测试并发执行时间
            start_time = time.time()
            concurrent_results = await data_manager.get_data_batch(requests[:3])
            concurrent_time = time.time() - start_time
            
            # 并发执行应该更快
            assert concurrent_time < serial_time
            assert len(concurrent_results) == 3
            assert all(isinstance(result, pd.DataFrame) for result in concurrent_results)
    
    @pytest.mark.asyncio
    async def test_priority_batch_processing(self, data_manager):
        """测试优先级批量处理"""
        # 创建不同优先级的请求
        requests = [
            DataRequest(data_type="stock_basic", ts_code="000001.SZ"),
            DataRequest(data_type="stock_basic", ts_code="000002.SZ"),
            DataRequest(data_type="stock_basic", ts_code="000003.SZ"),
        ]
        
        priorities = [3, 1, 2]  # 数字越小优先级越高
        
        execution_order = []
        
        async def track_execution(request):
            execution_order.append(request.ts_code)
            await asyncio.sleep(0.01)  # 短暂延迟以观察顺序
            return pd.DataFrame({"code": [request.ts_code]})
        
        with patch.object(data_manager, 'get_data', side_effect=track_execution):
            results = await data_manager.get_data_batch_with_priority(requests, priorities)
            
            assert len(results) == 3
            # 由于并发执行，顺序可能不完全按优先级，但高优先级应该先开始
            assert execution_order[0] == "000002.SZ"  # 优先级1，最高
    
    @pytest.mark.asyncio
    async def test_error_handling_in_concurrent_requests(self, data_manager):
        """测试并发请求中的错误处理"""
        requests = [
            DataRequest(data_type="stock_basic", ts_code="000001.SZ"),
            DataRequest(data_type="stock_basic", ts_code="ERROR.SZ"),  # 会出错的请求
            DataRequest(data_type="stock_basic", ts_code="000003.SZ"),
        ]
        
        async def selective_error(request):
            if request.ts_code == "ERROR.SZ":
                raise ValueError("Simulated error")
            return pd.DataFrame({"code": [request.ts_code]})
        
        with patch.object(data_manager, 'get_data', side_effect=selective_error):
            results = await data_manager.get_data_batch(requests)
            
            assert len(results) == 3
            assert isinstance(results[0], pd.DataFrame) and not results[0].empty
            assert isinstance(results[1], pd.DataFrame) and results[1].empty  # 错误返回空DataFrame
            assert isinstance(results[2], pd.DataFrame) and not results[2].empty
    
    @pytest.mark.asyncio
    async def test_scheduler_stats_collection(self, data_manager):
        """测试调度器统计信息收集"""
        request = DataRequest(data_type="stock_basic", ts_code="000001.SZ")
        
        with patch.object(data_manager, 'get_data', new_callable=AsyncMock) as mock_get_data:
            mock_get_data.return_value = pd.DataFrame({"test": [1]})
            
            # 执行一些请求
            await data_manager.get_data_with_scheduler(request)
            
            # 获取统计信息
            stats = data_manager.get_scheduler_stats()
            
            assert isinstance(stats, dict)
            assert 'total_tasks' in stats
            assert stats['total_tasks'] >= 1
    
    @pytest.mark.asyncio
    async def test_provider_stats_integration(self, data_manager):
        """测试数据提供者统计集成"""
        # 模拟提供者统计更新
        data_manager.scheduler.update_provider_stats("test_provider", True, 1.0)
        data_manager.scheduler.update_provider_stats("test_provider", False, 2.0)
        
        stats = data_manager.get_provider_stats()
        
        assert isinstance(stats, dict)
        assert "test_provider" in stats
        
        provider_stats = stats["test_provider"]
        assert provider_stats['total_requests'] == 2
        assert provider_stats['successful_requests'] == 1
        assert provider_stats['failed_requests'] == 1


class TestConnectionPoolIntegration:
    """连接池集成测试"""
    
    @pytest.fixture
    def config(self):
        """测试配置"""
        return Config(
            connection_pool_size=10,
            connection_pool_per_host=5,
            connection_keepalive_timeout=30,
            request_timeout=10
        )
    
    @pytest.mark.asyncio
    async def test_connection_pool_manager_singleton(self, config):
        """测试连接池管理器单例模式"""
        # 重置单例
        ConnectionPoolManager._instance = None
        
        # 创建多个数据管理器
        manager1 = DataManager(config)
        manager2 = DataManager(config)
        
        try:
            # 获取连接池
            pool1 = await manager1.source_manager.providers['eastmoney'].get_connection_pool()
            pool2 = await manager2.source_manager.providers['eastmoney'].get_connection_pool()
            
            # 应该是同一个实例
            assert pool1 is pool2
            
        finally:
            await manager1.close()
            await manager2.close()
            ConnectionPoolManager._instance = None
    
    @pytest.mark.asyncio
    async def test_provider_connection_pool_usage(self, config):
        """测试数据提供者使用连接池"""
        from quickstock.providers.eastmoney import EastmoneyProvider
        
        provider = EastmoneyProvider(config)
        
        try:
            # 获取连接池
            pool = await provider.get_connection_pool()
            assert pool is not None
            
            # 测试连接池统计
            stats = pool.get_stats()
            assert isinstance(stats, dict)
            
            connections = pool.get_active_connections()
            assert isinstance(connections, dict)
            
        finally:
            await provider.close()


class TestPerformanceOptimizations:
    """性能优化测试"""
    
    @pytest.fixture
    def high_performance_config(self):
        """高性能配置"""
        return Config(
            max_concurrent_requests=20,
            connection_pool_size=100,
            connection_pool_per_host=30,
            cache_enabled=True,
            memory_cache_size=5000,
            request_timeout=5
        )
    
    @pytest.mark.asyncio
    async def test_high_concurrency_performance(self, high_performance_config):
        """测试高并发性能"""
        data_manager = DataManager(high_performance_config)
        
        try:
            # 创建大量请求
            requests = [
                DataRequest(data_type="stock_basic", ts_code=f"{i:06d}.SZ")
                for i in range(1, 51)  # 50个请求
            ]
            
            # 模拟快速数据获取
            async def fast_get_data(request):
                await asyncio.sleep(0.01)  # 10ms延迟
                return pd.DataFrame({"code": [request.ts_code], "name": ["Test"]})
            
            with patch.object(data_manager, 'get_data', side_effect=fast_get_data):
                start_time = time.time()
                results = await data_manager.get_data_batch(requests)
                elapsed = time.time() - start_time
                
                # 50个请求应该在合理时间内完成
                assert elapsed < 5.0  # 5秒内完成
                assert len(results) == 50
                assert all(isinstance(result, pd.DataFrame) for result in results)
                
        finally:
            await data_manager.close()
    
    @pytest.mark.asyncio
    async def test_memory_usage_optimization(self, high_performance_config):
        """测试内存使用优化"""
        data_manager = DataManager(high_performance_config)
        
        try:
            # 创建大数据量的模拟响应
            large_df = pd.DataFrame({
                'date': pd.date_range('2024-01-01', periods=1000),
                'value': range(1000),
                'data': ['x' * 100] * 1000  # 每行100字符
            })
            
            async def large_data_response(request):
                return large_df.copy()
            
            requests = [
                DataRequest(data_type="stock_daily", ts_code=f"{i:06d}.SZ")
                for i in range(1, 11)  # 10个大数据请求
            ]
            
            with patch.object(data_manager, 'get_data', side_effect=large_data_response):
                start_time = time.time()
                results = await data_manager.get_data_batch(requests)
                elapsed = time.time() - start_time
                
                # 检查结果
                assert len(results) == 10
                assert all(len(result) == 1000 for result in results)
                
                # 性能检查：大数据量处理应该在合理时间内完成
                assert elapsed < 10.0
                
        finally:
            await data_manager.close()
    
    @pytest.mark.asyncio
    async def test_cache_performance_with_concurrency(self, high_performance_config):
        """测试缓存在并发环境下的性能"""
        data_manager = DataManager(high_performance_config)
        
        try:
            # 相同的请求（应该命中缓存）
            request = DataRequest(data_type="stock_basic", ts_code="000001.SZ")
            
            call_count = 0
            
            async def counted_get_data(req):
                nonlocal call_count
                call_count += 1
                await asyncio.sleep(0.1)  # 模拟数据获取延迟
                return pd.DataFrame({"code": [req.ts_code]})
            
            with patch.object(data_manager, '_get_data_without_cache', side_effect=counted_get_data):
                # 第一次请求（应该调用数据源）
                result1 = await data_manager.get_data(request)
                assert not result1.empty
                assert call_count == 1
                
                # 并发发起多个相同请求（应该命中缓存）
                tasks = [data_manager.get_data(request) for _ in range(5)]
                results = await asyncio.gather(*tasks)
                
                # 应该只调用了一次数据源（其他命中缓存）
                assert call_count == 1
                assert len(results) == 5
                assert all(not result.empty for result in results)
                
        finally:
            await data_manager.close()


@pytest.mark.asyncio
async def test_full_integration_scenario():
    """完整集成场景测试"""
    config = Config(
        max_concurrent_requests=10,
        connection_pool_size=50,
        connection_pool_per_host=20,
        cache_enabled=True,
        memory_cache_size=1000
    )
    
    data_manager = DataManager(config)
    
    try:
        # 模拟真实的数据获取场景
        stock_requests = [
            DataRequest(data_type="stock_daily", ts_code=f"{i:06d}.SZ", 
                       start_date="20240101", end_date="20240131")
            for i in range(1, 21)  # 20只股票
        ]
        
        index_requests = [
            DataRequest(data_type="index_daily", ts_code=f"{i:06d}.SH",
                       start_date="20240101", end_date="20240131")
            for i in range(1, 6)  # 5个指数
        ]
        
        all_requests = stock_requests + index_requests
        
        # 模拟不同响应时间的数据源
        async def variable_response_time(request):
            if request.data_type == "stock_daily":
                await asyncio.sleep(0.05)  # 股票数据较快
            else:
                await asyncio.sleep(0.1)   # 指数数据较慢
            
            return pd.DataFrame({
                "date": ["20240101", "20240102"],
                "close": [10.0, 10.5],
                "volume": [1000, 1100]
            })
        
        with patch.object(data_manager, 'get_data', side_effect=variable_response_time):
            start_time = time.time()
            
            # 使用不同的并发策略
            stock_results = await data_manager.get_data_batch(stock_requests)
            index_results = await data_manager.get_data_batch_with_priority(
                index_requests, 
                [TaskPriority.HIGH] * len(index_requests)
            )
            
            elapsed = time.time() - start_time
            
            # 验证结果
            assert len(stock_results) == 20
            assert len(index_results) == 5
            assert all(len(result) == 2 for result in stock_results + index_results)
            
            # 性能验证：并发处理应该比串行快
            expected_serial_time = (20 * 0.05) + (5 * 0.1)  # 1.5秒
            assert elapsed < expected_serial_time * 0.8  # 应该至少快20%
            
            # 获取性能统计
            scheduler_stats = data_manager.get_scheduler_stats()
            assert scheduler_stats['total_tasks'] >= 25
            
    finally:
        await data_manager.close()
        # 清理连接池单例
        ConnectionPoolManager._instance = None


if __name__ == "__main__":
    pytest.main([__file__])