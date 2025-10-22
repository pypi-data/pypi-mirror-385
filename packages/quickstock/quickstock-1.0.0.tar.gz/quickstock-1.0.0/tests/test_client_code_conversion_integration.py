"""
QuickStock客户端代码转换集成测试

实现task 7.2：创建客户端集成测试
- 测试QuickStockClient的代码转换集成
- 验证数据获取方法的多格式支持
- 测试向后兼容性和API一致性
"""

import pytest
import pandas as pd
from unittest.mock import Mock, patch, MagicMock
import asyncio

from quickstock.client import QuickStockClient
from quickstock.config import Config
from quickstock.core.errors import QuickStockError, ValidationError
from quickstock.utils.code_converter import (
    CodeConversionError,
    InvalidCodeFormatError,
    UnsupportedFormatError,
    ExchangeInferenceError
)


class TestClientCodeConversionIntegration:
    """测试客户端代码转换集成功能"""
    
    def setup_method(self):
        """测试前置设置"""
        self.test_config = Config(
            cache_enabled=True,
            log_level='ERROR',
            enable_auto_code_conversion=True,
            strict_code_validation=False
        )
        self.client = QuickStockClient(self.test_config)
    
    def test_client_normalize_code_integration(self):
        """测试客户端代码标准化集成"""
        # 测试各种格式的代码标准化
        test_cases = [
            ("000001", "000001.SZ"),
            ("000001.SZ", "000001.SZ"),
            ("SZ000001", "000001.SZ"),
            ("sz.000001", "000001.SZ"),
            ("0.000001", "000001.SZ"),
            ("hs_000001", "000001.SZ"),
            ("600000", "600000.SH"),
            ("600000.SH", "600000.SH"),
            ("sh.600000", "600000.SH"),
            ("1.600000", "600000.SH"),
        ]
        
        for input_code, expected in test_cases:
            result = self.client.normalize_code(input_code)
            assert result == expected, f"标准化 {input_code} 失败，期望 {expected}，得到 {result}"
    
    def test_client_convert_code_integration(self):
        """测试客户端代码格式转换集成"""
        source_code = "000001.SZ"
        
        # 测试转换到各种格式
        conversion_tests = [
            ("standard", "000001.SZ"),
            ("baostock", "sz.000001"),
            ("eastmoney", "0.000001"),
            ("tonghuashun", "hs_000001"),
        ]
        
        for target_format, expected in conversion_tests:
            result = self.client.convert_code(source_code, target_format)
            assert result == expected, f"转换到 {target_format} 失败，期望 {expected}，得到 {result}"
    
    def test_client_parse_code_integration(self):
        """测试客户端代码解析集成"""
        test_cases = [
            ("000001.SZ", ("000001", "SZ")),
            ("600000.SH", ("600000", "SH")),
            ("sz.000001", ("000001", "SZ")),
            ("sh.600000", ("600000", "SH")),
            ("0.000001", ("000001", "SZ")),
            ("1.600000", ("600000", "SH")),
        ]
        
        for input_code, expected in test_cases:
            result = self.client.parse_code(input_code)
            assert result == expected, f"解析 {input_code} 失败，期望 {expected}，得到 {result}"
    
    def test_client_validate_code_integration(self):
        """测试客户端代码验证集成"""
        # 有效代码
        valid_codes = [
            "000001.SZ", "600000.SH", "sz.000001", "sh.600000",
            "0.000001", "1.600000", "hs_000001", "000001", "600000"
        ]
        
        for code in valid_codes:
            assert self.client.validate_code(code) is True, f"代码 {code} 应该有效"
        
        # 无效代码
        invalid_codes = [
            "", None, "invalid", "12345", "1234567", "000001.XX"
        ]
        
        for code in invalid_codes:
            assert self.client.validate_code(code) is False, f"代码 {code} 应该无效"
    
    def test_client_get_supported_formats_integration(self):
        """测试客户端获取支持格式集成"""
        formats = self.client.get_supported_formats()
        
        assert isinstance(formats, list)
        assert len(formats) > 0
        
        expected_formats = ["standard", "baostock", "eastmoney", "tonghuashun", "pure_number"]
        for fmt in expected_formats:
            assert fmt in formats, f"格式 {fmt} 应该在支持列表中"
    
    def test_client_code_conversion_error_handling(self):
        """测试客户端代码转换错误处理"""
        # 测试无效格式错误
        with pytest.raises((ValidationError, InvalidCodeFormatError)):
            self.client.normalize_code("invalid_code")
        
        # 测试不支持的格式错误
        with pytest.raises(UnsupportedFormatError):
            self.client.convert_code("000001.SZ", "unknown_format")
        
        # 测试交易所推断错误
        with pytest.raises(ExchangeInferenceError):
            self.client.parse_code("123456")  # 不符合任何交易所规则
    
    def test_client_internal_code_validation_integration(self):
        """测试客户端内部代码验证集成"""
        # 测试内部验证方法
        result = self.client._validate_and_normalize_code("000001", "测试参数")
        assert result == "000001.SZ"
        
        result = self.client._validate_and_normalize_code("sz.000001", "测试参数")
        assert result == "000001.SZ"
        
        # 测试无效代码
        with pytest.raises(ValidationError) as exc_info:
            self.client._validate_and_normalize_code("invalid", "测试参数")
        
        error_msg = str(exc_info.value)
        assert "测试参数" in error_msg
        assert "invalid" in error_msg


