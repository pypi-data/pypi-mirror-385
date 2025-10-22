"""
数据源管理器测试

测试DataSourceManager的核心功能
"""

import pytest
import asyncio
import pandas as pd
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timedelta

from quickstock.config import Config
from quickstock.models import DataRequest
from quickstock.providers.manager import DataSourceManager, ProviderHealth, ProviderStats
from quickstock.providers.base import DataProvider
from quickstock.core.errors import DataSourceError, ValidationError


class MockProvider(DataProvider):
    """模拟数据提供者"""
    
    def __init__(self, config, name="mock", should_fail=False, response_delay=0.1):
        super().__init__(config)
        self.name = name
        self.should_fail = should_fail
        self.response_delay = response_delay
        self._available = True
        self._healthy = True
    
    async def get_stock_basic(self, **kwargs) -> pd.DataFrame:
        await asyncio.sleep(self.response_delay)
        if self.should_fail:
            raise Exception(f"Mock error from {self.name}")
        return pd.DataFrame({
            'ts_code': ['000001.SZ', '000002.SZ'],
            'name': ['平安银行', '万科A'],
            'market': ['主板', '主板']
        })
    
    async def get_stock_daily(self, ts_code: str, start_date: str, end_date: str) -> pd.DataFrame:
        await asyncio.sleep(self.response_delay)
        if self.should_fail:
            raise Exception(f"Mock error from {self.name}")
        return pd.DataFrame({
            'ts_code': [ts_code, ts_code],
            'trade_date': ['20240101', '20240102'],
            'close': [10.0, 10.5]
        })
    
    async def get_trade_cal(self, start_date: str, end_date: str) -> pd.DataFrame:
        await asyncio.sleep(self.response_delay)
        if self.should_fail:
            raise Exception(f"Mock error from {self.name}")
        return pd.DataFrame({
            'cal_date': ['20240101', '20240102'],
            'is_open': [1, 1]
        })
    
    def is_available(self) -> bool:
        return self._available
    
    async def health_check(self) -> bool:
        return self._healthy
    
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
            'stock_basic': ['provider1', 'provider2'],
            'stock_daily': ['provider2', 'provider1'],
            'trade_cal': ['provider1']
        }
    )


@pytest.fixture
def manager(config):
    """数据源管理器实例"""
    return DataSourceManager(config)


