"""
QuickStock客户端测试

测试QuickStockClient的基础功能和API接口
"""

import pytest
import pandas as pd
from unittest.mock import Mock, patch, AsyncMock
import asyncio

from quickstock.client import QuickStockClient
from quickstock.config import Config
from quickstock.core.errors import QuickStockError, ValidationError
from quickstock.models import DataRequest


class TestQuickStockClient:
    """QuickStockClient测试类"""
    
    def setup_method(self):
        """测试前置设置"""
        # 创建测试配置
        self.test_config = Config(
            cache_enabled=False,  # 禁用缓存以简化测试
            log_level='ERROR'     # 减少日志输出
        )
        
        # 创建客户端实例
        self.client = QuickStockClient(self.test_config)
    
    def test_client_initialization(self):
        """测试客户端初始化"""
        # 测试正常初始化
        client = QuickStockClient()
        assert client._initialized is True
        assert client.config is not None
        assert client.data_manager is not None
        assert hasattr(client, 'logger')
        
        # 测试使用自定义配置初始化
        config = Config(cache_enabled=False)
        client_with_config = QuickStockClient(config)
        assert client_with_config.config == config
        assert client_with_config._initialized is True
    
    def test_client_initialization_failure(self):
        """测试客户端初始化失败"""
        with patch('quickstock.client.DataManager') as mock_dm:
            mock_dm.side_effect = Exception("初始化失败")
            
            with pytest.raises(QuickStockError, match="QuickStock客户端初始化失败"):
                QuickStockClient()
    
    def test_ensure_initialized(self):
        """测试初始化检查"""
        # 正常情况
        self.client._ensure_initialized()  # 不应抛出异常
        
        # 未初始化情况
        self.client._initialized = False
        with pytest.raises(QuickStockError, match="客户端未正确初始化"):
            self.client._ensure_initialized()
    
    def test_get_config(self):
        """测试获取配置"""
        config = self.client.get_config()
        assert config == self.test_config
    
    def test_update_config(self):
        """测试更新配置"""
        # 正常更新
        self.client.update_config(cache_enabled=True, max_retries=5)
        assert self.client.config.cache_enabled is True
        assert self.client.config.max_retries == 5
        
        # 无效参数
        with pytest.raises(ValidationError):
            self.client.update_config(invalid_param="test")
    
    def test_context_manager(self):
        """测试上下文管理器"""
        with QuickStockClient(self.test_config) as client:
            assert client._initialized is True
        # 退出时不应抛出异常
    
    def test_string_representation(self):
        """测试字符串表示"""
        str_repr = str(self.client)
        assert "QuickStockClient" in str_repr
        assert "initialized=True" in str_repr
        
        repr_str = repr(self.client)
        assert repr_str == str_repr


