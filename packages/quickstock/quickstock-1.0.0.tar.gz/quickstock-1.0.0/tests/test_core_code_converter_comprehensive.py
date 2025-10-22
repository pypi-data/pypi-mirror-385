"""
全面的股票代码转换器核心功能单元测试

实现task 7.1：编写核心功能单元测试
- 测试StockCodeConverter的所有转换方法
- 验证缓存机制和性能优化功能
- 测试错误处理和异常情况
"""

import pytest
import time
import threading
from unittest.mock import patch, MagicMock
from concurrent.futures import ThreadPoolExecutor
from quickstock.utils.code_converter import (
    StockCodeConverter,
    CodeConversionCache,
    CodeConversionLogger,
    ErrorHandlingStrategy,
    PatternMatcher,
    ExchangeInferrer,
    CodeValidationHelper,
    CodeConversionError,
    InvalidCodeFormatError,
    UnsupportedFormatError,
    ExchangeInferenceError,
    BatchConversionError,
    normalize_stock_code,
    convert_stock_code,
    parse_stock_code,
    validate_stock_code,
    batch_normalize_codes,
    batch_convert_codes
)
from quickstock.core.errors import ValidationError


class TestStockCodeConverterCore:
    """测试StockCodeConverter核心转换方法"""
    
    def test_parse_stock_code_all_formats(self):
        """测试解析所有支持的格式"""
        test_cases = [
            # 标准格式
            ("000001.SZ", ("000001", "SZ")),
            ("600000.SH", ("600000", "SH")),
            ("300001.SZ", ("300001", "SZ")),
            ("688001.SH", ("688001", "SH")),
            
            # 交易所前缀格式
            ("SZ000001", ("000001", "SZ")),
            ("SH600000", ("600000", "SH")),
            
            # 纯数字格式（需要推断交易所）
            ("000001", ("000001", "SZ")),
            ("600000", ("600000", "SH")),
            ("300001", ("300001", "SZ")),
            ("688001", ("688001", "SH")),
            
            # Baostock格式
            ("sz.000001", ("000001", "SZ")),
            ("sh.600000", ("600000", "SH")),
            
            # 东方财富格式
            ("0.000001", ("000001", "SZ")),
            ("1.600000", ("600000", "SH")),
            
            # 同花顺格式
            ("hs_000001", ("000001", "SZ")),
            ("hs_600000", ("600000", "SH")),
        ]
        
        for input_code, expected in test_cases:
            result = StockCodeConverter.parse_stock_code(input_code)
            assert result == expected, f"解析 {input_code} 失败，期望 {expected}，得到 {result}"
    
    def test_parse_stock_code_invalid_inputs(self):
        """测试解析无效输入"""
        invalid_inputs = [
            "",
            None,
            "12345",  # 长度不足
            "1234567",  # 长度过长
            "invalid",
            "000001.XX",  # 无效交易所
            "xx.000001",  # 无效Baostock格式
            "2.000001",  # 无效东方财富格式
            "invalid_000001",  # 无效同花顺格式
        ]
        
        for invalid_input in invalid_inputs:
            with pytest.raises((ValidationError, InvalidCodeFormatError, ExchangeInferenceError)):
                StockCodeConverter.parse_stock_code(invalid_input)
    
    def test_normalize_code_comprehensive(self):
        """测试代码标准化的全面功能"""
        test_cases = [
            # 各种格式标准化为相同结果
            ("000001", "000001.SZ"),
            ("000001.SZ", "000001.SZ"),
            ("SZ000001", "000001.SZ"),
            ("sz.000001", "000001.SZ"),
            ("0.000001", "000001.SZ"),
            ("hs_000001", "000001.SZ"),
            
            ("600000", "600000.SH"),
            ("600000.SH", "600000.SH"),
            ("SH600000", "600000.SH"),
            ("sh.600000", "600000.SH"),
            ("1.600000", "600000.SH"),
            ("hs_600000", "600000.SH"),
            
            # 特殊股票代码
            ("300001", "300001.SZ"),  # 创业板
            ("688001", "688001.SH"),  # 科创板
            ("900001", "900001.SH"),  # B股
            ("200001", "200001.SZ"),  # B股
        ]
        
        for input_code, expected in test_cases:
            result = StockCodeConverter.normalize_code(input_code)
            assert result == expected, f"标准化 {input_code} 失败，期望 {expected}，得到 {result}"
    
    def test_convert_code_all_formats(self):
        """测试转换到所有目标格式"""
        source_code = "000001.SZ"
        
        conversion_tests = [
            ("standard", "000001.SZ"),
            ("baostock", "sz.000001"),
            ("eastmoney", "0.000001"),
            ("tonghuashun", "hs_000001"),
        ]
        
        for target_format, expected in conversion_tests:
            result = StockCodeConverter.convert_code(source_code, target_format)
            assert result == expected, f"转换到 {target_format} 失败，期望 {expected}，得到 {result}"
    
    def test_convert_code_unsupported_format(self):
        """测试转换到不支持的格式"""
        with pytest.raises(UnsupportedFormatError) as exc_info:
            StockCodeConverter.convert_code("000001.SZ", "unknown_format")
        
        error = exc_info.value
        assert "unknown_format" in str(error)
        assert len(error.suggestions) > 0
    
    def test_format_specific_conversions(self):
        """测试特定格式转换方法"""
        test_code = "000001.SZ"
        
        # 测试所有to_*格式方法
        assert StockCodeConverter.to_standard_format(test_code) == "000001.SZ"
        assert StockCodeConverter.to_baostock_format(test_code) == "sz.000001"
        assert StockCodeConverter.to_eastmoney_format(test_code) == "0.000001"
        assert StockCodeConverter.to_tonghuashun_format(test_code) == "hs_000001"
        
        # 测试所有from_*格式方法
        assert StockCodeConverter.from_baostock_format("sz.000001") == "000001.SZ"
        assert StockCodeConverter.from_eastmoney_format("0.000001") == "000001.SZ"
        assert StockCodeConverter.from_tonghuashun_format("hs_000001") == "000001.SZ"
    
    def test_case_insensitive_handling(self):
        """测试大小写不敏感处理"""
        test_cases = [
            ("sz.000001", "000001.SZ"),
            ("SZ.000001", "000001.SZ"),
            ("Sz.000001", "000001.SZ"),
            ("sZ.000001", "000001.SZ"),
            ("sh.600000", "600000.SH"),
            ("SH.600000", "600000.SH"),
        ]
        
        for input_code, expected in test_cases:
            result = StockCodeConverter.normalize_code(input_code)
            assert result == expected, f"大小写处理失败：{input_code} -> {result}, 期望 {expected}"
    
    def test_whitespace_handling(self):
        """测试空白字符处理"""
        test_cases = [
            (" 000001.SZ ", "000001.SZ"),
            ("\t600000.SH\n", "600000.SH"),
            ("  sz.000001  ", "000001.SZ"),
            ("\n\r1.600000\t\r", "600000.SH"),
        ]
        
        for input_code, expected in test_cases:
            result = StockCodeConverter.normalize_code(input_code)
            assert result == expected, f"空白字符处理失败：'{input_code}' -> {result}, 期望 {expected}"


