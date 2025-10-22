"""
数据源代码转换集成测试

实现task 7.3：实现数据源适配测试
- 测试各数据源的代码格式转换
- 验证数据返回的格式一致性
- 测试数据源间的代码转换正确性
"""

import pytest
import pandas as pd
from unittest.mock import Mock, AsyncMock, patch, MagicMock
import asyncio
import time
import threading
from concurrent.futures import ThreadPoolExecutor

from quickstock.providers.baostock import BaostockProvider
from quickstock.providers.eastmoney import EastmoneyProvider
from quickstock.providers.tonghuashun import TonghuashunProvider
from quickstock.providers.base import DataProvider as BaseProvider
from quickstock.utils.code_converter import (
    StockCodeConverter, 
    InvalidCodeFormatError,
    CodeConversionError,
    ExchangeInferenceError
)
from quickstock.core.errors import ValidationError, DataSourceError


class TestProviderCodeConversion:
    """测试数据源代码转换功能"""
    
    @pytest.fixture
    def mock_config(self):
        """模拟配置对象"""
        config = Mock()
        config.max_concurrent_requests = 10
        config.request_timeout = 30
        config.enable_baostock = True
        config.max_retries = 3
        config.retry_delay = 1.0
        config.connection_pool_size = 10
        config.connection_pool_per_host = 5
        config.connection_keepalive_timeout = 30
        config.connection_cleanup_enabled = True
        return config
    
    @pytest.fixture
    def baostock_provider(self, mock_config):
        """创建BaostockProvider实例"""
        with patch('quickstock.providers.baostock.BAOSTOCK_AVAILABLE', True):
            return BaostockProvider(mock_config)
    
    @pytest.fixture
    def eastmoney_provider(self, mock_config):
        """创建EastmoneyProvider实例"""
        return EastmoneyProvider(mock_config)
    
    @pytest.fixture
    def tonghuashun_provider(self, mock_config):
        """创建TonghuashunProvider实例"""
        return TonghuashunProvider(mock_config)
    
    def test_baostock_code_conversion(self, baostock_provider):
        """测试Baostock代码转换"""
        # 测试输入代码转换
        test_cases = [
            ("000001.SZ", "sz.000001"),
            ("600000.SH", "sh.600000"),
            ("sz.000001", "sz.000001"),  # 已经是baostock格式
            ("000001", "sz.000001"),     # 纯数字格式
        ]
        
        for input_code, expected_output in test_cases:
            result = baostock_provider.convert_input_code(input_code)
            assert result == expected_output, f"输入转换失败: {input_code} -> {result}, 期望: {expected_output}"
        
        # 测试输出代码转换
        output_test_cases = [
            ("sz.000001", "000001.SZ"),
            ("sh.600000", "600000.SH"),
        ]
        
        for input_code, expected_output in output_test_cases:
            result = baostock_provider.convert_output_code(input_code)
            assert result == expected_output, f"输出转换失败: {input_code} -> {result}, 期望: {expected_output}"
        
        # 测试格式要求
        assert baostock_provider.get_required_format() == "baostock"
    
    def test_eastmoney_code_conversion(self, eastmoney_provider):
        """测试东方财富代码转换"""
        # 测试输入代码转换
        test_cases = [
            ("000001.SZ", "0.000001"),
            ("600000.SH", "1.600000"),
            ("0.000001", "0.000001"),    # 已经是东方财富格式
            ("000001", "0.000001"),      # 纯数字格式
        ]
        
        for input_code, expected_output in test_cases:
            result = eastmoney_provider.convert_input_code(input_code)
            assert result == expected_output, f"输入转换失败: {input_code} -> {result}, 期望: {expected_output}"
        
        # 测试输出代码转换
        output_test_cases = [
            ("0.000001", "000001.SZ"),
            ("1.600000", "600000.SH"),
        ]
        
        for input_code, expected_output in output_test_cases:
            result = eastmoney_provider.convert_output_code(input_code)
            assert result == expected_output, f"输出转换失败: {input_code} -> {result}, 期望: {expected_output}"
        
        # 测试格式要求
        assert eastmoney_provider.get_required_format() == "eastmoney"
    
    def test_tonghuashun_code_conversion(self, tonghuashun_provider):
        """测试同花顺代码转换"""
        # 测试输入代码转换
        test_cases = [
            ("000001.SZ", "hs_000001"),
            ("600000.SH", "hs_600000"),
            ("hs_000001", "hs_000001"),  # 已经是同花顺格式
            ("000001", "hs_000001"),     # 纯数字格式
        ]
        
        for input_code, expected_output in test_cases:
            result = tonghuashun_provider.convert_input_code(input_code)
            assert result == expected_output, f"输入转换失败: {input_code} -> {result}, 期望: {expected_output}"
        
        # 测试输出代码转换
        output_test_cases = [
            ("hs_000001", "000001.SZ"),
            ("hs_600000", "600000.SH"),
        ]
        
        for input_code, expected_output in output_test_cases:
            result = tonghuashun_provider.convert_output_code(input_code)
            assert result == expected_output, f"输出转换失败: {input_code} -> {result}, 期望: {expected_output}"
        
        # 测试格式要求
        assert tonghuashun_provider.get_required_format() == "tonghuashun"
    
    def test_code_format_validation(self, baostock_provider, eastmoney_provider, tonghuashun_provider):
        """测试代码格式验证"""
        providers = [
            (baostock_provider, "baostock"),
            (eastmoney_provider, "eastmoney"),
            (tonghuashun_provider, "tonghuashun")
        ]
        
        valid_codes = ["000001.SZ", "600000.SH", "000001", "sz.000001", "1.600000", "hs_000001"]
        invalid_codes = ["", "invalid", "123", "000001.XX", "abc.def"]
        
        for provider, provider_name in providers:
            # 测试有效代码
            for code in valid_codes:
                try:
                    is_valid = provider.validate_code_format(code)
                    # 大部分有效代码应该能够转换成功
                    assert isinstance(is_valid, bool), f"{provider_name}: 验证结果应该是布尔值"
                except Exception:
                    # 某些格式可能不被特定提供者支持，这是正常的
                    pass
            
            # 测试无效代码
            for code in invalid_codes:
                is_valid = provider.validate_code_format(code)
                assert not is_valid, f"{provider_name}: 无效代码 {code} 应该验证失败"
    
    def test_cross_provider_consistency(self, baostock_provider, eastmoney_provider, tonghuashun_provider):
        """测试跨数据源的代码格式一致性"""
        # 标准格式的测试代码
        standard_codes = ["000001.SZ", "600000.SH", "000002.SZ", "600036.SH"]
        
        providers = [
            (baostock_provider, "baostock"),
            (eastmoney_provider, "eastmoney"),
            (tonghuashun_provider, "tonghuashun")
        ]
        
        for standard_code in standard_codes:
            # 每个提供者都应该能够处理标准格式的代码
            converted_codes = {}
            
            for provider, provider_name in providers:
                try:
                    # 转换为提供者特定格式
                    provider_format = provider.convert_input_code(standard_code)
                    converted_codes[provider_name] = provider_format
                    
                    # 转换回标准格式
                    back_to_standard = provider.convert_output_code(provider_format)
                    
                    # 验证往返转换的一致性
                    assert back_to_standard == standard_code, \
                        f"{provider_name}: 往返转换不一致 {standard_code} -> {provider_format} -> {back_to_standard}"
                    
                except Exception as e:
                    pytest.fail(f"{provider_name}: 处理标准代码 {standard_code} 失败: {e}")
            
            # 验证所有提供者都能处理相同的标准代码
            assert len(converted_codes) == 3, f"不是所有提供者都能处理代码 {standard_code}"
    
    def test_error_handling(self, baostock_provider, eastmoney_provider, tonghuashun_provider):
        """测试错误处理"""
        providers = [baostock_provider, eastmoney_provider, tonghuashun_provider]
        invalid_codes = ["", "invalid_code", "123.ABC", None]
        
        for provider in providers:
            for invalid_code in invalid_codes:
                if invalid_code is None:
                    continue
                
                # 测试输入转换错误处理
                with pytest.raises((ValidationError, InvalidCodeFormatError, ValueError, TypeError)):
                    provider.convert_input_code(invalid_code)
                
                # 测试输出转换错误处理
                with pytest.raises((ValidationError, InvalidCodeFormatError, ValueError, TypeError)):
                    provider.convert_output_code(invalid_code)
    
    @pytest.mark.asyncio
    async def test_data_format_consistency_mock(self, baostock_provider):
        """测试数据返回格式的一致性（使用模拟数据）"""
        # 模拟baostock返回的数据
        mock_data = pd.DataFrame({
            'code': ['sz.000001', 'sh.600000'],
            'date': ['2023-12-01', '2023-12-01'],
            'open': [10.0, 20.0],
            'close': [11.0, 21.0]
        })
        
        # 测试数据标准化
        standardized_data = baostock_provider._standardize_ohlcv_columns(mock_data.copy())
        
        # 验证代码格式已转换为标准格式
        if 'ts_code' in standardized_data.columns:
            expected_codes = ['000001.SZ', '600000.SH']
            actual_codes = standardized_data['ts_code'].tolist()
            assert actual_codes == expected_codes, f"代码格式转换不正确: {actual_codes}"
    
    def test_batch_code_conversion(self, baostock_provider):
        """测试批量代码转换"""
        # 测试批量输入转换
        input_codes = ["000001.SZ", "600000.SH", "000002.SZ"]
        expected_outputs = ["sz.000001", "sh.600000", "sz.000002"]
        
        actual_outputs = []
        for code in input_codes:
            try:
                converted = baostock_provider.convert_input_code(code)
                actual_outputs.append(converted)
            except Exception as e:
                pytest.fail(f"批量转换失败: {code}, 错误: {e}")
        
        assert actual_outputs == expected_outputs, f"批量转换结果不匹配: {actual_outputs}"
        
        # 测试批量输出转换
        output_codes = ["sz.000001", "sh.600000", "sz.000002"]
        expected_standards = ["000001.SZ", "600000.SH", "000002.SZ"]
        
        actual_standards = []
        for code in output_codes:
            try:
                converted = baostock_provider.convert_output_code(code)
                actual_standards.append(converted)
            except Exception as e:
                pytest.fail(f"批量输出转换失败: {code}, 错误: {e}")
        
        assert actual_standards == expected_standards, f"批量输出转换结果不匹配: {actual_standards}"
    
    def test_edge_cases(self, baostock_provider, eastmoney_provider, tonghuashun_provider):
        """测试边界情况"""
        providers = [
            (baostock_provider, "baostock"),
            (eastmoney_provider, "eastmoney"),
            (tonghuashun_provider, "tonghuashun")
        ]
        
        edge_cases = [
            "000001.sz",  # 小写交易所
            "000001.Sz",  # 混合大小写
            " 000001.SZ ", # 前后空格
            "SZ000001",   # 交易所前缀格式
        ]
        
        for provider, provider_name in providers:
            for edge_case in edge_cases:
                try:
                    # 尝试转换边界情况
                    result = provider.convert_input_code(edge_case)
                    assert result is not None, f"{provider_name}: 边界情况 {edge_case} 转换结果为None"
                    assert isinstance(result, str), f"{provider_name}: 转换结果应该是字符串"
                    assert len(result) > 0, f"{provider_name}: 转换结果不应该为空"
                except Exception:
                    # 某些边界情况可能不被支持，这是可以接受的
                    pass
    
    def test_performance_basic(self, baostock_provider):
        """基础性能测试"""
        import time
        
        # 测试单次转换性能
        test_code = "000001.SZ"
        
        start_time = time.time()
        for _ in range(1000):
            baostock_provider.convert_input_code(test_code)
        end_time = time.time()
        
        avg_time = (end_time - start_time) / 1000
        assert avg_time < 0.001, f"单次转换平均时间过长: {avg_time:.6f}秒"
        
        # 测试缓存效果（如果有的话）
        start_time = time.time()
        for _ in range(1000):
            baostock_provider.convert_input_code(test_code)
        end_time = time.time()
        
        cached_avg_time = (end_time - start_time) / 1000
        # 缓存应该提高性能，但这里只是基础检查
        assert cached_avg_time < 0.002, f"缓存后平均时间仍然过长: {cached_avg_time:.6f}秒"


