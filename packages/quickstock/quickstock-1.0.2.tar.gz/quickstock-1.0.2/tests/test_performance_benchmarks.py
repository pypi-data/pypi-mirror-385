"""
性能基准测试套件
"""

import pytest
import pandas as pd
import time
import asyncio
import psutil
import os
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from typing import List, Dict, Any

from quickstock import QuickStockClient, Config
from quickstock.models import DataRequest


class PerformanceBenchmark:
    """性能基准测试基类"""
    
    def __init__(self):
        self.results = {}
        self.process = psutil.Process(os.getpid())
    
    def measure_time(self, func, *args, **kwargs):
        """测量函数执行时间"""
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        return result, end_time - start_time
    
    def measure_memory(self):
        """测量当前内存使用"""
        return self.process.memory_info().rss / 1024 / 1024  # MB
    
    def record_benchmark(self, test_name: str, metrics: Dict[str, Any]):
        """记录基准测试结果"""
        self.results[test_name] = {
            'timestamp': datetime.now().isoformat(),
            **metrics
        }
    
    def print_results(self):
        """打印基准测试结果"""
        print("\n" + "="*60)
        print("PERFORMANCE BENCHMARK RESULTS")
        print("="*60)
        
        for test_name, metrics in self.results.items():
            print(f"\n{test_name}:")
            for key, value in metrics.items():
                if key != 'timestamp':
                    if isinstance(value, float):
                        if 'time' in key.lower():
                            print(f"  {key}: {value:.4f}s")
                        elif 'memory' in key.lower():
                            print(f"  {key}: {value:.2f}MB")
                        else:
                            print(f"  {key}: {value:.4f}")
                    else:
                        print(f"  {key}: {value}")


class TestDataRetrievalBenchmarks(PerformanceBenchmark):
    """数据获取性能基准测试"""
    
    @pytest.fixture
    def benchmark_client(self):
        """基准测试客户端"""
        config = Config(
            cache_enabled=True,
            memory_cache_size=10000,
            cache_expire_hours=24,
            request_timeout=30
        )
        return QuickStockClient(config)
    
    def test_stock_basic_performance(self, benchmark_client):
        """股票基础信息获取性能测试"""
        # 创建不同大小的测试数据集
        datasets = {
            'small': self._create_stock_data(100),
            'medium': self._create_stock_data(1000),
            'large': self._create_stock_data(5000)
        }
        
        for size, data in datasets.items():
            with patch.object(benchmark_client.data_manager.source_manager, 'fetch_data') as mock_fetch:
                mock_fetch.return_value = data
                
                initial_memory = self.measure_memory()
                
                # 测量执行时间
                result, execution_time = self.measure_time(
                    benchmark_client.stock_basic
                )
                
                final_memory = self.measure_memory()
                memory_usage = final_memory - initial_memory
                
                # 记录基准
                self.record_benchmark(f'stock_basic_{size}', {
                    'dataset_size': len(data),
                    'execution_time': execution_time,
                    'memory_usage': memory_usage,
                    'rows_per_second': len(data) / execution_time if execution_time > 0 else 0,
                    'memory_per_row': memory_usage / len(data) if len(data) > 0 else 0
                })
                
                # 验证结果
                assert len(result) == len(data)
                assert not result.empty
    
    def test_stock_daily_performance(self, benchmark_client):
        """股票日线数据获取性能测试"""
        # 创建不同时间跨度的数据
        time_spans = {
            '1_month': self._create_daily_data('000001.SZ', 30),
            '3_months': self._create_daily_data('000001.SZ', 90),
            '1_year': self._create_daily_data('000001.SZ', 365)
        }
        
        for span, data in time_spans.items():
            with patch.object(benchmark_client.data_manager.source_manager, 'fetch_data') as mock_fetch:
                mock_fetch.return_value = data
                
                initial_memory = self.measure_memory()
                
                result, execution_time = self.measure_time(
                    benchmark_client.stock_daily,
                    ts_code='000001.SZ',
                    start_date='20230101',
                    end_date='20231231'
                )
                
                final_memory = self.measure_memory()
                memory_usage = final_memory - initial_memory
                
                self.record_benchmark(f'stock_daily_{span}', {
                    'dataset_size': len(data),
                    'execution_time': execution_time,
                    'memory_usage': memory_usage,
                    'rows_per_second': len(data) / execution_time if execution_time > 0 else 0
                })
                
                assert len(result) == len(data)
    
    def test_concurrent_requests_performance(self, benchmark_client):
        """并发请求性能测试"""
        async def concurrent_benchmark():
            mock_data = self._create_stock_data(100)
            
            with patch.object(benchmark_client.data_manager.source_manager, 'fetch_data') as mock_fetch:
                mock_fetch.return_value = mock_data
                
                # 测试不同并发级别
                concurrency_levels = [1, 5, 10, 20]
                
                for level in concurrency_levels:
                    initial_memory = self.measure_memory()
                    start_time = time.perf_counter()
                    
                    # 创建并发任务
                    tasks = []
                    for i in range(level):
                        task = asyncio.create_task(
                            benchmark_client.data_manager.get_data(
                                DataRequest(
                                    data_type='stock_basic',
                                    extra_params={'batch': i}
                                )
                            )
                        )
                        tasks.append(task)
                    
                    # 等待所有任务完成
                    results = await asyncio.gather(*tasks)
                    
                    end_time = time.perf_counter()
                    final_memory = self.measure_memory()
                    
                    execution_time = end_time - start_time
                    memory_usage = final_memory - initial_memory
                    
                    self.record_benchmark(f'concurrent_requests_{level}', {
                        'concurrency_level': level,
                        'total_requests': level,
                        'execution_time': execution_time,
                        'memory_usage': memory_usage,
                        'requests_per_second': level / execution_time if execution_time > 0 else 0,
                        'avg_response_time': execution_time / level if level > 0 else 0
                    })
                    
                    # 验证所有请求都成功
                    assert len(results) == level
                    for result in results:
                        assert not result.empty
        
        asyncio.run(concurrent_benchmark())
    
    def _create_stock_data(self, size: int) -> pd.DataFrame:
        """创建测试用股票数据"""
        return pd.DataFrame({
            'ts_code': [f'{i:06d}.SZ' for i in range(size)],
            'name': [f'股票{i}' for i in range(size)],
            'area': ['深圳'] * size,
            'industry': ['制造业'] * size,
            'market': ['主板'] * size,
            'list_date': ['20100101'] * size,
            'is_hs': ['S'] * size
        })
    
    def _create_daily_data(self, ts_code: str, days: int) -> pd.DataFrame:
        """创建测试用日线数据"""
        dates = pd.date_range('2023-01-01', periods=days, freq='D')
        return pd.DataFrame({
            'ts_code': [ts_code] * days,
            'trade_date': [d.strftime('%Y%m%d') for d in dates],
            'open': [10.0 + i * 0.01 for i in range(days)],
            'high': [10.5 + i * 0.01 for i in range(days)],
            'low': [9.5 + i * 0.01 for i in range(days)],
            'close': [10.2 + i * 0.01 for i in range(days)],
            'volume': [1000000 + i * 1000 for i in range(days)],
            'amount': [10000000 + i * 10000 for i in range(days)]
        })


