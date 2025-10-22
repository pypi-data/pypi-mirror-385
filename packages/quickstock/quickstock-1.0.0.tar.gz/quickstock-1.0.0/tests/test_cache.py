"""
缓存层单元测试
"""

import pytest
import pandas as pd
import tempfile
import os
import asyncio
import sqlite3
import pickle
from datetime import datetime, timedelta
from unittest.mock import Mock

from quickstock.core.cache import MemoryCache, SQLiteCache, CacheLayer, CacheEntry


class TestCacheEntry:
    """测试缓存条目"""
    
    def test_cache_entry_creation(self):
        """测试缓存条目创建"""
        data = pd.DataFrame({'a': [1, 2, 3]})
        entry = CacheEntry(data)
        
        assert entry.data.equals(data)
        assert entry.expire_time is None
        assert isinstance(entry.access_time, datetime)
    
    def test_cache_entry_with_expiry(self):
        """测试带过期时间的缓存条目"""
        data = pd.DataFrame({'a': [1, 2, 3]})
        expire_time = datetime.now() + timedelta(hours=1)
        entry = CacheEntry(data, expire_time)
        
        assert entry.expire_time == expire_time
        assert not entry.is_expired()
    
    def test_cache_entry_expired(self):
        """测试过期的缓存条目"""
        data = pd.DataFrame({'a': [1, 2, 3]})
        expire_time = datetime.now() - timedelta(hours=1)
        entry = CacheEntry(data, expire_time)
        
        assert entry.is_expired()


class TestMemoryCache:
    """测试内存缓存"""
    
    @pytest.fixture
    def memory_cache(self):
        """创建内存缓存实例"""
        return MemoryCache(max_size=3)
    
    @pytest.fixture
    def sample_data(self):
        """创建测试数据"""
        return pd.DataFrame({
            'date': ['2023-01-01', '2023-01-02', '2023-01-03'],
            'value': [100, 200, 300]
        })
    
    @pytest.mark.asyncio
    async def test_set_and_get(self, memory_cache, sample_data):
        """测试设置和获取缓存"""
        key = "test_key"
        
        # 设置缓存
        await memory_cache.set(key, sample_data)
        
        # 获取缓存
        result = await memory_cache.get(key)
        
        assert result is not None
        assert result.equals(sample_data)
        assert memory_cache.size() == 1
    
    @pytest.mark.asyncio
    async def test_get_nonexistent_key(self, memory_cache):
        """测试获取不存在的键"""
        result = await memory_cache.get("nonexistent")
        assert result is None
    
    @pytest.mark.asyncio
    async def test_lru_eviction(self, memory_cache, sample_data):
        """测试LRU淘汰策略"""
        # 填满缓存
        for i in range(3):
            await memory_cache.set(f"key_{i}", sample_data)
        
        assert memory_cache.size() == 3
        
        # 添加第4个条目，应该淘汰最久未使用的
        await memory_cache.set("key_3", sample_data)
        
        assert memory_cache.size() == 3
        assert await memory_cache.get("key_0") is None  # 最早的被淘汰
        assert await memory_cache.get("key_3") is not None  # 新的存在
    
    @pytest.mark.asyncio
    async def test_access_updates_lru(self, memory_cache, sample_data):
        """测试访问更新LRU顺序"""
        # 添加3个条目
        for i in range(3):
            await memory_cache.set(f"key_{i}", sample_data)
        
        # 访问第一个条目
        await memory_cache.get("key_0")
        
        # 添加新条目，应该淘汰key_1（最久未访问）
        await memory_cache.set("key_3", sample_data)
        
        assert await memory_cache.get("key_0") is not None  # 被访问过，不被淘汰
        assert await memory_cache.get("key_1") is None      # 最久未访问，被淘汰
        assert await memory_cache.get("key_2") is not None
        assert await memory_cache.get("key_3") is not None
    
    @pytest.mark.asyncio
    async def test_expiry(self, memory_cache, sample_data):
        """测试缓存过期"""
        key = "test_key"
        
        # 设置很短的过期时间（1毫秒）
        await memory_cache.set(key, sample_data, expire_hours=1/3600000)  # 1毫秒
        
        # 立即获取应该成功
        result = await memory_cache.get(key)
        assert result is not None
        
        # 等待过期
        await asyncio.sleep(0.002)  # 等待2毫秒
        
        # 再次获取应该返回None
        result = await memory_cache.get(key)
        assert result is None
        assert memory_cache.size() == 0  # 过期条目被自动删除
    
    @pytest.mark.asyncio
    async def test_delete(self, memory_cache, sample_data):
        """测试删除缓存条目"""
        key = "test_key"
        
        await memory_cache.set(key, sample_data)
        assert await memory_cache.get(key) is not None
        
        # 删除条目
        deleted = await memory_cache.delete(key)
        assert deleted is True
        assert await memory_cache.get(key) is None
        assert memory_cache.size() == 0
        
        # 删除不存在的条目
        deleted = await memory_cache.delete("nonexistent")
        assert deleted is False
    
    def test_clear(self, memory_cache, sample_data):
        """测试清空缓存"""
        # 添加一些数据
        asyncio.run(memory_cache.set("key1", sample_data))
        asyncio.run(memory_cache.set("key2", sample_data))
        
        assert memory_cache.size() == 2
        
        # 清空缓存
        memory_cache.clear()
        
        assert memory_cache.size() == 0
        assert asyncio.run(memory_cache.get("key1")) is None
    
    def test_clear_expired(self, memory_cache, sample_data):
        """测试清理过期条目"""
        # 添加正常条目
        asyncio.run(memory_cache.set("normal_key", sample_data, expire_hours=1))
        
        # 添加过期条目（手动设置过期时间）
        with memory_cache._lock:
            expired_entry = CacheEntry(sample_data, datetime.now() - timedelta(hours=1))
            memory_cache._cache["expired_key"] = expired_entry
        
        assert memory_cache.size() == 2
        
        # 清理过期条目
        memory_cache.clear_expired()
        
        assert memory_cache.size() == 1
        assert asyncio.run(memory_cache.get("normal_key")) is not None
        assert asyncio.run(memory_cache.get("expired_key")) is None
    
    def test_get_stats(self, memory_cache, sample_data):
        """测试获取统计信息"""
        stats = memory_cache.get_stats()
        
        assert stats['size'] == 0
        assert stats['max_size'] == 3
        assert stats['usage_ratio'] == 0
        
        # 添加一些数据
        asyncio.run(memory_cache.set("key1", sample_data))
        
        stats = memory_cache.get_stats()
        assert stats['size'] == 1
        assert stats['usage_ratio'] == 1/3


