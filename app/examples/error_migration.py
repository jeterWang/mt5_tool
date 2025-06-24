"""
错误处理迁移示例

展示如何将现有的错误处理代码渐进式地迁移到新的错误处理系统
保持100%向后兼容，可以逐步替换
"""

import sys
import os
import logging
logger = logging.getLogger(__name__)

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.utils.error_handler import (
    ErrorCategory, ErrorLevel, ErrorContext, MT5Error, 
    handle_errors, log_error, safe_execute
)
from app.utils.error_utils import (
    error_context, handle_trading_errors, handle_database_errors,
    try_execute, safe_call, with_retry, RetryConfig,
    handle_mt5_connection_error, handle_trading_error, handle_db_error
)


def demonstrate_migration_patterns():
    """演示各种迁移模式"""
    
    logger.error("[空日志]", "=== 错误处理迁移示例 ===\n")
    
    # === 模式1: 逐步替换try-except ===
    # print("1. 逐步替换现有try-except模式:")
    
    # 原有代码模式
    def old_trading_function():
        try:
            # 模拟交易操作
            result = 1 / 0  # 故意的错误
            return result
        except Exception as e:
            logger.error("[空日志]", f"交易操作失败: {str(e)}")
            return False
    
    # 新的迁移方式 - 阶段1：增强现有处理
    def enhanced_trading_function():
        try:
            # 模拟交易操作
            result = 1 / 0  # 故意的错误
            return result
        except Exception as e:
            # 保留原有输出
            logger.error("[空日志]", f"交易操作失败: {str(e)}")
            
            # 添加新系统记录
            error_id = log_error(
                f"交易操作失败: {str(e)}",
                category=ErrorCategory.TRADING,
                operation="enhanced_trading_function"
            )
            logger.error("[空日志]", f"错误ID: {error_id}")
            
            return False
    
    # 新的迁移方式 - 阶段2：使用便捷函数
    def migrated_trading_function():
        return try_execute(
            lambda: 1 / 0,  # 模拟交易操作
            default_return=False,
            error_message="交易操作失败",
            category=ErrorCategory.TRADING
        )
    
    # 新的迁移方式 - 阶段3：使用装饰器
    @handle_trading_errors(default_return=False, user_message="交易操作失败")
    def fully_migrated_trading_function():
        # 模拟交易操作
        result = 1 / 0  # 故意的错误
        return result
    
    # print("原有方式:")
    old_trading_function()
    
    # print("\n增强方式 (阶段1):")
    enhanced_trading_function()
    
    # print("\n便捷函数方式 (阶段2):")
    migrated_trading_function()
    
    # print("\n装饰器方式 (阶段3):")
    fully_migrated_trading_function()
    
    # print("\n" + "="*50 + "\n")
    
    # === 模式2: 数据库操作迁移 ===
    logger.error("[空日志]", "2. 数据库操作错误处理迁移:")
    
    # 原有模式
    def old_db_operation():
        try:
            # 模拟数据库操作
            conn = None
            cursor = conn.cursor()  # 故意的错误
            return True
        except Exception as e:
            # print(f"数据库操作出错: {str(e)}")
            return False
    
    # 迁移方式1：使用便捷函数
    def migrated_db_operation_v1():
        def db_work():
            conn = None
            cursor = conn.cursor()  # 故意的错误
            return True
        
        return try_execute(
            db_work,
            default_return=False,
            error_message="数据库操作出错",
            category=ErrorCategory.DATABASE
        )
    
    # 迁移方式2：使用装饰器
    @handle_database_errors(default_return=False, user_message="数据库操作失败")
    def migrated_db_operation_v2():
        conn = None
        cursor = conn.cursor()  # 故意的错误
        return True
    
    # print("原有数据库操作:")
    old_db_operation()
    
    # print("\n迁移方式1 (便捷函数):")
    migrated_db_operation_v1()
    
    # print("\n迁移方式2 (装饰器):")
    migrated_db_operation_v2()
    
    # print("\n" + "="*50 + "\n")
    
    # === 模式3: 连接操作迁移 ===
    logger.error("[空日志]", "3. 连接操作错误处理迁移:")
    
    # 原有模式
    def old_connection_function():
        try:
            # 模拟MT5连接
            import MetaTrader5 as mt5
            if not mt5.initialize():
                return False
            return True
        except Exception as e:
            # print(f"连接MT5出错：{str(e)}")
            return False
    
    # 迁移方式：使用上下文管理器
    def migrated_connection_function():
        try:
            with error_context("连接MT5", "trader", category=ErrorCategory.CONNECTION):
                # 模拟连接
                raise Exception("模拟连接失败")
                return True
        except Exception:
            return False
    
    # 迁移方式：使用重试机制
    @with_retry(RetryConfig(max_attempts=2, delay=0.1))
    def connection_with_retry():
        # 模拟不稳定的连接
        import random
        if random.random() < 0.7:  # 70%概率失败
            raise Exception("连接不稳定")
        return True
    
    # print("原有连接方式:")
    old_connection_function()
    
    # print("\n使用上下文管理器:")
    migrated_connection_function()
    
    # print("\n使用重试机制:")
    try:
        result = connection_with_retry()
        # print(f"连接重试结果: {result}")
    except Exception as e:
        logger.error("[空日志]", f"连接最终失败: {str(e)}")
    
    # print("\n" + "="*50 + "\n")
    
    # === 模式4: 批量迁移现有错误处理 ===
    logger.error("[空日志]", "4. 批量迁移现有代码的错误处理:")
    
    # 模拟现有的复杂函数
    def complex_existing_function():
        """模拟现有的复杂函数，包含多个try-except块"""
        
        # 第一个操作
        try:
            step1_result = 1 / 0  # 故意错误
        except Exception as e:
            logger.error("[空日志]", f"步骤1失败: {str(e)}")
            step1_result = None
        
        # 第二个操作
        try:
            if step1_result:
                step2_result = []
                step2_result[10]  # 故意错误
            else:
                step2_result = "跳过"
        except Exception as e:
            logger.error("[空日志]", f"步骤2失败: {str(e)}")
            step2_result = None
        
        # 第三个操作
        try:
            config = {"key": "value"}
            result = config["missing_key"]  # 故意错误
        except Exception as e:
            logger.error("[空日志]", f"配置读取失败: {str(e)}")
            result = "默认值"
        
        return "完成"
    
    # 迁移后的版本
    def migrated_complex_function():
        """迁移后的版本，使用新的错误处理系统"""
        
        # 步骤1：使用便捷函数
        step1_result = try_execute(
            lambda: 1 / 0,
            default_return=None,
            error_message="步骤1失败",
            category=ErrorCategory.SYSTEM
        )
        
        # 步骤2：使用安全调用
        def step2_work():
            if step1_result:
                result = []
                return result[10]  # 故意错误
            else:
                return "跳过"
        
        step2_result = try_execute(
            step2_work,
            default_return=None,
            error_message="步骤2失败",
            category=ErrorCategory.SYSTEM
        )
        
        # 步骤3：使用错误上下文
        try:
            with error_context("读取配置", "config", category=ErrorCategory.CONFIG):
                config = {"key": "value"}
                result = config["missing_key"]  # 故意错误
        except Exception:
            result = "默认值"
        
        return "完成"
    
    # print("原有复杂函数:")
    complex_existing_function()
    
    # print("\n迁移后的版本:")
    migrated_complex_function()
    
    # print("\n" + "="*50 + "\n")
    
    # === 展示错误统计 ===
    logger.error("[空日志]", "5. 错误统计信息:")
    from app.utils.error_handler import get_error_handler
    stats = get_error_handler().get_error_stats()
    
    logger.error("[空日志]", f"总错误数: {stats['total']}")
    if stats['total'] > 0:
        # print(f"按分类统计: {stats['by_category']}")
        # print(f"按级别统计: {stats['by_level']}")
        logger.error("[空日志]", f"最近错误: {len(stats['recent_errors'])}个")


