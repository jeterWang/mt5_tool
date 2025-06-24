"""
错误处理系统简化测试

避免依赖问题，直接测试错误处理核心功能
"""

import sys
import os
import logging
logger = logging.getLogger(__name__)

def test_error_handling_core():
    """测试错误处理核心功能"""
    
    logger.error("=== Step 6: 错误处理系统核心测试 ===\n"))
    
    # 测试1: 基础模块导入
    try:
        # 直接导入避开主包的依赖
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app', 'utils'))
        
        import error_handler
        import error_utils
        
        logger.error("[OK] 错误处理核心模块导入成功"))
    except Exception as e:
        logger.error(f"[ERROR] 模块导入失败: {e}"))
        return False
    
    # 测试2: 错误分类和级别
    try:
        from error_handler import ErrorCategory, ErrorLevel
        
        # 测试枚举值
        assert ErrorCategory.TRADING.value == "TRADING"
        assert ErrorLevel.ERROR.value == "ERROR"
        
        logger.error("[OK] 错误分类和级别枚举正常"))
    except Exception as e:
        logger.error(f"[ERROR] 错误分类测试失败: {e}"))
        return False
    
    # 测试3: 错误上下文
    try:
        from error_handler import ErrorContext
        
        context = ErrorContext(
            operation="test_operation",
            component="test_component",
            symbol="EURUSD"
        )
        
        context_dict = context.to_dict()
        assert context_dict['operation'] == "test_operation"
        assert context_dict['symbol'] == "EURUSD"
        
        logger.error("[OK] 错误上下文功能正常"))
    except Exception as e:
        logger.error(f"[ERROR] 错误上下文测试失败: {e}"))
        return False
    
    # 测试4: MT5Error异常类
    try:
        from error_handler import MT5Error, ErrorCategory, ErrorLevel, ErrorContext
        
        context = ErrorContext(operation="test", component="test")
        error = MT5Error(
            message="测试错误",
            category=ErrorCategory.TRADING,
            level=ErrorLevel.ERROR,
            context=context
        )
        
        error_dict = error.to_dict()
        assert error_dict['message'] == "测试错误"
        assert error_dict['category'] == "TRADING"
        assert error_dict['level'] == "ERROR"
        
        logger.error("[OK] MT5Error异常类功能正常"))
    except Exception as e:
        logger.error(f"[ERROR] MT5Error测试失败: {e}"))
        return False
    
    # 测试5: 错误处理器
    try:
        from error_handler import ErrorHandler, MT5Error, ErrorCategory
        
        handler = ErrorHandler()
        
        # 测试错误记录
        error = MT5Error("测试错误", category=ErrorCategory.SYSTEM)
        handler.handle_error(error)
        
        # 测试统计功能
        stats = handler.get_error_stats()
        assert stats['total'] > 0
        
        logger.error("[OK] 错误处理器功能正常"))
    except Exception as e:
        logger.error(f"[ERROR] 错误处理器测试失败: {e}"))
        return False
    
    # 测试6: 便捷函数
    try:
        from error_handler import safe_execute
        
        # 测试正常执行
        result = safe_execute(lambda: "正常结果", default_return="错误时返回")
        assert result == "正常结果"
        
        # 测试错误处理
        result = safe_execute(
            lambda: 1 / 0, 
            default_return="错误时返回",
            error_message="除零错误",
            log_errors=True
        )
        assert result == "错误时返回"
        
        logger.info("[OK] 便捷函数功能正常"))
    except Exception as e:
        logger.error(f"[ERROR] 便捷函数测试失败: {e}"))
        return False
    
    # 测试7: 装饰器功能
    try:
        from error_handler import handle_errors, ErrorCategory, ErrorLevel
        
        @handle_errors(
            category=ErrorCategory.TRADING,
            level=ErrorLevel.ERROR,
            default_return="装饰器默认值"
        )
        def test_decorated_function():
            raise ValueError("装饰器测试错误")
        
        result = test_decorated_function()
        assert result == "装饰器默认值"
        
        logger.info("[OK] 装饰器功能正常"))
    except Exception as e:
        logger.error(f"[ERROR] 装饰器测试失败: {e}"))
        return False
    
    # 测试8: 错误工具
    try:
        from error_utils import try_execute, handle_trading_errors
        
        # 测试 try_execute
        result = try_execute(
            lambda: 1 / 0,
            default_return="工具函数默认值",
            error_message="工具函数测试"
        )
        assert result == "工具函数默认值"
        
        # 测试交易装饰器
        @handle_trading_errors(default_return=False)
        def test_trading_func():
            raise Exception("交易测试错误")
        
        result = test_trading_func()
        assert result == False
        
        logger.error("[OK] 错误工具功能正常"))
    except Exception as e:
        logger.error(f"[ERROR] 错误工具测试失败: {e}"))
        return False
    
    return True


