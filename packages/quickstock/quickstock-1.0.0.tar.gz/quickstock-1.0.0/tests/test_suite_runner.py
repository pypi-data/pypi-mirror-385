"""
测试套件运行器 - 统一管理和运行所有测试
"""

import pytest
import sys
import os
import time
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
import subprocess
import coverage


class TestSuiteRunner:
    """测试套件运行器"""
    
    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.test_dir = self.project_root / "tests"
        self.results = {}
        self.coverage_data = {}
        
    def run_unit_tests(self, verbose: bool = True) -> Dict[str, Any]:
        """运行单元测试"""
        print("Running Unit Tests...")
        start_time = time.time()
        
        # 单元测试文件模式
        unit_test_patterns = [
            "test_config.py",
            "test_models.py", 
            "test_cache.py",
            "test_errors.py",
            "test_formatter.py",
            "test_validators.py",
            "test_data_manager.py",
            "test_providers.py",
            "test_baostock_provider.py",
            "test_eastmoney_provider.py",
            "test_tonghuashun_provider.py"
        ]
        
        args = ["-v"] if verbose else []
        args.extend([str(self.test_dir / pattern) for pattern in unit_test_patterns])
        
        result = pytest.main(args)
        
        execution_time = time.time() - start_time
        
        unit_results = {
            'status': 'passed' if result == 0 else 'failed',
            'execution_time': execution_time,
            'exit_code': result,
            'test_count': len(unit_test_patterns)
        }
        
        self.results['unit_tests'] = unit_results
        return unit_results
    
    def run_integration_tests(self, verbose: bool = True) -> Dict[str, Any]:
        """运行集成测试"""
        print("Running Integration Tests...")
        start_time = time.time()
        
        integration_test_patterns = [
            "test_integration.py",
            "test_client_integration.py",
            "test_data_source_coordination.py",
            "test_data_source_manager.py"
        ]
        
        args = ["-v"] if verbose else []
        args.extend([str(self.test_dir / pattern) for pattern in integration_test_patterns])
        
        result = pytest.main(args)
        
        execution_time = time.time() - start_time
        
        integration_results = {
            'status': 'passed' if result == 0 else 'failed',
            'execution_time': execution_time,
            'exit_code': result,
            'test_count': len(integration_test_patterns)
        }
        
        self.results['integration_tests'] = integration_results
        return integration_results
    
    def run_end_to_end_tests(self, verbose: bool = True) -> Dict[str, Any]:
        """运行端到端测试"""
        print("Running End-to-End Tests...")
        start_time = time.time()
        
        e2e_test_patterns = [
            "test_end_to_end.py",
            "test_client.py"
        ]
        
        args = ["-v"] if verbose else []
        args.extend([str(self.test_dir / pattern) for pattern in e2e_test_patterns])
        
        result = pytest.main(args)
        
        execution_time = time.time() - start_time
        
        e2e_results = {
            'status': 'passed' if result == 0 else 'failed',
            'execution_time': execution_time,
            'exit_code': result,
            'test_count': len(e2e_test_patterns)
        }
        
        self.results['end_to_end_tests'] = e2e_results
        return e2e_results
    
    def run_performance_tests(self, verbose: bool = True) -> Dict[str, Any]:
        """运行性能测试"""
        print("Running Performance Tests...")
        start_time = time.time()
        
        performance_test_patterns = [
            "test_performance_benchmarks.py",
            "test_memory_optimization.py",
            "test_concurrency_features.py"
        ]
        
        args = ["-v", "-s"]  # -s 显示print输出
        if verbose:
            args.append("--tb=short")
        
        args.extend([str(self.test_dir / pattern) for pattern in performance_test_patterns])
        
        result = pytest.main(args)
        
        execution_time = time.time() - start_time
        
        performance_results = {
            'status': 'passed' if result == 0 else 'failed',
            'execution_time': execution_time,
            'exit_code': result,
            'test_count': len(performance_test_patterns)
        }
        
        self.results['performance_tests'] = performance_results
        return performance_results
    
    def run_coverage_analysis(self) -> Dict[str, Any]:
        """运行代码覆盖率分析"""
        print("Running Coverage Analysis...")
        
        try:
            # 初始化coverage
            cov = coverage.Coverage(
                source=['quickstock'],
                omit=[
                    '*/tests/*',
                    '*/test_*',
                    '*/__pycache__/*',
                    '*/venv/*',
                    '*/env/*'
                ]
            )
            
            cov.start()
            
            # 运行所有测试（除了性能测试）
            test_patterns = [
                "test_config.py",
                "test_models.py",
                "test_cache.py",
                "test_errors.py",
                "test_formatter.py",
                "test_validators.py",
                "test_integration.py",
                "test_client.py"
            ]
            
            args = ["-q"]  # 安静模式
            args.extend([str(self.test_dir / pattern) for pattern in test_patterns])
            
            pytest.main(args)
            
            cov.stop()
            cov.save()
            
            # 生成覆盖率报告
            coverage_report = {}
            
            # 获取覆盖率数据
            total_lines = 0
            covered_lines = 0
            
            for filename in cov.get_data().measured_files():
                if 'quickstock' in filename and 'test' not in filename:
                    analysis = cov.analysis2(filename)
                    file_total = len(analysis[1]) + len(analysis[2])
                    file_covered = len(analysis[1])
                    
                    total_lines += file_total
                    covered_lines += file_covered
                    
                    coverage_report[filename] = {
                        'total_lines': file_total,
                        'covered_lines': file_covered,
                        'coverage_percent': (file_covered / file_total * 100) if file_total > 0 else 0
                    }
            
            overall_coverage = (covered_lines / total_lines * 100) if total_lines > 0 else 0
            
            coverage_results = {
                'overall_coverage': overall_coverage,
                'total_lines': total_lines,
                'covered_lines': covered_lines,
                'file_coverage': coverage_report,
                'status': 'passed' if overall_coverage >= 80 else 'warning'
            }
            
            self.coverage_data = coverage_results
            return coverage_results
            
        except Exception as e:
            print(f"Coverage analysis failed: {e}")
            return {
                'status': 'failed',
                'error': str(e),
                'overall_coverage': 0
            }
    
    def run_all_tests(self, include_performance: bool = False, 
                     include_coverage: bool = True) -> Dict[str, Any]:
        """运行所有测试"""
        print("="*60)
        print("QUICKSTOCK SDK - COMPREHENSIVE TEST SUITE")
        print("="*60)
        
        start_time = time.time()
        
        # 运行各类测试
        self.run_unit_tests()
        self.run_integration_tests()
        self.run_end_to_end_tests()
        
        if include_performance:
            self.run_performance_tests()
        
        if include_coverage:
            self.run_coverage_analysis()
        
        total_time = time.time() - start_time
        
        # 汇总结果
        summary = self._generate_summary(total_time)
        self.results['summary'] = summary
        
        # 打印结果
        self._print_results()
        
        # 保存结果
        self._save_results()
        
        return self.results
    
    def _generate_summary(self, total_time: float) -> Dict[str, Any]:
        """生成测试摘要"""
        total_tests = 0
        passed_tests = 0
        failed_tests = 0
        
        for test_type, result in self.results.items():
            if test_type != 'summary' and 'test_count' in result:
                total_tests += result['test_count']
                if result['status'] == 'passed':
                    passed_tests += result['test_count']
                else:
                    failed_tests += result['test_count']
        
        return {
            'total_execution_time': total_time,
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': failed_tests,
            'success_rate': (passed_tests / total_tests * 100) if total_tests > 0 else 0,
            'overall_status': 'passed' if failed_tests == 0 else 'failed',
            'timestamp': datetime.now().isoformat()
        }
    
    def _print_results(self):
        """打印测试结果"""
        print("\n" + "="*60)
        print("TEST RESULTS SUMMARY")
        print("="*60)
        
        for test_type, result in self.results.items():
            if test_type == 'summary':
                continue
                
            status_symbol = "✓" if result['status'] == 'passed' else "✗"
            print(f"{status_symbol} {test_type.replace('_', ' ').title()}: {result['status'].upper()}")
            print(f"   Execution Time: {result['execution_time']:.2f}s")
            
            if 'test_count' in result:
                print(f"   Test Count: {result['test_count']}")
        
        # 覆盖率信息
        if self.coverage_data:
            print(f"\n📊 Code Coverage: {self.coverage_data['overall_coverage']:.1f}%")
            print(f"   Lines Covered: {self.coverage_data['covered_lines']}/{self.coverage_data['total_lines']}")
        
        # 总体摘要
        if 'summary' in self.results:
            summary = self.results['summary']
            print(f"\n🎯 Overall Results:")
            print(f"   Total Tests: {summary['total_tests']}")
            print(f"   Passed: {summary['passed_tests']}")
            print(f"   Failed: {summary['failed_tests']}")
            print(f"   Success Rate: {summary['success_rate']:.1f}%")
            print(f"   Total Time: {summary['total_execution_time']:.2f}s")
            
            if summary['overall_status'] == 'passed':
                print("\n🎉 ALL TESTS PASSED!")
            else:
                print("\n❌ SOME TESTS FAILED!")
        
        print("="*60)
    
    def _save_results(self):
        """保存测试结果到文件"""
        results_file = self.project_root / "test_results.json"
        
        try:
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, indent=2, ensure_ascii=False)
            print(f"\n📄 Test results saved to: {results_file}")
        except Exception as e:
            print(f"Failed to save results: {e}")
    
    def run_specific_test(self, test_pattern: str, verbose: bool = True) -> int:
        """运行特定测试"""
        print(f"Running specific test: {test_pattern}")
        
        args = ["-v"] if verbose else []
        args.append(str(self.test_dir / test_pattern))
        
        return pytest.main(args)
    
    def run_tests_by_marker(self, marker: str, verbose: bool = True) -> int:
        """根据标记运行测试"""
        print(f"Running tests with marker: {marker}")
        
        args = ["-v"] if verbose else []
        args.extend(["-m", marker])
        args.append(str(self.test_dir))
        
        return pytest.main(args)


