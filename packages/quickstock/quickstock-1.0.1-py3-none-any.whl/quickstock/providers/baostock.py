"""
Baostock数据提供者

提供基于baostock的股票、指数、基金数据获取功能
"""

import asyncio
import logging
import re
from typing import Optional, Dict, Any, List
import pandas as pd

try:
    import baostock as bs
    BAOSTOCK_AVAILABLE = True
except ImportError:
    BAOSTOCK_AVAILABLE = False
    bs = None

from .base import DataProvider, RateLimit
from ..core.errors import DataSourceError, ValidationError, NetworkError
from ..utils.code_converter import StockCodeConverter
from ..utils.validators import validate_stock_code, validate_date_format


class BaostockProvider(DataProvider):
    """Baostock数据提供者"""
    
    def __init__(self, config):
        """
        初始化Baostock提供者
        
        Args:
            config: 配置对象
        """
        super().__init__(config)
        self.logger = logging.getLogger(__name__)
        self._session_active = False
        self._login_lock = asyncio.Lock()
        
        # 检查baostock是否可用
        if not BAOSTOCK_AVAILABLE:
            raise DataSourceError(
                "baostock库未安装，请运行: pip install baostock",
                error_code="BAOSTOCK_NOT_INSTALLED"
            )
    
    async def _ensure_login(self):
        """确保baostock会话已登录"""
        async with self._login_lock:
            if not self._session_active:
                try:
                    # baostock登录
                    lg = bs.login()
                    if lg.error_code != '0':
                        raise DataSourceError(
                            f"Baostock登录失败: {lg.error_msg}",
                            error_code="BAOSTOCK_LOGIN_FAILED",
                            details={'error_code': lg.error_code, 'error_msg': lg.error_msg}
                        )
                    
                    self._session_active = True
                    self.logger.info("Baostock登录成功")
                    
                except Exception as e:
                    if isinstance(e, DataSourceError):
                        raise
                    raise NetworkError(
                        f"Baostock连接失败: {str(e)}",
                        error_code="BAOSTOCK_CONNECTION_ERROR"
                    )
    
    async def _logout(self):
        """登出baostock会话"""
        if self._session_active:
            try:
                bs.logout()
                self._session_active = False
                self.logger.info("Baostock登出成功")
            except Exception as e:
                self.logger.warning(f"Baostock登出时出现警告: {e}")
    
    def __del__(self):
        """析构函数，确保登出"""
        if hasattr(self, '_session_active') and self._session_active:
            try:
                bs.logout()
            except:
                pass
    
    async def get_stock_basic(self, **kwargs) -> pd.DataFrame:
        """
        获取股票基础信息
        
        Args:
            **kwargs: 查询参数
                - date: 查询日期，格式YYYY-MM-DD，默认为最新
                - market: 市场类型，可选值：'all', 'sh', 'sz'，默认为'all'
                
        Returns:
            股票基础信息DataFrame
        """
        await self._ensure_login()
        
        try:
            # 解析参数
            date = kwargs.get('date')
            market = kwargs.get('market', 'all')
            
            # 参数验证
            if date:
                validate_date_format(date)
            
            # 获取股票基础信息
            if date:
                # 获取指定日期的股票信息
                rs = bs.query_all_stock(day=date)
            else:
                # 获取最新的股票信息
                rs = bs.query_all_stock()
            
            if rs.error_code != '0':
                raise DataSourceError(
                    f"获取股票基础信息失败: {rs.error_msg}",
                    error_code="BAOSTOCK_QUERY_ERROR",
                    details={
                        'error_code': rs.error_code, 
                        'error_msg': rs.error_msg,
                        'date': date,
                        'market': market
                    }
                )
            
            # 转换为DataFrame
            data_list = []
            while (rs.error_code == '0') & rs.next():
                data_list.append(rs.get_row_data())
            
            if not data_list:
                self.logger.warning(f"未获取到股票基础信息数据，日期: {date}, 市场: {market}")
                return pd.DataFrame()
            
            df = pd.DataFrame(data_list, columns=rs.fields)
            
            # 根据市场类型过滤
            if market != 'all':
                df = self._filter_by_market(df, market)
            
            # 标准化列名
            df = self._standardize_stock_basic_columns(df)
            
            # 验证数据格式
            df = self.validate_data_format(df)
            
            self.logger.info(f"成功获取{len(df)}条股票基础信息")
            return df
            
        except Exception as e:
            if isinstance(e, (DataSourceError, ValidationError)):
                raise
            raise DataSourceError(
                f"获取股票基础信息时发生错误: {str(e)}",
                error_code="BAOSTOCK_UNEXPECTED_ERROR",
                details={'date': kwargs.get('date'), 'market': kwargs.get('market')}
            )
    
    async def get_stock_daily(self, ts_code: str, start_date: str, end_date: str, **kwargs) -> pd.DataFrame:
        """
        获取股票日线数据
        
        Args:
            ts_code: 股票代码
            start_date: 开始日期，格式YYYY-MM-DD
            end_date: 结束日期，格式YYYY-MM-DD
            **kwargs: 其他参数
                - adjustflag: 复权类型，'1'前复权，'2'后复权，'3'不复权，默认'3'
                - frequency: 数据频率，'d'日线，'w'周线，'m'月线，默认'd'
                - fields: 返回字段列表，默认返回所有字段
            
        Returns:
            股票日线数据DataFrame
        """
        # 参数验证
        validate_stock_code(ts_code)
        validate_date_format(start_date)
        validate_date_format(end_date)
        
        # 解析可选参数
        adjustflag = kwargs.get('adjustflag', '3')  # 默认不复权
        frequency = kwargs.get('frequency', 'd')    # 默认日线
        fields = kwargs.get('fields')
        
        # 验证参数值
        if adjustflag not in ['1', '2', '3']:
            raise ValidationError(f"无效的复权类型: {adjustflag}，必须是'1'、'2'或'3'")
        
        if frequency not in ['d', 'w', 'm']:
            raise ValidationError(f"无效的数据频率: {frequency}，必须是'd'、'w'或'm'")
        
        await self._ensure_login()
        
        try:
            # 转换股票代码格式
            baostock_code = self._convert_stock_code(ts_code)
            
            # 构建查询字段
            if fields:
                query_fields = ','.join(fields)
            else:
                query_fields = "date,code,open,high,low,close,preclose,volume,amount,adjustflag,turn,tradestatus,pctChg,isST"
            
            # 查询历史数据
            rs = bs.query_history_k_data_plus(
                baostock_code,
                query_fields,
                start_date=start_date,
                end_date=end_date,
                frequency=frequency,
                adjustflag=adjustflag
            )
            
            if rs.error_code != '0':
                raise DataSourceError(
                    f"获取股票{frequency}线数据失败: {rs.error_msg}",
                    error_code="BAOSTOCK_QUERY_ERROR",
                    details={
                        'error_code': rs.error_code, 
                        'error_msg': rs.error_msg,
                        'ts_code': ts_code,
                        'baostock_code': baostock_code,
                        'start_date': start_date,
                        'end_date': end_date,
                        'frequency': frequency,
                        'adjustflag': adjustflag
                    }
                )
            
            # 转换为DataFrame
            data_list = []
            while (rs.error_code == '0') & rs.next():
                data_list.append(rs.get_row_data())
            
            if not data_list:
                self.logger.warning(f"未获取到股票数据: {ts_code}, {start_date} - {end_date}")
                return pd.DataFrame()
            
            df = pd.DataFrame(data_list, columns=rs.fields)
            
            # 过滤掉停牌或无效数据
            df = self._filter_invalid_data(df)
            
            # 标准化列名和数据类型
            df = self._standardize_ohlcv_columns(df)
            
            # 验证数据格式和一致性
            df = self.validate_data_format(df)
            if not self.check_data_consistency(df, ts_code):
                self.logger.warning(f"数据一致性检查失败: {ts_code}")
            
            self.logger.info(f"成功获取股票{frequency}线数据: {ts_code}, {len(df)}条记录")
            return df
            
        except Exception as e:
            if isinstance(e, (DataSourceError, ValidationError)):
                raise
            raise DataSourceError(
                f"获取股票{frequency}线数据时发生错误: {str(e)}",
                error_code="BAOSTOCK_UNEXPECTED_ERROR",
                details={
                    'ts_code': ts_code, 
                    'start_date': start_date, 
                    'end_date': end_date,
                    'frequency': frequency,
                    'adjustflag': adjustflag
                }
            )
    
    async def get_trade_cal(self, start_date: str, end_date: str) -> pd.DataFrame:
        """
        获取交易日历
        
        Args:
            start_date: 开始日期，格式YYYY-MM-DD
            end_date: 结束日期，格式YYYY-MM-DD
            
        Returns:
            交易日历DataFrame
        """
        # 参数验证
        validate_date_format(start_date)
        validate_date_format(end_date)
        
        await self._ensure_login()
        
        try:
            # 查询交易日历
            rs = bs.query_trade_dates(start_date=start_date, end_date=end_date)
            
            if rs.error_code != '0':
                raise DataSourceError(
                    f"获取交易日历失败: {rs.error_msg}",
                    error_code="BAOSTOCK_QUERY_ERROR",
                    details={
                        'error_code': rs.error_code,
                        'error_msg': rs.error_msg,
                        'start_date': start_date,
                        'end_date': end_date
                    }
                )
            
            # 转换为DataFrame
            data_list = []
            while (rs.error_code == '0') & rs.next():
                data_list.append(rs.get_row_data())
            
            if not data_list:
                return pd.DataFrame()
            
            df = pd.DataFrame(data_list, columns=rs.fields)
            
            # 标准化列名
            df = self._standardize_trade_cal_columns(df)
            
            return df
            
        except Exception as e:
            if isinstance(e, (DataSourceError, ValidationError)):
                raise
            raise DataSourceError(
                f"获取交易日历时发生错误: {str(e)}",
                error_code="BAOSTOCK_UNEXPECTED_ERROR",
                details={'start_date': start_date, 'end_date': end_date}
            )
    
    def _convert_stock_code(self, ts_code: str) -> str:
        """
        转换股票代码格式为baostock格式
        
        Args:
            ts_code: 任意格式的股票代码
            
        Returns:
            baostock格式的股票代码（如sz.000001）
        """
        try:
            # 检查是否已经是baostock格式
            if re.match(r'^(sh|sz)\.([0-9]{6})$', ts_code.lower()):
                return ts_code.lower()
            
            # 使用统一的代码转换器
            return StockCodeConverter.to_baostock_format(ts_code)
        except Exception as e:
            self.logger.error(f"股票代码转换失败: {ts_code} -> baostock格式, 错误: {e}")
            # 记录转换错误到日志
            self.logger.debug(f"转换失败详情 - 输入代码: {ts_code}, 目标格式: baostock, 异常类型: {type(e).__name__}")
            raise ValidationError(f"无法将股票代码 {ts_code} 转换为baostock格式: {str(e)}")
    
    def _standardize_stock_basic_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        标准化股票基础信息列名
        
        Args:
            df: 原始DataFrame
            
        Returns:
            标准化后的DataFrame
        """
        if df.empty:
            return df
        
        # baostock股票基础信息列名映射
        column_mapping = {
            'code': 'ts_code',
            'code_name': 'name',
            'ipoDate': 'list_date',
            'outDate': 'delist_date',
            'type': 'market',
            'status': 'list_status'
        }
        
        # 重命名列
        df = df.rename(columns=column_mapping)
        
        # 转换股票代码格式（从baostock格式转为标准格式）
        if 'ts_code' in df.columns:
            try:
                df['ts_code'] = df['ts_code'].apply(self._convert_to_standard_code)
                self.logger.debug(f"成功转换{len(df)}条股票基础信息的代码格式")
            except Exception as e:
                self.logger.error(f"批量转换股票基础信息代码格式失败: {e}")
                # 尝试逐行转换，跳过失败的行
                valid_rows = []
                for idx, row in df.iterrows():
                    try:
                        row['ts_code'] = self._convert_to_standard_code(row['ts_code'])
                        valid_rows.append(row)
                    except Exception as row_error:
                        self.logger.warning(f"跳过无效代码行: {row['ts_code']}, 错误: {row_error}")
                        continue
                df = pd.DataFrame(valid_rows) if valid_rows else pd.DataFrame()
        
        # 确保必要的列存在
        required_columns = ['ts_code', 'name']
        for col in required_columns:
            if col not in df.columns:
                df[col] = None
        
        return df
    
    def _standardize_ohlcv_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        标准化OHLCV数据列名和数据类型
        
        Args:
            df: 原始DataFrame
            
        Returns:
            标准化后的DataFrame
        """
        if df.empty:
            return df
        
        # baostock OHLCV列名映射
        column_mapping = {
            'date': 'trade_date',
            'code': 'ts_code',
            'preclose': 'pre_close',
            'pctChg': 'pct_chg'
        }
        
        # 重命名列
        df = df.rename(columns=column_mapping)
        
        # 转换股票代码格式
        if 'ts_code' in df.columns:
            try:
                df['ts_code'] = df['ts_code'].apply(self._convert_to_standard_code)
                self.logger.debug(f"成功转换{len(df)}条OHLCV数据的代码格式")
            except Exception as e:
                self.logger.error(f"批量转换OHLCV数据代码格式失败: {e}")
                # 尝试逐行转换，跳过失败的行
                valid_rows = []
                for idx, row in df.iterrows():
                    try:
                        row['ts_code'] = self._convert_to_standard_code(row['ts_code'])
                        valid_rows.append(row)
                    except Exception as row_error:
                        self.logger.warning(f"跳过无效代码行: {row['ts_code']}, 错误: {row_error}")
                        continue
                df = pd.DataFrame(valid_rows) if valid_rows else pd.DataFrame()
        
        # 转换数据类型
        numeric_columns = ['open', 'high', 'low', 'close', 'pre_close', 'volume', 'amount', 'pct_chg']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # 转换日期格式
        if 'trade_date' in df.columns:
            df['trade_date'] = pd.to_datetime(df['trade_date']).dt.strftime('%Y%m%d')
        
        return df
    
    def _standardize_trade_cal_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        标准化交易日历列名
        
        Args:
            df: 原始DataFrame
            
        Returns:
            标准化后的DataFrame
        """
        if df.empty:
            return df
        
        # baostock交易日历列名映射
        column_mapping = {
            'calendar_date': 'cal_date',
            'is_trading_day': 'is_open'
        }
        
        # 重命名列
        df = df.rename(columns=column_mapping)
        
        # 转换数据类型
        if 'is_open' in df.columns:
            df['is_open'] = df['is_open'].astype(int)
        
        # 转换日期格式
        if 'cal_date' in df.columns:
            df['cal_date'] = pd.to_datetime(df['cal_date']).dt.strftime('%Y%m%d')
        
        return df
    
    def _convert_to_standard_code(self, baostock_code: str) -> str:
        """
        将baostock格式的代码转换为标准格式
        
        Args:
            baostock_code: baostock格式代码（如sz.000001）
            
        Returns:
            标准格式代码（如000001.SZ）
        """
        try:
            # 使用统一的代码转换器
            return StockCodeConverter.from_baostock_format(baostock_code)
        except Exception as e:
            self.logger.error(f"股票代码转换失败: {baostock_code} -> 标准格式, 错误: {e}")
            # 记录转换错误到日志
            self.logger.debug(f"转换失败详情 - 输入代码: {baostock_code}, 目标格式: standard, 异常类型: {type(e).__name__}")
            raise ValidationError(f"无法将baostock代码 {baostock_code} 转换为标准格式: {str(e)}")
    
    def _convert_index_code(self, ts_code: str) -> str:
        """
        转换指数代码格式为baostock格式
        
        Args:
            ts_code: 标准指数代码（如000001.SH）
            
        Returns:
            baostock格式的指数代码（如sh.000001）
        """
        # 指数代码转换逻辑与股票代码类似
        return self._convert_stock_code(ts_code)
    
    def _standardize_index_basic_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        标准化指数基础信息列名
        
        Args:
            df: 原始DataFrame
            
        Returns:
            标准化后的DataFrame
        """
        if df.empty:
            return df
        
        # baostock指数基础信息列名映射（使用行业分类数据作为替代）
        column_mapping = {
            'code': 'ts_code',
            'code_name': 'name',
            'industry': 'category',
            'industryClassification': 'classification'
        }
        
        # 重命名列
        df = df.rename(columns=column_mapping)
        
        # 转换代码格式
        if 'ts_code' in df.columns:
            try:
                df['ts_code'] = df['ts_code'].apply(self._convert_to_standard_code)
                self.logger.debug(f"成功转换{len(df)}条指数基础信息的代码格式")
            except Exception as e:
                self.logger.error(f"批量转换指数基础信息代码格式失败: {e}")
                # 尝试逐行转换，跳过失败的行
                valid_rows = []
                for idx, row in df.iterrows():
                    try:
                        row['ts_code'] = self._convert_to_standard_code(row['ts_code'])
                        valid_rows.append(row)
                    except Exception as row_error:
                        self.logger.warning(f"跳过无效代码行: {row['ts_code']}, 错误: {row_error}")
                        continue
                df = pd.DataFrame(valid_rows) if valid_rows else pd.DataFrame()
        
        # 确保必要的列存在
        required_columns = ['ts_code', 'name']
        for col in required_columns:
            if col not in df.columns:
                df[col] = None
        
        return df
    
    def _standardize_index_ohlcv_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        标准化指数OHLCV数据列名和数据类型
        
        Args:
            df: 原始DataFrame
            
        Returns:
            标准化后的DataFrame
        """
        if df.empty:
            return df
        
        # 指数OHLCV列名映射
        column_mapping = {
            'date': 'trade_date',
            'code': 'ts_code',
            'pctChg': 'pct_chg'
        }
        
        # 重命名列
        df = df.rename(columns=column_mapping)
        
        # 转换代码格式
        if 'ts_code' in df.columns:
            try:
                df['ts_code'] = df['ts_code'].apply(self._convert_to_standard_code)
                self.logger.debug(f"成功转换{len(df)}条指数OHLCV数据的代码格式")
            except Exception as e:
                self.logger.error(f"批量转换指数OHLCV数据代码格式失败: {e}")
                # 尝试逐行转换，跳过失败的行
                valid_rows = []
                for idx, row in df.iterrows():
                    try:
                        row['ts_code'] = self._convert_to_standard_code(row['ts_code'])
                        valid_rows.append(row)
                    except Exception as row_error:
                        self.logger.warning(f"跳过无效代码行: {row['ts_code']}, 错误: {row_error}")
                        continue
                df = pd.DataFrame(valid_rows) if valid_rows else pd.DataFrame()
        
        # 转换数据类型
        numeric_columns = ['open', 'high', 'low', 'close', 'volume', 'amount', 'pct_chg']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # 转换日期格式
        if 'trade_date' in df.columns:
            df['trade_date'] = pd.to_datetime(df['trade_date']).dt.strftime('%Y%m%d')
        
        return df
    
    def get_rate_limit(self) -> RateLimit:
        """
        获取速率限制信息
        
        Returns:
            速率限制对象
        """
        # baostock相对宽松的速率限制
        return RateLimit(
            requests_per_second=2.0,
            requests_per_minute=100,
            requests_per_hour=3000
        )
    
    def is_available(self) -> bool:
        """
        检查数据源是否可用
        
        Returns:
            是否可用
        """
        return BAOSTOCK_AVAILABLE and self.config.enable_baostock
    
    def _filter_by_market(self, df: pd.DataFrame, market: str) -> pd.DataFrame:
        """
        根据市场类型过滤股票数据
        
        Args:
            df: 股票数据DataFrame
            market: 市场类型 ('sh', 'sz')
            
        Returns:
            过滤后的DataFrame
        """
        if df.empty or 'code' not in df.columns:
            return df
        
        if market.lower() == 'sh':
            return df[df['code'].str.startswith('sh.')]
        elif market.lower() == 'sz':
            return df[df['code'].str.startswith('sz.')]
        else:
            return df
    
    def _filter_invalid_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        过滤无效的股票数据
        
        Args:
            df: 原始数据DataFrame
            
        Returns:
            过滤后的DataFrame
        """
        if df.empty:
            return df
        
        # 创建副本避免修改原数据
        filtered_df = df.copy()
        
        # 过滤掉停牌数据（tradestatus != '1'）
        if 'tradestatus' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['tradestatus'] == '1'].copy()
        
        # 过滤掉价格为空或0的数据
        price_columns = ['open', 'high', 'low', 'close']
        for col in price_columns:
            if col in filtered_df.columns:
                # 转换为数值类型并过滤
                numeric_values = pd.to_numeric(filtered_df[col], errors='coerce')
                valid_mask = (numeric_values > 0) & (~numeric_values.isna())
                filtered_df = filtered_df[valid_mask].copy()
        
        return filtered_df
    
    async def get_stock_minute(self, ts_code: str, freq: str = '1min',
                              start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """
        获取股票分钟数据（baostock不支持分钟数据）
        
        Args:
            ts_code: 股票代码
            freq: 频率 (1min, 5min, 15min, 30min, 60min)
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            股票分钟数据DataFrame
        """
        raise NotImplementedError("Baostock不支持分钟级数据获取，请使用其他数据源")
    
    async def get_index_basic(self, **kwargs) -> pd.DataFrame:
        """
        获取指数基础信息
        
        Args:
            **kwargs: 查询参数
                - date: 查询日期，格式YYYY-MM-DD，默认为最新
                
        Returns:
            指数基础信息DataFrame
        """
        await self._ensure_login()
        
        try:
            # 解析参数
            date = kwargs.get('date')
            
            # 参数验证
            if date:
                validate_date_format(date)
            
            # 获取指数基础信息
            if date:
                rs = bs.query_stock_industry(date=date)
            else:
                # baostock没有直接的指数基础信息接口，使用行业分类作为替代
                rs = bs.query_stock_industry()
            
            if rs.error_code != '0':
                raise DataSourceError(
                    f"获取指数基础信息失败: {rs.error_msg}",
                    error_code="BAOSTOCK_QUERY_ERROR",
                    details={
                        'error_code': rs.error_code,
                        'error_msg': rs.error_msg,
                        'date': date
                    }
                )
            
            # 转换为DataFrame
            data_list = []
            while (rs.error_code == '0') & rs.next():
                data_list.append(rs.get_row_data())
            
            if not data_list:
                self.logger.warning(f"未获取到指数基础信息数据，日期: {date}")
                return pd.DataFrame()
            
            df = pd.DataFrame(data_list, columns=rs.fields)
            
            # 标准化列名
            df = self._standardize_index_basic_columns(df)
            
            self.logger.info(f"成功获取{len(df)}条指数基础信息")
            return df
            
        except Exception as e:
            if isinstance(e, (DataSourceError, ValidationError)):
                raise
            raise DataSourceError(
                f"获取指数基础信息时发生错误: {str(e)}",
                error_code="BAOSTOCK_UNEXPECTED_ERROR",
                details={'date': kwargs.get('date')}
            )
    
    async def get_index_daily(self, ts_code: str, start_date: str, end_date: str, **kwargs) -> pd.DataFrame:
        """
        获取指数日线数据
        
        Args:
            ts_code: 指数代码
            start_date: 开始日期，格式YYYY-MM-DD
            end_date: 结束日期，格式YYYY-MM-DD
            **kwargs: 其他参数
                - frequency: 数据频率，'d'日线，'w'周线，'m'月线，默认'd'
                - fields: 返回字段列表，默认返回所有字段
            
        Returns:
            指数日线数据DataFrame
        """
        # 参数验证
        validate_stock_code(ts_code)  # 指数代码格式与股票代码类似
        validate_date_format(start_date)
        validate_date_format(end_date)
        
        # 解析可选参数
        frequency = kwargs.get('frequency', 'd')
        fields = kwargs.get('fields')
        
        # 验证参数值
        if frequency not in ['d', 'w', 'm']:
            raise ValidationError(f"无效的数据频率: {frequency}，必须是'd'、'w'或'm'")
        
        await self._ensure_login()
        
        try:
            # 转换指数代码格式
            baostock_code = self._convert_index_code(ts_code)
            
            # 构建查询字段
            if fields:
                query_fields = ','.join(fields)
            else:
                query_fields = "date,code,open,high,low,close,volume,amount,turn,pctChg"
            
            # 查询指数历史数据
            rs = bs.query_history_k_data_plus(
                baostock_code,
                query_fields,
                start_date=start_date,
                end_date=end_date,
                frequency=frequency,
                adjustflag="3"  # 指数不需要复权
            )
            
            if rs.error_code != '0':
                raise DataSourceError(
                    f"获取指数{frequency}线数据失败: {rs.error_msg}",
                    error_code="BAOSTOCK_QUERY_ERROR",
                    details={
                        'error_code': rs.error_code,
                        'error_msg': rs.error_msg,
                        'ts_code': ts_code,
                        'baostock_code': baostock_code,
                        'start_date': start_date,
                        'end_date': end_date,
                        'frequency': frequency
                    }
                )
            
            # 转换为DataFrame
            data_list = []
            while (rs.error_code == '0') & rs.next():
                data_list.append(rs.get_row_data())
            
            if not data_list:
                self.logger.warning(f"未获取到指数数据: {ts_code}, {start_date} - {end_date}")
                return pd.DataFrame()
            
            df = pd.DataFrame(data_list, columns=rs.fields)
            
            # 标准化列名和数据类型
            df = self._standardize_index_ohlcv_columns(df)
            
            self.logger.info(f"成功获取指数{frequency}线数据: {ts_code}, {len(df)}条记录")
            return df
            
        except Exception as e:
            if isinstance(e, (DataSourceError, ValidationError)):
                raise
            raise DataSourceError(
                f"获取指数{frequency}线数据时发生错误: {str(e)}",
                error_code="BAOSTOCK_UNEXPECTED_ERROR",
                details={
                    'ts_code': ts_code,
                    'start_date': start_date,
                    'end_date': end_date,
                    'frequency': frequency
                }
            )
    
    async def get_fund_basic(self, **kwargs) -> pd.DataFrame:
        """
        获取基金基础信息（baostock不支持基金数据）
        
        Args:
            **kwargs: 查询参数
            
        Returns:
            基金基础信息DataFrame
        """
        raise NotImplementedError("Baostock不支持基金数据获取，请使用其他数据源")
    
    async def get_fund_nav(self, ts_code: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        获取基金净值数据（baostock不支持基金数据）
        
        Args:
            ts_code: 基金代码
            start_date: 开始日期，格式YYYY-MM-DD
            end_date: 结束日期，格式YYYY-MM-DD
            
        Returns:
            基金净值数据DataFrame
        """
        raise NotImplementedError("Baostock不支持基金数据获取，请使用其他数据源")
    
    async def is_trade_date(self, date: str) -> bool:
        """
        判断指定日期是否为交易日
        
        Args:
            date: 日期，格式YYYY-MM-DD
            
        Returns:
            是否为交易日
        """
        validate_date_format(date)
        
        # 查询单日交易日历
        trade_cal = await self.get_trade_cal(date, date)
        
        if trade_cal.empty:
            return False
        
        # 检查is_open字段
        return bool(trade_cal.iloc[0]['is_open']) if 'is_open' in trade_cal.columns else False
    
    async def get_next_trade_date(self, date: str, n: int = 1) -> str:
        """
        获取指定日期之后的第n个交易日
        
        Args:
            date: 起始日期，格式YYYY-MM-DD
            n: 向后查找的交易日数量，默认1
            
        Returns:
            交易日期，格式YYYY-MM-DD
        """
        validate_date_format(date)
        
        if n <= 0:
            raise ValidationError("n必须大于0")
        
        # 查询未来一段时间的交易日历（最多查询100天）
        from datetime import datetime, timedelta
        start_date = datetime.strptime(date, '%Y-%m-%d')
        end_date = start_date + timedelta(days=100)
        end_date_str = end_date.strftime('%Y-%m-%d')
        
        trade_cal = await self.get_trade_cal(date, end_date_str)
        
        if trade_cal.empty:
            raise DataSourceError("未找到交易日历数据", error_code="NO_TRADE_CAL_DATA")
        
        # 过滤出交易日
        trade_days = trade_cal[trade_cal['is_open'] == 1]
        
        if len(trade_days) < n:
            raise DataSourceError(f"未找到足够的交易日数据，需要{n}个，实际{len(trade_days)}个")
        
        # 返回第n个交易日
        target_date = trade_days.iloc[n-1]['cal_date']
        
        # 转换日期格式
        if len(target_date) == 8:  # YYYYMMDD格式
            return f"{target_date[:4]}-{target_date[4:6]}-{target_date[6:8]}"
        else:
            return target_date
    
    async def get_prev_trade_date(self, date: str, n: int = 1) -> str:
        """
        获取指定日期之前的第n个交易日
        
        Args:
            date: 起始日期，格式YYYY-MM-DD
            n: 向前查找的交易日数量，默认1
            
        Returns:
            交易日期，格式YYYY-MM-DD
        """
        validate_date_format(date)
        
        if n <= 0:
            raise ValidationError("n必须大于0")
        
        # 查询过去一段时间的交易日历（最多查询100天）
        from datetime import datetime, timedelta
        end_date = datetime.strptime(date, '%Y-%m-%d')
        start_date = end_date - timedelta(days=100)
        start_date_str = start_date.strftime('%Y-%m-%d')
        
        trade_cal = await self.get_trade_cal(start_date_str, date)
        
        if trade_cal.empty:
            raise DataSourceError("未找到交易日历数据", error_code="NO_TRADE_CAL_DATA")
        
        # 过滤出交易日并按日期倒序排列
        trade_days = trade_cal[trade_cal['is_open'] == 1].sort_values('cal_date', ascending=False)
        
        if len(trade_days) < n:
            raise DataSourceError(f"未找到足够的交易日数据，需要{n}个，实际{len(trade_days)}个")
        
        # 返回第n个交易日
        target_date = trade_days.iloc[n-1]['cal_date']
        
        # 转换日期格式
        if len(target_date) == 8:  # YYYYMMDD格式
            return f"{target_date[:4]}-{target_date[4:6]}-{target_date[6:8]}"
        else:
            return target_date
    
    def convert_input_code(self, code: str) -> str:
        """将输入代码转换为baostock所需格式"""
        return self._convert_stock_code(code)
    
    def convert_output_code(self, code: str) -> str:
        """将baostock返回的代码转换为标准格式"""
        return self._convert_to_standard_code(code)
    
    def get_required_format(self) -> str:
        """获取baostock要求的代码格式"""
        return "baostock"
    
    async def health_check(self) -> bool:
        """
        健康检查
        
        Returns:
            是否健康
        """
        if not self.is_available():
            return False
        
        try:
            await self._ensure_login()
            return True
        except Exception as e:
            self.logger.warning(f"Baostock健康检查失败: {e}")
            return False