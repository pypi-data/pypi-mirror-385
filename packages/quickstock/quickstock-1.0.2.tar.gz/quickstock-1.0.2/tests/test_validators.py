"""
参数验证器测试
"""

import pytest
from datetime import datetime

from quickstock.utils.validators import (
    ValidationError,
    validate_stock_code,
    validate_date_format,
    validate_date_range,
    validate_frequency,
    validate_numeric_range,
    validate_list_length,
    validate_fields,
    validate_params,
    validate_data_request,
    StockDataValidator,
    IndexDataValidator,
    FundDataValidator,
    TradeCalValidator
)


class TestBasicValidators:
    """基础验证器测试类"""
    
    def test_validate_stock_code_valid(self):
        """测试有效股票代码"""
        # 6位数字代码
        assert validate_stock_code('000001') == True
        assert validate_stock_code('600000') == True
        
        # 带交易所后缀
        assert validate_stock_code('000001.SZ') == True
        assert validate_stock_code('600000.SH') == True
        
        # 交易所前缀
        assert validate_stock_code('SZ000001') == True
        assert validate_stock_code('SH600000') == True
    
    def test_validate_stock_code_invalid(self):
        """测试无效股票代码"""
        # 空值
        with pytest.raises(ValidationError, match="股票代码不能为空"):
            validate_stock_code('')
        
        with pytest.raises(ValidationError, match="股票代码不能为空"):
            validate_stock_code(None)
        
        # 非字符串
        with pytest.raises(ValidationError, match="必须为字符串"):
            validate_stock_code(123456)
        
        # 格式错误
        with pytest.raises(ValidationError, match="无效的股票代码格式"):
            validate_stock_code('12345')  # 5位数字
        
        with pytest.raises(ValidationError, match="无效的股票代码格式"):
            validate_stock_code('1234567')  # 7位数字
        
        with pytest.raises(ValidationError, match="无效的股票代码格式"):
            validate_stock_code('000001.XX')  # 无效交易所
    
    def test_validate_date_format_valid(self):
        """测试有效日期格式"""
        # YYYYMMDD格式
        assert validate_date_format('20231201') == True
        
        # YYYY-MM-DD格式
        assert validate_date_format('2023-12-01') == True
        
        # YYYY/MM/DD格式
        assert validate_date_format('2023/12/01') == True
        
        # YYYY.MM.DD格式
        assert validate_date_format('2023.12.01') == True
        
        # 允许空值
        assert validate_date_format('', allow_empty=True) == True
        assert validate_date_format(None, allow_empty=True) == True
    
    def test_validate_date_format_invalid(self):
        """测试无效日期格式"""
        # 空值但不允许
        with pytest.raises(ValidationError, match="日期不能为空"):
            validate_date_format('')
        
        with pytest.raises(ValidationError, match="日期不能为空"):
            validate_date_format(None)
        
        # 非字符串
        with pytest.raises(ValidationError, match="日期必须为字符串格式"):
            validate_date_format(20231201)
        
        # 格式错误
        with pytest.raises(ValidationError, match="无效的日期格式"):
            validate_date_format('2023-13-01')  # 无效月份
        
        with pytest.raises(ValidationError, match="无效的日期格式"):
            validate_date_format('2023/02/30')  # 无效日期
        
        with pytest.raises(ValidationError, match="无效的日期格式"):
            validate_date_format('invalid_date')
    
    def test_validate_date_range_valid(self):
        """测试有效日期范围"""
        # 正常范围
        assert validate_date_range('20231201', '20231231') == True
        assert validate_date_range('2023-12-01', '2023-12-31') == True
        
        # 相同日期
        assert validate_date_range('20231201', '20231201') == True
        
        # 只有开始日期
        assert validate_date_range('20231201', '') == True
        
        # 只有结束日期
        assert validate_date_range('', '20231231') == True
        
        # 都为空
        assert validate_date_range('', '') == True
    
    def test_validate_date_range_invalid(self):
        """测试无效日期范围"""
        # 开始日期大于结束日期
        with pytest.raises(ValidationError, match="开始日期不能大于结束日期"):
            validate_date_range('20231231', '20231201')
        
        # 无效日期格式
        with pytest.raises(ValidationError, match="无效的日期格式"):
            validate_date_range('invalid_date', '20231231')
    
    def test_validate_frequency_valid(self):
        """测试有效频率"""
        valid_freqs = ['1min', '5min', '15min', '30min', '60min', 
                      '1d', 'daily', '1w', 'weekly', '1m', 'monthly']
        
        for freq in valid_freqs:
            assert validate_frequency(freq) == True
            assert validate_frequency(freq.upper()) == True  # 测试大小写不敏感
    
    def test_validate_frequency_invalid(self):
        """测试无效频率"""
        # 空值
        with pytest.raises(ValidationError, match="频率不能为空"):
            validate_frequency('')
        
        with pytest.raises(ValidationError, match="频率不能为空"):
            validate_frequency(None)
        
        # 非字符串
        with pytest.raises(ValidationError, match="必须为字符串"):
            validate_frequency(1)
        
        # 不支持的频率
        with pytest.raises(ValidationError, match="不支持的频率"):
            validate_frequency('2min')
        
        with pytest.raises(ValidationError, match="不支持的频率"):
            validate_frequency('invalid_freq')
    
    def test_validate_numeric_range_valid(self):
        """测试有效数值范围"""
        # 整数
        assert validate_numeric_range(5, min_val=0, max_val=10) == True
        
        # 浮点数
        assert validate_numeric_range(5.5, min_val=0.0, max_val=10.0) == True
        
        # 边界值
        assert validate_numeric_range(0, min_val=0, max_val=10) == True
        assert validate_numeric_range(10, min_val=0, max_val=10) == True
        
        # 无限制
        assert validate_numeric_range(100) == True
    
    def test_validate_numeric_range_invalid(self):
        """测试无效数值范围"""
        # 非数值类型
        with pytest.raises(ValidationError, match="必须为数值类型"):
            validate_numeric_range('not_a_number')
        
        # NaN值
        with pytest.raises(ValidationError, match="不能为NaN或无穷大"):
            validate_numeric_range(float('nan'))
        
        # 无穷大值
        with pytest.raises(ValidationError, match="不能为NaN或无穷大"):
            validate_numeric_range(float('inf'))
        
        # 超出最小值
        with pytest.raises(ValidationError, match="不能小于"):
            validate_numeric_range(-1, min_val=0)
        
        # 超出最大值
        with pytest.raises(ValidationError, match="不能大于"):
            validate_numeric_range(11, max_val=10)
    
    def test_validate_list_length_valid(self):
        """测试有效列表长度"""
        # 正常列表
        assert validate_list_length([1, 2, 3], min_length=1, max_length=5) == True
        
        # 边界值
        assert validate_list_length([1], min_length=1, max_length=5) == True
        assert validate_list_length([1, 2, 3, 4, 5], min_length=1, max_length=5) == True
        
        # 空列表
        assert validate_list_length([], min_length=0) == True
    
    def test_validate_list_length_invalid(self):
        """测试无效列表长度"""
        # 非列表类型
        with pytest.raises(ValidationError, match="必须为列表类型"):
            validate_list_length('not_a_list')
        
        # 长度不足
        with pytest.raises(ValidationError, match="长度不能小于"):
            validate_list_length([], min_length=1)
        
        # 长度超出
        with pytest.raises(ValidationError, match="长度不能大于"):
            validate_list_length([1, 2, 3, 4, 5, 6], max_length=5)
    
    def test_validate_fields_valid(self):
        """测试有效字段验证"""
        valid_fields = ['open', 'high', 'low', 'close', 'volume']
        
        # None值
        assert validate_fields(None, valid_fields) == True
        
        # 有效字段
        assert validate_fields(['open', 'close'], valid_fields) == True
        
        # 所有字段
        assert validate_fields(valid_fields, valid_fields) == True
    
    def test_validate_fields_invalid(self):
        """测试无效字段验证"""
        valid_fields = ['open', 'high', 'low', 'close', 'volume']
        
        # 非列表类型
        with pytest.raises(ValidationError, match="必须为列表类型"):
            validate_fields('not_a_list', valid_fields)
        
        # 无效字段
        with pytest.raises(ValidationError, match="无效的字段"):
            validate_fields(['open', 'invalid_field'], valid_fields)