class TestStockAPI:
    """股票API测试类"""
    
    def setup_method(self):
        """测试前置设置"""
        self.test_config = Config(cache_enabled=False, log_level='ERROR')
        self.client = QuickStockClient(self.test_config)
        
        # Mock数据管理器
        self.mock_data_manager = Mock()
        self.client.data_manager = self.mock_data_manager
    
    @pytest.mark.asyncio
    async def test_stock_basic(self):
        """测试获取股票基础信息"""
        # 准备测试数据
        test_data = pd.DataFrame({
            'ts_code': ['000001.SZ', '000002.SZ'],
            'name': ['平安银行', '万科A'],
            'industry': ['银行', '房地产']
        })
        
        # Mock异步方法
        async def mock_get_data(request):
            return test_data
        
        self.mock_data_manager.get_data = mock_get_data
        
        # 测试调用
        result = self.client.stock_basic()
        
        # 验证结果
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2
        assert 'ts_code' in result.columns
    
    @pytest.mark.asyncio
    async def test_stock_daily(self):
        """测试获取股票日线数据"""
        # 准备测试数据
        test_data = pd.DataFrame({
            'ts_code': ['000001.SZ'] * 3,
            'trade_date': ['20240101', '20240102', '20240103'],
            'open': [10.0, 10.5, 11.0],
            'close': [10.5, 11.0, 10.8]
        })
        
        # Mock异步方法
        async def mock_get_data(request):
            assert request.data_type == 'stock_daily'
            assert request.ts_code == '000001.SZ'
            return test_data
        
        self.mock_data_manager.get_data = mock_get_data
        
        # 测试调用
        result = self.client.stock_daily('000001.SZ', '20240101', '20240103')
        
        # 验证结果
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 3
        assert 'trade_date' in result.columns
    
    def test_stock_daily_validation(self):
        """测试股票日线数据参数验证"""
        # 空股票代码
        with pytest.raises(QuickStockError, match="股票代码不能为空"):
            self.client.stock_daily('')
        
        # 无效股票代码格式
        with pytest.raises(QuickStockError, match="无效的股票代码格式"):
            self.client.stock_daily('invalid_code')
        
        # 无效日期格式
        with pytest.raises(QuickStockError, match="无效的日期格式"):
            self.client.stock_daily('000001.SZ', 'invalid_date')
    
    @pytest.mark.asyncio
    async def test_stock_minute(self):
        """测试获取股票分钟数据"""
        # 准备测试数据
        test_data = pd.DataFrame({
            'ts_code': ['000001.SZ'] * 2,
            'trade_time': ['09:30:00', '09:31:00'],
            'open': [10.0, 10.1],
            'close': [10.1, 10.2]
        })
        
        # Mock异步方法
        async def mock_get_data(request):
            assert request.data_type == 'stock_minute'
            assert request.freq == '1min'
            return test_data
        
        self.mock_data_manager.get_data = mock_get_data
        
        # 测试调用
        result = self.client.stock_minute('000001.SZ', '1min')
        
        # 验证结果
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2
    
    def test_stock_minute_validation(self):
        """测试股票分钟数据参数验证"""
        # 无效频率
        with pytest.raises(QuickStockError, match="频率参数无效"):
            self.client.stock_minute('000001.SZ', 'invalid_freq')
    
    @pytest.mark.asyncio
    async def test_stock_weekly(self):
        """测试获取股票周线数据"""
        test_data = pd.DataFrame({
            'ts_code': ['000001.SZ'],
            'trade_date': ['20240105'],
            'open': [10.0],
            'close': [10.5]
        })
        
        async def mock_get_data(request):
            assert request.data_type == 'stock_weekly'
            return test_data
        
        self.mock_data_manager.get_data = mock_get_data
        
        result = self.client.stock_weekly('000001.SZ')
        assert isinstance(result, pd.DataFrame)
    
    @pytest.mark.asyncio
    async def test_stock_monthly(self):
        """测试获取股票月线数据"""
        test_data = pd.DataFrame({
            'ts_code': ['000001.SZ'],
            'trade_date': ['20240131'],
            'open': [10.0],
            'close': [10.5]
        })
        
        async def mock_get_data(request):
            assert request.data_type == 'stock_monthly'
            return test_data
        
        self.mock_data_manager.get_data = mock_get_data
        
        result = self.client.stock_monthly('000001.SZ')
        assert isinstance(result, pd.DataFrame)


class TestIndexAPI:
    """指数API测试类"""
    
    def setup_method(self):
        """测试前置设置"""
        self.test_config = Config(cache_enabled=False, log_level='ERROR')
        self.client = QuickStockClient(self.test_config)
        
        # Mock数据管理器
        self.mock_data_manager = Mock()
        self.client.data_manager = self.mock_data_manager
    
    @pytest.mark.asyncio
    async def test_index_basic(self):
        """测试获取指数基础信息"""
        test_data = pd.DataFrame({
            'ts_code': ['000001.SH', '399001.SZ'],
            'name': ['上证指数', '深证成指'],
            'market': ['SSE', 'SZSE']
        })
        
        async def mock_get_data(request):
            assert request.data_type == 'index_basic'
            return test_data
        
        self.mock_data_manager.get_data = mock_get_data
        
        result = self.client.index_basic()
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2
    
    @pytest.mark.asyncio
    async def test_index_daily(self):
        """测试获取指数日线数据"""
        test_data = pd.DataFrame({
            'ts_code': ['000001.SH'] * 2,
            'trade_date': ['20240101', '20240102'],
            'open': [3000.0, 3010.0],
            'close': [3010.0, 3020.0]
        })
        
        async def mock_get_data(request):
            assert request.data_type == 'index_daily'
            return test_data
        
        self.mock_data_manager.get_data = mock_get_data
        
        result = self.client.index_daily('000001.SH')
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2
    
    @pytest.mark.asyncio
    async def test_index_weight(self):
        """测试获取指数成分股权重"""
        test_data = pd.DataFrame({
            'index_code': ['000001.SH'] * 2,
            'con_code': ['000001.SZ', '000002.SZ'],
            'weight': [5.0, 3.0]
        })
        
        async def mock_get_data(request):
            assert request.data_type == 'index_weight'
            return test_data
        
        self.mock_data_manager.get_data = mock_get_data
        
        result = self.client.index_weight('000001.SH')
        assert isinstance(result, pd.DataFrame)


