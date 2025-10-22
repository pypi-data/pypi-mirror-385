"""
QuickStock SDK主客户端类

提供统一的金融数据访问接口，类似tushare的调用方式
"""

import asyncio
import logging
from typing import Optional, Dict, Any, Union, List, Tuple
import pandas as pd

from .config import Config
from .core.data_manager import DataManager
from .models import DataRequest
from .core.errors import QuickStockError, ValidationError
from .utils.validators import validate_stock_code, validate_date_format
from .utils.code_converter import normalize_stock_code, convert_stock_code


class QuickStockClient:
    """
    QuickStock SDK的主入口类
    提供统一的数据访问接口
    """
    
    def __init__(self, config: Optional[Config] = None):
        """
        初始化客户端
        
        Args:
            config: 配置对象，包含数据源配置、缓存配置等
            
        Raises:
            QuickStockError: 初始化失败
        """
        try:
            # 加载配置
            self.config = config or Config.load_default()
            
            # 设置日志
            self._setup_logging()
            
            # 初始化数据管理器
            self.data_manager = DataManager(self.config)
            
            # 客户端状态
            self._initialized = True
            
            self.logger.info("QuickStock客户端初始化成功")
            
        except Exception as e:
            error_msg = f"QuickStock客户端初始化失败: {e}"
            if hasattr(self, 'logger'):
                self.logger.error(error_msg)
            raise QuickStockError(error_msg) from e
    
    def _setup_logging(self):
        """设置日志配置"""
        self.logger = logging.getLogger('quickstock')
        
        # 如果已经配置过日志，直接返回
        if self.logger.handlers:
            return
        
        # 设置日志级别
        self.logger.setLevel(getattr(logging, self.config.log_level.upper()))
        
        # 创建格式化器
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # 文件处理器（如果配置了日志文件）
        if self.config.log_file:
            try:
                import os
                os.makedirs(os.path.dirname(self.config.log_file), exist_ok=True)
                
                file_handler = logging.FileHandler(self.config.log_file, encoding='utf-8')
                file_handler.setFormatter(formatter)
                self.logger.addHandler(file_handler)
            except Exception as e:
                self.logger.warning(f"无法创建日志文件: {e}")
    
    def _ensure_initialized(self):
        """确保客户端已正确初始化"""
        if not hasattr(self, '_initialized') or not self._initialized:
            raise QuickStockError("客户端未正确初始化")
    
    def _is_standard_format(self, code: str) -> bool:
        """
        检查是否为标准格式代码
        
        Args:
            code: 股票代码
            
        Returns:
            是否为标准格式
        """
        if not code or not isinstance(code, str):
            return False
        
        code = code.strip()
        
        # 只接受标准格式：6位数字.交易所代码
        import re
        pattern = r'^[0-9]{6}\.(SH|SZ)$'
        return bool(re.match(pattern, code, re.IGNORECASE))
    
    def _run_async(self, coro):
        """
        运行异步协程
        
        Args:
            coro: 异步协程
            
        Returns:
            协程执行结果
        """
        import inspect
        
        # 如果不是协程，直接返回
        if not inspect.iscoroutine(coro):
            return coro
        
        try:
            # 尝试获取当前事件循环
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # 在运行的事件循环中，使用新线程运行协程
                import threading
                import concurrent.futures
                
                def run_coro():
                    new_loop = asyncio.new_event_loop()
                    try:
                        return new_loop.run_until_complete(coro)
                    finally:
                        new_loop.close()
                
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(run_coro)
                    return future.result()
            else:
                # 如果在同步环境中，直接运行协程
                return loop.run_until_complete(coro)
        except RuntimeError:
            # 没有事件循环，创建新的
            return asyncio.run(coro)
    
    def get_config(self) -> Config:
        """
        获取当前配置
        
        Returns:
            配置对象
        """
        self._ensure_initialized()
        return self.config
    
    def update_config(self, **kwargs):
        """
        更新配置参数
        
        Args:
            **kwargs: 要更新的配置参数
            
        Raises:
            ValidationError: 配置参数无效
        """
        self._ensure_initialized()
        
        try:
            self.config.update(**kwargs)
            self.logger.info(f"配置已更新: {list(kwargs.keys())}")
        except Exception as e:
            raise ValidationError(f"配置更新失败: {e}") from e
    
    def get_provider_stats(self) -> Dict[str, Any]:
        """
        获取数据源统计信息
        
        Returns:
            数据源统计信息字典
        """
        self._ensure_initialized()
        return self.data_manager.source_manager.get_provider_stats()
    
    def get_provider_health(self) -> Dict[str, Any]:
        """
        获取数据源健康状态
        
        Returns:
            数据源健康状态字典
        """
        self._ensure_initialized()
        return self.data_manager.source_manager.get_provider_health()
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        获取缓存统计信息
        
        Returns:
            缓存统计信息字典
        """
        self._ensure_initialized()
        return self.data_manager.get_cache_stats()
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """
        获取内存统计信息
        
        Returns:
            内存统计信息字典
        """
        self._ensure_initialized()
        return self.data_manager.get_memory_stats()
    
    def optimize_memory_usage(self) -> Dict[str, Any]:
        """
        优化内存使用
        
        Returns:
            优化后的内存统计信息
        """
        self._ensure_initialized()
        return self.data_manager.optimize_memory_usage()
    
    def clear_cache(self):
        """清空所有缓存"""
        self._ensure_initialized()
        self.data_manager.clear_cache()
        self.logger.info("缓存已清空")
    
    def clear_expired_cache(self):
        """清理过期缓存"""
        self._ensure_initialized()
        self.data_manager.clear_expired_cache()
        self.logger.info("过期缓存已清理")
    
    def health_check(self) -> Dict[str, bool]:
        """
        执行健康检查
        
        Returns:
            健康检查结果
        """
        self._ensure_initialized()
        
        try:
            # 异步健康检查
            coro = self.data_manager.source_manager.health_check_all()
            return self._run_async(coro)
        except Exception as e:
            self.logger.error(f"健康检查失败: {e}")
            return {}
    
    def test_connection(self, provider_name: str = None) -> bool:
        """
        测试数据源连接
        
        Args:
            provider_name: 数据源名称，如果为None则测试所有数据源
            
        Returns:
            连接测试结果
        """
        self._ensure_initialized()
        
        try:
            if provider_name:
                # 测试指定数据源
                coro = self.data_manager.source_manager.test_provider(provider_name)
                return self._run_async(coro)
            else:
                # 测试所有数据源
                health_results = self.health_check()
                return any(health_results.values()) if health_results else False
        except Exception as e:
            self.logger.error(f"连接测试失败: {e}")
            return False
    
    def __enter__(self):
        """上下文管理器入口"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        # 清理资源
        try:
            if hasattr(self, 'data_manager'):
                # 这里可以添加清理逻辑
                pass
        except Exception as e:
            if hasattr(self, 'logger'):
                self.logger.warning(f"资源清理时出现警告: {e}")
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        # 异步清理资源
        try:
            if hasattr(self, 'data_manager'):
                # 清理数据源连接
                if hasattr(self.data_manager, 'source_manager'):
                    await self.data_manager.source_manager.close_all()
                # 清理缓存
                if hasattr(self.data_manager, 'cache_layer'):
                    await self.data_manager.cache_layer.close()
        except Exception as e:
            if hasattr(self, 'logger'):
                self.logger.warning(f"异步资源清理时出现警告: {e}")
    
    def __str__(self) -> str:
        """字符串表示"""
        return f"QuickStockClient(initialized={getattr(self, '_initialized', False)})"
    
    def __repr__(self) -> str:
        """详细字符串表示"""
        return self.__str__()
    
    # 代码转换工具方法
    def normalize_code(self, code: str) -> str:
        """
        标准化股票代码
        
        支持多种格式的股票代码输入，统一转换为标准格式 (000001.SZ)
        
        Args:
            code: 股票代码，支持以下格式：
                - 标准格式: 000001.SZ, 600000.SH
                - Baostock格式: sz.000001, sh.600000
                - 东方财富格式: 0.000001, 1.600000
                - 同花顺格式: hs_000001, hs_600000
                - 纯数字: 000001, 600000
        
        Returns:
            标准格式的股票代码
            
        Example:
            >>> client = QuickStockClient()
            >>> client.normalize_code('sh.600000')  # '600000.SH'
            >>> client.normalize_code('1.600000')   # '600000.SH'
            >>> client.normalize_code('hs_000001')  # '000001.SZ'
        """
        return normalize_stock_code(code)
    
    def convert_code(self, code: str, target_format: str) -> str:
        """
        转换股票代码到指定格式
        
        Args:
            code: 原始股票代码
            target_format: 目标格式
                - 'standard': 标准格式 (000001.SZ)
                - 'baostock': Baostock格式 (sz.000001)
                - 'eastmoney': 东方财富格式 (0.000001)
                - 'tonghuashun': 同花顺格式 (hs_000001)
        
        Returns:
            转换后的股票代码
            
        Example:
            >>> client = QuickStockClient()
            >>> client.convert_code('000001.SZ', 'baostock')    # 'sz.000001'
            >>> client.convert_code('600000.SH', 'eastmoney')   # '1.600000'
        """
        return convert_stock_code(code, target_format)
    
    def parse_code(self, code: str) -> Tuple[str, str]:
        """
        解析股票代码，返回代码和交易所
        
        Args:
            code: 股票代码，支持多种格式
        
        Returns:
            (股票代码, 交易所) 元组
            
        Example:
            >>> client = QuickStockClient()
            >>> client.parse_code('000001.SZ')     # ('000001', 'SZ')
            >>> client.parse_code('sh.600000')     # ('600000', 'SH')
            >>> client.parse_code('1.600000')      # ('600000', 'SH')
        """
        from .utils.code_converter import StockCodeConverter
        return StockCodeConverter.parse_stock_code(code)
    
    def validate_code(self, code: str) -> bool:
        """
        验证股票代码格式是否有效
        
        Args:
            code: 股票代码
        
        Returns:
            是否为有效的股票代码格式
            
        Example:
            >>> client = QuickStockClient()
            >>> client.validate_code('000001.SZ')    # True
            >>> client.validate_code('invalid')      # False
        """
        try:
            self.normalize_code(code)
            return True
        except Exception:
            return False
    
    def get_supported_formats(self) -> List[str]:
        """
        获取支持的股票代码格式列表
        
        Returns:
            支持的格式列表
            
        Example:
            >>> client = QuickStockClient()
            >>> client.get_supported_formats()
            ['standard', 'baostock', 'eastmoney', 'tonghuashun', 'exchange_prefix', 'pure_number']
        """
        from .utils.code_converter import StockCodeConverter
        return StockCodeConverter.get_supported_formats()
    
    def identify_code_format(self, code: str) -> Optional[str]:
        """
        识别股票代码格式
        
        Args:
            code: 股票代码
        
        Returns:
            格式名称，如果无法识别返回None
            
        Example:
            >>> client = QuickStockClient()
            >>> client.identify_code_format('000001.SZ')    # 'standard'
            >>> client.identify_code_format('sh.600000')    # 'baostock'
        """
        from .utils.code_converter import StockCodeConverter
        return StockCodeConverter.identify_code_format(code)
    
    def suggest_code_corrections(self, code: str) -> List[str]:
        """
        为无效代码提供修正建议
        
        Args:
            code: 无效的股票代码
        
        Returns:
            修正建议列表
            
        Example:
            >>> client = QuickStockClient()
            >>> client.suggest_code_corrections('000001.sz')
            ['尝试: 000001.SZ']
        """
        from .utils.code_converter import StockCodeConverter
        return StockCodeConverter.suggest_code_corrections(code)
    
    def batch_normalize_codes(self, codes: List[str]) -> List[str]:
        """
        批量标准化股票代码
        
        Args:
            codes: 股票代码列表
        
        Returns:
            标准化后的股票代码列表
            
        Example:
            >>> client = QuickStockClient()
            >>> client.batch_normalize_codes(['000001.SZ', 'sh.600000'])
            ['000001.SZ', '600000.SH']
        """
        from .utils.code_converter import batch_normalize_codes
        return batch_normalize_codes(codes)
    
    def batch_convert_codes(self, codes: List[str], target_format: str) -> List[str]:
        """
        批量转换股票代码到指定格式
        
        Args:
            codes: 股票代码列表
            target_format: 目标格式
        
        Returns:
            转换后的股票代码列表
            
        Example:
            >>> client = QuickStockClient()
            >>> client.batch_convert_codes(['000001.SZ', '600000.SH'], 'baostock')
            ['sz.000001', 'sh.600000']
        """
        from .utils.code_converter import batch_convert_codes
        return batch_convert_codes(codes, target_format)
    
    def get_code_conversion_stats(self) -> Dict[str, Any]:
        """
        获取代码转换缓存统计信息
        
        Returns:
            缓存统计信息字典
            
        Example:
            >>> client = QuickStockClient()
            >>> stats = client.get_code_conversion_stats()
            >>> print(f"缓存命中率: {stats['hit_rate']:.2%}")
        """
        from .utils.code_converter import StockCodeConverter
        return StockCodeConverter.get_cache_stats()
    
    def clear_code_conversion_cache(self) -> None:
        """
        清空代码转换缓存
        
        Example:
            >>> client = QuickStockClient()
            >>> client.clear_code_conversion_cache()
        """
        from .utils.code_converter import StockCodeConverter
        StockCodeConverter.clear_cache()
        self.logger.info("代码转换缓存已清空")
    
    def validate_code_with_details(self, code: str) -> Dict[str, Any]:
        """
        验证股票代码并返回详细信息
        
        Args:
            code: 股票代码
        
        Returns:
            详细的验证结果字典，包含：
            - is_valid: 是否有效
            - issues: 检测到的问题列表
            - suggestions: 修正建议列表
            - detected_format: 检测到的格式
            - parsed_code: 解析后的代码
            - parsed_exchange: 解析后的交易所
            
        Example:
            >>> client = QuickStockClient()
            >>> result = client.validate_code_with_details('000001.sz')
            >>> print(result['suggestions'])
            ['尝试: 000001.SZ']
        """
        from .utils.code_converter import StockCodeConverter
        return StockCodeConverter.validate_code_with_details(code)
    
    def get_code_format_help(self, format_name: str = None) -> Dict[str, Any]:
        """
        获取股票代码格式帮助信息
        
        Args:
            format_name: 格式名称，如果为None则返回所有格式的帮助
        
        Returns:
            格式帮助信息字典
            
        Example:
            >>> client = QuickStockClient()
            >>> help_info = client.get_code_format_help('standard')
            >>> print(help_info['description'])
            '6位数字代码 + 点号 + 交易所代码(SH/SZ)'
        """
        from .utils.code_converter import StockCodeConverter
        return StockCodeConverter.get_format_help(format_name)
    
    def suggest_code_auto_correction(self, code: str) -> Dict[str, Any]:
        """
        为无效代码提供自动修正建议
        
        Args:
            code: 无效的股票代码
        
        Returns:
            自动修正建议字典，包含：
            - can_auto_correct: 是否可以自动修正
            - corrections: 修正选项列表（按置信度排序）
            - suggestions: 人工建议列表
            
        Example:
            >>> client = QuickStockClient()
            >>> suggestions = client.suggest_code_auto_correction('000001.sz')
            >>> if suggestions['can_auto_correct']:
            ...     best_correction = suggestions['corrections'][0]
            ...     print(f"建议修正为: {best_correction['corrected']}")
        """
        from .utils.code_converter import StockCodeConverter
        return StockCodeConverter.suggest_auto_correction(code)
    
    def get_validation_help(self) -> Dict[str, Any]:
        """
        获取代码验证帮助信息
        
        Returns:
            验证帮助信息字典，包含：
            - supported_formats: 支持的格式详情
            - validation_rules: 验证规则
            - common_errors: 常见错误及解决方案
            - examples: 有效和无效代码示例
            
        Example:
            >>> client = QuickStockClient()
            >>> help_info = client.get_validation_help()
            >>> print("支持的格式:")
            >>> for fmt, info in help_info['supported_formats'].items():
            ...     print(f"  {info['name']}: {info['pattern']}")
        """
        from .utils.code_converter import StockCodeConverter
        return StockCodeConverter.get_validation_help()
    
    def batch_validate_codes(self, codes: List[str]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        批量验证股票代码
        
        Args:
            codes: 股票代码列表
        
        Returns:
            (成功结果列表, 错误信息列表) 元组
            
        Example:
            >>> client = QuickStockClient()
            >>> codes = ['000001.SZ', '600000.SH', 'invalid']
            >>> valid, invalid = client.batch_validate_codes(codes)
            >>> print(f"有效代码: {len(valid)}, 无效代码: {len(invalid)}")
        """
        from .utils.code_converter import StockCodeConverter
        return StockCodeConverter.batch_convert_codes_with_errors(codes, 'standard')
    
    def _validate_and_normalize_code(self, ts_code: str, param_name: str = "股票代码") -> str:
        """
        验证并标准化股票代码（向后兼容版本）
        
        Args:
            ts_code: 股票代码
            param_name: 参数名称（用于错误信息）
            
        Returns:
            标准化后的股票代码
            
        Raises:
            ValidationError: 代码验证失败
        """
        if not ts_code:
            raise ValidationError(f"{param_name}不能为空")
        
        # 保存原始代码用于错误信息
        original_code = ts_code
        
        # 检查是否启用自动代码转换
        if not self.config.enable_auto_code_conversion:
            # 向后兼容模式：只验证标准格式代码
            if not self._is_standard_format(ts_code):
                raise ValidationError(f"{param_name}格式无效: {original_code}. 请使用标准格式（如：000001.SZ）")
            return ts_code
        
        try:
            # 自动标准化股票代码
            ts_code = self.normalize_code(ts_code)
            
            # 记录转换日志（如果启用）
            if self.config.log_code_conversions and original_code != ts_code:
                self.logger.debug(f"{param_name}标准化: {original_code} -> {ts_code}")
            
            # 验证标准化后的代码
            if not validate_stock_code(ts_code):
                raise ValidationError(f"{param_name}格式无效: {original_code}")
                
            return ts_code
            
        except Exception as e:
            # 根据错误处理策略处理异常
            return self._handle_code_validation_error(e, original_code, param_name)
    
    def _handle_code_validation_error(self, error: Exception, original_code: str, param_name: str) -> str:
        """
        处理代码验证错误（向后兼容）
        
        Args:
            error: 原始异常
            original_code: 原始代码
            param_name: 参数名称
            
        Returns:
            处理后的代码（如果可能）
            
        Raises:
            ValidationError: 无法处理的验证错误
        """
        # 如果是ImportError，说明代码转换器不可用，使用回退逻辑
        if isinstance(error, ImportError):
            # 在回退模式下，只接受标准格式代码
            if self._is_standard_format(original_code):
                return original_code
            raise ValidationError(f"{param_name}格式无效: {original_code}")
        
        # 导入新的异常类型
        try:
            from .utils.code_converter import CodeConversionError, InvalidCodeFormatError, ExchangeInferenceError
        except ImportError:
            # 如果新的转换器不可用，使用旧的验证逻辑（只接受标准格式）
            if self._is_standard_format(original_code):
                return original_code
            raise ValidationError(f"{param_name}格式无效: {original_code}")
        
        error_strategy = self.config.code_conversion_error_strategy
        
        if isinstance(error, CodeConversionError):
            if error_strategy == 'ignore':
                # 忽略错误，使用原始代码
                self.logger.warning(f"{param_name}转换失败，使用原始代码: {original_code}")
                return original_code
            elif error_strategy == 'lenient':
                # 宽松模式：尝试使用原始代码或提供建议
                if validate_stock_code(original_code):
                    self.logger.warning(f"{param_name}转换失败，但原始代码有效: {original_code}")
                    return original_code
                else:
                    # 提供用户友好的错误信息
                    error_msg = f"{param_name}验证失败: {error.get_user_friendly_message()}"
                    self.logger.warning(error_msg)
                    raise ValidationError(error_msg)
            else:  # strict
                error_msg = f"{param_name}验证失败: {error.get_user_friendly_message()}"
                self.logger.warning(error_msg)
                raise ValidationError(error_msg)
        
        elif isinstance(error, ValidationError):
            if error_strategy == 'ignore':
                self.logger.warning(f"{param_name}验证失败，使用原始代码: {original_code}")
                return original_code
            elif error_strategy == 'lenient':
                # 增强现有的ValidationError
                error_msg = f"{param_name}格式无效: {original_code}"
                if hasattr(error, 'suggestions') and error.suggestions:
                    error_msg += f". 建议: {'; '.join(error.suggestions[:3])}"
                raise ValidationError(error_msg)
            else:  # strict
                raise error
        
        else:
            # 其他异常（包括一般的Exception）
            if error_strategy == 'ignore':
                self.logger.warning(f"{param_name}验证时发生未知错误，使用原始代码: {original_code}")
                return original_code
            elif error_strategy == 'lenient':
                # 宽松模式：如果原始代码有效，使用原始代码
                if validate_stock_code(original_code):
                    self.logger.warning(f"{param_name}转换失败，但原始代码有效: {original_code}")
                    return original_code
                else:
                    self.logger.warning(f"{param_name}验证时发生未知错误: {error}")
                    raise ValidationError(f"{param_name}格式无效: {original_code}")
            else:  # strict
                self.logger.warning(f"{param_name}验证时发生未知错误: {error}")
                raise ValidationError(f"{param_name}格式无效: {original_code}")
    
    # 股票相关接口
    def stock_basic(self, **kwargs) -> pd.DataFrame:
        """
        获取股票基础信息
        
        Args:
            **kwargs: 查询参数
                - exchange: 交易所代码 (SSE上交所, SZSE深交所)
                - list_status: 上市状态 (L上市, D退市, P暂停)
                - fields: 指定返回字段
                - limit: 限制返回条数
                
        Returns:
            包含股票基础信息的DataFrame
            
        Raises:
            ValidationError: 参数验证失败
            QuickStockError: 数据获取失败
        """
        self._ensure_initialized()
        
        try:
            # 创建数据请求
            request = DataRequest(
                data_type='stock_basic',
                extra_params=kwargs
            )
            
            # 获取数据
            coro = self.data_manager.get_data(request)
            result = self._run_async(coro)
            
            self.logger.info(f"获取股票基础信息成功，共{len(result)}条记录")
            return result
            
        except Exception as e:
            error_msg = f"获取股票基础信息失败: {e}"
            self.logger.error(error_msg)
            raise QuickStockError(error_msg) from e
        
    def stock_daily(self, ts_code: str, start_date: str = None, 
                   end_date: str = None, **kwargs) -> pd.DataFrame:
        """
        获取股票日线数据
        
        Args:
            ts_code: 股票代码，支持多种格式：
                - 标准格式: 000001.SZ, 600000.SH
                - Baostock格式: sz.000001, sh.600000  
                - 东方财富格式: 0.000001, 1.600000
                - 同花顺格式: hs_000001, hs_600000
                - 纯数字: 000001, 600000
            start_date: 开始日期 (格式: YYYYMMDD 或 YYYY-MM-DD)
            end_date: 结束日期 (格式: YYYYMMDD 或 YYYY-MM-DD)
            **kwargs: 其他参数
                - adj: 复权类型 (None不复权, qfq前复权, hfq后复权)
                - fields: 指定返回字段
                
        Returns:
            包含股票日线数据的DataFrame
            
        Raises:
            ValidationError: 参数验证失败
            QuickStockError: 数据获取失败
        """
        self._ensure_initialized()
        
        try:
            # 使用增强的代码验证和标准化
            ts_code = self._validate_and_normalize_code(ts_code, "股票代码")
            
            if start_date and not validate_date_format(start_date):
                raise ValidationError(f"开始日期格式无效: {start_date}")
            
            if end_date and not validate_date_format(end_date):
                raise ValidationError(f"结束日期格式无效: {end_date}")
            
            # 创建数据请求
            request = DataRequest(
                data_type='stock_daily',
                ts_code=ts_code,
                start_date=start_date,
                end_date=end_date,
                extra_params=kwargs
            )
            
            # 获取数据
            coro = self.data_manager.get_data(request)
            result = self._run_async(coro)
            
            self.logger.info(f"获取股票{ts_code}日线数据成功，共{len(result)}条记录")
            return result
            
        except Exception as e:
            error_msg = f"获取股票日线数据失败: {e}"
            self.logger.error(error_msg)
            raise QuickStockError(error_msg) from e
        
    def stock_minute(self, ts_code: str, freq: str = '1min', 
                    start_date: str = None, end_date: str = None, **kwargs) -> pd.DataFrame:
        """
        获取股票分钟数据
        
        Args:
            ts_code: 股票代码 (如: 000001.SZ)
            freq: 频率 (1min, 5min, 15min, 30min, 60min)
            start_date: 开始日期 (格式: YYYYMMDD 或 YYYY-MM-DD)
            end_date: 结束日期 (格式: YYYYMMDD 或 YYYY-MM-DD)
            **kwargs: 其他参数
                - adj: 复权类型
                - fields: 指定返回字段
                
        Returns:
            包含股票分钟数据的DataFrame
            
        Raises:
            ValidationError: 参数验证失败
            QuickStockError: 数据获取失败
        """
        self._ensure_initialized()
        
        try:
            # 使用增强的代码验证和标准化
            ts_code = self._validate_and_normalize_code(ts_code, "股票代码")
            
            valid_freqs = ['1min', '5min', '15min', '30min', '60min']
            if freq not in valid_freqs:
                raise ValidationError(f"频率参数无效: {freq}，支持的频率: {valid_freqs}")
            
            if start_date and not validate_date_format(start_date):
                raise ValidationError(f"开始日期格式无效: {start_date}")
            
            if end_date and not validate_date_format(end_date):
                raise ValidationError(f"结束日期格式无效: {end_date}")
            
            # 创建数据请求
            request = DataRequest(
                data_type='stock_minute',
                ts_code=ts_code,
                freq=freq,
                start_date=start_date,
                end_date=end_date,
                extra_params=kwargs
            )
            
            # 获取数据
            coro = self.data_manager.get_data(request)
            result = self._run_async(coro)
            
            self.logger.info(f"获取股票{ts_code}分钟数据({freq})成功，共{len(result)}条记录")
            return result
            
        except Exception as e:
            error_msg = f"获取股票分钟数据失败: {e}"
            self.logger.error(error_msg)
            raise QuickStockError(error_msg) from e
    
    def stock_weekly(self, ts_code: str, start_date: str = None, 
                    end_date: str = None, **kwargs) -> pd.DataFrame:
        """
        获取股票周线数据
        
        Args:
            ts_code: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            **kwargs: 其他参数
                
        Returns:
            包含股票周线数据的DataFrame
        """
        self._ensure_initialized()
        
        try:
            # 使用增强的代码验证和标准化
            ts_code = self._validate_and_normalize_code(ts_code, "股票代码")
            
            # 创建数据请求
            request = DataRequest(
                data_type='stock_weekly',
                ts_code=ts_code,
                start_date=start_date,
                end_date=end_date,
                extra_params=kwargs
            )
            
            # 获取数据
            coro = self.data_manager.get_data(request)
            result = self._run_async(coro)
            
            self.logger.info(f"获取股票{ts_code}周线数据成功，共{len(result)}条记录")
            return result
            
        except Exception as e:
            error_msg = f"获取股票周线数据失败: {e}"
            self.logger.error(error_msg)
            raise QuickStockError(error_msg) from e
    
    def stock_monthly(self, ts_code: str, start_date: str = None, 
                     end_date: str = None, **kwargs) -> pd.DataFrame:
        """
        获取股票月线数据
        
        Args:
            ts_code: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            **kwargs: 其他参数
                
        Returns:
            包含股票月线数据的DataFrame
        """
        self._ensure_initialized()
        
        try:
            # 使用增强的代码验证和标准化
            ts_code = self._validate_and_normalize_code(ts_code, "股票代码")
            
            # 创建数据请求
            request = DataRequest(
                data_type='stock_monthly',
                ts_code=ts_code,
                start_date=start_date,
                end_date=end_date,
                extra_params=kwargs
            )
            
            # 获取数据
            coro = self.data_manager.get_data(request)
            result = self._run_async(coro)
            
            self.logger.info(f"获取股票{ts_code}月线数据成功，共{len(result)}条记录")
            return result
            
        except Exception as e:
            error_msg = f"获取股票月线数据失败: {e}"
            self.logger.error(error_msg)
            raise QuickStockError(error_msg) from e
    
    # 指数相关接口
    def index_basic(self, **kwargs) -> pd.DataFrame:
        """
        获取指数基础信息
        
        Args:
            **kwargs: 查询参数
                - market: 市场代码 (SSE上交所, SZSE深交所, CSI中证)
                - publisher: 发布商
                - category: 指数类别
                - fields: 指定返回字段
                - limit: 限制返回条数
                
        Returns:
            包含指数基础信息的DataFrame
            
        Raises:
            ValidationError: 参数验证失败
            QuickStockError: 数据获取失败
        """
        self._ensure_initialized()
        
        try:
            # 创建数据请求
            request = DataRequest(
                data_type='index_basic',
                extra_params=kwargs
            )
            
            # 获取数据
            coro = self.data_manager.get_data(request)
            result = self._run_async(coro)
            
            self.logger.info(f"获取指数基础信息成功，共{len(result)}条记录")
            return result
            
        except Exception as e:
            error_msg = f"获取指数基础信息失败: {e}"
            self.logger.error(error_msg)
            raise QuickStockError(error_msg) from e
        
    def index_daily(self, ts_code: str, start_date: str = None,
                   end_date: str = None, **kwargs) -> pd.DataFrame:
        """
        获取指数日线数据
        
        Args:
            ts_code: 指数代码 (如: 000001.SH)
            start_date: 开始日期 (格式: YYYYMMDD 或 YYYY-MM-DD)
            end_date: 结束日期 (格式: YYYYMMDD 或 YYYY-MM-DD)
            **kwargs: 其他参数
                - fields: 指定返回字段
                
        Returns:
            包含指数日线数据的DataFrame
            
        Raises:
            ValidationError: 参数验证失败
            QuickStockError: 数据获取失败
        """
        self._ensure_initialized()
        
        try:
            # 参数验证
            if not ts_code:
                raise ValidationError("指数代码不能为空")
            
            if start_date and not validate_date_format(start_date):
                raise ValidationError(f"开始日期格式无效: {start_date}")
            
            if end_date and not validate_date_format(end_date):
                raise ValidationError(f"结束日期格式无效: {end_date}")
            
            # 创建数据请求
            request = DataRequest(
                data_type='index_daily',
                ts_code=ts_code,
                start_date=start_date,
                end_date=end_date,
                extra_params=kwargs
            )
            
            # 获取数据
            coro = self.data_manager.get_data(request)
            result = self._run_async(coro)
            
            self.logger.info(f"获取指数{ts_code}日线数据成功，共{len(result)}条记录")
            return result
            
        except Exception as e:
            error_msg = f"获取指数日线数据失败: {e}"
            self.logger.error(error_msg)
            raise QuickStockError(error_msg) from e
    
    def index_weight(self, index_code: str, trade_date: str = None, **kwargs) -> pd.DataFrame:
        """
        获取指数成分股权重
        
        Args:
            index_code: 指数代码
            trade_date: 交易日期
            **kwargs: 其他参数
                
        Returns:
            包含指数成分股权重的DataFrame
        """
        self._ensure_initialized()
        
        try:
            # 参数验证
            if not index_code:
                raise ValidationError("指数代码不能为空")
            
            if trade_date and not validate_date_format(trade_date):
                raise ValidationError(f"交易日期格式无效: {trade_date}")
            
            # 创建数据请求
            request = DataRequest(
                data_type='index_weight',
                ts_code=index_code,
                start_date=trade_date,
                extra_params=kwargs
            )
            
            # 获取数据
            coro = self.data_manager.get_data(request)
            result = self._run_async(coro)
            
            self.logger.info(f"获取指数{index_code}成分股权重成功，共{len(result)}条记录")
            return result
            
        except Exception as e:
            error_msg = f"获取指数成分股权重失败: {e}"
            self.logger.error(error_msg)
            raise QuickStockError(error_msg) from e
    
    # 基金相关接口
    def fund_basic(self, **kwargs) -> pd.DataFrame:
        """
        获取基金基础信息
        
        Args:
            **kwargs: 查询参数
                - market: 市场类型 (E场内, O场外)
                - fund_type: 基金类型
                - status: 基金状态 (D正常, I发行, L上市)
                - fields: 指定返回字段
                - limit: 限制返回条数
                
        Returns:
            包含基金基础信息的DataFrame
            
        Raises:
            ValidationError: 参数验证失败
            QuickStockError: 数据获取失败
        """
        self._ensure_initialized()
        
        try:
            # 创建数据请求
            request = DataRequest(
                data_type='fund_basic',
                extra_params=kwargs
            )
            
            # 获取数据
            coro = self.data_manager.get_data(request)
            result = self._run_async(coro)
            
            self.logger.info(f"获取基金基础信息成功，共{len(result)}条记录")
            return result
            
        except Exception as e:
            error_msg = f"获取基金基础信息失败: {e}"
            self.logger.error(error_msg)
            raise QuickStockError(error_msg) from e
        
    def fund_nav(self, ts_code: str, start_date: str = None,
                end_date: str = None, **kwargs) -> pd.DataFrame:
        """
        获取基金净值数据
        
        Args:
            ts_code: 基金代码 (如: 110022.OF)
            start_date: 开始日期 (格式: YYYYMMDD 或 YYYY-MM-DD)
            end_date: 结束日期 (格式: YYYYMMDD 或 YYYY-MM-DD)
            **kwargs: 其他参数
                - fields: 指定返回字段
                
        Returns:
            包含基金净值数据的DataFrame
            
        Raises:
            ValidationError: 参数验证失败
            QuickStockError: 数据获取失败
        """
        self._ensure_initialized()
        
        try:
            # 参数验证
            if not ts_code:
                raise ValidationError("基金代码不能为空")
            
            if start_date and not validate_date_format(start_date):
                raise ValidationError(f"开始日期格式无效: {start_date}")
            
            if end_date and not validate_date_format(end_date):
                raise ValidationError(f"结束日期格式无效: {end_date}")
            
            # 创建数据请求
            request = DataRequest(
                data_type='fund_nav',
                ts_code=ts_code,
                start_date=start_date,
                end_date=end_date,
                extra_params=kwargs
            )
            
            # 获取数据
            coro = self.data_manager.get_data(request)
            result = self._run_async(coro)
            
            self.logger.info(f"获取基金{ts_code}净值数据成功，共{len(result)}条记录")
            return result
            
        except Exception as e:
            error_msg = f"获取基金净值数据失败: {e}"
            self.logger.error(error_msg)
            raise QuickStockError(error_msg) from e
    
    def fund_portfolio(self, ts_code: str, end_date: str = None, **kwargs) -> pd.DataFrame:
        """
        获取基金持仓数据
        
        Args:
            ts_code: 基金代码
            end_date: 截止日期
            **kwargs: 其他参数
                
        Returns:
            包含基金持仓数据的DataFrame
        """
        self._ensure_initialized()
        
        try:
            # 参数验证
            if not ts_code:
                raise ValidationError("基金代码不能为空")
            
            if end_date and not validate_date_format(end_date):
                raise ValidationError(f"截止日期格式无效: {end_date}")
            
            # 创建数据请求
            request = DataRequest(
                data_type='fund_portfolio',
                ts_code=ts_code,
                end_date=end_date,
                extra_params=kwargs
            )
            
            # 获取数据
            coro = self.data_manager.get_data(request)
            result = self._run_async(coro)
            
            self.logger.info(f"获取基金{ts_code}持仓数据成功，共{len(result)}条记录")
            return result
            
        except Exception as e:
            error_msg = f"获取基金持仓数据失败: {e}"
            self.logger.error(error_msg)
            raise QuickStockError(error_msg) from e
    
    # 交易日历接口
    def trade_cal(self, exchange: str = 'SSE', start_date: str = None, 
                 end_date: str = None, **kwargs) -> pd.DataFrame:
        """
        获取交易日历
        
        Args:
            exchange: 交易所代码 (SSE上交所, SZSE深交所)
            start_date: 开始日期 (格式: YYYYMMDD 或 YYYY-MM-DD)
            end_date: 结束日期 (格式: YYYYMMDD 或 YYYY-MM-DD)
            **kwargs: 其他参数
                - is_open: 是否交易日 (0休市, 1交易)
                - fields: 指定返回字段
                
        Returns:
            包含交易日历的DataFrame
            
        Raises:
            ValidationError: 参数验证失败
            QuickStockError: 数据获取失败
        """
        self._ensure_initialized()
        
        try:
            # 参数验证
            if start_date and not validate_date_format(start_date):
                raise ValidationError(f"开始日期格式无效: {start_date}")
            
            if end_date and not validate_date_format(end_date):
                raise ValidationError(f"结束日期格式无效: {end_date}")
            
            # 创建数据请求
            request = DataRequest(
                data_type='trade_cal',
                start_date=start_date,
                end_date=end_date,
                extra_params={'exchange': exchange, **kwargs}
            )
            
            # 获取数据
            coro = self.data_manager.get_data(request)
            result = self._run_async(coro)
            
            self.logger.info(f"获取交易日历成功，共{len(result)}条记录")
            return result
            
        except Exception as e:
            error_msg = f"获取交易日历失败: {e}"
            self.logger.error(error_msg)
            raise QuickStockError(error_msg) from e
        
    def is_trade_date(self, date: str, exchange: str = 'SSE') -> bool:
        """
        判断是否为交易日
        
        Args:
            date: 日期字符串 (格式: YYYYMMDD 或 YYYY-MM-DD)
            exchange: 交易所代码 (SSE上交所, SZSE深交所)
            
        Returns:
            是否为交易日
            
        Raises:
            ValidationError: 参数验证失败
            QuickStockError: 数据获取失败
        """
        self._ensure_initialized()
        
        try:
            # 参数验证
            if not date:
                raise ValidationError("日期不能为空")
            
            if not validate_date_format(date):
                raise ValidationError(f"日期格式无效: {date}")
            
            # 获取指定日期的交易日历
            trade_cal = self.trade_cal(
                exchange=exchange,
                start_date=date,
                end_date=date
            )
            
            if trade_cal.empty:
                # 如果没有找到记录，默认为非交易日
                return False
            
            # 检查is_open字段
            is_open = trade_cal.iloc[0].get('is_open', 0)
            result = bool(is_open)
            
            self.logger.debug(f"日期{date}交易日判断结果: {result}")
            return result
            
        except Exception as e:
            error_msg = f"交易日判断失败: {e}"
            self.logger.error(error_msg)
            raise QuickStockError(error_msg) from e
    
    def get_trade_dates(self, start_date: str, end_date: str, 
                       exchange: str = 'SSE') -> List[str]:
        """
        获取指定时间范围内的交易日列表
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
            exchange: 交易所代码
            
        Returns:
            交易日列表
        """
        self._ensure_initialized()
        
        try:
            # 获取交易日历
            trade_cal = self.trade_cal(
                exchange=exchange,
                start_date=start_date,
                end_date=end_date
            )
            
            # 筛选交易日
            trade_dates = trade_cal[trade_cal['is_open'] == 1]['cal_date'].tolist()
            
            self.logger.info(f"获取交易日列表成功，共{len(trade_dates)}个交易日")
            return trade_dates
            
        except Exception as e:
            error_msg = f"获取交易日列表失败: {e}"
            self.logger.error(error_msg)
            raise QuickStockError(error_msg) from e
    
    def get_prev_trade_date(self, date: str, exchange: str = 'SSE') -> Optional[str]:
        """
        获取指定日期的上一个交易日
        
        Args:
            date: 指定日期
            exchange: 交易所代码
            
        Returns:
            上一个交易日，如果没有则返回None
        """
        self._ensure_initialized()
        
        try:
            from datetime import datetime, timedelta
            
            # 解析日期
            if len(date) == 8:
                date_obj = datetime.strptime(date, '%Y%m%d')
            else:
                date_obj = datetime.strptime(date, '%Y-%m-%d')
            
            # 向前查找30天内的交易日历
            start_date_obj = date_obj - timedelta(days=30)
            start_date_str = start_date_obj.strftime('%Y%m%d')
            end_date_str = (date_obj - timedelta(days=1)).strftime('%Y%m%d')
            
            # 获取交易日历
            trade_cal = self.trade_cal(
                exchange=exchange,
                start_date=start_date_str,
                end_date=end_date_str
            )
            
            # 筛选交易日并按日期降序排序
            trade_dates = trade_cal[trade_cal['is_open'] == 1].sort_values(
                'cal_date', ascending=False
            )
            
            if not trade_dates.empty:
                prev_date = trade_dates.iloc[0]['cal_date']
                self.logger.debug(f"日期{date}的上一个交易日: {prev_date}")
                return prev_date
            
            return None
            
        except Exception as e:
            error_msg = f"获取上一个交易日失败: {e}"
            self.logger.error(error_msg)
            raise QuickStockError(error_msg) from e
    
    def get_next_trade_date(self, date: str, exchange: str = 'SSE') -> Optional[str]:
        """
        获取指定日期的下一个交易日
        
        Args:
            date: 指定日期
            exchange: 交易所代码
            
        Returns:
            下一个交易日，如果没有则返回None
        """
        self._ensure_initialized()
        
        try:
            from datetime import datetime, timedelta
            
            # 解析日期
            if len(date) == 8:
                date_obj = datetime.strptime(date, '%Y%m%d')
            else:
                date_obj = datetime.strptime(date, '%Y-%m-%d')
            
            # 向后查找30天内的交易日历
            start_date_str = (date_obj + timedelta(days=1)).strftime('%Y%m%d')
            end_date_obj = date_obj + timedelta(days=30)
            end_date_str = end_date_obj.strftime('%Y%m%d')
            
            # 获取交易日历
            trade_cal = self.trade_cal(
                exchange=exchange,
                start_date=start_date_str,
                end_date=end_date_str
            )
            
            # 筛选交易日并按日期升序排序
            trade_dates = trade_cal[trade_cal['is_open'] == 1].sort_values(
                'cal_date', ascending=True
            )
            
            if not trade_dates.empty:
                next_date = trade_dates.iloc[0]['cal_date']
                self.logger.debug(f"日期{date}的下一个交易日: {next_date}")
                return next_date
            
            return None
            
        except Exception as e:
            error_msg = f"获取下一个交易日失败: {e}"
            self.logger.error(error_msg)
            raise QuickStockError(error_msg) from e
    
    # 异步API接口
    async def stock_basic_async(self, **kwargs) -> pd.DataFrame:
        """
        异步获取股票基础信息
        
        Args:
            **kwargs: 查询参数
                
        Returns:
            包含股票基础信息的DataFrame
        """
        self._ensure_initialized()
        
        # 创建数据请求
        request = DataRequest(
            data_type='stock_basic',
            extra_params=kwargs
        )
        
        # 异步获取数据
        result = await self.data_manager.get_data(request)
        self.logger.info(f"异步获取股票基础信息成功，共{len(result)}条记录")
        return result
    
    async def stock_daily_async(self, ts_code: str, start_date: str = None, 
                               end_date: str = None, **kwargs) -> pd.DataFrame:
        """
        异步获取股票日线数据
        
        Args:
            ts_code: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            **kwargs: 其他参数
                
        Returns:
            包含股票日线数据的DataFrame
        """
        self._ensure_initialized()
        
        # 参数验证
        if not ts_code:
            raise ValidationError("股票代码不能为空")
        
        if not validate_stock_code(ts_code):
            raise ValidationError(f"股票代码格式无效: {ts_code}")
        
        if start_date and not validate_date_format(start_date):
            raise ValidationError(f"开始日期格式无效: {start_date}")
        
        if end_date and not validate_date_format(end_date):
            raise ValidationError(f"结束日期格式无效: {end_date}")
        
        # 创建数据请求
        request = DataRequest(
            data_type='stock_daily',
            ts_code=ts_code,
            start_date=start_date,
            end_date=end_date,
            extra_params=kwargs
        )
        
        # 异步获取数据
        result = await self.data_manager.get_data(request)
        self.logger.info(f"异步获取股票{ts_code}日线数据成功，共{len(result)}条记录")
        return result
    
    async def stock_minute_async(self, ts_code: str, freq: str = '1min', 
                                start_date: str = None, end_date: str = None, **kwargs) -> pd.DataFrame:
        """
        异步获取股票分钟数据
        
        Args:
            ts_code: 股票代码
            freq: 频率
            start_date: 开始日期
            end_date: 结束日期
            **kwargs: 其他参数
                
        Returns:
            包含股票分钟数据的DataFrame
        """
        self._ensure_initialized()
        
        # 参数验证
        if not ts_code:
            raise ValidationError("股票代码不能为空")
        
        if not validate_stock_code(ts_code):
            raise ValidationError(f"股票代码格式无效: {ts_code}")
        
        valid_freqs = ['1min', '5min', '15min', '30min', '60min']
        if freq not in valid_freqs:
            raise ValidationError(f"频率参数无效: {freq}，支持的频率: {valid_freqs}")
        
        # 创建数据请求
        request = DataRequest(
            data_type='stock_minute',
            ts_code=ts_code,
            freq=freq,
            start_date=start_date,
            end_date=end_date,
            extra_params=kwargs
        )
        
        # 异步获取数据
        result = await self.data_manager.get_data(request)
        self.logger.info(f"异步获取股票{ts_code}分钟数据({freq})成功，共{len(result)}条记录")
        return result
    
    async def get_data_batch_async(self, requests: List[DataRequest]) -> List[pd.DataFrame]:
        """
        异步批量获取数据
        
        Args:
            requests: 数据请求列表
            
        Returns:
            数据结果列表
        """
        self._ensure_initialized()
        
        results = await self.data_manager.get_data_batch(requests)
        self.logger.info(f"异步批量获取数据完成，共{len(requests)}个请求")
        return results
    
    async def trade_cal_async(self, exchange: str = 'SSE', start_date: str = None, 
                             end_date: str = None, **kwargs) -> pd.DataFrame:
        """
        异步获取交易日历
        
        Args:
            exchange: 交易所代码
            start_date: 开始日期
            end_date: 结束日期
            **kwargs: 其他参数
                
        Returns:
            包含交易日历的DataFrame
        """
        self._ensure_initialized()
        
        # 参数验证
        if start_date and not validate_date_format(start_date):
            raise ValidationError(f"开始日期格式无效: {start_date}")
        
        if end_date and not validate_date_format(end_date):
            raise ValidationError(f"结束日期格式无效: {end_date}")
        
        # 创建数据请求
        request = DataRequest(
            data_type='trade_cal',
            start_date=start_date,
            end_date=end_date,
            extra_params={'exchange': exchange, **kwargs}
        )
        
        # 异步获取数据
        result = await self.data_manager.get_data(request)
        self.logger.info(f"异步获取交易日历成功，共{len(result)}条记录")
        return result