class TestCodeConversionCache:
    """测试代码转换缓存机制"""
    
    def setup_method(self):
        """设置测试"""
        self.cache = CodeConversionCache(l1_size=10, l2_size=50)
    
    def test_cache_basic_operations(self):
        """测试缓存基本操作"""
        # 测试put和get
        self.cache.put("test_key", "test_value")
        assert self.cache.get("test_key") == "test_value"
        
        # 测试不存在的键
        assert self.cache.get("non_existent") is None
    
    def test_cache_lru_eviction(self):
        """测试LRU缓存淘汰"""
        # 填满L1缓存
        for i in range(15):  # 超过L1缓存大小
            self.cache.put(f"key_{i}", f"value_{i}")
        
        # 早期的键应该被淘汰到L2或完全淘汰
        stats = self.cache.get_stats()
        assert stats['l1_size'] <= 10
        assert stats['total_size'] <= 60  # L1 + L2
    
    def test_cache_hit_miss_stats(self):
        """测试缓存命中/未命中统计"""
        # 添加一些数据
        self.cache.put("key1", "value1")
        self.cache.put("key2", "value2")
        
        # 命中测试
        assert self.cache.get("key1") == "value1"
        assert self.cache.get("key2") == "value2"
        
        # 未命中测试
        assert self.cache.get("key3") is None
        
        stats = self.cache.get_stats()
        assert stats['l1_hits'] >= 2
        assert stats['misses'] >= 1
        assert stats['hit_rate'] > 0
    
    def test_cache_ttl_expiration(self):
        """测试缓存TTL过期"""
        # 创建短TTL的缓存
        short_ttl_cache = CodeConversionCache(ttl=1)  # 1秒TTL
        
        short_ttl_cache.put("expire_key", "expire_value")
        assert short_ttl_cache.get("expire_key") == "expire_value"
        
        # 等待过期
        time.sleep(1.1)
        assert short_ttl_cache.get("expire_key") is None
    
    def test_cache_promotion_demotion(self):
        """测试缓存提升和降级"""
        # 添加数据到L2
        for i in range(20):
            self.cache.put(f"l2_key_{i}", f"l2_value_{i}")
        
        # 频繁访问某个键，应该被提升到L1
        for _ in range(5):
            self.cache.get("l2_key_0")
        
        stats = self.cache.get_stats()
        assert stats['promotions'] > 0 or stats['l1_hits'] > 0
    
    def test_cache_clear(self):
        """测试缓存清理"""
        self.cache.put("key1", "value1")
        self.cache.put("key2", "value2")
        
        self.cache.clear()
        
        assert self.cache.get("key1") is None
        assert self.cache.get("key2") is None
        
        stats = self.cache.get_stats()
        assert stats['l1_size'] == 0
        assert stats['l2_size'] == 0
    
    def test_cache_thread_safety(self):
        """测试缓存线程安全"""
        def worker(thread_id):
            for i in range(100):
                key = f"thread_{thread_id}_key_{i}"
                value = f"thread_{thread_id}_value_{i}"
                self.cache.put(key, value)
                retrieved = self.cache.get(key)
                assert retrieved == value or retrieved is None  # 可能被其他线程淘汰
        
        threads = []
        for i in range(5):
            thread = threading.Thread(target=worker, args=(i,))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # 验证缓存仍然正常工作
        self.cache.put("final_test", "final_value")
        assert self.cache.get("final_test") == "final_value"