class TestFundAPI:
    """基金API测试类"""
    
    def setup_method(self):
        """测试前置设置"""
        self.test_config = Config(cache_enabled=False, log_level='ERROR')
        self.client = QuickStockClient(self.test_config)
        
        # Mock数据管理器
        self.mock_data_manager = Mock()
        self.client.data_manager = self.mock_data_manager
    
    @pytest.mark.asyncio
    async def test_fund_basic(self):
        """测试获取基金基础信息"""
        test_data = pd.DataFrame({
            'ts_code': ['110022.OF', '110023.OF'],
            'name': ['易方达消费', '易方达科技'],
            'fund_type': ['股票型', '股票型']
        })
        
        async def mock_get_data(request):
            assert request.data_type == 'fund_basic'
            return test_data
        
        self.mock_data_manager.get_data = mock_get_data
        
        result = self.client.fund_basic()
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2
    
    @pytest.mark.asyncio
    async def test_fund_nav(self):
        """测试获取基金净值数据"""
        test_data = pd.DataFrame({
            'ts_code': ['110022.OF'] * 2,
            'end_date': ['20240101', '20240102'],
            'unit_nav': [1.5, 1.52],
            'accum_nav': [2.0, 2.02]
        })
        
        async def mock_get_data(request):
            assert request.data_type == 'fund_nav'
            return test_data
        
        self.mock_data_manager.get_data = mock_get_data
        
        result = self.client.fund_nav('110022.OF')
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2
    
    @pytest.mark.asyncio
    async def test_fund_portfolio(self):
        """测试获取基金持仓数据"""
        test_data = pd.DataFrame({
            'ts_code': ['110022.OF'] * 2,
            'symbol': ['000001.SZ', '000002.SZ'],
            'mkv': [1000000, 800000],
            'amount': [100000, 80000]
        })
        
        async def mock_get_data(request):
            assert request.data_type == 'fund_portfolio'
            return test_data
        
        self.mock_data_manager.get_data = mock_get_data
        
        result = self.client.fund_portfolio('110022.OF')
        assert isinstance(result, pd.DataFrame)


