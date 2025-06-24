"""
错误处理工具函数

提供便捷的错误处理工具，与现有代码无缝集成
可以逐步替换现有的错误处理模式
"""

import functools
from typing import Any, Callable, Optional, Type, Union, Dict
from contextlib import contextmanager

from error_handler import (
    ErrorCategory, ErrorLevel, ErrorContext, MT5Error,
    handle_exception, log_error, safe_execute
)

# 简化版logger
import logging
logger = logging.getLogger(__name__)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


# === 上下文管理器 ===

@contextmanager
def error_context(operation: str, 
                 component: str = "",
                 category: ErrorCategory = ErrorCategory.UNKNOWN,
                 **kwargs):
    """错误上下文管理器
    
    用法:
        with error_context("连接MT5", "trader"):
            mt5.initialize()
    """
    try:
        yield
    except Exception as e:
        error_id = handle_exception(
            e, 
            operation=operation,
            component=component,
            category=category,
            **kwargs
        )
        logger.error("[空日志]", f"操作失败 [{error_id}]: {operation}")
        raise


# === 特定领域的错误处理装饰器 ===

def handle_trading_errors(default_return: Any = False,
                         symbol: Optional[str] = None,
                         user_message: str = "交易操作失败"):
    """交易相关错误处理装饰器"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                context = ErrorContext(
                    operation=func.__name__,
                    component="trading",
                    symbol=symbol or kwargs.get('symbol', 'unknown')
                )
                
                error = MT5Error(
                    message=f"交易操作 {func.__name__} 失败: {str(e)}",
                    category=ErrorCategory.TRADING,
                    level=ErrorLevel.ERROR,
                    context=context,
                    original_exception=e,
                    user_message=user_message
                )
                
                # 记录并处理错误
                from error_handler import get_error_handler
                get_error_handler().handle_error(error)
                
                return default_return
        return wrapper
    return decorator


def handle_database_errors(default_return: Any = None,
                          user_message: str = "数据库操作失败"):
    """数据库相关错误处理装饰器"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                context = ErrorContext(
                    operation=func.__name__,
                    component="database"
                )
                
                error = MT5Error(
                    message=f"数据库操作 {func.__name__} 失败: {str(e)}",
                    category=ErrorCategory.DATABASE,
                    level=ErrorLevel.ERROR,
                    context=context,
                    original_exception=e,
                    user_message=user_message
                )
                
                from error_handler import get_error_handler
                get_error_handler().handle_error(error)
                
                return default_return
        return wrapper
    return decorator


def handle_connection_errors(default_return: Any = False,
                           user_message: str = "连接操作失败"):
    """连接相关错误处理装饰器"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                context = ErrorContext(
                    operation=func.__name__,
                    component="connection"
                )
                
                error = MT5Error(
                    message=f"连接操作 {func.__name__} 失败: {str(e)}",
                    category=ErrorCategory.CONNECTION,
                    level=ErrorLevel.ERROR,
                    context=context,
                    original_exception=e,
                    user_message=user_message
                )
                
                from error_handler import get_error_handler
                get_error_handler().handle_error(error)
                
                return default_return
        return wrapper
    return decorator


# === 渐进式迁移工具 ===

class ErrorMigrationHelper:
    """错误处理迁移助手
    
    帮助现有代码渐进式地迁移到新的错误处理系统
    """
    
    @staticmethod
    def wrap_existing_try_except(original_exception_handler: Callable[[Exception], Any],
                                category: ErrorCategory = ErrorCategory.UNKNOWN,
                                operation: str = ""):
        """包装现有的异常处理代码
        
        Args:
            original_exception_handler: 原有的异常处理函数
            category: 错误分类
            operation: 操作名称
        
        Returns:
            新的异常处理函数
        """
        def new_handler(e: Exception) -> Any:
            # 先用新系统记录错误
            handle_exception(e, operation=operation, category=category)
            
            # 然后执行原有的处理逻辑
            return original_exception_handler(e)
        
        return new_handler
    
    @staticmethod
    def enhance_print_error(print_func: Callable[[str], None],
                          category: ErrorCategory = ErrorCategory.UNKNOWN):
        """增强现有的print错误输出
        
        在保持原有print输出的同时，添加到错误处理系统
        """
        # def enhanced_print(message: str, **kwargs):
            # 原有的print输出
            print_func(message)
            
            # 添加到新系统
            log_error(message, category=category, **kwargs)
        
        return enhanced_print


# === 向后兼容的便捷函数 ===

def try_execute(func: Callable, 
               *args, 
               default_return: Any = None,
               error_message: str = "",
               category: ErrorCategory = ErrorCategory.UNKNOWN,
               **kwargs) -> Any:
    """尝试执行函数，兼容现有代码模式
    
    这是safe_execute的增强版本，提供更多参数
    
    用法:
        # 替换现有的try-except
        result = try_execute(
            lambda: mt5.initialize(),
            default_return=False,
            error_message="MT5初始化失败",
            category=ErrorCategory.CONNECTION
        )
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        # 记录到新系统
        handle_exception(
            e, 
            operation=getattr(func, '__name__', 'anonymous'),
            category=category
        )
        
        # 兼容原有print输出
        if error_message:
            pass
            # print(f"{error_message}: {str(e)}")
        
        return default_return


