"""
向后兼容性测试

测试新的代码转换功能不会破坏现有代码的使用
"""

import pytest
import pandas as pd
from unittest.mock import Mock, patch

from quickstock import QuickStockClient
from quickstock.config import Config
from quickstock.core.errors import ValidationError


class TestBackwardCompatibility:
    """向后兼容性测试类"""
    
    def test_existing_standard_codes_still_work(self):
        """测试现有的标准格式代码仍然有效"""
        # 使用默认配置（启用自动转换）
        client = QuickStockClient()
        
        # 标准格式代码应该正常工作
        standard_codes = [
            "000001.SZ",
            "600000.SH",
            "300001.SZ",
            "688001.SH"
        ]
        
        for code in standard_codes:
            # 这些代码应该能够正常验证和标准化
            normalized = client._validate_and_normalize_code(code)
            assert normalized == code
    
    def test_disable_auto_conversion_backward_compatibility(self):
        """测试禁用自动转换时的向后兼容性"""
        # 禁用自动代码转换
        config = Config(enable_auto_code_conversion=False)
        client = QuickStockClient(config=config)
        
        # 标准格式代码应该仍然有效
        standard_codes = [
            "000001.SZ",
            "600000.SH",
            "300001.SZ"
        ]
        
        for code in standard_codes:
            normalized = client._validate_and_normalize_code(code)
            assert normalized == code
        
        # 非标准格式代码应该抛出异常
        non_standard_codes = [
            "sz.000001",
            "0.000001",
            "hs_000001",
            "000001"
        ]
        
        for code in non_standard_codes:
            with pytest.raises(ValidationError, match="请使用标准格式"):
                client._validate_and_normalize_code(code)
    
    def test_error_strategy_ignore_compatibility(self):
        """测试忽略错误策略的兼容性"""
        config = Config(code_conversion_error_strategy='ignore')
        client = QuickStockClient(config=config)
        
        # 有效代码应该正常转换
        assert client._validate_and_normalize_code("000001.SZ") == "000001.SZ"
        
        # 无效代码应该返回原始代码（不抛出异常）
        invalid_code = "INVALID_CODE"
        result = client._validate_and_normalize_code(invalid_code)
        assert result == invalid_code
    
    def test_error_strategy_lenient_compatibility(self):
        """测试宽松错误策略的兼容性"""
        config = Config(code_conversion_error_strategy='lenient')
        client = QuickStockClient(config=config)
        
        # 有效代码应该正常转换
        assert client._validate_and_normalize_code("000001.SZ") == "000001.SZ"
        
        # 标准格式的代码即使转换失败也应该返回原始代码
        with patch('quickstock.client.normalize_stock_code', side_effect=Exception("转换失败")):
            # 如果原始代码是有效的标准格式，应该返回原始代码
            result = client._validate_and_normalize_code("000001.SZ")
            assert result == "000001.SZ"
    
    def test_error_strategy_strict_compatibility(self):
        """测试严格错误策略的兼容性"""
        config = Config(code_conversion_error_strategy='strict')
        client = QuickStockClient(config=config)
        
        # 有效代码应该正常转换
        assert client._validate_and_normalize_code("000001.SZ") == "000001.SZ"
        
        # 无效代码应该抛出异常
        with pytest.raises(ValidationError):
            client._validate_and_normalize_code("INVALID_CODE")
    
    def test_logging_configuration_compatibility(self):
        """测试日志配置的兼容性"""
        # 启用代码转换日志
        config = Config(log_code_conversions=True)
        client = QuickStockClient(config=config)
        
        # 模拟日志记录
        with patch.object(client.logger, 'debug') as mock_debug:
            # 转换代码应该记录日志
            client._validate_and_normalize_code("sz.000001")
            
            # 验证日志被调用
            mock_debug.assert_called()
            
        # 禁用代码转换日志
        config = Config(log_code_conversions=False)
        client = QuickStockClient(config=config)
        
        with patch.object(client.logger, 'debug') as mock_debug:
            # 转换代码不应该记录调试日志
            client._validate_and_normalize_code("sz.000001")
            
            # 验证调试日志没有被调用（或调用次数较少）
            # 注意：可能还有其他调试日志，所以我们检查特定的转换日志
            debug_calls = [call for call in mock_debug.call_args_list 
                          if '标准化' in str(call)]
            assert len(debug_calls) == 0
    
    def test_config_update_compatibility(self):
        """测试配置更新的兼容性"""
        client = QuickStockClient()
        
        # 更新代码转换相关配置
        client.update_config(
            enable_auto_code_conversion=False,
            code_conversion_error_strategy='lenient'
        )
        
        # 验证配置已更新
        assert client.config.enable_auto_code_conversion is False
        assert client.config.code_conversion_error_strategy == 'lenient'
        
        # 验证更新后的行为
        with pytest.raises(ValidationError, match="请使用标准格式"):
            client._validate_and_normalize_code("sz.000001")
    
    def test_existing_api_methods_compatibility(self):
        """测试现有API方法的兼容性"""
        client = QuickStockClient()
        
        # 模拟数据管理器
        with patch.object(client.data_manager, 'get_data') as mock_get_data:
            mock_get_data.return_value = pd.DataFrame({
                'ts_code': ['000001.SZ'],
                'trade_date': ['20231201'],
                'close': [10.0]
            })
            
            # 测试现有的API方法仍然工作
            # 使用标准格式代码
            result = client.stock_daily('000001.SZ', start_date='20231201', end_date='20231201')
            assert not result.empty
            
            # 使用非标准格式代码（应该自动转换）
            result = client.stock_daily('sz.000001', start_date='20231201', end_date='20231201')
            assert not result.empty
    
    def test_code_converter_fallback_compatibility(self):
        """测试代码转换器回退兼容性"""
        client = QuickStockClient()
        
        # 模拟代码转换器不可用的情况
        with patch('quickstock.client.normalize_stock_code', side_effect=ImportError("模块不可用")):
            # 标准格式代码应该仍然有效
            result = client._validate_and_normalize_code("000001.SZ")
            assert result == "000001.SZ"
            
            # 非标准格式代码应该抛出异常
            with pytest.raises(ValidationError):
                client._validate_and_normalize_code("sz.000001")
    
    def test_gradual_feature_enablement(self):
        """测试渐进式功能启用"""
        # 开始时禁用所有新功能
        config = Config(
            enable_auto_code_conversion=False,
            strict_code_validation=True,
            enable_code_format_inference=False,
            enable_exchange_inference=False
        )
        client = QuickStockClient(config=config)
        
        # 只有标准格式代码应该工作
        assert client._validate_and_normalize_code("000001.SZ") == "000001.SZ"
        
        # 逐步启用功能
        client.update_config(enable_auto_code_conversion=True)
        
        # 现在应该支持自动转换
        assert client._validate_and_normalize_code("sz.000001") == "000001.SZ"
        
        # 进一步启用格式推断
        client.update_config(enable_code_format_inference=True)
        
        # 应该支持更多格式
        assert client._validate_and_normalize_code("000001") == "000001.SZ"
    
    def test_legacy_validation_function_compatibility(self):
        """测试旧版验证函数的兼容性"""
        from quickstock.utils.validators import validate_stock_code
        
        # 旧的验证函数应该仍然工作
        assert validate_stock_code("000001.SZ") is True
        assert validate_stock_code("600000.SH") is True
        assert validate_stock_code("invalid") is False
    
    def test_configuration_file_compatibility(self):
        """测试配置文件的兼容性"""
        # 创建一个只包含旧配置项的配置
        old_config_data = {
            'tushare_token': None,
            'cache_enabled': True,
            'request_timeout': 30
        }
        
        # 应该能够创建配置对象（新配置项使用默认值）
        config = Config(**old_config_data)
        
        # 验证新配置项有默认值
        assert config.enable_auto_code_conversion is True
        assert config.code_conversion_cache_size == 10000
        assert config.code_conversion_error_strategy == 'strict'
        
        # 验证旧配置项仍然有效
        assert config.tushare_token is None
        assert config.cache_enabled is True
        assert config.request_timeout == 30
    
    def test_client_initialization_compatibility(self):
        """测试客户端初始化的兼容性"""
        # 不传入配置应该使用默认配置
        client1 = QuickStockClient()
        assert client1.config is not None
        assert client1.config.enable_auto_code_conversion is True
        
        # 传入旧版本的配置应该仍然工作
        old_config = Config(tushare_token=None, cache_enabled=True)
        client2 = QuickStockClient(config=old_config)
        assert client2.config.tushare_token is None
        assert client2.config.cache_enabled is True
        assert client2.config.enable_auto_code_conversion is True  # 新功能默认启用
    
    def test_error_message_compatibility(self):
        """测试错误消息的兼容性"""
        client = QuickStockClient()
        
        # 空代码应该有清晰的错误消息
        with pytest.raises(ValidationError, match="股票代码不能为空"):
            client._validate_and_normalize_code("")
        
        # 无效代码应该有有用的错误消息
        with pytest.raises(ValidationError, match="验证失败"):
            client._validate_and_normalize_code("INVALID_CODE")
    
    def test_performance_compatibility(self):
        """测试性能兼容性"""
        client = QuickStockClient()
        
        # 标准格式代码的处理应该很快
        import time
        
        start_time = time.time()
        for _ in range(100):
            client._validate_and_normalize_code("000001.SZ")
        end_time = time.time()
        
        # 100次验证应该在合理时间内完成（比如1秒）
        assert (end_time - start_time) < 1.0
        
        # 启用缓存后，重复验证应该更快
        config = Config(enable_code_conversion_cache=True)
        client_with_cache = QuickStockClient(config=config)
        
        start_time = time.time()
        for _ in range(100):
            client_with_cache._validate_and_normalize_code("sz.000001")
        end_time = time.time()
        
        # 有缓存的情况下应该更快
        assert (end_time - start_time) < 1.0