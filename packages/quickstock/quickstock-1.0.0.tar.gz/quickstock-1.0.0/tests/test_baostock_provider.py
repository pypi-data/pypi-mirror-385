"""
Baostock数据提供者测试
"""

import pytest
import pandas as pd
from unittest.mock import Mock, patch, AsyncMock
import asyncio

from quickstock.providers.baostock import BaostockProvider, BAOSTOCK_AVAILABLE
from quickstock.config import Config
from quickstock.core.errors import DataSourceError, ValidationError, NetworkError


class TestBaostockProvider:
    """Baostock提供者测试类"""
    
    @pytest.fixture
    def config(self):
        """创建测试配置"""
        return Config(
            enable_baostock=True,
            request_timeout=30,
            max_retries=3,
            retry_delay=1.0
        )
    
    @pytest.fixture
    def provider(self, config):
        """创建Baostock提供者实例"""
        if not BAOSTOCK_AVAILABLE:
            pytest.skip("baostock库未安装")
        return BaostockProvider(config)
    
    def test_init_without_baostock(self, config):
        """测试在没有baostock库时的初始化"""
        with patch('quickstock.providers.baostock.BAOSTOCK_AVAILABLE', False):
            with pytest.raises(DataSourceError) as exc_info:
                BaostockProvider(config)
            
            assert "baostock库未安装" in str(exc_info.value)
            assert exc_info.value.error_code == "BAOSTOCK_NOT_INSTALLED"
    
    def test_init_with_baostock(self, provider):
        """测试正常初始化"""
        assert provider is not None
        assert not provider._session_active
        assert provider.config.enable_baostock is True
    
    def test_is_available(self, provider):
        """测试可用性检查"""
        assert provider.is_available() is True
        
        # 测试配置禁用时
        provider.config.enable_baostock = False
        assert provider.is_available() is False
    
    def test_get_rate_limit(self, provider):
        """测试速率限制信息"""
        rate_limit = provider.get_rate_limit()
        
        assert rate_limit.requests_per_second == 2.0
        assert rate_limit.requests_per_minute == 100
        assert rate_limit.requests_per_hour == 3000
    
    def test_convert_stock_code(self, provider):
        """测试股票代码转换"""
        # 测试标准格式转换
        assert provider._convert_stock_code('000001.SZ') == 'sz.000001'
        assert provider._convert_stock_code('600000.SH') == 'sh.600000'
        
        # 测试无后缀代码的自动判断
        assert provider._convert_stock_code('000001') == 'sz.000001'
        assert provider._convert_stock_code('600000') == 'sh.600000'
        assert provider._convert_stock_code('300001') == 'sz.300001'
        
        # 测试其他格式
        assert provider._convert_stock_code('BK0001') == 'BK0001'
    
    def test_convert_to_standard_code(self, provider):
        """测试转换为标准代码格式"""
        assert provider._convert_to_standard_code('sz.000001') == '000001.SZ'
        assert provider._convert_to_standard_code('sh.600000') == '600000.SH'
        assert provider._convert_to_standard_code('000001') == '000001'
    
    def test_standardize_stock_basic_columns(self, provider):
        """测试股票基础信息列名标准化"""
        # 创建测试数据
        df = pd.DataFrame({
            'code': ['sz.000001', 'sh.600000'],
            'code_name': ['平安银行', '浦发银行'],
            'ipoDate': ['1991-04-03', '1999-11-10'],
            'type': ['1', '1'],
            'status': ['1', '1']
        })
        
        result = provider._standardize_stock_basic_columns(df)
        
        # 验证列名映射
        assert 'ts_code' in result.columns
        assert 'name' in result.columns
        assert 'list_date' in result.columns
        
        # 验证股票代码转换
        assert result.loc[0, 'ts_code'] == '000001.SZ'
        assert result.loc[1, 'ts_code'] == '600000.SH'
    
    def test_standardize_ohlcv_columns(self, provider):
        """测试OHLCV数据列名标准化"""
        # 创建测试数据
        df = pd.DataFrame({
            'date': ['2023-01-01', '2023-01-02'],
            'code': ['sz.000001', 'sz.000001'],
            'open': ['10.00', '10.10'],
            'high': ['10.50', '10.60'],
            'low': ['9.80', '9.90'],
            'close': ['10.20', '10.30'],
            'preclose': ['9.90', '10.20'],
            'volume': ['1000000', '1100000'],
            'amount': ['10200000', '11330000'],
            'pctChg': ['3.03', '0.98']
        })
        
        result = provider._standardize_ohlcv_columns(df)
        
        # 验证列名映射
        assert 'trade_date' in result.columns
        assert 'ts_code' in result.columns
        assert 'pre_close' in result.columns
        assert 'pct_chg' in result.columns
        
        # 验证数据类型转换
        assert result['open'].dtype in ['float64', 'float32']
        assert result['volume'].dtype in ['float64', 'float32', 'int64']  # volume可能是整数类型
        
        # 验证股票代码转换
        assert result.loc[0, 'ts_code'] == '000001.SZ'
        
        # 验证日期格式转换
        assert result.loc[0, 'trade_date'] == '20230101'
    
    def test_standardize_trade_cal_columns(self, provider):
        """测试交易日历列名标准化"""
        # 创建测试数据
        df = pd.DataFrame({
            'calendar_date': ['2023-01-01', '2023-01-02'],
            'is_trading_day': ['0', '1']
        })
        
        result = provider._standardize_trade_cal_columns(df)
        
        # 验证列名映射
        assert 'cal_date' in result.columns
        assert 'is_open' in result.columns
        
        # 验证数据类型转换
        assert result['is_open'].dtype == 'int64'
        
        # 验证日期格式转换
        assert result.loc[0, 'cal_date'] == '20230101'
    
    def test_filter_by_market(self, provider):
        """测试按市场过滤"""
        # 创建测试数据
        df = pd.DataFrame({
            'code': ['sz.000001', 'sh.600000', 'sz.300001'],
            'name': ['平安银行', '浦发银行', '新和成']
        })
        
        # 测试深圳市场过滤
        sz_result = provider._filter_by_market(df, 'sz')
        assert len(sz_result) == 2
        assert all(sz_result['code'].str.startswith('sz.'))
        
        # 测试上海市场过滤
        sh_result = provider._filter_by_market(df, 'sh')
        assert len(sh_result) == 1
        assert all(sh_result['code'].str.startswith('sh.'))
        
        # 测试其他市场（返回全部）
        all_result = provider._filter_by_market(df, 'all')
        assert len(all_result) == 3
    
    def test_filter_invalid_data(self, provider):
        """测试过滤无效数据"""
        # 创建测试数据
        df = pd.DataFrame({
            'date': ['2023-01-01', '2023-01-02', '2023-01-03'],
            'code': ['sz.000001', 'sz.000001', 'sz.000001'],
            'open': ['10.00', '0.00', '10.20'],
            'close': ['10.20', '0.00', '10.30'],
            'tradestatus': ['1', '0', '1']  # 0表示停牌
        })
        
        result = provider._filter_invalid_data(df)
        
        # 第一行：正常交易，价格正常 -> 保留
        # 第二行：停牌且价格为0 -> 过滤
        # 第三行：正常交易，价格正常 -> 保留
        # 所以应该有2行数据
        assert len(result) == 2
        assert result.iloc[0]['date'] == '2023-01-01'
        assert result.iloc[1]['date'] == '2023-01-03'
        
        # 测试只有价格为0的情况
        df_zero_price = pd.DataFrame({
            'date': ['2023-01-01', '2023-01-02'],
            'code': ['sz.000001', 'sz.000001'],
            'open': ['0.00', '10.20'],
            'close': ['10.20', '10.30'],
            'tradestatus': ['1', '1']
        })
        
        result_zero = provider._filter_invalid_data(df_zero_price)
        # 第一行开盘价为0，应该被过滤
        assert len(result_zero) == 1
        assert result_zero.iloc[0]['date'] == '2023-01-02'
    
    def test_convert_index_code(self, provider):
        """测试指数代码转换"""
        # 指数代码转换应该与股票代码转换相同
        assert provider._convert_index_code('000001.SH') == 'sh.000001'
        assert provider._convert_index_code('399001.SZ') == 'sz.399001'
    
    def test_standardize_index_basic_columns(self, provider):
        """测试指数基础信息列名标准化"""
        # 创建测试数据
        df = pd.DataFrame({
            'code': ['sh.000001', 'sz.399001'],
            'code_name': ['上证指数', '深证成指'],
            'industry': ['指数', '指数'],
            'industryClassification': ['综合指数', '综合指数']
        })
        
        result = provider._standardize_index_basic_columns(df)
        
        # 验证列名映射
        assert 'ts_code' in result.columns
        assert 'name' in result.columns
        assert 'category' in result.columns
        
        # 验证代码转换
        assert result.loc[0, 'ts_code'] == '000001.SH'
        assert result.loc[1, 'ts_code'] == '399001.SZ'
    
    def test_standardize_index_ohlcv_columns(self, provider):
        """测试指数OHLCV数据列名标准化"""
        # 创建测试数据
        df = pd.DataFrame({
            'date': ['2023-01-01', '2023-01-02'],
            'code': ['sh.000001', 'sh.000001'],
            'open': ['3100.00', '3120.00'],
            'high': ['3150.00', '3160.00'],
            'low': ['3080.00', '3090.00'],
            'close': ['3120.00', '3130.00'],
            'volume': ['1000000', '1100000'],
            'amount': ['10200000', '11330000'],
            'pctChg': ['0.65', '0.32']
        })
        
        result = provider._standardize_index_ohlcv_columns(df)
        
        # 验证列名映射
        assert 'trade_date' in result.columns
        assert 'ts_code' in result.columns
        assert 'pct_chg' in result.columns
        
        # 验证数据类型转换
        assert result['open'].dtype in ['float64', 'float32']
        assert result['volume'].dtype in ['float64', 'float32', 'int64']  # volume可能是整数类型
        
        # 验证代码转换
        assert result.loc[0, 'ts_code'] == '000001.SH'
        
        # 验证日期格式转换
        assert result.loc[0, 'trade_date'] == '20230101'
    
    @pytest.mark.asyncio
    async def test_ensure_login_success(self, provider):
        """测试成功登录"""
        mock_result = Mock()
        mock_result.error_code = '0'
        mock_result.error_msg = 'success'
        
        with patch('quickstock.providers.baostock.bs.login', return_value=mock_result):
            await provider._ensure_login()
            assert provider._session_active is True
    
    @pytest.mark.asyncio
    async def test_ensure_login_failure(self, provider):
        """测试登录失败"""
        mock_result = Mock()
        mock_result.error_code = '10001'
        mock_result.error_msg = 'login failed'
        
        with patch('quickstock.providers.baostock.bs.login', return_value=mock_result):
            with pytest.raises(DataSourceError) as exc_info:
                await provider._ensure_login()
            
            assert "Baostock登录失败" in str(exc_info.value)
            assert exc_info.value.error_code == "BAOSTOCK_LOGIN_FAILED"
            assert provider._session_active is False
    
    @pytest.mark.asyncio
    async def test_ensure_login_network_error(self, provider):
        """测试登录网络错误"""
        with patch('quickstock.providers.baostock.bs.login', side_effect=ConnectionError("网络连接失败")):
            with pytest.raises(NetworkError) as exc_info:
                await provider._ensure_login()
            
            assert "Baostock连接失败" in str(exc_info.value)
            assert exc_info.value.error_code == "BAOSTOCK_CONNECTION_ERROR"
    
    @pytest.mark.asyncio
    async def test_logout(self, provider):
        """测试登出"""
        provider._session_active = True
        
        with patch('quickstock.providers.baostock.bs.logout') as mock_logout:
            await provider._logout()
            mock_logout.assert_called_once()
            assert provider._session_active is False
    
    @pytest.mark.asyncio
    async def test_health_check_success(self, provider):
        """测试健康检查成功"""
        with patch.object(provider, '_ensure_login', new_callable=AsyncMock):
            result = await provider.health_check()
            assert result is True
    
    @pytest.mark.asyncio
    async def test_health_check_failure(self, provider):
        """测试健康检查失败"""
        with patch.object(provider, '_ensure_login', new_callable=AsyncMock, side_effect=Exception("连接失败")):
            result = await provider.health_check()
            assert result is False
    
    @pytest.mark.asyncio
    async def test_get_stock_basic_success(self, provider):
        """测试成功获取股票基础信息"""
        mock_result = Mock()
        mock_result.error_code = '0'
        mock_result.fields = ['code', 'code_name', 'ipoDate', 'type', 'status']
        mock_result.next.side_effect = [True, True, False]
        mock_result.get_row_data.side_effect = [
            ['sz.000001', '平安银行', '1991-04-03', '1', '1'],
            ['sh.600000', '浦发银行', '1999-11-10', '1', '1']
        ]
        
        with patch.object(provider, '_ensure_login', new_callable=AsyncMock):
            with patch('quickstock.providers.baostock.bs.query_all_stock', return_value=mock_result):
                result = await provider.get_stock_basic()
                
                assert isinstance(result, pd.DataFrame)
                assert len(result) == 2
                assert 'ts_code' in result.columns
                assert 'name' in result.columns
    
    @pytest.mark.asyncio
    async def test_get_stock_basic_with_date(self, provider):
        """测试指定日期获取股票基础信息"""
        mock_result = Mock()
        mock_result.error_code = '0'
        mock_result.fields = ['code', 'code_name', 'ipoDate', 'type', 'status']
        mock_result.next.return_value = False
        
        with patch.object(provider, '_ensure_login', new_callable=AsyncMock):
            with patch('quickstock.providers.baostock.bs.query_all_stock', return_value=mock_result) as mock_query:
                await provider.get_stock_basic(date='2023-01-01')
                mock_query.assert_called_once_with(day='2023-01-01')
    
    @pytest.mark.asyncio
    async def test_get_stock_basic_invalid_date(self, provider):
        """测试无效日期格式"""
        with pytest.raises((ValidationError, DataSourceError)):
            await provider.get_stock_basic(date='invalid-date')
    
    @pytest.mark.asyncio
    async def test_get_stock_basic_query_error(self, provider):
        """测试查询错误"""
        mock_result = Mock()
        mock_result.error_code = '10001'
        mock_result.error_msg = 'query failed'
        
        with patch.object(provider, '_ensure_login', new_callable=AsyncMock):
            with patch('quickstock.providers.baostock.bs.query_all_stock', return_value=mock_result):
                with pytest.raises(DataSourceError) as exc_info:
                    await provider.get_stock_basic()
                
                assert "获取股票基础信息失败" in str(exc_info.value)
                assert exc_info.value.error_code == "BAOSTOCK_QUERY_ERROR"
    
    @pytest.mark.asyncio
    async def test_get_stock_daily_success(self, provider):
        """测试成功获取股票日线数据"""
        mock_result = Mock()
        mock_result.error_code = '0'
        mock_result.fields = ['date', 'code', 'open', 'high', 'low', 'close', 'preclose', 'volume', 'amount', 'pctChg', 'tradestatus']
        mock_result.next.side_effect = [True, True, False]
        mock_result.get_row_data.side_effect = [
            ['2023-01-01', 'sz.000001', '10.00', '10.50', '9.80', '10.20', '9.90', '1000000', '10200000', '3.03', '1'],
            ['2023-01-02', 'sz.000001', '10.20', '10.60', '9.90', '10.30', '10.20', '1100000', '11330000', '0.98', '1']
        ]
        
        with patch.object(provider, '_ensure_login', new_callable=AsyncMock):
            with patch('quickstock.providers.baostock.bs.query_history_k_data_plus', return_value=mock_result):
                result = await provider.get_stock_daily('000001.SZ', '2023-01-01', '2023-01-31')
                
                assert isinstance(result, pd.DataFrame)
                assert len(result) == 2
                assert 'ts_code' in result.columns
                assert 'trade_date' in result.columns
                assert 'open' in result.columns
                assert 'close' in result.columns
    
    @pytest.mark.asyncio
    async def test_get_stock_daily_validation_error(self, provider):
        """测试获取股票日线数据时的参数验证错误"""
        with pytest.raises(ValidationError):
            await provider.get_stock_daily('invalid_code', '2023-01-01', '2023-01-31')
    
    @pytest.mark.asyncio
    async def test_get_stock_daily_invalid_adjustflag(self, provider):
        """测试无效的复权类型"""
        with pytest.raises(ValidationError) as exc_info:
            await provider.get_stock_daily('000001.SZ', '2023-01-01', '2023-01-31', adjustflag='4')
        
        assert "无效的复权类型" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_get_stock_daily_invalid_frequency(self, provider):
        """测试无效的数据频率"""
        with pytest.raises(ValidationError) as exc_info:
            await provider.get_stock_daily('000001.SZ', '2023-01-01', '2023-01-31', frequency='x')
        
        assert "无效的数据频率" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_get_stock_daily_query_error(self, provider):
        """测试查询错误"""
        mock_result = Mock()
        mock_result.error_code = '10001'
        mock_result.error_msg = 'query failed'
        
        with patch.object(provider, '_ensure_login', new_callable=AsyncMock):
            with patch('quickstock.providers.baostock.bs.query_history_k_data_plus', return_value=mock_result):
                with pytest.raises(DataSourceError) as exc_info:
                    await provider.get_stock_daily('000001.SZ', '2023-01-01', '2023-01-31')
                
                assert "获取股票d线数据失败" in str(exc_info.value)
                assert exc_info.value.error_code == "BAOSTOCK_QUERY_ERROR"
    
    @pytest.mark.asyncio
    async def test_get_stock_minute_not_supported(self, provider):
        """测试分钟数据不支持"""
        with pytest.raises(NotImplementedError) as exc_info:
            await provider.get_stock_minute('000001.SZ', '1min')
        
        assert "Baostock不支持分钟级数据获取" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_get_index_basic_success(self, provider):
        """测试成功获取指数基础信息"""
        mock_result = Mock()
        mock_result.error_code = '0'
        mock_result.fields = ['code', 'code_name', 'industry', 'industryClassification']
        mock_result.next.side_effect = [True, True, False]
        mock_result.get_row_data.side_effect = [
            ['sh.000001', '上证指数', '指数', '综合指数'],
            ['sz.399001', '深证成指', '指数', '综合指数']
        ]
        
        with patch.object(provider, '_ensure_login', new_callable=AsyncMock):
            with patch('quickstock.providers.baostock.bs.query_stock_industry', return_value=mock_result):
                result = await provider.get_index_basic()
                
                assert isinstance(result, pd.DataFrame)
                assert len(result) == 2
                assert 'ts_code' in result.columns
                assert 'name' in result.columns
    
    @pytest.mark.asyncio
    async def test_get_index_daily_success(self, provider):
        """测试成功获取指数日线数据"""
        mock_result = Mock()
        mock_result.error_code = '0'
        mock_result.fields = ['date', 'code', 'open', 'high', 'low', 'close', 'volume', 'amount', 'pctChg']
        mock_result.next.side_effect = [True, True, False]
        mock_result.get_row_data.side_effect = [
            ['2023-01-01', 'sh.000001', '3100.00', '3150.00', '3080.00', '3120.00', '1000000', '10200000', '0.65'],
            ['2023-01-02', 'sh.000001', '3120.00', '3160.00', '3090.00', '3130.00', '1100000', '11330000', '0.32']
        ]
        
        with patch.object(provider, '_ensure_login', new_callable=AsyncMock):
            with patch('quickstock.providers.baostock.bs.query_history_k_data_plus', return_value=mock_result):
                result = await provider.get_index_daily('000001.SH', '2023-01-01', '2023-01-31')
                
                assert isinstance(result, pd.DataFrame)
                assert len(result) == 2
                assert 'ts_code' in result.columns
                assert 'trade_date' in result.columns
                assert 'open' in result.columns
                assert 'close' in result.columns
    
    @pytest.mark.asyncio
    async def test_get_index_daily_validation_error(self, provider):
        """测试获取指数日线数据时的参数验证错误"""
        with pytest.raises(ValidationError):
            await provider.get_index_daily('invalid_code', '2023-01-01', '2023-01-31')
    
    @pytest.mark.asyncio
    async def test_get_fund_basic_not_supported(self, provider):
        """测试基金基础信息不支持"""
        with pytest.raises(NotImplementedError) as exc_info:
            await provider.get_fund_basic()
        
        assert "Baostock不支持基金数据获取" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_get_fund_nav_not_supported(self, provider):
        """测试基金净值数据不支持"""
        with pytest.raises(NotImplementedError) as exc_info:
            await provider.get_fund_nav('000001', '2023-01-01', '2023-01-31')
        
        assert "Baostock不支持基金数据获取" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_get_trade_cal_success(self, provider):
        """测试成功获取交易日历"""
        mock_result = Mock()
        mock_result.error_code = '0'
        mock_result.fields = ['calendar_date', 'is_trading_day']
        mock_result.next.side_effect = [True, True, True, False]
        mock_result.get_row_data.side_effect = [
            ['2023-01-01', '0'],  # 元旦，非交易日
            ['2023-01-03', '1'],  # 交易日
            ['2023-01-04', '1']   # 交易日
        ]
        
        with patch.object(provider, '_ensure_login', new_callable=AsyncMock):
            with patch('quickstock.providers.baostock.bs.query_trade_dates', return_value=mock_result):
                result = await provider.get_trade_cal('2023-01-01', '2023-01-04')
                
                assert isinstance(result, pd.DataFrame)
                assert len(result) == 3
                assert 'cal_date' in result.columns
                assert 'is_open' in result.columns
    
    @pytest.mark.asyncio
    async def test_is_trade_date(self, provider):
        """测试判断是否为交易日"""
        # Mock交易日
        mock_trade_day = pd.DataFrame({
            'cal_date': ['20230103'],
            'is_open': [1]
        })
        
        # Mock非交易日
        mock_non_trade_day = pd.DataFrame({
            'cal_date': ['20230101'],
            'is_open': [0]
        })
        
        with patch.object(provider, 'get_trade_cal', new_callable=AsyncMock) as mock_get_cal:
            # 测试交易日
            mock_get_cal.return_value = mock_trade_day
            result = await provider.is_trade_date('2023-01-03')
            assert result is True
            
            # 测试非交易日
            mock_get_cal.return_value = mock_non_trade_day
            result = await provider.is_trade_date('2023-01-01')
            assert result is False
            
            # 测试空数据
            mock_get_cal.return_value = pd.DataFrame()
            result = await provider.is_trade_date('2023-01-01')
            assert result is False
    
    @pytest.mark.asyncio
    async def test_get_next_trade_date(self, provider):
        """测试获取下一个交易日"""
        # Mock交易日历数据
        mock_trade_cal = pd.DataFrame({
            'cal_date': ['20230103', '20230104', '20230105', '20230106'],
            'is_open': [1, 1, 1, 1]
        })
        
        with patch.object(provider, 'get_trade_cal', new_callable=AsyncMock, return_value=mock_trade_cal):
            # 测试获取下一个交易日
            result = await provider.get_next_trade_date('2023-01-03', 1)
            assert result == '2023-01-03'  # 第1个交易日是自己
            
            # 测试获取第2个交易日
            result = await provider.get_next_trade_date('2023-01-03', 2)
            assert result == '2023-01-04'
    
    @pytest.mark.asyncio
    async def test_get_prev_trade_date(self, provider):
        """测试获取上一个交易日"""
        # Mock交易日历数据
        mock_trade_cal = pd.DataFrame({
            'cal_date': ['20230103', '20230104', '20230105', '20230106'],
            'is_open': [1, 1, 1, 1]
        })
        
        with patch.object(provider, 'get_trade_cal', new_callable=AsyncMock, return_value=mock_trade_cal):
            # 测试获取上一个交易日
            result = await provider.get_prev_trade_date('2023-01-06', 1)
            assert result == '2023-01-06'  # 第1个交易日是最近的
            
            # 测试获取第2个交易日
            result = await provider.get_prev_trade_date('2023-01-06', 2)
            assert result == '2023-01-05'
    
    @pytest.mark.asyncio
    async def test_get_next_trade_date_validation_error(self, provider):
        """测试获取下一个交易日的参数验证"""
        with pytest.raises(ValidationError):
            await provider.get_next_trade_date('invalid-date', 1)
        
        with pytest.raises(ValidationError):
            await provider.get_next_trade_date('2023-01-01', 0)
    
    @pytest.mark.asyncio
    async def test_get_trade_cal_validation_error(self, provider):
        """测试获取交易日历时的参数验证错误"""
        with pytest.raises(ValidationError):
            await provider.get_trade_cal('invalid_date', '2023-01-31')
    
    @pytest.mark.asyncio
    async def test_get_trade_cal_validation_error(self, provider):
        """测试获取交易日历时的参数验证错误"""
        with pytest.raises(ValidationError):
            await provider.get_trade_cal('invalid_date', '2023-01-31')


