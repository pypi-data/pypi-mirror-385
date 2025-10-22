"""
数据提供者接口的单元测试
"""

import pytest
import pandas as pd
from unittest.mock import AsyncMock

from quickstock.providers.base import DataProvider, RateLimit
from quickstock.config import Config


class MockDataProvider(DataProvider):
    """用于测试的模拟数据提供者"""
    
    async def get_stock_basic(self, **kwargs) -> pd.DataFrame:
        """模拟获取股票基础信息"""
        return pd.DataFrame({
            'ts_code': ['000001.SZ', '000002.SZ'],
            'name': ['平安银行', '万科A'],
            'market': ['主板', '主板']
        })
    
    async def get_stock_daily(self, ts_code: str, start_date: str, 
                             end_date: str) -> pd.DataFrame:
        """模拟获取股票日线数据"""
        return pd.DataFrame({
            'ts_code': [ts_code, ts_code],
            'trade_date': ['20230101', '20230102'],
            'open': [10.0, 10.5],
            'high': [10.5, 11.0],
            'low': [9.8, 10.2],
            'close': [10.2, 10.8],
            'volume': [1000000, 1200000]
        })
    
    async def get_trade_cal(self, start_date: str, end_date: str) -> pd.DataFrame:
        """模拟获取交易日历"""
        return pd.DataFrame({
            'cal_date': ['20230101', '20230102', '20230103'],
            'is_open': [0, 1, 1],
            'exchange': ['SSE', 'SSE', 'SSE']
        })


class TestRateLimit:
    """RateLimit类测试"""
    
    def test_default_rate_limit(self):
        """测试默认速率限制"""
        rate_limit = RateLimit()
        
        assert rate_limit.requests_per_second == 1.0
        assert rate_limit.requests_per_minute == 60
        assert rate_limit.requests_per_hour == 3600
    
    def test_custom_rate_limit(self):
        """测试自定义速率限制"""
        rate_limit = RateLimit(
            requests_per_second=2.0,
            requests_per_minute=120,
            requests_per_hour=7200
        )
        
        assert rate_limit.requests_per_second == 2.0
        assert rate_limit.requests_per_minute == 120
        assert rate_limit.requests_per_hour == 7200


class TestDataProvider:
    """DataProvider基类测试"""
    
    def setup_method(self):
        """测试前准备"""
        self.config = Config()
        self.provider = MockDataProvider(self.config)
    
    def test_provider_initialization(self):
        """测试提供者初始化"""
        assert self.provider.config == self.config
        assert isinstance(self.provider, DataProvider)
    
    def test_get_provider_name(self):
        """测试获取提供者名称"""
        name = self.provider.get_provider_name()
        assert name == 'mockdata'  # MockDataProvider -> mockdata
    
    def test_is_available_default(self):
        """测试默认可用性检查"""
        assert self.provider.is_available() is True
    
    def test_get_rate_limit_default(self):
        """测试默认速率限制"""
        rate_limit = self.provider.get_rate_limit()
        assert isinstance(rate_limit, RateLimit)
        assert rate_limit.requests_per_second == 1.0
    
    @pytest.mark.asyncio
    async def test_health_check_default(self):
        """测试默认健康检查"""
        health = await self.provider.health_check()
        assert health is True
    
    @pytest.mark.asyncio
    async def test_get_stock_basic(self):
        """测试获取股票基础信息"""
        data = await self.provider.get_stock_basic()
        
        assert isinstance(data, pd.DataFrame)
        assert len(data) == 2
        assert 'ts_code' in data.columns
        assert 'name' in data.columns
        assert data.iloc[0]['ts_code'] == '000001.SZ'
    
    @pytest.mark.asyncio
    async def test_get_stock_daily(self):
        """测试获取股票日线数据"""
        data = await self.provider.get_stock_daily('000001.SZ', '20230101', '20230102')
        
        assert isinstance(data, pd.DataFrame)
        assert len(data) == 2
        assert 'ts_code' in data.columns
        assert 'trade_date' in data.columns
        assert 'open' in data.columns
        assert 'close' in data.columns
        assert data.iloc[0]['ts_code'] == '000001.SZ'
    
    @pytest.mark.asyncio
    async def test_get_trade_cal(self):
        """测试获取交易日历"""
        data = await self.provider.get_trade_cal('20230101', '20230103')
        
        assert isinstance(data, pd.DataFrame)
        assert len(data) == 3
        assert 'cal_date' in data.columns
        assert 'is_open' in data.columns
        assert data.iloc[0]['cal_date'] == '20230101'
    
    @pytest.mark.asyncio
    async def test_get_stock_minute_not_implemented(self):
        """测试分钟数据获取（默认不支持）"""
        with pytest.raises(NotImplementedError, match="mockdata不支持分钟数据获取"):
            await self.provider.get_stock_minute('000001.SZ', '1min')
    
    @pytest.mark.asyncio
    async def test_get_index_basic_not_implemented(self):
        """测试指数基础信息获取（默认不支持）"""
        with pytest.raises(NotImplementedError, match="mockdata不支持指数基础信息获取"):
            await self.provider.get_index_basic()
    
    @pytest.mark.asyncio
    async def test_get_index_daily_not_implemented(self):
        """测试指数日线数据获取（默认不支持）"""
        with pytest.raises(NotImplementedError, match="mockdata不支持指数日线数据获取"):
            await self.provider.get_index_daily('000001.SH', '20230101', '20230102')
    
    @pytest.mark.asyncio
    async def test_get_fund_basic_not_implemented(self):
        """测试基金基础信息获取（默认不支持）"""
        with pytest.raises(NotImplementedError, match="mockdata不支持基金基础信息获取"):
            await self.provider.get_fund_basic()
    
    @pytest.mark.asyncio
    async def test_get_fund_nav_not_implemented(self):
        """测试基金净值数据获取（默认不支持）"""
        with pytest.raises(NotImplementedError, match="mockdata不支持基金净值数据获取"):
            await self.provider.get_fund_nav('110001.OF', '20230101', '20230102')


