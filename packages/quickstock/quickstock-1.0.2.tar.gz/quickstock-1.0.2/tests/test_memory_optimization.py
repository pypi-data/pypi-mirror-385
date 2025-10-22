"""
内存优化功能测试

测试内存监控、垃圾回收优化、流式处理等功能
"""

import pytest
import pandas as pd
import numpy as np
import asyncio
import gc
import time
from unittest.mock import Mock, patch, MagicMock

from quickstock.utils.memory import (
    MemoryMonitor, GarbageCollectionOptimizer, DataFrameOptimizer,
    StreamProcessor, MemoryEfficientCache, get_memory_monitor, get_gc_optimizer
)
from quickstock.core.data_manager import DataManager
from quickstock.config import Config
from quickstock.models import DataRequest


class TestMemoryMonitor:
    """内存监控器测试"""
    
    def test_memory_monitor_init(self):
        """测试内存监控器初始化"""
        monitor = MemoryMonitor(warning_threshold=70.0, critical_threshold=85.0)
        
        assert monitor.warning_threshold == 70.0
        assert monitor.critical_threshold == 85.0
        assert 'warning' in monitor._callbacks
        assert 'critical' in monitor._callbacks
        assert 'normal' in monitor._callbacks
    
    def test_get_memory_stats(self):
        """测试获取内存统计信息"""
        monitor = MemoryMonitor()
        stats = monitor.get_memory_stats()
        
        assert hasattr(stats, 'total_memory_mb')
        assert hasattr(stats, 'available_memory_mb')
        assert hasattr(stats, 'used_memory_mb')
        assert hasattr(stats, 'memory_percent')
        assert hasattr(stats, 'process_memory_mb')
        assert hasattr(stats, 'process_memory_percent')
        
        assert stats.total_memory_mb >= 0
        assert stats.process_memory_mb >= 0
    
    def test_check_memory_status(self):
        """测试内存状态检查"""
        monitor = MemoryMonitor(warning_threshold=90.0, critical_threshold=95.0)
        status = monitor.check_memory_status()
        
        assert status in ['normal', 'warning', 'critical']
    
    def test_register_callback(self):
        """测试注册回调函数"""
        monitor = MemoryMonitor()
        callback_called = False
        
        def test_callback(stats):
            nonlocal callback_called
            callback_called = True
        
        monitor.register_callback('warning', test_callback)
        assert len(monitor._callbacks['warning']) == 1
        
        # 触发回调
        stats = monitor.get_memory_stats()
        monitor.trigger_callbacks('warning', stats)
        assert callback_called
    
    def test_monitor_context(self):
        """测试内存监控上下文管理器"""
        monitor = MemoryMonitor()
        
        with monitor.monitor_context(log_stats=False) as start_stats:
            assert hasattr(start_stats, 'process_memory_mb')
            # 分配一些内存
            data = np.random.random((1000, 100))
            del data


class TestGarbageCollectionOptimizer:
    """垃圾回收优化器测试"""
    
    def test_gc_optimizer_init(self):
        """测试垃圾回收优化器初始化"""
        optimizer = GarbageCollectionOptimizer()
        
        assert 'collections' in optimizer._gc_stats
        assert 'objects_collected' in optimizer._gc_stats
        assert 'time_spent' in optimizer._gc_stats
    
    def test_optimize_gc_thresholds(self):
        """测试优化垃圾回收阈值"""
        optimizer = GarbageCollectionOptimizer()
        old_thresholds = gc.get_threshold()
        
        optimizer.optimize_gc_thresholds(1500, 15, 15)
        new_thresholds = gc.get_threshold()
        
        assert new_thresholds != old_thresholds
        assert new_thresholds[0] == 1500
        assert new_thresholds[1] == 15
        assert new_thresholds[2] == 15
        
        # 恢复原始阈值
        gc.set_threshold(*old_thresholds)
    
    def test_force_gc(self):
        """测试强制垃圾回收"""
        optimizer = GarbageCollectionOptimizer()
        
        # 创建一些垃圾对象
        garbage = []
        for i in range(1000):
            garbage.append([i] * 100)
        del garbage
        
        initial_collections = optimizer._gc_stats['collections']
        collected = optimizer.force_gc()
        
        assert isinstance(collected, int)
        assert collected >= 0
        assert optimizer._gc_stats['collections'] == initial_collections + 1
    
    def test_get_gc_stats(self):
        """测试获取垃圾回收统计信息"""
        optimizer = GarbageCollectionOptimizer()
        stats = optimizer.get_gc_stats()
        
        assert 'collections' in stats
        assert 'objects_collected' in stats
        assert 'time_spent' in stats
        assert 'gc_counts' in stats
        assert 'gc_threshold' in stats
        assert 'gc_stats' in stats
    
    def test_gc_disabled_context(self):
        """测试垃圾回收禁用上下文管理器"""
        optimizer = GarbageCollectionOptimizer()
        
        was_enabled = gc.isenabled()
        
        with optimizer.gc_disabled():
            assert not gc.isenabled()
        
        assert gc.isenabled() == was_enabled