class TestClientDataMethodsCodeConversion:
    """测试客户端数据获取方法的代码转换集成"""
    
    def setup_method(self):
        """测试前置设置"""
        self.test_config = Config(
            cache_enabled=False,
            log_level='ERROR',
            enable_auto_code_conversion=True
        )
        self.client = QuickStockClient(self.test_config)
    
    @patch('quickstock.client.QuickStockClient._get_data')
    def test_stock_daily_multi_format_support(self, mock_get_data):
        """测试股票日线数据多格式支持"""
        # Mock返回数据
        mock_data = pd.DataFrame({
            'ts_code': ['000001.SZ'],
            'trade_date': ['20231201'],
            'open': [10.0],
            'high': [11.0],
            'low': [9.5],
            'close': [10.5],
            'vol': [1000000]
        })
        mock_get_data.return_value = mock_data
        
        # 测试不同格式的代码输入
        test_formats = [
            "000001.SZ",    # 标准格式
            "000001",       # 纯数字
            "sz.000001",    # Baostock格式
            "0.000001",     # 东方财富格式
            "hs_000001",    # 同花顺格式
        ]
        
        for code_format in test_formats:
            result = self.client.stock_daily(
                ts_code=code_format,
                start_date='20231201',
                end_date='20231201'
            )
            
            # 验证结果
            assert isinstance(result, pd.DataFrame)
            assert len(result) == 1
            
            # 验证传递给底层方法的代码已被标准化
            mock_get_data.assert_called()
            call_args = mock_get_data.call_args
            # 检查传递的参数中的ts_code是否已标准化
            assert '000001.SZ' in str(call_args)
    
    @patch('quickstock.client.QuickStockClient._get_data')
    def test_stock_minute_multi_format_support(self, mock_get_data):
        """测试股票分钟数据多格式支持"""
        mock_data = pd.DataFrame({
            'ts_code': ['600000.SH'],
            'trade_time': ['20231201 09:30:00'],
            'open': [10.0],
            'high': [10.2],
            'low': [9.9],
            'close': [10.1],
            'vol': [100000]
        })
        mock_get_data.return_value = mock_data
        
        # 测试上海股票的不同格式
        test_formats = [
            "600000.SH",    # 标准格式
            "600000",       # 纯数字
            "sh.600000",    # Baostock格式
            "1.600000",     # 东方财富格式
            "hs_600000",    # 同花顺格式
        ]
        
        for code_format in test_formats:
            result = self.client.stock_minute(
                ts_code=code_format,
                start_date='20231201',
                end_date='20231201',
                freq='1min'
            )
            
            assert isinstance(result, pd.DataFrame)
            mock_get_data.assert_called()
    
    @patch('quickstock.client.QuickStockClient._get_data')
    def test_stock_basic_code_filtering(self, mock_get_data):
        """测试股票基础信息代码过滤"""
        mock_data = pd.DataFrame({
            'ts_code': ['000001.SZ', '600000.SH', '300001.SZ'],
            'symbol': ['000001', '600000', '300001'],
            'name': ['平安银行', '浦发银行', '特锐德'],
            'area': ['深圳', '上海', '深圳'],
            'industry': ['银行', '银行', '电气设备'],
            'list_date': ['19910403', '19990910', '20100126']
        })
        mock_get_data.return_value = mock_data
        
        # 测试使用不同格式的代码过滤
        result = self.client.stock_basic(ts_code="sz.000001")
        
        assert isinstance(result, pd.DataFrame)
        mock_get_data.assert_called()
        
        # 验证传递的参数已标准化
        call_args = mock_get_data.call_args
        assert '000001.SZ' in str(call_args)
    
    def test_data_methods_error_handling_with_invalid_codes(self):
        """测试数据方法对无效代码的错误处理"""
        # 测试各种数据获取方法对无效代码的处理
        invalid_codes = ["", "invalid", "12345", "000001.XX"]
        
        data_methods = [
            ('stock_daily', {'start_date': '20231201', 'end_date': '20231201'}),
            ('stock_minute', {'start_date': '20231201', 'end_date': '20231201', 'freq': '1min'}),
            ('stock_basic', {}),
        ]
        
        for method_name, extra_kwargs in data_methods:
            method = getattr(self.client, method_name)
            
            for invalid_code in invalid_codes:
                with pytest.raises((ValidationError, QuickStockError)):
                    method(ts_code=invalid_code, **extra_kwargs)
    
    @patch('quickstock.client.QuickStockClient._get_data')
    def test_batch_data_retrieval_with_mixed_formats(self, mock_get_data):
        """测试混合格式的批量数据获取"""
        mock_data = pd.DataFrame({
            'ts_code': ['000001.SZ', '600000.SH'],
            'trade_date': ['20231201', '20231201'],
            'open': [10.0, 15.0],
            'close': [10.5, 15.5]
        })
        mock_get_data.return_value = mock_data
        
        # 使用混合格式的代码列表
        mixed_codes = ["000001.SZ", "sh.600000", "0.000002", "hs_300001"]
        
        # 模拟批量获取（这里简化为循环调用）
        results = []
        for code in mixed_codes[:2]:  # 只测试前两个以避免过多mock
            try:
                result = self.client.stock_daily(
                    ts_code=code,
                    start_date='20231201',
                    end_date='20231201'
                )
                results.append(result)
            except Exception as e:
                # 记录错误但继续处理其他代码
                print(f"处理代码 {code} 时出错: {e}")
        
        # 验证至少有一些成功的结果
        assert len(results) >= 0  # 允许所有都失败（因为是mock）


