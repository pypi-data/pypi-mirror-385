"""
数据管理器单元测试
"""

import pytest
import pandas as pd
import tempfile
import os
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

from quickstock.core.data_manager import DataManager
from quickstock.models import DataRequest
from quickstock.core.errors import ValidationError, DataSourceError


class TestDataManager:
    """测试数据管理器"""
    
    @pytest.fixture
    def mock_config(self):
        """创建模拟配置"""
        config = Mock()
        config.cache_enabled = True
        config.cache_expire_hours = 24
        config.memory_cache_size = 100
        config.sqlite_db_path = tempfile.mktemp(suffix='.db')
        config.max_retries = 3
        config.retry_delay = 1.0
        return config
    
    @pytest.fixture
    def sample_data(self):
        """创建测试数据"""
        return pd.DataFrame({
            'ts_code': ['000001.SZ', '000002.SZ'],
            'name': ['平安银行', '万科A'],
            'close': [10.5, 20.3]
        })
    
    @pytest.fixture
    def data_manager(self, mock_config):
        """创建数据管理器实例"""
        manager = DataManager(mock_config)
        yield manager
        # 清理
        if os.path.exists(mock_config.sqlite_db_path):
            os.unlink(mock_config.sqlite_db_path)
    
    @pytest.mark.asyncio
    async def test_get_data_from_cache(self, data_manager, sample_data):
        """测试从缓存获取数据"""
        request = DataRequest(data_type='stock_basic')
        
        # 模拟缓存层返回数据
        with patch.object(data_manager.cache_layer, 'get', return_value=sample_data):
            result = await data_manager.get_data(request)
            
            assert result.equals(sample_data)
    
    @pytest.mark.asyncio
    async def test_get_data_from_source(self, data_manager, sample_data):
        """测试从数据源获取数据"""
        request = DataRequest(data_type='stock_basic')
        
        # 模拟缓存未命中
        with patch.object(data_manager.cache_layer, 'get', return_value=None):
            # 模拟数据源返回数据
            with patch.object(data_manager.source_manager, 'fetch_data', return_value=sample_data):
                # 模拟格式化器返回数据
                with patch.object(data_manager.formatter, 'format_data', return_value=sample_data):
                    # 模拟缓存设置
                    with patch.object(data_manager.cache_layer, 'set') as mock_set:
                        result = await data_manager.get_data(request)
                        
                        assert result.equals(sample_data)
                        # 验证数据被缓存
                        mock_set.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_data_validation_error(self, data_manager):
        """测试请求参数验证错误"""
        # 创建无效请求
        request = DataRequest(data_type='')  # 空的数据类型
        
        with pytest.raises(Exception):  # 应该抛出异常或通过错误处理器处理
            await data_manager.get_data(request)
    
    @pytest.mark.asyncio
    async def test_refresh_data(self, data_manager, sample_data):
        """测试强制刷新数据"""
        request = DataRequest(data_type='stock_basic')
        
        # 模拟数据源返回数据
        with patch.object(data_manager.source_manager, 'fetch_data', return_value=sample_data):
            # 模拟格式化器返回数据
            with patch.object(data_manager.formatter, 'format_data', return_value=sample_data):
                # 模拟缓存设置
                with patch.object(data_manager.cache_layer, 'set') as mock_set:
                    result = await data_manager.refresh_data(request)
                    
                    assert result.equals(sample_data)
                    # 验证数据被缓存
                    mock_set.assert_called_once()
    
    def test_build_cache_key(self, data_manager):
        """测试缓存键构建"""
        request = DataRequest(
            data_type='stock_basic',
            ts_code='000001.SZ',
            start_date='20230101'
        )
        
        cache_key = data_manager._build_cache_key(request)
        
        assert isinstance(cache_key, str)
        assert len(cache_key) > 0
        
        # 相同请求应该生成相同的缓存键
        cache_key2 = data_manager._build_cache_key(request)
        assert cache_key == cache_key2
    
    def test_validate_request_valid(self, data_manager):
        """测试有效请求验证"""
        request = DataRequest(
            data_type='stock_basic',
            ts_code='000001.SZ',
            start_date='20230101',
            end_date='20231231'
        )
        
        assert data_manager._validate_request(request) is True
    
    def test_validate_request_invalid(self, data_manager):
        """测试无效请求验证"""
        request = DataRequest(data_type='')  # 空的数据类型
        
        assert data_manager._validate_request(request) is False
    
    def test_clear_cache(self, data_manager):
        """测试清空缓存"""
        with patch.object(data_manager.cache_layer, 'clear') as mock_clear:
            data_manager.clear_cache()
            mock_clear.assert_called_once()
    
    def test_clear_expired_cache(self, data_manager):
        """测试清理过期缓存"""
        with patch.object(data_manager.cache_layer, 'clear_expired') as mock_clear_expired:
            data_manager.clear_expired_cache()
            mock_clear_expired.assert_called_once()
    
    def test_get_cache_stats(self, data_manager):
        """测试获取缓存统计"""
        mock_stats = {'memory_hits': 10, 'sqlite_hits': 5}
        
        with patch.object(data_manager.cache_layer, 'get_stats', return_value=mock_stats):
            stats = data_manager.get_cache_stats()
            assert stats == mock_stats
    
    @pytest.mark.asyncio
    async def test_get_data_with_disabled_cache(self, data_manager, sample_data):
        """测试禁用缓存时的数据获取"""
        # 禁用缓存
        data_manager.config.cache_enabled = False
        
        request = DataRequest(data_type='stock_basic')
        
        # 模拟数据源返回数据
        with patch.object(data_manager.source_manager, 'fetch_data', return_value=sample_data):
            # 模拟格式化器返回数据
            with patch.object(data_manager.formatter, 'format_data', return_value=sample_data):
                # 确保不会调用缓存
                with patch.object(data_manager.cache_layer, 'get') as mock_get:
                    with patch.object(data_manager.cache_layer, 'set') as mock_set:
                        result = await data_manager.get_data(request)
                        
                        assert result.equals(sample_data)
                        # 验证没有调用缓存
                        mock_get.assert_not_called()
                        mock_set.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_get_data_empty_result(self, data_manager):
        """测试获取空数据的情况"""
        request = DataRequest(data_type='stock_basic')
        empty_data = pd.DataFrame()
        
        # 模拟缓存未命中
        with patch.object(data_manager.cache_layer, 'get', return_value=None):
            # 模拟数据源返回空数据
            with patch.object(data_manager.source_manager, 'fetch_data', return_value=empty_data):
                # 模拟格式化器返回空数据
                with patch.object(data_manager.formatter, 'format_data', return_value=empty_data):
                    # 模拟缓存设置
                    with patch.object(data_manager.cache_layer, 'set') as mock_set:
                        result = await data_manager.get_data(request)
                        
                        assert result.empty
                        # 验证空数据不会被缓存
                        mock_set.assert_not_called()


