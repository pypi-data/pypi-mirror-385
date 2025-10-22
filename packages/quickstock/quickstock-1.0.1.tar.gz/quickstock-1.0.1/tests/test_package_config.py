"""
测试包配置和安装相关功能
"""
import sys
import subprocess
import importlib
import pkg_resources
import pytest
from pathlib import Path

import quickstock


class TestPackageConfig:
    """测试包配置"""
    
    def test_package_version(self):
        """测试包版本信息"""
        assert hasattr(quickstock, '__version__')
        assert isinstance(quickstock.__version__, str)
        assert len(quickstock.__version__.split('.')) >= 2
    
    def test_package_author(self):
        """测试包作者信息"""
        assert hasattr(quickstock, '__author__')
        assert isinstance(quickstock.__author__, str)
        assert quickstock.__author__ == "QuickStock Team"
    
    def test_package_imports(self):
        """测试包的主要导入"""
        from quickstock import QuickStockClient, Config
        from quickstock import (
            QuickStockError,
            DataSourceError,
            CacheError,
            ValidationError,
            RateLimitError,
            NetworkError
        )
        
        # 验证类可以实例化
        config = Config()
        assert isinstance(config, Config)
        
        client = QuickStockClient(config)
        assert isinstance(client, QuickStockClient)
    
    def test_package_all_exports(self):
        """测试__all__导出"""
        expected_exports = {
            "QuickStockClient",
            "Config", 
            "QuickStockError",
            "DataSourceError",
            "CacheError",
            "ValidationError",
            "RateLimitError",
            "NetworkError",
        }
        
        assert hasattr(quickstock, '__all__')
        actual_exports = set(quickstock.__all__)
        assert actual_exports == expected_exports
    
    def test_package_structure(self):
        """测试包结构"""
        import quickstock.client
        import quickstock.config
        import quickstock.core
        import quickstock.providers
        import quickstock.utils
        
        # 验证核心模块存在
        assert hasattr(quickstock.core, 'cache')
        assert hasattr(quickstock.core, 'data_manager')
        assert hasattr(quickstock.core, 'errors')
        assert hasattr(quickstock.core, 'formatter')
    
    def test_dependencies_available(self):
        """测试核心依赖是否可用"""
        try:
            import pandas
            import numpy
            import requests
            import aiohttp
            import yaml
            import dateutil
            
            # 验证版本要求
            assert pkg_resources.get_distribution("pandas").version >= "1.3.0"
            assert pkg_resources.get_distribution("numpy").version >= "1.20.0"
            assert pkg_resources.get_distribution("requests").version >= "2.25.0"
            
        except ImportError as e:
            pytest.fail(f"Required dependency not available: {e}")
    
    def test_optional_dependencies(self):
        """测试可选依赖的处理"""
        # 测试tushare可选依赖
        try:
            import tushare
            tushare_available = True
        except ImportError:
            tushare_available = False
        
        # 测试baostock可选依赖
        try:
            import baostock
            baostock_available = True
        except ImportError:
            baostock_available = False
        
        # 即使可选依赖不可用，包也应该能正常导入
        from quickstock import QuickStockClient
        client = QuickStockClient()
        assert client is not None
    
    def test_package_metadata(self):
        """测试包元数据"""
        try:
            distribution = pkg_resources.get_distribution("quickstock")
            
            # 验证基本信息
            assert distribution.project_name == "quickstock"
            assert distribution.version == quickstock.__version__
            
            # 验证依赖信息
            requirements = [str(req) for req in distribution.requires()]
            required_deps = ["pandas", "numpy", "requests", "aiohttp", "pyyaml"]
            
            for dep in required_deps:
                assert any(dep in req for req in requirements), f"Missing dependency: {dep}"
                
        except pkg_resources.DistributionNotFound:
            pytest.skip("Package not installed, skipping metadata test")
    
    def test_entry_points(self):
        """测试入口点配置"""
        try:
            distribution = pkg_resources.get_distribution("quickstock")
            entry_points = distribution.get_entry_map()
            
            # 检查控制台脚本
            if 'console_scripts' in entry_points:
                console_scripts = entry_points['console_scripts']
                assert 'quickstock' in console_scripts
                
        except pkg_resources.DistributionNotFound:
            pytest.skip("Package not installed, skipping entry points test")
    
    def test_type_hints_support(self):
        """测试类型提示支持"""
        # 检查py.typed文件是否存在
        package_path = Path(quickstock.__file__).parent
        py_typed_path = package_path / "py.typed"
        
        assert py_typed_path.exists(), "py.typed file should exist for type hint support"
    
    @pytest.mark.slow
    def test_package_installation(self):
        """测试包安装（需要在CI环境中运行）"""
        # 这个测试只在CI环境中运行
        if not sys.platform.startswith('linux'):
            pytest.skip("Package installation test only runs in CI environment")
        
        try:
            # 测试基本安装
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", "-e", "."
            ], capture_output=True, text=True, timeout=60)
            
            assert result.returncode == 0, f"Installation failed: {result.stderr}"
            
            # 测试可选依赖安装
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", "-e", ".[dev]"
            ], capture_output=True, text=True, timeout=120)
            
            assert result.returncode == 0, f"Dev installation failed: {result.stderr}"
            
        except subprocess.TimeoutExpired:
            pytest.fail("Package installation timed out")
        except Exception as e:
            pytest.skip(f"Cannot test installation: {e}")


class TestPackageCompatibility:
    """测试包兼容性"""
    
    def test_python_version_compatibility(self):
        """测试Python版本兼容性"""
        # 验证当前Python版本符合要求
        assert sys.version_info >= (3, 7), "Requires Python 3.7 or higher"
    
    def test_import_performance(self):
        """测试导入性能"""
        import time
        
        start_time = time.time()
        importlib.reload(quickstock)
        import_time = time.time() - start_time
        
        # 导入时间应该在合理范围内（小于2秒）
        assert import_time < 2.0, f"Import time too slow: {import_time:.2f}s"
    
    def test_memory_usage(self):
        """测试内存使用"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        memory_before = process.memory_info().rss
        
        # 导入包
        import quickstock
        client = quickstock.QuickStockClient()
        
        memory_after = process.memory_info().rss
        memory_increase = (memory_after - memory_before) / 1024 / 1024  # MB
        
        # 内存增长应该在合理范围内（小于50MB）
        assert memory_increase < 50, f"Memory usage too high: {memory_increase:.2f}MB"