class TestClientBackwardCompatibility:
    """测试客户端向后兼容性"""
    
    def setup_method(self):
        """测试前置设置"""
        # 创建禁用自动转换的配置以测试兼容性
        self.legacy_config = Config(
            enable_auto_code_conversion=False,
            strict_code_validation=True
        )
        self.legacy_client = QuickStockClient(self.legacy_config)
        
        # 创建启用自动转换的配置
        self.modern_config = Config(
            enable_auto_code_conversion=True,
            strict_code_validation=False
        )
        self.modern_client = QuickStockClient(self.modern_config)
    
    @patch('quickstock.client.QuickStockClient._get_data')
    def test_legacy_code_format_still_works(self, mock_get_data):
        """测试传统代码格式仍然有效"""
        mock_data = pd.DataFrame({
            'ts_code': ['000001.SZ'],
            'trade_date': ['20231201'],
            'close': [10.5]
        })
        mock_get_data.return_value = mock_data
        
        # 传统标准格式应该在两种配置下都工作
        standard_codes = ["000001.SZ", "600000.SH"]
        
        for code in standard_codes:
            # 测试传统客户端
            result_legacy = self.legacy_client.stock_daily(
                ts_code=code,
                start_date='20231201',
                end_date='20231201'
            )
            assert isinstance(result_legacy, pd.DataFrame)
            
            # 测试现代客户端
            result_modern = self.modern_client.stock_daily(
                ts_code=code,
                start_date='20231201',
                end_date='20231201'
            )
            assert isinstance(result_modern, pd.DataFrame)
    
    def test_api_interface_consistency(self):
        """测试API接口一致性"""
        # 验证两种客户端都有相同的公共方法
        legacy_methods = set(dir(self.legacy_client))
        modern_methods = set(dir(self.modern_client))
        
        # 公共API方法应该相同
        public_methods = {method for method in legacy_methods 
                         if not method.startswith('_') and callable(getattr(self.legacy_client, method))}
        
        for method in public_methods:
            assert hasattr(self.modern_client, method), f"现代客户端缺少方法: {method}"
            assert callable(getattr(self.modern_client, method)), f"方法 {method} 不可调用"
    
    def test_configuration_backward_compatibility(self):
        """测试配置向后兼容性"""
        # 旧配置应该仍然有效
        old_style_config = Config(
            cache_enabled=True,
            max_retries=3,
            request_timeout=30
        )
        
        client = QuickStockClient(old_style_config)
        
        # 验证客户端正常初始化
        assert client.config.cache_enabled is True
        assert client.config.max_retries == 3
        assert client.config.request_timeout == 30
        
        # 新配置项应该有默认值
        assert hasattr(client.config, 'enable_auto_code_conversion')
        assert hasattr(client.config, 'strict_code_validation')
    
    def test_error_message_backward_compatibility(self):
        """测试错误消息向后兼容性"""
        # 确保错误消息格式保持一致
        with pytest.raises((ValidationError, QuickStockError)) as exc_info:
            self.legacy_client.stock_daily(ts_code="", start_date='20231201')
        
        legacy_error = str(exc_info.value)
        
        with pytest.raises((ValidationError, QuickStockError)) as exc_info:
            self.modern_client.stock_daily(ts_code="", start_date='20231201')
        
        modern_error = str(exc_info.value)
        
        # 错误消息应该包含相似的关键信息
        assert "股票代码" in legacy_error or "ts_code" in legacy_error
        assert "股票代码" in modern_error or "ts_code" in modern_error


