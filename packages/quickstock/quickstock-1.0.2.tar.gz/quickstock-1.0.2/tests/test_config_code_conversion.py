"""
代码转换配置测试

测试Config类中新增的代码转换配置选项
"""

import pytest
import tempfile
import os
from quickstock.config import Config
from quickstock.core.errors import ValidationError


class TestCodeConversionConfig:
    """代码转换配置测试类"""
    
    def test_default_code_conversion_config(self):
        """测试默认代码转换配置"""
        config = Config()
        
        # 验证默认值
        assert config.enable_auto_code_conversion is True
        assert config.strict_code_validation is False
        assert config.code_conversion_cache_size == 10000
        assert config.log_code_conversions is False
        assert config.code_conversion_timeout == 1.0
        assert config.enable_code_format_inference is True
        assert config.enable_exchange_inference is True
        assert config.code_conversion_batch_size == 1000
        assert config.enable_code_conversion_cache is True
        assert config.code_conversion_error_strategy == "strict"
    
    def test_code_conversion_config_validation(self):
        """测试代码转换配置验证"""
        # 测试无效的缓存大小
        with pytest.raises(ValidationError, match="code_conversion_cache_size必须大于0"):
            Config(code_conversion_cache_size=0)
        
        with pytest.raises(ValidationError, match="code_conversion_cache_size必须大于0"):
            Config(code_conversion_cache_size=-1)
        
        # 测试无效的超时时间
        with pytest.raises(ValidationError, match="code_conversion_timeout必须大于0"):
            Config(code_conversion_timeout=0)
        
        with pytest.raises(ValidationError, match="code_conversion_timeout必须大于0"):
            Config(code_conversion_timeout=-1)
        
        # 测试无效的批次大小
        with pytest.raises(ValidationError, match="code_conversion_batch_size必须大于0"):
            Config(code_conversion_batch_size=0)
        
        with pytest.raises(ValidationError, match="code_conversion_batch_size必须大于0"):
            Config(code_conversion_batch_size=-1)
        
        # 测试无效的错误策略
        with pytest.raises(ValidationError, match="code_conversion_error_strategy必须是以下之一"):
            Config(code_conversion_error_strategy="invalid")
    
    def test_valid_code_conversion_config(self):
        """测试有效的代码转换配置"""
        config = Config(
            enable_auto_code_conversion=False,
            strict_code_validation=True,
            code_conversion_cache_size=5000,
            log_code_conversions=True,
            code_conversion_timeout=2.0,
            enable_code_format_inference=False,
            enable_exchange_inference=False,
            code_conversion_batch_size=500,
            enable_code_conversion_cache=False,
            code_conversion_error_strategy="lenient"
        )
        
        assert config.enable_auto_code_conversion is False
        assert config.strict_code_validation is True
        assert config.code_conversion_cache_size == 5000
        assert config.log_code_conversions is True
        assert config.code_conversion_timeout == 2.0
        assert config.enable_code_format_inference is False
        assert config.enable_exchange_inference is False
        assert config.code_conversion_batch_size == 500
        assert config.enable_code_conversion_cache is False
        assert config.code_conversion_error_strategy == "lenient"
    
    def test_enable_code_conversion_method(self):
        """测试启用代码转换方法"""
        config = Config()
        
        # 测试启用
        config.enable_code_conversion(True)
        assert config.enable_auto_code_conversion is True
        
        # 测试禁用
        config.enable_code_conversion(False)
        assert config.enable_auto_code_conversion is False
        
        # 测试默认参数
        config.enable_code_conversion()
        assert config.enable_auto_code_conversion is True
    
    def test_set_code_conversion_cache_size_method(self):
        """测试设置代码转换缓存大小方法"""
        config = Config()
        
        # 测试有效值
        config.set_code_conversion_cache_size(5000)
        assert config.code_conversion_cache_size == 5000
        
        # 测试无效值
        with pytest.raises(ValidationError, match="代码转换缓存大小必须大于0"):
            config.set_code_conversion_cache_size(0)
        
        with pytest.raises(ValidationError, match="代码转换缓存大小必须大于0"):
            config.set_code_conversion_cache_size(-1)
    
    def test_set_code_conversion_error_strategy_method(self):
        """测试设置代码转换错误策略方法"""
        config = Config()
        
        # 测试有效策略
        for strategy in ['strict', 'lenient', 'ignore']:
            config.set_code_conversion_error_strategy(strategy)
            assert config.code_conversion_error_strategy == strategy
        
        # 测试无效策略
        with pytest.raises(ValidationError, match="错误处理策略必须是以下之一"):
            config.set_code_conversion_error_strategy("invalid")
    
    def test_get_code_conversion_config_method(self):
        """测试获取代码转换配置方法"""
        config = Config(
            enable_auto_code_conversion=False,
            strict_code_validation=True,
            code_conversion_cache_size=5000,
            log_code_conversions=True,
            code_conversion_timeout=2.0,
            enable_code_format_inference=False,
            enable_exchange_inference=False,
            code_conversion_batch_size=500,
            enable_code_conversion_cache=False,
            code_conversion_error_strategy="lenient"
        )
        
        conversion_config = config.get_code_conversion_config()
        
        expected_config = {
            'enable_auto_code_conversion': False,
            'strict_code_validation': True,
            'code_conversion_cache_size': 5000,
            'log_code_conversions': True,
            'code_conversion_timeout': 2.0,
            'enable_code_format_inference': False,
            'enable_exchange_inference': False,
            'code_conversion_batch_size': 500,
            'enable_code_conversion_cache': False,
            'code_conversion_error_strategy': 'lenient'
        }
        
        assert conversion_config == expected_config
    
    def test_config_file_with_code_conversion_options(self):
        """测试包含代码转换选项的配置文件"""
        config_data = {
            'enable_auto_code_conversion': False,
            'strict_code_validation': True,
            'code_conversion_cache_size': 5000,
            'log_code_conversions': True,
            'code_conversion_timeout': 2.0,
            'enable_code_format_inference': False,
            'enable_exchange_inference': False,
            'code_conversion_batch_size': 500,
            'enable_code_conversion_cache': False,
            'code_conversion_error_strategy': 'lenient'
        }
        
        # 测试YAML格式
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            import yaml
            yaml.dump(config_data, f)
            yaml_path = f.name
        
        try:
            config = Config.from_file(yaml_path)
            assert config.enable_auto_code_conversion is False
            assert config.strict_code_validation is True
            assert config.code_conversion_cache_size == 5000
            assert config.log_code_conversions is True
            assert config.code_conversion_timeout == 2.0
            assert config.enable_code_format_inference is False
            assert config.enable_exchange_inference is False
            assert config.code_conversion_batch_size == 500
            assert config.enable_code_conversion_cache is False
            assert config.code_conversion_error_strategy == 'lenient'
        finally:
            os.unlink(yaml_path)
        
        # 测试JSON格式
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            import json
            json.dump(config_data, f)
            json_path = f.name
        
        try:
            config = Config.from_file(json_path)
            assert config.enable_auto_code_conversion is False
            assert config.strict_code_validation is True
            assert config.code_conversion_cache_size == 5000
            assert config.log_code_conversions is True
            assert config.code_conversion_timeout == 2.0
            assert config.enable_code_format_inference is False
            assert config.enable_exchange_inference is False
            assert config.code_conversion_batch_size == 500
            assert config.enable_code_conversion_cache is False
            assert config.code_conversion_error_strategy == 'lenient'
        finally:
            os.unlink(json_path)
    
    def test_config_update_with_code_conversion_options(self):
        """测试使用代码转换选项更新配置"""
        config = Config()
        
        # 更新代码转换配置
        config.update(
            enable_auto_code_conversion=False,
            strict_code_validation=True,
            code_conversion_cache_size=5000,
            code_conversion_error_strategy='lenient'
        )
        
        assert config.enable_auto_code_conversion is False
        assert config.strict_code_validation is True
        assert config.code_conversion_cache_size == 5000
        assert config.code_conversion_error_strategy == 'lenient'
        
        # 测试无效的缓存大小更新
        with pytest.raises(ValidationError, match="code_conversion_cache_size必须大于0"):
            config.update(code_conversion_cache_size=0)
        
        # 测试无效的错误策略更新（使用新的配置对象避免状态污染）
        config2 = Config()
        with pytest.raises(ValidationError, match="code_conversion_error_strategy必须是以下之一"):
            config2.update(code_conversion_error_strategy='invalid')
    
    def test_config_to_dict_includes_code_conversion(self):
        """测试配置转字典包含代码转换选项"""
        config = Config()
        config_dict = config.to_dict()
        
        # 验证代码转换配置项存在
        assert 'enable_auto_code_conversion' in config_dict
        assert 'strict_code_validation' in config_dict
        assert 'code_conversion_cache_size' in config_dict
        assert 'log_code_conversions' in config_dict
        assert 'code_conversion_timeout' in config_dict
        assert 'enable_code_format_inference' in config_dict
        assert 'enable_exchange_inference' in config_dict
        assert 'code_conversion_batch_size' in config_dict
        assert 'enable_code_conversion_cache' in config_dict
        assert 'code_conversion_error_strategy' in config_dict
        
        # 验证默认值
        assert config_dict['enable_auto_code_conversion'] is True
        assert config_dict['strict_code_validation'] is False
        assert config_dict['code_conversion_cache_size'] == 10000
        assert config_dict['log_code_conversions'] is False
        assert config_dict['code_conversion_timeout'] == 1.0
        assert config_dict['enable_code_format_inference'] is True
        assert config_dict['enable_exchange_inference'] is True
        assert config_dict['code_conversion_batch_size'] == 1000
        assert config_dict['enable_code_conversion_cache'] is True
        assert config_dict['code_conversion_error_strategy'] == 'strict'