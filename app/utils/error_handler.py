"""
统一错误处理系统

为MT5交易系统提供统一、强大、可扩展的错误处理机制
与现有错误处理并行工作，渐进式替换
"""

import functools
import traceback
import sys
from typing import Any, Callable, Dict, List, Optional, Type, Union
from enum import Enum
from datetime import datetime
import json

# 简化版logger，避免相对导入问题
import logging

# 创建简单的logger
logger = logging.getLogger(__name__)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


class ErrorLevel(Enum):
    """错误级别枚举"""
    DEBUG = "DEBUG"          # 调试信息
    INFO = "INFO"            # 一般信息  
    WARNING = "WARNING"      # 警告
    ERROR = "ERROR"          # 错误
    CRITICAL = "CRITICAL"    # 严重错误
    FATAL = "FATAL"          # 致命错误


class ErrorCategory(Enum):
    """错误分类枚举"""
    # 连接相关
    CONNECTION = "CONNECTION"          # MT5连接错误
    NETWORK = "NETWORK"               # 网络错误
    
    # 交易相关
    TRADING = "TRADING"               # 交易操作错误
    ORDER = "ORDER"                   # 订单错误
    POSITION = "POSITION"             # 持仓错误
    
    # 数据相关
    DATABASE = "DATABASE"             # 数据库错误
    FILE_IO = "FILE_IO"              # 文件读写错误
    DATA_SYNC = "DATA_SYNC"          # 数据同步错误
    
    # 配置相关
    CONFIG = "CONFIG"                 # 配置错误
    VALIDATION = "VALIDATION"         # 验证错误
    
    # 系统相关
    SYSTEM = "SYSTEM"                 # 系统错误
    PERMISSION = "PERMISSION"         # 权限错误
    RESOURCE = "RESOURCE"             # 资源错误
    
    # UI相关
    GUI = "GUI"                       # 界面错误
    USER_INPUT = "USER_INPUT"         # 用户输入错误
    
    # 业务逻辑
    BUSINESS = "BUSINESS"             # 业务逻辑错误
    RISK_CONTROL = "RISK_CONTROL"     # 风控错误
    
    # 其他
    UNKNOWN = "UNKNOWN"               # 未知错误


class ErrorContext:
    """错误上下文信息"""
    
    def __init__(self, 
                 operation: str = "",
                 component: str = "",
                 user_id: Optional[str] = None,
                 symbol: Optional[str] = None,
                 order_id: Optional[str] = None,
                 **kwargs):
        self.operation = operation       # 执行的操作
        self.component = component       # 出错的组件
        self.user_id = user_id          # 用户ID
        self.symbol = symbol            # 交易品种
        self.order_id = order_id        # 订单ID
        self.timestamp = datetime.now()  # 错误时间
        self.extra = kwargs             # 额外信息
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'operation': self.operation,
            'component': self.component,
            'user_id': self.user_id,
            'symbol': self.symbol,
            'order_id': self.order_id,
            'timestamp': self.timestamp.isoformat(),
            'extra': self.extra
        }


class MT5Error(Exception):
    """MT5系统基础异常类"""
    
    def __init__(self, 
                 message: str,
                 category: ErrorCategory = ErrorCategory.UNKNOWN,
                 level: ErrorLevel = ErrorLevel.ERROR,
                 context: Optional[ErrorContext] = None,
                 original_exception: Optional[Exception] = None,
                 recoverable: bool = True,
                 user_message: Optional[str] = None):
        super().__init__(message)
        self.category = category
        self.level = level
        self.context = context or ErrorContext()
        self.original_exception = original_exception
        self.recoverable = recoverable           # 是否可恢复
        self.user_message = user_message or message  # 用户友好的错误信息
        self.error_id = self._generate_error_id()
    
    def _generate_error_id(self) -> str:
        """生成唯一错误ID"""
        from hashlib import sha256
        content = f"{self.category.value}_{self.context.timestamp}_{str(self)}"
        return sha256(content.encode()).hexdigest()[:8]
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'error_id': self.error_id,
            'message': str(self),
            'user_message': self.user_message,
            'category': self.category.value,
            'level': self.level.value,
            'recoverable': self.recoverable,
            'context': self.context.to_dict(),
            'original_exception': str(self.original_exception) if self.original_exception else None,
            'traceback': traceback.format_exc() if self.original_exception else None
        }


# === 具体异常类 ===

class ConnectionError(MT5Error):
    """连接相关异常"""
    def __init__(self, message: str, **kwargs):
        super().__init__(message, category=ErrorCategory.CONNECTION, **kwargs)