class TestCacheBenchmarks(PerformanceBenchmark):
    """缓存性能基准测试"""
    
    @pytest.fixture
    def cache_client(self):
        """缓存测试客户端"""
        config = Config(
            cache_enabled=True,
            memory_cache_size=5000,
            cache_expire_hours=1
        )
        return QuickStockClient(config)
    
    def test_cache_write_performance(self, cache_client):
        """缓存写入性能测试"""
        datasets = {
            'small': self._create_test_data(100),
            'medium': self._create_test_data(1000),
            'large': self._create_test_data(5000)
        }
        
        for size, data in datasets.items():
            cache_layer = cache_client.data_manager.cache_layer
            
            initial_memory = self.measure_memory()
            
            # 测量缓存写入时间
            start_time = time.perf_counter()
            
            for i in range(10):  # 写入10次
                key = f"test_key_{size}_{i}"
                asyncio.run(cache_layer.set(key, data))
            
            end_time = time.perf_counter()
            final_memory = self.measure_memory()
            
            execution_time = end_time - start_time
            memory_usage = final_memory - initial_memory
            
            self.record_benchmark(f'cache_write_{size}', {
                'dataset_size': len(data),
                'write_operations': 10,
                'execution_time': execution_time,
                'memory_usage': memory_usage,
                'writes_per_second': 10 / execution_time if execution_time > 0 else 0,
                'avg_write_time': execution_time / 10
            })
    
    def test_cache_read_performance(self, cache_client):
        """缓存读取性能测试"""
        cache_layer = cache_client.data_manager.cache_layer
        test_data = self._create_test_data(1000)
        
        # 预先写入缓存
        asyncio.run(cache_layer.set("benchmark_key", test_data))
        
        initial_memory = self.measure_memory()
        
        # 测量缓存读取时间
        start_time = time.perf_counter()
        
        for i in range(100):  # 读取100次
            result = asyncio.run(cache_layer.get("benchmark_key"))
            assert result is not None
        
        end_time = time.perf_counter()
        final_memory = self.measure_memory()
        
        execution_time = end_time - start_time
        memory_usage = final_memory - initial_memory
        
        self.record_benchmark('cache_read_performance', {
            'read_operations': 100,
            'execution_time': execution_time,
            'memory_usage': memory_usage,
            'reads_per_second': 100 / execution_time if execution_time > 0 else 0,
            'avg_read_time': execution_time / 100
        })
    
    def test_cache_hit_ratio_performance(self, cache_client):
        """缓存命中率性能测试"""
        mock_data = self._create_test_data(500)
        
        with patch.object(cache_client.data_manager.source_manager, 'fetch_data') as mock_fetch:
            mock_fetch.return_value = mock_data
            
            # 执行多次相同请求
            cache_hits = 0
            total_requests = 50
            
            start_time = time.perf_counter()
            
            for i in range(total_requests):
                result = cache_client.stock_basic()
                assert not result.empty
                
                # 第一次之后都应该是缓存命中
                if i > 0:
                    cache_hits += 1
            
            end_time = time.perf_counter()
            
            execution_time = end_time - start_time
            hit_ratio = cache_hits / (total_requests - 1) if total_requests > 1 else 0
            
            self.record_benchmark('cache_hit_ratio', {
                'total_requests': total_requests,
                'cache_hits': cache_hits,
                'hit_ratio': hit_ratio,
                'execution_time': execution_time,
                'avg_request_time': execution_time / total_requests,
                'data_source_calls': mock_fetch.call_count
            })
            
            # 验证缓存效果
            assert mock_fetch.call_count == 1  # 只调用一次数据源
            assert hit_ratio > 0.9  # 命中率应该大于90%
    
    def _create_test_data(self, size: int) -> pd.DataFrame:
        """创建测试数据"""
        return pd.DataFrame({
            'id': range(size),
            'value': [i * 1.5 for i in range(size)],
            'text': [f'text_{i}' for i in range(size)]
        })


