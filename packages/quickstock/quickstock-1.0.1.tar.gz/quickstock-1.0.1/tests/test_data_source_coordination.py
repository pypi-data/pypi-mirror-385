"""
数据源协调机制集成测试

测试多数据源协调、fallback机制、负载均衡等功能
"""

import pytest
import asyncio
import pandas as pd
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timedelta

from quickstock.config import Config
from quickstock.models import DataRequest
from quickstock.providers.manager import (
    DataSourceManager, 
    FallbackStrategy, 
    LoadBalanceStrategy,
    ProviderHealth, 
    ProviderStats
)
from quickstock.providers.base import DataProvider
from quickstock.core.errors import DataSourceError


class SlowProvider(DataProvider):
    """慢速提供者（用于测试性能优先策略）"""
    
    def __init__(self, config, name="slow", delay=2.0):
        super().__init__(config)
        self.name = name
        self.delay = delay
    
    async def get_stock_basic(self, **kwargs) -> pd.DataFrame:
        await asyncio.sleep(self.delay)
        return pd.DataFrame({
            'ts_code': ['000001.SZ'],
            'name': ['慢速数据'],
            'market': ['主板']
        })
    
    async def get_stock_daily(self, ts_code: str, start_date: str, end_date: str) -> pd.DataFrame:
        await asyncio.sleep(self.delay)
        return pd.DataFrame({
            'ts_code': [ts_code],
            'trade_date': ['20240101'],
            'close': [10.0]
        })
    
    async def get_trade_cal(self, start_date: str, end_date: str) -> pd.DataFrame:
        await asyncio.sleep(self.delay)
        return pd.DataFrame({
            'cal_date': ['20240101'],
            'is_open': [1]
        })
    
    def get_provider_name(self) -> str:
        return self.name


class FastProvider(DataProvider):
    """快速提供者（用于测试性能优先策略）"""
    
    def __init__(self, config, name="fast", delay=0.1):
        super().__init__(config)
        self.name = name
        self.delay = delay
    
    async def get_stock_basic(self, **kwargs) -> pd.DataFrame:
        await asyncio.sleep(self.delay)
        return pd.DataFrame({
            'ts_code': ['000001.SZ'],
            'name': ['快速数据'],
            'market': ['主板']
        })
    
    async def get_stock_daily(self, ts_code: str, start_date: str, end_date: str) -> pd.DataFrame:
        await asyncio.sleep(self.delay)
        return pd.DataFrame({
            'ts_code': [ts_code],
            'trade_date': ['20240101'],
            'close': [10.0]
        })
    
    async def get_trade_cal(self, start_date: str, end_date: str) -> pd.DataFrame:
        await asyncio.sleep(self.delay)
        return pd.DataFrame({
            'cal_date': ['20240101'],
            'is_open': [1]
        })
    
    def get_provider_name(self) -> str:
        return self.name


class UnreliableProvider(DataProvider):
    """不可靠提供者（用于测试熔断器）"""
    
    def __init__(self, config, name="unreliable", failure_rate=0.7):
        super().__init__(config)
        self.name = name
        self.failure_rate = failure_rate
        self.call_count = 0
    
    async def get_stock_basic(self, **kwargs) -> pd.DataFrame:
        self.call_count += 1
        if (self.call_count % 10) / 10 < self.failure_rate:
            raise Exception(f"Simulated failure from {self.name}")
        
        return pd.DataFrame({
            'ts_code': ['000001.SZ'],
            'name': ['不可靠数据'],
            'market': ['主板']
        })
    
    async def get_stock_daily(self, ts_code: str, start_date: str, end_date: str) -> pd.DataFrame:
        self.call_count += 1
        if (self.call_count % 10) / 10 < self.failure_rate:
            raise Exception(f"Simulated failure from {self.name}")
        
        return pd.DataFrame({
            'ts_code': [ts_code],
            'trade_date': ['20240101'],
            'close': [10.0]
        })
    
    async def get_trade_cal(self, start_date: str, end_date: str) -> pd.DataFrame:
        self.call_count += 1
        if (self.call_count % 10) / 10 < self.failure_rate:
            raise Exception(f"Simulated failure from {self.name}")
        
        return pd.DataFrame({
            'cal_date': ['20240101'],
            'is_open': [1]
        })
    
    def get_provider_name(self) -> str:
        return self.name


@pytest.fixture
def config():
    """测试配置"""
    return Config(
        enable_baostock=False,
        enable_eastmoney=False,
        enable_tonghuashun=False,
        data_source_priority={
            'stock_basic': ['slow', 'fast', 'unreliable'],
            'stock_daily': ['unreliable', 'slow', 'fast']
        }
    )