class TestValidateParams:
    """参数验证装饰器测试类"""
    
    def test_validate_params_decorator_success(self):
        """测试参数验证装饰器成功情况"""
        @validate_params(
            code=validate_stock_code,
            date=lambda x: validate_date_format(x, allow_empty=True)
        )
        def test_function(code: str, date: str = None):
            return f"{code}_{date}"
        
        # 有效参数
        result = test_function('000001', '20231201')
        assert result == '000001_20231201'
        
        # 默认参数
        result = test_function('000001')
        assert result == '000001_None'
    
    def test_validate_params_decorator_failure(self):
        """测试参数验证装饰器失败情况"""
        @validate_params(
            code=validate_stock_code
        )
        def test_function(code: str):
            return code
        
        # 无效参数
        with pytest.raises(ValidationError, match="参数 code 验证失败"):
            test_function('invalid_code')


class TestDataRequestValidator:
    """数据请求验证器测试类"""
    
    def test_validate_data_request_valid(self):
        """测试有效数据请求"""
        # 股票基础信息
        assert validate_data_request('stock_basic') == True
        
        # 股票日线数据
        assert validate_data_request('stock_daily', ts_code='000001', 
                                   start_date='20231201', end_date='20231231') == True
        
        # 带频率的请求
        assert validate_data_request('stock_minute', ts_code='000001', freq='1min') == True
    
    def test_validate_data_request_invalid(self):
        """测试无效数据请求"""
        # 无效数据类型
        with pytest.raises(ValidationError, match="不支持的数据类型"):
            validate_data_request('invalid_type')
        
        # 无效股票代码
        with pytest.raises(ValidationError, match="无效的股票代码格式"):
            validate_data_request('stock_daily', ts_code='invalid_code')
        
        # 无效日期范围
        with pytest.raises(ValidationError, match="开始日期不能大于结束日期"):
            validate_data_request('stock_daily', start_date='20231231', end_date='20231201')
        
        # 无效频率
        with pytest.raises(ValidationError, match="不支持的频率"):
            validate_data_request('stock_minute', freq='invalid_freq')