class TestMemoryBenchmarks(PerformanceBenchmark):
    """内存使用基准测试"""
    
    def test_memory_scaling(self):
        """内存扩展性测试"""
        config = Config(cache_enabled=True, memory_cache_size=10000)
        client = QuickStockClient(config)
        
        data_sizes = [100, 500, 1000, 2000, 5000]
        
        for size in data_sizes:
            # 创建测试数据
            test_data = pd.DataFrame({
                'ts_code': [f'{i:06d}.SZ' for i in range(size)],
                'close': [10.0 + i * 0.01 for i in range(size)],
                'volume': [1000000 + i * 1000 for i in range(size)]
            })
            
            with patch.object(client.data_manager.source_manager, 'fetch_data') as mock_fetch:
                mock_fetch.return_value = test_data
                
                initial_memory = self.measure_memory()
                
                # 执行数据获取
                result = client.stock_daily(
                    ts_code='000001.SZ',
                    start_date='20230101',
                    end_date='20231231'
                )
                
                final_memory = self.measure_memory()
                memory_usage = final_memory - initial_memory
                
                self.record_benchmark(f'memory_scaling_{size}', {
                    'dataset_size': size,
                    'memory_usage': memory_usage,
                    'memory_per_row': memory_usage / size if size > 0 else 0,
                    'result_size': len(result)
                })
                
                assert len(result) == size
    
    def test_memory_leak_detection(self):
        """内存泄漏检测测试"""
        config = Config(cache_enabled=True)
        client = QuickStockClient(config)
        
        test_data = pd.DataFrame({
            'ts_code': ['000001.SZ'] * 100,
            'close': [10.0] * 100
        })
        
        with patch.object(client.data_manager.source_manager, 'fetch_data') as mock_fetch:
            mock_fetch.return_value = test_data
            
            initial_memory = self.measure_memory()
            memory_readings = [initial_memory]
            
            # 执行多次操作
            for i in range(20):
                result = client.stock_daily(
                    ts_code=f'{i:06d}.SZ',
                    start_date='20230101',
                    end_date='20230110'
                )
                
                current_memory = self.measure_memory()
                memory_readings.append(current_memory)
                
                assert not result.empty
            
            final_memory = self.measure_memory()
            total_increase = final_memory - initial_memory
            
            # 计算内存增长趋势
            memory_growth_rate = (final_memory - initial_memory) / len(memory_readings)
            
            self.record_benchmark('memory_leak_detection', {
                'initial_memory': initial_memory,
                'final_memory': final_memory,
                'total_increase': total_increase,
                'operations': 20,
                'memory_growth_rate': memory_growth_rate,
                'max_memory': max(memory_readings),
                'min_memory': min(memory_readings)
            })
            
            # 内存增长应该是合理的（小于50MB）
            assert total_increase < 50, f"Memory increased by {total_increase:.2f}MB"


@pytest.fixture(scope="session", autouse=True)
def print_benchmark_results():
    """在测试会话结束时打印所有基准测试结果"""
    yield
    
    # 收集所有基准测试实例的结果
    all_results = {}
    
    # 这里可以添加结果收集逻辑
    # 由于pytest的限制，我们在每个测试类中单独打印结果
    
    print("\n" + "="*60)
    print("BENCHMARK TESTS COMPLETED")
    print("="*60)


if __name__ == "__main__":
    # 运行基准测试
    benchmark = PerformanceBenchmark()
    
    # 可以在这里添加直接运行的基准测试
    print("Running performance benchmarks...")
    
    pytest.main([__file__, "-v", "-s"])