class TestDataFrameOptimizer:
    """DataFrame优化器测试"""
    
    def test_optimize_dtypes_basic(self):
        """测试基本数据类型优化"""
        # 创建测试数据
        df = pd.DataFrame({
            'int_col': [1, 2, 3, 4, 5],
            'float_col': [1.1, 2.2, 3.3, 4.4, 5.5],
            'str_col': ['A', 'B', 'A', 'B', 'A']
        })
        
        original_memory = df.memory_usage(deep=True).sum()
        optimized_df = DataFrameOptimizer.optimize_dtypes(df)
        optimized_memory = optimized_df.memory_usage(deep=True).sum()
        
        # 优化后内存使用应该减少或保持不变
        assert optimized_memory <= original_memory
        
        # 检查数据类型优化
        assert optimized_df['int_col'].dtype in [np.int8, np.int16, np.int32, np.int64]
        assert optimized_df['str_col'].dtype.name == 'category'
    
    def test_optimize_dtypes_aggressive(self):
        """测试激进模式数据类型优化"""
        df = pd.DataFrame({
            'float_col': [1.123456789, 2.987654321, 3.456789012]
        })
        
        optimized_df = DataFrameOptimizer.optimize_dtypes(df, aggressive=True)
        
        # 激进模式可能会将float64转换为float32
        assert optimized_df['float_col'].dtype in [np.float32, np.float64]
    
    def test_optimize_dtypes_empty_dataframe(self):
        """测试空DataFrame的优化"""
        df = pd.DataFrame()
        optimized_df = DataFrameOptimizer.optimize_dtypes(df)
        
        assert optimized_df.empty
        assert len(optimized_df.columns) == 0
    
    def test_get_memory_usage(self):
        """测试获取DataFrame内存使用详情"""
        df = pd.DataFrame({
            'int_col': [1, 2, 3, 4, 5],
            'float_col': [1.1, 2.2, 3.3, 4.4, 5.5],
            'str_col': ['A', 'B', 'C', 'D', 'E']
        })
        
        usage = DataFrameOptimizer.get_memory_usage(df)
        
        assert 'total_mb' in usage
        assert 'index_mb' in usage
        assert 'columns' in usage
        
        assert usage['total_mb'] > 0
        assert len(usage['columns']) == 3
        
        for col_name, col_info in usage['columns'].items():
            assert 'memory_mb' in col_info
            assert 'dtype' in col_info
            assert 'null_count' in col_info
            assert 'unique_count' in col_info
    
    def test_get_memory_usage_empty_dataframe(self):
        """测试空DataFrame的内存使用"""
        df = pd.DataFrame()
        usage = DataFrameOptimizer.get_memory_usage(df)
        
        assert usage['total_mb'] == 0
        assert usage['columns'] == {}


