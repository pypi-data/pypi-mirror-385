"""
测试增强的股票代码验证和错误处理功能

测试task 2.3的实现：智能代码验证和错误提示
"""

import pytest
from quickstock.utils.code_converter import (
    StockCodeConverter, 
    CodeConversionError,
    InvalidCodeFormatError,
    UnsupportedFormatError,
    ExchangeInferenceError,
    CodeValidationHelper
)
from quickstock.client import QuickStockClient
from quickstock.core.errors import ValidationError


class TestCodeConversionErrors:
    """测试代码转换异常类"""
    
    def test_code_conversion_error_basic(self):
        """测试基础代码转换异常"""
        error = CodeConversionError(
            "测试错误",
            code="invalid_code",
            suggestions=["建议1", "建议2"]
        )
        
        assert error.code == "invalid_code"
        assert error.suggestions == ["建议1", "建议2"]
        assert "invalid_code" in error.get_user_friendly_message()
        assert "建议1" in error.get_user_friendly_message()
    
    def test_invalid_code_format_error(self):
        """测试无效格式异常"""
        error = InvalidCodeFormatError(
            "invalid_code",
            supported_formats=['standard', 'baostock'],
            detected_issues=["长度不足", "缺少交易所"]
        )
        
        assert error.code == "invalid_code"
        assert "长度不足" in error.suggestions
        assert "标准格式" in error.get_user_friendly_message()
    
    def test_unsupported_format_error(self):
        """测试不支持格式异常"""
        error = UnsupportedFormatError(
            "unknown_format",
            ['standard', 'baostock']
        )
        
        assert "unknown_format" in str(error)
        assert "standard, baostock" in error.get_user_friendly_message()
    
    def test_exchange_inference_error(self):
        """测试交易所推断异常"""
        error = ExchangeInferenceError("123456")
        
        assert error.code == "123456"
        assert "123456.SH" in error.get_user_friendly_message()
        assert "123456.SZ" in error.get_user_friendly_message()


class TestCodeValidationHelper:
    """测试代码验证助手"""
    
    def test_validate_valid_codes(self):
        """测试有效代码验证"""
        valid_codes = [
            "000001.SZ",
            "600000.SH",
            "sz.000001",
            "1.600000",
            "hs_000001"
        ]
        
        for code in valid_codes:
            is_valid, issues, suggestions = CodeValidationHelper.validate_and_suggest(code)
            assert is_valid, f"代码 {code} 应该是有效的"
            assert len(issues) == 0, f"代码 {code} 不应该有问题"
    
    def test_validate_invalid_codes(self):
        """测试无效代码验证"""
        invalid_cases = [
            ("", ["代码不能为空"]),
            ("12345", ["代码长度过短"]),
            ("invalid@code", ["包含无效字符"]),
            ("abcdef", ["缺少数字部分"]),
        ]
        
        for code, expected_issues in invalid_cases:
            is_valid, issues, suggestions = CodeValidationHelper.validate_and_suggest(code)
            assert not is_valid, f"代码 {code} 应该是无效的"
            assert len(issues) > 0, f"代码 {code} 应该有问题"
            
            # 检查是否包含预期的问题（使用部分匹配）
            for expected_issue in expected_issues:
                assert any(expected_issue in issue for issue in issues), \
                    f"应该检测到问题: {expected_issue}，实际问题: {issues}"
    
    def test_get_detailed_validation_result(self):
        """测试详细验证结果"""
        # 测试有效代码
        result = CodeValidationHelper.get_detailed_validation_result("000001.SZ")
        assert result['is_valid'] is True
        assert result['detected_format'] == 'standard'
        assert result['parsed_code'] == '000001'
        assert result['parsed_exchange'] == 'SZ'
        
        # 测试无效代码
        result = CodeValidationHelper.get_detailed_validation_result("invalid")
        assert result['is_valid'] is False
        assert len(result['issues']) > 0
        assert len(result['suggestions']) > 0