class TradingError(MT5Error):
    """交易相关异常"""
    def __init__(self, message: str, **kwargs):
        super().__init__(message, category=ErrorCategory.TRADING, **kwargs)


class DatabaseError(MT5Error):
    """数据库相关异常"""
    def __init__(self, message: str, **kwargs):
        super().__init__(message, category=ErrorCategory.DATABASE, **kwargs)


class ConfigError(MT5Error):
    """配置相关异常"""
    def __init__(self, message: str, **kwargs):
        super().__init__(message, category=ErrorCategory.CONFIG, **kwargs)


class RiskControlError(MT5Error):
    """风控相关异常"""
    def __init__(self, message: str, **kwargs):
        super().__init__(message, category=ErrorCategory.RISK_CONTROL, level=ErrorLevel.WARNING, **kwargs)


# === 错误处理器 ===

class ErrorHandler:
    """统一错误处理器"""
    
    def __init__(self):
        self._error_history: List[MT5Error] = []
        self._max_history = 1000
        self._handlers: Dict[ErrorCategory, List[Callable]] = {}
        self._recovery_strategies: Dict[ErrorCategory, Callable] = {}
    
    def register_handler(self, category: ErrorCategory, handler: Callable[[MT5Error], None]) -> None:
        """注册错误处理器"""
        if category not in self._handlers:
            self._handlers[category] = []
        self._handlers[category].append(handler)
    
    def register_recovery_strategy(self, category: ErrorCategory, strategy: Callable[[MT5Error], bool]) -> None:
        """注册错误恢复策略"""
        self._recovery_strategies[category] = strategy
    
    def handle_error(self, error: MT5Error) -> bool:
        """处理错误
        
        Returns:
            bool: 是否成功恢复
        """
        # 记录错误
        self._record_error(error)
        
        # 执行注册的处理器
        for handler in self._handlers.get(error.category, []):
            try:
                handler(error)
            except Exception as e:
                logger.error("[空日志]", f"错误处理器执行失败: {e}")
        
        # 尝试恢复
        return self._attempt_recovery(error)
    
    def _record_error(self, error: MT5Error) -> None:
        """记录错误"""
        # 添加到历史记录
        self._error_history.append(error)
        if len(self._error_history) > self._max_history:
            self._error_history.pop(0)
        
        # 日志记录 - 简化版，避免extra数据冲突
        log_message = f"[{error.error_id}] {str(error)} | Category: {error.category.value} | Component: {error.context.component}"
        
        if error.level == ErrorLevel.CRITICAL or error.level == ErrorLevel.FATAL:
            logger.critical("[空日志]", log_message)
        elif error.level == ErrorLevel.ERROR:
            logger.error("[空日志]", log_message)
        elif error.level == ErrorLevel.WARNING:
            logger.warning("[空日志]", log_message)
        else:
            logger.info("[空日志]", "[空日志]", log_message)
    
    def _attempt_recovery(self, error: MT5Error) -> bool:
        """尝试错误恢复"""
        if not error.recoverable:
            return False
        
        strategy = self._recovery_strategies.get(error.category)
        if strategy:
            try:
                return strategy(error)
            except Exception as e:
                logger.error("[空日志]", f"错误恢复策略执行失败: {e}")
        
        return False
    
    def get_error_stats(self) -> Dict[str, Any]:
        """获取错误统计信息"""
        total = len(self._error_history)
        if total == 0:
            return {"total": 0}
        
        by_category = {}
        by_level = {}
        recent_errors = []
        
        for error in self._error_history[-10:]:  # 最近10个错误
            # 按分类统计
            cat = error.category.value
            by_category[cat] = by_category.get(cat, 0) + 1
            
            # 按级别统计
            lvl = error.level.value
            by_level[lvl] = by_level.get(lvl, 0) + 1
            
            # 最近错误
            recent_errors.append({
                'id': error.error_id,
                'message': error.user_message,
                'category': cat,
                'level': lvl,
                'timestamp': error.context.timestamp.isoformat()
            })
        
        return {
            'total': total,
            'by_category': by_category,
            'by_level': by_level,
            'recent_errors': recent_errors
        }


# === 全局错误处理器实例 ===
_global_handler = ErrorHandler()


def get_error_handler() -> ErrorHandler:
    """获取全局错误处理器"""
    return _global_handler


# === 装饰器 ===

