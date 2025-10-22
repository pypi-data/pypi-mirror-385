"""
端到端测试套件 - 测试完整的用户场景
"""

import pytest
import pandas as pd
import asyncio
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

from quickstock import QuickStockClient, Config
from quickstock.models import DataRequest
from quickstock.core.errors import QuickStockError, DataSourceError


class TestEndToEndScenarios:
    """端到端场景测试"""
    
    @pytest.fixture
    def client(self):
        """创建测试客户端"""
        config = Config(
            cache_enabled=True,
            cache_expire_hours=1,
            enable_baostock=True,
            enable_eastmoney=True,
            enable_tonghuashun=True
        )
        return QuickStockClient(config)
    
    @pytest.fixture
    def mock_stock_data(self):
        """模拟股票数据"""
        return pd.DataFrame({
            'ts_code': ['000001.SZ', '000002.SZ', '600000.SH'],
            'name': ['平安银行', '万科A', '浦发银行'],
            'area': ['深圳', '深圳', '上海'],
            'industry': ['银行', '房地产', '银行'],
            'market': ['主板', '主板', '主板'],
            'list_date': ['19910403', '19910129', '19990810'],
            'is_hs': ['S', 'S', 'S']
        })
    
    @pytest.fixture
    def mock_daily_data(self):
        """模拟日线数据"""
        dates = pd.date_range('2023-01-01', '2023-01-10', freq='D')
        return pd.DataFrame({
            'ts_code': ['000001.SZ'] * len(dates),
            'trade_date': [d.strftime('%Y%m%d') for d in dates],
            'open': [10.0 + i * 0.1 for i in range(len(dates))],
            'high': [10.5 + i * 0.1 for i in range(len(dates))],
            'low': [9.5 + i * 0.1 for i in range(len(dates))],
            'close': [10.2 + i * 0.1 for i in range(len(dates))],
            'volume': [1000000 + i * 10000 for i in range(len(dates))],
            'amount': [10000000 + i * 100000 for i in range(len(dates))]
        })
    
    def test_complete_stock_analysis_workflow(self, client, mock_stock_data, mock_daily_data):
        """测试完整的股票分析工作流程"""
        with patch.object(client.data_manager.source_manager, 'fetch_data') as mock_fetch:
            # 模拟数据获取
            mock_fetch.side_effect = [mock_stock_data, mock_daily_data]
            
            # 1. 获取股票列表
            stocks = client.stock_basic()
            assert not stocks.empty
            assert 'ts_code' in stocks.columns
            assert len(stocks) == 3
            
            # 2. 选择一只股票获取历史数据
            stock_code = stocks.iloc[0]['ts_code']
            daily_data = client.stock_daily(
                ts_code=stock_code,
                start_date='20230101',
                end_date='20230110'
            )
            
            assert not daily_data.empty
            assert 'close' in daily_data.columns
            assert len(daily_data) == 10
            
            # 3. 验证数据完整性
            assert daily_data['ts_code'].iloc[0] == stock_code
            assert daily_data['close'].dtype == float
            assert daily_data['volume'].dtype == int
    
    def test_multi_data_source_fallback(self, client):
        """测试多数据源fallback机制"""
        with patch.object(client.data_manager.source_manager, 'providers') as mock_providers:
            # 模拟第一个数据源失败
            mock_provider1 = MagicMock()
            mock_provider1.get_stock_basic.side_effect = DataSourceError("Provider 1 failed")
            
            # 模拟第二个数据源成功
            mock_provider2 = MagicMock()
            mock_provider2.get_stock_basic.return_value = pd.DataFrame({
                'ts_code': ['000001.SZ'],
                'name': ['测试股票']
            })
            
            mock_providers.values.return_value = [mock_provider1, mock_provider2]
            
            # 应该成功获取数据（通过fallback）
            result = client.stock_basic()
            assert not result.empty
            assert result.iloc[0]['ts_code'] == '000001.SZ'
    
    def test_cache_performance_scenario(self, client, mock_stock_data):
        """测试缓存性能场景"""
        with patch.object(client.data_manager.source_manager, 'fetch_data') as mock_fetch:
            mock_fetch.return_value = mock_stock_data
            
            # 第一次请求 - 应该从数据源获取
            start_time = datetime.now()
            result1 = client.stock_basic()
            first_request_time = (datetime.now() - start_time).total_seconds()
            
            # 第二次请求 - 应该从缓存获取
            start_time = datetime.now()
            result2 = client.stock_basic()
            second_request_time = (datetime.now() - start_time).total_seconds()
            
            # 验证结果一致
            pd.testing.assert_frame_equal(result1, result2)
            
            # 缓存请求应该更快（至少快50%）
            assert second_request_time < first_request_time * 0.5
            
            # 验证只调用了一次数据源
            assert mock_fetch.call_count == 1
    
    def test_error_recovery_scenario(self, client):
        """测试错误恢复场景"""
        with patch.object(client.data_manager.source_manager, 'fetch_data') as mock_fetch:
            # 模拟网络错误，然后恢复
            mock_fetch.side_effect = [
                DataSourceError("Network error"),
                DataSourceError("Timeout"),
                pd.DataFrame({'ts_code': ['000001.SZ'], 'name': ['测试股票']})
            ]
            
            # 应该在重试后成功
            result = client.stock_basic()
            assert not result.empty
            assert result.iloc[0]['ts_code'] == '000001.SZ'
            
            # 验证重试了3次
            assert mock_fetch.call_count == 3
    
    def test_concurrent_requests_scenario(self, client):
        """测试并发请求场景"""
        async def concurrent_test():
            with patch.object(client.data_manager.source_manager, 'fetch_data') as mock_fetch:
                # 模拟不同的数据返回
                mock_fetch.side_effect = [
                    pd.DataFrame({'ts_code': ['000001.SZ'], 'name': ['股票1']}),
                    pd.DataFrame({'ts_code': ['000002.SZ'], 'name': ['股票2']}),
                    pd.DataFrame({'ts_code': ['000003.SZ'], 'name': ['股票3']})
                ]
                
                # 并发请求
                tasks = [
                    asyncio.create_task(client.data_manager.get_data(
                        DataRequest(data_type='stock_basic', extra_params={'code': f'00000{i}.SZ'})
                    )) for i in range(1, 4)
                ]
                
                results = await asyncio.gather(*tasks)
                
                # 验证所有请求都成功
                assert len(results) == 3
                for result in results:
                    assert not result.empty
                    assert 'ts_code' in result.columns
        
        # 运行异步测试
        asyncio.run(concurrent_test())
    
    def test_data_validation_and_formatting(self, client):
        """测试数据验证和格式化"""
        # 模拟格式不一致的原始数据
        raw_data = pd.DataFrame({
            'code': ['000001.SZ'],  # 不标准的列名
            'stock_name': ['平安银行'],  # 不标准的列名
            'list_dt': ['1991-04-03'],  # 不标准的日期格式
            'close_price': ['10.50']  # 字符串格式的价格
        })
        
        with patch.object(client.data_manager.source_manager, 'fetch_data') as mock_fetch:
            mock_fetch.return_value = raw_data
            
            # 获取数据
            result = client.stock_basic()
            
            # 验证数据已被标准化
            assert 'ts_code' in result.columns
            assert 'name' in result.columns
            assert 'list_date' in result.columns
            
            # 验证数据类型
            if 'close' in result.columns:
                assert result['close'].dtype == float
    
    def test_large_dataset_handling(self, client):
        """测试大数据集处理"""
        # 创建大数据集（模拟1000只股票）
        large_dataset = pd.DataFrame({
            'ts_code': [f'{i:06d}.SZ' for i in range(1, 1001)],
            'name': [f'股票{i}' for i in range(1, 1001)],
            'industry': ['制造业'] * 1000,
            'list_date': ['20100101'] * 1000
        })
        
        with patch.object(client.data_manager.source_manager, 'fetch_data') as mock_fetch:
            mock_fetch.return_value = large_dataset
            
            start_time = datetime.now()
            result = client.stock_basic()
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # 验证数据完整性
            assert len(result) == 1000
            assert not result.empty
            
            # 验证处理时间合理（应该在5秒内完成）
            assert processing_time < 5.0
    
    def test_trade_calendar_integration(self, client):
        """测试交易日历集成"""
        mock_calendar = pd.DataFrame({
            'cal_date': ['20230101', '20230102', '20230103'],
            'is_open': [0, 1, 1]  # 元旦不开市，2号3号开市
        })
        
        with patch.object(client.data_manager.source_manager, 'fetch_data') as mock_fetch:
            mock_fetch.return_value = mock_calendar
            
            # 获取交易日历
            calendar = client.trade_cal(start_date='20230101', end_date='20230103')
            assert len(calendar) == 3
            
            # 测试交易日判断
            assert client.is_trade_date('20230101') is False
            assert client.is_trade_date('20230102') is True
            assert client.is_trade_date('20230103') is True