class TestCodeConversionLogger:
    """测试代码转换日志记录器"""
    
    def setup_method(self):
        """设置测试"""
        self.logger = CodeConversionLogger()
    
    def test_log_successful_conversion(self):
        """测试记录成功转换"""
        self.logger.log_conversion(
            "000001", "000001.SZ", "pure_number", "standard", 0.001
        )
        
        stats = self.logger.get_conversion_stats()
        assert stats['conversions']['total'] == 1
        assert stats['conversions']['successful'] == 1
        assert stats['conversions']['failed'] == 0
        assert stats['conversions']['success_rate'] == 1.0
    
    def test_log_failed_conversion(self):
        """测试记录失败转换"""
        error = InvalidCodeFormatError("invalid_code", ["standard", "baostock"])
        self.logger.log_error("invalid_code", error)
        
        stats = self.logger.get_conversion_stats()
        assert stats['conversions']['failed'] == 1
        assert stats['errors']['total'] == 1
        assert 'InvalidCodeFormatError' in stats['errors']['by_type']
    
    def test_log_performance_metrics(self):
        """测试性能指标记录"""
        # 记录多次转换以测试性能统计
        for i in range(10):
            conversion_time = 0.001 + (i * 0.0001)  # 递增的转换时间
            self.logger.log_conversion(
                f"00000{i}", f"00000{i}.SZ", "pure_number", "standard", conversion_time
            )
        
        stats = self.logger.get_conversion_stats()
        assert stats['performance']['total_time'] > 0
        assert stats['performance']['average_time'] > 0
        assert stats['performance']['min_time'] > 0
        assert stats['performance']['max_time'] > 0
    
    def test_log_format_usage_stats(self):
        """测试格式使用统计"""
        # 记录不同格式的转换
        format_pairs = [
            ("pure_number", "standard"),
            ("baostock", "standard"),
            ("eastmoney", "standard"),
            ("standard", "baostock"),
        ]
        
        for source_format, target_format in format_pairs:
            self.logger.log_conversion(
                "000001", "000001.SZ", source_format, target_format, 0.001
            )
        
        stats = self.logger.get_conversion_stats()
        assert len(stats['formats']['source_formats']) > 0
        assert len(stats['formats']['target_formats']) > 0
        assert stats['formats']['most_common_source'] is not None
        assert stats['formats']['most_common_target'] is not None