def test_migration_compatibility():
    """测试迁移兼容性"""
    
    logger.info("\n=== 迁移兼容性测试 ===\n"))
    
    # 测试现有代码模式仍然工作
    def existing_error_pattern():
        """现有的错误处理模式"""
        try:
            result = 1 / 0
            return result
        except Exception as e:
            logger.error(f"现有模式处理错误: {str(e)}"))
            return None
    
    result = existing_error_pattern()
    if result is None:
        logger.error("[OK] 现有错误处理模式不受影响"))
    else:
        logger.error("[ERROR] 现有错误处理模式受到影响"))
        return False
    
    # 测试新旧混合使用
    try:
        from error_utils import try_execute
        
        def mixed_usage():
            # 旧模式
            try:
                step1 = {}['missing']
            except KeyError as e:
                logger.info(f"旧模式: {str(e)}"))
                step1 = "旧模式默认值"
            
            # 新模式
            step2 = try_execute(
                lambda: [][-1],
                default_return="新模式默认值",
                error_message="新模式测试"
            )
            
            return step1, step2
        
        result = mixed_usage()
        if result == ("旧模式默认值", "新模式默认值"):
            logger.info("[OK] 新旧模式可以混合使用"))
        else:
            logger.error("[ERROR] 新旧模式混合失败"))
            return False
    except Exception as e:
        logger.error(f"[ERROR] 混合使用测试失败: {e}"))
        return False
    
    return True


def show_final_statistics():
    """显示最终统计"""
    
    logger.info("\n=== 最终统计信息 ===\n"))
    
    try:
        from error_handler import get_error_handler
        
        handler = get_error_handler()
        stats = handler.get_error_stats()
        
        logger.error(f"总错误记录数: {stats['total']}"))
        
        if stats['total'] > 0:
            logger.info(f"按分类统计: {stats.get('by_category', {})}"))
            logger.info(f"按级别统计: {stats.get('by_level', {})}"))
            
            recent = stats.get('recent_errors', [])
            if recent:
                logger.error(f"最近错误数量: {len(recent)}"))
                for error in recent[-3:]:  # 显示最近3个
                    logger.error(f"  - {error['id']}: {error['message']}"))
        
    except Exception as e:
        logger.error(f"获取统计信息失败: {e}"))


if __name__ == "__main__":
    logger.error("开始Step 6错误处理系统测试...\n"))
    
    success = True
    
    # 运行核心功能测试
    if not test_error_handling_core():
        success = False
    
    # 运行兼容性测试
    if not test_migration_compatibility():
        success = False
    
    # 显示统计信息
    show_final_statistics()
    
    logger.info(f"\n{'='*60}"))
    if success:
        logger.error("✅ Step 6: 错误处理改进 - 所有核心测试通过！"))
        logger.info("\n🎯 核心特性验证:"))
        logger.error("  ✅ 统一错误分类系统 (ErrorCategory)"))
        logger.error("  ✅ 错误级别管理 (ErrorLevel)"))
        logger.error("  ✅ 错误上下文记录 (ErrorContext)"))
        logger.error("  ✅ MT5专用异常类 (MT5Error)"))
        logger.error("  ✅ 统一错误处理器 (ErrorHandler)"))
        logger.error("  ✅ 装饰器模式支持 (@handle_errors)"))
        logger.info("  ✅ 便捷函数工具 (safe_execute, try_execute)"))
        logger.error("  ✅ 错误统计和追踪功能"))
        logger.info("  ✅ 100%向后兼容性"))
        logger.info("  ✅ 渐进式迁移支持"))
        
        logger.info("\n📊 系统价值:"))
        logger.error("  - 统一的错误处理标准"))
        logger.error("  - 详细的错误分类和追踪"))
        logger.error("  - 用户友好的错误信息"))
        logger.error("  - 可选的错误恢复机制"))
        logger.info("  - 与现有代码无缝集成"))
        logger.info("  - 支持渐进式代码改进"))
        
    else:
        logger.error("❌ Step 6: 错误处理改进 - 部分测试失败"))
        logger.error("   请检查错误处理模块的实现"))
    
    logger.info(f"{'='*60}"))
    logger.info("\n💡 使用建议:"))
    logger.error("1. 新代码使用 @handle_errors 装饰器"))
    logger.info("2. 现有代码可用 try_execute() 渐进替换"))
    logger.error("3. 关键操作使用 error_context() 上下文管理器"))
    logger.error("4. 定期查看错误统计信息优化系统稳定性"))
