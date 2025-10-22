"""
异常定义和错误处理

定义SDK的异常层次结构和错误处理机制
"""

import logging
import time
from typing import Callable, Dict, Any, Optional, TYPE_CHECKING
from datetime import datetime, timedelta

if TYPE_CHECKING:
    from ..config import Config


class QuickStockError(Exception):
    """SDK基础异常类"""
    
    def __init__(self, message: str, error_code: str = None, details: Dict[str, Any] = None):
        """
        初始化异常
        
        Args:
            message: 错误消息
            error_code: 错误代码
            details: 错误详细信息
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}


class DataSourceError(QuickStockError):
    """数据源相关异常"""
    pass


class CacheError(QuickStockError):
    """缓存相关异常"""
    pass


class ValidationError(QuickStockError):
    """参数验证异常"""
    pass


class RateLimitError(QuickStockError):
    """速率限制异常"""
    pass


class NetworkError(QuickStockError):
    """网络相关异常"""
    pass


class ErrorHandler:
    """错误处理器"""
    
    def __init__(self, config: 'Config'):
        """
        初始化错误处理器
        
        Args:
            config: 配置对象
        """
        self.config = config
        self.logger = self._setup_logger()
        self._error_stats = {
            'total_errors': 0,
            'retry_attempts': 0,
            'successful_retries': 0,
            'failed_retries': 0,
            'error_types': {}
        }
        self._rate_limit_tracker = {}
    
    def _setup_logger(self) -> logging.Logger:
        """
        设置日志记录器
        
        Returns:
            配置好的日志记录器
        """
        logger = logging.getLogger('quickstock.errors')
        
        # 避免重复添加处理器
        if logger.handlers:
            return logger
        
        # 设置日志级别
        log_level = getattr(self.config, 'log_level', 'INFO')
        if isinstance(log_level, str):
            logger.setLevel(getattr(logging, log_level.upper()))
        else:
            logger.setLevel(logging.INFO)  # 默认级别
        
        # 创建格式化器
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # 添加控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # 如果配置了日志文件，添加文件处理器
        log_file = getattr(self.config, 'log_file', None)
        if log_file and isinstance(log_file, str):
            try:
                file_handler = logging.FileHandler(log_file)
                file_handler.setFormatter(formatter)
                logger.addHandler(file_handler)
            except Exception as e:
                logger.warning(f"无法创建日志文件处理器: {e}")
        
        return logger
    
    async def handle_with_retry(self, func: Callable, *args, **kwargs):
        """
        带重试的错误处理
        
        Args:
            func: 要执行的函数
            *args: 函数参数
            **kwargs: 函数关键字参数
            
        Returns:
            函数执行结果
        """
        import asyncio
        
        last_error = None
        retry_count = 0
        start_time = time.time()
        
        for attempt in range(self.config.max_retries + 1):
            try:
                result = await func(*args, **kwargs)
                
                # 更新统计信息（成功）
                if last_error:
                    self._update_error_stats(last_error, attempt, True)
                    execution_time = time.time() - start_time
                    self.logger.info(
                        f"函数 {func.__name__} 在第{attempt + 1}次尝试后成功，"
                        f"总耗时: {execution_time:.2f}秒"
                    )
                
                return result
                
            except Exception as error:
                last_error = error
                
                # 记录错误
                context = {
                    'attempt': attempt + 1,
                    'max_retries': self.config.max_retries,
                    'function': func.__name__,
                    'args': str(args)[:100],  # 限制长度避免日志过长
                    'kwargs': str(kwargs)[:100],
                    'execution_time': time.time() - start_time
                }
                self.log_error(error, context)
                
                # 跟踪速率限制
                if isinstance(error, RateLimitError):
                    provider = kwargs.get('provider', 'unknown')
                    self._track_rate_limit(provider, error)
                
                # 判断是否应该停止重试
                if self._should_stop_retrying(error, attempt):
                    break
                
                # 判断是否应该重试
                if self.should_retry(error):
                    # 计算延迟时间
                    delay = self._calculate_retry_delay(attempt, error)
                    self.logger.info(
                        f"第{attempt + 1}次尝试失败，{delay:.2f}秒后重试: {error}"
                    )
                    await asyncio.sleep(delay)
                    continue
                else:
                    # 不应该重试，直接退出
                    break
        
        # 更新统计信息（失败）
        self._update_error_stats(last_error, attempt, False)
        
        # 所有重试都失败了，抛出最后的异常
        raise last_error
        
    def should_retry(self, error: Exception) -> bool:
        """
        判断是否应该重试
        
        Args:
            error: 异常对象
            
        Returns:
            是否应该重试
        """
        # 网络相关错误应该重试
        if isinstance(error, (NetworkError, ConnectionError, TimeoutError)):
            return True
        
        # 数据源临时错误应该重试
        if isinstance(error, DataSourceError):
            # 检查错误消息中是否包含临时性错误的关键词
            error_msg = str(error).lower()
            temporary_keywords = [
                'timeout', 'connection', 'network', 'temporary', 
                'server error', '502', '503', '504'
            ]
            return any(keyword in error_msg for keyword in temporary_keywords)
        
        # 速率限制错误应该重试
        if isinstance(error, RateLimitError):
            return True
        
        # 缓存错误可以重试
        if isinstance(error, CacheError):
            return True
        
        # 参数验证错误不应该重试
        if isinstance(error, ValidationError):
            return False
        
        # 其他未知错误，默认不重试
        return False
        
    def log_error(self, error: Exception, context: Dict[str, Any]):
        """
        记录错误信息
        
        Args:
            error: 异常对象
            context: 错误上下文信息
        """
        error_info = {
            'error_type': type(error).__name__,
            'error_message': str(error),
            'context': context
        }
        
        # 如果是QuickStockError，记录额外信息
        if isinstance(error, QuickStockError):
            error_info.update({
                'error_code': error.error_code,
                'details': error.details
            })
        
        # 根据错误类型选择日志级别
        if isinstance(error, (ValidationError,)):
            self.logger.warning(f"参数验证错误: {error_info}")
        elif isinstance(error, (NetworkError, DataSourceError)):
            self.logger.error(f"数据获取错误: {error_info}")
        elif isinstance(error, CacheError):
            self.logger.warning(f"缓存错误: {error_info}")
        else:
            self.logger.error(f"未知错误: {error_info}")
    
    def create_error(self, error_type: str, message: str, 
                    error_code: str = None, details: Dict[str, Any] = None) -> QuickStockError:
        """
        创建特定类型的错误
        
        Args:
            error_type: 错误类型
            message: 错误消息
            error_code: 错误代码
            details: 错误详细信息
            
        Returns:
            对应的异常对象
        """
        error_classes = {
            'data_source': DataSourceError,
            'cache': CacheError,
            'validation': ValidationError,
            'rate_limit': RateLimitError,
            'network': NetworkError
        }
        
        error_class = error_classes.get(error_type, QuickStockError)
        return error_class(message, error_code, details)
    
    def get_error_stats(self) -> Dict[str, Any]:
        """
        获取错误统计信息
        
        Returns:
            错误统计数据
        """
        return self._error_stats.copy()
    
    def reset_error_stats(self):
        """重置错误统计"""
        self._error_stats = {
            'total_errors': 0,
            'retry_attempts': 0,
            'successful_retries': 0,
            'failed_retries': 0,
            'error_types': {}
        }
        self._rate_limit_tracker.clear()
    
    def _update_error_stats(self, error: Exception, retry_count: int, success: bool):
        """
        更新错误统计信息
        
        Args:
            error: 异常对象
            retry_count: 重试次数
            success: 是否最终成功
        """
        self._error_stats['total_errors'] += 1
        self._error_stats['retry_attempts'] += retry_count
        
        if success and retry_count > 0:
            self._error_stats['successful_retries'] += 1
        elif not success and retry_count > 0:
            self._error_stats['failed_retries'] += 1
        
        # 统计错误类型
        error_type = type(error).__name__
        self._error_stats['error_types'][error_type] = (
            self._error_stats['error_types'].get(error_type, 0) + 1
        )
    
    def _calculate_retry_delay(self, attempt: int, error: Exception) -> float:
        """
        计算重试延迟时间
        
        Args:
            attempt: 当前尝试次数（从0开始）
            error: 异常对象
            
        Returns:
            延迟时间（秒）
        """
        base_delay = self.config.retry_delay
        
        # 对于速率限制错误，使用更长的延迟
        if isinstance(error, RateLimitError):
            # 检查是否有速率限制信息
            if hasattr(error, 'details') and error.details:
                retry_after = error.details.get('retry_after')
                if retry_after:
                    return float(retry_after)
            
            # 默认使用更长的延迟
            base_delay = max(base_delay, 5.0)
        
        # 指数退避，但有最大限制
        delay = base_delay * (2 ** attempt)
        max_delay = 60.0  # 默认最大延迟60秒
        
        return min(delay, max_delay)
    
    def _should_stop_retrying(self, error: Exception, attempt: int) -> bool:
        """
        判断是否应该停止重试
        
        Args:
            error: 异常对象
            attempt: 当前尝试次数
            
        Returns:
            是否应该停止重试
        """
        # 达到最大重试次数
        if attempt >= self.config.max_retries:
            return True
        
        # 对于某些错误类型，立即停止重试
        if isinstance(error, ValidationError):
            return True
        
        # 对于认证错误，不重试
        if isinstance(error, DataSourceError):
            error_msg = str(error).lower()
            auth_keywords = ['authentication', 'unauthorized', 'invalid token', 'api key']
            if any(keyword in error_msg for keyword in auth_keywords):
                return True
        
        return False
    
    def _track_rate_limit(self, provider: str, error: RateLimitError):
        """
        跟踪速率限制信息
        
        Args:
            provider: 数据提供者名称
            error: 速率限制错误
        """
        now = datetime.now()
        
        if provider not in self._rate_limit_tracker:
            self._rate_limit_tracker[provider] = {
                'last_error': now,
                'error_count': 0,
                'reset_time': None
            }
        
        tracker = self._rate_limit_tracker[provider]
        tracker['last_error'] = now
        tracker['error_count'] += 1
        
        # 如果错误包含重置时间信息
        if hasattr(error, 'details') and error.details:
            reset_after = error.details.get('reset_after')
            if reset_after:
                tracker['reset_time'] = now + timedelta(seconds=float(reset_after))
    
    def is_rate_limited(self, provider: str) -> bool:
        """
        检查指定提供者是否仍在速率限制中
        
        Args:
            provider: 数据提供者名称
            
        Returns:
            是否仍在速率限制中
        """
        if provider not in self._rate_limit_tracker:
            return False
        
        tracker = self._rate_limit_tracker[provider]
        reset_time = tracker.get('reset_time')
        
        if reset_time and datetime.now() < reset_time:
            return True
        
        return False