def handle_errors(category: ErrorCategory = ErrorCategory.UNKNOWN,
                 level: ErrorLevel = ErrorLevel.ERROR,
                 recoverable: bool = True,
                 user_message: Optional[str] = None,
                 reraise: bool = False,
                 default_return: Any = None):
                     pass
    """错误处理装饰器
    
    Args:
        category: 错误分类
        level: 错误级别
        recoverable: 是否可恢复
        user_message: 用户友好的错误信息
        reraise: 是否重新抛出异常
        default_return: 发生错误时的默认返回值
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except MT5Error:
                # 如果已经是MT5Error，直接重新抛出
                raise
            except Exception as e:
                # 创建错误上下文
                context = ErrorContext(
                    operation=func.__name__,
                    component=func.__module__
                )
                
                # 创建MT5Error
                mt5_error = MT5Error(
                    message=f"函数 {func.__name__} 执行失败: {str(e)}",
                    category=category,
                    level=level,
                    context=context,
                    original_exception=e,
                    recoverable=recoverable,
                    user_message=user_message
                )
                
                # 处理错误
                recovered = _global_handler.handle_error(mt5_error)
                
                # 如果设置了reraise=True，总是重新抛出
                if reraise:
                    raise mt5_error
                
                # 如果没有恢复但是有默认返回值，返回默认值
                if not recovered and default_return is not None:
                    return default_return
                
                # 如果恢复成功，返回默认值
                if recovered:
                    return default_return
                
                # 其他情况重新抛出异常
                raise mt5_error
        
        return wrapper
    return decorator


# === 便捷函数 ===

def log_error(message: str, 
             category: ErrorCategory = ErrorCategory.UNKNOWN,
             level: ErrorLevel = ErrorLevel.ERROR,
             **context_kwargs) -> str:
    """记录错误的便捷函数
    
    Returns:
        str: 错误ID
    """
    context = ErrorContext(**context_kwargs)
    error = MT5Error(message, category=category, level=level, context=context)
    _global_handler.handle_error(error)
    return error.error_id


def handle_exception(e: Exception,
                    operation: str = "",
                    component: str = "",
                    category: ErrorCategory = ErrorCategory.UNKNOWN,
                    **context_kwargs) -> str:
    """处理已捕获异常的便捷函数
    
    Returns:
        str: 错误ID
    """
    context = ErrorContext(operation=operation, component=component, **context_kwargs)
    
    error = MT5Error(
        message=f"操作 {operation} 失败: {str(e)}",
        category=category,
        context=context,
        original_exception=e
    )
    
    _global_handler.handle_error(error)
    return error.error_id


# === 恢复策略 ===

def setup_default_recovery_strategies():
    """设置默认的错误恢复策略"""
    
    def connection_recovery(error: MT5Error) -> bool:
        """连接错误恢复策略"""
        logger.info("[空日志]", "[空日志]", f"尝试恢复连接错误: {error.error_id}")
        # 这里可以实现重连逻辑
        # 例如：重新初始化MT5连接
        return False  # 默认不自动恢复，需要用户手动重连
    
    def database_recovery(error: MT5Error) -> bool:
        """数据库错误恢复策略"""
        logger.info("[空日志]", "[空日志]", f"尝试恢复数据库错误: {error.error_id}")
        # 这里可以实现数据库重连、创建表等逻辑
        return False
    
    def config_recovery(error: MT5Error) -> bool:
        """配置错误恢复策略"""
        logger.info("[空日志]", "[空日志]", f"尝试恢复配置错误: {error.error_id}")
        # 这里可以实现配置重新加载、使用默认配置等逻辑
        return False
    
    # 注册恢复策略
    handler = get_error_handler()
    handler.register_recovery_strategy(ErrorCategory.CONNECTION, connection_recovery)
    handler.register_recovery_strategy(ErrorCategory.DATABASE, database_recovery)
    handler.register_recovery_strategy(ErrorCategory.CONFIG, config_recovery)


# 初始化默认恢复策略
setup_default_recovery_strategies()


# === 向后兼容的函数 ===

def safe_execute(func: Callable, 
                default_return: Any = None,
                error_message: str = "",
                log_errors: bool = True) -> Any:
    """安全执行函数，与现有代码兼容
    
    这个函数提供了与现有try-except模式兼容的接口
    可以逐步替换现有的错误处理代码
    
    Args:
        func: 要执行的函数
        default_return: 错误时的默认返回值
        error_message: 自定义错误信息
        log_errors: 是否记录错误
    
    Returns:
        函数执行结果或默认值
    """
    try:
        return func()
    except Exception as e:
        if log_errors:
            handle_exception(
                e, 
                operation=getattr(func, '__name__', 'unknown'),
                component='safe_execute'
            )
        elif error_message:
            # 兼容现有的print输出
            # print(f"{error_message}: {str(e)}")
        
        return default_return