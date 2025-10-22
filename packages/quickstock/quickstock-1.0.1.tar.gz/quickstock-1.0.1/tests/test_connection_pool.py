"""
连接池测试

测试HTTP连接池和并发控制功能
"""

import pytest
import asyncio
import aiohttp
import time
from unittest.mock import AsyncMock, patch, MagicMock

from quickstock.core.connection_pool import (
    ConnectionPool, ConnectionPoolConfig, ConnectionPoolManager,
    RateLimiter, RequestStats
)
from quickstock.core.errors import NetworkError, RateLimitError


class TestRateLimiter:
    """速率限制器测试"""
    
    @pytest.mark.asyncio
    async def test_rate_limiter_basic(self):
        """测试基本速率限制功能"""
        limiter = RateLimiter(rate_limit=2.0, window=1)
        
        # 第一个请求应该立即通过
        start_time = time.time()
        await limiter.acquire()
        elapsed = time.time() - start_time
        assert elapsed < 0.1
        
        # 第二个请求也应该立即通过
        start_time = time.time()
        await limiter.acquire()
        elapsed = time.time() - start_time
        assert elapsed < 0.1
        
        # 第三个请求应该被限制
        start_time = time.time()
        await limiter.acquire()
        elapsed = time.time() - start_time
        assert elapsed >= 0.9  # 应该等待接近1秒
    
    @pytest.mark.asyncio
    async def test_rate_limiter_window_reset(self):
        """测试时间窗口重置"""
        limiter = RateLimiter(rate_limit=1.0, window=1)
        
        # 第一个请求
        await limiter.acquire()
        
        # 等待窗口重置
        await asyncio.sleep(1.1)
        
        # 第二个请求应该立即通过
        start_time = time.time()
        await limiter.acquire()
        elapsed = time.time() - start_time
        assert elapsed < 0.1


class TestRequestStats:
    """请求统计测试"""
    
    def test_request_stats_basic(self):
        """测试基本统计功能"""
        stats = RequestStats()
        
        # 添加成功请求
        stats.add_request(success=True, response_time=1.0)
        assert stats.total_requests == 1
        assert stats.successful_requests == 1
        assert stats.failed_requests == 0
        assert stats.success_rate == 1.0
        assert stats.average_response_time == 1.0
        
        # 添加失败请求
        stats.add_request(success=False, response_time=2.0, retries=1)
        assert stats.total_requests == 2
        assert stats.successful_requests == 1
        assert stats.failed_requests == 1
        assert stats.retry_requests == 1
        assert stats.success_rate == 0.5
        assert stats.average_response_time == 1.0  # 只计算成功请求
    
    def test_cache_hit_stats(self):
        """测试缓存命中统计"""
        stats = RequestStats()
        
        stats.add_cache_hit()
        stats.add_cache_hit()
        
        assert stats.cache_hits == 2