class TestDataProviderAbstract:
    """测试DataProvider抽象类"""
    
    def test_cannot_instantiate_abstract_class(self):
        """测试不能直接实例化抽象类"""
        config = Config()
        
        with pytest.raises(TypeError):
            DataProvider(config)
    
    def test_must_implement_abstract_methods(self):
        """测试必须实现抽象方法"""
        config = Config()
        
        class IncompleteProvider(DataProvider):
            # 没有实现所有抽象方法
            async def get_stock_basic(self, **kwargs) -> pd.DataFrame:
                return pd.DataFrame()
        
        with pytest.raises(TypeError):
            IncompleteProvider(config)


class TestDataProviderWithCustomMethods:
    """测试自定义方法的数据提供者"""
    
    def setup_method(self):
        """测试前准备"""
        self.config = Config()
    
    def test_provider_with_minute_data_support(self):
        """测试支持分钟数据的提供者"""
        
        class MinuteDataProvider(DataProvider):
            async def get_stock_basic(self, **kwargs) -> pd.DataFrame:
                return pd.DataFrame()
            
            async def get_stock_daily(self, ts_code: str, start_date: str, 
                                     end_date: str) -> pd.DataFrame:
                return pd.DataFrame()
            
            async def get_trade_cal(self, start_date: str, end_date: str) -> pd.DataFrame:
                return pd.DataFrame()
            
            async def get_stock_minute(self, ts_code: str, freq: str = '1min',
                                      start_date: str = None, end_date: str = None) -> pd.DataFrame:
                return pd.DataFrame({
                    'ts_code': [ts_code],
                    'datetime': ['2023-01-01 09:30:00'],
                    'open': [10.0],
                    'close': [10.1]
                })
        
        provider = MinuteDataProvider(self.config)
        assert provider.get_provider_name() == 'minutedata'
    
    def test_provider_with_custom_rate_limit(self):
        """测试自定义速率限制的提供者"""
        
        class CustomRateLimitProvider(DataProvider):
            async def get_stock_basic(self, **kwargs) -> pd.DataFrame:
                return pd.DataFrame()
            
            async def get_stock_daily(self, ts_code: str, start_date: str, 
                                     end_date: str) -> pd.DataFrame:
                return pd.DataFrame()
            
            async def get_trade_cal(self, start_date: str, end_date: str) -> pd.DataFrame:
                return pd.DataFrame()
            
            def get_rate_limit(self) -> RateLimit:
                return RateLimit(requests_per_second=0.5, requests_per_minute=30)
        
        provider = CustomRateLimitProvider(self.config)
        rate_limit = provider.get_rate_limit()
        assert rate_limit.requests_per_second == 0.5
        assert rate_limit.requests_per_minute == 30