@pytest.fixture
def manager_with_providers(config):
    """带有多个提供者的管理器"""
    manager = DataSourceManager(config)
    
    # 注册不同类型的提供者
    slow_provider = SlowProvider(config, "slow", delay=1.0)
    fast_provider = FastProvider(config, "fast", delay=0.1)
    unreliable_provider = UnreliableProvider(config, "unreliable", failure_rate=0.8)
    
    manager.register_provider("slow", slow_provider)
    manager.register_provider("fast", fast_provider)
    manager.register_provider("unreliable", unreliable_provider)
    
    return manager


class TestFallbackStrategies:
    """Fallback策略测试"""
    
    @pytest.mark.asyncio
    async def test_priority_order_fallback(self, manager_with_providers):
        """测试优先级顺序fallback"""
        manager = manager_with_providers
        manager.set_fallback_strategy(FallbackStrategy.PRIORITY_ORDER)
        
        # 由于slow是第一优先级，应该使用slow提供者
        request = DataRequest(data_type="stock_basic")
        data = await manager.fetch_data(request)
        
        assert isinstance(data, pd.DataFrame)
        assert data.iloc[0]['name'] == '慢速数据'
    
    @pytest.mark.asyncio
    async def test_performance_based_fallback(self, manager_with_providers):
        """测试基于性能的fallback"""
        manager = manager_with_providers
        
        # 先执行几次请求建立性能统计
        for _ in range(3):
            try:
                request = DataRequest(data_type="stock_basic")
                await manager.fetch_data(request)
            except:
                pass
        
        # 设置基于性能的策略
        manager.set_fallback_strategy(FallbackStrategy.PERFORMANCE_BASED)
        
        request = DataRequest(data_type="stock_basic")
        data = await manager.fetch_data(request)
        
        assert isinstance(data, pd.DataFrame)
        # 应该选择性能最好的提供者
    
    @pytest.mark.asyncio
    async def test_fastest_first_fallback(self, manager_with_providers):
        """测试最快优先fallback"""
        manager = manager_with_providers
        
        # 先执行几次请求建立响应时间统计
        for _ in range(2):
            try:
                request = DataRequest(data_type="stock_basic")
                await manager.fetch_data(request)
            except:
                pass
        
        # 设置最快优先策略
        manager.set_fallback_strategy(FallbackStrategy.FASTEST_FIRST)
        
        request = DataRequest(data_type="stock_basic")
        data = await manager.fetch_data(request)
        
        assert isinstance(data, pd.DataFrame)


class TestLoadBalanceStrategies:
    """负载均衡策略测试"""
    
    @pytest.mark.asyncio
    async def test_round_robin_load_balance(self, manager_with_providers):
        """测试轮询负载均衡"""
        manager = manager_with_providers
        manager.set_load_balance_strategy(LoadBalanceStrategy.ROUND_ROBIN)
        
        # 执行多次请求，应该轮询使用不同的提供者
        results = []
        for _ in range(6):
            try:
                request = DataRequest(data_type="stock_basic")
                data = await manager.fetch_data(request)
                results.append(data.iloc[0]['name'])
            except:
                pass
        
        # 应该有不同的提供者被使用
        assert len(set(results)) > 1
    
    @pytest.mark.asyncio
    async def test_least_connections_load_balance(self, manager_with_providers):
        """测试最少连接负载均衡"""
        manager = manager_with_providers
        manager.set_load_balance_strategy(LoadBalanceStrategy.LEAST_CONNECTIONS)
        
        # 模拟一些活跃连接
        manager.provider_stats["slow"].active_connections = 5
        manager.provider_stats["fast"].active_connections = 1
        
        request = DataRequest(data_type="stock_basic")
        data = await manager.fetch_data(request)
        
        assert isinstance(data, pd.DataFrame)
        # 应该选择连接数最少的提供者
    
    @pytest.mark.asyncio
    async def test_performance_based_load_balance(self, manager_with_providers):
        """测试基于性能的负载均衡"""
        manager = manager_with_providers
        manager.set_load_balance_strategy(LoadBalanceStrategy.PERFORMANCE_BASED)
        
        # 先建立一些性能统计
        for _ in range(3):
            try:
                request = DataRequest(data_type="stock_basic")
                await manager.fetch_data(request)
            except:
                pass
        
        request = DataRequest(data_type="stock_basic")
        data = await manager.fetch_data(request)
        
        assert isinstance(data, pd.DataFrame)


class TestCircuitBreaker:
    """熔断器测试"""
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_opens(self, manager_with_providers):
        """测试熔断器开启"""
        manager = manager_with_providers
        manager.circuit_breaker_enabled = True
        manager.circuit_breaker_threshold = 0.5
        
        # 执行多次请求让unreliable提供者失败率超过阈值
        for _ in range(10):
            try:
                request = DataRequest(data_type="stock_daily")  # unreliable是第一优先级
                await manager.fetch_data(request)
            except:
                pass
        
        # 检查熔断器是否开启
        is_open = manager._is_circuit_breaker_open("unreliable")
        assert is_open is True
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_disabled(self, manager_with_providers):
        """测试禁用熔断器"""
        manager = manager_with_providers
        manager.circuit_breaker_enabled = False
        
        # 即使失败率很高，熔断器也不应该开启
        for _ in range(10):
            try:
                request = DataRequest(data_type="stock_daily")
                await manager.fetch_data(request)
            except:
                pass
        
        is_open = manager._is_circuit_breaker_open("unreliable")
        assert is_open is False