class TestConnectionPool:
    """连接池测试"""
    
    @pytest.fixture
    def pool_config(self):
        """连接池配置"""
        return ConnectionPoolConfig(
            connector_limit=10,
            connector_limit_per_host=5,
            total_timeout=10,
            max_retries=2,
            retry_delay=0.1
        )
    
    @pytest.fixture
    def connection_pool(self, pool_config):
        """连接池实例"""
        pool = ConnectionPool(pool_config)
        return pool
    
    @pytest.mark.asyncio
    async def test_connection_pool_creation(self, connection_pool):
        """测试连接池创建"""
        try:
            assert not connection_pool._closed
            assert len(connection_pool._sessions) == 0
            assert len(connection_pool._rate_limiters) == 0
        finally:
            await connection_pool.close()
    
    @pytest.mark.asyncio
    async def test_get_session(self, connection_pool):
        """测试获取会话"""
        try:
            url = "https://example.com/api"
            
            # 第一次获取会话
            session1 = await connection_pool.get_session(url)
            assert isinstance(session1, aiohttp.ClientSession)
            assert not session1.closed
            
            # 第二次获取应该返回相同的会话
            session2 = await connection_pool.get_session(url)
            assert session1 is session2
            
            # 不同主机应该创建新会话
            session3 = await connection_pool.get_session("https://other.com/api")
            assert session3 is not session1
        finally:
            await connection_pool.close()
    
    @pytest.mark.asyncio
    async def test_rate_limiter_creation(self, connection_pool):
        """测试速率限制器创建"""
        url = "https://example.com/api"
        
        limiter1 = await connection_pool.get_rate_limiter(url)
        assert isinstance(limiter1, RateLimiter)
        
        # 相同主机应该返回相同的限制器
        limiter2 = await connection_pool.get_rate_limiter(url)
        assert limiter1 is limiter2
    
    @pytest.mark.asyncio
    async def test_set_rate_limit(self, connection_pool):
        """测试设置速率限制"""
        url = "https://example.com/api"
        
        # 设置自定义速率限制
        connection_pool.set_rate_limit(url, 5.0)
        
        limiter = await connection_pool.get_rate_limiter(url)
        assert limiter.rate_limit == 5.0
    
    @pytest.mark.asyncio
    async def test_connection_pool_close(self, pool_config):
        """测试连接池关闭"""
        pool = ConnectionPool(pool_config)
        
        # 创建一些会话
        await pool.get_session("https://example.com")
        await pool.get_session("https://other.com")
        
        assert len(pool._sessions) == 2
        
        # 关闭连接池
        await pool.close()
        
        assert pool._closed
        assert len(pool._sessions) == 0
    
    @pytest.mark.asyncio
    async def test_stats_collection(self, connection_pool):
        """测试统计信息收集"""
        # 初始统计应该为空
        stats = connection_pool.get_stats()
        assert isinstance(stats, dict)
        
        # 获取特定主机的统计
        host_stats = connection_pool.get_stats("https://example.com")
        assert 'no_data' in host_stats
    
    @pytest.mark.asyncio
    async def test_active_connections(self, connection_pool):
        """测试活跃连接数统计"""
        connections = connection_pool.get_active_connections()
        assert isinstance(connections, dict)
        assert len(connections) == 0
        
        # 创建会话后应该有连接记录
        await connection_pool.get_session("https://example.com")
        connections = connection_pool.get_active_connections()
        assert "https://example.com" in connections


class TestConnectionPoolManager:
    """连接池管理器测试"""
    
    @pytest.fixture
    def pool_config(self):
        """连接池配置"""
        return ConnectionPoolConfig(
            connector_limit=10,
            connector_limit_per_host=5,
            total_timeout=10
        )
    
    @pytest.mark.asyncio
    async def test_singleton_pattern(self, pool_config):
        """测试单例模式"""
        # 重置单例
        ConnectionPoolManager._instance = None
        
        manager1 = await ConnectionPoolManager.get_instance(pool_config)
        manager2 = await ConnectionPoolManager.get_instance()
        
        assert manager1 is manager2
        
        # 清理
        await manager1.close()
        ConnectionPoolManager._instance = None
    
    @pytest.mark.asyncio
    async def test_manager_operations(self, pool_config):
        """测试管理器操作"""
        # 重置单例
        ConnectionPoolManager._instance = None
        
        manager = await ConnectionPoolManager.get_instance(pool_config)
        
        # 测试设置速率限制
        manager.set_rate_limit("https://example.com", 3.0)
        
        # 测试获取统计信息
        stats = manager.get_stats()
        assert isinstance(stats, dict)
        
        # 测试获取活跃连接
        connections = manager.get_active_connections()
        assert isinstance(connections, dict)
        
        # 测试健康检查
        health = await manager.health_check()
        assert isinstance(health, dict)
        
        # 清理
        await manager.close()
        ConnectionPoolManager._instance = None


