"""
配置管理系统的单元测试
"""

import os
import json
import yaml
import tempfile
import pytest
from pathlib import Path

from quickstock.config import Config
from quickstock.core.errors import ValidationError


class TestConfig:
    """配置类测试"""
    
    def test_default_config(self):
        """测试默认配置"""
        config = Config()
        
        # 验证默认值
        assert config.cache_enabled is True
        assert config.cache_expire_hours == 24
        assert config.memory_cache_size == 1000
        assert config.request_timeout == 30
        assert config.max_retries == 3
        assert config.retry_delay == 1.0
        assert config.date_format == "%Y%m%d"
        assert config.float_precision == 4
        assert config.log_level == "INFO"
        
        # 验证数据源优先级
        assert 'stock_basic' in config.data_source_priority
        assert 'tushare' in config.data_source_priority['stock_basic']
    
    def test_config_validation(self):
        """测试配置验证"""
        # 测试无效的缓存过期时间
        with pytest.raises(ValidationError, match="cache_expire_hours必须大于0"):
            Config(cache_expire_hours=0)
        
        # 测试无效的内存缓存大小
        with pytest.raises(ValidationError, match="memory_cache_size必须大于0"):
            Config(memory_cache_size=-1)
        
        # 测试无效的请求超时时间
        with pytest.raises(ValidationError, match="request_timeout必须大于0"):
            Config(request_timeout=0)
        
        # 测试无效的重试次数
        with pytest.raises(ValidationError, match="max_retries不能小于0"):
            Config(max_retries=-1)
        
        # 测试无效的重试延迟
        with pytest.raises(ValidationError, match="retry_delay不能小于0"):
            Config(retry_delay=-1)
        
        # 测试无效的浮点精度
        with pytest.raises(ValidationError, match="float_precision不能小于0"):
            Config(float_precision=-1)
        
        # 测试无效的日志级别
        with pytest.raises(ValidationError, match="log_level必须是以下之一"):
            Config(log_level="INVALID")
    
    def test_path_expansion(self):
        """测试路径展开"""
        config = Config(
            sqlite_db_path="~/test.db",
            log_file="~/test.log"
        )
        
        # 验证路径已展开
        assert not config.sqlite_db_path.startswith('~')
        assert not config.log_file.startswith('~')
        assert config.sqlite_db_path.startswith(os.path.expanduser('~'))
        assert config.log_file.startswith(os.path.expanduser('~'))
    
    def test_from_json_file(self):
        """测试从JSON文件加载配置"""
        config_data = {
            "tushare_token": "test_token",
            "cache_enabled": False,
            "cache_expire_hours": 48,
            "memory_cache_size": 2000,
            "request_timeout": 60,
            "log_level": "DEBUG"
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            temp_path = f.name
        
        try:
            config = Config.from_file(temp_path)
            
            assert config.tushare_token == "test_token"
            assert config.cache_enabled is False
            assert config.cache_expire_hours == 48
            assert config.memory_cache_size == 2000
            assert config.request_timeout == 60
            assert config.log_level == "DEBUG"
        finally:
            os.unlink(temp_path)
    
    def test_from_yaml_file(self):
        """测试从YAML文件加载配置"""
        config_data = {
            "tushare_token": "test_token",
            "cache_enabled": False,
            "cache_expire_hours": 48,
            "memory_cache_size": 2000,
            "request_timeout": 60,
            "log_level": "DEBUG"
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config_data, f)
            temp_path = f.name
        
        try:
            config = Config.from_file(temp_path)
            
            assert config.tushare_token == "test_token"
            assert config.cache_enabled is False
            assert config.cache_expire_hours == 48
            assert config.memory_cache_size == 2000
            assert config.request_timeout == 60
            assert config.log_level == "DEBUG"
        finally:
            os.unlink(temp_path)
    
    def test_from_file_not_found(self):
        """测试加载不存在的配置文件"""
        with pytest.raises(FileNotFoundError, match="配置文件不存在"):
            Config.from_file("/nonexistent/config.json")
    
    def test_from_file_invalid_json(self):
        """测试加载无效的JSON配置文件"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("invalid json content")
            temp_path = f.name
        
        try:
            with pytest.raises(ValidationError, match="配置文件格式错误"):
                Config.from_file(temp_path)
        finally:
            os.unlink(temp_path)
    
    def test_from_file_invalid_config(self):
        """测试加载包含无效配置的文件"""
        config_data = {
            "cache_expire_hours": -1  # 无效值
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            temp_path = f.name
        
        try:
            with pytest.raises(ValidationError, match="cache_expire_hours必须大于0"):
                Config.from_file(temp_path)
        finally:
            os.unlink(temp_path)
    
    def test_to_json_file(self):
        """测试保存配置到JSON文件"""
        config = Config(
            tushare_token="test_token",
            cache_enabled=False,
            cache_expire_hours=48
        )
        
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            temp_path = f.name
        
        try:
            config.to_file(temp_path, 'json')
            
            # 验证文件内容
            with open(temp_path, 'r') as f:
                saved_data = json.load(f)
            
            assert saved_data['tushare_token'] == "test_token"
            assert saved_data['cache_enabled'] is False
            assert saved_data['cache_expire_hours'] == 48
        finally:
            os.unlink(temp_path)
    
    def test_to_yaml_file(self):
        """测试保存配置到YAML文件"""
        config = Config(
            tushare_token="test_token",
            cache_enabled=False,
            cache_expire_hours=48
        )
        
        with tempfile.NamedTemporaryFile(suffix='.yaml', delete=False) as f:
            temp_path = f.name
        
        try:
            config.to_file(temp_path, 'yaml')
            
            # 验证文件内容
            with open(temp_path, 'r') as f:
                saved_data = yaml.safe_load(f)
            
            assert saved_data['tushare_token'] == "test_token"
            assert saved_data['cache_enabled'] is False
            assert saved_data['cache_expire_hours'] == 48
        finally:
            os.unlink(temp_path)
    
    def test_to_file_auto_format(self):
        """测试自动格式检测保存"""
        config = Config(tushare_token="test_token")
        
        # 测试JSON格式自动检测
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            temp_path = f.name
        
        try:
            config.to_file(temp_path, 'auto')
            
            with open(temp_path, 'r') as f:
                saved_data = json.load(f)
            assert saved_data['tushare_token'] == "test_token"
        finally:
            os.unlink(temp_path)
        
        # 测试YAML格式自动检测
        with tempfile.NamedTemporaryFile(suffix='.yaml', delete=False) as f:
            temp_path = f.name
        
        try:
            config.to_file(temp_path, 'auto')
            
            with open(temp_path, 'r') as f:
                saved_data = yaml.safe_load(f)
            assert saved_data['tushare_token'] == "test_token"
        finally:
            os.unlink(temp_path)
    
    def test_update_config(self):
        """测试配置更新"""
        config = Config()
        
        # 更新有效配置
        config.update(
            cache_enabled=False,
            cache_expire_hours=48,
            log_level="DEBUG"
        )
        
        assert config.cache_enabled is False
        assert config.cache_expire_hours == 48
        assert config.log_level == "DEBUG"
        
        # 更新无效配置参数
        with pytest.raises(ValidationError, match="未知的配置参数"):
            config.update(invalid_param="value")
        
        # 更新无效配置值
        with pytest.raises(ValidationError, match="cache_expire_hours必须大于0"):
            config.update(cache_expire_hours=-1)
    
    def test_data_source_priority(self):
        """测试数据源优先级管理"""
        config = Config()
        
        # 获取数据源优先级
        priority = config.get_data_source_priority('stock_basic')
        assert 'tushare' in priority
        
        # 设置数据源优先级
        config.set_data_source_priority('test_type', ['source1', 'source2'])
        assert config.get_data_source_priority('test_type') == ['source1', 'source2']
        
        # 获取不存在的数据类型
        assert config.get_data_source_priority('nonexistent') == []
    
    def test_to_dict(self):
        """测试转换为字典"""
        config = Config(tushare_token="test_token")
        config_dict = config.to_dict()
        
        assert isinstance(config_dict, dict)
        assert config_dict['tushare_token'] == "test_token"
        assert 'cache_enabled' in config_dict
    
    def test_string_representation(self):
        """测试字符串表示"""
        config = Config(tushare_token="test_token")
        str_repr = str(config)
        
        assert "Config(" in str_repr
        assert "***" in str_repr  # token应该被隐藏
        assert "cache_enabled=True" in str_repr
    
    def test_load_default(self):
        """测试加载默认配置"""
        # 如果默认配置文件不存在，应该返回默认配置
        config = Config.load_default()
        assert isinstance(config, Config)
        assert config.cache_enabled is True
    
    def test_get_default_config_path(self):
        """测试获取默认配置路径"""
        path = Config.get_default_config_path()
        assert path.endswith('.quickstock/config.yaml')
        assert not path.startswith('~')  # 应该已经展开