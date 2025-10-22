"""
股票代码转换工具

提供统一的股票代码格式转换功能，支持不同数据源之间的代码格式转换
"""

import re
import time
import threading
import logging
import concurrent.futures
from collections import OrderedDict
from typing import Dict, Optional, Tuple, List, Any, Union
from datetime import datetime
from functools import lru_cache
from ..core.errors import ValidationError


class CodeConversionError(ValidationError):
    """代码转换基础异常"""
    
    def __init__(self, message: str, code: str = None, suggestions: List[str] = None, 
                 error_code: str = None, details: Dict[str, Any] = None, 
                 recovery_actions: List[str] = None):
        """
        初始化代码转换异常
        
        Args:
            message: 错误消息
            code: 导致错误的股票代码
            suggestions: 修正建议列表
            error_code: 错误代码
            details: 错误详细信息
            recovery_actions: 恢复操作建议
        """
        super().__init__(message, error_code, details)
        self.code = code
        self.suggestions = suggestions or []
        self.recovery_actions = recovery_actions or []
        self.timestamp = datetime.now()
        self.context = {}
    
    def get_user_friendly_message(self) -> str:
        """
        获取用户友好的错误消息
        
        Returns:
            格式化的错误消息
        """
        msg = self.message
        
        if self.code:
            msg += f"\n输入代码: {self.code}"
        
        if self.suggestions:
            msg += "\n建议尝试:"
            for i, suggestion in enumerate(self.suggestions, 1):
                msg += f"\n  {i}. {suggestion}"
        
        if self.recovery_actions:
            msg += "\n恢复操作:"
            for i, action in enumerate(self.recovery_actions, 1):
                msg += f"\n  {i}. {action}"
        
        return msg
    
    def add_context(self, key: str, value: Any) -> None:
        """添加上下文信息"""
        self.context[key] = value
    
    def get_context(self) -> Dict[str, Any]:
        """获取上下文信息"""
        return self.context.copy()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'error_type': self.__class__.__name__,
            'message': self.message,
            'code': self.code,
            'error_code': self.error_code,
            'suggestions': self.suggestions,
            'recovery_actions': self.recovery_actions,
            'details': self.details,
            'context': self.context,
            'timestamp': self.timestamp.isoformat()
        }


class InvalidCodeFormatError(CodeConversionError):
    """无效的代码格式异常"""
    
    def __init__(self, code: str, supported_formats: List[str] = None, 
                 detected_issues: List[str] = None, format_analysis: Dict[str, Any] = None):
        """
        初始化无效格式异常
        
        Args:
            code: 无效的股票代码
            supported_formats: 支持的格式列表
            detected_issues: 检测到的问题列表
            format_analysis: 格式分析结果
        """
        self.supported_formats = supported_formats or []
        self.detected_issues = detected_issues or []
        self.format_analysis = format_analysis or {}
        
        # 生成详细的错误消息
        message = f"无效的股票代码格式: {code}"
        
        # 生成修正建议和恢复操作
        suggestions = self._generate_suggestions(code)
        recovery_actions = self._generate_recovery_actions(code)
        
        super().__init__(
            message, code, suggestions, "INVALID_CODE_FORMAT", 
            {'format_analysis': self.format_analysis}, recovery_actions
        )
    
    def _generate_suggestions(self, code: str) -> List[str]:
        """生成修正建议"""
        suggestions = []
        
        if self.detected_issues:
            suggestions.extend(self.detected_issues)
        
        # 基于格式分析提供具体建议
        if self.format_analysis:
            if self.format_analysis.get('has_digits') and self.format_analysis.get('digit_count') == 6:
                if not self.format_analysis.get('has_exchange'):
                    suggestions.append("代码包含6位数字但缺少交易所标识，请添加 .SH 或 .SZ")
            
            if self.format_analysis.get('has_invalid_chars'):
                invalid_chars = self.format_analysis.get('invalid_chars', [])
                suggestions.append(f"包含无效字符: {', '.join(invalid_chars)}")
        
        if self.supported_formats:
            suggestions.append("支持的格式包括:")
            for fmt in self.supported_formats:
                if fmt == 'standard':
                    suggestions.append("  - 标准格式: 000001.SZ, 600000.SH")
                elif fmt == 'baostock':
                    suggestions.append("  - Baostock格式: sz.000001, sh.600000")
                elif fmt == 'eastmoney':
                    suggestions.append("  - 东方财富格式: 0.000001, 1.600000")
                elif fmt == 'tonghuashun':
                    suggestions.append("  - 同花顺格式: hs_000001, hs_600000")
                elif fmt == 'pure_number':
                    suggestions.append("  - 纯数字格式: 000001, 600000")
        
        return suggestions
    
    def _generate_recovery_actions(self, code: str) -> List[str]:
        """生成恢复操作建议"""
        actions = []
        
        # 尝试自动修正
        if code and isinstance(code, str):
            code_clean = code.strip().upper()
            
            # 检查是否只是大小写问题
            if re.match(r'^[0-9]{6}\.(sh|sz)$', code.lower()):
                actions.append(f"尝试使用大写格式: {code_clean}")
            
            # 检查是否缺少交易所
            if re.match(r'^[0-9]{6}$', code_clean):
                actions.append("添加交易所后缀 (.SH 或 .SZ)")
                actions.append("或使用自动推断功能")
        
        actions.append("使用 validate_code() 方法检查代码格式")
        actions.append("查看文档了解支持的格式")
        
        return actions


class UnsupportedFormatError(CodeConversionError):
    """不支持的格式异常"""
    
    def __init__(self, format_name: str, supported_formats: List[str], 
                 similar_formats: List[str] = None):
        """
        初始化不支持格式异常
        
        Args:
            format_name: 不支持的格式名称
            supported_formats: 支持的格式列表
            similar_formats: 相似的格式列表
        """
        self.format_name = format_name
        self.supported_formats = supported_formats
        self.similar_formats = similar_formats or []
        
        message = f"不支持的目标格式: {format_name}"
        suggestions = self._generate_suggestions()
        recovery_actions = self._generate_recovery_actions()
        
        super().__init__(
            message, None, suggestions, "UNSUPPORTED_FORMAT",
            {'requested_format': format_name, 'similar_formats': self.similar_formats},
            recovery_actions
        )
    
    def _generate_suggestions(self) -> List[str]:
        """生成格式建议"""
        suggestions = []
        
        if self.similar_formats:
            suggestions.append("您可能想要使用:")
            suggestions.extend([f"  - {fmt}" for fmt in self.similar_formats])
        
        suggestions.append(f"支持的格式: {', '.join(self.supported_formats)}")
        return suggestions
    
    def _generate_recovery_actions(self) -> List[str]:
        """生成恢复操作"""
        actions = [
            "检查格式名称拼写",
            "使用 get_supported_formats() 查看所有支持的格式",
            "查看文档了解格式详情"
        ]
        
        if self.similar_formats:
            actions.insert(0, f"尝试使用相似格式: {self.similar_formats[0]}")
        
        return actions


class ExchangeInferenceError(CodeConversionError):
    """交易所推断失败异常"""
    
    def __init__(self, code: str, inference_details: Dict[str, Any] = None, 
                 possible_exchanges: List[str] = None):
        """
        初始化交易所推断异常
        
        Args:
            code: 无法推断交易所的股票代码
            inference_details: 推断过程的详细信息
            possible_exchanges: 可能的交易所列表
        """
        self.inference_details = inference_details or {}
        self.possible_exchanges = possible_exchanges or []
        
        message = f"无法推断股票代码 {code} 的交易所"
        
        # 生成建议和恢复操作
        suggestions = self._generate_exchange_suggestions(code)
        recovery_actions = self._generate_recovery_actions(code)
        
        super().__init__(
            message, code, suggestions, "EXCHANGE_INFERENCE_FAILED", 
            self.inference_details, recovery_actions
        )
    
    def _generate_exchange_suggestions(self, code: str) -> List[str]:
        """生成交易所推断建议"""
        suggestions = []
        
        if len(code) == 6 and code.isdigit():
            suggestions.append("请明确指定交易所:")
            suggestions.append(f"  - 上海证券交易所: {code}.SH")
            suggestions.append(f"  - 深圳证券交易所: {code}.SZ")
            
            # 基于代码规则提供更具体的建议
            if code.startswith('60') or code.startswith('68') or code.startswith('90'):
                suggestions.append(f"根据代码规则，{code} 可能属于上海证券交易所")
                self.possible_exchanges.append('SH')
            elif code.startswith('00') or code.startswith('30') or code.startswith('20'):
                suggestions.append(f"根据代码规则，{code} 可能属于深圳证券交易所")
                self.possible_exchanges.append('SZ')
            else:
                suggestions.append("代码不符合常见的交易所规则，请手动指定")
        else:
            suggestions.append("请使用标准格式: 000001.SZ 或 600000.SH")
        
        return suggestions
    
    def _generate_recovery_actions(self, code: str) -> List[str]:
        """生成恢复操作"""
        actions = []
        
        if self.possible_exchanges:
            actions.append(f"尝试使用推荐的交易所: {', '.join(self.possible_exchanges)}")
        
        actions.extend([
            "使用完整的股票代码格式 (代码.交易所)",
            "查询股票所属交易所信息",
            "使用数据源特定的格式"
        ])
        
        return actions


class BatchConversionError(CodeConversionError):
    """批量转换错误异常"""
    
    def __init__(self, failed_codes: List[Tuple[str, Exception]], 
                 successful_count: int, total_count: int):
        """
        初始化批量转换错误
        
        Args:
            failed_codes: 失败的代码和对应异常列表
            successful_count: 成功转换的数量
            total_count: 总数量
        """
        self.failed_codes = failed_codes
        self.successful_count = successful_count
        self.total_count = total_count
        self.failure_rate = len(failed_codes) / total_count if total_count > 0 else 0
        
        message = f"批量转换部分失败: {len(failed_codes)}/{total_count} 个代码转换失败"
        
        suggestions = self._generate_batch_suggestions()
        recovery_actions = self._generate_batch_recovery_actions()
        
        super().__init__(
            message, None, suggestions, "BATCH_CONVERSION_FAILED",
            {
                'failed_codes': [(code, str(exc)) for code, exc in failed_codes],
                'successful_count': successful_count,
                'total_count': total_count,
                'failure_rate': self.failure_rate
            },
            recovery_actions
        )
    
    def _generate_batch_suggestions(self) -> List[str]:
        """生成批量处理建议"""
        suggestions = []
        
        if self.failure_rate < 0.1:  # 失败率小于10%
            suggestions.append("大部分代码转换成功，只有少数失败")
        elif self.failure_rate < 0.5:  # 失败率小于50%
            suggestions.append("部分代码转换失败，建议检查失败的代码格式")
        else:
            suggestions.append("大量代码转换失败，建议检查输入数据格式")
        
        # 分析失败原因
        error_types = {}
        for _, exc in self.failed_codes:
            error_type = type(exc).__name__
            error_types[error_type] = error_types.get(error_type, 0) + 1
        
        if error_types:
            suggestions.append("主要错误类型:")
            for error_type, count in sorted(error_types.items(), key=lambda x: x[1], reverse=True):
                suggestions.append(f"  - {error_type}: {count} 次")
        
        return suggestions
    
    def _generate_batch_recovery_actions(self) -> List[str]:
        """生成批量恢复操作"""
        actions = [
            "检查失败的代码列表",
            "使用单个代码转换进行调试",
            "预处理输入数据以统一格式"
        ]
        
        if self.failure_rate > 0.5:
            actions.insert(0, "考虑使用不同的输入格式")
        
        return actions
    
    def get_failed_codes(self) -> List[str]:
        """获取失败的代码列表"""
        return [code for code, _ in self.failed_codes]
    
    def get_failure_summary(self) -> Dict[str, Any]:
        """获取失败摘要"""
        return {
            'total_failed': len(self.failed_codes),
            'total_successful': self.successful_count,
            'total_count': self.total_count,
            'failure_rate': self.failure_rate,
            'failed_codes': self.get_failed_codes()
        }