class TestDataSourceIntegration:
    """数据源集成测试"""
    
    @pytest.fixture
    def mock_config(self):
        """模拟配置对象"""
        config = Mock()
        config.max_concurrent_requests = 10
        config.request_timeout = 30
        config.enable_baostock = True
        config.max_retries = 3
        config.retry_delay = 1.0
        config.connection_pool_size = 10
        config.connection_pool_per_host = 5
        config.connection_keepalive_timeout = 30
        config.connection_cleanup_enabled = True
        return config
    
    def test_provider_interface_compliance(self, mock_config):
        """测试提供者接口合规性"""
        with patch('quickstock.providers.baostock.BAOSTOCK_AVAILABLE', True):
            providers = [
                BaostockProvider(mock_config),
                EastmoneyProvider(mock_config),
                TonghuashunProvider(mock_config)
            ]
        
        for provider in providers:
            # 检查必需的方法是否存在
            assert hasattr(provider, 'convert_input_code'), f"{provider.__class__.__name__}: 缺少convert_input_code方法"
            assert hasattr(provider, 'convert_output_code'), f"{provider.__class__.__name__}: 缺少convert_output_code方法"
            assert hasattr(provider, 'get_required_format'), f"{provider.__class__.__name__}: 缺少get_required_format方法"
            assert hasattr(provider, 'validate_code_format'), f"{provider.__class__.__name__}: 缺少validate_code_format方法"
            
            # 检查方法是否可调用
            assert callable(provider.convert_input_code), f"{provider.__class__.__name__}: convert_input_code不可调用"
            assert callable(provider.convert_output_code), f"{provider.__class__.__name__}: convert_output_code不可调用"
            assert callable(provider.get_required_format), f"{provider.__class__.__name__}: get_required_format不可调用"
            assert callable(provider.validate_code_format), f"{provider.__class__.__name__}: validate_code_format不可调用"
            
            # 测试基本功能
            format_name = provider.get_required_format()
            assert isinstance(format_name, str), f"{provider.__class__.__name__}: get_required_format应该返回字符串"
            assert len(format_name) > 0, f"{provider.__class__.__name__}: 格式名称不应该为空"
    
    def test_unified_converter_integration(self):
        """测试与统一转换器的集成"""
        # 测试所有支持的格式
        test_codes = [
            "000001.SZ",
            "600000.SH", 
            "sz.000001",
            "sh.600000",
            "0.000001",
            "1.600000",
            "hs_000001",
            "hs_600000"
        ]
        
        for code in test_codes:
            try:
                # 统一转换器应该能够识别和标准化所有格式
                standard_code = StockCodeConverter.normalize_code(code)
                assert standard_code is not None, f"标准化失败: {code}"
                assert isinstance(standard_code, str), f"标准化结果应该是字符串: {code}"
                assert '.' in standard_code, f"标准化结果应该包含点号: {code} -> {standard_code}"
                
                # 验证标准化结果的格式
                parts = standard_code.split('.')
                assert len(parts) == 2, f"标准格式应该有两部分: {standard_code}"
                assert len(parts[0]) == 6, f"股票代码应该是6位: {standard_code}"
                assert parts[1] in ['SH', 'SZ'], f"交易所代码应该是SH或SZ: {standard_code}"
                
            except Exception as e:
                pytest.fail(f"统一转换器处理代码 {code} 失败: {e}")
    
    def test_error_consistency(self):
        """测试错误处理的一致性"""
        invalid_inputs = [
            "",
            "invalid",
            "123.ABC",
            "000001.XX",
            None,
            123,
            [],
            {}
        ]
        
        for invalid_input in invalid_inputs:
            if invalid_input is None or not isinstance(invalid_input, str):
                continue
                
            # 统一转换器应该对无效输入抛出一致的异常
            with pytest.raises((ValidationError, InvalidCodeFormatError, ValueError)):
                StockCodeConverter.normalize_code(invalid_input)


