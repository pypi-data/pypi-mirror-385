"""
缓存层实现

提供多级缓存支持，包括内存缓存和SQLite持久化缓存
"""

import sqlite3
import pickle
import time
import logging
from collections import OrderedDict
from typing import Optional, Dict, Any
from typing import TYPE_CHECKING
import pandas as pd
from datetime import datetime, timedelta
import threading
import os

if TYPE_CHECKING:
    from ..config import Config

logger = logging.getLogger(__name__)


class CacheEntry:
    """缓存条目"""
    
    def __init__(self, data: pd.DataFrame, expire_time: Optional[datetime] = None):
        self.data = data
        self.expire_time = expire_time
        self.access_time = datetime.now()
    
    def is_expired(self) -> bool:
        """检查是否过期"""
        if self.expire_time is None:
            return False
        return datetime.now() > self.expire_time


class MemoryCache:
    """内存缓存实现，使用LRU策略"""
    
    def __init__(self, max_size: int = 1000):
        """
        初始化内存缓存
        
        Args:
            max_size: 最大缓存条目数
        """
        self.max_size = max_size
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._lock = threading.RLock()
        
    async def get(self, key: str) -> Optional[pd.DataFrame]:
        """
        从内存缓存获取数据
        
        Args:
            key: 缓存键
            
        Returns:
            缓存的数据，如果不存在或过期则返回None
        """
        with self._lock:
            if key not in self._cache:
                return None
                
            entry = self._cache[key]
            
            # 检查是否过期
            if entry.is_expired():
                del self._cache[key]
                return None
            
            # 更新访问时间并移到末尾（LRU策略）
            entry.access_time = datetime.now()
            self._cache.move_to_end(key)
            
            return entry.data.copy()
        
    async def set(self, key: str, data: pd.DataFrame, expire_hours: int = None):
        """
        设置内存缓存数据
        
        Args:
            key: 缓存键
            data: 要缓存的数据
            expire_hours: 过期时间（小时），None表示不过期
        """
        with self._lock:
            # 计算过期时间
            expire_time = None
            if expire_hours is not None:
                expire_time = datetime.now() + timedelta(hours=expire_hours)
            
            # 创建缓存条目
            entry = CacheEntry(data.copy(), expire_time)
            
            # 如果键已存在，更新并移到末尾
            if key in self._cache:
                self._cache[key] = entry
                self._cache.move_to_end(key)
            else:
                # 检查是否需要清理空间
                while len(self._cache) >= self.max_size:
                    # 删除最久未使用的条目
                    oldest_key = next(iter(self._cache))
                    del self._cache[oldest_key]
                
                self._cache[key] = entry
    
    async def delete(self, key: str) -> bool:
        """
        删除缓存条目
        
        Args:
            key: 缓存键
            
        Returns:
            是否成功删除
        """
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False
    
    def clear(self):
        """清空所有缓存"""
        with self._lock:
            self._cache.clear()
    
    def size(self) -> int:
        """获取当前缓存大小"""
        with self._lock:
            return len(self._cache)
    
    def clear_expired(self):
        """清理过期的缓存条目"""
        with self._lock:
            expired_keys = []
            for key, entry in self._cache.items():
                if entry.is_expired():
                    expired_keys.append(key)
            
            for key in expired_keys:
                del self._cache[key]
                
            logger.debug(f"清理了 {len(expired_keys)} 个过期的内存缓存条目")
    
    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        with self._lock:
            return {
                'size': len(self._cache),
                'max_size': self.max_size,
                'usage_ratio': len(self._cache) / self.max_size if self.max_size > 0 else 0
            }


