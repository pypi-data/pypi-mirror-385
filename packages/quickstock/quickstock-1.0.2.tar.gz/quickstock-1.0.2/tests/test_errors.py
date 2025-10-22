"""
错误处理模块的单元测试
"""

import pytest
import asyncio
import logging
from unittest.mock import Mock, patch, AsyncMock
from quickstock.core.errors import (
    QuickStockError, DataSourceError, CacheError, ValidationError,
    RateLimitError, NetworkError, ErrorHandler
)
from quickstock.config import Config


class TestQuickStockError:
    """测试QuickStockError基础异常类"""
    
    def test_basic_error_creation(self):
        """测试基础错误创建"""
        error = QuickStockError("测试错误")
        assert str(error) == "测试错误"
        assert error.message == "测试错误"
        assert error.error_code is None
        assert error.details == {}
    
    def test_error_with_code_and_details(self):
        """测试带错误码和详细信息的错误"""
        details = {"param": "value", "context": "test"}
        error = QuickStockError("测试错误", "E001", details)
        
        assert error.message == "测试错误"
        assert error.error_code == "E001"
        assert error.details == details
    
    def test_error_inheritance(self):
        """测试错误继承关系"""
        assert issubclass(DataSourceError, QuickStockError)
        assert issubclass(CacheError, QuickStockError)
        assert issubclass(ValidationError, QuickStockError)
        assert issubclass(RateLimitError, QuickStockError)
        assert issubclass(NetworkError, QuickStockError)


class TestSpecificErrors:
    """测试具体的异常类"""
    
    def test_data_source_error(self):
        """测试数据源错误"""
        error = DataSourceError("数据源连接失败", "DS001", {"source": "tushare"})
        assert isinstance(error, QuickStockError)
        assert error.error_code == "DS001"
        assert error.details["source"] == "tushare"
    
    def test_cache_error(self):
        """测试缓存错误"""
        error = CacheError("缓存写入失败", "C001")
        assert isinstance(error, QuickStockError)
        assert error.error_code == "C001"
    
    def test_validation_error(self):
        """测试参数验证错误"""
        error = ValidationError("参数格式错误", "V001", {"param": "ts_code"})
        assert isinstance(error, QuickStockError)
        assert error.details["param"] == "ts_code"
    
    def test_rate_limit_error(self):
        """测试速率限制错误"""
        error = RateLimitError("请求频率过高", "R001")
        assert isinstance(error, QuickStockError)
        assert "请求频率过高" in str(error)
    
    def test_network_error(self):
        """测试网络错误"""
        error = NetworkError("网络连接超时", "N001")
        assert isinstance(error, QuickStockError)
        assert error.error_code == "N001"