class TestEnhancedStockCodeConverter:
    """测试增强的股票代码转换器"""
    
    def test_normalize_code_with_enhanced_errors(self):
        """测试带增强错误处理的代码标准化"""
        # 测试有效代码
        assert StockCodeConverter.normalize_code("000001.SZ") == "000001.SZ"
        assert StockCodeConverter.normalize_code("sz.000001") == "000001.SZ"
        
        # 测试无效代码抛出增强异常
        with pytest.raises(InvalidCodeFormatError) as exc_info:
            StockCodeConverter.normalize_code("invalid_code")
        
        error = exc_info.value
        assert error.code == "invalid_code"
        assert len(error.suggestions) > 0
        assert "invalid_code" in error.get_user_friendly_message()
    
    def test_convert_code_with_enhanced_errors(self):
        """测试带增强错误处理的代码转换"""
        # 测试有效转换
        result = StockCodeConverter.convert_code("000001.SZ", "baostock")
        assert result == "sz.000001"
        
        # 测试不支持的格式
        with pytest.raises(UnsupportedFormatError) as exc_info:
            StockCodeConverter.convert_code("000001.SZ", "unknown_format")
        
        error = exc_info.value
        assert "unknown_format" in str(error)
        assert len(error.suggestions) > 0
    
    def test_exchange_inference_with_enhanced_errors(self):
        """测试带增强错误处理的交易所推断"""
        # 测试可推断的代码
        assert StockCodeConverter.normalize_code("000001") == "000001.SZ"
        assert StockCodeConverter.normalize_code("600000") == "600000.SH"
        
        # 测试无法推断的代码
        with pytest.raises(ExchangeInferenceError) as exc_info:
            StockCodeConverter.normalize_code("999999")  # 假设这个代码无法推断
        
        # 注意：这个测试可能需要根据实际的推断规则调整
    
    def test_validate_code_with_details(self):
        """测试详细代码验证"""
        # 测试有效代码
        result = StockCodeConverter.validate_code_with_details("000001.SZ")
        assert result['is_valid'] is True
        assert result['detected_format'] == 'standard'
        
        # 测试无效代码
        result = StockCodeConverter.validate_code_with_details("invalid")
        assert result['is_valid'] is False
        assert len(result['issues']) > 0
        assert len(result['suggestions']) > 0
    
    def test_get_format_help(self):
        """测试格式帮助信息"""
        # 测试获取所有格式帮助
        all_help = StockCodeConverter.get_format_help()
        assert 'standard' in all_help
        assert 'baostock' in all_help
        assert all_help['standard']['name'] == '标准格式'
        
        # 测试获取特定格式帮助
        standard_help = StockCodeConverter.get_format_help('standard')
        assert standard_help['name'] == '标准格式'
        assert '000001.SZ' in standard_help['examples']
    
    def test_suggest_auto_correction(self):
        """测试自动修正建议"""
        # 测试大小写修正
        result = StockCodeConverter.suggest_auto_correction("000001.sz")
        assert result['can_auto_correct'] is True
        assert len(result['corrections']) > 0
        assert result['corrections'][0]['corrected'] == "000001.SZ"
        
        # 测试添加交易所后缀
        result = StockCodeConverter.suggest_auto_correction("000001")
        assert result['can_auto_correct'] is True
        corrections = result['corrections']
        assert any(c['corrected'] == "000001.SZ" for c in corrections)
        
        # 测试格式转换
        result = StockCodeConverter.suggest_auto_correction("SZ000001")
        assert result['can_auto_correct'] is True
        assert any(c['corrected'] == "000001.SZ" for c in corrections)
    
    def test_get_validation_help(self):
        """测试验证帮助信息"""
        help_info = StockCodeConverter.get_validation_help()
        
        assert 'supported_formats' in help_info
        assert 'validation_rules' in help_info
        assert 'common_errors' in help_info
        assert 'examples' in help_info
        
        # 检查内容结构
        assert 'valid' in help_info['examples']
        assert 'invalid' in help_info['examples']
        assert len(help_info['examples']['valid']) > 0
        assert len(help_info['examples']['invalid']) > 0
    
    def test_batch_convert_with_enhanced_errors(self):
        """测试批量转换的增强错误处理"""
        codes = ["000001.SZ", "invalid_code", "600000.SH"]
        
        results, errors = StockCodeConverter.batch_convert_codes_with_errors(codes)
        
        # 应该有2个成功结果
        assert len(results) == 2
        assert results[0]['original'] == "000001.SZ"
        assert results[1]['original'] == "600000.SH"
        
        # 应该有1个错误
        assert len(errors) == 1
        error = errors[0]
        assert error['original'] == "invalid_code"
        assert 'error_type' in error
        assert 'suggestions' in error
        assert 'user_friendly_message' in error