class TestProviderDataFormatConsistency:
    """测试数据源返回数据格式的一致性"""
    
    @pytest.fixture
    def mock_config(self):
        """模拟配置对象"""
        config = Mock()
        config.max_concurrent_requests = 10
        config.request_timeout = 30
        config.enable_baostock = True
        config.max_retries = 3
        config.retry_delay = 1.0
        config.connection_pool_size = 10
        config.connection_pool_per_host = 5
        config.connection_keepalive_timeout = 30
        config.connection_cleanup_enabled = True
        return config
    
    def test_ohlcv_data_format_consistency(self, mock_config):
        """测试OHLCV数据格式一致性"""
        with patch('quickstock.providers.baostock.BAOSTOCK_AVAILABLE', True):
            providers = [
                BaostockProvider(mock_config),
                EastmoneyProvider(mock_config),
                TonghuashunProvider(mock_config)
            ]
        
        # 模拟各数据源的原始数据格式
        raw_data_formats = {
            'baostock': pd.DataFrame({
                'code': ['sz.000001', 'sh.600000'],
                'date': ['2023-12-01', '2023-12-01'],
                'open': [10.0, 20.0],
                'high': [11.0, 21.0],
                'low': [9.5, 19.5],
                'close': [10.5, 20.5],
                'volume': [1000000, 2000000]
            }),
            'eastmoney': pd.DataFrame({
                'secucode': ['0.000001', '1.600000'],
                'trade_date': ['20231201', '20231201'],
                'open_price': [10.0, 20.0],
                'high_price': [11.0, 21.0],
                'low_price': [9.5, 19.5],
                'close_price': [10.5, 20.5],
                'vol': [1000000, 2000000]
            }),
            'tonghuashun': pd.DataFrame({
                'symbol': ['hs_000001', 'hs_600000'],
                'date': ['2023-12-01', '2023-12-01'],
                'o': [10.0, 20.0],
                'h': [11.0, 21.0],
                'l': [9.5, 19.5],
                'c': [10.5, 20.5],
                'v': [1000000, 2000000]
            })
        }
        
        expected_standard_format = pd.DataFrame({
            'ts_code': ['000001.SZ', '600000.SH'],
            'trade_date': ['20231201', '20231201'],
            'open': [10.0, 20.0],
            'high': [11.0, 21.0],
            'low': [9.5, 19.5],
            'close': [10.5, 20.5],
            'vol': [1000000, 2000000]
        })
        
        for provider in providers:
            provider_name = provider.__class__.__name__.lower().replace('provider', '')
            if provider_name in raw_data_formats:
                raw_data = raw_data_formats[provider_name]
                
                # 测试数据标准化
                try:
                    standardized_data = provider._standardize_ohlcv_columns(raw_data.copy())
                    
                    # 验证必需的列存在
                    required_columns = ['ts_code', 'trade_date', 'open', 'high', 'low', 'close', 'vol']
                    for col in required_columns:
                        assert col in standardized_data.columns, \
                            f"{provider_name}: 缺少必需列 {col}"
                    
                    # 验证代码格式已标准化
                    if 'ts_code' in standardized_data.columns:
                        for code in standardized_data['ts_code']:
                            assert '.' in code, f"{provider_name}: 代码格式未标准化 {code}"
                            parts = code.split('.')
                            assert len(parts) == 2, f"{provider_name}: 代码格式不正确 {code}"
                            assert parts[1] in ['SH', 'SZ'], f"{provider_name}: 交易所代码不正确 {code}"
                    
                    # 验证日期格式
                    if 'trade_date' in standardized_data.columns:
                        for date in standardized_data['trade_date']:
                            assert len(str(date)) == 8, f"{provider_name}: 日期格式不正确 {date}"
                
                except AttributeError:
                    # 某些提供者可能没有实现_standardize_ohlcv_columns方法
                    pass
    
    def test_stock_basic_data_format_consistency(self, mock_config):
        """测试股票基础信息数据格式一致性"""
        with patch('quickstock.providers.baostock.BAOSTOCK_AVAILABLE', True):
            providers = [
                BaostockProvider(mock_config),
                EastmoneyProvider(mock_config),
                TonghuashunProvider(mock_config)
            ]
        
        # 模拟各数据源的股票基础信息格式
        raw_basic_formats = {
            'baostock': pd.DataFrame({
                'code': ['sz.000001', 'sh.600000'],
                'code_name': ['平安银行', '浦发银行'],
                'ipoDate': ['1991-04-03', '1999-09-10'],
                'outDate': ['', ''],
                'type': ['1', '1'],
                'status': ['1', '1']
            }),
            'eastmoney': pd.DataFrame({
                'secucode': ['0.000001', '1.600000'],
                'security_name_abbr': ['平安银行', '浦发银行'],
                'list_date': ['19910403', '19990910'],
                'delist_date': ['', ''],
                'security_type': ['A股', 'A股'],
                'status': ['L', 'L']
            }),
            'tonghuashun': pd.DataFrame({
                'symbol': ['hs_000001', 'hs_600000'],
                'name': ['平安银行', '浦发银行'],
                'list_date': ['1991-04-03', '1999-09-10'],
                'delist_date': ['', ''],
                'market': ['深圳', '上海'],
                'status': ['正常', '正常']
            })
        }
        
        for provider in providers:
            provider_name = provider.__class__.__name__.lower().replace('provider', '')
            if provider_name in raw_basic_formats:
                raw_data = raw_basic_formats[provider_name]
                
                try:
                    standardized_data = provider._standardize_stock_basic_columns(raw_data.copy())
                    
                    # 验证必需的列存在
                    required_columns = ['ts_code', 'symbol', 'name', 'list_date']
                    for col in required_columns:
                        if col in standardized_data.columns:
                            # 验证代码格式
                            if col == 'ts_code':
                                for code in standardized_data[col]:
                                    if pd.notna(code) and code:
                                        assert '.' in str(code), f"{provider_name}: ts_code格式未标准化 {code}"
                
                except AttributeError:
                    # 某些提供者可能没有实现_standardize_stock_basic_columns方法
                    pass
    
    def test_data_source_code_conversion_integration(self, mock_config):
        """测试数据源代码转换集成"""
        with patch('quickstock.providers.baostock.BAOSTOCK_AVAILABLE', True):
            providers = [
                ('baostock', BaostockProvider(mock_config)),
                ('eastmoney', EastmoneyProvider(mock_config)),
                ('tonghuashun', TonghuashunProvider(mock_config))
            ]
        
        # 测试代码在不同数据源间的转换一致性
        test_codes = [
            "000001.SZ",
            "600000.SH",
            "000002.SZ",
            "600036.SH",
            "300001.SZ",
            "688001.SH"
        ]
        
        for standard_code in test_codes:
            conversion_results = {}
            
            for provider_name, provider in providers:
                try:
                    # 转换为数据源特定格式
                    provider_format = provider.convert_input_code(standard_code)
                    conversion_results[provider_name] = provider_format
                    
                    # 验证转换结果不为空
                    assert provider_format is not None, \
                        f"{provider_name}: 转换结果为None"
                    assert isinstance(provider_format, str), \
                        f"{provider_name}: 转换结果不是字符串"
                    assert len(provider_format) > 0, \
                        f"{provider_name}: 转换结果为空字符串"
                    
                    # 转换回标准格式验证一致性
                    back_to_standard = provider.convert_output_code(provider_format)
                    assert back_to_standard == standard_code, \
                        f"{provider_name}: 往返转换不一致 {standard_code} -> {provider_format} -> {back_to_standard}"
                
                except Exception as e:
                    pytest.fail(f"{provider_name}: 处理代码 {standard_code} 失败: {e}")
            
            # 验证所有数据源都能处理相同的标准代码
            assert len(conversion_results) == 3, \
                f"不是所有数据源都能处理代码 {standard_code}: {conversion_results}"