class ContinuousIntegrationRunner:
    """持续集成运行器"""
    
    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.runner = TestSuiteRunner(project_root)
    
    def run_ci_pipeline(self) -> bool:
        """运行CI流水线"""
        print("Starting CI Pipeline...")
        
        # 1. 代码质量检查
        if not self._run_code_quality_checks():
            print("❌ Code quality checks failed")
            return False
        
        # 2. 运行测试套件
        results = self.runner.run_all_tests(
            include_performance=False,  # CI中跳过性能测试
            include_coverage=True
        )
        
        # 3. 检查结果
        if results['summary']['overall_status'] != 'passed':
            print("❌ Test suite failed")
            return False
        
        # 4. 检查覆盖率
        if 'overall_coverage' in self.runner.coverage_data:
            coverage = self.runner.coverage_data['overall_coverage']
            if coverage < 80:
                print(f"❌ Coverage too low: {coverage:.1f}% (minimum: 80%)")
                return False
        
        print("✅ CI Pipeline passed!")
        return True
    
    def _run_code_quality_checks(self) -> bool:
        """运行代码质量检查"""
        print("Running code quality checks...")
        
        # 检查Python语法
        try:
            result = subprocess.run([
                sys.executable, '-m', 'py_compile', 
                str(self.project_root / 'quickstock')
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"Syntax check failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"Failed to run syntax check: {e}")
            return False
        
        print("✅ Code quality checks passed")
        return True
    
    def generate_ci_config(self):
        """生成CI配置文件"""
        # GitHub Actions配置
        github_actions_config = """
name: QuickStock SDK Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, '3.10', '3.11']

    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v3
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-cov pytest-asyncio
    
    - name: Run tests
      run: |
        python -m pytest tests/ -v --cov=quickstock --cov-report=xml
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        flags: unittests
        name: codecov-umbrella
"""
        
        github_dir = self.project_root / ".github" / "workflows"
        github_dir.mkdir(parents=True, exist_ok=True)
        
        with open(github_dir / "tests.yml", 'w') as f:
            f.write(github_actions_config)
        
        print(f"✅ GitHub Actions config generated: {github_dir / 'tests.yml'}")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='QuickStock SDK Test Suite Runner')
    parser.add_argument('--type', choices=['unit', 'integration', 'e2e', 'performance', 'all'], 
                       default='all', help='Test type to run')
    parser.add_argument('--coverage', action='store_true', help='Include coverage analysis')
    parser.add_argument('--performance', action='store_true', help='Include performance tests')
    parser.add_argument('--ci', action='store_true', help='Run in CI mode')
    parser.add_argument('--generate-ci', action='store_true', help='Generate CI configuration')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--marker', '-m', help='Run tests with specific marker')
    parser.add_argument('--pattern', '-p', help='Run specific test pattern')
    
    args = parser.parse_args()
    
    if args.generate_ci:
        ci_runner = ContinuousIntegrationRunner()
        ci_runner.generate_ci_config()
        return
    
    runner = TestSuiteRunner()
    
    if args.ci:
        ci_runner = ContinuousIntegrationRunner()
        success = ci_runner.run_ci_pipeline()
        sys.exit(0 if success else 1)
    
    if args.pattern:
        result = runner.run_specific_test(args.pattern, args.verbose)
        sys.exit(result)
    
    if args.marker:
        result = runner.run_tests_by_marker(args.marker, args.verbose)
        sys.exit(result)
    
    if args.type == 'unit':
        runner.run_unit_tests(args.verbose)
    elif args.type == 'integration':
        runner.run_integration_tests(args.verbose)
    elif args.type == 'e2e':
        runner.run_end_to_end_tests(args.verbose)
    elif args.type == 'performance':
        runner.run_performance_tests(args.verbose)
    else:  # all
        runner.run_all_tests(
            include_performance=args.performance,
            include_coverage=args.coverage
        )


if __name__ == "__main__":
    main()