class TestTradeCalendarAPI:
    """交易日历API测试类"""
    
    def setup_method(self):
        """测试前置设置"""
        self.test_config = Config(cache_enabled=False, log_level='ERROR')
        self.client = QuickStockClient(self.test_config)
        
        # Mock数据管理器
        self.mock_data_manager = Mock()
        self.client.data_manager = self.mock_data_manager
    
    @pytest.mark.asyncio
    async def test_trade_cal(self):
        """测试获取交易日历"""
        test_data = pd.DataFrame({
            'exchange': ['SSE', 'SSE', 'SSE'],
            'cal_date': ['20240101', '20240102', '20240103'],
            'is_open': [0, 1, 1]
        })
        
        async def mock_get_data(request):
            assert request.data_type == 'trade_cal'
            return test_data
        
        self.mock_data_manager.get_data = mock_get_data
        
        result = self.client.trade_cal()
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 3
    
    @pytest.mark.asyncio
    async def test_is_trade_date(self):
        """测试判断是否为交易日"""
        # Mock trade_cal方法
        def mock_trade_cal(*args, **kwargs):
            return pd.DataFrame({
                'exchange': ['SSE'],
                'cal_date': ['20240102'],
                'is_open': [1]
            })
        
        self.client.trade_cal = mock_trade_cal
        
        # 测试交易日
        result = self.client.is_trade_date('20240102')
        assert result is True
        
        # 测试非交易日
        def mock_trade_cal_holiday(*args, **kwargs):
            return pd.DataFrame({
                'exchange': ['SSE'],
                'cal_date': ['20240101'],
                'is_open': [0]
            })
        
        self.client.trade_cal = mock_trade_cal_holiday
        result = self.client.is_trade_date('20240101')
        assert result is False
        
        # 测试空结果
        def mock_trade_cal_empty(*args, **kwargs):
            return pd.DataFrame()
        
        self.client.trade_cal = mock_trade_cal_empty
        result = self.client.is_trade_date('20240101')
        assert result is False
    
    def test_is_trade_date_validation(self):
        """测试交易日判断参数验证"""
        # 空日期
        with pytest.raises(QuickStockError, match="日期不能为空"):
            self.client.is_trade_date('')
        
        # 无效日期格式
        with pytest.raises(QuickStockError, match="无效的日期格式"):
            self.client.is_trade_date('invalid_date')
    
    @pytest.mark.asyncio
    async def test_get_trade_dates(self):
        """测试获取交易日列表"""
        # Mock trade_cal方法
        def mock_trade_cal(*args, **kwargs):
            return pd.DataFrame({
                'exchange': ['SSE'] * 3,
                'cal_date': ['20240101', '20240102', '20240103'],
                'is_open': [0, 1, 1]
            })
        
        self.client.trade_cal = mock_trade_cal
        
        result = self.client.get_trade_dates('20240101', '20240103')
        assert isinstance(result, list)
        assert len(result) == 2
        assert '20240102' in result
        assert '20240103' in result
    
    @pytest.mark.asyncio
    async def test_get_prev_trade_date(self):
        """测试获取上一个交易日"""
        # Mock trade_cal方法
        def mock_trade_cal(*args, **kwargs):
            return pd.DataFrame({
                'exchange': ['SSE'] * 2,
                'cal_date': ['20240101', '20240102'],
                'is_open': [1, 1]
            }).sort_values('cal_date', ascending=False)
        
        self.client.trade_cal = mock_trade_cal
        
        result = self.client.get_prev_trade_date('20240103')
        assert result == '20240102'
    
    @pytest.mark.asyncio
    async def test_get_next_trade_date(self):
        """测试获取下一个交易日"""
        # Mock trade_cal方法
        def mock_trade_cal(*args, **kwargs):
            return pd.DataFrame({
                'exchange': ['SSE'] * 2,
                'cal_date': ['20240102', '20240103'],
                'is_open': [1, 1]
            }).sort_values('cal_date', ascending=True)
        
        self.client.trade_cal = mock_trade_cal
        
        result = self.client.get_next_trade_date('20240101')
        assert result == '20240102'


class TestClientUtilityMethods:
    """客户端工具方法测试类"""
    
    def setup_method(self):
        """测试前置设置"""
        self.test_config = Config(cache_enabled=False, log_level='ERROR')
        self.client = QuickStockClient(self.test_config)
        
        # Mock数据管理器
        self.mock_data_manager = Mock()
        self.client.data_manager = self.mock_data_manager
    
    def test_get_provider_stats(self):
        """测试获取数据源统计信息"""
        mock_stats = {'baostock': {'total_requests': 10, 'success_rate': 0.9}}
        self.mock_data_manager.source_manager.get_provider_stats.return_value = mock_stats
        
        result = self.client.get_provider_stats()
        assert result == mock_stats
    
    def test_get_provider_health(self):
        """测试获取数据源健康状态"""
        mock_health = {'baostock': {'is_healthy': True, 'last_check': '2024-01-01'}}
        self.mock_data_manager.source_manager.get_provider_health.return_value = mock_health
        
        result = self.client.get_provider_health()
        assert result == mock_health
    
    def test_get_cache_stats(self):
        """测试获取缓存统计信息"""
        mock_cache_stats = {'hit_rate': 0.8, 'total_size': 1000}
        self.mock_data_manager.get_cache_stats.return_value = mock_cache_stats
        
        result = self.client.get_cache_stats()
        assert result == mock_cache_stats
    
    def test_clear_cache(self):
        """测试清空缓存"""
        self.client.clear_cache()
        self.mock_data_manager.clear_cache.assert_called_once()
    
    def test_clear_expired_cache(self):
        """测试清理过期缓存"""
        self.client.clear_expired_cache()
        self.mock_data_manager.clear_expired_cache.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_health_check(self):
        """测试健康检查"""
        mock_health_results = {'baostock': True, 'eastmoney': False}
        
        # Mock异步方法
        async def mock_health_check_all():
            return mock_health_results
        
        self.mock_data_manager.source_manager.health_check_all = mock_health_check_all
        
        result = self.client.health_check()
        assert result == mock_health_results
    
    @pytest.mark.asyncio
    async def test_test_connection(self):
        """测试连接测试"""
        # 测试指定数据源
        async def mock_test_provider(provider_name):
            return provider_name == 'baostock'
        
        self.mock_data_manager.source_manager.test_provider = mock_test_provider
        
        result = self.client.test_connection('baostock')
        assert result is True
        
        result = self.client.test_connection('invalid_provider')
        assert result is False
        
        # 测试所有数据源
        def mock_health_check():
            return {'baostock': True, 'eastmoney': False}
        
        self.client.health_check = mock_health_check
        
        result = self.client.test_connection()
        assert result is True