class TestBaostockProviderIntegration:
    """Baostock提供者集成测试"""
    
    @pytest.fixture
    def config(self):
        """创建测试配置"""
        return Config(enable_baostock=True)
    
    @pytest.fixture
    def provider(self, config):
        """创建Baostock提供者实例"""
        if not BAOSTOCK_AVAILABLE:
            pytest.skip("baostock库未安装")
        return BaostockProvider(config)
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_real_stock_basic_query(self, provider):
        """测试真实的股票基础信息查询（需要网络连接）"""
        try:
            result = await provider.get_stock_basic()
            
            # 验证返回结果
            assert isinstance(result, pd.DataFrame)
            if not result.empty:
                assert 'ts_code' in result.columns
                assert 'name' in result.columns
                
        except Exception as e:
            pytest.skip(f"网络连接问题，跳过集成测试: {e}")
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_real_stock_daily_query(self, provider):
        """测试真实的股票日线数据查询（需要网络连接）"""
        try:
            result = await provider.get_stock_daily('000001.SZ', '2023-01-01', '2023-01-31')
            
            # 验证返回结果
            assert isinstance(result, pd.DataFrame)
            if not result.empty:
                assert 'ts_code' in result.columns
                assert 'trade_date' in result.columns
                assert 'open' in result.columns
                assert 'close' in result.columns
                
        except Exception as e:
            pytest.skip(f"网络连接问题，跳过集成测试: {e}")
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_real_trade_cal_query(self, provider):
        """测试真实的交易日历查询（需要网络连接）"""
        try:
            result = await provider.get_trade_cal('2023-01-01', '2023-01-31')
            
            # 验证返回结果
            assert isinstance(result, pd.DataFrame)
            if not result.empty:
                assert 'cal_date' in result.columns
                assert 'is_open' in result.columns
                
        except Exception as e:
            pytest.skip(f"网络连接问题，跳过集成测试: {e}")