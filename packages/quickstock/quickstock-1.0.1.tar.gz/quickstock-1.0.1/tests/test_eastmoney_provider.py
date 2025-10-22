"""
东方财富数据提供者测试
"""

import pytest
import pandas as pd
from unittest.mock import AsyncMock, patch, MagicMock
import asyncio

from quickstock.providers.eastmoney import EastmoneyProvider
from quickstock.config import Config
from quickstock.core.errors import DataSourceError, NetworkError, ValidationError


class TestEastmoneyProvider:
    """东方财富提供者测试类"""
    
    @pytest.fixture
    def config(self):
        """创建测试配置"""
        return Config(
            request_timeout=30,
            max_retries=3,
            retry_delay=1.0
        )
    
    @pytest.fixture
    def provider(self, config):
        """创建东方财富提供者实例"""
        return EastmoneyProvider(config)
    
    def test_init(self, provider):
        """测试初始化"""
        assert provider.base_url == "https://push2his.eastmoney.com/api/qt"
        assert provider.trends_url == "https://push2his.eastmoney.com/api/qt/stock/trends2/get"
        assert provider.kline_url == "https://push2his.eastmoney.com/api/qt/stock/kline/get"
        assert "User-Agent" in provider.headers
        assert provider._cache == {}
        assert provider._session is None
    
    def test_get_provider_name(self, provider):
        """测试获取提供者名称"""
        assert provider.get_provider_name() == "eastmoney"
    
    def test_get_rate_limit(self, provider):
        """测试获取速率限制"""
        rate_limit = provider.get_rate_limit()
        assert rate_limit.requests_per_second == 2.0
        assert rate_limit.requests_per_minute == 100
        assert rate_limit.requests_per_hour == 5000
    
    def test_convert_stock_code(self, provider):
        """测试股票代码转换"""
        # 测试深圳股票
        assert provider._convert_stock_code("000001.SZ") == "0.000001"
        assert provider._convert_stock_code("300001.SZ") == "0.300001"
        
        # 测试上海股票
        assert provider._convert_stock_code("600000.SH") == "1.600000"
        assert provider._convert_stock_code("000001.SH") == "1.000001"
        
        # 测试错误格式
        with pytest.raises(ValidationError):
            provider._convert_stock_code("000001")
        
        with pytest.raises(ValidationError):
            provider._convert_stock_code("000001.BJ")
    
    def test_parse_kline_data(self, provider):
        """测试K线数据解析"""
        # 测试正常数据
        klines = [
            "20240101,10.00,10.50,11.00,9.50,1000000,10500000,5.26,5.00,0.50,2.5",
            "20240102,10.50,10.80,11.20,10.30,1200000,12960000,8.57,2.86,0.30,3.0"
        ]
        
        result = provider._parse_kline_data(klines)
        
        assert len(result) == 2
        assert result[0]['trade_date'] == "20240101"
        assert result[0]['open'] == 10.00
        assert result[0]['close'] == 10.50
        assert result[0]['high'] == 11.00
        assert result[0]['low'] == 9.50
        assert result[0]['volume'] == 1000000
        assert result[0]['amount'] == 10500000.0
        
        # 测试异常数据
        invalid_klines = [
            "invalid,data",
            "20240101,invalid,10.50,11.00,9.50,1000000,10500000,5.26,5.00,0.50,2.5"
        ]
        
        result = provider._parse_kline_data(invalid_klines)
        assert len(result) == 0  # 异常数据应该被跳过
    
    @pytest.mark.asyncio
    async def test_get_session(self, provider):
        """测试获取会话"""
        session = await provider._get_session()
        assert session is not None
        assert not session.closed
        
        # 再次获取应该返回同一个会话
        session2 = await provider._get_session()
        assert session is session2
        
        # 清理
        await provider.close()
    
    @pytest.mark.asyncio
    async def test_make_request_success(self, provider):
        """测试成功的HTTP请求"""
        mock_response_data = {
            'rc': 0,
            'data': {
                'klines': ['20240101,10.00,10.50,11.00,9.50,1000000,10500000,5.26,5.00,0.50,2.5']
            }
        }
        
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value=mock_response_data)
            mock_get.return_value.__aenter__.return_value = mock_response
            
            result = await provider._make_request("http://test.com")
            assert result == mock_response_data
        
        await provider.close()
    
    @pytest.mark.asyncio
    async def test_make_request_api_error(self, provider):
        """测试API错误响应"""
        mock_response_data = {
            'rc': -1,
            'rt': 'API Error'
        }
        
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value=mock_response_data)
            mock_get.return_value.__aenter__.return_value = mock_response
            
            with pytest.raises(DataSourceError, match="东方财富API返回错误"):
                await provider._make_request("http://test.com")
        
        await provider.close()
    
    @pytest.mark.asyncio
    async def test_make_request_http_error(self, provider):
        """测试HTTP错误"""
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = AsyncMock()
            mock_response.status = 404
            mock_get.return_value.__aenter__.return_value = mock_response
            
            with pytest.raises(NetworkError, match="HTTP请求失败"):
                await provider._make_request("http://test.com")
        
        await provider.close()
    
    @pytest.mark.asyncio
    async def test_get_stock_basic(self, provider):
        """测试获取股票基础信息"""
        result = await provider.get_stock_basic()
        assert isinstance(result, pd.DataFrame)
        assert result.empty  # 东方财富不支持股票基础信息
    
    @pytest.mark.asyncio
    async def test_get_stock_daily_success(self, provider):
        """测试成功获取股票日线数据"""
        mock_response_data = {
            'rc': 0,
            'data': {
                'klines': [
                    '20240101,10.00,10.50,11.00,9.50,1000000,10500000,5.26,5.00,0.50,2.5',
                    '20240102,10.50,10.80,11.20,10.30,1200000,12960000,8.57,2.86,0.30,3.0'
                ]
            }
        }
        
        with patch.object(provider, '_make_request', return_value=mock_response_data):
            result = await provider.get_stock_daily("000001.SZ", "20240101", "20240102")
            
            assert isinstance(result, pd.DataFrame)
            assert len(result) == 2
            assert 'ts_code' in result.columns
            assert 'trade_date' in result.columns
            assert 'open' in result.columns
            assert 'close' in result.columns
            assert result.iloc[0]['ts_code'] == "000001.SZ"
            assert result.iloc[0]['trade_date'] == "20240101"
            assert result.iloc[0]['open'] == 10.00
    
    @pytest.mark.asyncio
    async def test_get_stock_daily_no_data(self, provider):
        """测试获取股票日线数据无数据"""
        mock_response_data = {
            'rc': 0,
            'data': {
                'klines': []
            }
        }
        
        with patch.object(provider, '_make_request', return_value=mock_response_data):
            result = await provider.get_stock_daily("000001.SZ", "20240101", "20240102")
            
            assert isinstance(result, pd.DataFrame)
            assert result.empty
    
    @pytest.mark.asyncio
    async def test_get_stock_daily_invalid_code(self, provider):
        """测试无效股票代码"""
        from quickstock.utils.validators import ValidationError as ValidatorError
        with pytest.raises(ValidatorError):
            await provider.get_stock_daily("invalid_code", "20240101", "20240102")
    
    @pytest.mark.asyncio
    async def test_get_stock_daily_invalid_date(self, provider):
        """测试无效日期格式"""
        from quickstock.utils.validators import ValidationError as ValidatorError
        with pytest.raises(ValidatorError):
            await provider.get_stock_daily("000001.SZ", "2024-01-01", "20240102")
    
    def test_parse_trends_data(self, provider):
        """测试分时数据解析"""
        # 测试正常数据
        trends = [
            "09:30,10.00,10.50,11.00,9.50,1000000,10500000,5.26,5.00,0.50,2.5",
            "09:31,10.50,10.80,11.20,10.30,1200000,12960000,8.57,2.86,0.30,3.0"
        ]
        
        result = provider._parse_trends_data(trends)
        
        assert len(result) == 2
        assert result[0]['trade_time'] == "09:30"
        assert result[0]['open'] == 10.00
        assert result[0]['close'] == 10.50
        assert result[0]['high'] == 11.00
        assert result[0]['low'] == 9.50
        assert result[0]['volume'] == 1000000
        assert result[0]['amount'] == 10500000.0
    
    @pytest.mark.asyncio
    async def test_get_stock_minute_1min(self, provider):
        """测试获取1分钟数据"""
        mock_response_data = {
            'rc': 0,
            'data': {
                'trends': [
                    '09:30,10.00,10.50,11.00,9.50,1000000,10500000,5.26,5.00,0.50,2.5',
                    '09:31,10.50,10.80,11.20,10.30,1200000,12960000,8.57,2.86,0.30,3.0'
                ]
            }
        }
        
        with patch.object(provider, '_make_request', return_value=mock_response_data):
            result = await provider.get_stock_minute("000001.SZ", "1min")
            
            assert isinstance(result, pd.DataFrame)
            assert len(result) == 2
            assert 'ts_code' in result.columns
            assert 'trade_time' in result.columns
            assert result.iloc[0]['ts_code'] == "000001.SZ"
            assert result.iloc[0]['trade_time'] == "09:30"
    
    @pytest.mark.asyncio
    async def test_get_stock_minute_30min(self, provider):
        """测试获取30分钟数据"""
        mock_response_data = {
            'rc': 0,
            'data': {
                'klines': [
                    '20240101,10.00,10.50,11.00,9.50,1000000,10500000,5.26,5.00,0.50,2.5',
                    '20240102,10.50,10.80,11.20,10.30,1200000,12960000,8.57,2.86,0.30,3.0'
                ]
            }
        }
        
        with patch.object(provider, '_make_request', return_value=mock_response_data):
            result = await provider.get_stock_minute("000001.SZ", "30min")
            
            assert isinstance(result, pd.DataFrame)
            assert len(result) == 2
            assert 'ts_code' in result.columns
            assert 'trade_date' in result.columns
            assert result.iloc[0]['ts_code'] == "000001.SZ"
    
    @pytest.mark.asyncio
    async def test_get_stock_minute_invalid_freq(self, provider):
        """测试无效频率"""
        with pytest.raises(ValidationError, match="不支持的分钟频率"):
            await provider.get_stock_minute("000001.SZ", "5min")
    
    @pytest.mark.asyncio
    async def test_get_stock_weekly(self, provider):
        """测试获取周线数据"""
        mock_response_data = {
            'rc': 0,
            'data': {
                'klines': [
                    '20240101,10.00,10.50,11.00,9.50,1000000,10500000,5.26,5.00,0.50,2.5',
                    '20240108,10.50,10.80,11.20,10.30,1200000,12960000,8.57,2.86,0.30,3.0'
                ]
            }
        }
        
        with patch.object(provider, '_make_request', return_value=mock_response_data):
            result = await provider.get_stock_weekly("000001.SZ")
            
            assert isinstance(result, pd.DataFrame)
            assert len(result) == 2
            assert 'ts_code' in result.columns
            assert 'trade_date' in result.columns
            assert result.iloc[0]['ts_code'] == "000001.SZ"
    
    @pytest.mark.asyncio
    async def test_get_stock_monthly(self, provider):
        """测试获取月线数据"""
        mock_response_data = {
            'rc': 0,
            'data': {
                'klines': [
                    '20240101,10.00,10.50,11.00,9.50,1000000,10500000,5.26,5.00,0.50,2.5',
                    '20240201,10.50,10.80,11.20,10.30,1200000,12960000,8.57,2.86,0.30,3.0'
                ]
            }
        }
        
        with patch.object(provider, '_make_request', return_value=mock_response_data):
            result = await provider.get_stock_monthly("000001.SZ")
            
            assert isinstance(result, pd.DataFrame)
            assert len(result) == 2
            assert 'ts_code' in result.columns
            assert 'trade_date' in result.columns
            assert result.iloc[0]['ts_code'] == "000001.SZ"

    @pytest.mark.asyncio
    async def test_get_trade_cal(self, provider):
        """测试获取交易日历"""
        result = await provider.get_trade_cal("20240101", "20240131")
        assert isinstance(result, pd.DataFrame)
        assert result.empty  # 东方财富不支持交易日历
    
    def test_get_cache_key(self, provider):
        """测试缓存键生成"""
        key1 = provider._get_cache_key('stock_daily', ts_code='000001.SZ', start_date='20240101')
        key2 = provider._get_cache_key('stock_daily', ts_code='000001.SZ', start_date='20240101')
        key3 = provider._get_cache_key('stock_daily', ts_code='000002.SZ', start_date='20240101')
        
        assert key1 == key2  # 相同参数应该生成相同的键
        assert key1 != key3  # 不同参数应该生成不同的键
        assert len(key1) == 32  # MD5哈希长度
    
    def test_cache_operations(self, provider):
        """测试缓存操作"""
        cache_key = "test_key"
        test_data = pd.DataFrame({'a': [1, 2, 3]})
        
        # 测试缓存设置和获取
        provider._set_cache(cache_key, test_data, expire_seconds=1)
        cached_data = provider._get_from_cache(cache_key)
        
        assert cached_data is not None
        pd.testing.assert_frame_equal(cached_data, test_data)
        
        # 测试缓存过期
        import time
        time.sleep(1.1)  # 等待缓存过期
        expired_data = provider._get_from_cache(cache_key)
        assert expired_data is None
    
    def test_deduplicate_data(self, provider):
        """测试数据去重"""
        # 测试日线数据去重
        df = pd.DataFrame({
            'ts_code': ['000001.SZ', '000001.SZ', '000001.SZ'],
            'trade_date': ['20240101', '20240101', '20240102'],
            'close': [10.0, 10.5, 11.0]
        })
        
        result = provider._deduplicate_data(df)
        assert len(result) == 2  # 应该去掉一个重复的
        assert result.iloc[0]['close'] == 10.5  # 应该保留最后一个
    
    def test_clear_cache(self, provider):
        """测试清空缓存"""
        # 设置一些缓存
        provider._set_cache("key1", pd.DataFrame({'a': [1]}))
        provider._set_cache("key2", pd.DataFrame({'b': [2]}))
        
        assert len(provider._cache) == 2
        
        # 清空缓存
        provider.clear_cache()
        
        assert len(provider._cache) == 0
        assert len(provider._cache_expire_time) == 0
    
    def test_get_cache_stats(self, provider):
        """测试获取缓存统计"""
        # 设置一些缓存
        provider._set_cache("key1", pd.DataFrame({'a': [1]}), expire_seconds=3600)
        provider._set_cache("key2", pd.DataFrame({'b': [2]}), expire_seconds=-1)  # 已过期
        
        stats = provider.get_cache_stats()
        
        assert stats['total_cache_entries'] == 2
        assert stats['valid_cache_entries'] == 1
        assert stats['expired_cache_entries'] == 1
    
    @pytest.mark.asyncio
    async def test_health_check(self, provider):
        """测试健康检查"""
        # Mock成功响应
        mock_response = {'rc': 0, 'data': {}}
        
        with patch.object(provider, '_make_request', return_value=mock_response):
            result = await provider.health_check()
            assert result is True
        
        # Mock失败响应
        with patch.object(provider, '_make_request', side_effect=NetworkError("Network error")):
            result = await provider.health_check()
            assert result is False
    
    @pytest.mark.asyncio
    async def test_get_stock_daily_with_cache(self, provider):
        """测试带缓存的股票日线数据获取"""
        mock_response_data = {
            'rc': 0,
            'data': {
                'klines': [
                    '20240101,10.00,10.50,11.00,9.50,1000000,10500000,5.26,5.00,0.50,2.5'
                ]
            }
        }
        
        with patch.object(provider, '_make_request', return_value=mock_response_data) as mock_request:
            # 第一次请求
            result1 = await provider.get_stock_daily("000001.SZ", "20240101", "20240102")
            assert len(result1) == 1
            assert mock_request.call_count == 1
            
            # 第二次请求应该使用缓存
            result2 = await provider.get_stock_daily("000001.SZ", "20240101", "20240102")
            assert len(result2) == 1
            assert mock_request.call_count == 1  # 没有新的请求
            
            # 验证数据一致性
            pd.testing.assert_frame_equal(result1, result2)
    
    @pytest.mark.asyncio
    async def test_close(self, provider):
        """测试关闭会话"""
        # 先获取会话
        session = await provider._get_session()
        assert not session.closed
        
        # 关闭会话
        await provider.close()
        assert session.closed


if __name__ == "__main__":
    pytest.main([__file__])