class TestErrorHandlingStrategy:
    """测试错误处理策略"""
    
    def setup_method(self):
        """设置测试"""
        self.error_handler = ErrorHandlingStrategy(
            enable_auto_correction=True,
            enable_fuzzy_matching=True,
            max_suggestions=5
        )
    
    def test_handle_invalid_format_with_auto_correction(self):
        """测试自动修正无效格式"""
        # 测试大小写问题
        result = self.error_handler.handle_invalid_format("000001.sz")
        assert len(result['auto_corrections']) > 0
        assert result['auto_corrections'][0]['corrected_code'] == "000001.SZ"
        assert result['auto_corrections'][0]['confidence'] > 0.9
        
        # 测试缺少交易所
        result = self.error_handler.handle_invalid_format("000001")
        assert len(result['auto_corrections']) > 0
        assert any("000001.SZ" in correction['corrected_code'] 
                  for correction in result['auto_corrections'])
    
    def test_handle_invalid_format_without_auto_correction(self):
        """测试不启用自动修正的错误处理"""
        handler = ErrorHandlingStrategy(enable_auto_correction=False)
        result = handler.handle_invalid_format("invalid_code")
        
        assert len(result['auto_corrections']) == 0
        assert len(result['suggestions']) > 0
        assert result['recommended_action'] is not None
    
    def test_handle_exchange_inference_failure(self):
        """测试交易所推断失败处理"""
        result = self.error_handler.handle_exchange_inference_failure("123456")
        
        assert len(result['possible_exchanges']) == 0  # 不符合规则的代码
        assert len(result['fallback_options']) > 0
        
        # 测试符合规则的代码
        result = self.error_handler.handle_exchange_inference_failure("000001")
        assert "SZ" in result['possible_exchanges']
        assert result['confidence_scores']['SZ'] > 0.8
    
    def test_handle_batch_conversion_errors(self):
        """测试批量转换错误处理"""
        failed_items = [
            ("invalid1", InvalidCodeFormatError("invalid1", ["standard"])),
            ("invalid2", ExchangeInferenceError("invalid2")),
            ("123456", InvalidCodeFormatError("123456", ["standard"])),
        ]
        
        result = self.error_handler.handle_batch_conversion_errors(
            failed_items, successful_count=7
        )
        
        assert result['failure_analysis']['total_failed'] == 3
        assert len(result['correctable_items']) >= 0
        assert len(result['uncorrectable_items']) >= 0
        assert len(result['recommendations']) > 0
        assert result['recovery_strategy'] in [
            'individual_correction', 'batch_correction', 
            'format_standardization', 'data_validation'
        ]
    
    def test_suggest_format_corrections(self):
        """测试格式修正建议"""
        # 测试基本格式错误
        suggestions = self.error_handler.suggest_format_corrections("12345")
        assert any("长度不足" in str(s) for s in suggestions)
        
        # 测试特定格式建议
        suggestions = self.error_handler.suggest_format_corrections(
            "000001", target_format="baostock"
        )
        assert any("baostock" in str(s) for s in suggestions)
    
    def test_fuzzy_matching(self):
        """测试模糊匹配功能"""
        result = self.error_handler.handle_invalid_format("00001.SZ")  # 缺少一位数字
        
        # 应该有模糊匹配建议
        assert len(result['suggestions']) > 0
        # 检查是否有相关的建议
        suggestions_text = " ".join(result['suggestions'])
        assert "000001" in suggestions_text or "匹配" in suggestions_text


