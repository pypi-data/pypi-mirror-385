"""
配置管理系统

提供SDK的配置管理功能，支持配置文件加载、保存、验证等
"""

import os
import json
import yaml
from dataclasses import dataclass, field, asdict
from typing import Optional, Dict, Any
from pathlib import Path

from .core.errors import ValidationError


@dataclass
class Config:
    """SDK配置类"""
    
    # 数据源配置
    tushare_token: Optional[str] = None
    enable_baostock: bool = True
    enable_eastmoney: bool = True
    enable_tonghuashun: bool = True
    
    # 缓存配置
    cache_enabled: bool = True
    cache_expire_hours: int = 24
    memory_cache_size: int = 1000
    sqlite_db_path: str = "~/.quickstock/cache.db"
    
    # 网络配置
    request_timeout: int = 30
    max_retries: int = 3
    retry_delay: float = 1.0
    max_concurrent_requests: int = 10  # 最大并发请求数
    
    # 连接池配置
    connection_pool_size: int = 100  # 连接池总大小
    connection_pool_per_host: int = 30  # 每个主机的连接数
    connection_keepalive_timeout: int = 30  # 连接保持时间
    connection_cleanup_enabled: bool = True  # 启用连接清理
    
    # 数据格式配置
    date_format: str = "%Y%m%d"
    float_precision: int = 4
    
    # 内存优化配置
    stream_chunk_size: int = 10000
    memory_limit_mb: float = 500.0
    memory_batch_size: int = 50
    aggressive_memory_optimization: bool = False
    
    # 日志配置
    log_level: str = "INFO"
    log_file: Optional[str] = "~/.quickstock/quickstock.log"
    
    # 股票代码转换配置
    enable_auto_code_conversion: bool = True
    strict_code_validation: bool = False
    code_conversion_cache_size: int = 10000
    log_code_conversions: bool = False
    code_conversion_timeout: float = 1.0  # 代码转换超时时间（秒）
    enable_code_format_inference: bool = True  # 启用代码格式自动推断
    enable_exchange_inference: bool = True  # 启用交易所自动推断
    code_conversion_batch_size: int = 1000  # 批量转换的批次大小
    enable_code_conversion_cache: bool = True  # 启用代码转换缓存
    code_conversion_error_strategy: str = "strict"  # 错误处理策略: strict, lenient, ignore
    
    # 数据源优先级配置
    data_source_priority: Dict[str, list] = field(default_factory=lambda: {
        'stock_basic': ['tushare', 'baostock'],
        'stock_daily': ['tushare', 'eastmoney', 'baostock'],
        'stock_minute': ['eastmoney', 'tonghuashun'],
        'index_basic': ['tushare', 'baostock'],
        'index_daily': ['tushare', 'baostock'],
        'fund_basic': ['tushare'],
        'fund_nav': ['tushare'],
        'trade_cal': ['tushare', 'baostock'],
        'concept': ['tonghuashun']
    })
    
    def __post_init__(self):
        """初始化后的验证和处理"""
        self._expand_paths()
        self._validate_config()
    
    def _expand_paths(self):
        """展开路径中的~符号"""
        if self.sqlite_db_path.startswith('~'):
            self.sqlite_db_path = os.path.expanduser(self.sqlite_db_path)
        if self.log_file and self.log_file.startswith('~'):
            self.log_file = os.path.expanduser(self.log_file)
    
    def _validate_config(self):
        """验证配置参数"""
        # 验证缓存配置
        if self.cache_expire_hours <= 0:
            raise ValidationError("cache_expire_hours必须大于0")
        
        if self.memory_cache_size <= 0:
            raise ValidationError("memory_cache_size必须大于0")
        
        # 验证网络配置
        if self.request_timeout <= 0:
            raise ValidationError("request_timeout必须大于0")
        
        if self.max_retries < 0:
            raise ValidationError("max_retries不能小于0")
        
        if self.retry_delay < 0:
            raise ValidationError("retry_delay不能小于0")
        
        if self.max_concurrent_requests <= 0:
            raise ValidationError("max_concurrent_requests必须大于0")
        
        # 验证连接池配置
        if self.connection_pool_size <= 0:
            raise ValidationError("connection_pool_size必须大于0")
        
        if self.connection_pool_per_host <= 0:
            raise ValidationError("connection_pool_per_host必须大于0")
        
        if self.connection_keepalive_timeout <= 0:
            raise ValidationError("connection_keepalive_timeout必须大于0")
        
        # 验证数据格式配置
        if self.float_precision < 0:
            raise ValidationError("float_precision不能小于0")
        
        # 验证日志级别
        valid_log_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if self.log_level.upper() not in valid_log_levels:
            raise ValidationError(f"log_level必须是以下之一: {valid_log_levels}")
        
        # 验证数据源优先级配置
        if not isinstance(self.data_source_priority, dict):
            raise ValidationError("data_source_priority必须是字典类型")
        
        # 验证内存优化配置
        if self.stream_chunk_size <= 0:
            raise ValidationError("stream_chunk_size必须大于0")
        
        if self.memory_limit_mb <= 0:
            raise ValidationError("memory_limit_mb必须大于0")
        
        if self.memory_batch_size <= 0:
            raise ValidationError("memory_batch_size必须大于0")
        
        # 验证代码转换配置
        if self.code_conversion_cache_size <= 0:
            raise ValidationError("code_conversion_cache_size必须大于0")
        
        if self.code_conversion_timeout <= 0:
            raise ValidationError("code_conversion_timeout必须大于0")
        
        if self.code_conversion_batch_size <= 0:
            raise ValidationError("code_conversion_batch_size必须大于0")
        
        valid_error_strategies = ['strict', 'lenient', 'ignore']
        if self.code_conversion_error_strategy not in valid_error_strategies:
            raise ValidationError(f"code_conversion_error_strategy必须是以下之一: {valid_error_strategies}")
    
    @classmethod
    def from_file(cls, config_path: str) -> 'Config':
        """
        从配置文件加载配置
        
        Args:
            config_path: 配置文件路径，支持JSON和YAML格式
            
        Returns:
            配置对象
            
        Raises:
            FileNotFoundError: 配置文件不存在
            ValidationError: 配置文件格式错误或内容无效
        """
        config_path = os.path.expanduser(config_path)
        
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"配置文件不存在: {config_path}")
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                if config_path.endswith('.json'):
                    config_data = json.load(f)
                elif config_path.endswith(('.yaml', '.yml')):
                    config_data = yaml.safe_load(f)
                else:
                    # 尝试JSON格式
                    try:
                        f.seek(0)
                        config_data = json.load(f)
                    except json.JSONDecodeError:
                        # 尝试YAML格式
                        f.seek(0)
                        config_data = yaml.safe_load(f)
            
            # 创建配置对象
            return cls(**config_data)
            
        except (json.JSONDecodeError, yaml.YAMLError) as e:
            raise ValidationError(f"配置文件格式错误: {e}")
        except TypeError as e:
            raise ValidationError(f"配置参数错误: {e}")
    
    def to_file(self, config_path: str, format: str = 'auto'):
        """
        保存配置到文件
        
        Args:
            config_path: 配置文件路径
            format: 文件格式 ('json', 'yaml', 'auto')
                   'auto'会根据文件扩展名自动判断
        
        Raises:
            ValidationError: 格式参数无效
        """
        config_path = os.path.expanduser(config_path)
        
        # 确保目录存在
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        
        # 确定文件格式
        if format == 'auto':
            if config_path.endswith('.json'):
                format = 'json'
            elif config_path.endswith(('.yaml', '.yml')):
                format = 'yaml'
            else:
                format = 'json'  # 默认使用JSON
        
        if format not in ['json', 'yaml']:
            raise ValidationError(f"不支持的文件格式: {format}")
        
        # 转换为字典
        config_dict = asdict(self)
        
        # 保存文件
        with open(config_path, 'w', encoding='utf-8') as f:
            if format == 'json':
                json.dump(config_dict, f, indent=2, ensure_ascii=False)
            else:  # yaml
                yaml.dump(config_dict, f, default_flow_style=False, 
                         allow_unicode=True, indent=2)
    
    @classmethod
    def get_default_config_path(cls) -> str:
        """
        获取默认配置文件路径
        
        Returns:
            默认配置文件路径
        """
        return os.path.expanduser("~/.quickstock/config.yaml")
    
    @classmethod
    def load_default(cls) -> 'Config':
        """
        加载默认配置
        如果默认配置文件存在则加载，否则返回默认配置对象
        
        Returns:
            配置对象
        """
        default_path = cls.get_default_config_path()
        if os.path.exists(default_path):
            return cls.from_file(default_path)
        else:
            return cls()
    
    def save_as_default(self):
        """将当前配置保存为默认配置"""
        self.to_file(self.get_default_config_path(), 'yaml')
    
    def update(self, **kwargs):
        """
        更新配置参数
        
        Args:
            **kwargs: 要更新的配置参数
        """
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                raise ValidationError(f"未知的配置参数: {key}")
        
        # 重新验证配置
        self._validate_config()
    
    def get_data_source_priority(self, data_type: str) -> list:
        """
        获取指定数据类型的数据源优先级
        
        Args:
            data_type: 数据类型
            
        Returns:
            数据源优先级列表
        """
        return self.data_source_priority.get(data_type, [])
    
    def set_data_source_priority(self, data_type: str, priority_list: list):
        """
        设置指定数据类型的数据源优先级
        
        Args:
            data_type: 数据类型
            priority_list: 数据源优先级列表
        """
        self.data_source_priority[data_type] = priority_list
    
    def enable_code_conversion(self, enable: bool = True):
        """
        启用或禁用自动代码转换
        
        Args:
            enable: 是否启用自动代码转换
        """
        self.enable_auto_code_conversion = enable
    
    def set_code_conversion_cache_size(self, size: int):
        """
        设置代码转换缓存大小
        
        Args:
            size: 缓存大小
        """
        if size <= 0:
            raise ValidationError("代码转换缓存大小必须大于0")
        self.code_conversion_cache_size = size
    
    def set_code_conversion_error_strategy(self, strategy: str):
        """
        设置代码转换错误处理策略
        
        Args:
            strategy: 错误处理策略 ('strict', 'lenient', 'ignore')
        """
        valid_strategies = ['strict', 'lenient', 'ignore']
        if strategy not in valid_strategies:
            raise ValidationError(f"错误处理策略必须是以下之一: {valid_strategies}")
        self.code_conversion_error_strategy = strategy
    
    def get_code_conversion_config(self) -> Dict[str, Any]:
        """
        获取代码转换相关的配置
        
        Returns:
            代码转换配置字典
        """
        return {
            'enable_auto_code_conversion': self.enable_auto_code_conversion,
            'strict_code_validation': self.strict_code_validation,
            'code_conversion_cache_size': self.code_conversion_cache_size,
            'log_code_conversions': self.log_code_conversions,
            'code_conversion_timeout': self.code_conversion_timeout,
            'enable_code_format_inference': self.enable_code_format_inference,
            'enable_exchange_inference': self.enable_exchange_inference,
            'code_conversion_batch_size': self.code_conversion_batch_size,
            'enable_code_conversion_cache': self.enable_code_conversion_cache,
            'code_conversion_error_strategy': self.code_conversion_error_strategy
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典
        
        Returns:
            配置字典
        """
        return asdict(self)
    
    def __str__(self) -> str:
        """字符串表示"""
        return f"Config(tushare_token={'***' if self.tushare_token else None}, " \
               f"cache_enabled={self.cache_enabled}, " \
               f"sqlite_db_path='{self.sqlite_db_path}')"
    
    def __repr__(self) -> str:
        """详细字符串表示"""
        return self.__str__()