class TestStreamProcessor:
    """流式处理器测试"""
    
    def test_stream_processor_init(self):
        """测试流式处理器初始化"""
        processor = StreamProcessor(chunk_size=5000, memory_limit_mb=200.0)
        
        assert processor.chunk_size == 5000
        assert processor.memory_limit_mb == 200.0
        assert hasattr(processor, 'memory_monitor')
        assert hasattr(processor, 'gc_optimizer')
    
    def test_process_dataframe_chunks(self):
        """测试DataFrame分块处理"""
        processor = StreamProcessor(chunk_size=100)
        
        # 创建测试数据
        df = pd.DataFrame({
            'col1': range(500),
            'col2': np.random.random(500)
        })
        
        def double_values(chunk):
            chunk['col1'] = chunk['col1'] * 2
            return chunk
        
        processed_chunks = list(processor.process_dataframe_chunks(
            df, double_values, optimize_memory=False
        ))
        
        # 检查分块数量
        expected_chunks = (len(df) + processor.chunk_size - 1) // processor.chunk_size
        assert len(processed_chunks) == expected_chunks
        
        # 检查处理结果
        combined_df = pd.concat(processed_chunks, ignore_index=True)
        assert len(combined_df) == len(df)
        assert all(combined_df['col1'] == df['col1'] * 2)
    
    def test_batch_process_requests(self):
        """测试批量处理请求"""
        processor = StreamProcessor(chunk_size=50)
        
        # 创建测试请求
        requests = list(range(200))
        
        def process_batch(batch):
            return [x * 2 for x in batch]
        
        processed_batches = list(processor.batch_process_requests(
            requests, process_batch, batch_size=30
        ))
        
        # 检查批次数量
        expected_batches = (len(requests) + 30 - 1) // 30
        assert len(processed_batches) == expected_batches
        
        # 检查处理结果
        all_results = []
        for batch in processed_batches:
            all_results.extend(batch)
        
        assert len(all_results) == len(requests)
        assert all_results == [x * 2 for x in requests]


class TestMemoryEfficientCache:
    """内存高效缓存测试"""
    
    def test_memory_efficient_cache_init(self):
        """测试内存高效缓存初始化"""
        cache = MemoryEfficientCache(max_memory_mb=50.0)
        
        assert cache.max_memory_mb == 50.0
        assert len(cache._cache) == 0
        assert len(cache._access_times) == 0
        assert len(cache._memory_usage) == 0
    
    def test_cache_set_get(self):
        """测试缓存设置和获取"""
        cache = MemoryEfficientCache(max_memory_mb=100.0)
        
        # 设置缓存
        test_data = pd.DataFrame({'col1': [1, 2, 3], 'col2': [4, 5, 6]})
        cache.set('test_key', test_data)
        
        # 获取缓存
        retrieved_data = cache.get('test_key')
        
        assert retrieved_data is not None
        pd.testing.assert_frame_equal(retrieved_data, test_data)
    
    def test_cache_cleanup(self):
        """测试缓存清理"""
        cache = MemoryEfficientCache(max_memory_mb=0.1)  # 很小的限制
        
        # 添加多个大对象
        for i in range(10):
            large_data = pd.DataFrame(np.random.random((1000, 100)))
            cache.set(f'key_{i}', large_data)
            time.sleep(0.01)  # 确保访问时间不同
        
        # 检查是否进行了清理
        assert len(cache._cache) < 10
    
    def test_cache_stats(self):
        """测试缓存统计信息"""
        cache = MemoryEfficientCache(max_memory_mb=100.0)
        
        # 添加一些数据
        test_data = pd.DataFrame({'col1': [1, 2, 3]})
        cache.set('test_key', test_data)
        
        stats = cache.get_stats()
        
        assert 'total_items' in stats
        assert 'total_memory_mb' in stats
        assert 'max_memory_mb' in stats
        assert 'memory_usage_percent' in stats
        assert 'average_item_size_mb' in stats
        
        assert stats['total_items'] == 1
        assert stats['max_memory_mb'] == 100.0