class TestErrorHandler:
    """测试错误处理器"""
    
    @pytest.fixture
    def config(self):
        """创建测试配置"""
        return Config(
            max_retries=3,
            retry_delay=0.1  # 使用较短的延迟以加快测试
        )
    
    @pytest.fixture
    def error_handler(self, config):
        """创建错误处理器实例"""
        return ErrorHandler(config)
    
    def test_error_handler_initialization(self, config):
        """测试错误处理器初始化"""
        handler = ErrorHandler(config)
        assert handler.config == config
        assert isinstance(handler.logger, logging.Logger)
    
    def test_should_retry_network_errors(self, error_handler):
        """测试网络错误应该重试"""
        assert error_handler.should_retry(NetworkError("连接超时"))
        assert error_handler.should_retry(ConnectionError("连接失败"))
        assert error_handler.should_retry(TimeoutError("请求超时"))
    
    def test_should_retry_temporary_data_source_errors(self, error_handler):
        """测试临时性数据源错误应该重试"""
        assert error_handler.should_retry(DataSourceError("server error 502"))
        assert error_handler.should_retry(DataSourceError("connection timeout"))
        assert error_handler.should_retry(DataSourceError("temporary failure"))
        assert error_handler.should_retry(DataSourceError("503 service unavailable"))
    
    def test_should_not_retry_permanent_errors(self, error_handler):
        """测试永久性错误不应该重试"""
        assert not error_handler.should_retry(ValidationError("参数错误"))
        assert not error_handler.should_retry(DataSourceError("authentication failed"))
        assert not error_handler.should_retry(DataSourceError("invalid api key"))
    
    def test_should_retry_rate_limit_and_cache_errors(self, error_handler):
        """测试速率限制和缓存错误应该重试"""
        assert error_handler.should_retry(RateLimitError("请求过于频繁"))
        assert error_handler.should_retry(CacheError("缓存写入失败"))
    
    @pytest.mark.asyncio
    async def test_handle_with_retry_success_first_attempt(self, error_handler):
        """测试第一次尝试就成功的情况"""
        mock_func = AsyncMock(return_value="success")
        
        result = await error_handler.handle_with_retry(mock_func, "arg1", key="value")
        
        assert result == "success"
        assert mock_func.call_count == 1
        mock_func.assert_called_with("arg1", key="value")
    
    @pytest.mark.asyncio
    async def test_handle_with_retry_success_after_retries(self, error_handler):
        """测试重试后成功的情况"""
        mock_func = AsyncMock()
        # 前两次失败，第三次成功
        mock_func.side_effect = [
            NetworkError("连接失败"),
            NetworkError("连接失败"),
            "success"
        ]
        
        result = await error_handler.handle_with_retry(mock_func)
        
        assert result == "success"
        assert mock_func.call_count == 3
    
    @pytest.mark.asyncio
    async def test_handle_with_retry_all_attempts_fail(self, error_handler):
        """测试所有重试都失败的情况"""
        mock_func = AsyncMock()
        error = NetworkError("持续连接失败")
        mock_func.side_effect = error
        
        with pytest.raises(NetworkError) as exc_info:
            await error_handler.handle_with_retry(mock_func)
        
        assert str(exc_info.value) == "持续连接失败"
        # 应该尝试 max_retries + 1 次
        assert mock_func.call_count == error_handler.config.max_retries + 1
    
    @pytest.mark.asyncio
    async def test_handle_with_retry_no_retry_for_validation_error(self, error_handler):
        """测试参数验证错误不会重试"""
        mock_func = AsyncMock()
        error = ValidationError("参数格式错误")
        mock_func.side_effect = error
        
        with pytest.raises(ValidationError):
            await error_handler.handle_with_retry(mock_func)
        
        # 只应该尝试一次，不重试
        assert mock_func.call_count == 1
    
    @pytest.mark.asyncio
    async def test_exponential_backoff_delay(self, error_handler):
        """测试指数退避延迟"""
        mock_func = AsyncMock()
        mock_func.side_effect = NetworkError("连接失败")
        
        with patch('asyncio.sleep') as mock_sleep:
            with pytest.raises(NetworkError):
                await error_handler.handle_with_retry(mock_func)
            
            # 检查延迟时间是否符合指数退避
            expected_delays = [
                error_handler.config.retry_delay * (2 ** 0),  # 0.1
                error_handler.config.retry_delay * (2 ** 1),  # 0.2
                error_handler.config.retry_delay * (2 ** 2),  # 0.4
            ]
            
            assert mock_sleep.call_count == 3
            for i, call in enumerate(mock_sleep.call_args_list):
                assert call[0][0] == expected_delays[i]
    
    def test_log_error_basic(self, error_handler):
        """测试基础错误日志记录"""
        error = Exception("测试错误")
        context = {"test": "context"}
        
        with patch.object(error_handler.logger, 'error') as mock_log:
            error_handler.log_error(error, context)
            
            mock_log.assert_called_once()
            log_message = mock_log.call_args[0][0]
            assert "未知错误" in log_message
            assert "Exception" in log_message
    
    def test_log_error_quickstock_error(self, error_handler):
        """测试QuickStock错误的日志记录"""
        error = DataSourceError("数据源错误", "DS001", {"source": "test"})
        context = {"attempt": 1}
        
        with patch.object(error_handler.logger, 'error') as mock_log:
            error_handler.log_error(error, context)
            
            mock_log.assert_called_once()
            log_message = mock_log.call_args[0][0]
            assert "数据获取错误" in log_message
    
    def test_log_error_validation_warning(self, error_handler):
        """测试参数验证错误使用警告级别"""
        error = ValidationError("参数错误")
        context = {}
        
        with patch.object(error_handler.logger, 'warning') as mock_log:
            error_handler.log_error(error, context)
            
            mock_log.assert_called_once()
            log_message = mock_log.call_args[0][0]
            assert "参数验证错误" in log_message
    
    def test_create_error_data_source(self, error_handler):
        """测试创建数据源错误"""
        error = error_handler.create_error(
            "data_source", "连接失败", "DS001", {"source": "tushare"}
        )
        
        assert isinstance(error, DataSourceError)
        assert error.message == "连接失败"
        assert error.error_code == "DS001"
        assert error.details["source"] == "tushare"
    
    def test_create_error_cache(self, error_handler):
        """测试创建缓存错误"""
        error = error_handler.create_error("cache", "缓存失败", "C001")
        
        assert isinstance(error, CacheError)
        assert error.message == "缓存失败"
        assert error.error_code == "C001"
    
    def test_create_error_validation(self, error_handler):
        """测试创建验证错误"""
        error = error_handler.create_error("validation", "参数无效", "V001")
        
        assert isinstance(error, ValidationError)
        assert error.message == "参数无效"
        assert error.error_code == "V001"
    
    def test_create_error_rate_limit(self, error_handler):
        """测试创建速率限制错误"""
        error = error_handler.create_error("rate_limit", "请求过频", "R001")
        
        assert isinstance(error, RateLimitError)
        assert error.message == "请求过频"
        assert error.error_code == "R001"
    
    def test_create_error_network(self, error_handler):
        """测试创建网络错误"""
        error = error_handler.create_error("network", "网络超时", "N001")
        
        assert isinstance(error, NetworkError)
        assert error.message == "网络超时"
        assert error.error_code == "N001"
    
    def test_create_error_unknown_type(self, error_handler):
        """测试创建未知类型错误"""
        error = error_handler.create_error("unknown", "未知错误", "U001")
        
        assert isinstance(error, QuickStockError)
        assert not isinstance(error, (DataSourceError, CacheError, ValidationError))
        assert error.message == "未知错误"
        assert error.error_code == "U001"