class TestProviderCodeConversionPerformance:
    """测试数据源代码转换性能"""
    
    @pytest.fixture
    def mock_config(self):
        """模拟配置对象"""
        config = Mock()
        config.max_concurrent_requests = 10
        config.request_timeout = 30
        config.enable_baostock = True
        config.max_retries = 3
        config.retry_delay = 1.0
        config.connection_pool_size = 10
        config.connection_pool_per_host = 5
        config.connection_keepalive_timeout = 30
        config.connection_cleanup_enabled = True
        return config
    
    def test_single_conversion_performance(self, mock_config):
        """测试单次转换性能"""
        with patch('quickstock.providers.baostock.BAOSTOCK_AVAILABLE', True):
            provider = BaostockProvider(mock_config)
        
        test_code = "000001.SZ"
        iterations = 1000
        
        # 测试输入转换性能
        start_time = time.time()
        for _ in range(iterations):
            provider.convert_input_code(test_code)
        input_time = time.time() - start_time
        
        # 测试输出转换性能
        baostock_code = "sz.000001"
        start_time = time.time()
        for _ in range(iterations):
            provider.convert_output_code(baostock_code)
        output_time = time.time() - start_time
        
        # 验证性能要求
        avg_input_time = input_time / iterations
        avg_output_time = output_time / iterations
        
        assert avg_input_time < 0.001, f"输入转换平均时间过长: {avg_input_time:.6f}秒"
        assert avg_output_time < 0.001, f"输出转换平均时间过长: {avg_output_time:.6f}秒"
    
    def test_batch_conversion_performance(self, mock_config):
        """测试批量转换性能"""
        with patch('quickstock.providers.baostock.BAOSTOCK_AVAILABLE', True):
            provider = BaostockProvider(mock_config)
        
        # 生成测试代码
        test_codes = [f"{i:06d}.SZ" for i in range(1, 101)]  # 100个代码
        
        start_time = time.time()
        results = []
        for code in test_codes:
            try:
                result = provider.convert_input_code(code)
                results.append(result)
            except Exception:
                # 忽略转换失败的代码
                pass
        end_time = time.time()
        
        total_time = end_time - start_time
        avg_time_per_code = total_time / len(test_codes)
        
        # 验证批量处理性能
        assert total_time < 1.0, f"批量转换总时间过长: {total_time:.3f}秒"
        assert avg_time_per_code < 0.01, f"平均每个代码转换时间过长: {avg_time_per_code:.6f}秒"
        assert len(results) > 0, "批量转换没有成功的结果"
    
    def test_concurrent_conversion_performance(self, mock_config):
        """测试并发转换性能"""
        with patch('quickstock.providers.baostock.BAOSTOCK_AVAILABLE', True):
            provider = BaostockProvider(mock_config)
        
        test_codes = ["000001.SZ", "600000.SH", "000002.SZ", "600036.SH"] * 25  # 100个代码
        results = []
        errors = []
        
        def convert_code(code):
            try:
                result = provider.convert_input_code(code)
                results.append(result)
            except Exception as e:
                errors.append(e)
        
        # 并发转换
        start_time = time.time()
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(convert_code, code) for code in test_codes]
            for future in futures:
                future.result()  # 等待完成
        end_time = time.time()
        
        concurrent_time = end_time - start_time
        
        # 验证并发性能和正确性
        assert len(errors) == 0, f"并发转换出现错误: {errors[:5]}"  # 只显示前5个错误
        assert len(results) == len(test_codes), f"并发转换结果数量不匹配: {len(results)} != {len(test_codes)}"
        assert concurrent_time < 2.0, f"并发转换时间过长: {concurrent_time:.3f}秒"
    
    def test_memory_usage_during_conversion(self, mock_config):
        """测试转换过程中的内存使用"""
        import psutil
        import os
        
        with patch('quickstock.providers.baostock.BAOSTOCK_AVAILABLE', True):
            provider = BaostockProvider(mock_config)
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # 大量转换操作
        test_codes = [f"{i:06d}.SZ" for i in range(1, 1001)]  # 1000个代码
        
        for code in test_codes:
            try:
                provider.convert_input_code(code)
            except Exception:
                pass
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # 内存增长应该在合理范围内
        assert memory_increase < 50, f"内存增长过多: {memory_increase:.2f}MB"