class TestDataManagerMemoryOptimization:
    """数据管理器内存优化测试"""
    
    @pytest.fixture
    def config(self):
        """测试配置"""
        return Config(
            cache_enabled=True,
            stream_chunk_size=100,
            memory_limit_mb=100.0,
            memory_batch_size=10
        )
    
    @pytest.fixture
    def data_manager(self, config):
        """测试数据管理器"""
        return DataManager(config)
    
    def test_memory_optimization_init(self, data_manager):
        """测试内存优化组件初始化"""
        assert hasattr(data_manager, 'memory_monitor')
        assert hasattr(data_manager, 'gc_optimizer')
        assert hasattr(data_manager, 'stream_processor')
        
        assert data_manager.stream_processor.chunk_size == 100
        assert data_manager.stream_processor.memory_limit_mb == 100.0
    
    def test_memory_callbacks(self, data_manager):
        """测试内存状态回调"""
        # 模拟内存警告
        mock_stats = Mock()
        mock_stats.process_memory_mb = 800.0
        mock_stats.memory_percent = 85.0
        
        # 测试警告回调
        data_manager._on_memory_warning(mock_stats)
        
        # 测试临界回调
        mock_stats.memory_percent = 95.0
        data_manager._on_memory_critical(mock_stats)
    
    @pytest.mark.asyncio
    async def test_get_data_streaming(self, data_manager):
        """测试流式数据获取"""
        # 模拟数据请求
        request = DataRequest(
            data_type='stock_daily',
            ts_code='000001.SZ',
            start_date='20230101',
            end_date='20230131'
        )
        
        # 模拟数据源返回大数据集
        large_data = pd.DataFrame({
            'ts_code': ['000001.SZ'] * 1000,
            'trade_date': ['20230101'] * 1000,
            'close': np.random.random(1000)
        })
        
        with patch.object(data_manager.source_manager, 'fetch_data', 
                         return_value=large_data):
            chunks = []
            async for chunk in data_manager.get_data_streaming(request, chunk_size=200):
                chunks.append(chunk)
            
            # 检查分块结果
            assert len(chunks) > 1  # 应该被分成多个块
            
            # 合并所有块
            combined_data = pd.concat(chunks, ignore_index=True)
            assert len(combined_data) == len(large_data)
    
    @pytest.mark.asyncio
    async def test_get_data_with_memory_optimization(self, data_manager):
        """测试内存优化的数据获取"""
        request = DataRequest(
            data_type='stock_basic',
            extra_params={'limit': 100}
        )
        
        # 模拟数据
        test_data = pd.DataFrame({
            'ts_code': [f'00000{i}.SZ' for i in range(100)],
            'name': [f'股票{i}' for i in range(100)],
            'industry': ['制造业'] * 50 + ['金融业'] * 50
        })
        
        with patch.object(data_manager, 'get_data', return_value=test_data):
            optimized_data = await data_manager.get_data_with_memory_optimization(request)
            
            # 检查数据类型优化
            assert optimized_data['industry'].dtype.name == 'category'
            assert len(optimized_data) == 100
    
    @pytest.mark.asyncio
    async def test_get_data_batch_memory_efficient(self, data_manager):
        """测试内存高效的批量数据获取"""
        requests = [
            DataRequest(data_type='stock_basic', extra_params={'limit': 10}),
            DataRequest(data_type='stock_basic', extra_params={'limit': 20}),
            DataRequest(data_type='stock_basic', extra_params={'limit': 15})
        ]
        
        # 模拟数据
        def mock_get_data_with_optimization(request):
            limit = request.extra_params.get('limit', 10)
            return pd.DataFrame({
                'ts_code': [f'00000{i}.SZ' for i in range(limit)],
                'name': [f'股票{i}' for i in range(limit)]
            })
        
        with patch.object(data_manager, 'get_data_with_memory_optimization', 
                         side_effect=mock_get_data_with_optimization):
            results = await data_manager.get_data_batch_memory_efficient(requests)
            
            assert len(results) == 3
            assert len(results[0]) == 10
            assert len(results[1]) == 20
            assert len(results[2]) == 15
    
    def test_optimize_memory_usage(self, data_manager):
        """测试内存使用优化"""
        stats = data_manager.optimize_memory_usage()
        
        assert hasattr(stats, 'process_memory_mb')
        assert hasattr(stats, 'memory_percent')
        assert stats.process_memory_mb >= 0
    
    def test_get_memory_stats(self, data_manager):
        """测试获取内存统计信息"""
        stats = data_manager.get_memory_stats()
        
        assert 'memory' in stats
        assert 'garbage_collection' in stats
        assert 'cache' in stats
        
        assert 'process_memory_mb' in stats['memory']
        assert 'system_memory_percent' in stats['memory']


class TestGlobalMemoryFunctions:
    """全局内存函数测试"""
    
    def test_get_memory_monitor(self):
        """测试获取全局内存监控器"""
        monitor1 = get_memory_monitor()
        monitor2 = get_memory_monitor()
        
        # 应该返回同一个实例
        assert monitor1 is monitor2
        assert isinstance(monitor1, MemoryMonitor)
    
    def test_get_gc_optimizer(self):
        """测试获取全局垃圾回收优化器"""
        optimizer1 = get_gc_optimizer()
        optimizer2 = get_gc_optimizer()
        
        # 应该返回同一个实例
        assert optimizer1 is optimizer2
        assert isinstance(optimizer1, GarbageCollectionOptimizer)


if __name__ == '__main__':
    pytest.main([__file__])