class TestDataSourceManager:
    """数据源管理器测试类"""    

    def test_init(self, config):
        """测试初始化"""
        manager = DataSourceManager(config)
        
        assert manager.config == config
        assert isinstance(manager.providers, dict)
        assert isinstance(manager.provider_health, dict)
        assert isinstance(manager.provider_stats, dict)
    
    def test_register_provider(self, manager, config):
        """测试注册数据提供者"""
        provider = MockProvider(config, "test_provider")
        
        manager.register_provider("test_provider", provider)
        
        assert "test_provider" in manager.providers
        assert manager.providers["test_provider"] == provider
        assert "test_provider" in manager.provider_stats
        assert "test_provider" in manager.provider_health
    
    def test_unregister_provider(self, manager, config):
        """测试注销数据提供者"""
        provider = MockProvider(config, "test_provider")
        manager.register_provider("test_provider", provider)
        
        manager.unregister_provider("test_provider")
        
        assert "test_provider" not in manager.providers
        assert "test_provider" not in manager.provider_stats
        assert "test_provider" not in manager.provider_health
    
    def test_list_providers(self, manager, config):
        """测试获取提供者列表"""
        provider1 = MockProvider(config, "provider1")
        provider2 = MockProvider(config, "provider2")
        
        manager.register_provider("provider1", provider1)
        manager.register_provider("provider2", provider2)
        
        providers = manager.list_providers()
        assert set(providers) == {"provider1", "provider2"}
    
    def test_get_provider(self, manager, config):
        """测试获取数据提供者"""
        provider = MockProvider(config, "test_provider")
        manager.register_provider("test_provider", provider)
        
        retrieved_provider = manager.get_provider("test_provider")
        assert retrieved_provider == provider
        
        # 测试不存在的提供者
        assert manager.get_provider("nonexistent") is None
    
    def test_get_provider_priority(self, manager):
        """测试获取数据源优先级"""
        priority = manager._get_provider_priority("stock_basic")
        assert priority == []  # 没有注册提供者时返回空列表
        
        # 注册提供者后测试
        provider1 = MockProvider(manager.config, "provider1")
        provider2 = MockProvider(manager.config, "provider2")
        manager.register_provider("provider1", provider1)
        manager.register_provider("provider2", provider2)
        
        priority = manager._get_provider_priority("stock_basic")
        assert priority == ["provider1", "provider2"]
        
        priority = manager._get_provider_priority("stock_daily")
        assert priority == ["provider2", "provider1"]
    
    @pytest.mark.asyncio
    async def test_is_provider_healthy(self, manager, config):
        """测试提供者健康检查"""
        # 健康的提供者
        healthy_provider = MockProvider(config, "healthy")
        healthy_provider._healthy = True
        manager.register_provider("healthy", healthy_provider)
        
        is_healthy = await manager._is_provider_healthy("healthy")
        assert is_healthy is True
        
        # 不健康的提供者
        unhealthy_provider = MockProvider(config, "unhealthy")
        unhealthy_provider._healthy = False
        manager.register_provider("unhealthy", unhealthy_provider)
        
        is_healthy = await manager._is_provider_healthy("unhealthy")
        assert is_healthy is False
    
    @pytest.mark.asyncio
    async def test_fetch_data_success(self, manager, config):
        """测试成功获取数据"""
        provider = MockProvider(config, "provider1")
        manager.register_provider("provider1", provider)
        
        request = DataRequest(data_type="stock_basic")
        data = await manager.fetch_data(request)
        
        assert isinstance(data, pd.DataFrame)
        assert not data.empty
        assert "ts_code" in data.columns
        
        # 检查统计信息
        stats = manager.provider_stats["provider1"]
        assert stats.total_requests == 1
        assert stats.successful_requests == 1
        assert stats.failed_requests == 0
    
    @pytest.mark.asyncio
    async def test_fetch_data_fallback(self, manager, config):
        """测试fallback机制"""
        # 第一个提供者会失败
        failing_provider = MockProvider(config, "provider1", should_fail=True)
        manager.register_provider("provider1", failing_provider)
        
        # 第二个提供者正常
        working_provider = MockProvider(config, "provider2")
        manager.register_provider("provider2", working_provider)
        
        request = DataRequest(data_type="stock_basic")
        data = await manager.fetch_data(request)
        
        assert isinstance(data, pd.DataFrame)
        assert not data.empty
        
        # 检查统计信息
        stats1 = manager.provider_stats["provider1"]
        assert stats1.failed_requests == 1
        
        stats2 = manager.provider_stats["provider2"]
        assert stats2.successful_requests == 1
    
    @pytest.mark.asyncio
    async def test_fetch_data_all_fail(self, manager, config):
        """测试所有数据源都失败的情况"""
        failing_provider1 = MockProvider(config, "provider1", should_fail=True)
        failing_provider2 = MockProvider(config, "provider2", should_fail=True)
        
        manager.register_provider("provider1", failing_provider1)
        manager.register_provider("provider2", failing_provider2)
        
        request = DataRequest(data_type="stock_basic")
        
        with pytest.raises(DataSourceError):
            await manager.fetch_data(request)
    
    @pytest.mark.asyncio
    async def test_health_check_all(self, manager, config):
        """测试所有提供者健康检查"""
        healthy_provider = MockProvider(config, "healthy")
        healthy_provider._healthy = True
        manager.register_provider("healthy", healthy_provider)
        
        unhealthy_provider = MockProvider(config, "unhealthy")
        unhealthy_provider._healthy = False
        manager.register_provider("unhealthy", unhealthy_provider)
        
        results = await manager.health_check_all()
        
        assert results["healthy"] is True
        assert results["unhealthy"] is False
    
    def test_record_success(self, manager, config):
        """测试记录成功统计"""
        provider = MockProvider(config, "provider1")
        manager.register_provider("provider1", provider)
        
        manager._record_success("provider1", 0.5)
        
        stats = manager.provider_stats["provider1"]
        assert stats.total_requests == 1
        assert stats.successful_requests == 1
        assert stats.total_response_time == 0.5
        assert stats.success_rate == 1.0
    
    def test_record_failure(self, manager, config):
        """测试记录失败统计"""
        provider = MockProvider(config, "provider1")
        manager.register_provider("provider1", provider)
        
        manager._record_failure("provider1", "Test error", 0.5)
        
        stats = manager.provider_stats["provider1"]
        assert stats.total_requests == 1
        assert stats.failed_requests == 1
        assert stats.success_rate == 0.0
        
        health = manager.provider_health["provider1"]
        assert health.error_count == 1
        assert health.last_error == "Test error"
    
    def test_get_provider_stats(self, manager, config):
        """测试获取提供者统计信息"""
        provider = MockProvider(config, "provider1")
        manager.register_provider("provider1", provider)
        
        # 获取单个提供者统计
        stats = manager.get_provider_stats("provider1")
        assert "provider1" in stats
        assert isinstance(stats["provider1"], ProviderStats)
        
        # 获取所有提供者统计
        all_stats = manager.get_provider_stats()
        assert "provider1" in all_stats
    
    def test_get_provider_health(self, manager, config):
        """测试获取提供者健康状态"""
        provider = MockProvider(config, "provider1")
        manager.register_provider("provider1", provider)
        
        # 获取单个提供者健康状态
        health = manager.get_provider_health("provider1")
        assert "provider1" in health
        assert isinstance(health["provider1"], ProviderHealth)
        
        # 获取所有提供者健康状态
        all_health = manager.get_provider_health()
        assert "provider1" in all_health
    
    def test_reset_stats(self, manager, config):
        """测试重置统计信息"""
        provider = MockProvider(config, "provider1")
        manager.register_provider("provider1", provider)
        
        # 记录一些统计信息
        manager._record_success("provider1", 0.5)
        manager._record_failure("provider1", "Test error", 0.5)
        
        # 重置统计
        manager.reset_stats("provider1")
        
        stats = manager.provider_stats["provider1"]
        assert stats.total_requests == 0
        assert stats.successful_requests == 0
        assert stats.failed_requests == 0
        
        health = manager.provider_health["provider1"]
        assert health.error_count == 0
        assert health.last_error is None
    
    def test_get_best_provider(self, manager, config):
        """测试获取最佳提供者"""
        provider1 = MockProvider(config, "provider1")
        provider2 = MockProvider(config, "provider2")
        
        manager.register_provider("provider1", provider1)
        manager.register_provider("provider2", provider2)
        
        # 模拟provider1性能更好
        manager._record_success("provider1", 0.2)  # 快速响应
        manager._record_success("provider1", 0.3)
        
        manager._record_success("provider2", 1.0)  # 慢响应
        manager._record_failure("provider2", "Error", 1.0)  # 有失败
        
        best = manager.get_best_provider("stock_basic")
        assert best == "provider1"
    
    @pytest.mark.asyncio
    async def test_test_provider(self, manager, config):
        """测试提供者测试功能"""
        working_provider = MockProvider(config, "working")
        failing_provider = MockProvider(config, "failing", should_fail=True)
        
        manager.register_provider("working", working_provider)
        manager.register_provider("failing", failing_provider)
        
        # 测试正常提供者
        result = await manager.test_provider("working")
        assert result is True
        
        # 测试失败提供者
        result = await manager.test_provider("failing")
        assert result is False
        
        # 测试不存在的提供者
        result = await manager.test_provider("nonexistent")
        assert result is False
    
    @pytest.mark.asyncio
    async def test_fetch_different_data_types(self, manager, config):
        """测试获取不同类型的数据"""
        provider = MockProvider(config, "provider1")
        manager.register_provider("provider1", provider)
        
        # 测试股票基础数据
        request = DataRequest(data_type="stock_basic")
        data = await manager.fetch_data(request)
        assert isinstance(data, pd.DataFrame)
        
        # 测试股票日线数据
        request = DataRequest(
            data_type="stock_daily",
            ts_code="000001.SZ",
            start_date="20240101",
            end_date="20240102"
        )
        data = await manager.fetch_data(request)
        assert isinstance(data, pd.DataFrame)
        
        # 测试交易日历
        request = DataRequest(
            data_type="trade_cal",
            start_date="20240101",
            end_date="20240102"
        )
        data = await manager.fetch_data(request)
        assert isinstance(data, pd.DataFrame)
    
    @pytest.mark.asyncio
    async def test_unsupported_data_type(self, manager, config):
        """测试不支持的数据类型"""
        provider = MockProvider(config, "provider1")
        manager.register_provider("provider1", provider)
        
        request = DataRequest(data_type="unsupported_type")
        
        with pytest.raises(DataSourceError, match="不支持的数据类型"):
            await manager.fetch_data(request)


class TestProviderStats:
    """提供者统计信息测试"""
    
    def test_success_rate(self):
        """测试成功率计算"""
        stats = ProviderStats("test")
        assert stats.success_rate == 1.0  # 没有请求时默认为1.0
        
        stats.total_requests = 10
        stats.successful_requests = 8
        assert stats.success_rate == 0.8
    
    def test_average_response_time(self):
        """测试平均响应时间计算"""
        stats = ProviderStats("test")
        assert stats.average_response_time == 0.0  # 没有成功请求时为0
        
        stats.successful_requests = 2
        stats.total_response_time = 1.0
        assert stats.average_response_time == 0.5


class TestProviderHealth:
    """提供者健康状态测试"""
    
    def test_init(self):
        """测试初始化"""
        health = ProviderHealth("test")
        assert health.name == "test"
        assert health.is_healthy is True
        assert health.error_count == 0
        assert health.last_error is None