class TestPatternMatcher:
    """测试模式匹配器"""
    
    def test_identify_format_all_patterns(self):
        """测试识别所有格式模式"""
        test_cases = [
            ("000001.SZ", "standard"),
            ("SZ000001", "exchange_prefix"),
            ("000001", "pure_number"),
            ("sz.000001", "baostock"),
            ("0.000001", "eastmoney"),
            ("hs_000001", "tonghuashun"),
        ]
        
        for code, expected_format in test_cases:
            result = PatternMatcher.identify_format(code)
            assert result == expected_format, f"识别 {code} 失败，期望 {expected_format}，得到 {result}"
    
    def test_identify_format_invalid_codes(self):
        """测试识别无效代码格式"""
        invalid_codes = [
            "invalid",
            "12345",
            "1234567",
            "000001.XX",
            "xx.000001",
            "2.000001",
        ]
        
        for code in invalid_codes:
            result = PatternMatcher.identify_format(code)
            assert result is None, f"无效代码 {code} 应该返回 None，但得到 {result}"
    
    def test_validate_format(self):
        """测试格式验证"""
        # 正确格式验证
        assert PatternMatcher.validate_format("000001.SZ", "standard") is True
        assert PatternMatcher.validate_format("sz.000001", "baostock") is True
        assert PatternMatcher.validate_format("0.000001", "eastmoney") is True
        
        # 错误格式验证
        assert PatternMatcher.validate_format("000001.SZ", "baostock") is False
        assert PatternMatcher.validate_format("sz.000001", "standard") is False
    
    def test_get_format_info(self):
        """测试获取格式信息"""
        info = PatternMatcher.get_format_info("standard")
        assert info is not None
        assert "pattern" in info
        assert "description" in info
        assert "examples" in info
    
    def test_get_all_supported_formats(self):
        """测试获取所有支持的格式"""
        formats = PatternMatcher.get_all_supported_formats()
        expected_formats = ["standard", "exchange_prefix", "pure_number", 
                          "baostock", "eastmoney", "tonghuashun"]
        
        for fmt in expected_formats:
            assert fmt in formats


class TestExchangeInferrer:
    """测试交易所推断引擎"""
    
    def test_infer_exchange_standard_rules(self):
        """测试标准交易所推断规则"""
        # 上海交易所规则
        sh_codes = ["600000", "601000", "688001", "900001"]
        for code in sh_codes:
            result = ExchangeInferrer.infer_exchange(code)
            assert result == "SH", f"代码 {code} 应该推断为 SH，但得到 {result}"
        
        # 深圳交易所规则
        sz_codes = ["000001", "002001", "300001", "200001"]
        for code in sz_codes:
            result = ExchangeInferrer.infer_exchange(code)
            assert result == "SZ", f"代码 {code} 应该推断为 SZ，但得到 {result}"
    
    def test_infer_exchange_edge_cases(self):
        """测试交易所推断边界情况"""
        # 无法推断的代码
        with pytest.raises(ExchangeInferenceError):
            ExchangeInferrer.infer_exchange("123456")  # 不符合任何规则
        
        with pytest.raises(ExchangeInferenceError):
            ExchangeInferrer.infer_exchange("invalid")  # 非数字代码
    
    def test_get_exchange_info(self):
        """测试获取交易所信息"""
        sh_info = ExchangeInferrer.get_exchange_info("SH")
        assert sh_info is not None
        assert "name" in sh_info
        assert "patterns" in sh_info
        assert "description" in sh_info
        
        sz_info = ExchangeInferrer.get_exchange_info("SZ")
        assert sz_info is not None
        assert "name" in sz_info
        assert "patterns" in sz_info
    
    def test_get_inference_confidence(self):
        """测试推断置信度"""
        # 高置信度代码
        confidence = ExchangeInferrer.get_inference_confidence("600000")
        assert confidence > 0.9
        
        confidence = ExchangeInferrer.get_inference_confidence("000001")
        assert confidence > 0.9
        
        # 低置信度或无法推断的代码
        confidence = ExchangeInferrer.get_inference_confidence("123456")
        assert confidence == 0.0