class TestErrorHandlerIntegration:
    """错误处理器集成测试"""
    
    @pytest.fixture
    def config(self):
        """创建测试配置"""
        return Config(max_retries=2, retry_delay=0.01)
    
    @pytest.fixture
    def error_handler(self, config):
        """创建错误处理器实例"""
        return ErrorHandler(config)
    
    @pytest.mark.asyncio
    async def test_real_world_scenario_network_recovery(self, error_handler):
        """测试真实场景：网络恢复"""
        call_count = 0
        
        async def flaky_network_call():
            nonlocal call_count
            call_count += 1
            if call_count <= 2:
                raise NetworkError(f"网络错误 #{call_count}")
            return {"data": "success", "attempt": call_count}
        
        result = await error_handler.handle_with_retry(flaky_network_call)
        
        assert result["data"] == "success"
        assert result["attempt"] == 3
        assert call_count == 3
    
    @pytest.mark.asyncio
    async def test_real_world_scenario_rate_limit_recovery(self, error_handler):
        """测试真实场景：速率限制恢复"""
        call_count = 0
        
        async def rate_limited_call():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise RateLimitError("请求过于频繁，请稍后重试")
            return {"status": "ok", "call_count": call_count}
        
        result = await error_handler.handle_with_retry(rate_limited_call)
        
        assert result["status"] == "ok"
        assert result["call_count"] == 2
    
    @pytest.mark.asyncio
    async def test_real_world_scenario_permanent_failure(self, error_handler):
        """测试真实场景：永久性失败"""
        async def auth_failure():
            raise ValidationError("API密钥无效")
        
        with pytest.raises(ValidationError) as exc_info:
            await error_handler.handle_with_retry(auth_failure)
        
        assert "API密钥无效" in str(exc_info.value)