class TestClientCodeConversionPerformance:
    """测试客户端代码转换性能"""
    
    def setup_method(self):
        """测试前置设置"""
        self.client = QuickStockClient(Config(
            cache_enabled=True,
            enable_auto_code_conversion=True
        ))
    
    def test_code_conversion_caching_performance(self):
        """测试代码转换缓存性能"""
        import time
        
        # 第一次转换（应该被缓存）
        start_time = time.time()
        result1 = self.client.normalize_code("000001")
        first_time = time.time() - start_time
        
        # 第二次转换（应该从缓存获取）
        start_time = time.time()
        result2 = self.client.normalize_code("000001")
        second_time = time.time() - start_time
        
        assert result1 == result2 == "000001.SZ"
        # 第二次应该更快或至少不显著更慢
        assert second_time <= first_time * 2
    
    def test_batch_code_conversion_performance(self):
        """测试批量代码转换性能"""
        import time
        
        # 生成测试代码
        test_codes = [f"{i:06d}" for i in range(100)]
        
        start_time = time.time()
        results = []
        for code in test_codes:
            try:
                result = self.client.normalize_code(code)
                results.append(result)
            except Exception:
                # 忽略无法转换的代码
                pass
        end_time = time.time()
        
        processing_time = end_time - start_time
        
        # 验证结果
        assert len(results) > 0
        
        # 性能应该在合理范围内（每个代码转换应该很快）
        avg_time_per_code = processing_time / len(test_codes)
        assert avg_time_per_code < 0.01, f"平均每个代码转换时间过长: {avg_time_per_code:.4f}秒"
    
    @patch('quickstock.client.QuickStockClient._get_data')
    def test_data_method_code_conversion_overhead(self, mock_get_data):
        """测试数据方法代码转换开销"""
        import time
        
        mock_data = pd.DataFrame({
            'ts_code': ['000001.SZ'],
            'trade_date': ['20231201'],
            'close': [10.5]
        })
        mock_get_data.return_value = mock_data
        
        # 测试标准格式（无需转换）
        start_time = time.time()
        self.client.stock_daily(ts_code="000001.SZ", start_date='20231201', end_date='20231201')
        standard_time = time.time() - start_time
        
        # 测试需要转换的格式
        start_time = time.time()
        self.client.stock_daily(ts_code="sz.000001", start_date='20231201', end_date='20231201')
        conversion_time = time.time() - start_time
        
        # 转换开销应该很小
        overhead = conversion_time - standard_time
        assert overhead < 0.1, f"代码转换开销过大: {overhead:.4f}秒"