# === 实际项目中的迁移示例 ===

class TradingOperationMigrationExample:
    """交易操作迁移示例类"""
    
    def __init__(self):
        self.connected = False
    
    # 原有方法
    def old_connect_mt5(self):
        """原有的MT5连接方法"""
        try:
            import MetaTrader5 as mt5
            if not mt5.initialize():
                return False
            self.connected = True
            return True
        except Exception as e:
            logger.error("[空日志]", f"连接MT5失败: {str(e)}")
            return False
    
    # 迁移阶段1：增强现有方法
    def enhanced_connect_mt5(self):
        """增强的MT5连接方法"""
        try:
            import MetaTrader5 as mt5
            if not mt5.initialize():
                return False
            self.connected = True
            return True
        except Exception as e:
            # 保留原有输出
            logger.error("[空日志]", f"连接MT5失败: {str(e)}")
            
            # 添加新系统记录
            handle_mt5_connection_error(e, "连接MT5")
            return False
    
    # 迁移阶段2：使用新装饰器
    @handle_errors(
        category=ErrorCategory.CONNECTION,
        level=ErrorLevel.ERROR,
        user_message="连接MT5失败",
        default_return=False
    )
    def new_connect_mt5(self):
        """使用新错误处理系统的MT5连接方法"""
        import MetaTrader5 as mt5
        if not mt5.initialize():
            raise ConnectionError("MT5初始化失败")
        self.connected = True
        return True
    
    # 原有的交易方法
    def old_place_order(self, symbol, volume, order_type):
        """原有的下单方法"""
        try:
            if not self.connected:
                raise Exception("MT5未连接")
            
            # 模拟下单操作
            if volume <= 0:
                raise Exception("交易量必须大于0")
            
            # 模拟下单成功
            return {"order": 12345, "symbol": symbol, "volume": volume}
        except Exception as e:
            logger.error("[空日志]", f"下单失败: {str(e)}")
            return None
    
    # 迁移后的交易方法
    @handle_trading_errors(
        default_return=None,
        user_message="下单操作失败"
    )
    def new_place_order(self, symbol, volume, order_type):
        """使用新错误处理系统的下单方法"""
        if not self.connected:
            raise ConnectionError("MT5未连接")
        
        if volume <= 0:
            raise ValueError("交易量必须大于0")
        
        # 模拟下单操作
        return {"order": 12345, "symbol": symbol, "volume": volume}