class ErrorHandlingStrategy:
    """错误处理策略类，处理各种代码转换错误场景"""
    
    def __init__(self, enable_auto_correction: bool = True, 
                 enable_fuzzy_matching: bool = True,
                 max_suggestions: int = 5):
        """
        初始化错误处理策略
        
        Args:
            enable_auto_correction: 是否启用自动修正
            enable_fuzzy_matching: 是否启用模糊匹配
            max_suggestions: 最大建议数量
        """
        self.enable_auto_correction = enable_auto_correction
        self.enable_fuzzy_matching = enable_fuzzy_matching
        self.max_suggestions = max_suggestions
        self.logger = logging.getLogger(__name__)
    
    def handle_invalid_format(self, code: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        处理无效格式错误
        
        Args:
            code: 无效的股票代码
            context: 错误上下文
            
        Returns:
            处理结果字典
        """
        context = context or {}
        result = {
            'original_code': code,
            'auto_corrections': [],
            'suggestions': [],
            'confidence_scores': {},
            'recommended_action': None
        }
        
        if not code or not isinstance(code, str):
            result['recommended_action'] = 'provide_valid_string'
            result['suggestions'] = ['请提供有效的股票代码字符串']
            return result
        
        code_clean = code.strip()
        
        # 尝试自动修正
        if self.enable_auto_correction:
            corrections = self._attempt_auto_corrections(code_clean)
            result['auto_corrections'] = corrections
            
            # 如果有高置信度的修正，推荐使用
            high_confidence = [c for c in corrections if c['confidence'] > 0.8]
            if high_confidence:
                result['recommended_action'] = 'use_auto_correction'
                result['suggestions'].insert(0, f"建议使用: {high_confidence[0]['corrected_code']}")
        
        # 生成格式建议
        format_suggestions = self._generate_format_suggestions(code_clean)
        result['suggestions'].extend(format_suggestions[:self.max_suggestions])
        
        # 模糊匹配
        if self.enable_fuzzy_matching:
            fuzzy_matches = self._find_fuzzy_matches(code_clean)
            if fuzzy_matches:
                result['suggestions'].append("可能的匹配:")
                result['suggestions'].extend([f"  - {match}" for match in fuzzy_matches[:3]])
        
        return result
    
    def handle_exchange_inference_failure(self, code: str, 
                                        context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        处理交易所推断失败
        
        Args:
            code: 股票代码
            context: 错误上下文
            
        Returns:
            处理结果字典
        """
        context = context or {}
        result = {
            'original_code': code,
            'possible_exchanges': [],
            'confidence_scores': {},
            'recommendations': [],
            'fallback_options': []
        }
        
        if len(code) == 6 and code.isdigit():
            # 基于代码规则推断可能的交易所
            exchange_analysis = self._analyze_exchange_patterns(code)
            result.update(exchange_analysis)
            
            # 生成具体建议
            if exchange_analysis['possible_exchanges']:
                for exchange in exchange_analysis['possible_exchanges']:
                    confidence = exchange_analysis['confidence_scores'].get(exchange, 0)
                    result['recommendations'].append({
                        'action': 'specify_exchange',
                        'suggested_code': f"{code}.{exchange}",
                        'confidence': confidence,
                        'reason': f"基于代码规则推断为{exchange}交易所"
                    })
            
            # 提供回退选项
            result['fallback_options'] = [
                f"手动指定: {code}.SH",
                f"手动指定: {code}.SZ",
                "查询股票信息确认交易所",
                "使用数据源特定格式"
            ]
        else:
            result['recommendations'] = [{
                'action': 'use_standard_format',
                'reason': '代码格式不符合6位数字规则',
                'suggested_format': '000001.SZ'
            }]
        
        return result
    
    def handle_batch_conversion_errors(self, failed_items: List[Tuple[str, Exception]], 
                                     successful_count: int, 
                                     context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        处理批量转换错误
        
        Args:
            failed_items: 失败的项目列表
            successful_count: 成功数量
            context: 错误上下文
            
        Returns:
            处理结果字典
        """
        context = context or {}
        total_count = len(failed_items) + successful_count
        failure_rate = len(failed_items) / total_count if total_count > 0 else 0
        
        result = {
            'failure_analysis': self._analyze_batch_failures(failed_items),
            'recovery_strategy': self._determine_recovery_strategy(failure_rate),
            'correctable_items': [],
            'uncorrectable_items': [],
            'recommendations': []
        }
        
        # 分析每个失败项目
        for code, exception in failed_items:
            if isinstance(exception, (InvalidCodeFormatError, ExchangeInferenceError)):
                # 尝试自动修正
                correction_result = self.handle_invalid_format(code)
                if correction_result['auto_corrections']:
                    result['correctable_items'].append({
                        'original_code': code,
                        'error': str(exception),
                        'corrections': correction_result['auto_corrections']
                    })
                else:
                    result['uncorrectable_items'].append({
                        'original_code': code,
                        'error': str(exception),
                        'suggestions': correction_result['suggestions']
                    })
            else:
                result['uncorrectable_items'].append({
                    'original_code': code,
                    'error': str(exception),
                    'suggestions': ['检查代码格式', '查看错误详情']
                })
        
        # 生成恢复建议
        result['recommendations'] = self._generate_batch_recovery_recommendations(
            result['failure_analysis'], failure_rate
        )
        
        return result
    
    def suggest_format_corrections(self, code: str, target_format: str = None) -> List[Dict[str, Any]]:
        """
        建议格式修正
        
        Args:
            code: 原始代码
            target_format: 目标格式
            
        Returns:
            修正建议列表
        """
        suggestions = []
        
        if not code or not isinstance(code, str):
            return [{'type': 'error', 'message': '请提供有效的股票代码字符串'}]
        
        code_clean = code.strip()
        
        # 基本格式检查和建议
        basic_suggestions = self._get_basic_format_suggestions(code_clean)
        suggestions.extend(basic_suggestions)
        
        # 如果指定了目标格式，提供特定建议
        if target_format:
            format_specific = self._get_format_specific_suggestions(code_clean, target_format)
            suggestions.extend(format_specific)
        
        # 自动修正建议
        if self.enable_auto_correction:
            auto_corrections = self._attempt_auto_corrections(code_clean)
            for correction in auto_corrections:
                suggestions.append({
                    'type': 'auto_correction',
                    'original': code_clean,
                    'corrected': correction['corrected_code'],
                    'confidence': correction['confidence'],
                    'reason': correction['reason']
                })
        
        return suggestions[:self.max_suggestions]
    
    def _attempt_auto_corrections(self, code: str) -> List[Dict[str, Any]]:
        """尝试自动修正代码"""
        corrections = []
        
        # 修正1: 大小写问题
        if re.match(r'^[0-9]{6}\.(sh|sz)$', code.lower()):
            corrections.append({
                'corrected_code': code.upper(),
                'confidence': 0.95,
                'reason': '修正大小写格式',
                'type': 'case_correction'
            })
        
        # 修正2: 缺少交易所后缀
        if re.match(r'^[0-9]{6}$', code):
            # 尝试推断交易所
            try:
                if code.startswith('60') or code.startswith('68') or code.startswith('90'):
                    corrections.append({
                        'corrected_code': f"{code}.SH",
                        'confidence': 0.85,
                        'reason': '基于代码规则推断为上海交易所',
                        'type': 'exchange_inference'
                    })
                elif code.startswith('00') or code.startswith('30') or code.startswith('20'):
                    corrections.append({
                        'corrected_code': f"{code}.SZ",
                        'confidence': 0.85,
                        'reason': '基于代码规则推断为深圳交易所',
                        'type': 'exchange_inference'
                    })
            except Exception:
                pass
        
        # 修正3: 反向格式 (SH000001 -> 000001.SH)
        match = re.match(r'^(SH|SZ)([0-9]{6})$', code.upper())
        if match:
            exchange, stock_code = match.groups()
            corrections.append({
                'corrected_code': f"{stock_code}.{exchange}",
                'confidence': 0.9,
                'reason': '修正交易所前缀格式',
                'type': 'format_correction'
            })
        
        # 修正4: 去除多余字符
        clean_code = re.sub(r'[^0-9A-Za-z.]', '', code)
        if clean_code != code and len(clean_code) >= 6:
            corrections.append({
                'corrected_code': clean_code,
                'confidence': 0.7,
                'reason': '去除无效字符',
                'type': 'character_cleanup'
            })
        
        return sorted(corrections, key=lambda x: x['confidence'], reverse=True)
    
    def _generate_format_suggestions(self, code: str) -> List[str]:
        """生成格式建议"""
        suggestions = []
        
        # 分析代码特征
        has_digits = bool(re.search(r'\d', code))
        has_letters = bool(re.search(r'[a-zA-Z]', code))
        has_dot = '.' in code
        length = len(code)
        
        if has_digits and length >= 6:
            digit_part = re.findall(r'\d+', code)
            if digit_part and len(digit_part[0]) == 6:
                suggestions.append(f"尝试标准格式: {digit_part[0]}.SH 或 {digit_part[0]}.SZ")
        
        if not has_dot and has_digits:
            suggestions.append("可能缺少交易所标识，尝试添加 .SH 或 .SZ")
        
        if length < 6:
            suggestions.append("代码长度不足，股票代码通常为6位数字")
        elif length > 15:
            suggestions.append("代码长度过长，请检查格式")
        
        return suggestions
    
    def _find_fuzzy_matches(self, code: str) -> List[str]:
        """查找模糊匹配"""
        matches = []
        
        # 提取数字部分
        digits = re.findall(r'\d+', code)
        if digits:
            main_digits = digits[0]
            if len(main_digits) == 6:
                matches.extend([
                    f"{main_digits}.SH",
                    f"{main_digits}.SZ",
                    f"sh.{main_digits}",
                    f"sz.{main_digits}"
                ])
        
        return matches
    
    def _analyze_exchange_patterns(self, code: str) -> Dict[str, Any]:
        """分析交易所模式"""
        result = {
            'possible_exchanges': [],
            'confidence_scores': {},
            'analysis_details': {}
        }
        
        if len(code) == 6 and code.isdigit():
            # 上海交易所规则
            if code.startswith('60') or code.startswith('68') or code.startswith('90'):
                result['possible_exchanges'].append('SH')
                result['confidence_scores']['SH'] = 0.9
                result['analysis_details']['SH'] = '符合上海交易所代码规则'
            
            # 深圳交易所规则
            if code.startswith('00') or code.startswith('30') or code.startswith('20'):
                result['possible_exchanges'].append('SZ')
                result['confidence_scores']['SZ'] = 0.9
                result['analysis_details']['SZ'] = '符合深圳交易所代码规则'
            
            # 如果都不匹配，降低置信度但仍提供选项
            if not result['possible_exchanges']:
                result['possible_exchanges'] = ['SH', 'SZ']
                result['confidence_scores'] = {'SH': 0.5, 'SZ': 0.5}
                result['analysis_details'] = {
                    'SH': '不确定，需要手动确认',
                    'SZ': '不确定，需要手动确认'
                }
        
        return result
    
    def _analyze_batch_failures(self, failed_items: List[Tuple[str, Exception]]) -> Dict[str, Any]:
        """分析批量失败情况"""
        analysis = {
            'error_types': {},
            'common_patterns': [],
            'correctable_count': 0,
            'total_failed': len(failed_items)
        }
        
        # 统计错误类型
        for code, exception in failed_items:
            error_type = type(exception).__name__
            analysis['error_types'][error_type] = analysis['error_types'].get(error_type, 0) + 1
            
            # 检查是否可修正
            if isinstance(exception, (InvalidCodeFormatError, ExchangeInferenceError)):
                analysis['correctable_count'] += 1
        
        # 分析常见模式
        codes = [code for code, _ in failed_items]
        analysis['common_patterns'] = self._find_common_error_patterns(codes)
        
        return analysis
    
    def _determine_recovery_strategy(self, failure_rate: float) -> str:
        """确定恢复策略"""
        if failure_rate < 0.1:
            return 'individual_correction'  # 个别修正
        elif failure_rate < 0.3:
            return 'batch_correction'  # 批量修正
        elif failure_rate < 0.7:
            return 'format_standardization'  # 格式标准化
        else:
            return 'data_validation'  # 数据验证
    
    def _generate_batch_recovery_recommendations(self, failure_analysis: Dict[str, Any], 
                                               failure_rate: float) -> List[Dict[str, Any]]:
        """生成批量恢复建议"""
        recommendations = []
        
        strategy = self._determine_recovery_strategy(failure_rate)
        
        if strategy == 'individual_correction':
            recommendations.append({
                'priority': 'high',
                'action': '逐个修正失败的代码',
                'description': '失败率较低，建议逐个检查和修正'
            })
        elif strategy == 'batch_correction':
            recommendations.append({
                'priority': 'high',
                'action': '使用批量修正工具',
                'description': '应用自动修正规则处理常见错误'
            })
        elif strategy == 'format_standardization':
            recommendations.append({
                'priority': 'high',
                'action': '标准化输入格式',
                'description': '预处理数据以统一格式'
            })
        else:
            recommendations.append({
                'priority': 'critical',
                'action': '验证输入数据质量',
                'description': '失败率过高，需要检查数据源'
            })
        
        # 基于错误类型添加具体建议
        if 'InvalidCodeFormatError' in failure_analysis['error_types']:
            recommendations.append({
                'priority': 'medium',
                'action': '检查代码格式规范',
                'description': '确保输入符合支持的格式'
            })
        
        if 'ExchangeInferenceError' in failure_analysis['error_types']:
            recommendations.append({
                'priority': 'medium',
                'action': '明确指定交易所',
                'description': '使用完整格式避免推断错误'
            })
        
        return recommendations
    
    def _get_basic_format_suggestions(self, code: str) -> List[Dict[str, Any]]:
        """获取基本格式建议"""
        suggestions = []
        
        # 长度检查
        if len(code) < 6:
            suggestions.append({
                'type': 'format_error',
                'message': '代码长度不足，需要至少6位数字'
            })
        elif len(code) > 20:
            suggestions.append({
                'type': 'format_error',
                'message': '代码长度过长，请检查格式'
            })
        
        # 字符检查
        if not re.search(r'\d', code):
            suggestions.append({
                'type': 'format_error',
                'message': '缺少数字部分，股票代码必须包含数字'
            })
        
        invalid_chars = re.findall(r'[^0-9A-Za-z._]', code)
        if invalid_chars:
            suggestions.append({
                'type': 'format_error',
                'message': f'包含无效字符: {", ".join(set(invalid_chars))}'
            })
        
        return suggestions
    
    def _get_format_specific_suggestions(self, code: str, target_format: str) -> List[Dict[str, Any]]:
        """获取特定格式建议"""
        suggestions = []
        
        format_examples = {
            'standard': '000001.SZ',
            'baostock': 'sz.000001',
            'eastmoney': '0.000001',
            'tonghuashun': 'hs_000001'
        }
        
        if target_format in format_examples:
            suggestions.append({
                'type': 'format_example',
                'message': f'{target_format}格式示例: {format_examples[target_format]}'
            })
        
        return suggestions
    
    def _find_common_error_patterns(self, codes: List[str]) -> List[str]:
        """查找常见错误模式"""
        patterns = []
        
        # 检查是否都缺少交易所
        missing_exchange = sum(1 for code in codes if re.match(r'^[0-9]{6}$', code))
        if missing_exchange > len(codes) * 0.5:
            patterns.append('大部分代码缺少交易所标识')
        
        # 检查是否都是大小写问题
        case_issues = sum(1 for code in codes if re.match(r'^[0-9]{6}\.(sh|sz)$', code.lower()))
        if case_issues > len(codes) * 0.5:
            patterns.append('大部分代码存在大小写问题')
        
        return patterns


class CodeConversionLogger:
    """代码转换日志记录器，记录转换过程和错误统计"""
    
    def __init__(self, logger_name: str = 'quickstock.code_converter', 
                 enable_performance_logging: bool = True,
                 enable_detailed_logging: bool = False):
        """
        初始化代码转换日志记录器
        
        Args:
            logger_name: 日志记录器名称
            enable_performance_logging: 是否启用性能日志
            enable_detailed_logging: 是否启用详细日志
        """
        self.logger = logging.getLogger(logger_name)
        self.enable_performance_logging = enable_performance_logging
        self.enable_detailed_logging = enable_detailed_logging
        
        # 统计信息
        self._stats = {
            'conversions': {
                'total': 0,
                'successful': 0,
                'failed': 0,
                'by_format': {},
                'by_error_type': {}
            },
            'performance': {
                'total_time': 0.0,
                'average_time': 0.0,
                'max_time': 0.0,
                'min_time': float('inf')
            },
            'cache': {
                'hits': 0,
                'misses': 0,
                'hit_rate': 0.0
            },
            'errors': {
                'recent_errors': [],
                'error_patterns': {},
                'recovery_attempts': 0,
                'recovery_successes': 0
            },
            'start_time': datetime.now()
        }
        
        # 性能监控
        self._performance_samples = []
        self._max_samples = 1000
    
    def log_conversion(self, original_code: str, converted_code: str, 
                      source_format: str, target_format: str,
                      execution_time: float = None, cached: bool = False,
                      context: Dict[str, Any] = None):
        """
        记录代码转换
        
        Args:
            original_code: 原始代码
            converted_code: 转换后代码
            source_format: 源格式
            target_format: 目标格式
            execution_time: 执行时间（秒）
            cached: 是否来自缓存
            context: 上下文信息
        """
        context = context or {}
        
        # 更新统计信息
        self._stats['conversions']['total'] += 1
        self._stats['conversions']['successful'] += 1
        
        # 按格式统计
        format_key = f"{source_format}->{target_format}"
        self._stats['conversions']['by_format'][format_key] = (
            self._stats['conversions']['by_format'].get(format_key, 0) + 1
        )
        
        # 缓存统计
        if cached:
            self._stats['cache']['hits'] += 1
        else:
            self._stats['cache']['misses'] += 1
        
        self._update_cache_hit_rate()
        
        # 性能统计
        if execution_time is not None:
            self._update_performance_stats(execution_time)
        
        # 详细日志
        if self.enable_detailed_logging:
            log_data = {
                'action': 'conversion_success',
                'original_code': original_code,
                'converted_code': converted_code,
                'source_format': source_format,
                'target_format': target_format,
                'cached': cached,
                'execution_time': execution_time,
                'context': context
            }
            self.logger.debug(f"代码转换成功: {log_data}")
        
        # 性能日志
        if self.enable_performance_logging and execution_time is not None:
            if execution_time > 0.01:  # 记录超过10ms的转换
                self.logger.info(
                    f"代码转换耗时较长: {original_code} -> {converted_code}, "
                    f"耗时: {execution_time:.3f}s, 格式: {format_key}"
                )
    
    def log_conversion_error(self, original_code: str, error: Exception,
                           source_format: str = None, target_format: str = None,
                           execution_time: float = None, context: Dict[str, Any] = None):
        """
        记录转换错误
        
        Args:
            original_code: 原始代码
            error: 异常对象
            source_format: 源格式
            target_format: 目标格式
            execution_time: 执行时间
            context: 上下文信息
        """
        context = context or {}
        
        # 更新统计信息
        self._stats['conversions']['total'] += 1
        self._stats['conversions']['failed'] += 1
        
        # 按错误类型统计
        error_type = type(error).__name__
        self._stats['conversions']['by_error_type'][error_type] = (
            self._stats['conversions']['by_error_type'].get(error_type, 0) + 1
        )
        
        # 记录最近错误
        error_record = {
            'timestamp': datetime.now(),
            'code': original_code,
            'error_type': error_type,
            'error_message': str(error),
            'source_format': source_format,
            'target_format': target_format,
            'context': context
        }
        
        self._stats['errors']['recent_errors'].append(error_record)
        
        # 保持最近错误列表大小
        if len(self._stats['errors']['recent_errors']) > 100:
            self._stats['errors']['recent_errors'] = self._stats['errors']['recent_errors'][-100:]
        
        # 分析错误模式
        self._analyze_error_pattern(original_code, error_type)
        
        # 记录日志
        log_data = {
            'action': 'conversion_error',
            'original_code': original_code,
            'error_type': error_type,
            'error_message': str(error),
            'source_format': source_format,
            'target_format': target_format,
            'execution_time': execution_time,
            'context': context
        }
        
        if isinstance(error, CodeConversionError):
            log_data.update({
                'error_code': error.error_code,
                'suggestions': error.suggestions,
                'recovery_actions': error.recovery_actions
            })
        
        self.logger.error(f"代码转换失败: {log_data}")
    
    def log_batch_conversion(self, total_count: int, successful_count: int, 
                           failed_count: int, execution_time: float,
                           context: Dict[str, Any] = None):
        """
        记录批量转换
        
        Args:
            total_count: 总数量
            successful_count: 成功数量
            failed_count: 失败数量
            execution_time: 执行时间
            context: 上下文信息
        """
        context = context or {}
        
        success_rate = successful_count / total_count if total_count > 0 else 0
        
        log_data = {
            'action': 'batch_conversion',
            'total_count': total_count,
            'successful_count': successful_count,
            'failed_count': failed_count,
            'success_rate': success_rate,
            'execution_time': execution_time,
            'throughput': total_count / execution_time if execution_time > 0 else 0,
            'context': context
        }
        
        if success_rate < 0.8:  # 成功率低于80%时记录警告
            self.logger.warning(f"批量转换成功率较低: {log_data}")
        else:
            self.logger.info(f"批量转换完成: {log_data}")
    
    def log_cache_operation(self, operation: str, key: str, hit: bool = None,
                          cache_size: int = None, context: Dict[str, Any] = None):
        """
        记录缓存操作
        
        Args:
            operation: 操作类型 (get, put, clear)
            key: 缓存键
            hit: 是否命中（仅对get操作有效）
            cache_size: 缓存大小
            context: 上下文信息
        """
        context = context or {}
        
        if self.enable_detailed_logging:
            log_data = {
                'action': f'cache_{operation}',
                'key': key,
                'hit': hit,
                'cache_size': cache_size,
                'context': context
            }
            self.logger.debug(f"缓存操作: {log_data}")
    
    def log_recovery_attempt(self, original_code: str, recovery_action: str,
                           success: bool, result_code: str = None,
                           context: Dict[str, Any] = None):
        """
        记录错误恢复尝试
        
        Args:
            original_code: 原始代码
            recovery_action: 恢复操作
            success: 是否成功
            result_code: 恢复后的代码
            context: 上下文信息
        """
        context = context or {}
        
        self._stats['errors']['recovery_attempts'] += 1
        if success:
            self._stats['errors']['recovery_successes'] += 1
        
        log_data = {
            'action': 'recovery_attempt',
            'original_code': original_code,
            'recovery_action': recovery_action,
            'success': success,
            'result_code': result_code,
            'context': context
        }
        
        if success:
            self.logger.info(f"错误恢复成功: {log_data}")
        else:
            self.logger.warning(f"错误恢复失败: {log_data}")
    
    def get_conversion_stats(self) -> Dict[str, Any]:
        """
        获取转换统计信息
        
        Returns:
            统计信息字典
        """
        stats = self._stats.copy()
        
        # 计算成功率
        total = stats['conversions']['total']
        if total > 0:
            stats['conversions']['success_rate'] = stats['conversions']['successful'] / total
            stats['conversions']['failure_rate'] = stats['conversions']['failed'] / total
        else:
            stats['conversions']['success_rate'] = 0.0
            stats['conversions']['failure_rate'] = 0.0
        
        # 计算恢复成功率
        recovery_attempts = stats['errors']['recovery_attempts']
        if recovery_attempts > 0:
            stats['errors']['recovery_success_rate'] = (
                stats['errors']['recovery_successes'] / recovery_attempts
            )
        else:
            stats['errors']['recovery_success_rate'] = 0.0
        
        # 运行时间
        stats['uptime'] = (datetime.now() - stats['start_time']).total_seconds()
        
        return stats
    
    def get_performance_report(self) -> Dict[str, Any]:
        """
        获取性能报告
        
        Returns:
            性能报告字典
        """
        stats = self._stats['performance'].copy()
        
        if self._performance_samples:
            # 计算百分位数
            sorted_samples = sorted(self._performance_samples)
            n = len(sorted_samples)
            
            stats.update({
                'p50': sorted_samples[int(n * 0.5)],
                'p90': sorted_samples[int(n * 0.9)],
                'p95': sorted_samples[int(n * 0.95)],
                'p99': sorted_samples[int(n * 0.99)],
                'sample_count': n
            })
        
        return stats
    
    def get_error_analysis(self) -> Dict[str, Any]:
        """
        获取错误分析报告
        
        Returns:
            错误分析字典
        """
        analysis = {
            'error_summary': self._stats['conversions']['by_error_type'].copy(),
            'error_patterns': self._stats['errors']['error_patterns'].copy(),
            'recent_errors': self._stats['errors']['recent_errors'][-10:],  # 最近10个错误
            'recovery_stats': {
                'attempts': self._stats['errors']['recovery_attempts'],
                'successes': self._stats['errors']['recovery_successes'],
                'success_rate': (
                    self._stats['errors']['recovery_successes'] / 
                    max(1, self._stats['errors']['recovery_attempts'])
                )
            }
        }
        
        # 分析错误趋势
        if len(self._stats['errors']['recent_errors']) >= 5:
            recent_error_types = [
                error['error_type'] for error in self._stats['errors']['recent_errors'][-10:]
            ]
            analysis['recent_error_trend'] = {
                error_type: recent_error_types.count(error_type)
                for error_type in set(recent_error_types)
            }
        
        return analysis
    
    def reset_stats(self):
        """重置统计信息"""
        self._stats = {
            'conversions': {
                'total': 0,
                'successful': 0,
                'failed': 0,
                'by_format': {},
                'by_error_type': {}
            },
            'performance': {
                'total_time': 0.0,
                'average_time': 0.0,
                'max_time': 0.0,
                'min_time': float('inf')
            },
            'cache': {
                'hits': 0,
                'misses': 0,
                'hit_rate': 0.0
            },
            'errors': {
                'recent_errors': [],
                'error_patterns': {},
                'recovery_attempts': 0,
                'recovery_successes': 0
            },
            'start_time': datetime.now()
        }
        self._performance_samples.clear()
    
    def export_logs(self, format_type: str = 'json') -> Union[str, Dict[str, Any]]:
        """
        导出日志数据
        
        Args:
            format_type: 导出格式 ('json', 'dict')
            
        Returns:
            导出的数据
        """
        data = {
            'stats': self.get_conversion_stats(),
            'performance': self.get_performance_report(),
            'error_analysis': self.get_error_analysis(),
            'export_time': datetime.now().isoformat()
        }
        
        if format_type == 'json':
            import json
            return json.dumps(data, indent=2, ensure_ascii=False)
        else:
            return data
    
    def _update_performance_stats(self, execution_time: float):
        """更新性能统计"""
        perf = self._stats['performance']
        
        perf['total_time'] += execution_time
        perf['max_time'] = max(perf['max_time'], execution_time)
        perf['min_time'] = min(perf['min_time'], execution_time)
        
        # 计算平均时间
        total_conversions = self._stats['conversions']['total']
        if total_conversions > 0:
            perf['average_time'] = perf['total_time'] / total_conversions
        
        # 保存性能样本
        self._performance_samples.append(execution_time)
        if len(self._performance_samples) > self._max_samples:
            self._performance_samples = self._performance_samples[-self._max_samples:]
    
    def _update_cache_hit_rate(self):
        """更新缓存命中率"""
        cache = self._stats['cache']
        total_requests = cache['hits'] + cache['misses']
        if total_requests > 0:
            cache['hit_rate'] = cache['hits'] / total_requests
    
    def _analyze_error_pattern(self, code: str, error_type: str):
        """分析错误模式"""
        patterns = self._stats['errors']['error_patterns']
        
        # 按错误类型分析
        if error_type not in patterns:
            patterns[error_type] = {
                'count': 0,
                'common_codes': {},
                'code_patterns': []
            }
        
        pattern_data = patterns[error_type]
        pattern_data['count'] += 1
        
        # 记录常见代码
        pattern_data['common_codes'][code] = pattern_data['common_codes'].get(code, 0) + 1
        
        # 分析代码模式
        if len(code) == 6 and code.isdigit():
            pattern_data['code_patterns'].append('6_digit_number')
        elif '.' in code:
            pattern_data['code_patterns'].append('contains_dot')
        elif code.isalpha():
            pattern_data['code_patterns'].append('alphabetic_only')


class ConversionMonitor:
    """代码转换监控器，提供实时监控和报警功能"""
    
    def __init__(self, logger: CodeConversionLogger, 
                 alert_thresholds: Dict[str, float] = None):
        """
        初始化转换监控器
        
        Args:
            logger: 代码转换日志记录器
            alert_thresholds: 报警阈值配置
        """
        self.logger = logger
        self.alert_thresholds = alert_thresholds or {
            'failure_rate': 0.1,  # 失败率超过10%报警
            'avg_response_time': 0.01,  # 平均响应时间超过10ms报警
            'cache_hit_rate': 0.8,  # 缓存命中率低于80%报警
            'error_spike': 10  # 短时间内错误数量超过10个报警
        }
        self.alerts = []
        self._last_check_time = datetime.now()
    
    def check_health(self) -> Dict[str, Any]:
        """
        检查系统健康状态
        
        Returns:
            健康状态报告
        """
        stats = self.logger.get_conversion_stats()
        performance = self.logger.get_performance_report()
        
        health_report = {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'metrics': {
                'total_conversions': stats['conversions']['total'],
                'success_rate': stats['conversions']['success_rate'],
                'failure_rate': stats['conversions']['failure_rate'],
                'avg_response_time': performance['average_time'],
                'cache_hit_rate': stats['cache']['hit_rate']
            },
            'alerts': [],
            'recommendations': []
        }
        
        # 检查各项指标
        alerts = []
        
        # 检查失败率
        if stats['conversions']['failure_rate'] > self.alert_thresholds['failure_rate']:
            alerts.append({
                'type': 'high_failure_rate',
                'severity': 'warning',
                'message': f"转换失败率过高: {stats['conversions']['failure_rate']:.2%}",
                'threshold': self.alert_thresholds['failure_rate'],
                'current_value': stats['conversions']['failure_rate']
            })
        
        # 检查响应时间
        if performance['average_time'] > self.alert_thresholds['avg_response_time']:
            alerts.append({
                'type': 'slow_response',
                'severity': 'warning',
                'message': f"平均响应时间过长: {performance['average_time']:.3f}s",
                'threshold': self.alert_thresholds['avg_response_time'],
                'current_value': performance['average_time']
            })
        
        # 检查缓存命中率
        if stats['cache']['hit_rate'] < self.alert_thresholds['cache_hit_rate']:
            alerts.append({
                'type': 'low_cache_hit_rate',
                'severity': 'info',
                'message': f"缓存命中率较低: {stats['cache']['hit_rate']:.2%}",
                'threshold': self.alert_thresholds['cache_hit_rate'],
                'current_value': stats['cache']['hit_rate']
            })
        
        # 检查错误激增
        recent_errors = len([
            error for error in stats['errors']['recent_errors']
            if (datetime.now() - error['timestamp']).total_seconds() < 300  # 5分钟内
        ])
        
        if recent_errors > self.alert_thresholds['error_spike']:
            alerts.append({
                'type': 'error_spike',
                'severity': 'critical',
                'message': f"短时间内错误激增: {recent_errors} 个错误（5分钟内）",
                'threshold': self.alert_thresholds['error_spike'],
                'current_value': recent_errors
            })
        
        health_report['alerts'] = alerts
        
        # 确定整体状态
        if any(alert['severity'] == 'critical' for alert in alerts):
            health_report['status'] = 'critical'
        elif any(alert['severity'] == 'warning' for alert in alerts):
            health_report['status'] = 'warning'
        
        # 生成建议
        health_report['recommendations'] = self._generate_recommendations(alerts, stats)
        
        return health_report
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """
        获取监控面板数据
        
        Returns:
            面板数据字典
        """
        stats = self.logger.get_conversion_stats()
        performance = self.logger.get_performance_report()
        error_analysis = self.logger.get_error_analysis()
        
        return {
            'overview': {
                'total_conversions': stats['conversions']['total'],
                'success_rate': stats['conversions']['success_rate'],
                'avg_response_time': performance['average_time'],
                'cache_hit_rate': stats['cache']['hit_rate'],
                'uptime': stats['uptime']
            },
            'conversion_stats': stats['conversions'],
            'performance_metrics': performance,
            'error_summary': error_analysis['error_summary'],
            'recent_errors': error_analysis['recent_errors'],
            'format_distribution': stats['conversions']['by_format'],
            'health_status': self.check_health()['status']
        }
    
    def _generate_recommendations(self, alerts: List[Dict[str, Any]], 
                                stats: Dict[str, Any]) -> List[str]:
        """生成优化建议"""
        recommendations = []
        
        for alert in alerts:
            if alert['type'] == 'high_failure_rate':
                recommendations.append("检查输入数据质量，考虑添加预处理步骤")
                recommendations.append("分析失败原因，优化错误处理逻辑")
            elif alert['type'] == 'slow_response':
                recommendations.append("检查缓存配置，考虑增加缓存大小")
                recommendations.append("优化转换算法，减少计算复杂度")
            elif alert['type'] == 'low_cache_hit_rate':
                recommendations.append("分析缓存使用模式，调整缓存策略")
                recommendations.append("考虑预热常用代码转换")
            elif alert['type'] == 'error_spike':
                recommendations.append("立即检查系统状态和输入数据")
                recommendations.append("考虑启用降级模式")
        
        return list(set(recommendations))  # 去重


class CodeValidationHelper:
    """代码验证助手"""
    
    @staticmethod
    def validate_and_suggest(code: str) -> Tuple[bool, List[str], List[str]]:
        """
        验证代码并提供建议
        
        Args:
            code: 股票代码
            
        Returns:
            (是否有效, 检测到的问题, 修正建议) 元组
        """
        if not code or not isinstance(code, str):
            return False, ["代码不能为空且必须为字符串"], ["请提供有效的股票代码字符串"]
        
        code = code.strip()
        issues = []
        suggestions = []
        
        # 检查基本格式
        if not code:
            issues.append("代码为空")
            suggestions.append("请提供股票代码")
            return False, issues, suggestions
        
        # 检查长度
        if len(code) < 6:
            issues.append("代码长度过短")
            suggestions.append("股票代码至少需要6位数字")
        elif len(code) > 20:
            issues.append("代码长度过长")
            suggestions.append("请检查代码格式是否正确")
        
        # 检查字符
        if not re.match(r'^[a-zA-Z0-9._]+$', code):
            issues.append("包含无效字符")
            suggestions.append("股票代码只能包含字母、数字、点号和下划线")
        
        # 检查是否包含数字
        if not re.search(r'\d', code):
            issues.append("缺少数字部分")
            suggestions.append("股票代码必须包含6位数字")
        
        # 尝试识别格式
        detected_format = PatternMatcher.identify_format(code)
        if detected_format:
            return True, [], []
        
        # 提供格式建议
        format_suggestions = PatternMatcher.suggest_corrections(code)
        suggestions.extend(format_suggestions)
        
        return False, issues, suggestions
    
    @staticmethod
    def get_detailed_validation_result(code: str) -> Dict[str, Any]:
        """
        获取详细的验证结果
        
        Args:
            code: 股票代码
            
        Returns:
            详细的验证结果字典
        """
        is_valid, issues, suggestions = CodeValidationHelper.validate_and_suggest(code)
        
        result = {
            'code': code,
            'is_valid': is_valid,
            'issues': issues,
            'suggestions': suggestions,
            'detected_format': None,
            'possible_formats': [],
            'exchange_info': None
        }
        
        if is_valid:
            try:
                # 识别格式
                detected_format = PatternMatcher.identify_format(code)
                result['detected_format'] = detected_format
                
                # 尝试解析
                stock_code, exchange = StockCodeConverter.parse_stock_code(code)
                result['parsed_code'] = stock_code
                result['parsed_exchange'] = exchange
                result['exchange_info'] = ExchangeInferrer.get_exchange_info(exchange)
                
            except Exception as e:
                result['parse_error'] = str(e)
        else:
            # 获取可能的格式
            result['possible_formats'] = PatternMatcher.get_format_suggestions(code)
        
        return result


class PatternMatcher:
    """股票代码格式识别器"""
    
    PATTERNS = {
        'standard': re.compile(r'^([0-9]{6})\.(SH|SZ)$'),
        'exchange_prefix': re.compile(r'^(SH|SZ)([0-9]{6})$'),
        'pure_number': re.compile(r'^([0-9]{6})$'),
        'baostock': re.compile(r'^(sh|sz)\.([0-9]{6})$'),
        'eastmoney': re.compile(r'^([01])\.([0-9]{6})$'),
        'tonghuashun': re.compile(r'^hs_([0-9]{6})$'),
    }
    
    @classmethod
    def identify_format(cls, code: str) -> Optional[str]:
        """
        识别股票代码格式
        
        Args:
            code: 股票代码
            
        Returns:
            格式名称，如果无法识别返回None
        """
        if not code or not isinstance(code, str):
            return None
        
        code = code.strip()
        
        # 按优先级检查各种格式
        for format_name, pattern in cls.PATTERNS.items():
            if pattern.match(code.upper() if format_name in ['standard', 'exchange_prefix'] else code.lower()):
                return format_name
        
        return None
    
    @classmethod
    def validate_format(cls, code: str, expected_format: str) -> bool:
        """
        验证代码是否符合指定格式
        
        Args:
            code: 股票代码
            expected_format: 期望的格式
            
        Returns:
            是否符合格式
        """
        if not code or not isinstance(code, str) or expected_format not in cls.PATTERNS:
            return False
        
        pattern = cls.PATTERNS[expected_format]
        test_code = code.upper() if expected_format in ['standard', 'exchange_prefix'] else code.lower()
        return bool(pattern.match(test_code))
    
    @classmethod
    def get_format_suggestions(cls, code: str) -> List[str]:
        """
        获取可能的格式建议
        
        Args:
            code: 股票代码
            
        Returns:
            可能的格式列表
        """
        if not code or not isinstance(code, str):
            return []
        
        suggestions = []
        code = code.strip()
        
        # 检查所有可能的格式
        for format_name, pattern in cls.PATTERNS.items():
            test_code = code.upper() if format_name in ['standard', 'exchange_prefix'] else code.lower()
            if pattern.match(test_code):
                suggestions.append(format_name)
        
        return suggestions
    
    @classmethod
    def suggest_corrections(cls, code: str) -> List[str]:
        """
        为无效代码提供修正建议
        
        Args:
            code: 无效的股票代码
            
        Returns:
            修正建议列表
        """
        if not code or not isinstance(code, str):
            return ["请提供有效的股票代码字符串"]
        
        code = code.strip()
        suggestions = []
        
        # 检查是否只是大小写问题
        if re.match(r'^[0-9]{6}\.(sh|sz)$', code.lower()):
            suggestions.append(f"尝试: {code.upper()}")
        
        # 检查是否缺少交易所后缀
        if re.match(r'^[0-9]{6}$', code):
            suggestions.append(f"尝试: {code}.SH 或 {code}.SZ")
        
        # 检查是否是反向格式
        if re.match(r'^(SH|SZ)[0-9]{6}$', code.upper()):
            match = re.match(r'^(SH|SZ)([0-9]{6})$', code.upper())
            if match:
                exchange, stock_code = match.groups()
                suggestions.append(f"尝试: {stock_code}.{exchange}")
        
        # 检查常见的格式错误
        if '.' in code:
            parts = code.split('.')
            if len(parts) == 2:
                left, right = parts
                if len(left) == 6 and left.isdigit() and len(right) == 2:
                    suggestions.append(f"尝试: {left}.{right.upper()}")
        
        if not suggestions:
            suggestions.append("请使用标准格式: 000001.SZ")
            suggestions.append("或其他支持的格式: sh.000001, 0.000001, hs_000001")
        
        return suggestions


class ExchangeInferrer:
    """交易所推断引擎"""
    
    EXCHANGE_RULES = {
        'SH': {
            'patterns': [r'^60\d{4}$', r'^68\d{4}$', r'^90\d{4}$'],
            'description': '上海证券交易所',
            'examples': ['600000', '688001', '900001']
        },
        'SZ': {
            'patterns': [r'^00\d{4}$', r'^30\d{4}$', r'^20\d{4}$'],
            'description': '深圳证券交易所',
            'examples': ['000001', '300001', '200001']
        }
    }
    
    @classmethod
    def infer_exchange(cls, code: str) -> str:
        """
        推断股票代码的交易所
        
        Args:
            code: 6位股票代码
            
        Returns:
            交易所代码 (SH/SZ)
            
        Raises:
            ValidationError: 无法推断交易所
        """
        if not code or not isinstance(code, str) or len(code) != 6 or not code.isdigit():
            raise ValidationError(f"无效的股票代码用于交易所推断: {code}")
        
        inference_details = {
            'code': code,
            'checked_patterns': [],
            'possible_exchanges': []
        }
        
        for exchange, rules in cls.EXCHANGE_RULES.items():
            for pattern in rules['patterns']:
                inference_details['checked_patterns'].append({
                    'exchange': exchange,
                    'pattern': pattern,
                    'matched': bool(re.match(pattern, code))
                })
                
                if re.match(pattern, code):
                    return exchange
        
        # 如果无法推断，抛出异常而不是默认返回
        raise ValidationError(f"无法推断股票代码 {code} 的交易所，请明确指定交易所")
    
    @classmethod
    def get_exchange_info(cls, exchange: str) -> Dict[str, Any]:
        """
        获取交易所信息
        
        Args:
            exchange: 交易所代码
            
        Returns:
            交易所信息字典
        """
        return cls.EXCHANGE_RULES.get(exchange, {})
    
    @classmethod
    def get_all_exchanges(cls) -> List[str]:
        """获取所有支持的交易所列表"""
        return list(cls.EXCHANGE_RULES.keys())
    
    @classmethod
    def is_valid_exchange(cls, exchange: str) -> bool:
        """检查是否是有效的交易所代码"""
        return exchange in cls.EXCHANGE_RULES


class CacheEntry:
    """缓存条目，包含值和元数据"""
    
    def __init__(self, value: str, access_count: int = 1, created_at: float = None):
        self.value = value
        self.access_count = access_count
        self.created_at = created_at or time.time()
        self.last_accessed = self.created_at
        self.frequency_score = 1.0
    
    def access(self) -> None:
        """记录访问"""
        self.access_count += 1
        self.last_accessed = time.time()
        # 更新频率分数（考虑时间衰减）
        time_factor = 1.0 / (1.0 + (time.time() - self.created_at) / 3600)  # 1小时衰减
        self.frequency_score = self.access_count * time_factor
    
    def age(self) -> float:
        """获取条目年龄（秒）"""
        return time.time() - self.created_at
    
    def idle_time(self) -> float:
        """获取空闲时间（秒）"""
        return time.time() - self.last_accessed


class CodeConversionCache:
    """增强的代码转换缓存管理器 - 多级缓存和智能管理"""
    
    def __init__(self, l1_size: int = 1000, l2_size: int = 10000, 
                 enable_preheating: bool = True, ttl: int = 3600):
        """
        初始化多级缓存系统
        
        Args:
            l1_size: L1缓存大小（热点数据）
            l2_size: L2缓存大小（常规数据）
            enable_preheating: 是否启用缓存预热
            ttl: 缓存条目生存时间（秒）
        """
        # L1缓存：最热点的数据，使用LRU策略
        self._l1_cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._l1_max_size = l1_size
        
        # L2缓存：常规数据，使用LFU策略
        self._l2_cache: Dict[str, CacheEntry] = {}
        self._l2_max_size = l2_size
        
        self._ttl = ttl
        self._enable_preheating = enable_preheating
        self._lock = threading.RLock()
        
        # 统计信息
        self._stats = {
            'l1_hits': 0,
            'l2_hits': 0,
            'misses': 0,
            'l1_evictions': 0,
            'l2_evictions': 0,
            'puts': 0,
            'promotions': 0,  # L2到L1的提升次数
            'demotions': 0,   # L1到L2的降级次数
            'ttl_evictions': 0,
            'preheating_hits': 0,
            'created_at': time.time()
        }
        
        # 预热数据
        self._preheating_patterns = [
            # 常见的股票代码模式
            ('000001.SZ', '000001', 'SZ'),
            ('600000.SH', '600000', 'SH'),
            ('300001.SZ', '300001', 'SZ'),
        ]
        
        if self._enable_preheating:
            self._preheat_cache()
    
    def get(self, key: str) -> Optional[str]:
        """
        获取缓存值 - 多级缓存查找
        
        Args:
            key: 缓存键
            
        Returns:
            缓存值，如果不存在返回None
        """
        with self._lock:
            # 首先检查L1缓存
            if key in self._l1_cache:
                entry = self._l1_cache.pop(key)
                
                # 检查TTL
                if self._is_expired(entry):
                    self._stats['ttl_evictions'] += 1
                    return None
                
                entry.access()
                self._l1_cache[key] = entry  # 移动到末尾
                self._stats['l1_hits'] += 1
                return entry.value
            
            # 检查L2缓存
            if key in self._l2_cache:
                entry = self._l2_cache[key]
                
                # 检查TTL
                if self._is_expired(entry):
                    del self._l2_cache[key]
                    self._stats['ttl_evictions'] += 1
                    return None
                
                entry.access()
                self._stats['l2_hits'] += 1
                
                # 如果访问频率足够高，提升到L1缓存
                if entry.frequency_score > 2.0:
                    self._promote_to_l1(key, entry)
                
                return entry.value
            
            self._stats['misses'] += 1
            return None
    
    def put(self, key: str, value: str) -> None:
        """
        存储缓存值 - 智能缓存策略
        
        Args:
            key: 缓存键
            value: 缓存值
        """
        with self._lock:
            entry = CacheEntry(value)
            
            # 如果已存在于L1缓存，更新
            if key in self._l1_cache:
                self._l1_cache[key] = entry
                return
            
            # 如果已存在于L2缓存，更新
            if key in self._l2_cache:
                self._l2_cache[key] = entry
                return
            
            # 新条目，根据策略决定放入哪个缓存
            if self._should_put_in_l1(key, value):
                self._put_in_l1(key, entry)
            else:
                self._put_in_l2(key, entry)
            
            self._stats['puts'] += 1
    
    def _should_put_in_l1(self, key: str, value: str) -> bool:
        """判断是否应该直接放入L1缓存"""
        # 常见格式的代码直接放入L1
        if '.SZ' in key or '.SH' in key:
            return True
        
        # 标准化操作的结果放入L1
        if key.startswith('normalize:'):
            return True
        
        return False
    
    def _put_in_l1(self, key: str, entry: CacheEntry) -> None:
        """放入L1缓存"""
        if len(self._l1_cache) >= self._l1_max_size:
            # LRU淘汰：移除最久未使用的项
            old_key, old_entry = self._l1_cache.popitem(last=False)
            self._stats['l1_evictions'] += 1
            
            # 将淘汰的项降级到L2缓存（如果还有价值）
            if old_entry.access_count > 1:
                self._demote_to_l2(old_key, old_entry)
        
        self._l1_cache[key] = entry
    
    def _put_in_l2(self, key: str, entry: CacheEntry) -> None:
        """放入L2缓存"""
        if len(self._l2_cache) >= self._l2_max_size:
            # LFU淘汰：移除频率最低的项
            victim_key = min(self._l2_cache.keys(), 
                           key=lambda k: self._l2_cache[k].frequency_score)
            del self._l2_cache[victim_key]
            self._stats['l2_evictions'] += 1
        
        self._l2_cache[key] = entry
    
    def _promote_to_l1(self, key: str, entry: CacheEntry) -> None:
        """将条目从L2提升到L1"""
        del self._l2_cache[key]
        self._put_in_l1(key, entry)
        self._stats['promotions'] += 1
    
    def _demote_to_l2(self, key: str, entry: CacheEntry) -> None:
        """将条目从L1降级到L2"""
        if len(self._l2_cache) < self._l2_max_size:
            self._l2_cache[key] = entry
            self._stats['demotions'] += 1
    
    def _is_expired(self, entry: CacheEntry) -> bool:
        """检查缓存条目是否过期"""
        return entry.age() > self._ttl
    
    def _preheat_cache(self) -> None:
        """预热缓存 - 加载常见的转换结果"""
        for pattern_key, stock_code, exchange in self._preheating_patterns:
            # 预热标准化结果
            normalize_key = f"normalize:{pattern_key}"
            self.put(normalize_key, pattern_key)
            
            # 预热格式转换结果
            self.put(f"convert:{pattern_key}:baostock", f"{exchange.lower()}.{stock_code}")
            self.put(f"convert:{pattern_key}:eastmoney", f"{'1' if exchange == 'SH' else '0'}.{stock_code}")
            self.put(f"convert:{pattern_key}:tonghuashun", f"hs_{stock_code}")
    
    def clear(self) -> None:
        """清空所有缓存"""
        with self._lock:
            self._l1_cache.clear()
            self._l2_cache.clear()
            
            # 重置统计信息
            created_at = self._stats['created_at']
            self._stats = {
                'l1_hits': 0,
                'l2_hits': 0,
                'misses': 0,
                'l1_evictions': 0,
                'l2_evictions': 0,
                'puts': 0,
                'promotions': 0,
                'demotions': 0,
                'ttl_evictions': 0,
                'preheating_hits': 0,
                'created_at': created_at
            }
            
            # 重新预热
            if self._enable_preheating:
                self._preheat_cache()
    
    def cleanup_expired(self) -> int:
        """清理过期条目"""
        expired_count = 0
        
        with self._lock:
            # 清理L1缓存中的过期条目
            expired_keys = []
            for key, entry in self._l1_cache.items():
                if self._is_expired(entry):
                    expired_keys.append(key)
            
            for key in expired_keys:
                del self._l1_cache[key]
                expired_count += 1
            
            # 清理L2缓存中的过期条目
            expired_keys = []
            for key, entry in self._l2_cache.items():
                if self._is_expired(entry):
                    expired_keys.append(key)
            
            for key in expired_keys:
                del self._l2_cache[key]
                expired_count += 1
            
            self._stats['ttl_evictions'] += expired_count
        
        return expired_count
    
    def get_stats(self) -> Dict[str, Any]:
        """获取详细的缓存统计信息"""
        with self._lock:
            total_hits = self._stats['l1_hits'] + self._stats['l2_hits']
            total_requests = total_hits + self._stats['misses']
            
            l1_hit_rate = self._stats['l1_hits'] / total_requests if total_requests > 0 else 0.0
            l2_hit_rate = self._stats['l2_hits'] / total_requests if total_requests > 0 else 0.0
            overall_hit_rate = total_hits / total_requests if total_requests > 0 else 0.0
            
            return {
                'l1_cache': {
                    'size': len(self._l1_cache),
                    'max_size': self._l1_max_size,
                    'hits': self._stats['l1_hits'],
                    'hit_rate': l1_hit_rate,
                    'evictions': self._stats['l1_evictions'],
                    'utilization': len(self._l1_cache) / self._l1_max_size
                },
                'l2_cache': {
                    'size': len(self._l2_cache),
                    'max_size': self._l2_max_size,
                    'hits': self._stats['l2_hits'],
                    'hit_rate': l2_hit_rate,
                    'evictions': self._stats['l2_evictions'],
                    'utilization': len(self._l2_cache) / self._l2_max_size
                },
                'overall': {
                    'total_hits': total_hits,
                    'misses': self._stats['misses'],
                    'hit_rate': overall_hit_rate,
                    'puts': self._stats['puts'],
                    'promotions': self._stats['promotions'],
                    'demotions': self._stats['demotions'],
                    'ttl_evictions': self._stats['ttl_evictions'],
                    'uptime': time.time() - self._stats['created_at']
                },
                'memory_usage': {
                    'total_entries': len(self._l1_cache) + len(self._l2_cache),
                    'estimated_memory_kb': (len(self._l1_cache) + len(self._l2_cache)) * 0.1  # 估算
                }
            }
    
    def get_size(self) -> int:
        """获取总缓存大小"""
        with self._lock:
            return len(self._l1_cache) + len(self._l2_cache)
    
    def is_full(self) -> bool:
        """检查缓存是否已满"""
        with self._lock:
            return (len(self._l1_cache) >= self._l1_max_size and 
                   len(self._l2_cache) >= self._l2_max_size)
    
    def get_hot_keys(self, limit: int = 10) -> List[Tuple[str, float]]:
        """获取热点键列表"""
        with self._lock:
            all_entries = []
            
            # 收集L1缓存的条目
            for key, entry in self._l1_cache.items():
                all_entries.append((key, entry.frequency_score + 1.0))  # L1加权
            
            # 收集L2缓存的条目
            for key, entry in self._l2_cache.items():
                all_entries.append((key, entry.frequency_score))
            
            # 按频率分数排序
            all_entries.sort(key=lambda x: x[1], reverse=True)
            
            return all_entries[:limit]


class CacheManager:
    """缓存管理器 - 负责缓存的生命周期管理和监控"""
    
    def __init__(self, cache: CodeConversionCache):
        self.cache = cache
        self._cleanup_interval = 300  # 5分钟清理一次
        self._last_cleanup = time.time()
        self._monitoring_enabled = True
        self._performance_threshold = 0.8  # 命中率阈值
        
        # 自动清理线程
        self._cleanup_thread = None
        self._stop_cleanup = threading.Event()
        
    def start_auto_cleanup(self) -> None:
        """启动自动清理线程"""
        if self._cleanup_thread is None or not self._cleanup_thread.is_alive():
            self._stop_cleanup.clear()
            self._cleanup_thread = threading.Thread(target=self._auto_cleanup_worker, daemon=True)
            self._cleanup_thread.start()
    
    def stop_auto_cleanup(self) -> None:
        """停止自动清理线程"""
        if self._cleanup_thread and self._cleanup_thread.is_alive():
            self._stop_cleanup.set()
            self._cleanup_thread.join(timeout=1.0)
    
    def _auto_cleanup_worker(self) -> None:
        """自动清理工作线程"""
        while not self._stop_cleanup.wait(self._cleanup_interval):
            try:
                self.perform_maintenance()
            except Exception as e:
                # 记录错误但不中断清理线程
                logging.getLogger(__name__).error(f"缓存清理错误: {e}")
    
    def perform_maintenance(self) -> Dict[str, Any]:
        """执行缓存维护操作"""
        maintenance_result = {
            'expired_cleaned': 0,
            'performance_check': {},
            'recommendations': [],
            'timestamp': time.time()
        }
        
        # 清理过期条目
        expired_count = self.cache.cleanup_expired()
        maintenance_result['expired_cleaned'] = expired_count
        
        # 性能检查
        stats = self.cache.get_stats()
        maintenance_result['performance_check'] = self._analyze_performance(stats)
        
        # 生成优化建议
        maintenance_result['recommendations'] = self._generate_recommendations(stats)
        
        self._last_cleanup = time.time()
        return maintenance_result
    
    def _analyze_performance(self, stats: Dict[str, Any]) -> Dict[str, Any]:
        """分析缓存性能"""
        analysis = {
            'overall_health': 'good',
            'issues': [],
            'metrics': {}
        }
        
        overall_hit_rate = stats['overall']['hit_rate']
        l1_utilization = stats['l1_cache']['utilization']
        l2_utilization = stats['l2_cache']['utilization']
        
        analysis['metrics'] = {
            'hit_rate': overall_hit_rate,
            'l1_utilization': l1_utilization,
            'l2_utilization': l2_utilization,
            'promotion_rate': stats['overall']['promotions'] / max(stats['overall']['puts'], 1)
        }
        
        # 检查性能问题
        if overall_hit_rate < self._performance_threshold:
            analysis['overall_health'] = 'poor'
            analysis['issues'].append(f"命中率过低: {overall_hit_rate:.2%}")
        
        if l1_utilization > 0.95:
            analysis['issues'].append("L1缓存利用率过高，可能需要扩容")
        
        if l2_utilization > 0.95:
            analysis['issues'].append("L2缓存利用率过高，可能需要扩容")
        
        if stats['overall']['ttl_evictions'] > stats['overall']['puts'] * 0.1:
            analysis['issues'].append("TTL淘汰过多，考虑延长生存时间")
        
        return analysis
    
    def _generate_recommendations(self, stats: Dict[str, Any]) -> List[str]:
        """生成优化建议"""
        recommendations = []
        
        overall_hit_rate = stats['overall']['hit_rate']
        l1_hit_rate = stats['l1_cache']['hit_rate']
        l2_hit_rate = stats['l2_cache']['hit_rate']
        
        # 命中率优化建议
        if overall_hit_rate < 0.7:
            recommendations.append("考虑增加缓存大小或优化缓存策略")
        
        if l1_hit_rate / (l1_hit_rate + l2_hit_rate) < 0.6:
            recommendations.append("考虑调整L1缓存大小或提升策略")
        
        # 内存使用建议
        total_entries = stats['memory_usage']['total_entries']
        if total_entries > 50000:
            recommendations.append("缓存条目过多，考虑实施更积极的淘汰策略")
        
        # 提升/降级建议
        promotion_rate = stats['overall']['promotions'] / max(stats['overall']['puts'], 1)
        if promotion_rate > 0.3:
            recommendations.append("提升率过高，考虑调整L1缓存大小")
        elif promotion_rate < 0.05:
            recommendations.append("提升率过低，考虑优化热点检测算法")
        
        return recommendations
    
    def get_cache_health(self) -> Dict[str, Any]:
        """获取缓存健康状态"""
        stats = self.cache.get_stats()
        performance = self._analyze_performance(stats)
        
        return {
            'status': performance['overall_health'],
            'last_maintenance': self._last_cleanup,
            'next_maintenance': self._last_cleanup + self._cleanup_interval,
            'performance': performance,
            'uptime': stats['overall']['uptime'],
            'auto_cleanup_active': self._cleanup_thread and self._cleanup_thread.is_alive()
        }
    
    def optimize_cache_sizes(self) -> Dict[str, Any]:
        """根据使用模式优化缓存大小"""
        stats = self.cache.get_stats()
        hot_keys = self.cache.get_hot_keys(100)
        
        # 分析访问模式
        l1_optimal_size = max(500, len(hot_keys) // 2)
        l2_optimal_size = max(5000, len(hot_keys) * 2)
        
        current_l1_size = stats['l1_cache']['max_size']
        current_l2_size = stats['l2_cache']['max_size']
        
        optimization_result = {
            'current_sizes': {
                'l1': current_l1_size,
                'l2': current_l2_size
            },
            'recommended_sizes': {
                'l1': l1_optimal_size,
                'l2': l2_optimal_size
            },
            'expected_improvement': {
                'hit_rate_increase': 0.0,
                'memory_change': 0.0
            }
        }
        
        # 估算改进效果
        if l1_optimal_size > current_l1_size:
            optimization_result['expected_improvement']['hit_rate_increase'] = 0.05
        
        memory_change = (l1_optimal_size + l2_optimal_size) - (current_l1_size + current_l2_size)
        optimization_result['expected_improvement']['memory_change'] = memory_change * 0.1  # KB
        
        return optimization_result


class PerformanceMonitor:
    """性能监控器 - 实时监控代码转换性能"""
    
    def __init__(self):
        self._metrics = {
            'conversion_times': [],
            'batch_conversion_times': [],
            'cache_performance': {},
            'error_rates': {},
            'throughput_samples': [],
            'memory_usage_samples': [],
            'concurrent_performance': {}
        }
        self._lock = threading.RLock()
        self._start_time = time.time()
        
        # 性能阈值
        self._thresholds = {
            'max_conversion_time': 0.001,  # 1ms
            'max_batch_time_per_item': 0.0005,  # 0.5ms per item
            'min_cache_hit_rate': 0.8,
            'max_error_rate': 0.05,
            'min_throughput': 1000  # conversions per second
        }
        
        # 采样配置
        self._max_samples = 1000
        self._sampling_interval = 60  # 60秒
        self._last_sample_time = time.time()
    
    def record_conversion_time(self, operation: str, execution_time: float, 
                              cached: bool = False, success: bool = True) -> None:
        """记录转换时间"""
        with self._lock:
            sample = {
                'operation': operation,
                'time': execution_time,
                'cached': cached,
                'success': success,
                'timestamp': time.time()
            }
            
            self._metrics['conversion_times'].append(sample)
            
            # 限制样本数量
            if len(self._metrics['conversion_times']) > self._max_samples:
                self._metrics['conversion_times'] = self._metrics['conversion_times'][-self._max_samples:]
    
    def record_batch_conversion(self, batch_size: int, total_time: float, 
                               successful_count: int, parallel: bool = False,
                               max_workers: int = None) -> None:
        """记录批量转换性能"""
        with self._lock:
            sample = {
                'batch_size': batch_size,
                'total_time': total_time,
                'successful_count': successful_count,
                'time_per_item': total_time / batch_size if batch_size > 0 else 0,
                'success_rate': successful_count / batch_size if batch_size > 0 else 0,
                'parallel': parallel,
                'max_workers': max_workers,
                'throughput': successful_count / total_time if total_time > 0 else 0,
                'timestamp': time.time()
            }
            
            self._metrics['batch_conversion_times'].append(sample)
            
            # 限制样本数量
            if len(self._metrics['batch_conversion_times']) > self._max_samples:
                self._metrics['batch_conversion_times'] = self._metrics['batch_conversion_times'][-self._max_samples:]
    
    def record_cache_performance(self, cache_stats: Dict[str, Any]) -> None:
        """记录缓存性能"""
        with self._lock:
            timestamp = time.time()
            self._metrics['cache_performance'][timestamp] = cache_stats.copy()
            
            # 清理旧数据
            cutoff_time = timestamp - 3600  # 保留1小时的数据
            self._metrics['cache_performance'] = {
                t: stats for t, stats in self._metrics['cache_performance'].items()
                if t > cutoff_time
            }
    
    def record_error_rate(self, operation: str, error_count: int, total_count: int) -> None:
        """记录错误率"""
        with self._lock:
            if operation not in self._metrics['error_rates']:
                self._metrics['error_rates'][operation] = []
            
            sample = {
                'error_count': error_count,
                'total_count': total_count,
                'error_rate': error_count / total_count if total_count > 0 else 0,
                'timestamp': time.time()
            }
            
            self._metrics['error_rates'][operation].append(sample)
            
            # 限制样本数量
            if len(self._metrics['error_rates'][operation]) > 100:
                self._metrics['error_rates'][operation] = self._metrics['error_rates'][operation][-100:]
    
    def record_throughput_sample(self, operations_count: int, time_window: float) -> None:
        """记录吞吐量样本"""
        with self._lock:
            throughput = operations_count / time_window if time_window > 0 else 0
            sample = {
                'operations_count': operations_count,
                'time_window': time_window,
                'throughput': throughput,
                'timestamp': time.time()
            }
            
            self._metrics['throughput_samples'].append(sample)
            
            # 限制样本数量
            if len(self._metrics['throughput_samples']) > self._max_samples:
                self._metrics['throughput_samples'] = self._metrics['throughput_samples'][-self._max_samples:]
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """获取性能摘要"""
        with self._lock:
            summary = {
                'uptime': time.time() - self._start_time,
                'conversion_performance': self._analyze_conversion_performance(),
                'batch_performance': self._analyze_batch_performance(),
                'cache_performance': self._analyze_cache_performance(),
                'error_analysis': self._analyze_error_rates(),
                'throughput_analysis': self._analyze_throughput(),
                'performance_alerts': self._check_performance_alerts(),
                'recommendations': self._generate_performance_recommendations()
            }
            
            return summary
    
    def _analyze_conversion_performance(self) -> Dict[str, Any]:
        """分析转换性能"""
        if not self._metrics['conversion_times']:
            return {'status': 'no_data'}
        
        times = [sample['time'] for sample in self._metrics['conversion_times'] if sample['success']]
        cached_times = [sample['time'] for sample in self._metrics['conversion_times'] 
                       if sample['success'] and sample['cached']]
        uncached_times = [sample['time'] for sample in self._metrics['conversion_times'] 
                         if sample['success'] and not sample['cached']]
        
        analysis = {
            'total_conversions': len(self._metrics['conversion_times']),
            'successful_conversions': len(times),
            'avg_time': sum(times) / len(times) if times else 0,
            'min_time': min(times) if times else 0,
            'max_time': max(times) if times else 0,
            'p95_time': self._percentile(times, 95) if times else 0,
            'p99_time': self._percentile(times, 99) if times else 0,
        }
        
        if cached_times:
            analysis['cached_performance'] = {
                'avg_time': sum(cached_times) / len(cached_times),
                'count': len(cached_times)
            }
        
        if uncached_times:
            analysis['uncached_performance'] = {
                'avg_time': sum(uncached_times) / len(uncached_times),
                'count': len(uncached_times)
            }
        
        return analysis
    
    def _analyze_batch_performance(self) -> Dict[str, Any]:
        """分析批量转换性能"""
        if not self._metrics['batch_conversion_times']:
            return {'status': 'no_data'}
        
        samples = self._metrics['batch_conversion_times']
        
        # 分析串行和并行性能
        serial_samples = [s for s in samples if not s['parallel']]
        parallel_samples = [s for s in samples if s['parallel']]
        
        analysis = {
            'total_batches': len(samples),
            'serial_batches': len(serial_samples),
            'parallel_batches': len(parallel_samples)
        }
        
        if serial_samples:
            throughputs = [s['throughput'] for s in serial_samples]
            analysis['serial_performance'] = {
                'avg_throughput': sum(throughputs) / len(throughputs),
                'max_throughput': max(throughputs),
                'avg_time_per_item': sum(s['time_per_item'] for s in serial_samples) / len(serial_samples)
            }
        
        if parallel_samples:
            throughputs = [s['throughput'] for s in parallel_samples]
            analysis['parallel_performance'] = {
                'avg_throughput': sum(throughputs) / len(throughputs),
                'max_throughput': max(throughputs),
                'avg_time_per_item': sum(s['time_per_item'] for s in parallel_samples) / len(parallel_samples),
                'speedup_factor': 0  # 计算加速比
            }
            
            # 计算并行加速比
            if serial_samples and parallel_samples:
                serial_avg = sum(s['time_per_item'] for s in serial_samples) / len(serial_samples)
                parallel_avg = sum(s['time_per_item'] for s in parallel_samples) / len(parallel_samples)
                analysis['parallel_performance']['speedup_factor'] = serial_avg / parallel_avg if parallel_avg > 0 else 0
        
        return analysis
    
    def _analyze_cache_performance(self) -> Dict[str, Any]:
        """分析缓存性能"""
        if not self._metrics['cache_performance']:
            return {'status': 'no_data'}
        
        # 获取最新的缓存统计
        latest_timestamp = max(self._metrics['cache_performance'].keys())
        latest_stats = self._metrics['cache_performance'][latest_timestamp]
        
        # 计算缓存性能趋势
        timestamps = sorted(self._metrics['cache_performance'].keys())
        if len(timestamps) >= 2:
            first_stats = self._metrics['cache_performance'][timestamps[0]]
            trend = {
                'hit_rate_change': latest_stats['overall']['hit_rate'] - first_stats['overall']['hit_rate'],
                'size_change': latest_stats['memory_usage']['total_entries'] - first_stats['memory_usage']['total_entries']
            }
        else:
            trend = {'hit_rate_change': 0, 'size_change': 0}
        
        return {
            'current_stats': latest_stats,
            'trend': trend,
            'data_points': len(timestamps)
        }
    
    def _analyze_error_rates(self) -> Dict[str, Any]:
        """分析错误率"""
        analysis = {}
        
        for operation, samples in self._metrics['error_rates'].items():
            if samples:
                recent_samples = [s for s in samples if time.time() - s['timestamp'] < 3600]  # 最近1小时
                if recent_samples:
                    avg_error_rate = sum(s['error_rate'] for s in recent_samples) / len(recent_samples)
                    analysis[operation] = {
                        'avg_error_rate': avg_error_rate,
                        'sample_count': len(recent_samples),
                        'status': 'good' if avg_error_rate < self._thresholds['max_error_rate'] else 'warning'
                    }
        
        return analysis
    
    def _analyze_throughput(self) -> Dict[str, Any]:
        """分析吞吐量"""
        if not self._metrics['throughput_samples']:
            return {'status': 'no_data'}
        
        recent_samples = [s for s in self._metrics['throughput_samples'] 
                         if time.time() - s['timestamp'] < 3600]  # 最近1小时
        
        if not recent_samples:
            return {'status': 'no_recent_data'}
        
        throughputs = [s['throughput'] for s in recent_samples]
        
        return {
            'avg_throughput': sum(throughputs) / len(throughputs),
            'max_throughput': max(throughputs),
            'min_throughput': min(throughputs),
            'sample_count': len(recent_samples),
            'status': 'good' if sum(throughputs) / len(throughputs) >= self._thresholds['min_throughput'] else 'warning'
        }
    
    def _check_performance_alerts(self) -> List[Dict[str, Any]]:
        """检查性能警报"""
        alerts = []
        
        # 检查转换时间
        if self._metrics['conversion_times']:
            recent_times = [s['time'] for s in self._metrics['conversion_times'] 
                           if time.time() - s['timestamp'] < 300 and s['success']]  # 最近5分钟
            if recent_times:
                avg_time = sum(recent_times) / len(recent_times)
                if avg_time > self._thresholds['max_conversion_time']:
                    alerts.append({
                        'type': 'performance',
                        'severity': 'warning',
                        'message': f'平均转换时间过长: {avg_time:.4f}s (阈值: {self._thresholds["max_conversion_time"]}s)',
                        'metric': 'conversion_time',
                        'value': avg_time,
                        'threshold': self._thresholds['max_conversion_time']
                    })
        
        # 检查缓存命中率
        if self._metrics['cache_performance']:
            latest_timestamp = max(self._metrics['cache_performance'].keys())
            latest_stats = self._metrics['cache_performance'][latest_timestamp]
            hit_rate = latest_stats['overall']['hit_rate']
            if hit_rate < self._thresholds['min_cache_hit_rate']:
                alerts.append({
                    'type': 'cache',
                    'severity': 'warning',
                    'message': f'缓存命中率过低: {hit_rate:.2%} (阈值: {self._thresholds["min_cache_hit_rate"]:.2%})',
                    'metric': 'cache_hit_rate',
                    'value': hit_rate,
                    'threshold': self._thresholds['min_cache_hit_rate']
                })
        
        return alerts
    
    def _generate_performance_recommendations(self) -> List[str]:
        """生成性能优化建议"""
        recommendations = []
        
        # 基于转换性能的建议
        conversion_analysis = self._analyze_conversion_performance()
        if conversion_analysis.get('avg_time', 0) > self._thresholds['max_conversion_time']:
            recommendations.append("考虑优化正则表达式或增加快速路径缓存")
        
        # 基于批量性能的建议
        batch_analysis = self._analyze_batch_performance()
        if batch_analysis.get('parallel_performance', {}).get('speedup_factor', 0) < 2:
            recommendations.append("并行处理效果不佳，考虑优化线程池配置或减少锁竞争")
        
        # 基于缓存性能的建议
        cache_analysis = self._analyze_cache_performance()
        if cache_analysis.get('current_stats', {}).get('overall', {}).get('hit_rate', 0) < 0.8:
            recommendations.append("缓存命中率较低，考虑增加缓存大小或优化缓存策略")
        
        return recommendations
    
    def _percentile(self, data: List[float], percentile: int) -> float:
        """计算百分位数"""
        if not data:
            return 0.0
        
        sorted_data = sorted(data)
        index = int(len(sorted_data) * percentile / 100)
        return sorted_data[min(index, len(sorted_data) - 1)]
    
    def reset_metrics(self) -> None:
        """重置所有性能指标"""
        with self._lock:
            self._metrics = {
                'conversion_times': [],
                'batch_conversion_times': [],
                'cache_performance': {},
                'error_rates': {},
                'throughput_samples': [],
                'memory_usage_samples': [],
                'concurrent_performance': {}
            }
            self._start_time = time.time()


class PerformanceBenchmark:
    """性能基准测试套件"""
    
    def __init__(self, converter_class):
        self.converter_class = converter_class
        self.test_data = self._generate_test_data()
        self.results = {}
    
    def _generate_test_data(self) -> Dict[str, List[str]]:
        """生成测试数据"""
        return {
            'standard_codes': [
                '000001.SZ', '000002.SZ', '600000.SH', '600036.SH', '300001.SZ',
                '002001.SZ', '688001.SH', '300750.SZ', '000858.SZ', '600519.SH'
            ] * 100,  # 1000个标准格式代码
            
            'mixed_formats': [
                '000001.SZ', 'sz.000001', '0.000001', 'hs_000001', '000001',
                '600000.SH', 'sh.600000', '1.600000', 'hs_600000', '600000',
                'SZ000001', 'SH600000'
            ] * 100,  # 1200个混合格式代码
            
            'invalid_codes': [
                'invalid', '12345', '1234567', 'ABC123', '000001.XX',
                '', None, '000001.', '.SZ', 'sz.'
            ] * 10,  # 100个无效代码
            
            'edge_cases': [
                '000000.SZ', '999999.SH', '123456.SZ', '654321.SH',
                'sz.000000', 'sh.999999', '0.000000', '1.999999'
            ] * 25  # 200个边界情况
        }
    
    def run_single_conversion_benchmark(self, iterations: int = 10000) -> Dict[str, Any]:
        """运行单次转换基准测试"""
        print(f"运行单次转换基准测试 ({iterations} 次迭代)...")
        
        test_codes = self.test_data['standard_codes'][:iterations]
        
        # 预热
        for code in test_codes[:100]:
            try:
                self.converter_class.normalize_code(code)
            except:
                pass
        
        # 基准测试
        start_time = time.time()
        successful_conversions = 0
        
        for code in test_codes:
            try:
                self.converter_class.normalize_code(code)
                successful_conversions += 1
            except:
                pass
        
        end_time = time.time()
        total_time = end_time - start_time
        
        result = {
            'test_type': 'single_conversion',
            'iterations': iterations,
            'successful_conversions': successful_conversions,
            'total_time': total_time,
            'avg_time_per_conversion': total_time / iterations,
            'conversions_per_second': iterations / total_time,
            'success_rate': successful_conversions / iterations
        }
        
        self.results['single_conversion'] = result
        return result
    
    def run_batch_conversion_benchmark(self, batch_sizes: List[int] = None) -> Dict[str, Any]:
        """运行批量转换基准测试"""
        if batch_sizes is None:
            batch_sizes = [10, 50, 100, 500, 1000]
        
        print(f"运行批量转换基准测试 (批量大小: {batch_sizes})...")
        
        results = {}
        
        for batch_size in batch_sizes:
            test_codes = self.test_data['mixed_formats'][:batch_size]
            
            # 串行处理
            start_time = time.time()
            try:
                serial_results = self.converter_class.batch_normalize_codes(test_codes, parallel=False)
                serial_time = time.time() - start_time
                serial_success = len([r for r in serial_results if r])
            except Exception as e:
                serial_time = float('inf')
                serial_success = 0
            
            # 并行处理
            start_time = time.time()
            try:
                parallel_results = self.converter_class.batch_normalize_codes(test_codes, parallel=True)
                parallel_time = time.time() - start_time
                parallel_success = len([r for r in parallel_results if r])
            except Exception as e:
                parallel_time = float('inf')
                parallel_success = 0
            
            # 计算加速比
            speedup = serial_time / parallel_time if parallel_time > 0 and serial_time != float('inf') else 0
            
            results[f'batch_{batch_size}'] = {
                'batch_size': batch_size,
                'serial': {
                    'time': serial_time,
                    'success_count': serial_success,
                    'throughput': serial_success / serial_time if serial_time > 0 else 0
                },
                'parallel': {
                    'time': parallel_time,
                    'success_count': parallel_success,
                    'throughput': parallel_success / parallel_time if parallel_time > 0 else 0
                },
                'speedup_factor': speedup
            }
        
        self.results['batch_conversion'] = results
        return results
    
    def run_cache_performance_benchmark(self, cache_sizes: List[int] = None) -> Dict[str, Any]:
        """运行缓存性能基准测试"""
        if cache_sizes is None:
            cache_sizes = [100, 500, 1000, 5000]
        
        print(f"运行缓存性能基准测试 (缓存大小: {cache_sizes})...")
        
        results = {}
        original_cache = self.converter_class._cache
        
        for cache_size in cache_sizes:
            # 创建指定大小的缓存
            test_cache = CodeConversionCache(l1_size=cache_size//10, l2_size=cache_size)
            self.converter_class._cache = test_cache
            
            # 预热缓存
            warmup_codes = self.test_data['standard_codes'][:cache_size//2]
            for code in warmup_codes:
                try:
                    self.converter_class.normalize_code(code)
                except:
                    pass
            
            # 测试缓存命中性能
            test_codes = warmup_codes * 2  # 重复测试以触发缓存命中
            
            start_time = time.time()
            cache_hits = 0
            total_conversions = 0
            
            for code in test_codes:
                try:
                    self.converter_class.normalize_code(code)
                    total_conversions += 1
                except:
                    pass
            
            end_time = time.time()
            
            cache_stats = test_cache.get_stats()
            
            results[f'cache_{cache_size}'] = {
                'cache_size': cache_size,
                'test_time': end_time - start_time,
                'total_conversions': total_conversions,
                'cache_stats': cache_stats,
                'avg_time_per_conversion': (end_time - start_time) / total_conversions if total_conversions > 0 else 0
            }
        
        # 恢复原始缓存
        self.converter_class._cache = original_cache
        
        self.results['cache_performance'] = results
        return results
    
    def run_memory_usage_benchmark(self, data_sizes: List[int] = None) -> Dict[str, Any]:
        """运行内存使用基准测试"""
        if data_sizes is None:
            data_sizes = [1000, 5000, 10000, 50000]
        
        print(f"运行内存使用基准测试 (数据大小: {data_sizes})...")
        
        import psutil
        import os
        
        results = {}
        process = psutil.Process(os.getpid())
        
        for data_size in data_sizes:
            # 清空缓存
            self.converter_class.clear_cache()
            
            # 记录初始内存
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            # 生成测试数据
            test_codes = (self.test_data['mixed_formats'] * (data_size // len(self.test_data['mixed_formats']) + 1))[:data_size]
            
            # 执行转换
            start_time = time.time()
            successful_conversions = 0
            
            for code in test_codes:
                try:
                    self.converter_class.normalize_code(code)
                    successful_conversions += 1
                except:
                    pass
            
            end_time = time.time()
            
            # 记录最终内存
            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_increase = final_memory - initial_memory
            
            cache_stats = self.converter_class.get_cache_stats()
            
            results[f'memory_{data_size}'] = {
                'data_size': data_size,
                'successful_conversions': successful_conversions,
                'execution_time': end_time - start_time,
                'initial_memory_mb': initial_memory,
                'final_memory_mb': final_memory,
                'memory_increase_mb': memory_increase,
                'memory_per_conversion_kb': (memory_increase * 1024) / successful_conversions if successful_conversions > 0 else 0,
                'cache_entries': cache_stats['memory_usage']['total_entries']
            }
        
        self.results['memory_usage'] = results
        return results
    
    def run_concurrent_benchmark(self, thread_counts: List[int] = None, operations_per_thread: int = 1000) -> Dict[str, Any]:
        """运行并发性能基准测试"""
        if thread_counts is None:
            thread_counts = [1, 2, 4, 8, 16]
        
        print(f"运行并发性能基准测试 (线程数: {thread_counts}, 每线程操作数: {operations_per_thread})...")
        
        results = {}
        
        def worker_function(codes: List[str], results_list: List[Dict[str, Any]], worker_id: int):
            """工作线程函数"""
            start_time = time.time()
            successful_conversions = 0
            errors = 0
            
            for code in codes:
                try:
                    self.converter_class.normalize_code(code)
                    successful_conversions += 1
                except:
                    errors += 1
            
            end_time = time.time()
            
            results_list.append({
                'worker_id': worker_id,
                'successful_conversions': successful_conversions,
                'errors': errors,
                'execution_time': end_time - start_time
            })
        
        for thread_count in thread_counts:
            # 准备测试数据
            total_operations = thread_count * operations_per_thread
            test_codes = (self.test_data['mixed_formats'] * (total_operations // len(self.test_data['mixed_formats']) + 1))[:total_operations]
            
            # 分割数据给各个线程
            codes_per_thread = len(test_codes) // thread_count
            thread_data = [test_codes[i*codes_per_thread:(i+1)*codes_per_thread] for i in range(thread_count)]
            
            # 启动线程
            threads = []
            thread_results = []
            
            start_time = time.time()
            
            for i in range(thread_count):
                thread = threading.Thread(
                    target=worker_function,
                    args=(thread_data[i], thread_results, i)
                )
                threads.append(thread)
                thread.start()
            
            # 等待所有线程完成
            for thread in threads:
                thread.join()
            
            end_time = time.time()
            
            # 汇总结果
            total_successful = sum(r['successful_conversions'] for r in thread_results)
            total_errors = sum(r['errors'] for r in thread_results)
            total_time = end_time - start_time
            
            results[f'concurrent_{thread_count}'] = {
                'thread_count': thread_count,
                'operations_per_thread': operations_per_thread,
                'total_operations': total_operations,
                'successful_conversions': total_successful,
                'errors': total_errors,
                'total_time': total_time,
                'throughput': total_successful / total_time if total_time > 0 else 0,
                'success_rate': total_successful / total_operations if total_operations > 0 else 0,
                'thread_results': thread_results
            }
        
        self.results['concurrent'] = results
        return results
    
    def run_full_benchmark_suite(self) -> Dict[str, Any]:
        """运行完整的基准测试套件"""
        print("开始运行完整的性能基准测试套件...")
        
        suite_start_time = time.time()
        
        # 运行各项基准测试
        self.run_single_conversion_benchmark()
        self.run_batch_conversion_benchmark()
        self.run_cache_performance_benchmark()
        self.run_memory_usage_benchmark()
        self.run_concurrent_benchmark()
        
        suite_end_time = time.time()
        
        # 生成综合报告
        summary = {
            'suite_execution_time': suite_end_time - suite_start_time,
            'test_results': self.results,
            'performance_score': self._calculate_performance_score(),
            'recommendations': self._generate_benchmark_recommendations()
        }
        
        return summary
    
    def _calculate_performance_score(self) -> Dict[str, Any]:
        """计算性能评分"""
        scores = {}
        
        # 单次转换性能评分 (0-100)
        if 'single_conversion' in self.results:
            single_result = self.results['single_conversion']
            avg_time = single_result['avg_time_per_conversion']
            if avg_time <= 0.0001:  # 0.1ms
                scores['single_conversion'] = 100
            elif avg_time <= 0.001:  # 1ms
                scores['single_conversion'] = 80
            elif avg_time <= 0.01:  # 10ms
                scores['single_conversion'] = 60
            else:
                scores['single_conversion'] = 40
        
        # 批量转换性能评分
        if 'batch_conversion' in self.results:
            batch_results = self.results['batch_conversion']
            avg_speedup = sum(r['speedup_factor'] for r in batch_results.values()) / len(batch_results)
            if avg_speedup >= 4:
                scores['batch_conversion'] = 100
            elif avg_speedup >= 2:
                scores['batch_conversion'] = 80
            elif avg_speedup >= 1.5:
                scores['batch_conversion'] = 60
            else:
                scores['batch_conversion'] = 40
        
        # 缓存性能评分
        if 'cache_performance' in self.results:
            cache_results = self.results['cache_performance']
            avg_hit_rate = sum(r['cache_stats']['overall']['hit_rate'] for r in cache_results.values()) / len(cache_results)
            if avg_hit_rate >= 0.9:
                scores['cache_performance'] = 100
            elif avg_hit_rate >= 0.8:
                scores['cache_performance'] = 80
            elif avg_hit_rate >= 0.7:
                scores['cache_performance'] = 60
            else:
                scores['cache_performance'] = 40
        
        # 计算总分
        if scores:
            overall_score = sum(scores.values()) / len(scores)
            scores['overall'] = overall_score
        
        return scores
    
    def _generate_benchmark_recommendations(self) -> List[str]:
        """生成基准测试建议"""
        recommendations = []
        
        # 基于单次转换性能的建议
        if 'single_conversion' in self.results:
            avg_time = self.results['single_conversion']['avg_time_per_conversion']
            if avg_time > 0.001:
                recommendations.append("单次转换性能较慢，建议优化正则表达式或增加快速路径")
        
        # 基于批量转换性能的建议
        if 'batch_conversion' in self.results:
            batch_results = self.results['batch_conversion']
            avg_speedup = sum(r['speedup_factor'] for r in batch_results.values()) / len(batch_results)
            if avg_speedup < 2:
                recommendations.append("并行处理效果不佳，建议优化线程池配置或减少锁竞争")
        
        # 基于内存使用的建议
        if 'memory_usage' in self.results:
            memory_results = self.results['memory_usage']
            max_memory_per_conversion = max(r['memory_per_conversion_kb'] for r in memory_results.values())
            if max_memory_per_conversion > 1:  # 1KB per conversion
                recommendations.append("内存使用过高，建议优化缓存策略或实施更积极的清理")
        
        return recommendations
    
    def generate_report(self, output_file: str = None) -> str:
        """生成基准测试报告"""
        if not self.results:
            return "没有基准测试结果可用"
        
        report_lines = [
            "# 股票代码转换器性能基准测试报告",
            f"生成时间: {time.strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## 测试摘要"
        ]
        
        # 添加各项测试结果
        for test_type, results in self.results.items():
            report_lines.append(f"\n### {test_type.replace('_', ' ').title()}")
            
            if test_type == 'single_conversion':
                report_lines.extend([
                    f"- 总转换次数: {results['iterations']:,}",
                    f"- 成功转换次数: {results['successful_conversions']:,}",
                    f"- 平均转换时间: {results['avg_time_per_conversion']:.6f}s",
                    f"- 转换速率: {results['conversions_per_second']:.0f} ops/s",
                    f"- 成功率: {results['success_rate']:.2%}"
                ])
            
            elif test_type == 'batch_conversion':
                report_lines.append("| 批量大小 | 串行时间(s) | 并行时间(s) | 加速比 | 串行吞吐量 | 并行吞吐量 |")
                report_lines.append("|---------|------------|------------|--------|-----------|-----------|")
                
                for batch_key, batch_result in results.items():
                    batch_size = batch_result['batch_size']
                    serial_time = batch_result['serial']['time']
                    parallel_time = batch_result['parallel']['time']
                    speedup = batch_result['speedup_factor']
                    serial_throughput = batch_result['serial']['throughput']
                    parallel_throughput = batch_result['parallel']['throughput']
                    
                    report_lines.append(
                        f"| {batch_size} | {serial_time:.4f} | {parallel_time:.4f} | "
                        f"{speedup:.2f}x | {serial_throughput:.0f} | {parallel_throughput:.0f} |"
                    )
        
        # 添加性能评分
        scores = self._calculate_performance_score()
        if scores:
            report_lines.extend([
                "\n## 性能评分",
                f"- 总体评分: {scores.get('overall', 0):.1f}/100"
            ])
            
            for test_type, score in scores.items():
                if test_type != 'overall':
                    report_lines.append(f"- {test_type.replace('_', ' ').title()}: {score:.1f}/100")
        
        # 添加建议
        recommendations = self._generate_benchmark_recommendations()
        if recommendations:
            report_lines.extend([
                "\n## 优化建议"
            ])
            for i, rec in enumerate(recommendations, 1):
                report_lines.append(f"{i}. {rec}")
        
        report = "\n".join(report_lines)
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report)
        
        return report


class StockCodeConverter:
    """股票代码转换器 - 性能优化版本"""
    
    # 交易所映射
    EXCHANGE_MAPPING = {
        'SH': 'sh',  # 上海证券交易所
        'SZ': 'sz',  # 深圳证券交易所
    }
    
    # 反向映射
    REVERSE_EXCHANGE_MAPPING = {v: k for k, v in EXCHANGE_MAPPING.items()}
    
    # 预编译的正则表达式模式 - 性能优化
    _COMPILED_PATTERNS = {
        'standard': re.compile(r'^([0-9]{6})\.(SH|SZ)$', re.IGNORECASE),
        'exchange_prefix': re.compile(r'^(SH|SZ)([0-9]{6})$', re.IGNORECASE),
        'pure_number': re.compile(r'^([0-9]{6})$'),
        'baostock': re.compile(r'^(sh|sz)\.([0-9]{6})$', re.IGNORECASE),
        'eastmoney': re.compile(r'^([01])\.([0-9]{6})$'),
        'tonghuashun': re.compile(r'^hs_([0-9]{6})$', re.IGNORECASE),
    }
    
    # 快速路径映射 - 常见代码的预计算结果
    _FAST_PATH_CACHE = {}
    _fast_path_lock = threading.Lock()
    
    # 交易所推断规则 - 预编译
    _EXCHANGE_RULES = {
        'SH': re.compile(r'^(60|68|90)\d{4}$'),
        'SZ': re.compile(r'^(00|30|20)\d{4}$'),
    }
    
    # 增强的缓存系统
    _cache = CodeConversionCache(l1_size=1000, l2_size=10000, enable_preheating=True)
    _cache_manager = CacheManager(_cache)
    
    # 性能监控系统
    _performance_monitor = PerformanceMonitor()
    
    # 错误处理和日志实例
    _error_handler = ErrorHandlingStrategy()
    _logger = CodeConversionLogger()
    _monitor = ConversionMonitor(_logger)
    
    # 启动缓存自动维护
    _cache_manager.start_auto_cleanup()
    
    # 性能统计
    _performance_stats = {
        'fast_path_hits': 0,
        'cache_hits': 0,
        'total_conversions': 0,
        'avg_conversion_time': 0.0,
    }
    _stats_lock = threading.Lock()
    
    @classmethod
    def parse_stock_code(cls, code: str) -> Tuple[str, str]:
        """
        解析股票代码，提取代码和交易所 - 性能优化版本
        
        Args:
            code: 股票代码（支持多种格式）
            
        Returns:
            (股票代码, 交易所) 元组
            
        Raises:
            ValidationError: 无效的股票代码格式
        """
        if not code or not isinstance(code, str):
            raise ValidationError("股票代码不能为空且必须为字符串")
        
        code_clean = code.strip().upper()
        
        # 快速路径检查 - 常见代码的预计算结果
        with cls._stats_lock:
            cls._performance_stats['total_conversions'] += 1
        
        if code_clean in cls._FAST_PATH_CACHE:
            with cls._stats_lock:
                cls._performance_stats['fast_path_hits'] += 1
            return cls._FAST_PATH_CACHE[code_clean]
        
        # 使用预编译的正则表达式进行快速匹配
        # 格式1: 000001.SZ (最常见格式，优先检查)
        match = cls._COMPILED_PATTERNS['standard'].match(code_clean)
        if match:
            stock_code, exchange = match.groups()
            result = (stock_code, exchange.upper())
            cls._add_to_fast_path_cache(code_clean, result)
            return result
        
        # 格式2: SZ000001
        match = cls._COMPILED_PATTERNS['exchange_prefix'].match(code_clean)
        if match:
            exchange, stock_code = match.groups()
            result = (stock_code, exchange.upper())
            cls._add_to_fast_path_cache(code_clean, result)
            return result
        
        # 格式3: 纯6位数字，需要根据代码推断交易所
        match = cls._COMPILED_PATTERNS['pure_number'].match(code_clean)
        if match:
            stock_code = match.group(1)
            exchange = cls._infer_exchange_fast(stock_code)
            result = (stock_code, exchange)
            cls._add_to_fast_path_cache(code_clean, result)
            return result
        
        raise ValidationError(f"无效的股票代码格式: {code}")
    
    @classmethod
    def _infer_exchange(cls, code: str) -> str:
        """
        根据股票代码推断交易所
        
        Args:
            code: 6位股票代码
            
        Returns:
            交易所代码 (SH/SZ)
            
        Raises:
            ExchangeInferenceError: 无法推断交易所
        """
        try:
            return ExchangeInferrer.infer_exchange(code)
        except ValidationError as e:
            # 转换为更具体的交易所推断错误
            raise ExchangeInferenceError(code, {'original_error': str(e)})
    
    @classmethod
    def _infer_exchange_fast(cls, code: str) -> str:
        """
        快速推断交易所 - 使用预编译正则表达式
        
        Args:
            code: 6位股票代码
            
        Returns:
            交易所代码 (SH/SZ)
            
        Raises:
            ExchangeInferenceError: 无法推断交易所
        """
        # 使用预编译的正则表达式进行快速匹配
        if cls._EXCHANGE_RULES['SH'].match(code):
            return 'SH'
        elif cls._EXCHANGE_RULES['SZ'].match(code):
            return 'SZ'
        else:
            # 无法推断，抛出异常
            raise ExchangeInferenceError(
                code, 
                {
                    'inference_method': 'fast_regex',
                    'checked_patterns': ['SH: 60/68/90xxxx', 'SZ: 00/30/20xxxx']
                },
                []  # 无明确建议
            )
    
    @classmethod
    def _add_to_fast_path_cache(cls, code: str, result: Tuple[str, str]) -> None:
        """
        添加到快速路径缓存
        
        Args:
            code: 原始代码
            result: 解析结果
        """
        with cls._fast_path_lock:
            # 限制快速路径缓存大小，避免内存泄漏
            if len(cls._FAST_PATH_CACHE) >= 1000:
                # 清理一半的缓存项（简单的LRU策略）
                items = list(cls._FAST_PATH_CACHE.items())
                cls._FAST_PATH_CACHE = dict(items[500:])
            
            cls._FAST_PATH_CACHE[code] = result
    
    @classmethod
    def clear_fast_path_cache(cls) -> None:
        """清空快速路径缓存"""
        with cls._fast_path_lock:
            cls._FAST_PATH_CACHE.clear()
    
    @classmethod
    def get_performance_stats(cls) -> Dict[str, Any]:
        """获取性能统计信息"""
        with cls._stats_lock:
            stats = cls._performance_stats.copy()
            
        # 计算命中率
        total = stats['total_conversions']
        if total > 0:
            stats['fast_path_hit_rate'] = stats['fast_path_hits'] / total
            stats['cache_hit_rate'] = stats['cache_hits'] / total
        else:
            stats['fast_path_hit_rate'] = 0.0
            stats['cache_hit_rate'] = 0.0
            
        return stats
    
    @classmethod
    def to_standard_format(cls, code: str) -> str:
        """
        转换为标准格式 (000001.SZ)
        
        Args:
            code: 原始股票代码
            
        Returns:
            标准格式的股票代码
        """
        stock_code, exchange = cls.parse_stock_code(code)
        return f"{stock_code}.{exchange}"
    
    @classmethod
    def to_baostock_format(cls, code: str) -> str:
        """
        转换为Baostock格式 (sh.600000)
        
        Args:
            code: 原始股票代码
            
        Returns:
            Baostock格式的股票代码
        """
        stock_code, exchange = cls.parse_stock_code(code)
        exchange_lower = cls.EXCHANGE_MAPPING.get(exchange, exchange.lower())
        return f"{exchange_lower}.{stock_code}"
    
    @classmethod
    def to_eastmoney_format(cls, code: str) -> str:
        """
        转换为东方财富格式 (1.600000)
        
        Args:
            code: 原始股票代码
            
        Returns:
            东方财富格式的股票代码
        """
        stock_code, exchange = cls.parse_stock_code(code)
        # 东方财富的交易所编码：1=上海，0=深圳
        exchange_code = '1' if exchange == 'SH' else '0'
        return f"{exchange_code}.{stock_code}"
    
    @classmethod
    def to_tonghuashun_format(cls, code: str) -> str:
        """
        转换为同花顺格式 (hs_600000)
        
        Args:
            code: 原始股票代码
            
        Returns:
            同花顺格式的股票代码
        """
        stock_code, exchange = cls.parse_stock_code(code)
        return f"hs_{stock_code}"
    
    @classmethod
    def from_baostock_format(cls, code: str) -> str:
        """
        从Baostock格式转换为标准格式
        
        Args:
            code: Baostock格式代码 (sh.600000)
            
        Returns:
            标准格式代码 (600000.SH)
        """
        match = re.match(r'^(sh|sz)\.([0-9]{6})$', code.lower())
        if not match:
            raise ValidationError(f"无效的Baostock格式代码: {code}")
        
        exchange_lower, stock_code = match.groups()
        exchange = cls.REVERSE_EXCHANGE_MAPPING.get(exchange_lower, exchange_lower.upper())
        return f"{stock_code}.{exchange}"
    
    @classmethod
    def from_eastmoney_format(cls, code: str) -> str:
        """
        从东方财富格式转换为标准格式
        
        Args:
            code: 东方财富格式代码 (1.600000)
            
        Returns:
            标准格式代码 (600000.SH)
        """
        match = re.match(r'^([01])\.([0-9]{6})$', code)
        if not match:
            raise ValidationError(f"无效的东方财富格式代码: {code}")
        
        exchange_code, stock_code = match.groups()
        exchange = 'SH' if exchange_code == '1' else 'SZ'
        return f"{stock_code}.{exchange}"
    
    @classmethod
    def from_tonghuashun_format(cls, code: str) -> str:
        """
        从同花顺格式转换为标准格式
        
        Args:
            code: 同花顺格式代码 (hs_600000)
            
        Returns:
            标准格式代码 (600000.SH)
        """
        match = re.match(r'^hs_([0-9]{6})$', code.lower())
        if not match:
            raise ValidationError(f"无效的同花顺格式代码: {code}")
        
        stock_code = match.group(1)
        exchange = cls._infer_exchange(stock_code)
        return f"{stock_code}.{exchange}"
    
    @classmethod
    def convert_code(cls, code: str, target_format: str) -> str:
        """
        转换股票代码到指定格式
        
        Args:
            code: 原始股票代码
            target_format: 目标格式 ('standard', 'baostock', 'eastmoney', 'tonghuashun')
            
        Returns:
            转换后的股票代码
            
        Raises:
            InvalidCodeFormatError: 无效的代码格式
            UnsupportedFormatError: 不支持的目标格式
            ExchangeInferenceError: 无法推断交易所
        """
        if not code or not isinstance(code, str):
            raise InvalidCodeFormatError(
                str(code) if code else "None",
                cls.get_supported_formats(),
                ["代码不能为空且必须为字符串"]
            )
        
        if not target_format or not isinstance(target_format, str):
            raise UnsupportedFormatError(
                str(target_format) if target_format else "None",
                cls.get_supported_formats()
            )
        
        # 检查目标格式是否支持
        supported_formats = cls.get_supported_formats()
        if target_format not in supported_formats:
            raise UnsupportedFormatError(target_format, supported_formats)
        
        # 使用缓存
        cache_key = f"convert:{code.strip()}:{target_format}"
        
        def compute_conversion():
            try:
                # 如果目标格式是standard，直接使用normalize_code
                if target_format == 'standard':
                    return cls.normalize_code(code)
                
                # 对于其他格式，先标准化输入代码，然后转换
                standard_code = cls.normalize_code(code)
                
                format_converters = {
                    'baostock': cls.to_baostock_format,
                    'eastmoney': cls.to_eastmoney_format,
                    'tonghuashun': cls.to_tonghuashun_format,
                }
                
                converter = format_converters.get(target_format)
                if not converter:
                    raise UnsupportedFormatError(target_format, supported_formats)
                
                return converter(standard_code)
                
            except (InvalidCodeFormatError, UnsupportedFormatError, ExchangeInferenceError):
                # 重新抛出特定的错误类型
                raise
            except ValidationError as e:
                # 转换通用ValidationError为更具体的错误
                raise InvalidCodeFormatError(
                    code,
                    supported_formats,
                    [str(e)] + PatternMatcher.suggest_corrections(code)
                )
        
        return cls._get_cached_or_compute(cache_key, compute_conversion)
    
    @classmethod
    def get_cache_stats(cls) -> Dict[str, Any]:
        """
        获取详细的缓存统计信息
        
        Returns:
            缓存统计信息字典
        """
        return cls._cache.get_stats()
    
    @classmethod
    def clear_cache(cls) -> None:
        """清空转换缓存"""
        cls._cache.clear()
    
    @classmethod
    def get_cache_health(cls) -> Dict[str, Any]:
        """获取缓存健康状态"""
        return cls._cache_manager.get_cache_health()
    
    @classmethod
    def optimize_cache(cls) -> Dict[str, Any]:
        """优化缓存配置"""
        return cls._cache_manager.optimize_cache_sizes()
    
    @classmethod
    def perform_cache_maintenance(cls) -> Dict[str, Any]:
        """执行缓存维护"""
        return cls._cache_manager.perform_maintenance()
    
    @classmethod
    def get_hot_keys(cls, limit: int = 10) -> List[Tuple[str, float]]:
        """获取热点缓存键"""
        return cls._cache.get_hot_keys(limit)
    
    @classmethod
    def cleanup_expired_cache(cls) -> int:
        """清理过期缓存条目"""
        return cls._cache.cleanup_expired()
    
    @classmethod
    def get_performance_summary(cls) -> Dict[str, Any]:
        """获取性能摘要"""
        return cls._performance_monitor.get_performance_summary()
    
    @classmethod
    def reset_performance_metrics(cls) -> None:
        """重置性能指标"""
        cls._performance_monitor.reset_metrics()
        with cls._stats_lock:
            cls._performance_stats = {
                'fast_path_hits': 0,
                'cache_hits': 0,
                'total_conversions': 0,
                'avg_conversion_time': 0.0,
            }
    
    @classmethod
    def run_performance_benchmark(cls, test_types: List[str] = None) -> Dict[str, Any]:
        """运行性能基准测试"""
        benchmark = PerformanceBenchmark(cls)
        
        if test_types is None:
            return benchmark.run_full_benchmark_suite()
        
        results = {}
        for test_type in test_types:
            if test_type == 'single_conversion':
                results[test_type] = benchmark.run_single_conversion_benchmark()
            elif test_type == 'batch_conversion':
                results[test_type] = benchmark.run_batch_conversion_benchmark()
            elif test_type == 'cache_performance':
                results[test_type] = benchmark.run_cache_performance_benchmark()
            elif test_type == 'memory_usage':
                results[test_type] = benchmark.run_memory_usage_benchmark()
            elif test_type == 'concurrent':
                results[test_type] = benchmark.run_concurrent_benchmark()
        
        return results
    
    @classmethod
    def generate_performance_report(cls, output_file: str = None) -> str:
        """生成性能报告"""
        benchmark = PerformanceBenchmark(cls)
        benchmark.run_full_benchmark_suite()
        return benchmark.generate_report(output_file)
    
    @classmethod
    def identify_code_format(cls, code: str) -> Optional[str]:
        """
        识别股票代码格式
        
        Args:
            code: 股票代码
            
        Returns:
            格式名称，如果无法识别返回None
        """
        return PatternMatcher.identify_format(code)
    
    @classmethod
    def validate_code_format(cls, code: str, expected_format: str) -> bool:
        """
        验证代码是否符合指定格式
        
        Args:
            code: 股票代码
            expected_format: 期望的格式
            
        Returns:
            是否符合格式
        """
        return PatternMatcher.validate_format(code, expected_format)
    
    @classmethod
    def get_format_suggestions(cls, code: str) -> List[str]:
        """
        获取代码可能的格式建议
        
        Args:
            code: 股票代码
            
        Returns:
            可能的格式列表
        """
        return PatternMatcher.get_format_suggestions(code)
    
    @classmethod
    def suggest_code_corrections(cls, code: str) -> List[str]:
        """
        为无效代码提供修正建议
        
        Args:
            code: 无效的股票代码
            
        Returns:
            修正建议列表
        """
        return PatternMatcher.suggest_corrections(code)
    
    @classmethod
    def get_supported_formats(cls) -> List[str]:
        """
        获取支持的代码格式列表
        
        Returns:
            支持的格式列表
        """
        return list(PatternMatcher.PATTERNS.keys())
    
    @classmethod
    def get_error_handler(cls) -> ErrorHandlingStrategy:
        """获取错误处理策略实例"""
        return cls._error_handler
    
    @classmethod
    def get_logger(cls) -> CodeConversionLogger:
        """获取日志记录器实例"""
        return cls._logger
    
    @classmethod
    def get_monitor(cls) -> ConversionMonitor:
        """获取监控器实例"""
        return cls._monitor
    
    @classmethod
    def get_health_status(cls) -> Dict[str, Any]:
        """获取系统健康状态"""
        return cls._monitor.check_health()
    
    @classmethod
    def get_conversion_stats(cls) -> Dict[str, Any]:
        """获取转换统计信息"""
        return cls._logger.get_conversion_stats()
    
    @classmethod
    def reset_stats(cls):
        """重置统计信息"""
        cls._logger.reset_stats()
    
    @classmethod
    def _get_cached_or_compute(cls, cache_key: str, compute_func) -> str:
        """
        从缓存获取结果或计算新结果 - 增强版本
        
        Args:
            cache_key: 缓存键
            compute_func: 计算函数
            
        Returns:
            转换结果
        """
        start_time = time.time()
        
        # 尝试从缓存获取
        cached_result = cls._cache.get(cache_key)
        if cached_result is not None:
            # 更新缓存命中统计
            with cls._stats_lock:
                cls._performance_stats['cache_hits'] += 1
            return cached_result
        
        # 计算新结果
        result = compute_func()
        
        # 存储到缓存
        cls._cache.put(cache_key, result)
        
        # 更新性能统计
        computation_time = time.time() - start_time
        with cls._stats_lock:
            cls._performance_stats['avg_conversion_time'] = (
                (cls._performance_stats['avg_conversion_time'] * cls._performance_stats['total_conversions'] + computation_time) /
                (cls._performance_stats['total_conversions'] + 1)
            )
        
        return result
    
    @classmethod
    def normalize_code(cls, code: str) -> str:
        """
        标准化股票代码（转换为标准格式）
        
        Args:
            code: 任意格式的股票代码
            
        Returns:
            标准格式的股票代码 (000001.SZ)
            
        Raises:
            InvalidCodeFormatError: 无效的代码格式
            ExchangeInferenceError: 无法推断交易所
        """
        start_time = time.time()
        
        try:
            if not code or not isinstance(code, str):
                error = InvalidCodeFormatError(
                    str(code) if code else "None",
                    cls.get_supported_formats(),
                    ["代码不能为空且必须为字符串"]
                )
                cls._logger.log_conversion_error(
                    str(code) if code else "None", error,
                    context={'validation_stage': 'input_check'}
                )
                raise error
            
            # 使用缓存
            cache_key = f"normalize:{code.strip()}"
            cached_result = cls._cache.get(cache_key)
            
            if cached_result is not None:
                execution_time = time.time() - start_time
                cls._logger.log_conversion(
                    code, cached_result, 'unknown', 'standard',
                    execution_time, cached=True
                )
                return cached_result
            
            def compute_normalization():
                # 尝试不同的格式解析
                input_code = code.strip()
                
                # 首先进行详细验证
                is_valid, issues, suggestions = CodeValidationHelper.validate_and_suggest(input_code)
                
                if not is_valid:
                    # 尝试错误恢复
                    recovery_result = cls._error_handler.handle_invalid_format(
                        input_code, {'operation': 'normalize'}
                    )
                    
                    # 如果有自动修正建议，尝试使用
                    if recovery_result['auto_corrections']:
                        best_correction = recovery_result['auto_corrections'][0]
                        if best_correction['confidence'] > 0.8:
                            cls._logger.log_recovery_attempt(
                                input_code, 'auto_correction', True, 
                                best_correction['corrected_code']
                            )
                            return cls.normalize_code(best_correction['corrected_code'])
                    
                    error = InvalidCodeFormatError(
                        input_code,
                        cls.get_supported_formats(),
                        issues + suggestions
                    )
                    cls._logger.log_conversion_error(
                        input_code, error, context={'validation_stage': 'format_check'}
                    )
                    raise error
                
                # 使用PatternMatcher识别格式
                detected_format = PatternMatcher.identify_format(input_code)
                
                if detected_format:
                    try:
                        if detected_format == 'standard':
                            return input_code.upper()
                        elif detected_format == 'baostock':
                            return cls.from_baostock_format(input_code.lower())
                        elif detected_format == 'eastmoney':
                            return cls.from_eastmoney_format(input_code)
                        elif detected_format == 'tonghuashun':
                            return cls.from_tonghuashun_format(input_code.lower())
                        elif detected_format in ['exchange_prefix', 'pure_number']:
                            return cls.to_standard_format(input_code)
                    except ExchangeInferenceError as e:
                        # 尝试交易所推断恢复
                        recovery_result = cls._error_handler.handle_exchange_inference_failure(
                            input_code, {'detected_format': detected_format}
                        )
                        
                        # 如果有推荐的交易所，尝试使用
                        if recovery_result['recommendations']:
                            best_rec = recovery_result['recommendations'][0]
                            if best_rec['confidence'] > 0.8:
                                cls._logger.log_recovery_attempt(
                                    input_code, 'exchange_inference', True,
                                    best_rec['suggested_code']
                                )
                                return best_rec['suggested_code']
                        
                        cls._logger.log_conversion_error(
                            input_code, e, detected_format, 'standard',
                            context={'inference_details': recovery_result}
                        )
                        raise e
                    except ValidationError as e:
                        # 转换为更具体的错误类型
                        error = InvalidCodeFormatError(
                            input_code,
                            cls.get_supported_formats(),
                            [str(e)] + PatternMatcher.suggest_corrections(input_code)
                        )
                        cls._logger.log_conversion_error(
                            input_code, error, detected_format, 'standard'
                        )
                        raise error
                
                # 如果自动识别失败，尝试标准解析
                try:
                    return cls.to_standard_format(input_code)
                except ValidationError as e:
                    # 提供更好的错误信息和建议
                    suggestions = PatternMatcher.suggest_corrections(input_code)
                    error = InvalidCodeFormatError(
                        input_code,
                        cls.get_supported_formats(),
                        [str(e)] + suggestions
                    )
                    cls._logger.log_conversion_error(
                        input_code, error, context={'fallback_attempt': True}
                    )
                    raise error
            
            result = compute_normalization()
            
            # 存储到缓存
            cls._cache.put(cache_key, result)
            
            # 记录成功的转换
            execution_time = time.time() - start_time
            cls._logger.log_conversion(
                code, result, 'auto_detected', 'standard',
                execution_time, cached=False
            )
            
            # 记录性能监控数据
            cls._performance_monitor.record_conversion_time(
                'normalize', execution_time, cached=False, success=True
            )
            
            return result
            
        except CodeConversionError:
            # 重新抛出代码转换相关错误
            raise
        except Exception as e:
            # 处理意外错误
            execution_time = time.time() - start_time
            cls._logger.log_conversion_error(
                code, e, context={'unexpected_error': True, 'execution_time': execution_time}
            )
            raise ValidationError(f"代码标准化过程中发生意外错误: {str(e)}")
    
    @classmethod
    def batch_normalize_codes(cls, codes: List[str], parallel: bool = True, max_workers: int = None) -> List[str]:
        """
        批量标准化股票代码 - 支持并行处理
        
        Args:
            codes: 股票代码列表
            parallel: 是否使用并行处理
            max_workers: 最大工作线程数，None表示自动选择
            
        Returns:
            标准化后的股票代码列表
            
        Raises:
            ValidationError: 如果输入不是列表
            BatchConversionError: 如果批量转换中有失败项
        """
        if not isinstance(codes, list):
            raise ValidationError("输入必须是股票代码列表")
        
        if not codes:
            return []
        
        start_time = time.time()
        
        # 对于小批量数据，不使用并行处理
        if len(codes) < 50 or not parallel:
            return cls._batch_normalize_sequential(codes, start_time)
        
        # 并行处理大批量数据
        return cls._batch_normalize_parallel(codes, start_time, max_workers)
    
    @classmethod
    def _batch_normalize_sequential(cls, codes: List[str], start_time: float) -> List[str]:
        """顺序处理批量标准化"""
        results = []
        failed_items = []
        
        for i, code in enumerate(codes):
            try:
                normalized = cls.normalize_code(code)
                results.append(normalized)
            except CodeConversionError as e:
                # 记录失败项
                failed_items.append((code, e))
                results.append(code)  # 保留原始代码
            except Exception as e:
                # 处理意外错误
                failed_items.append((code, e))
                results.append(code)
        
        execution_time = time.time() - start_time
        successful_count = len(codes) - len(failed_items)
        
        # 记录批量转换结果
        cls._logger.log_batch_conversion(
            len(codes), successful_count, len(failed_items), execution_time,
            {'parallel': False}
        )
        
        # 记录性能监控数据
        cls._performance_monitor.record_batch_conversion(
            len(codes), execution_time, successful_count, parallel=False
        )
        
        # 处理失败项
        cls._handle_batch_failures(failed_items, successful_count, len(codes))
        
        return results
    
    @classmethod
    def _batch_normalize_parallel(cls, codes: List[str], start_time: float, max_workers: int = None) -> List[str]:
        """并行处理批量标准化"""
        if max_workers is None:
            # 自动选择工作线程数：CPU核心数的2倍，但不超过代码数量
            import os
            max_workers = min(len(codes), os.cpu_count() * 2)
        
        results = [None] * len(codes)
        failed_items = []
        
        def normalize_single(index_code_pair):
            index, code = index_code_pair
            try:
                normalized = cls.normalize_code(code)
                return index, normalized, None
            except Exception as e:
                return index, code, e
        
        # 使用线程池进行并行处理
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 提交所有任务
            future_to_index = {
                executor.submit(normalize_single, (i, code)): i 
                for i, code in enumerate(codes)
            }
            
            # 收集结果
            for future in concurrent.futures.as_completed(future_to_index):
                try:
                    index, result, error = future.result()
                    results[index] = result
                    
                    if error is not None:
                        failed_items.append((codes[index], error))
                        
                except Exception as e:
                    # 处理执行异常
                    index = future_to_index[future]
                    failed_items.append((codes[index], e))
                    results[index] = codes[index]
        
        execution_time = time.time() - start_time
        successful_count = len(codes) - len(failed_items)
        
        # 记录批量转换结果
        cls._logger.log_batch_conversion(
            len(codes), successful_count, len(failed_items), execution_time,
            {'parallel': True, 'max_workers': max_workers}
        )
        
        # 记录性能监控数据
        cls._performance_monitor.record_batch_conversion(
            len(codes), execution_time, successful_count, 
            parallel=True, max_workers=max_workers
        )
        
        # 处理失败项
        cls._handle_batch_failures(failed_items, successful_count, len(codes))
        
        return results
    
    @classmethod
    def _handle_batch_failures(cls, failed_items: List[Tuple[str, Exception]], 
                              successful_count: int, total_count: int) -> None:
        """处理批量转换失败项"""
        if not failed_items:
            return
            
        # 使用错误处理策略分析失败情况
        error_analysis = cls._error_handler.handle_batch_conversion_errors(
            failed_items, successful_count, {'operation': 'batch_normalize'}
        )
        
        # 如果失败率过高，抛出批量转换错误
        failure_rate = len(failed_items) / total_count
        if failure_rate > 0.5:  # 失败率超过50%
            raise BatchConversionError(failed_items, successful_count, total_count)
        else:
            # 失败率较低，只记录警告
            cls._logger.logger.warning(
                f"批量标准化部分失败: {len(failed_items)}/{total_count} 个代码失败"
            )
    
    @classmethod
    def batch_convert_codes(cls, codes: List[str], target_format: str, parallel: bool = True, max_workers: int = None) -> List[str]:
        """
        批量转换股票代码到指定格式 - 支持并行处理
        
        Args:
            codes: 股票代码列表
            target_format: 目标格式
            parallel: 是否使用并行处理
            max_workers: 最大工作线程数
            
        Returns:
            转换后的股票代码列表
            
        Raises:
            ValidationError: 如果输入不是列表或包含无效代码
        """
        if not isinstance(codes, list):
            raise ValidationError("输入必须是股票代码列表")
        
        if not codes:
            return []
        
        if not target_format or not isinstance(target_format, str):
            raise ValidationError("目标格式不能为空且必须为字符串")
        
        start_time = time.time()
        
        # 对于小批量数据，不使用并行处理
        if len(codes) < 50 or not parallel:
            return cls._batch_convert_sequential(codes, target_format, start_time)
        
        # 并行处理大批量数据
        return cls._batch_convert_parallel(codes, target_format, start_time, max_workers)
    
    @classmethod
    def _batch_convert_sequential(cls, codes: List[str], target_format: str, start_time: float) -> List[str]:
        """顺序处理批量转换"""
        results = []
        errors = []
        
        for i, code in enumerate(codes):
            try:
                converted = cls.convert_code(code, target_format)
                results.append(converted)
            except Exception as e:
                error_info = {
                    'index': i,
                    'code': code,
                    'error': str(e)
                }
                errors.append(error_info)
                # 对于批量处理，我们继续处理其他代码
                results.append(None)
        
        execution_time = time.time() - start_time
        
        # 记录批量转换结果
        successful_count = len([r for r in results if r is not None])
        cls._logger.log_batch_conversion(
            len(codes), successful_count, len(errors), execution_time,
            {'parallel': True, 'max_workers': max_workers}
        )
        
        # 处理错误情况
        return cls._handle_batch_convert_results(results, errors)
    
    @classmethod
    def _batch_convert_parallel(cls, codes: List[str], target_format: str, 
                               start_time: float, max_workers: int = None) -> List[str]:
        """并行处理批量转换"""
        if max_workers is None:
            import os
            max_workers = min(len(codes), os.cpu_count() * 2)
        
        results = [None] * len(codes)
        errors = []
        
        def convert_single(index_code_pair):
            index, code = index_code_pair
            try:
                converted = cls.convert_code(code, target_format)
                return index, converted, None
            except Exception as e:
                return index, None, {'index': index, 'code': code, 'error': str(e)}
        
        # 使用线程池进行并行处理
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 提交所有任务
            future_to_index = {
                executor.submit(convert_single, (i, code)): i 
                for i, code in enumerate(codes)
            }
            
            # 收集结果
            for future in concurrent.futures.as_completed(future_to_index):
                try:
                    index, result, error = future.result()
                    results[index] = result
                    
                    if error is not None:
                        errors.append(error)
                        
                except Exception as e:
                    # 处理执行异常
                    index = future_to_index[future]
                    errors.append({
                        'index': index,
                        'code': codes[index],
                        'error': str(e)
                    })
                    results[index] = None
        
        execution_time = time.time() - start_time
        
        # 记录批量转换结果
        successful_count = len([r for r in results if r is not None])
        cls._logger.log_batch_conversion(
            len(codes), successful_count, len(errors), execution_time,
            parallel=True, max_workers=max_workers
        )
        
        # 处理错误情况
        return cls._handle_batch_convert_results(results, errors)
    
    @classmethod
    def _handle_batch_convert_results(cls, results: List[Any], errors: List[Dict[str, Any]]) -> List[str]:
        """处理批量转换结果"""
        if errors:
            # 过滤掉None值，只返回成功的结果
            valid_results = [r for r in results if r is not None]
            if not valid_results:
                # 如果所有代码都失败了，抛出异常
                error_msg = f"批量转换失败，共{len(errors)}个错误: " + "; ".join([f"索引{e['index']}: {e['error']}" for e in errors[:3]])
                if len(errors) > 3:
                    error_msg += f" 等{len(errors)}个错误"
                raise ValidationError(error_msg)
            
            # 部分成功的情况，返回成功的结果
            return valid_results
        
        return results
    
    @classmethod
    def batch_convert_codes_with_errors(cls, codes: List[str], target_format: str = 'standard') -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        批量转换股票代码，返回成功结果和错误信息
        
        Args:
            codes: 股票代码列表
            target_format: 目标格式，默认为'standard'
            
        Returns:
            (成功结果列表, 错误信息列表) 元组
        """
        if not isinstance(codes, list):
            raise ValidationError("输入必须是股票代码列表")
        
        if not codes:
            return [], []
        
        results = []
        errors = []
        
        for i, code in enumerate(codes):
            try:
                if target_format == 'standard':
                    converted = cls.normalize_code(code)
                else:
                    converted = cls.convert_code(code, target_format)
                results.append({
                    'index': i,
                    'original': code,
                    'converted': converted,
                    'success': True
                })
            except Exception as e:
                error_info = {
                    'index': i,
                    'original': code,
                    'error': str(e),
                    'success': False
                }
                
                # 如果是我们的自定义异常，添加更多信息
                if isinstance(e, CodeConversionError):
                    error_info.update({
                        'error_type': type(e).__name__,
                        'error_code': e.error_code,
                        'suggestions': e.suggestions,
                        'user_friendly_message': e.get_user_friendly_message()
                    })
                
                errors.append(error_info)
        
        return results, errors
    
    @classmethod
    def validate_code_with_details(cls, code: str) -> Dict[str, Any]:
        """
        验证股票代码并返回详细信息
        
        Args:
            code: 股票代码
            
        Returns:
            详细的验证结果字典
        """
        return CodeValidationHelper.get_detailed_validation_result(code)
    
    @classmethod
    def get_format_help(cls, format_name: str = None) -> Dict[str, Any]:
        """
        获取格式帮助信息
        
        Args:
            format_name: 格式名称，如果为None则返回所有格式的帮助
            
        Returns:
            格式帮助信息字典
        """
        format_help = {
            'standard': {
                'name': '标准格式',
                'pattern': '000001.SZ',
                'description': '6位数字代码 + 点号 + 交易所代码(SH/SZ)',
                'examples': ['000001.SZ', '600000.SH', '300001.SZ'],
                'usage': '最常用的格式，推荐使用'
            },
            'baostock': {
                'name': 'Baostock格式',
                'pattern': 'sz.000001',
                'description': '交易所代码(sh/sz) + 点号 + 6位数字代码',
                'examples': ['sz.000001', 'sh.600000', 'sz.300001'],
                'usage': 'Baostock数据源使用的格式'
            },
            'eastmoney': {
                'name': '东方财富格式',
                'pattern': '0.000001',
                'description': '交易所编号(0深圳/1上海) + 点号 + 6位数字代码',
                'examples': ['0.000001', '1.600000', '0.300001'],
                'usage': '东方财富数据源使用的格式'
            },
            'tonghuashun': {
                'name': '同花顺格式',
                'pattern': 'hs_000001',
                'description': 'hs_ + 6位数字代码',
                'examples': ['hs_000001', 'hs_600000', 'hs_300001'],
                'usage': '同花顺数据源使用的格式'
            },
            'exchange_prefix': {
                'name': '交易所前缀格式',
                'pattern': 'SZ000001',
                'description': '交易所代码(SH/SZ) + 6位数字代码',
                'examples': ['SZ000001', 'SH600000', 'SZ300001'],
                'usage': '某些系统使用的格式'
            },
            'pure_number': {
                'name': '纯数字格式',
                'pattern': '000001',
                'description': '6位数字代码（需要自动推断交易所）',
                'examples': ['000001', '600000', '300001'],
                'usage': '简化格式，系统会自动推断交易所'
            }
        }
        
        if format_name:
            return format_help.get(format_name, {})
        
        return format_help
    
    @classmethod
    def suggest_auto_correction(cls, code: str) -> Dict[str, Any]:
        """
        为无效代码提供自动修正建议
        
        Args:
            code: 无效的股票代码
            
        Returns:
            自动修正建议字典
        """
        if not code or not isinstance(code, str):
            return {
                'original': code,
                'can_auto_correct': False,
                'suggestions': ["请提供有效的股票代码字符串"],
                'corrections': []
            }
        
        code = code.strip()
        corrections = []
        
        # 尝试各种自动修正
        
        # 1. 大小写修正
        if re.match(r'^[0-9]{6}\.(sh|sz)$', code.lower()):
            corrections.append({
                'type': 'case_correction',
                'original': code,
                'corrected': code.upper(),
                'confidence': 0.95,
                'description': '修正大小写'
            })
        
        # 2. 缺少交易所后缀
        if re.match(r'^[0-9]{6}$', code):
            try:
                exchange = cls._infer_exchange(code)
                corrections.append({
                    'type': 'add_exchange',
                    'original': code,
                    'corrected': f"{code}.{exchange}",
                    'confidence': 0.8,
                    'description': f'添加推断的交易所后缀: {exchange}'
                })
            except:
                corrections.extend([
                    {
                        'type': 'add_exchange_option',
                        'original': code,
                        'corrected': f"{code}.SH",
                        'confidence': 0.5,
                        'description': '添加上海证券交易所后缀'
                    },
                    {
                        'type': 'add_exchange_option',
                        'original': code,
                        'corrected': f"{code}.SZ",
                        'confidence': 0.5,
                        'description': '添加深圳证券交易所后缀'
                    }
                ])
        
        # 3. 格式转换
        if re.match(r'^(SH|SZ)[0-9]{6}$', code.upper()):
            match = re.match(r'^(SH|SZ)([0-9]{6})$', code.upper())
            if match:
                exchange, stock_code = match.groups()
                corrections.append({
                    'type': 'format_conversion',
                    'original': code,
                    'corrected': f"{stock_code}.{exchange}",
                    'confidence': 0.9,
                    'description': '转换为标准格式'
                })
        
        # 4. 去除多余字符
        clean_code = re.sub(r'[^a-zA-Z0-9.]', '', code)
        if clean_code != code and clean_code:
            try:
                # 尝试验证清理后的代码
                cls.normalize_code(clean_code)
                corrections.append({
                    'type': 'clean_characters',
                    'original': code,
                    'corrected': clean_code,
                    'confidence': 0.7,
                    'description': '移除无效字符'
                })
            except:
                pass
        
        return {
            'original': code,
            'can_auto_correct': len(corrections) > 0,
            'suggestions': PatternMatcher.suggest_corrections(code),
            'corrections': sorted(corrections, key=lambda x: x['confidence'], reverse=True)
        }
    
    @classmethod
    def get_validation_help(cls) -> Dict[str, Any]:
        """
        获取代码验证帮助信息
        
        Returns:
            验证帮助信息字典
        """
        return {
            'supported_formats': cls.get_format_help(),
            'validation_rules': {
                'length': '代码总长度应在6-20个字符之间',
                'characters': '只能包含字母、数字、点号和下划线',
                'structure': '必须包含6位数字作为股票代码',
                'exchange': '需要明确指定交易所或使用可推断的格式'
            },
            'common_errors': {
                'empty_code': {
                    'description': '代码为空',
                    'solution': '请提供有效的股票代码'
                },
                'invalid_length': {
                    'description': '代码长度不正确',
                    'solution': '检查代码格式，确保包含完整的股票代码和交易所信息'
                },
                'invalid_characters': {
                    'description': '包含无效字符',
                    'solution': '只使用字母、数字、点号和下划线'
                },
                'missing_exchange': {
                    'description': '缺少交易所信息',
                    'solution': '添加交易所后缀(.SH/.SZ)或使用包含交易所信息的格式'
                },
                'case_sensitivity': {
                    'description': '大小写错误',
                    'solution': '交易所代码使用大写(SH/SZ)'
                }
            },
            'examples': {
                'valid': [
                    '000001.SZ - 平安银行(深圳)',
                    '600000.SH - 浦发银行(上海)',
                    'sz.000001 - Baostock格式',
                    '0.000001 - 东方财富格式',
                    'hs_000001 - 同花顺格式'
                ],
                'invalid': [
                    '000001 - 缺少交易所后缀',
                    '000001.sz - 交易所代码应为大写',
                    'invalid_code - 不是有效的股票代码格式',
                    '12345 - 代码长度不足6位'
                ]
            }
        }


# 便捷函数
def normalize_stock_code(code: str) -> str:
    """标准化股票代码"""
    return StockCodeConverter.normalize_code(code)


def convert_stock_code(code: str, target_format: str) -> str:
    """转换股票代码格式"""
    return StockCodeConverter.convert_code(code, target_format)


def batch_normalize_codes(codes: List[str]) -> List[str]:
    """批量标准化股票代码"""
    return StockCodeConverter.batch_normalize_codes(codes)


def batch_convert_codes(codes: List[str], target_format: str) -> List[str]:
    """批量转换股票代码"""
    return StockCodeConverter.batch_convert_codes(codes, target_format)