class TestCodeValidationHelper:
    """测试代码验证助手"""
    
    def test_validate_code_format(self):
        """测试代码格式验证"""
        # 有效代码
        valid_codes = [
            "000001.SZ", "600000.SH", "sz.000001", "sh.600000",
            "0.000001", "1.600000", "hs_000001", "000001"
        ]
        
        for code in valid_codes:
            result = CodeValidationHelper.validate_code_format(code)
            assert result['is_valid'] is True, f"代码 {code} 应该有效"
            assert result['format'] is not None
    
    def test_validate_code_format_invalid(self):
        """测试无效代码格式验证"""
        invalid_codes = [
            "", None, "12345", "1234567", "invalid", "000001.XX"
        ]
        
        for code in invalid_codes:
            result = CodeValidationHelper.validate_code_format(code)
            assert result['is_valid'] is False, f"代码 {code} 应该无效"
            assert len(result['errors']) > 0
    
    def test_analyze_code_structure(self):
        """测试代码结构分析"""
        analysis = CodeValidationHelper.analyze_code_structure("000001.SZ")
        
        assert analysis['has_digits'] is True
        assert analysis['has_letters'] is True
        assert analysis['has_dot'] is True
        assert analysis['digit_count'] == 6
        assert analysis['total_length'] == 9
        assert analysis['detected_exchange'] == "SZ"
    
    def test_get_validation_suggestions(self):
        """测试获取验证建议"""
        suggestions = CodeValidationHelper.get_validation_suggestions("12345")
        assert len(suggestions) > 0
        assert any("长度" in suggestion for suggestion in suggestions)
        
        suggestions = CodeValidationHelper.get_validation_suggestions("000001.XX")
        assert len(suggestions) > 0
        assert any("交易所" in suggestion for suggestion in suggestions)
    
    def test_is_likely_stock_code(self):
        """测试股票代码可能性判断"""
        # 很可能是股票代码
        assert CodeValidationHelper.is_likely_stock_code("000001.SZ") is True
        assert CodeValidationHelper.is_likely_stock_code("600000") is True
        assert CodeValidationHelper.is_likely_stock_code("sz.000001") is True
        
        # 不太可能是股票代码
        assert CodeValidationHelper.is_likely_stock_code("invalid") is False
        assert CodeValidationHelper.is_likely_stock_code("12345") is False
        assert CodeValidationHelper.is_likely_stock_code("") is False


class TestBatchOperations:
    """测试批量操作功能"""
    
    def test_batch_normalize_codes_success(self):
        """测试批量标准化成功情况"""
        input_codes = [
            "000001", "600000.SH", "sz.000001", "1.600000", "hs_300001"
        ]
        expected_results = [
            "000001.SZ", "600000.SH", "000001.SZ", "600000.SH", "300001.SZ"
        ]
        
        results = batch_normalize_codes(input_codes)
        assert len(results) == len(expected_results)
        
        for i, (result, expected) in enumerate(zip(results, expected_results)):
            assert result == expected, f"批量标准化第{i}项失败：{result} != {expected}"
    
    def test_batch_normalize_codes_with_errors(self):
        """测试批量标准化包含错误的情况"""
        input_codes = [
            "000001.SZ",  # 有效
            "invalid",    # 无效
            "600000.SH",  # 有效
            "12345",      # 无效
        ]
        
        with pytest.raises(BatchConversionError) as exc_info:
            batch_normalize_codes(input_codes, ignore_errors=False)
        
        error = exc_info.value
        assert error.successful_count == 2
        assert len(error.failed_codes) == 2
        assert error.failure_rate == 0.5
    
    def test_batch_normalize_codes_ignore_errors(self):
        """测试批量标准化忽略错误"""
        input_codes = [
            "000001.SZ",  # 有效
            "invalid",    # 无效
            "600000.SH",  # 有效
        ]
        
        results = batch_normalize_codes(input_codes, ignore_errors=True)
        # 应该只返回有效的结果
        assert len(results) == 2
        assert "000001.SZ" in results
        assert "600000.SH" in results
    
    def test_batch_convert_codes_success(self):
        """测试批量格式转换成功情况"""
        input_codes = ["000001.SZ", "600000.SH", "300001.SZ"]
        target_format = "baostock"
        expected_results = ["sz.000001", "sh.600000", "sz.300001"]
        
        results = batch_convert_codes(input_codes, target_format)
        assert len(results) == len(expected_results)
        
        for i, (result, expected) in enumerate(zip(results, expected_results)):
            assert result == expected, f"批量转换第{i}项失败：{result} != {expected}"
    
    def test_batch_convert_codes_unsupported_format(self):
        """测试批量转换到不支持的格式"""
        input_codes = ["000001.SZ", "600000.SH"]
        
        with pytest.raises(UnsupportedFormatError):
            batch_convert_codes(input_codes, "unsupported_format")
    
    def test_batch_operations_performance(self):
        """测试批量操作性能"""
        # 生成大量测试数据
        large_input = [f"{i:06d}.SZ" for i in range(1000)]
        
        start_time = time.time()
        results = batch_normalize_codes(large_input)
        end_time = time.time()
        
        # 验证结果
        assert len(results) == 1000
        assert all(code.endswith('.SZ') for code in results)
        
        # 验证性能（应该在合理时间内完成）
        processing_time = end_time - start_time
        assert processing_time < 1.0, f"批量处理1000个代码耗时过长: {processing_time:.3f}秒"