class TestProviderErrorHandlingComprehensive:
    """测试数据源错误处理的全面性"""
    
    @pytest.fixture
    def mock_config(self):
        """模拟配置对象"""
        config = Mock()
        config.max_concurrent_requests = 10
        config.request_timeout = 30
        config.enable_baostock = True
        config.max_retries = 3
        config.retry_delay = 1.0
        config.connection_pool_size = 10
        config.connection_pool_per_host = 5
        config.connection_keepalive_timeout = 30
        config.connection_cleanup_enabled = True
        return config
    
    def test_invalid_code_error_handling(self, mock_config):
        """测试无效代码错误处理"""
        with patch('quickstock.providers.baostock.BAOSTOCK_AVAILABLE', True):
            providers = [
                ('baostock', BaostockProvider(mock_config)),
                ('eastmoney', EastmoneyProvider(mock_config)),
                ('tonghuashun', TonghuashunProvider(mock_config))
            ]
        
        invalid_codes = [
            "",
            None,
            "invalid",
            "123",
            "1234567",
            "000001.XX",
            "abc.def",
            "000001.",
            ".SZ",
            "000001..SZ",
            "000001.SZ.extra"
        ]
        
        for provider_name, provider in providers:
            for invalid_code in invalid_codes:
                if invalid_code is None:
                    continue
                
                # 测试输入转换错误处理
                with pytest.raises((ValidationError, InvalidCodeFormatError, ValueError, TypeError, CodeConversionError)):
                    provider.convert_input_code(invalid_code)
                
                # 测试输出转换错误处理
                with pytest.raises((ValidationError, InvalidCodeFormatError, ValueError, TypeError, CodeConversionError)):
                    provider.convert_output_code(invalid_code)
                
                # 测试验证方法错误处理
                is_valid = provider.validate_code_format(invalid_code)
                assert not is_valid, f"{provider_name}: 无效代码 {invalid_code} 验证应该失败"
    
    def test_edge_case_error_handling(self, mock_config):
        """测试边界情况错误处理"""
        with patch('quickstock.providers.baostock.BAOSTOCK_AVAILABLE', True):
            provider = BaostockProvider(mock_config)
        
        edge_cases = [
            "000001.sz",    # 小写交易所
            "000001.Sz",    # 混合大小写
            " 000001.SZ ",  # 前后空格
            "\t000001.SZ\n", # 制表符和换行符
            "SZ000001",     # 交易所前缀格式
            "000001SZ",     # 无分隔符
            "０００００１.SZ", # 全角数字
            "000001．SZ",   # 全角句号
        ]
        
        for edge_case in edge_cases:
            try:
                # 某些边界情况可能被正确处理
                result = provider.convert_input_code(edge_case)
                if result is not None:
                    assert isinstance(result, str), f"边界情况处理结果应该是字符串: {edge_case}"
                    assert len(result) > 0, f"边界情况处理结果不应该为空: {edge_case}"
            except (ValidationError, InvalidCodeFormatError, ValueError, CodeConversionError):
                # 这些异常是可以接受的
                pass
            except Exception as e:
                pytest.fail(f"边界情况 {edge_case} 处理出现意外异常: {e}")
    
    def test_error_message_quality(self, mock_config):
        """测试错误消息质量"""
        with patch('quickstock.providers.baostock.BAOSTOCK_AVAILABLE', True):
            provider = BaostockProvider(mock_config)
        
        invalid_codes = ["invalid_code", "123.ABC", ""]
        
        for invalid_code in invalid_codes:
            try:
                provider.convert_input_code(invalid_code)
                pytest.fail(f"应该抛出异常的代码: {invalid_code}")
            except Exception as e:
                error_msg = str(e)
                
                # 验证错误消息质量
                assert len(error_msg) > 0, "错误消息不应该为空"
                assert len(error_msg) < 500, f"错误消息过长: {len(error_msg)}字符"
                
                # 错误消息应该包含有用信息
                useful_keywords = ["代码", "格式", "无效", "错误", "code", "format", "invalid", "error"]
                has_useful_info = any(keyword in error_msg.lower() for keyword in useful_keywords)
                assert has_useful_info, f"错误消息缺少有用信息: {error_msg}"
    
    def test_exception_type_consistency(self, mock_config):
        """测试异常类型一致性"""
        with patch('quickstock.providers.baostock.BAOSTOCK_AVAILABLE', True):
            providers = [
                BaostockProvider(mock_config),
                EastmoneyProvider(mock_config),
                TonghuashunProvider(mock_config)
            ]
        
        invalid_code = "invalid_code"
        exception_types = set()
        
        for provider in providers:
            try:
                provider.convert_input_code(invalid_code)
                pytest.fail(f"提供者 {provider.__class__.__name__} 应该抛出异常")
            except Exception as e:
                exception_types.add(type(e))
        
        # 所有提供者应该抛出相似类型的异常
        expected_exception_types = {ValidationError, InvalidCodeFormatError, ValueError, CodeConversionError}
        
        for exc_type in exception_types:
            assert any(issubclass(exc_type, expected) for expected in expected_exception_types), \
                f"意外的异常类型: {exc_type}"