class TestPerformanceScenarios:
    """性能测试场景"""
    
    @pytest.fixture
    def performance_client(self):
        """性能测试客户端"""
        config = Config(
            cache_enabled=True,
            memory_cache_size=10000,
            cache_expire_hours=24
        )
        return QuickStockClient(config)
    
    def test_memory_usage_under_load(self, performance_client):
        """测试负载下的内存使用"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # 模拟大量数据请求
        large_datasets = []
        for i in range(10):
            dataset = pd.DataFrame({
                'ts_code': [f'{j:06d}.SZ' for j in range(i*100, (i+1)*100)],
                'close': [10.0 + j * 0.01 for j in range(100)],
                'volume': [1000000 + j * 1000 for j in range(100)]
            })
            large_datasets.append(dataset)
        
        with patch.object(performance_client.data_manager.source_manager, 'fetch_data') as mock_fetch:
            mock_fetch.side_effect = large_datasets
            
            # 执行多次请求
            for i in range(10):
                result = performance_client.stock_daily(
                    ts_code=f'{i:06d}.SZ',
                    start_date='20230101',
                    end_date='20231231'
                )
                assert not result.empty
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # 内存增长应该控制在合理范围内（小于100MB）
        assert memory_increase < 100, f"Memory increased by {memory_increase:.2f}MB"
    
    def test_cache_hit_ratio(self, performance_client):
        """测试缓存命中率"""
        mock_data = pd.DataFrame({
            'ts_code': ['000001.SZ'],
            'close': [10.0],
            'volume': [1000000]
        })
        
        with patch.object(performance_client.data_manager.source_manager, 'fetch_data') as mock_fetch:
            mock_fetch.return_value = mock_data
            
            # 执行多次相同请求
            for _ in range(10):
                result = performance_client.stock_daily(
                    ts_code='000001.SZ',
                    start_date='20230101',
                    end_date='20230110'
                )
                assert not result.empty
            
            # 应该只调用一次数据源（其余都是缓存命中）
            assert mock_fetch.call_count == 1
    
    def test_concurrent_performance(self, performance_client):
        """测试并发性能"""
        async def performance_test():
            mock_data = pd.DataFrame({
                'ts_code': ['000001.SZ'],
                'close': [10.0],
                'volume': [1000000]
            })
            
            with patch.object(performance_client.data_manager.source_manager, 'fetch_data') as mock_fetch:
                mock_fetch.return_value = mock_data
                
                start_time = datetime.now()
                
                # 并发执行20个请求
                tasks = []
                for i in range(20):
                    task = asyncio.create_task(
                        performance_client.data_manager.get_data(
                            DataRequest(
                                data_type='stock_daily',
                                ts_code=f'{i:06d}.SZ',
                                start_date='20230101',
                                end_date='20230110'
                            )
                        )
                    )
                    tasks.append(task)
                
                results = await asyncio.gather(*tasks)
                
                total_time = (datetime.now() - start_time).total_seconds()
                
                # 验证所有请求都成功
                assert len(results) == 20
                for result in results:
                    assert not result.empty
                
                # 并发执行应该比串行快（假设串行需要20秒，并发应该在5秒内）
                assert total_time < 5.0, f"Concurrent requests took {total_time:.2f}s"
        
        asyncio.run(performance_test())


if __name__ == "__main__":
    pytest.main([__file__, "-v"])