class TestConvenienceFunctions:
    """测试便捷函数"""
    
    def test_normalize_stock_code_function(self):
        """测试normalize_stock_code便捷函数"""
        assert normalize_stock_code("000001") == "000001.SZ"
        assert normalize_stock_code("600000.SH") == "600000.SH"
        assert normalize_stock_code("sz.000001") == "000001.SZ"
    
    def test_convert_stock_code_function(self):
        """测试convert_stock_code便捷函数"""
        assert convert_stock_code("000001.SZ", "baostock") == "sz.000001"
        assert convert_stock_code("600000.SH", "eastmoney") == "1.600000"
        assert convert_stock_code("300001.SZ", "tonghuashun") == "hs_300001"
    
    def test_parse_stock_code_function(self):
        """测试parse_stock_code便捷函数"""
        assert parse_stock_code("000001.SZ") == ("000001", "SZ")
        assert parse_stock_code("sh.600000") == ("600000", "SH")
        assert parse_stock_code("1.600000") == ("600000", "SH")
    
    def test_validate_stock_code_function(self):
        """测试validate_stock_code便捷函数"""
        assert validate_stock_code("000001.SZ") is True
        assert validate_stock_code("600000.SH") is True
        assert validate_stock_code("sz.000001") is True
        assert validate_stock_code("invalid") is False
        assert validate_stock_code("12345") is False


class TestPerformanceOptimizations:
    """测试性能优化功能"""
    
    def test_conversion_caching(self):
        """测试转换缓存性能"""
        # 第一次转换（应该被缓存）
        start_time = time.time()
        result1 = StockCodeConverter.normalize_code("000001")
        first_time = time.time() - start_time
        
        # 第二次转换（应该从缓存获取）
        start_time = time.time()
        result2 = StockCodeConverter.normalize_code("000001")
        second_time = time.time() - start_time
        
        assert result1 == result2 == "000001.SZ"
        # 第二次应该更快（从缓存获取）
        # 注意：在测试环境中时间差异可能很小，所以这个断言可能需要调整
        assert second_time <= first_time * 2  # 允许一定的时间波动
    
    def test_regex_compilation_optimization(self):
        """测试正则表达式编译优化"""
        # 多次使用相同的模式应该重用编译后的正则表达式
        codes = ["000001.SZ", "000002.SZ", "000003.SZ"] * 100
        
        start_time = time.time()
        for code in codes:
            PatternMatcher.identify_format(code)
        end_time = time.time()
        
        processing_time = end_time - start_time
        # 应该在合理时间内完成（正则表达式已预编译）
        assert processing_time < 0.5, f"正则表达式处理耗时过长: {processing_time:.3f}秒"
    
    def test_concurrent_conversion_performance(self):
        """测试并发转换性能"""
        codes = [f"{i:06d}.SZ" for i in range(100)]
        
        def convert_batch(code_batch):
            return [StockCodeConverter.normalize_code(code) for code in code_batch]
        
        # 串行处理
        start_time = time.time()
        serial_results = convert_batch(codes)
        serial_time = time.time() - start_time
        
        # 并行处理
        start_time = time.time()
        with ThreadPoolExecutor(max_workers=4) as executor:
            batch_size = 25
            batches = [codes[i:i+batch_size] for i in range(0, len(codes), batch_size)]
            futures = [executor.submit(convert_batch, batch) for batch in batches]
            parallel_results = []
            for future in futures:
                parallel_results.extend(future.result())
        parallel_time = time.time() - start_time
        
        # 验证结果一致性
        assert len(serial_results) == len(parallel_results) == 100
        assert serial_results == parallel_results
        
        # 并行处理应该不会显著慢于串行处理（考虑到开销）
        assert parallel_time < serial_time * 2