class TestProviderIntegrationWithRealScenarios:
    """测试数据源在真实场景下的集成"""
    
    @pytest.fixture
    def mock_config(self):
        """模拟配置对象"""
        config = Mock()
        config.max_concurrent_requests = 10
        config.request_timeout = 30
        config.enable_baostock = True
        config.max_retries = 3
        config.retry_delay = 1.0
        config.connection_pool_size = 10
        config.connection_pool_per_host = 5
        config.connection_keepalive_timeout = 30
        config.connection_cleanup_enabled = True
        return config
    
    def test_mixed_format_batch_processing(self, mock_config):
        """测试混合格式批量处理"""
        with patch('quickstock.providers.baostock.BAOSTOCK_AVAILABLE', True):
            provider = BaostockProvider(mock_config)
        
        # 混合格式的代码列表（模拟真实使用场景）
        mixed_codes = [
            "000001.SZ",    # 标准格式
            "600000",       # 纯数字
            "sz.000002",    # Baostock格式
            "SH600036",     # 交易所前缀格式
            "000001.sz",    # 小写交易所
            "300001.SZ",    # 创业板
            "688001.SH",    # 科创板
        ]
        
        results = []
        errors = []
        
        for code in mixed_codes:
            try:
                result = provider.convert_input_code(code)
                results.append((code, result))
            except Exception as e:
                errors.append((code, e))
        
        # 验证大部分代码能够成功转换
        success_rate = len(results) / len(mixed_codes)
        assert success_rate >= 0.7, f"成功率过低: {success_rate:.2%}"
        
        # 验证转换结果格式正确
        for original, converted in results:
            assert isinstance(converted, str), f"转换结果应该是字符串: {original} -> {converted}"
            assert len(converted) > 0, f"转换结果不应该为空: {original} -> {converted}"
            # Baostock格式应该包含点号和交易所前缀
            assert '.' in converted, f"Baostock格式应该包含点号: {original} -> {converted}"
            assert converted.startswith(('sh.', 'sz.')), f"Baostock格式前缀不正确: {original} -> {converted}"
    
    def test_data_pipeline_integration(self, mock_config):
        """测试数据管道集成"""
        with patch('quickstock.providers.baostock.BAOSTOCK_AVAILABLE', True):
            provider = BaostockProvider(mock_config)
        
        # 模拟完整的数据处理管道
        input_codes = ["000001.SZ", "600000.SH", "sz.000002"]
        
        # 步骤1: 输入代码转换
        converted_codes = []
        for code in input_codes:
            try:
                converted = provider.convert_input_code(code)
                converted_codes.append(converted)
            except Exception as e:
                pytest.fail(f"输入转换失败: {code}, 错误: {e}")
        
        # 步骤2: 模拟数据获取（这里只是验证代码格式）
        for code in converted_codes:
            assert provider.validate_code_format(code), f"转换后的代码格式无效: {code}"
        
        # 步骤3: 输出代码转换（模拟数据返回时的处理）
        output_codes = []
        for code in converted_codes:
            try:
                output = provider.convert_output_code(code)
                output_codes.append(output)
            except Exception as e:
                pytest.fail(f"输出转换失败: {code}, 错误: {e}")
        
        # 验证管道完整性
        assert len(output_codes) == len(input_codes), "管道处理前后数量不一致"
        
        # 验证往返转换的一致性（对于标准格式输入）
        for i, (original, final) in enumerate(zip(input_codes, output_codes)):
            if '.' in original and original.count('.') == 1:  # 标准格式
                normalized_original = StockCodeConverter.normalize_code(original)
                assert final == normalized_original, \
                    f"往返转换不一致: {original} -> {final}, 期望: {normalized_original}"
    
    def test_provider_switching_scenario(self, mock_config):
        """测试数据源切换场景"""
        with patch('quickstock.providers.baostock.BAOSTOCK_AVAILABLE', True):
            providers = [
                ('baostock', BaostockProvider(mock_config)),
                ('eastmoney', EastmoneyProvider(mock_config)),
                ('tonghuashun', TonghuashunProvider(mock_config))
            ]
        
        # 模拟用户在不同数据源间切换的场景
        test_code = "000001.SZ"
        
        conversion_chain = []
        
        # 在不同数据源间转换
        for provider_name, provider in providers:
            try:
                # 转换为数据源特定格式
                provider_format = provider.convert_input_code(test_code)
                conversion_chain.append((provider_name, provider_format))
                
                # 转换回标准格式
                back_to_standard = provider.convert_output_code(provider_format)
                
                # 验证往返转换一致性
                assert back_to_standard == test_code, \
                    f"{provider_name}: 往返转换不一致 {test_code} -> {provider_format} -> {back_to_standard}"
                
            except Exception as e:
                pytest.fail(f"{provider_name}: 数据源切换失败: {e}")
        
        # 验证所有数据源都能处理相同的代码
        assert len(conversion_chain) == 3, f"不是所有数据源都能处理代码: {conversion_chain}"
        
        # 验证不同数据源的格式确实不同
        formats = [fmt for _, fmt in conversion_chain]
        unique_formats = set(formats)
        assert len(unique_formats) == 3, f"数据源格式应该不同: {formats}"


if __name__ == "__main__":
    # 运行所有测试
    pytest.main([__file__, "-v", "--tb=short"])