class TestErrorHandlerEnhancements:
    """测试错误处理器的增强功能"""
    
    @pytest.fixture
    def config(self):
        """创建测试配置"""
        return Config(
            max_retries=2,
            retry_delay=0.01,
            log_level='INFO'
        )
    
    @pytest.fixture
    def error_handler(self, config):
        """创建错误处理器实例"""
        return ErrorHandler(config)
    
    def test_error_stats_initialization(self, error_handler):
        """测试错误统计初始化"""
        stats = error_handler.get_error_stats()
        
        assert stats['total_errors'] == 0
        assert stats['retry_attempts'] == 0
        assert stats['successful_retries'] == 0
        assert stats['failed_retries'] == 0
        assert stats['error_types'] == {}
    
    @pytest.mark.asyncio
    async def test_error_stats_tracking(self, error_handler):
        """测试错误统计跟踪"""
        mock_func = AsyncMock()
        mock_func.side_effect = [
            NetworkError("网络错误"),
            "success"
        ]
        
        result = await error_handler.handle_with_retry(mock_func)
        
        stats = error_handler.get_error_stats()
        assert stats['total_errors'] == 1
        assert stats['retry_attempts'] == 1
        assert stats['successful_retries'] == 1
        assert stats['error_types']['NetworkError'] == 1
    
    def test_reset_error_stats(self, error_handler):
        """测试重置错误统计"""
        # 手动设置一些统计数据
        error_handler._error_stats['total_errors'] = 5
        error_handler._error_stats['error_types']['TestError'] = 3
        
        error_handler.reset_error_stats()
        
        stats = error_handler.get_error_stats()
        assert stats['total_errors'] == 0
        assert stats['error_types'] == {}
    
    def test_calculate_retry_delay_normal(self, error_handler):
        """测试普通错误的重试延迟计算"""
        error = NetworkError("网络错误")
        
        delay0 = error_handler._calculate_retry_delay(0, error)
        delay1 = error_handler._calculate_retry_delay(1, error)
        delay2 = error_handler._calculate_retry_delay(2, error)
        
        assert delay0 == 0.01  # base_delay
        assert delay1 == 0.02  # base_delay * 2
        assert delay2 == 0.04  # base_delay * 4
    
    def test_calculate_retry_delay_rate_limit(self, error_handler):
        """测试速率限制错误的重试延迟计算"""
        error = RateLimitError("请求过频", details={'retry_after': 10})
        
        delay = error_handler._calculate_retry_delay(0, error)
        assert delay == 10.0
    
    def test_calculate_retry_delay_max_limit(self, error_handler):
        """测试重试延迟的最大限制"""
        error = NetworkError("网络错误")
        
        # 使用更大的尝试次数来测试最大延迟限制
        # 0.01 * (2 ** 20) = 0.01 * 1048576 = 10485.76，应该被限制为60.0
        delay = error_handler._calculate_retry_delay(20, error)
        assert delay == 60.0  # 默认最大延迟
    
    def test_should_stop_retrying_validation_error(self, error_handler):
        """测试参数验证错误应该立即停止重试"""
        error = ValidationError("参数错误")
        
        assert error_handler._should_stop_retrying(error, 0)
        assert error_handler._should_stop_retrying(error, 1)
    
    def test_should_stop_retrying_auth_error(self, error_handler):
        """测试认证错误应该立即停止重试"""
        error = DataSourceError("authentication failed")
        
        assert error_handler._should_stop_retrying(error, 0)
    
    def test_should_stop_retrying_max_attempts(self, error_handler):
        """测试达到最大重试次数应该停止"""
        error = NetworkError("网络错误")
        
        assert not error_handler._should_stop_retrying(error, 0)
        assert not error_handler._should_stop_retrying(error, 1)
        assert error_handler._should_stop_retrying(error, 2)  # max_retries = 2
    
    def test_track_rate_limit(self, error_handler):
        """测试速率限制跟踪"""
        error = RateLimitError("请求过频", details={'reset_after': 60})
        
        error_handler._track_rate_limit('tushare', error)
        
        assert 'tushare' in error_handler._rate_limit_tracker
        tracker = error_handler._rate_limit_tracker['tushare']
        assert tracker['error_count'] == 1
        assert tracker['reset_time'] is not None
    
    def test_is_rate_limited(self, error_handler):
        """测试速率限制检查"""
        # 未跟踪的提供者不应该被限制
        assert not error_handler.is_rate_limited('unknown')
        
        # 添加速率限制跟踪
        from datetime import datetime, timedelta
        error_handler._rate_limit_tracker['test'] = {
            'last_error': datetime.now(),
            'error_count': 1,
            'reset_time': datetime.now() + timedelta(seconds=60)
        }
        
        assert error_handler.is_rate_limited('test')
    
    @pytest.mark.asyncio
    async def test_enhanced_retry_with_stats(self, error_handler):
        """测试增强的重试机制和统计"""
        call_count = 0
        
        async def test_func():
            nonlocal call_count
            call_count += 1
            if call_count <= 2:
                raise NetworkError(f"网络错误 #{call_count}")
            return "success"
        
        result = await error_handler.handle_with_retry(test_func)
        
        assert result == "success"
        
        stats = error_handler.get_error_stats()
        assert stats['total_errors'] == 1
        assert stats['retry_attempts'] == 2
        assert stats['successful_retries'] == 1
        assert stats['error_types']['NetworkError'] == 1


if __name__ == "__main__":
    pytest.main([__file__])