class TestEnhancedQuickStockClient:
    """测试增强的QuickStock客户端"""
    
    def setup_method(self):
        """设置测试"""
        self.client = QuickStockClient()
    
    def test_validate_code_with_details(self):
        """测试详细代码验证"""
        # 测试有效代码
        result = self.client.validate_code_with_details("000001.SZ")
        assert result['is_valid'] is True
        assert result['detected_format'] == 'standard'
        
        # 测试无效代码
        result = self.client.validate_code_with_details("invalid")
        assert result['is_valid'] is False
        assert len(result['suggestions']) > 0
    
    def test_get_code_format_help(self):
        """测试格式帮助"""
        # 测试获取所有格式帮助
        all_help = self.client.get_code_format_help()
        assert 'standard' in all_help
        assert 'baostock' in all_help
        
        # 测试获取特定格式帮助
        standard_help = self.client.get_code_format_help('standard')
        assert standard_help['name'] == '标准格式'
    
    def test_suggest_code_auto_correction(self):
        """测试自动修正建议"""
        result = self.client.suggest_code_auto_correction("000001.sz")
        assert result['can_auto_correct'] is True
        assert len(result['corrections']) > 0
    
    def test_get_validation_help(self):
        """测试验证帮助"""
        help_info = self.client.get_validation_help()
        assert 'supported_formats' in help_info
        assert 'validation_rules' in help_info
        assert 'common_errors' in help_info
    
    def test_batch_validate_codes(self):
        """测试批量验证"""
        codes = ["000001.SZ", "invalid", "600000.SH"]
        valid, invalid = self.client.batch_validate_codes(codes)
        
        assert len(valid) == 2
        assert len(invalid) == 1
        assert invalid[0]['original'] == "invalid"
    
    def test_enhanced_validate_and_normalize_code(self):
        """测试增强的内部验证方法"""
        # 测试有效代码
        result = self.client._validate_and_normalize_code("000001.SZ")
        assert result == "000001.SZ"
        
        # 测试无效代码应该抛出增强的错误信息
        with pytest.raises(ValidationError) as exc_info:
            self.client._validate_and_normalize_code("invalid_code")
        
        error_msg = str(exc_info.value)
        assert "股票代码验证失败" in error_msg or "股票代码格式无效" in error_msg


class TestIntegrationWithDataMethods:
    """测试与数据获取方法的集成"""
    
    def setup_method(self):
        """设置测试"""
        self.client = QuickStockClient()
    
    def test_stock_daily_with_enhanced_validation(self):
        """测试股票日线数据获取的增强验证"""
        # 这个测试可能需要mock数据源，这里只测试验证部分
        
        # 测试无效代码应该给出更好的错误信息
        from quickstock.core.errors import QuickStockError
        with pytest.raises(QuickStockError) as exc_info:
            # 使用一个明显无效的代码
            self.client.stock_daily("invalid_code_format")
        
        # 错误信息应该包含建议
        error_msg = str(exc_info.value)
        # 由于我们增强了_validate_and_normalize_code方法，
        # 错误信息应该更加详细
        assert len(error_msg) > 50  # 应该有详细的错误信息
        assert "股票代码验证失败" in error_msg
        assert "建议尝试" in error_msg  # 应该包含建议信息
        assert "标准格式" in error_msg  # 应该包含格式说明
    
    def test_multiple_format_support_in_data_methods(self):
        """测试数据方法支持多种格式"""
        # 这个测试需要mock数据源，这里只测试代码标准化部分
        
        test_codes = [
            "000001.SZ",
            "sz.000001", 
            "0.000001",
            "hs_000001"
        ]
        
        for code in test_codes:
            try:
                # 测试代码能够被正确标准化
                normalized = self.client.normalize_code(code)
                assert normalized.endswith('.SZ') or normalized.endswith('.SH')
            except Exception as e:
                pytest.fail(f"代码 {code} 标准化失败: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])