def safe_call(obj: Any, method_name: str, *args, 
             default_return: Any = None,
             error_message: str = "",
             **kwargs) -> Any:
    """安全调用对象方法
    
    用法:
        # 替换 obj.method() 调用
        result = safe_call(trader, 'get_account_info', 
                          default_return={},
                          error_message="获取账户信息失败")
    """
    try:
        method = getattr(obj, method_name)
        return method(*args, **kwargs)
    except Exception as e:
        handle_exception(
            e, 
            operation=f"{obj.__class__.__name__}.{method_name}",
            category=ErrorCategory.UNKNOWN
        )
        
        if error_message:
            pass
            # print(f"{error_message}: {str(e)}")
        
        return default_return


# === 错误恢复工具 ===

class RetryConfig:
    """重试配置"""
    def __init__(self, 
                 max_attempts: int = 3,
                 delay: float = 1.0,
                 backoff_factor: float = 2.0,
                 exceptions: tuple = (Exception,)):
                     pass
        self.max_attempts = max_attempts
        self.delay = delay
        self.backoff_factor = backoff_factor
        self.exceptions = exceptions


def with_retry(config: RetryConfig = None):
    """重试装饰器
    
    用法:
        @with_retry(RetryConfig(max_attempts=3, delay=1.0))
        def connect_mt5():
            return mt5.initialize()
    """
    if config is None:
        config = RetryConfig()
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            delay = config.delay
            
            for attempt in range(config.max_attempts):
                try:
                    return func(*args, **kwargs)
                except config.exceptions as e:
                    last_exception = e
                    
                    if attempt < config.max_attempts - 1:
                        logger.warning("[空日志]", f"重试 {func.__name__} (第{attempt + 1}次): {str(e)}")
                        import time
                        time.sleep(delay)
                        delay *= config.backoff_factor
                    else:
                        logger.error("[空日志]", f"{func.__name__} 重试失败，已达最大重试次数")
            
            # 记录最终失败
            if last_exception:
                handle_exception(
                    last_exception,
                    operation=func.__name__,
                    component="retry_wrapper"
                )
                raise last_exception
        
        return wrapper
    return decorator


# === 预定义的常用错误处理器 ===

# MT5连接错误处理
def handle_mt5_connection_error(e: Exception, operation: str = "MT5操作") -> bool:
    """处理MT5连接错误"""
    error_id = handle_exception(
        e, 
        operation=operation,
        category=ErrorCategory.CONNECTION,
        component="mt5"
    )
    logger.error("[空日志]", f"MT5连接错误 [{error_id}]: {str(e)}")
    return False

# 交易错误处理
def handle_trading_error(e: Exception, symbol: str = "", operation: str = "交易操作") -> bool:
    """处理交易错误"""
    error_id = handle_exception(
        e,
        operation=operation,
        category=ErrorCategory.TRADING,
        component="trading",
        symbol=symbol
    )
    logger.error("[空日志]", f"交易错误 [{error_id}]: {str(e)}")
    return False

# 数据库错误处理
def handle_db_error(e: Exception, operation: str = "数据库操作") -> Any:
    """处理数据库错误"""
    error_id = handle_exception(
        e,
        operation=operation,
        category=ErrorCategory.DATABASE,
        component="database"
    )
    logger.error("[空日志]", f"数据库错误 [{error_id}]: {str(e)}")
    return None

# 配置错误处理
def handle_config_error(e: Exception, operation: str = "配置操作") -> bool:
    """处理配置错误"""
    error_id = handle_exception(
        e,
        operation=operation,
        category=ErrorCategory.CONFIG,
        component="config"
    )
    logger.error("[空日志]", f"配置错误 [{error_id}]: {str(e)}")
    return False


# === 使用示例函数 ===

def demonstrate_usage():
    """演示新错误处理系统的用法"""
    
    logger.error("[空日志]", "=== 新错误处理系统使用示例 ===")
    
    # 1. 使用装饰器
    @handle_trading_errors(default_return=False, user_message="下单失败")
    def place_order_example(symbol: str, volume: float):
        # 模拟交易操作
        if volume <= 0:
            raise ValueError("交易量必须大于0")
        return True
    
    # 2. 使用上下文管理器
    try:
        with error_context("连接MT5", "trader", category=ErrorCategory.CONNECTION):
            # 模拟连接操作
            pass
    except Exception:
        pass
    
    # 3. 使用便捷函数
    result = try_execute(
        lambda: 1 / 0,  # 模拟错误
        default_return=0,
        error_message="除零错误",
        category=ErrorCategory.SYSTEM
    )
    
    # 4. 使用重试机制
    @with_retry(RetryConfig(max_attempts=2, delay=0.1))
    def unreliable_operation():
        import random
        if random.random() < 0.5:
            raise Exception("随机失败")
        return "成功"
    
    try:
        result = unreliable_operation()
        # print(f"重试操作结果: {result}")
    except Exception:
        pass
    
    # print("示例执行完成")


if __name__ == "__main__":
    demonstrate_usage()