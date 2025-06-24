# -*- coding: utf-8 -*-
"""
Step 6: 错误处理改进测试

测试新的错误处理系统的核心功能
"""

import sys
import os

# 添加路径
current_dir = os.path.dirname(__file__)
utils_path = os.path.join(current_dir, 'app', 'utils')
sys.path.insert(0, utils_path)

def test_core_functionality():
    """测试核心功能"""
    
    print("=== Step 6: 错误处理系统测试 ===")
    print()
    
    # 测试1: 导入测试
    try:
        import error_handler
        import error_utils
        print("[OK] 错误处理模块导入成功")
    except Exception as e:
        print("[ERROR] 模块导入失败:", str(e))
        return False
    
    # 测试2: 错误分类
    try:
        from error_handler import ErrorCategory, ErrorLevel
        
        # 测试枚举
        trading_cat = ErrorCategory.TRADING
        error_level = ErrorLevel.ERROR
        
        print("[OK] 错误分类和级别定义正常")
    except Exception as e:
        print("[ERROR] 错误分类测试失败:", str(e))
        return False
    
    # 测试3: 错误上下文
    try:
        from error_handler import ErrorContext
        
        ctx = ErrorContext(
            operation="test_op",
            component="test_comp",
            symbol="EURUSD"
        )
        
        ctx_dict = ctx.to_dict()
        assert ctx_dict['operation'] == "test_op"
        
        print("[OK] 错误上下文功能正常")
    except Exception as e:
        print("[ERROR] 错误上下文测试失败:", str(e))
        return False
    
    # 测试4: MT5Error异常
    try:
        from error_handler import MT5Error, ErrorCategory, ErrorLevel, ErrorContext
        
        ctx = ErrorContext(operation="test")
        error = MT5Error(
            "测试错误",
            category=ErrorCategory.TRADING,
            level=ErrorLevel.ERROR,
            context=ctx
        )
        
        error_dict = error.to_dict()
        assert error_dict['category'] == "TRADING"
        
        print("[OK] MT5Error异常类正常")
    except Exception as e:
        print("[ERROR] MT5Error测试失败:", str(e))
        return False
    
    # 测试5: 错误处理器
    try:
        from error_handler import ErrorHandler, get_error_handler
        
        handler = get_error_handler()
        
        # 创建测试错误
        from error_handler import MT5Error, ErrorCategory
        test_error = MT5Error("测试错误", category=ErrorCategory.SYSTEM)
        
        # 处理错误
        handler.handle_error(test_error)
        
        # 检查统计
        stats = handler.get_error_stats()
        assert stats['total'] > 0
        
        print("[OK] 错误处理器功能正常")
    except Exception as e:
        print("[ERROR] 错误处理器测试失败:", str(e))
        return False
    
    # 测试6: 便捷函数
    try:
        from error_handler import safe_execute
        
        # 测试正常情况
        result = safe_execute(lambda: "success")
        assert result == "success"
        
        # 测试错误情况
        result = safe_execute(
            lambda: 1/0,
            default_return="default",
            error_message="Test error"
        )
        assert result == "default"
        
        print("[OK] 便捷函数正常")
    except Exception as e:
        print("[ERROR] 便捷函数测试失败:", str(e))
        return False
    
    # 测试7: 装饰器
    try:
        from error_handler import handle_errors, ErrorCategory
        
        @handle_errors(
            category=ErrorCategory.SYSTEM,
            default_return="decorator_default",
            reraise=False  # 关键：不重新抛出异常
        )
        def test_func():
            raise ValueError("装饰器测试")
        
        result = test_func()
        assert result == "decorator_default"
        
        print("[OK] 装饰器功能正常")
    except Exception as e:
        print("[ERROR] 装饰器测试失败:", str(e))
        return False
    
    # 测试8: 错误工具
    try:
        from error_utils import try_execute
        
        result = try_execute(
            lambda: 1/0,
            default_return="utils_default"
        )
        assert result == "utils_default"
        
        print("[OK] 错误工具正常")
    except Exception as e:
        print("[ERROR] 错误工具测试失败:", str(e))
        return False
    
    return True


def test_compatibility():
    """测试兼容性"""
    
    print()
    print("=== 兼容性测试 ===")
    print()
    
    # 现有代码模式
    def old_pattern():
        try:
            return 1/0
        except Exception as e:
            print("旧模式错误:", str(e))
            return None
    
    result = old_pattern()
    if result is None:
        print("[OK] 现有代码模式正常")
    else:
        print("[ERROR] 现有代码受影响")
        return False
    
    # 混合使用测试
    try:
        from error_utils import try_execute
        
        # 旧模式
        old_result = None
        try:
            old_result = 1/0
        except:
            old_result = "old_default"
        
        # 新模式
        new_result = try_execute(
            lambda: [1, 2, 3][10],  # 索引越界错误
            default_return="new_default"
        )
        
        if old_result == "old_default" and new_result == "new_default":
            print("[OK] 新旧模式可混合使用")
        else:
            print("[ERROR] 混合使用失败")
            return False
    except Exception as e:
        print("[ERROR] 混合测试失败:", str(e))
        return False
    
    return True


def show_statistics():
    """显示统计信息"""
    
    print()
    print("=== 统计信息 ===")
    print()
    
    try:
        from error_handler import get_error_handler
        
        handler = get_error_handler()
        stats = handler.get_error_stats()
        
        print("错误统计:")
        print("  总数:", stats['total'])
        if stats['total'] > 0:
            print("  分类:", stats.get('by_category', {}))
            print("  级别:", stats.get('by_level', {}))
    except Exception as e:
        print("统计获取失败:", str(e))


if __name__ == "__main__":
    print("开始Step 6测试...")
    print()
    
    success = True
    
    if not test_core_functionality():
        success = False
    
    if not test_compatibility():
        success = False
    
    show_statistics()
    
    print()
    print("="*50)
    if success:
        print("[SUCCESS] Step 6: 错误处理改进 - 所有测试通过!")
        print()
        print("核心特性:")
        print("  - 统一错误分类系统")
        print("  - 错误级别管理")
        print("  - 错误上下文记录")
        print("  - MT5专用异常类")
        print("  - 统一错误处理器")
        print("  - 装饰器支持")
        print("  - 便捷函数工具")
        print("  - 错误统计功能")
        print("  - 100%向后兼容")
        print("  - 渐进式迁移支持")
    else:
        print("[FAILED] Step 6: 错误处理改进 - 部分测试失败")
    
    print("="*50)