class TestSQLiteCache:
    """测试SQLite缓存"""
    
    @pytest.fixture
    def temp_db_path(self):
        """创建临时数据库路径"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        yield db_path
        # 清理
        if os.path.exists(db_path):
            os.unlink(db_path)
    
    @pytest.fixture
    def sqlite_cache(self, temp_db_path):
        """创建SQLite缓存实例"""
        return SQLiteCache(temp_db_path)
    
    @pytest.fixture
    def sample_data(self):
        """创建测试数据"""
        return pd.DataFrame({
            'date': ['2023-01-01', '2023-01-02', '2023-01-03'],
            'value': [100, 200, 300]
        })
    
    @pytest.mark.asyncio
    async def test_set_and_get(self, sqlite_cache, sample_data):
        """测试设置和获取缓存"""
        key = "test_key"
        
        # 设置缓存
        await sqlite_cache.set(key, sample_data)
        
        # 获取缓存
        result = await sqlite_cache.get(key)
        
        assert result is not None
        assert result.equals(sample_data)
    
    @pytest.mark.asyncio
    async def test_get_nonexistent_key(self, sqlite_cache):
        """测试获取不存在的键"""
        result = await sqlite_cache.get("nonexistent")
        assert result is None
    
    @pytest.mark.asyncio
    async def test_expiry(self, sqlite_cache, sample_data):
        """测试缓存过期"""
        key = "test_key"
        
        # 设置已过期的数据（过去的时间）
        past_time = datetime.now() - timedelta(hours=1)
        
        # 直接在数据库中插入过期数据
        data_blob = pickle.dumps(sample_data)
        
        with sqlite3.connect(sqlite_cache.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO cache_data 
                (key, data, created_time, expire_time, access_count, last_access_time)
                VALUES (?, ?, CURRENT_TIMESTAMP, ?, 0, CURRENT_TIMESTAMP)
            ''', (key, data_blob, past_time.isoformat()))
            conn.commit()
        
        # 获取应该返回None（因为已过期）
        result = await sqlite_cache.get(key)
        assert result is None
    
    @pytest.mark.asyncio
    async def test_delete(self, sqlite_cache, sample_data):
        """测试删除缓存条目"""
        key = "test_key"
        
        await sqlite_cache.set(key, sample_data)
        assert await sqlite_cache.get(key) is not None
        
        # 删除条目
        deleted = await sqlite_cache.delete(key)
        assert deleted is True
        assert await sqlite_cache.get(key) is None
        
        # 删除不存在的条目
        deleted = await sqlite_cache.delete("nonexistent")
        assert deleted is False
    
    def test_clear(self, sqlite_cache, sample_data):
        """测试清空缓存"""
        # 添加一些数据
        asyncio.run(sqlite_cache.set("key1", sample_data))
        asyncio.run(sqlite_cache.set("key2", sample_data))
        
        # 清空缓存
        sqlite_cache.clear()
        
        assert asyncio.run(sqlite_cache.get("key1")) is None
        assert asyncio.run(sqlite_cache.get("key2")) is None
    
    def test_get_stats(self, sqlite_cache, sample_data):
        """测试获取统计信息"""
        stats = sqlite_cache.get_stats()
        
        assert stats['total_entries'] == 0
        assert stats['expired_entries'] == 0
        assert stats['valid_entries'] == 0
        
        # 添加一些数据
        asyncio.run(sqlite_cache.set("key1", sample_data))
        
        stats = sqlite_cache.get_stats()
        assert stats['total_entries'] == 1
        assert stats['valid_entries'] == 1


class TestCacheLayer:
    """测试缓存层"""
    
    @pytest.fixture
    def mock_config(self):
        """创建模拟配置"""
        config = Mock()
        config.memory_cache_size = 100
        config.sqlite_db_path = tempfile.mktemp(suffix='.db')
        config.cache_expire_hours = 24
        return config
    
    @pytest.fixture
    def cache_layer(self, mock_config):
        """创建缓存层实例"""
        layer = CacheLayer(mock_config)
        yield layer
        # 清理
        if os.path.exists(mock_config.sqlite_db_path):
            os.unlink(mock_config.sqlite_db_path)
    
    @pytest.fixture
    def sample_data(self):
        """创建测试数据"""
        return pd.DataFrame({
            'date': ['2023-01-01', '2023-01-02'],
            'value': [100, 200]
        })
    
    @pytest.mark.asyncio
    async def test_multi_level_cache_set_get(self, cache_layer, sample_data):
        """测试多级缓存的设置和获取"""
        key = "test_key"
        
        # 设置缓存
        await cache_layer.set(key, sample_data)
        
        # 获取缓存（应该从内存缓存命中）
        result = await cache_layer.get(key)
        
        assert result is not None
        assert result.equals(sample_data)
        
        stats = cache_layer.get_stats()
        assert stats['hit_stats']['memory_hits'] == 1
        assert stats['hit_stats']['sqlite_hits'] == 0
    
    @pytest.mark.asyncio
    async def test_sqlite_fallback(self, cache_layer, sample_data):
        """测试SQLite缓存回退机制"""
        key = "test_key"
        
        # 直接设置SQLite缓存
        await cache_layer.sqlite_cache.set(key, sample_data)
        
        # 从缓存层获取（应该从SQLite命中并同步到内存）
        result = await cache_layer.get(key)
        
        assert result is not None
        assert result.equals(sample_data)
        
        stats = cache_layer.get_stats()
        assert stats['hit_stats']['memory_hits'] == 0
        assert stats['hit_stats']['sqlite_hits'] == 1
        
        # 再次获取应该从内存缓存命中
        result = await cache_layer.get(key)
        assert result is not None
        
        stats = cache_layer.get_stats()
        assert stats['hit_stats']['memory_hits'] == 1
        assert stats['hit_stats']['sqlite_hits'] == 1
    
    @pytest.mark.asyncio
    async def test_cache_miss(self, cache_layer):
        """测试缓存未命中"""
        result = await cache_layer.get("nonexistent")
        
        assert result is None
        
        stats = cache_layer.get_stats()
        assert stats['hit_stats']['misses'] == 1
    
    @pytest.mark.asyncio
    async def test_delete_from_both_caches(self, cache_layer, sample_data):
        """测试从两级缓存删除"""
        key = "test_key"
        
        # 设置缓存
        await cache_layer.set(key, sample_data)
        
        # 删除缓存
        deleted = await cache_layer.delete(key)
        assert deleted is True
        
        # 验证两级缓存都被删除
        assert await cache_layer.memory_cache.get(key) is None
        assert await cache_layer.sqlite_cache.get(key) is None
    
    def test_clear_expired(self, cache_layer):
        """测试清理过期缓存"""
        # 这里主要测试方法调用不出错
        cache_layer.clear_expired()
    
    def test_get_comprehensive_stats(self, cache_layer, sample_data):
        """测试获取综合统计信息"""
        # 添加一些数据
        asyncio.run(cache_layer.set("key1", sample_data))
        asyncio.run(cache_layer.get("key1"))  # 内存命中
        asyncio.run(cache_layer.get("nonexistent"))  # 未命中
        
        stats = cache_layer.get_stats()
        
        assert 'memory_cache' in stats
        assert 'sqlite_cache' in stats
        assert 'hit_stats' in stats
        
        hit_stats = stats['hit_stats']
        assert hit_stats['memory_hits'] == 1
        assert hit_stats['misses'] == 1
        assert hit_stats['total_sets'] == 1
        assert hit_stats['hit_rate'] == 0.5  # 1命中 / 2总请求