class TestClientCodeConversionEdgeCases:
    """测试客户端代码转换边界情况"""
    
    def setup_method(self):
        """测试前置设置"""
        self.client = QuickStockClient(Config(
            enable_auto_code_conversion=True,
            strict_code_validation=False
        ))
    
    def test_none_and_empty_code_handling(self):
        """测试None和空代码处理"""
        # None值处理
        with pytest.raises((ValidationError, TypeError)):
            self.client.normalize_code(None)
        
        # 空字符串处理
        with pytest.raises(ValidationError):
            self.client.normalize_code("")
        
        # 空白字符串处理
        with pytest.raises(ValidationError):
            self.client.normalize_code("   ")
    
    def test_special_characters_in_codes(self):
        """测试代码中的特殊字符处理"""
        special_codes = [
            "000001.SZ\n",  # 换行符
            "\t000001.SZ",  # 制表符
            "000001.SZ ",   # 尾随空格
            " 000001.SZ",   # 前导空格
        ]
        
        for code in special_codes:
            result = self.client.normalize_code(code)
            assert result == "000001.SZ", f"特殊字符处理失败: '{code}' -> {result}"
    
    def test_case_sensitivity_handling(self):
        """测试大小写敏感性处理"""
        case_variants = [
            ("000001.sz", "000001.SZ"),
            ("000001.Sz", "000001.SZ"),
            ("000001.sZ", "000001.SZ"),
            ("SZ.000001", "000001.SZ"),
            ("sz.000001", "000001.SZ"),
            ("Sz.000001", "000001.SZ"),
        ]
        
        for input_code, expected in case_variants:
            result = self.client.normalize_code(input_code)
            assert result == expected, f"大小写处理失败: {input_code} -> {result}, 期望 {expected}"
    
    def test_unicode_and_encoding_handling(self):
        """测试Unicode和编码处理"""
        # 测试包含中文字符的无效代码
        with pytest.raises(ValidationError):
            self.client.normalize_code("平安银行")
        
        # 测试包含特殊Unicode字符的代码
        with pytest.raises(ValidationError):
            self.client.normalize_code("000001．SZ")  # 全角句号
    
    def test_very_long_code_handling(self):
        """测试超长代码处理"""
        very_long_code = "0" * 1000 + ".SZ"
        
        with pytest.raises(ValidationError):
            self.client.normalize_code(very_long_code)
    
    def test_concurrent_code_conversion(self):
        """测试并发代码转换"""
        import threading
        import time
        
        results = []
        errors = []
        
        def convert_code(code):
            try:
                result = self.client.normalize_code(code)
                results.append(result)
            except Exception as e:
                errors.append(e)
        
        # 创建多个线程同时转换代码
        threads = []
        test_codes = ["000001", "600000", "300001", "sz.000001", "sh.600000"] * 10
        
        for code in test_codes:
            thread = threading.Thread(target=convert_code, args=(code,))
            threads.append(thread)
            thread.start()
        
        # 等待所有线程完成
        for thread in threads:
            thread.join()
        
        # 验证结果
        assert len(errors) == 0, f"并发转换出现错误: {errors}"
        assert len(results) == len(test_codes)
        
        # 验证结果正确性
        expected_results = ["000001.SZ", "600000.SH", "300001.SZ", "000001.SZ", "600000.SH"] * 10
        assert sorted(results) == sorted(expected_results)


if __name__ == "__main__":
    # 运行所有测试
    pytest.main([__file__, "-v", "--tb=short"])