class TestConnectionPoolIntegration:
    """连接池集成测试"""
    
    @pytest.fixture
    async def mock_server(self):
        """模拟HTTP服务器"""
        async def handler(request):
            # 模拟不同的响应
            if 'slow' in request.path_qs:
                await asyncio.sleep(0.1)
            
            if 'error' in request.path_qs:
                return aiohttp.web.Response(status=500, text="Server Error")
            
            return aiohttp.web.json_response({"status": "ok", "data": "test"})
        
        app = aiohttp.web.Application()
        app.router.add_get('/{path:.*}', handler)
        
        runner = aiohttp.web.AppRunner(app)
        await runner.setup()
        
        site = aiohttp.web.TCPSite(runner, 'localhost', 0)
        await site.start()
        
        port = site._server.sockets[0].getsockname()[1]
        base_url = f"http://localhost:{port}"
        
        yield base_url
        
        await runner.cleanup()
    
    @pytest.mark.asyncio
    async def test_successful_request(self, mock_server):
        """测试成功请求"""
        config = ConnectionPoolConfig(total_timeout=5)
        pool = ConnectionPool(config)
        
        try:
            async with pool.request('GET', f"{mock_server}/test") as response:
                assert response.status == 200
                data = await response.json()
                assert data['status'] == 'ok'
        finally:
            await pool.close()
    
    @pytest.mark.asyncio
    async def test_rate_limiting(self, mock_server):
        """测试速率限制"""
        config = ConnectionPoolConfig(default_rate_limit=2.0)
        pool = ConnectionPool(config)
        
        try:
            # 设置严格的速率限制
            pool.set_rate_limit(mock_server, 1.0)
            
            # 第一个请求应该立即执行
            start_time = time.time()
            async with pool.request('GET', f"{mock_server}/test1") as response:
                assert response.status == 200
            first_elapsed = time.time() - start_time
            
            # 第二个请求应该被延迟
            start_time = time.time()
            async with pool.request('GET', f"{mock_server}/test2") as response:
                assert response.status == 200
            second_elapsed = time.time() - start_time
            
            # 第二个请求应该比第一个慢（由于速率限制）
            assert second_elapsed > first_elapsed + 0.5
            
        finally:
            await pool.close()
    
    @pytest.mark.asyncio
    async def test_concurrent_requests(self, mock_server):
        """测试并发请求"""
        config = ConnectionPoolConfig(
            connector_limit_per_host=5,
            default_rate_limit=10.0  # 较高的速率限制
        )
        pool = ConnectionPool(config)
        
        try:
            # 创建多个并发请求
            tasks = []
            for i in range(5):
                task = pool.request('GET', f"{mock_server}/test{i}")
                tasks.append(task)
            
            # 并发执行
            start_time = time.time()
            responses = []
            
            for task in tasks:
                async with task as response:
                    assert response.status == 200
                    responses.append(await response.json())
            
            elapsed = time.time() - start_time
            
            # 并发执行应该比串行快
            assert elapsed < 1.0  # 5个请求在1秒内完成
            assert len(responses) == 5
            
        finally:
            await pool.close()
    
    @pytest.mark.asyncio
    async def test_error_handling_and_retry(self, mock_server):
        """测试错误处理和重试"""
        config = ConnectionPoolConfig(
            max_retries=2,
            retry_delay=0.1,
            backoff_factor=1.5
        )
        pool = ConnectionPool(config)
        
        try:
            # 测试服务器错误（应该重试）
            with pytest.raises(NetworkError):
                async with pool.request('GET', f"{mock_server}/error") as response:
                    pass
            
        finally:
            await pool.close()


@pytest.mark.asyncio
async def test_connection_pool_performance():
    """测试连接池性能"""
    config = ConnectionPoolConfig(
        connector_limit=50,
        connector_limit_per_host=20,
        default_rate_limit=50.0
    )
    
    # 重置单例
    ConnectionPoolManager._instance = None
    
    manager = await ConnectionPoolManager.get_instance(config)
    
    try:
        # 模拟大量并发请求的统计更新
        start_time = time.time()
        
        for i in range(100):
            # 模拟统计更新
            stats = manager.get_stats()
            connections = manager.get_active_connections()
        
        elapsed = time.time() - start_time
        
        # 性能检查：100次操作应该在合理时间内完成
        assert elapsed < 1.0
        
    finally:
        await manager.close()
        ConnectionPoolManager._instance = None


if __name__ == "__main__":
    pytest.main([__file__])