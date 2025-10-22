"""
数据格式化器测试
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime
from unittest.mock import Mock

from quickstock.core.formatter import DataFormatter
from quickstock.config import Config


class TestDataFormatter:
    """数据格式化器测试类"""
    
    @pytest.fixture
    def config(self):
        """创建测试配置"""
        config = Mock(spec=Config)
        config.date_format = '%Y%m%d'
        config.float_precision = 4
        return config
    
    @pytest.fixture
    def formatter(self, config):
        """创建数据格式化器实例"""
        return DataFormatter(config)
    
    def test_init(self, config):
        """测试初始化"""
        formatter = DataFormatter(config)
        assert formatter.config == config
        assert formatter.date_format == '%Y%m%d'
        assert formatter.float_precision == 4
        assert isinstance(formatter._column_mappings, dict)
    
    def test_basic_format_empty_data(self, formatter):
        """测试空数据的基本格式化"""
        empty_df = pd.DataFrame()
        result = formatter._basic_format(empty_df)
        assert result.empty
    
    def test_basic_format_normal_data(self, formatter):
        """测试正常数据的基本格式化"""
        # 创建测试数据
        data = pd.DataFrame({
            'Code': ['000001', '000002', '000001'],  # 包含重复行
            'Name': ['平安银行', '万科A', '平安银行'],
            'Price': [10.5, 20.3, 10.5],
            'Volume': [1000, 2000, 1000]
        })
        
        result = formatter._basic_format(data)
        
        # 验证去重
        assert len(result) == 2
        
        # 验证列名转换为小写
        expected_columns = ['code', 'name', 'price', 'volume']
        assert list(result.columns) == expected_columns
        
        # 验证索引重置
        assert list(result.index) == [0, 1]
    
    def test_basic_format_with_nulls(self, formatter):
        """测试包含空值的数据格式化"""
        data = pd.DataFrame({
            'Code': ['000001', None, ''],
            'Name': ['平安银行', np.nan, '万科A'],
            'Price': [10.5, np.inf, -np.inf]
        })
        
        result = formatter._basic_format(data)
        
        # 验证字符串空值处理
        assert result.loc[1, 'code'] == ''
        assert result.loc[2, 'code'] == ''
        assert result.loc[1, 'name'] == ''
        
        # 验证无穷大值处理
        assert pd.isna(result.loc[1, 'price'])
        assert pd.isna(result.loc[2, 'price'])
    
    def test_apply_column_mapping_baostock(self, formatter):
        """测试baostock数据源的列名映射"""
        data = pd.DataFrame({
            'code': ['000001'],
            'date': ['20231201'],
            'preclose': [10.0],
            'pctChg': [0.05]
        })
        
        result = formatter._apply_column_mapping(data, 'baostock')
        
        # 验证列名映射
        assert 'ts_code' in result.columns
        assert 'trade_date' in result.columns
        assert 'pre_close' in result.columns
        assert 'pct_chg' in result.columns
    
    def test_apply_column_mapping_unknown_source(self, formatter):
        """测试未知数据源的列名映射"""
        data = pd.DataFrame({
            'code': ['000001'],
            'price': [10.0]
        })
        
        result = formatter._apply_column_mapping(data, 'unknown_source')
        
        # 验证列名不变
        assert list(result.columns) == ['code', 'price']
    
    def test_convert_date_format(self, formatter):
        """测试日期格式转换"""
        # 测试不同格式的日期
        date_series = pd.Series([
            '20231201',      # YYYYMMDD
            '2023-12-01',    # YYYY-MM-DD
            '2023/12/01',    # YYYY/MM/DD
            '2023.12.01',    # YYYY.MM.DD
            '',              # 空值
            None,            # None值
            'invalid_date'   # 无效日期
        ])
        
        result = formatter._convert_date_format(date_series)
        
        # 验证转换结果
        assert result.iloc[0] == '20231201'
        assert result.iloc[1] == '20231201'
        assert result.iloc[2] == '20231201'
        assert result.iloc[3] == '20231201'
        assert result.iloc[4] == ''
        assert result.iloc[5] == ''
        assert result.iloc[6] == 'invalid_date'  # 无效日期保持原值
    
    def test_standardize_dates(self, formatter):
        """测试日期标准化"""
        data = pd.DataFrame({
            'trade_date': ['2023-12-01', '20231202'],
            'list_date': ['2023/01/01', '2023.01.02'],
            'other_col': ['not_date', 'also_not_date']
        })
        
        result = formatter._standardize_dates(data, ['trade_date', 'list_date'])
        
        # 验证日期列被标准化
        assert result.loc[0, 'trade_date'] == '20231201'
        assert result.loc[1, 'trade_date'] == '20231202'
        assert result.loc[0, 'list_date'] == '20230101'
        assert result.loc[1, 'list_date'] == '20230102'
        
        # 验证非日期列不变
        assert result.loc[0, 'other_col'] == 'not_date'
    
    def test_standardize_numeric_columns(self, formatter):
        """测试数值列标准化"""
        data = pd.DataFrame({
            'price': ['10.123456', '20.987654'],
            'volume': ['1000', '2000'],
            'invalid': ['abc', 'def']
        })
        
        result = formatter._standardize_numeric_columns(data, ['price', 'volume', 'invalid'])
        
        # 验证数值转换和精度
        assert result.loc[0, 'price'] == 10.1235
        assert result.loc[1, 'price'] == 20.9877
        assert result.loc[0, 'volume'] == 1000.0
        assert result.loc[1, 'volume'] == 2000.0
        
        # 验证无效数值转换为NaN
        assert pd.isna(result.loc[0, 'invalid'])
        assert pd.isna(result.loc[1, 'invalid'])
    
    def test_ensure_columns(self, formatter):
        """测试列确保和类型设置"""
        data = pd.DataFrame({
            'ts_code': ['000001', '000002'],
            'name': ['平安银行', '万科A'],
            'price': [10.5, 20.3],
            'volume': [1000, 2000],
            'extra_col': ['extra1', 'extra2']
        })
        
        column_spec = {
            'ts_code': str,
            'name': str,
            'price': float,
            'volume': int,
            'missing_col': str
        }
        
        result = formatter._ensure_columns(data, column_spec)
        
        # 验证只保留存在的列
        expected_columns = ['ts_code', 'name', 'price', 'volume']
        assert list(result.columns) == expected_columns
        
        # 验证数据类型
        assert result['ts_code'].dtype == 'object'  # str在pandas中是object
        assert result['name'].dtype == 'object'
        assert result['price'].dtype == 'float64'
        assert result['volume'].dtype == 'Int64'  # 可空整数类型
    
    @pytest.mark.asyncio
    async def test_format_stock_basic(self, formatter):
        """测试股票基础信息格式化"""
        data = pd.DataFrame({
            'code': ['000001', '000002'],
            'name': ['平安银行', '万科A'],
            'industry': ['银行', '房地产'],
            'list_date': ['2023-01-01', '2023-01-02']
        })
        
        result = formatter.format_stock_basic(data, 'baostock')
        
        # 验证基本格式化
        assert len(result) == 2
        assert not result.empty
        
        # 验证列名映射（baostock: code -> ts_code）
        if 'ts_code' in result.columns:
            assert result.loc[0, 'ts_code'] == '000001'
    
    @pytest.mark.asyncio
    async def test_format_stock_ohlcv(self, formatter):
        """测试股票OHLCV数据格式化"""
        data = pd.DataFrame({
            'code': ['000001', '000001'],
            'date': ['2023-12-01', '2023-12-02'],
            'open': [10.0, 10.5],
            'high': [10.5, 11.0],
            'low': [9.8, 10.2],
            'close': [10.2, 10.8],
            'volume': [1000000, 1200000],
            'amount': [10200000.0, 12960000.0]
        })
        
        result = formatter.format_stock_ohlcv(data, 'baostock')
        
        # 验证基本格式化
        assert len(result) == 2
        assert not result.empty
        
        # 验证数值精度
        numeric_columns = ['open', 'high', 'low', 'close', 'amount']
        for col in numeric_columns:
            if col in result.columns:
                assert all(result[col].apply(lambda x: len(str(x).split('.')[-1]) <= 4 if '.' in str(x) else True))
    
    @pytest.mark.asyncio
    async def test_format_data_dispatch(self, formatter):
        """测试format_data方法的分发逻辑"""
        data = pd.DataFrame({
            'code': ['000001'],
            'name': ['测试股票']
        })
        
        # 测试股票基础信息
        result = await formatter.format_data(data, 'stock_basic', 'test')
        assert not result.empty
        
        # 测试股票日线数据
        result = await formatter.format_data(data, 'stock_daily', 'test')
        assert not result.empty
        
        # 测试未知数据类型
        result = await formatter.format_data(data, 'unknown_type', 'test')
        assert not result.empty  # 应该返回基本格式化的数据
    
    @pytest.mark.asyncio
    async def test_format_data_empty_input(self, formatter):
        """测试空数据输入"""
        empty_df = pd.DataFrame()
        
        result = await formatter.format_data(empty_df, 'stock_basic', 'test')
        assert result.empty
    
    @pytest.mark.asyncio
    async def test_format_data_error_handling(self, formatter):
        """测试格式化错误处理"""
        # 创建可能导致错误的数据
        problematic_data = pd.DataFrame({
            'col1': [1, 2, 3],
            'col2': ['a', 'b', 'c']
        })
        
        # 即使出现错误，也应该返回基本格式化的数据
        result = await formatter.format_data(problematic_data, 'stock_basic', 'test')
        assert not result.empty
    
    def test_standardize_data_types_optimization(self, formatter):
        """测试数据类型优化"""
        data = pd.DataFrame({
            'category_col': ['A', 'B', 'A', 'B', 'A'],      # 重复值多，适合分类类型
            'unique_col': ['X', 'Y', 'Z', 'W', 'V'],        # 唯一值多，不适合分类类型
            'small_int': [1, 2, 3, 4, 5],                   # 小整数
            'large_int': [1000000, 2000000, 3000000, 4000000, 5000000],  # 大整数
            'negative_int': [-100, -200, -50, -75, -125]    # 负整数
        })
        
        result = formatter._standardize_data_types(data)
        
        # 验证分类类型优化
        assert result['category_col'].dtype.name == 'category'
        assert result['unique_col'].dtype == 'object'  # 不应该转换为分类类型
        
        # 验证整数类型优化
        assert result['small_int'].dtype in ['uint8', 'int8']
        assert result['negative_int'].dtype in ['int8', 'int16', 'int32']


if __name__ == '__main__':
    pytest.main([__file__])