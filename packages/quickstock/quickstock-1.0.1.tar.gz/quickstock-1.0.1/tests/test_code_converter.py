"""
股票代码转换器测试
"""

import pytest
from quickstock.utils.code_converter import StockCodeConverter, normalize_stock_code, convert_stock_code
from quickstock.core.errors import ValidationError


class TestStockCodeConverter:
    """股票代码转换器测试类"""
    
    def test_parse_standard_format(self):
        """测试解析标准格式代码"""
        code, exchange = StockCodeConverter.parse_stock_code("000001.SZ")
        assert code == "000001"
        assert exchange == "SZ"
        
        code, exchange = StockCodeConverter.parse_stock_code("600000.SH")
        assert code == "600000"
        assert exchange == "SH"
    
    def test_parse_exchange_prefix_format(self):
        """测试解析交易所前缀格式"""
        code, exchange = StockCodeConverter.parse_stock_code("SZ000001")
        assert code == "000001"
        assert exchange == "SZ"
        
        code, exchange = StockCodeConverter.parse_stock_code("SH600000")
        assert code == "600000"
        assert exchange == "SH"
    
    def test_parse_pure_number_format(self):
        """测试解析纯数字格式"""
        # 深圳股票
        code, exchange = StockCodeConverter.parse_stock_code("000001")
        assert code == "000001"
        assert exchange == "SZ"
        
        # 上海股票
        code, exchange = StockCodeConverter.parse_stock_code("600000")
        assert code == "600000"
        assert exchange == "SH"
        
        # 创业板
        code, exchange = StockCodeConverter.parse_stock_code("300001")
        assert code == "300001"
        assert exchange == "SZ"
    
    def test_parse_invalid_format(self):
        """测试解析无效格式"""
        with pytest.raises(ValidationError):
            StockCodeConverter.parse_stock_code("invalid")
        
        with pytest.raises(ValidationError):
            StockCodeConverter.parse_stock_code("")
        
        with pytest.raises(ValidationError):
            StockCodeConverter.parse_stock_code("12345")  # 不足6位
    
    def test_to_standard_format(self):
        """测试转换为标准格式"""
        assert StockCodeConverter.to_standard_format("000001") == "000001.SZ"
        assert StockCodeConverter.to_standard_format("600000") == "600000.SH"
        assert StockCodeConverter.to_standard_format("SZ000001") == "000001.SZ"
        assert StockCodeConverter.to_standard_format("000001.SZ") == "000001.SZ"
    
    def test_to_baostock_format(self):
        """测试转换为Baostock格式"""
        assert StockCodeConverter.to_baostock_format("000001.SZ") == "sz.000001"
        assert StockCodeConverter.to_baostock_format("600000.SH") == "sh.600000"
        assert StockCodeConverter.to_baostock_format("000001") == "sz.000001"
        assert StockCodeConverter.to_baostock_format("600000") == "sh.600000"
    
    def test_to_eastmoney_format(self):
        """测试转换为东方财富格式"""
        assert StockCodeConverter.to_eastmoney_format("000001.SZ") == "0.000001"
        assert StockCodeConverter.to_eastmoney_format("600000.SH") == "1.600000"
        assert StockCodeConverter.to_eastmoney_format("000001") == "0.000001"
        assert StockCodeConverter.to_eastmoney_format("600000") == "1.600000"
    
    def test_to_tonghuashun_format(self):
        """测试转换为同花顺格式"""
        assert StockCodeConverter.to_tonghuashun_format("000001.SZ") == "hs_000001"
        assert StockCodeConverter.to_tonghuashun_format("600000.SH") == "hs_600000"
        assert StockCodeConverter.to_tonghuashun_format("000001") == "hs_000001"
        assert StockCodeConverter.to_tonghuashun_format("600000") == "hs_600000"
    
    def test_from_baostock_format(self):
        """测试从Baostock格式转换"""
        assert StockCodeConverter.from_baostock_format("sz.000001") == "000001.SZ"
        assert StockCodeConverter.from_baostock_format("sh.600000") == "600000.SH"
        
        with pytest.raises(ValidationError):
            StockCodeConverter.from_baostock_format("invalid.format")
    
    def test_from_eastmoney_format(self):
        """测试从东方财富格式转换"""
        assert StockCodeConverter.from_eastmoney_format("0.000001") == "000001.SZ"
        assert StockCodeConverter.from_eastmoney_format("1.600000") == "600000.SH"
        
        with pytest.raises(ValidationError):
            StockCodeConverter.from_eastmoney_format("2.000001")  # 无效的交易所代码
    
    def test_from_tonghuashun_format(self):
        """测试从同花顺格式转换"""
        assert StockCodeConverter.from_tonghuashun_format("hs_000001") == "000001.SZ"
        assert StockCodeConverter.from_tonghuashun_format("hs_600000") == "600000.SH"
        
        with pytest.raises(ValidationError):
            StockCodeConverter.from_tonghuashun_format("invalid_format")
    
    def test_convert_code(self):
        """测试通用代码转换"""
        code = "000001.SZ"
        
        assert StockCodeConverter.convert_code(code, "standard") == "000001.SZ"
        assert StockCodeConverter.convert_code(code, "baostock") == "sz.000001"
        assert StockCodeConverter.convert_code(code, "eastmoney") == "0.000001"
        assert StockCodeConverter.convert_code(code, "tonghuashun") == "hs_000001"
        
        with pytest.raises(ValidationError):
            StockCodeConverter.convert_code(code, "invalid_format")
    
    def test_normalize_code(self):
        """测试代码标准化"""
        # 各种格式都应该标准化为相同结果
        test_cases = [
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
        ]
        
        for input_code, expected in test_cases:
            result = StockCodeConverter.normalize_code(input_code)
            assert result == expected, f"输入: {input_code}, 期望: {expected}, 实际: {result}"