class TestEventCallbacks:
    """事件回调测试"""
    
    @pytest.mark.asyncio
    async def test_provider_failed_event(self, manager_with_providers):
        """测试提供者失败事件"""
        manager = manager_with_providers
        
        failed_providers = []
        
        def on_provider_failed(provider_name, error):
            failed_providers.append(provider_name)
        
        manager.add_event_callback('provider_failed', on_provider_failed)
        
        # 触发失败
        for _ in range(5):
            try:
                request = DataRequest(data_type="stock_daily")  # unreliable是第一优先级
                await manager.fetch_data(request)
            except:
                pass
        
        assert len(failed_providers) > 0
        assert "unreliable" in failed_providers
    
    @pytest.mark.asyncio
    async def test_fallback_triggered_event(self, manager_with_providers):
        """测试fallback触发事件"""
        manager = manager_with_providers
        
        fallback_events = []
        
        def on_fallback_triggered(from_provider, data_type):
            fallback_events.append((from_provider, data_type))
        
        manager.add_event_callback('fallback_triggered', on_fallback_triggered)
        
        # 触发fallback
        for _ in range(3):
            try:
                request = DataRequest(data_type="stock_daily")
                await manager.fetch_data(request)
            except:
                pass
        
        assert len(fallback_events) > 0


class TestCoordinationStats:
    """协调机制统计测试"""
    
    def test_get_coordination_stats(self, manager_with_providers):
        """测试获取协调统计信息"""
        manager = manager_with_providers
        manager.set_fallback_strategy(FallbackStrategy.PERFORMANCE_BASED)
        manager.set_load_balance_strategy(LoadBalanceStrategy.ROUND_ROBIN)
        
        stats = manager.get_coordination_stats()
        
        assert stats['fallback_strategy'] == 'performance_based'
        assert stats['load_balance_strategy'] == 'round_robin'
        assert stats['circuit_breaker_enabled'] is True
        assert stats['total_providers'] == 3
        assert 'healthy_providers' in stats
        assert 'circuit_breaker_open_providers' in stats
    
    @pytest.mark.asyncio
    async def test_provider_recovery_tracking(self, manager_with_providers):
        """测试提供者恢复跟踪"""
        manager = manager_with_providers
        
        recovered_providers = []
        
        def on_provider_recovered(provider_name):
            recovered_providers.append(provider_name)
        
        manager.add_event_callback('provider_recovered', on_provider_recovered)
        
        # 先让提供者失败
        manager.provider_health["fast"].is_healthy = False
        
        # 然后成功请求应该触发恢复事件
        request = DataRequest(data_type="stock_basic")
        try:
            await manager.fetch_data(request)
        except:
            pass
        
        # 检查是否有恢复事件（这个测试可能需要调整，因为fast提供者可能不是第一选择）


class TestAdvancedScenarios:
    """高级场景测试"""
    
    @pytest.mark.asyncio
    async def test_all_providers_circuit_breaker_open(self, manager_with_providers):
        """测试所有提供者熔断器都开启的情况"""
        manager = manager_with_providers
        manager.circuit_breaker_enabled = True
        manager.circuit_breaker_threshold = 0.1  # 很低的阈值
        
        # 让所有提供者都失败多次
        for provider_name in manager.providers.keys():
            for _ in range(10):
                manager._record_failure(provider_name, "Test error", 1.0)
        
        # 即使熔断器都开启，也应该尝试获取数据
        request = DataRequest(data_type="stock_basic")
        try:
            data = await manager.fetch_data(request)
            assert isinstance(data, pd.DataFrame)
        except DataSourceError:
            # 如果所有提供者都失败，抛出异常也是正常的
            pass
    
    @pytest.mark.asyncio
    async def test_concurrent_requests(self, manager_with_providers):
        """测试并发请求"""
        manager = manager_with_providers
        manager.set_load_balance_strategy(LoadBalanceStrategy.LEAST_CONNECTIONS)
        
        # 创建多个并发请求
        tasks = []
        for _ in range(10):
            request = DataRequest(data_type="stock_basic")
            tasks.append(manager.fetch_data(request))
        
        # 执行并发请求
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 检查结果
        successful_results = [r for r in results if isinstance(r, pd.DataFrame)]
        assert len(successful_results) > 0
        
        # 检查连接数统计
        total_connections = sum(
            stats.active_connections 
            for stats in manager.provider_stats.values()
        )
        # 所有请求完成后，活跃连接数应该为0
        assert total_connections == 0