class TestSpecificValidators:
    """特定验证器测试类"""
    
    def test_stock_data_validator(self):
        """测试股票数据验证器"""
        # 基础信息请求
        assert StockDataValidator.validate_basic_request() == True
        
        # 日线数据请求
        assert StockDataValidator.validate_daily_request('000001') == True
        
        # 分钟数据请求
        assert StockDataValidator.validate_minute_request('000001', '1min') == True
        
        # 无效请求
        with pytest.raises(ValidationError):
            StockDataValidator.validate_daily_request('invalid_code')
    
    def test_index_data_validator(self):
        """测试指数数据验证器"""
        # 基础信息请求
        assert IndexDataValidator.validate_basic_request() == True
        
        # 日线数据请求
        assert IndexDataValidator.validate_daily_request('000001.SH') == True
    
    def test_fund_data_validator(self):
        """测试基金数据验证器"""
        # 基础信息请求
        assert FundDataValidator.validate_basic_request() == True
        
        # 净值数据请求
        assert FundDataValidator.validate_nav_request('110022') == True
    
    def test_trade_cal_validator(self):
        """测试交易日历验证器"""
        # 基本请求
        assert TradeCalValidator.validate_request() == True
        
        # 带日期范围的请求
        assert TradeCalValidator.validate_request('20231201', '20231231') == True
        
        # 无效日期范围
        with pytest.raises(ValidationError):
            TradeCalValidator.validate_request('20231231', '20231201')


class TestEdgeCases:
    """边界情况测试类"""
    
    def test_empty_and_none_values(self):
        """测试空值和None值处理"""
        # 空字符串
        with pytest.raises(ValidationError):
            validate_stock_code('')
        
        # None值
        with pytest.raises(ValidationError):
            validate_stock_code(None)
        
        # 空白字符串
        with pytest.raises(ValidationError):
            validate_stock_code('   ')
    
    def test_case_sensitivity(self):
        """测试大小写敏感性"""
        # 股票代码大小写
        assert validate_stock_code('000001.sz') == True  # 小写交易所
        assert validate_stock_code('sh600000') == True   # 小写交易所
        
        # 频率大小写
        assert validate_frequency('1MIN') == True
        assert validate_frequency('Daily') == True
    
    def test_whitespace_handling(self):
        """测试空白字符处理"""
        # 股票代码前后空格
        assert validate_stock_code('  000001  ') == True
        
        # 日期前后空格
        assert validate_date_format('  20231201  ') == True
    
    def test_unicode_handling(self):
        """测试Unicode字符处理"""
        # 中文字符在股票代码中应该失败
        with pytest.raises(ValidationError):
            validate_stock_code('平安银行')
        
        # 全角数字应该失败
        with pytest.raises(ValidationError):
            validate_stock_code('０００００１')


if __name__ == '__main__':
    pytest.main([__file__])