class TestConvenienceFunctions:
    """便捷函数测试"""
    
    def test_normalize_stock_code(self):
        """测试标准化函数"""
        assert normalize_stock_code("sz.000001") == "000001.SZ"
        assert normalize_stock_code("1.600000") == "600000.SH"
    
    def test_convert_stock_code(self):
        """测试转换函数"""
        assert convert_stock_code("000001.SZ", "baostock") == "sz.000001"
        assert convert_stock_code("600000.SH", "eastmoney") == "1.600000"


class TestEdgeCases:
    """边界情况测试"""
    
    def test_case_insensitive(self):
        """测试大小写不敏感"""
        assert StockCodeConverter.normalize_code("sz.000001") == "000001.SZ"
        assert StockCodeConverter.normalize_code("SZ.000001") == "000001.SZ"
        assert StockCodeConverter.normalize_code("Sz.000001") == "000001.SZ"
    
    def test_whitespace_handling(self):
        """测试空白字符处理"""
        assert StockCodeConverter.normalize_code(" 000001.SZ ") == "000001.SZ"
        assert StockCodeConverter.normalize_code("\t600000.SH\n") == "600000.SH"
    
    def test_special_stock_codes(self):
        """测试特殊股票代码"""
        # 科创板
        assert StockCodeConverter.normalize_code("688001") == "688001.SH"
        
        # 创业板
        assert StockCodeConverter.normalize_code("300001") == "300001.SZ"
        
        # B股
        assert StockCodeConverter.normalize_code("900001") == "900001.SH"
        assert StockCodeConverter.normalize_code("200001") == "200001.SZ"


class TestRealWorldExamples:
    """真实世界示例测试"""
    
    def test_common_stocks(self):
        """测试常见股票代码"""
        # 平安银行
        test_codes = ["000001", "000001.SZ", "SZ000001", "sz.000001", "0.000001", "hs_000001"]
        for code in test_codes:
            assert normalize_stock_code(code) == "000001.SZ"
        
        # 浦发银行
        test_codes = ["600000", "600000.SH", "SH600000", "sh.600000", "1.600000", "hs_600000"]
        for code in test_codes:
            assert normalize_stock_code(code) == "600000.SH"
    
    def test_cross_format_conversion(self):
        """测试跨格式转换"""
        # 从Baostock格式转换到其他格式
        baostock_code = "sz.000001"
        assert convert_stock_code(baostock_code, "standard") == "000001.SZ"
        assert convert_stock_code(baostock_code, "eastmoney") == "0.000001"
        assert convert_stock_code(baostock_code, "tonghuashun") == "hs_000001"
        
        # 从东方财富格式转换到其他格式
        eastmoney_code = "1.600000"
        assert convert_stock_code(eastmoney_code, "standard") == "600000.SH"
        assert convert_stock_code(eastmoney_code, "baostock") == "sh.600000"
        assert convert_stock_code(eastmoney_code, "tonghuashun") == "hs_600000"