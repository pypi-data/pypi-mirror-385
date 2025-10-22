"""
集成测试 - 验证各组件协作
"""

import pytest
from quickstock import QuickStockClient, Config
from quickstock.models import DataRequest
from quickstock.providers.base import RateLimit


@pytest.mark.integration
class TestBasicIntegration:
    """基本集成测试"""
    
    def test_client_initialization(self):
        """测试客户端初始化"""
        # 使用默认配置
        client1 = QuickStockClient()
        assert client1.config is not None
        assert client1.data_manager is not None
        
        # 使用自定义配置
        config = Config(cache_enabled=False)
        client2 = QuickStockClient(config)
        assert client2.config.cache_enabled is False
    
    def test_config_and_models_integration(self):
        """测试配置和模型的集成"""
        config = Config(
            tushare_token="test_token",
            cache_expire_hours=48
        )
        
        # 创建数据请求
        request = DataRequest(
            data_type='stock_basic',
            start_date='20230101',
            end_date='20231231'
        )
        
        # 验证请求
        assert request.validate() is True
        
        # 生成缓存键
        cache_key = request.to_cache_key()
        assert len(cache_key) == 32
        
        print(f"Integration test passed - Config: {config}, Request cache key: {cache_key[:8]}...")
    
    def test_provider_interface_integration(self):
        """测试提供者接口集成"""
        from quickstock.providers.base import DataProvider
        import pandas as pd
        
        class TestProvider(DataProvider):
            async def get_stock_basic(self, **kwargs) -> pd.DataFrame:
                return pd.DataFrame({'ts_code': ['000001.SZ'], 'name': ['测试股票']})
            
            async def get_stock_daily(self, ts_code: str, start_date: str, 
                                     end_date: str) -> pd.DataFrame:
                return pd.DataFrame({
                    'ts_code': [ts_code],
                    'trade_date': [start_date],
                    'close': [10.0]
                })
            
            async def get_trade_cal(self, start_date: str, end_date: str) -> pd.DataFrame:
                return pd.DataFrame({
                    'cal_date': [start_date],
                    'is_open': [1]
                })
        
        config = Config()
        provider = TestProvider(config)
        
        assert provider.get_provider_name() == 'test'
        assert provider.is_available() is True
        assert isinstance(provider.get_rate_limit(), RateLimit)
    
    def test_error_handling_integration(self):
        """测试错误处理集成"""
        from quickstock.core.errors import ValidationError, QuickStockError
        
        # 测试配置验证错误
        with pytest.raises(ValidationError):
            Config(cache_expire_hours=-1)
        
        # 测试请求验证错误
        request = DataRequest(data_type='')
        with pytest.raises(ValidationError):
            request.validate()
        
        # 测试异常层次结构
        error = ValidationError("测试错误", error_code="TEST001")
        assert isinstance(error, QuickStockError)
        assert error.message == "测试错误"
        assert error.error_code == "TEST001"
    
    def test_full_workflow_simulation(self):
        """测试完整工作流程模拟"""
        # 1. 创建配置
        config = Config(
            cache_enabled=True,
            cache_expire_hours=24,
            tushare_token="test_token"
        )
        
        # 2. 创建客户端
        client = QuickStockClient(config)
        
        # 3. 创建数据请求
        request = DataRequest(
            data_type='stock_basic',
            fields=['ts_code', 'name', 'industry']
        )
        
        # 4. 验证请求
        assert request.validate() is True
        
        # 5. 生成缓存键
        cache_key = request.to_cache_key()
        
        # 6. 验证组件存在
        assert hasattr(client, 'data_manager')
        assert hasattr(client.data_manager, 'cache_layer')
        assert hasattr(client.data_manager, 'source_manager')
        assert hasattr(client.data_manager, 'formatter')
        assert hasattr(client.data_manager, 'error_handler')
        
        print(f"Full workflow simulation passed - Cache key: {cache_key[:8]}...")


if __name__ == "__main__":
    # 运行基本测试
    test = TestBasicIntegration()
    test.test_client_initialization()
    test.test_config_and_models_integration()
    test.test_provider_interface_integration()
    test.test_error_handling_integration()
    test.test_full_workflow_simulation()
    print("All integration tests passed!")