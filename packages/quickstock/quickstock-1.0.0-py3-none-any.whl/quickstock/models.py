"""
数据模型定义

定义SDK中使用的各种数据模型和请求对象
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any


@dataclass
class DataRequest:
    """数据请求模型"""
    data_type: str  # stock_basic, stock_daily, index_basic等
    ts_code: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    freq: Optional[str] = None  # 1min, 5min, 1d, 1w, 1m
    fields: Optional[List[str]] = None
    extra_params: Dict[str, Any] = field(default_factory=dict)
    
    def to_cache_key(self) -> str:
        """
        转换为缓存键
        
        Returns:
            缓存键字符串
        """
        import hashlib
        
        # 构建缓存键的组成部分
        key_parts = [
            self.data_type,
            self.ts_code or '',
            self.start_date or '',
            self.end_date or '',
            self.freq or '',
            ','.join(self.fields or []),
            str(sorted(self.extra_params.items()))
        ]
        
        # 生成缓存键
        key_string = '|'.join(key_parts)
        
        # 使用MD5哈希生成固定长度的键
        return hashlib.md5(key_string.encode('utf-8')).hexdigest()
    
    def validate(self) -> bool:
        """
        验证请求参数
        
        Returns:
            验证是否通过
            
        Raises:
            ValidationError: 参数验证失败
        """
        from .core.errors import ValidationError
        
        # 验证数据类型
        if not self.data_type:
            raise ValidationError("data_type不能为空")
        
        # 验证日期格式
        if self.start_date and not self._is_valid_date(self.start_date):
            raise ValidationError(f"start_date格式无效: {self.start_date}")
        
        if self.end_date and not self._is_valid_date(self.end_date):
            raise ValidationError(f"end_date格式无效: {self.end_date}")
        
        # 验证日期范围
        if (self.start_date and self.end_date and 
            self.start_date > self.end_date):
            raise ValidationError("start_date不能大于end_date")
        
        # 验证频率
        if self.freq and self.freq not in ['1min', '5min', '15min', '30min', 
                                          '60min', '1d', '1w', '1m']:
            raise ValidationError(f"不支持的频率: {self.freq}")
        
        return True
    
    def _is_valid_date(self, date_str: str) -> bool:
        """
        验证日期格式
        
        Args:
            date_str: 日期字符串
            
        Returns:
            是否为有效日期格式
        """
        import re
        from datetime import datetime
        
        # 支持的日期格式: YYYYMMDD, YYYY-MM-DD
        patterns = [
            r'^\d{8}$',  # YYYYMMDD
            r'^\d{4}-\d{2}-\d{2}$'  # YYYY-MM-DD
        ]
        
        for pattern in patterns:
            if re.match(pattern, date_str):
                try:
                    if len(date_str) == 8:
                        datetime.strptime(date_str, '%Y%m%d')
                    else:
                        datetime.strptime(date_str, '%Y-%m-%d')
                    return True
                except ValueError:
                    continue
        
        return False


# 标准化数据模型定义

# 股票基础信息标准格式
STOCK_BASIC_COLUMNS = {
    'ts_code': str,      # 股票代码
    'symbol': str,       # 股票代码（不含后缀）
    'name': str,         # 股票名称
    'area': str,         # 所属地域
    'industry': str,     # 所属行业
    'market': str,       # 市场类型
    'list_date': str,    # 上市日期
    'is_hs': str        # 是否沪深港通标的
}

# OHLCV数据标准格式
OHLCV_COLUMNS = {
    'ts_code': str,      # 股票代码
    'trade_date': str,   # 交易日期
    'open': float,       # 开盘价
    'high': float,       # 最高价
    'low': float,        # 最低价
    'close': float,      # 收盘价
    'volume': int,       # 成交量
    'amount': float      # 成交额
}

# 指数基础信息标准格式
INDEX_BASIC_COLUMNS = {
    'ts_code': str,      # 指数代码
    'name': str,         # 指数名称
    'market': str,       # 市场
    'publisher': str,    # 发布方
    'category': str,     # 指数类别
    'base_date': str,    # 基期
    'base_point': float, # 基点
    'list_date': str     # 发布日期
}

# 基金基础信息标准格式
FUND_BASIC_COLUMNS = {
    'ts_code': str,      # 基金代码
    'name': str,         # 基金名称
    'management': str,   # 管理人
    'custodian': str,    # 托管人
    'fund_type': str,    # 基金类型
    'found_date': str,   # 成立日期
    'due_date': str,     # 到期日期
    'list_date': str,    # 上市日期
    'issue_date': str,   # 发行日期
    'delist_date': str,  # 退市日期
    'issue_amount': float, # 发行份额
    'market': str        # 市场类型
}

# 交易日历标准格式
TRADE_CAL_COLUMNS = {
    'exchange': str,     # 交易所
    'cal_date': str,     # 日历日期
    'is_open': int,      # 是否交易
    'pretrade_date': str # 上一交易日
}