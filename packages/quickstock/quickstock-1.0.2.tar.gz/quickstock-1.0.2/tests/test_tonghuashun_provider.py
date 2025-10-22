"""
同花顺数据提供者测试
"""

import pytest
import pandas as pd
from unittest.mock import Mock, patch, AsyncMock
import asyncio

from quickstock.providers.tonghuashun import TonghuashunProvider
from quickstock.config import Config
from quickstock.core.errors import DataSourceError, NetworkError, ValidationError


class TestTonghuashunProvider:
    """同花顺数据提供者测试类"""
    
    @pytest.fixture
    def config(self):
        """创建测试配置"""
        return Config(
            request_timeout=30,
            max_retries=3
        )
    
    @pytest.fixture
    def provider(self, config):
        """创建同花顺提供者实例"""
        return TonghuashunProvider(config)
    
    def test_init(self, provider):
        """测试初始化"""
        assert provider.get_provider_name() == "tonghuashun"
        assert provider.base_url == "https://q.10jqka.com.cn"
        assert provider.data_url == "https://d.10jqka.com.cn"
        assert "User-Agent" in provider.headers
    
    def test_get_rate_limit(self, provider):
        """测试获取速率限制"""
        rate_limit = provider.get_rate_limit()
        assert rate_limit.requests_per_second == 2.0
        assert rate_limit.requests_per_minute == 100
        assert rate_limit.requests_per_hour == 5000
    
    def test_str_hash(self, provider):
        """测试字符串哈希函数"""
        user_agent = "Mozilla/5.0"
        hash_value = provider._str_hash(user_agent)
        assert isinstance(hash_value, int)
        assert hash_value > 0
    
    def test_time_now(self, provider):
        """测试时间函数"""
        time_value = provider._time_now()
        assert isinstance(time_value, int)
        assert time_value > 0
    
    def test_generate_tonghuashun_id(self, provider):
        """测试生成同花顺ID"""
        timestamp = 1234567890.0
        user_agent = "Mozilla/5.0"
        id_str = provider._generate_tonghuashun_id(timestamp, user_agent)
        assert isinstance(id_str, str)
        assert len(id_str) > 0
    
    @pytest.mark.asyncio
    async def test_make_request_success(self, provider):
        """测试成功的HTTP请求"""
        with patch.object(provider.session, 'get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.text = "test response"
            mock_get.return_value = mock_response
            
            result = await provider._make_request("http://test.com")
            assert result == "test response"
            mock_get.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_make_request_404(self, provider):
        """测试404错误"""
        with patch.object(provider.session, 'get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 404
            mock_get.return_value = mock_response
            
            with pytest.raises(DataSourceError, match="数据不存在"):
                await provider._make_request("http://test.com")
    
    @pytest.mark.asyncio
    async def test_make_request_network_error(self, provider):
        """测试网络错误"""
        with patch.object(provider.session, 'get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 500
            mock_get.return_value = mock_response
            
            with pytest.raises(NetworkError, match="请求失败"):
                await provider._make_request("http://test.com")
    
    @pytest.mark.asyncio
    async def test_get_concept_list_success(self, provider):
        """测试成功获取概念板块列表"""
        mock_html = '''
        <html>
            <div id="gnSection" value='{"1": {"platecode": "885333", "platename": "网络安全", "cid": "301558"}}'>
            </div>
        </html>
        '''
        
        with patch.object(provider, '_make_request', return_value=mock_html):
            result = await provider.get_concept_list()
            
            assert isinstance(result, pd.DataFrame)
            assert len(result) == 1
            assert result.iloc[0]['code'] == "885333"
            assert result.iloc[0]['name'] == "网络安全"
            assert result.iloc[0]['cid'] == "301558"
    
    @pytest.mark.asyncio
    async def test_get_concept_list_cache(self, provider):
        """测试概念板块列表缓存"""
        # 设置缓存
        provider._concept_cache = [{"code": "test", "name": "测试", "cid": "123"}]
        
        result = await provider.get_concept_list()
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1
        assert result.iloc[0]['code'] == "test"
    
    @pytest.mark.asyncio
    async def test_get_concept_list_no_data(self, provider):
        """测试获取概念板块列表无数据"""
        mock_html = '<html><div></div></html>'
        
        with patch.object(provider, '_make_request', return_value=mock_html):
            with pytest.raises(DataSourceError, match="无法找到概念板块数据"):
                await provider.get_concept_list()
    
    @pytest.mark.asyncio
    async def test_get_concept_stocks_success(self, provider):
        """测试成功获取概念板块成分股"""
        mock_html = '''
        <html>
            <table>
                <tr>
                    <td></td>
                    <td><a>000001</a></td>
                </tr>
                <tr>
                    <td></td>
                    <td><a>000002</a></td>
                </tr>
            </table>
        </html>
        '''
        
        with patch.object(provider, '_make_request', return_value=mock_html):
            result = await provider.get_concept_stocks("301558")
            
            assert isinstance(result, pd.DataFrame)
            assert len(result) == 2
            assert result.iloc[0]['code'] == "000001"
            assert result.iloc[0]['cid'] == "301558"
            assert result.iloc[1]['code'] == "000002"
    
    @pytest.mark.asyncio
    async def test_get_concept_stocks_cache(self, provider):
        """测试概念板块成分股缓存"""
        # 设置缓存
        provider._concept_stock_cache["301558"] = [{"code": "000001", "cid": "301558"}]
        
        result = await provider.get_concept_stocks("301558")
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1
        assert result.iloc[0]['code'] == "000001"
    
    @pytest.mark.asyncio
    async def test_abstract_methods_not_implemented(self, provider):
        """测试抽象方法未实现"""
        with pytest.raises(NotImplementedError):
            await provider.get_stock_basic()
        
        with pytest.raises(NotImplementedError):
            await provider.get_stock_daily("000001", "20240101", "20240131")
        
        with pytest.raises(NotImplementedError):
            await provider.get_trade_cal("20240101", "20240131")
    
    def test_is_available(self, provider):
        """测试可用性检查"""
        assert provider.is_available() is True
    
    @pytest.mark.asyncio
    async def test_health_check(self, provider):
        """测试健康检查"""
        result = await provider.health_check()
        assert result is True
    
    @pytest.mark.asyncio
    async def test_get_concept_basic(self, provider):
        """测试获取概念板块基础信息"""
        # Mock概念列表数据
        provider._concept_cache = [
            {"code": "885333", "name": "网络安全", "cid": "301558"},
            {"code": "885334", "name": "人工智能", "cid": "301559"}
        ]
        
        result = await provider.get_concept_basic()
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2
        assert "code" in result.columns
        assert "name" in result.columns
        assert "cid" in result.columns
    
    @pytest.mark.asyncio
    async def test_get_concept_basic_refresh(self, provider):
        """测试强制刷新概念板块基础信息"""
        # 设置初始缓存
        provider._concept_cache = [{"code": "old", "name": "旧数据", "cid": "old"}]
        
        mock_html = '''
        <html>
            <div id="gnSection" value='{"1": {"platecode": "885333", "platename": "网络安全", "cid": "301558"}}'>
            </div>
        </html>
        '''
        
        with patch.object(provider, '_make_request', return_value=mock_html):
            result = await provider.get_concept_basic(refresh=True)
            
            assert isinstance(result, pd.DataFrame)
            assert len(result) == 1
            assert result.iloc[0]['code'] == "885333"
    
    @pytest.mark.asyncio
    async def test_get_concept_constituent(self, provider):
        """测试获取概念板块成分股"""
        # Mock成分股数据
        provider._concept_stock_cache["301558"] = [
            {"code": "000001", "cid": "301558"},
            {"code": "000002", "cid": "301558"}
        ]
        
        result = await provider.get_concept_constituent("301558")
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2
        assert "code" in result.columns
        assert "cid" in result.columns
    
    @pytest.mark.asyncio
    async def test_search_concept_by_name(self, provider):
        """测试根据名称搜索概念板块"""
        # Mock概念列表数据
        provider._concept_cache = [
            {"code": "885333", "name": "网络安全", "cid": "301558"},
            {"code": "885334", "name": "人工智能", "cid": "301559"},
            {"code": "885335", "name": "网络游戏", "cid": "301560"}
        ]
        
        result = await provider.search_concept_by_name("网络")
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2  # 网络安全 和 网络游戏
        assert all("网络" in name for name in result['name'].values)
    
    @pytest.mark.asyncio
    async def test_search_concept_by_name_no_match(self, provider):
        """测试搜索不存在的概念名称"""
        provider._concept_cache = [
            {"code": "885333", "name": "网络安全", "cid": "301558"}
        ]
        
        result = await provider.search_concept_by_name("不存在的概念")
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0
    
    @pytest.mark.asyncio
    async def test_get_stock_concepts(self, provider):
        """测试获取股票所属概念板块"""
        # Mock概念列表
        provider._concept_cache = [
            {"code": "885333", "name": "网络安全", "cid": "301558"},
            {"code": "885334", "name": "人工智能", "cid": "301559"}
        ]
        
        # Mock成分股数据
        provider._concept_stock_cache["301558"] = [
            {"code": "000001", "cid": "301558"},
            {"code": "000002", "cid": "301558"}
        ]
        provider._concept_stock_cache["301559"] = [
            {"code": "000001", "cid": "301559"},
            {"code": "000003", "cid": "301559"}
        ]
        
        result = await provider.get_stock_concepts("000001")
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2  # 000001属于两个概念
        assert all(code == "000001" for code in result['stock_code'].values)
        assert "concept_code" in result.columns
        assert "concept_name" in result.columns
    
    @pytest.mark.asyncio
    async def test_get_stock_concepts_no_match(self, provider):
        """测试获取不存在股票的概念板块"""
        provider._concept_cache = [
            {"code": "885333", "name": "网络安全", "cid": "301558"}
        ]
        provider._concept_stock_cache["301558"] = [
            {"code": "000001", "cid": "301558"}
        ]
        
        result = await provider.get_stock_concepts("999999")
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0
    
    @pytest.mark.asyncio
    async def test_get_concept_stats(self, provider):
        """测试获取概念板块统计信息"""
        # Mock概念列表
        provider._concept_cache = [
            {"code": "885333", "name": "网络安全", "cid": "301558"}
        ]
        
        # Mock成分股数据
        provider._concept_stock_cache["301558"] = [
            {"code": "000001", "cid": "301558"},
            {"code": "000002", "cid": "301558"},
            {"code": "000003", "cid": "301558"}
        ]
        
        result = await provider.get_concept_stats("885333")
        assert isinstance(result, dict)
        assert result['concept_code'] == "885333"
        assert result['concept_name'] == "网络安全"
        assert result['concept_cid'] == "301558"
        assert result['stock_count'] == 3
        assert len(result['constituent_stocks']) == 3
        assert "000001" in result['constituent_stocks']
    
    @pytest.mark.asyncio
    async def test_get_concept_stats_not_found(self, provider):
        """测试获取不存在概念的统计信息"""
        provider._concept_cache = []
        
        with pytest.raises(DataSourceError, match="概念板块.*不存在"):
            await provider.get_concept_stats("999999")
    
    def test_compute_range(self, provider):
        """测试计算价格涨跌幅"""
        data = [
            {"date_at": "20240101", "start": 100.0, "end": 105.0, "max": 106.0, "min": 99.0},
            {"date_at": "20240102", "start": 105.0, "end": 110.0, "max": 112.0, "min": 104.0},
        ]
        
        result = provider._compute_range(data)
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2
        assert 'range_amount' in result.columns
        assert 'range' in result.columns
        assert 'amplitude' in result.columns
        
        # 检查第二行的计算结果
        assert result.iloc[1]['range_amount'] == 5.0  # 110 - 105
        assert abs(result.iloc[1]['range'] - 0.048) < 0.001  # 5/105 ≈ 0.048
    
    def test_parse_price_data(self, provider):
        """测试解析价格数据"""
        # Mock原始数据
        raw_data = '''{"bk_885943": {"data": "20240101,100.0,106.0,99.0,105.0,1000,50000.0,0,0,5.0;20240102,105.0,112.0,104.0,110.0,1200,60000.0,0,0,5.0"}}'''
        
        result = provider._parse_price_data(raw_data, "885943")
        assert isinstance(result, list)
        assert len(result) == 2
        
        # 检查第一条数据
        first_item = result[0]
        assert first_item['date_at'] == "20240101"
        assert first_item['start'] == 100.0
        assert first_item['end'] == 105.0
        assert first_item['max'] == 106.0
        assert first_item['min'] == 99.0
        assert first_item['count'] == 1000
        assert first_item['amount'] == 50000.0
    
    def test_parse_price_data_invalid_json(self, provider):
        """测试解析无效JSON数据"""
        raw_data = "invalid json"
        
        with pytest.raises(DataSourceError, match="解析价格数据JSON失败"):
            provider._parse_price_data(raw_data, "885943")
    
    def test_parse_price_data_empty(self, provider):
        """测试解析空数据"""
        raw_data = '{"bk_885943": {"data": ""}}'
        
        result = provider._parse_price_data(raw_data, "885943")
        assert isinstance(result, list)
        assert len(result) == 0
    
    @pytest.mark.asyncio
    async def test_get_concept_minute_data_success(self, provider):
        """测试成功获取概念分钟数据"""
        mock_data = '''{"bk_885943": {"data": "20240101,100.0,106.0,99.0,105.0,1000,50000.0,0,0,5.0"}}'''
        
        with patch.object(provider, '_make_request', return_value=mock_data):
            result = await provider.get_concept_minute_data("885943", "1min")
            
            assert isinstance(result, pd.DataFrame)
            assert not result.empty
            assert 'date_at' in result.columns
            assert 'start' in result.columns
            assert 'end' in result.columns
    
    @pytest.mark.asyncio
    async def test_get_concept_minute_data_invalid_freq(self, provider):
        """测试无效频率参数"""
        with pytest.raises(ValidationError, match="不支持的频率"):
            await provider.get_concept_minute_data("885943", "5min")
    
    @pytest.mark.asyncio
    async def test_get_concept_minute_data_cache(self, provider):
        """测试分钟数据缓存"""
        # 设置缓存
        cached_df = pd.DataFrame([{"date_at": "20240101", "start": 100.0}])
        provider._price_cache["885943_1min"] = cached_df
        
        result = await provider.get_concept_minute_data("885943", "1min")
        assert result is cached_df
    
    @pytest.mark.asyncio
    async def test_get_concept_daily_data_success(self, provider):
        """测试成功获取概念日线数据"""
        mock_data = '''{"bk_885943": {"data": "20240101,100.0,106.0,99.0,105.0,1000,50000.0,0,0,5.0;20240102,105.0,112.0,104.0,110.0,1200,60000.0,0,0,5.0"}}'''
        
        with patch.object(provider, '_make_request', return_value=mock_data):
            result = await provider.get_concept_daily_data("885943")
            
            assert isinstance(result, pd.DataFrame)
            assert not result.empty
            # 由于会获取多年数据，所以数据量会比较大，这里只检查不为空即可
            assert len(result) >= 2
    
    @pytest.mark.asyncio
    async def test_get_concept_daily_data_with_date_filter(self, provider):
        """测试带日期过滤的日线数据获取"""
        # Mock缓存数据
        cached_df = pd.DataFrame([
            {"date_at": "20240101", "start": 100.0, "end": 105.0},
            {"date_at": "20240102", "start": 105.0, "end": 110.0},
            {"date_at": "20240103", "start": 110.0, "end": 115.0}
        ])
        provider._price_cache["885943_daily"] = cached_df
        
        result = await provider.get_concept_daily_data("885943", "20240102", "20240102")
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1
        assert result.iloc[0]['date_at'] == "20240102"
    
    @pytest.mark.asyncio
    async def test_get_concept_daily_data_invalid_date(self, provider):
        """测试无效日期格式"""
        # ValidationError可能来自不同的模块，所以使用Exception基类
        with pytest.raises(Exception, match="无效的日期格式"):
            await provider.get_concept_daily_data("885943", "invalid_date")
    
    @pytest.mark.asyncio
    async def test_get_concept_weekly_data_success(self, provider):
        """测试成功获取概念周线数据"""
        mock_data = '''{"bk_885943": {"data": "20240101,100.0,106.0,99.0,105.0,1000,50000.0,0,0,5.0"}}'''
        
        with patch.object(provider, '_make_request', return_value=mock_data):
            result = await provider.get_concept_weekly_data("885943")
            
            assert isinstance(result, pd.DataFrame)
            assert not result.empty
    
    @pytest.mark.asyncio
    async def test_get_concept_monthly_data_success(self, provider):
        """测试成功获取概念月线数据"""
        mock_data = '''{"bk_885943": {"data": "20240101,100.0,106.0,99.0,105.0,1000,50000.0,0,0,5.0"}}'''
        
        with patch.object(provider, '_make_request', return_value=mock_data):
            result = await provider.get_concept_monthly_data("885943")
            
            assert isinstance(result, pd.DataFrame)
            assert not result.empty


if __name__ == "__main__":
    pytest.main([__file__])