"""
QuickStock SDK - 现代化的金融数据获取SDK

提供统一、高效、可扩展的金融数据访问接口，支持多数据源集成，
具备完善的缓存机制和错误处理能力。

主要功能:
- 股票、指数、基金等金融数据获取
- 多数据源支持 (Tushare, 东方财富, 同花顺等)
- 本地缓存机制
- 统一的数据格式
- 异步数据获取支持

使用示例:
    >>> from quickstock import QuickStockClient
    >>> client = QuickStockClient()
    >>> data = client.stock_basic()
"""

from .client import QuickStockClient
from .config import Config
from .core.errors import (
    QuickStockError,
    DataSourceError,
    CacheError,
    ValidationError,
    RateLimitError,
    NetworkError
)

__version__ = "1.0.0"
__author__ = "QuickStock Team"

__all__ = [
    "QuickStockClient",
    "Config",
    "QuickStockError",
    "DataSourceError", 
    "CacheError",
    "ValidationError",
    "RateLimitError",
    "NetworkError",
]