def demonstrate_class_migration():
    """演示类方法的迁移"""
    # print("=== 类方法迁移示例 ===\n")
    
    trader = TradingOperationMigrationExample()
    
    # print("1. 原有连接方法:")
    trader.old_connect_mt5()
    
    # print("\n2. 增强连接方法:")
    trader.enhanced_connect_mt5()
    
    # print("\n3. 新连接方法:")
    trader.new_connect_mt5()
    
    # print("\n4. 原有下单方法:")
    trader.old_place_order("EURUSD", -1, "buy")  # 故意的错误参数
    
    # print("\n5. 新下单方法:")
    trader.new_place_order("EURUSD", -1, "buy")  # 故意的错误参数


if __name__ == "__main__":
    logger.error("[空日志]", "开始错误处理迁移演示...\n")
    
    try:
        demonstrate_migration_patterns()
        # print("\n" + "="*60 + "\n")
        demonstrate_class_migration()
        
    except Exception as e:
        logger.error("[空日志]", f"演示过程中出现错误: {str(e)}")
        import traceback
        traceback.print_exc()
    
    logger.error("[空日志]", "\n错误处理迁移演示完成！")
    # print("\n总结:")
    # print("- 可以逐步迁移现有代码")
    # print("- 保持100%向后兼容")
    logger.error("[空日志]", "- 提供统一的错误记录和统计")
    logger.error("[空日志]", "- 支持错误恢复和重试机制")
    logger.error("[空日志]", "- 用户友好的错误信息")