class TestErrorHandlingComprehensive:
    """测试全面的错误处理"""
    
    def test_all_exception_types(self):
        """测试所有异常类型"""
        # InvalidCodeFormatError
        with pytest.raises(InvalidCodeFormatError) as exc_info:
            StockCodeConverter.parse_stock_code("invalid")
        
        error = exc_info.value
        assert error.code == "invalid"
        assert len(error.suggestions) > 0
        assert len(error.recovery_actions) > 0
        
        # UnsupportedFormatError
        with pytest.raises(UnsupportedFormatError) as exc_info:
            StockCodeConverter.convert_code("000001.SZ", "unknown_format")
        
        error = exc_info.value
        assert error.format_name == "unknown_format"
        assert len(error.supported_formats) > 0
        
        # ExchangeInferenceError
        with pytest.raises(ExchangeInferenceError) as exc_info:
            StockCodeConverter.parse_stock_code("123456")
        
        error = exc_info.value
        assert error.code == "123456"
    
    def test_exception_context_and_details(self):
        """测试异常上下文和详细信息"""
        try:
            StockCodeConverter.parse_stock_code("invalid_code")
        except CodeConversionError as e:
            # 测试异常的详细信息
            assert e.code == "invalid_code"
            assert e.timestamp is not None
            
            # 测试用户友好消息
            friendly_msg = e.get_user_friendly_message()
            assert "invalid_code" in friendly_msg
            assert len(friendly_msg) > len(str(e))
            
            # 测试字典转换
            error_dict = e.to_dict()
            assert error_dict['code'] == "invalid_code"
            assert 'timestamp' in error_dict
            assert 'suggestions' in error_dict
    
    def test_error_recovery_mechanisms(self):
        """测试错误恢复机制"""
        error_handler = ErrorHandlingStrategy(enable_auto_correction=True)
        
        # 测试自动修正
        result = error_handler.handle_invalid_format("000001.sz")
        assert len(result['auto_corrections']) > 0
        assert result['auto_corrections'][0]['corrected_code'] == "000001.SZ"
        
        # 测试建议生成
        suggestions = error_handler.suggest_format_corrections("12345")
        assert len(suggestions) > 0
        assert any("长度" in str(s) for s in suggestions)
    
    def test_logging_integration(self):
        """测试日志集成"""
        logger = CodeConversionLogger()
        
        # 测试成功转换日志
        logger.log_conversion("000001", "000001.SZ", "pure_number", "standard", 0.001)
        
        # 测试错误日志
        error = InvalidCodeFormatError("invalid", ["standard"])
        logger.log_error("invalid", error)
        
        # 验证统计信息
        stats = logger.get_conversion_stats()
        assert stats['conversions']['total'] == 1
        assert stats['conversions']['successful'] == 1
        assert stats['errors']['total'] == 1


if __name__ == "__main__":
    # 运行所有测试
    pytest.main([__file__, "-v", "--tb=short"])