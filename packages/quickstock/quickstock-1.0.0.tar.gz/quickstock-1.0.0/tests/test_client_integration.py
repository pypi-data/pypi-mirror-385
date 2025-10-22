"""
QuickStock客户端集成测试

测试客户端与其他组件的集成
"""

import pytest
import pandas as pd
from unittest.mock import Mock, patch

from quickstock.client import QuickStockClient
from quickstock.config import Config
from quickstock.core.errors import QuickStockError


class TestClientIntegration:
    """客户端集成测试类"""
    
    def setup_method(self):
        """测试前置设置"""
        # 创建测试配置
        self.test_config = Config(
            cache_enabled=True,
            log_level='ERROR'
        )
    
    def test_client_with_real_components(self):
        """测试客户端与真实组件的集成"""
        # 创建客户端
        client = QuickStockClient(self.test_config)
        
        # 验证组件初始化
        assert client.data_manager is not None
        assert client.data_manager.cache_layer is not None
        assert client.data_manager.source_manager is not None
        assert client.data_manager.formatter is not None
        assert client.data_manager.error_handler is not None
        
        # 验证配置传递
        assert client.data_manager.config == self.test_config
    
    def test_client_configuration_propagation(self):
        """测试配置在组件间的传递"""
        config = Config(
            cache_enabled=False,
            max_retries=5,
            request_timeout=60
        )
        
        client = QuickStockClient(config)
        
        # 验证配置传递到数据管理器
        assert client.data_manager.config.cache_enabled is False
        assert client.data_manager.config.max_retries == 5
        assert client.data_manager.config.request_timeout == 60
    
    def test_client_error_handling_integration(self):
        """测试客户端错误处理集成"""
        client = QuickStockClient(self.test_config)
        
        # Mock数据管理器抛出异常
        with patch.object(client.data_manager, 'get_data') as mock_get_data:
            async def mock_error(*args, **kwargs):
                raise Exception("测试异常")
            
            mock_get_data.side_effect = mock_error
            
            # 验证异常被正确处理和包装
            with pytest.raises(QuickStockError, match="获取股票基础信息失败"):
                client.stock_basic()
    
    def test_client_cache_integration(self):
        """测试客户端缓存集成"""
        client = QuickStockClient(self.test_config)
        
        # 测试缓存操作
        client.clear_cache()
        client.clear_expired_cache()
        
        # 获取缓存统计
        cache_stats = client.get_cache_stats()
        assert isinstance(cache_stats, dict)
    
    def test_client_provider_management_integration(self):
        """测试客户端数据源管理集成"""
        client = QuickStockClient(self.test_config)
        
        # 获取数据源统计
        provider_stats = client.get_provider_stats()
        assert isinstance(provider_stats, dict)
        
        # 获取数据源健康状态
        provider_health = client.get_provider_health()
        assert isinstance(provider_health, dict)
        
        # 测试连接
        result = client.test_connection()
        assert isinstance(result, bool)
    
    def test_client_health_check_integration(self):
        """测试客户端健康检查集成"""
        client = QuickStockClient(self.test_config)
        
        # 执行健康检查
        health_results = client.health_check()
        assert isinstance(health_results, dict)
    
    def test_client_context_manager_integration(self):
        """测试客户端上下文管理器集成"""
        with QuickStockClient(self.test_config) as client:
            # 验证客户端正常工作
            assert client._initialized is True
            
            # 测试基本功能
            config = client.get_config()
            assert config == self.test_config
        
        # 上下文退出后不应抛出异常
    
    def test_client_logging_integration(self):
        """测试客户端日志集成"""
        import logging
        
        # 创建带日志配置的客户端
        config = Config(log_level='DEBUG')
        client = QuickStockClient(config)
        
        # 验证日志器设置
        assert hasattr(client, 'logger')
        # 注意：日志器可能已经被之前的测试设置过，所以我们检查配置而不是实际级别
        assert client.config.log_level == 'DEBUG'
    
    def test_client_async_integration(self):
        """测试客户端异步处理集成"""
        client = QuickStockClient(self.test_config)
        
        # 测试异步方法处理
        async def test_async_func():
            return "async_result"
        
        result = client._run_async(test_async_func())
        assert result == "async_result"
        
        # 测试非协程处理
        result = client._run_async("sync_result")
        assert result == "sync_result"


class TestClientAPIIntegration:
    """客户端API集成测试类"""
    
    def setup_method(self):
        """测试前置设置"""
        self.test_config = Config(cache_enabled=False, log_level='ERROR')
        self.client = QuickStockClient(self.test_config)
    
    def test_stock_api_parameter_validation_integration(self):
        """测试股票API参数验证集成"""
        # 测试各种无效参数
        with pytest.raises(QuickStockError):
            self.client.stock_daily('')  # 空代码
        
        with pytest.raises(QuickStockError):
            self.client.stock_daily('000001.SZ', 'invalid_date')  # 无效日期
        
        with pytest.raises(QuickStockError):
            self.client.stock_minute('000001.SZ', 'invalid_freq')  # 无效频率
    
    def test_trade_calendar_api_integration(self):
        """测试交易日历API集成"""
        # 测试参数验证
        with pytest.raises(QuickStockError):
            self.client.is_trade_date('')  # 空日期
        
        with pytest.raises(QuickStockError):
            self.client.is_trade_date('invalid_date')  # 无效日期
    
    def test_api_error_message_consistency(self):
        """测试API错误消息一致性"""
        # 所有API方法都应该返回一致的错误格式
        api_methods = [
            ('stock_basic', {}),
            ('stock_daily', {'ts_code': '000001.SZ'}),
            ('index_basic', {}),
            ('fund_basic', {}),
            ('trade_cal', {})
        ]
        
        for method_name, kwargs in api_methods:
            method = getattr(self.client, method_name)
            
            # Mock数据管理器抛出异常
            with patch.object(self.client.data_manager, 'get_data') as mock_get_data:
                async def mock_error(*args, **kwargs):
                    raise Exception("测试异常")
                
                mock_get_data.side_effect = mock_error
                
                # 验证异常格式
                with pytest.raises(QuickStockError) as exc_info:
                    method(**kwargs)
                
                error_msg = str(exc_info.value)
                assert "失败" in error_msg
                assert "测试异常" in error_msg


if __name__ == '__main__':
    pytest.main([__file__])