class TestDataRequest:
    """测试数据请求模型"""
    
    def test_data_request_creation(self):
        """测试数据请求创建"""
        request = DataRequest(
            data_type='stock_basic',
            ts_code='000001.SZ',
            start_date='20230101',
            end_date='20231231'
        )
        
        assert request.data_type == 'stock_basic'
        assert request.ts_code == '000001.SZ'
        assert request.start_date == '20230101'
        assert request.end_date == '20231231'
    
    def test_to_cache_key(self):
        """测试缓存键生成"""
        request = DataRequest(
            data_type='stock_basic',
            ts_code='000001.SZ'
        )
        
        cache_key = request.to_cache_key()
        
        assert isinstance(cache_key, str)
        assert len(cache_key) == 32  # MD5哈希长度
        
        # 相同请求应该生成相同的缓存键
        cache_key2 = request.to_cache_key()
        assert cache_key == cache_key2
        
        # 不同请求应该生成不同的缓存键
        request2 = DataRequest(data_type='stock_daily', ts_code='000001.SZ')
        cache_key3 = request2.to_cache_key()
        assert cache_key != cache_key3
    
    def test_validate_valid_request(self):
        """测试有效请求验证"""
        request = DataRequest(
            data_type='stock_basic',
            ts_code='000001.SZ',
            start_date='20230101',
            end_date='20231231',
            freq='1d'
        )
        
        assert request.validate() is True
    
    def test_validate_empty_data_type(self):
        """测试空数据类型验证"""
        request = DataRequest(data_type='')
        
        with pytest.raises(ValidationError):
            request.validate()
    
    def test_validate_invalid_date_format(self):
        """测试无效日期格式验证"""
        request = DataRequest(
            data_type='stock_basic',
            start_date='invalid_date'
        )
        
        with pytest.raises(ValidationError):
            request.validate()
    
    def test_validate_invalid_date_range(self):
        """测试无效日期范围验证"""
        request = DataRequest(
            data_type='stock_basic',
            start_date='20231231',
            end_date='20230101'  # 结束日期早于开始日期
        )
        
        with pytest.raises(ValidationError):
            request.validate()
    
    def test_validate_invalid_frequency(self):
        """测试无效频率验证"""
        request = DataRequest(
            data_type='stock_basic',
            freq='invalid_freq'
        )
        
        with pytest.raises(ValidationError):
            request.validate()
    
    def test_is_valid_date(self):
        """测试日期格式验证"""
        request = DataRequest(data_type='test')
        
        # 有效的日期格式
        assert request._is_valid_date('20230101') is True
        assert request._is_valid_date('2023-01-01') is True
        
        # 无效的日期格式
        assert request._is_valid_date('2023/01/01') is False
        assert request._is_valid_date('invalid') is False
        assert request._is_valid_date('20230230') is False  # 不存在的日期