class SQLiteCache:
    """SQLite持久化缓存实现"""
    
    def __init__(self, db_path: str):
        """
        初始化SQLite缓存
        
        Args:
            db_path: 数据库文件路径
        """
        self.db_path = db_path
        self._lock = threading.RLock()
        self._init_database()
        
    def _init_database(self):
        """初始化数据库表结构"""
        # 确保目录存在
        db_dir = os.path.dirname(self.db_path)
        if db_dir:  # 只有当目录不为空时才创建
            os.makedirs(db_dir, exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS cache_data (
                    key TEXT PRIMARY KEY,
                    data BLOB NOT NULL,
                    created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expire_time TIMESTAMP,
                    access_count INTEGER DEFAULT 0,
                    last_access_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 创建索引以提高查询性能
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_expire_time 
                ON cache_data(expire_time)
            ''')
            
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_last_access 
                ON cache_data(last_access_time)
            ''')
            
            conn.commit()
        
    async def get(self, key: str) -> Optional[pd.DataFrame]:
        """
        从SQLite缓存获取数据
        
        Args:
            key: 缓存键
            
        Returns:
            缓存的数据，如果不存在或过期则返回None
        """
        with self._lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    
                    # 查询数据
                    cursor.execute('''
                        SELECT data, expire_time FROM cache_data 
                        WHERE key = ?
                    ''', (key,))
                    
                    result = cursor.fetchone()
                    if result is None:
                        return None
                    
                    data_blob, expire_time_str = result
                    
                    # 检查是否过期
                    if expire_time_str:
                        expire_time = datetime.fromisoformat(expire_time_str)
                        if datetime.now() > expire_time:
                            # 删除过期数据
                            cursor.execute('DELETE FROM cache_data WHERE key = ?', (key,))
                            conn.commit()
                            return None
                    
                    # 更新访问统计
                    cursor.execute('''
                        UPDATE cache_data 
                        SET access_count = access_count + 1,
                            last_access_time = CURRENT_TIMESTAMP
                        WHERE key = ?
                    ''', (key,))
                    conn.commit()
                    
                    # 反序列化数据
                    data = pickle.loads(data_blob)
                    return data
                    
            except Exception as e:
                logger.error(f"SQLite缓存获取失败: {e}")
                return None
        
    async def set(self, key: str, data: pd.DataFrame, expire_hours: int = None):
        """
        设置SQLite缓存数据
        
        Args:
            key: 缓存键
            data: 要缓存的数据
            expire_hours: 过期时间（小时），None表示不过期
        """
        with self._lock:
            try:
                # 序列化数据
                data_blob = pickle.dumps(data)
                
                # 计算过期时间
                expire_time = None
                if expire_hours is not None:
                    expire_time = datetime.now() + timedelta(hours=expire_hours)
                
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    
                    # 插入或更新数据
                    cursor.execute('''
                        INSERT OR REPLACE INTO cache_data 
                        (key, data, created_time, expire_time, access_count, last_access_time)
                        VALUES (?, ?, CURRENT_TIMESTAMP, ?, 0, CURRENT_TIMESTAMP)
                    ''', (key, data_blob, expire_time.isoformat() if expire_time else None))
                    
                    conn.commit()
                    
            except Exception as e:
                logger.error(f"SQLite缓存设置失败: {e}")
    
    async def delete(self, key: str) -> bool:
        """
        删除缓存条目
        
        Args:
            key: 缓存键
            
        Returns:
            是否成功删除
        """
        with self._lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute('DELETE FROM cache_data WHERE key = ?', (key,))
                    conn.commit()
                    return cursor.rowcount > 0
            except Exception as e:
                logger.error(f"SQLite缓存删除失败: {e}")
                return False
    
    def clear(self):
        """清空所有缓存"""
        with self._lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    conn.execute('DELETE FROM cache_data')
                    conn.commit()
            except Exception as e:
                logger.error(f"SQLite缓存清空失败: {e}")
    
    def clear_expired(self):
        """清理过期的缓存条目"""
        with self._lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute('''
                        DELETE FROM cache_data 
                        WHERE expire_time IS NOT NULL 
                        AND expire_time < CURRENT_TIMESTAMP
                    ''')
                    deleted_count = cursor.rowcount
                    conn.commit()
                    
                    logger.debug(f"清理了 {deleted_count} 个过期的SQLite缓存条目")
                    
            except Exception as e:
                logger.error(f"SQLite缓存清理失败: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        with self._lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    
                    # 总条目数
                    cursor.execute('SELECT COUNT(*) FROM cache_data')
                    total_count = cursor.fetchone()[0]
                    
                    # 过期条目数
                    cursor.execute('''
                        SELECT COUNT(*) FROM cache_data 
                        WHERE expire_time IS NOT NULL 
                        AND expire_time < CURRENT_TIMESTAMP
                    ''')
                    expired_count = cursor.fetchone()[0]
                    
                    # 数据库文件大小
                    db_size = os.path.getsize(self.db_path) if os.path.exists(self.db_path) else 0
                    
                    return {
                        'total_entries': total_count,
                        'expired_entries': expired_count,
                        'valid_entries': total_count - expired_count,
                        'db_size_bytes': db_size,
                        'db_size_mb': round(db_size / (1024 * 1024), 2)
                    }
                    
            except Exception as e:
                logger.error(f"获取SQLite缓存统计失败: {e}")
                return {}


class CacheLayer:
    """多级缓存实现，协调内存缓存和SQLite缓存"""
    
    def __init__(self, config: 'Config'):
        """
        初始化缓存层
        
        Args:
            config: 配置对象
        """
        self.memory_cache = MemoryCache(config.memory_cache_size)
        self.sqlite_cache = SQLiteCache(config.sqlite_db_path)
        self.config = config
        self._stats = {
            'memory_hits': 0,
            'sqlite_hits': 0,
            'misses': 0,
            'sets': 0
        }
    
    async def get(self, key: str) -> Optional[pd.DataFrame]:
        """
        从缓存获取数据，实现多级缓存策略
        
        Args:
            key: 缓存键
            
        Returns:
            缓存的数据，如果不存在则返回None
        """
        # 1. 先从内存缓存获取
        data = await self.memory_cache.get(key)
        if data is not None:
            self._stats['memory_hits'] += 1
            return data
        
        # 2. 如果内存缓存没有，从SQLite缓存获取
        data = await self.sqlite_cache.get(key)
        if data is not None:
            self._stats['sqlite_hits'] += 1
            # 3. 将SQLite中的数据同步到内存缓存
            await self.memory_cache.set(key, data, self.config.cache_expire_hours)
            return data
        
        # 4. 两级缓存都没有数据
        self._stats['misses'] += 1
        return None
        
    async def set(self, key: str, data: pd.DataFrame, expire_hours: int = None):
        """
        设置缓存数据，同时更新内存和SQLite缓存
        
        Args:
            key: 缓存键
            data: 要缓存的数据
            expire_hours: 过期时间（小时），None使用配置默认值
        """
        if expire_hours is None:
            expire_hours = self.config.cache_expire_hours
        
        # 同时设置内存缓存和SQLite缓存
        await self.memory_cache.set(key, data, expire_hours)
        await self.sqlite_cache.set(key, data, expire_hours)
        
        self._stats['sets'] += 1
    
    async def delete(self, key: str) -> bool:
        """
        删除缓存条目
        
        Args:
            key: 缓存键
            
        Returns:
            是否成功删除
        """
        memory_deleted = await self.memory_cache.delete(key)
        sqlite_deleted = await self.sqlite_cache.delete(key)
        
        return memory_deleted or sqlite_deleted
        
    def is_expired(self, key: str) -> bool:
        """
        检查缓存是否过期
        
        Args:
            key: 缓存键
            
        Returns:
            是否过期
        """
        # 检查内存缓存中的条目是否过期
        with self.memory_cache._lock:
            if key in self.memory_cache._cache:
                return self.memory_cache._cache[key].is_expired()
        
        # 如果内存缓存中没有，这里简化处理，认为需要重新获取
        return True
        
    def clear_expired(self):
        """清理过期缓存"""
        self.memory_cache.clear_expired()
        self.sqlite_cache.clear_expired()
    
    def clear(self):
        """清空所有缓存"""
        self.memory_cache.clear()
        self.sqlite_cache.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        memory_stats = self.memory_cache.get_stats()
        sqlite_stats = self.sqlite_cache.get_stats()
        
        total_requests = self._stats['memory_hits'] + self._stats['sqlite_hits'] + self._stats['misses']
        hit_rate = 0
        if total_requests > 0:
            hit_rate = (self._stats['memory_hits'] + self._stats['sqlite_hits']) / total_requests
        
        return {
            'memory_cache': memory_stats,
            'sqlite_cache': sqlite_stats,
            'hit_stats': {
                'memory_hits': self._stats['memory_hits'],
                'sqlite_hits': self._stats['sqlite_hits'],
                'misses': self._stats['misses'],
                'total_sets': self._stats['sets'],
                'hit_rate': round(hit_rate, 4)
            }
        }
    
    async def close(self):
        """关闭缓存层，清理资源"""
        # 内存缓存不需要特殊清理
        # SQLite缓存也不需要特殊清理，连接会自动关闭
        pass