class TestCodeConversionMethods:
    """代码转换方法测试类"""
    
    def setup_method(self):
        """测试前置设置"""
        self.test_config = Config(cache_enabled=False, log_level='ERROR')
        self.client = QuickStockClient(self.test_config)
    
    def test_normalize_code(self):
        """测试标准化股票代码"""
        # 测试标准格式
        result = self.client.normalize_code('000001.SZ')
        assert result == '000001.SZ'
        
        # 测试Baostock格式
        result = self.client.normalize_code('sz.000001')
        assert result == '000001.SZ'
        
        # 测试东方财富格式
        result = self.client.normalize_code('0.000001')
        assert result == '000001.SZ'
        
        # 测试同花顺格式
        result = self.client.normalize_code('hs_000001')
        assert result == '000001.SZ'
        
        # 测试纯数字格式
        result = self.client.normalize_code('000001')
        assert result == '000001.SZ'
        
        result = self.client.normalize_code('600000')
        assert result == '600000.SH'
    
    def test_convert_code(self):
        """测试转换股票代码格式"""
        # 转换为Baostock格式
        result = self.client.convert_code('000001.SZ', 'baostock')
        assert result == 'sz.000001'
        
        result = self.client.convert_code('600000.SH', 'baostock')
        assert result == 'sh.600000'
        
        # 转换为东方财富格式
        result = self.client.convert_code('000001.SZ', 'eastmoney')
        assert result == '0.000001'
        
        result = self.client.convert_code('600000.SH', 'eastmoney')
        assert result == '1.600000'
        
        # 转换为同花顺格式
        result = self.client.convert_code('000001.SZ', 'tonghuashun')
        assert result == 'hs_000001'
        
        # 转换为标准格式
        result = self.client.convert_code('sz.000001', 'standard')
        assert result == '000001.SZ'
    
    def test_parse_code(self):
        """测试解析股票代码"""
        # 测试标准格式
        code, exchange = self.client.parse_code('000001.SZ')
        assert code == '000001'
        assert exchange == 'SZ'
        
        code, exchange = self.client.parse_code('600000.SH')
        assert code == '600000'
        assert exchange == 'SH'
        
        # 测试纯数字格式（需要推断交易所）
        code, exchange = self.client.parse_code('000001')
        assert code == '000001'
        assert exchange == 'SZ'
        
        code, exchange = self.client.parse_code('600000')
        assert code == '600000'
        assert exchange == 'SH'
        
        # 测试交易所前缀格式
        code, exchange = self.client.parse_code('SZ000001')
        assert code == '000001'
        assert exchange == 'SZ'
    
    def test_validate_code(self):
        """测试验证股票代码"""
        # 有效代码
        assert self.client.validate_code('000001.SZ') is True
        assert self.client.validate_code('600000.SH') is True
        assert self.client.validate_code('sz.000001') is True
        assert self.client.validate_code('1.600000') is True
        assert self.client.validate_code('hs_000001') is True
        assert self.client.validate_code('000001') is True
        
        # 无效代码
        assert self.client.validate_code('invalid') is False
        assert self.client.validate_code('') is False
        assert self.client.validate_code('123') is False
        assert self.client.validate_code('000001.XX') is False
    
    def test_get_supported_formats(self):
        """测试获取支持的格式列表"""
        formats = self.client.get_supported_formats()
        assert isinstance(formats, list)
        assert 'standard' in formats
        assert 'baostock' in formats
        assert 'eastmoney' in formats
        assert 'tonghuashun' in formats
        assert 'pure_number' in formats
        assert 'exchange_prefix' in formats
    
    def test_identify_code_format(self):
        """测试识别代码格式"""
        assert self.client.identify_code_format('000001.SZ') == 'standard'
        assert self.client.identify_code_format('sz.000001') == 'baostock'
        assert self.client.identify_code_format('0.000001') == 'eastmoney'
        assert self.client.identify_code_format('hs_000001') == 'tonghuashun'
        assert self.client.identify_code_format('000001') == 'pure_number'
        assert self.client.identify_code_format('SZ000001') == 'exchange_prefix'
        assert self.client.identify_code_format('invalid') is None
    
    def test_suggest_code_corrections(self):
        """测试代码修正建议"""
        suggestions = self.client.suggest_code_corrections('000001.sz')
        assert isinstance(suggestions, list)
        assert len(suggestions) > 0
        assert any('000001.SZ' in s for s in suggestions)
        
        suggestions = self.client.suggest_code_corrections('000001')
        assert isinstance(suggestions, list)
        assert len(suggestions) > 0
        
        suggestions = self.client.suggest_code_corrections('invalid')
        assert isinstance(suggestions, list)
        assert len(suggestions) > 0
    
    def test_batch_normalize_codes(self):
        """测试批量标准化代码"""
        codes = ['000001.SZ', 'sh.600000', '0.000002', 'hs_300001']
        results = self.client.batch_normalize_codes(codes)
        
        assert isinstance(results, list)
        assert len(results) == 4
        assert '000001.SZ' in results
        assert '600000.SH' in results
        assert '000002.SZ' in results
        assert '300001.SZ' in results
    
    def test_batch_convert_codes(self):
        """测试批量转换代码"""
        codes = ['000001.SZ', '600000.SH']
        results = self.client.batch_convert_codes(codes, 'baostock')
        
        assert isinstance(results, list)
        assert len(results) == 2
        assert 'sz.000001' in results
        assert 'sh.600000' in results
    
    def test_get_code_conversion_stats(self):
        """测试获取代码转换统计信息"""
        # 先执行一些转换操作以生成统计数据
        self.client.normalize_code('000001.SZ')
        self.client.convert_code('000001.SZ', 'baostock')
        
        stats = self.client.get_code_conversion_stats()
        assert isinstance(stats, dict)
        assert 'hit_rate' in stats
        assert 'size' in stats
        assert 'max_size' in stats
    
    def test_clear_code_conversion_cache(self):
        """测试清空代码转换缓存"""
        # 先执行一些转换操作
        self.client.normalize_code('000001.SZ')
        
        # 清空缓存
        self.client.clear_code_conversion_cache()
        
        # 验证缓存已清空
        stats = self.client.get_code_conversion_stats()
        assert stats['size'] == 0
    
    def test_code_conversion_error_handling(self):
        """测试代码转换错误处理"""
        # 测试无效代码
        with pytest.raises(ValidationError):
            self.client.normalize_code('')
        
        with pytest.raises(ValidationError):
            self.client.convert_code('invalid', 'baostock')
        
        with pytest.raises(ValidationError):
            self.client.convert_code('000001.SZ', 'invalid_format')
        
        # 测试批量处理中的错误
        codes = ['000001.SZ', 'invalid', '600000.SH']
        results = self.client.batch_normalize_codes(codes)
        # 应该返回有效的结果，跳过无效的代码
        assert len(results) == 2
        assert '000001.SZ' in results
        assert '600000.SH' in results


class TestAsyncHandling:
    """异步处理测试类"""
    
    def setup_method(self):
        """测试前置设置"""
        self.test_config = Config(cache_enabled=False, log_level='ERROR')
        self.client = QuickStockClient(self.test_config)
    
    def test_run_async_with_existing_loop(self):
        """测试在现有事件循环中运行异步方法"""
        async def test_coro():
            return "test_result"
        
        # 在同步环境中测试
        result = self.client._run_async(test_coro())
        assert result == "test_result"
    
    @pytest.mark.asyncio
    async def test_run_async_in_async_context(self):
        """测试在异步上下文中运行异步方法"""
        async def test_coro():
            return "async_result"
        
        # 在异步环境中，_run_async应该能正确处理协程
        result = self.client._run_async(test_coro())
        assert result == "async_result"


if __name__ == '__main__':
    pytest.main([__file__])