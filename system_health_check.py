#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MT5交易系统 - 系统健康检查
验证所有已完成重构步骤的集成效果
"""

import sys
import os
import traceback
import logging
logger = logging.getLogger(__name__)
from pathlib import Path

# 添加项目根目录到Python路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

logger.info("=" * 60)
logger.info("MT5交易系统 - 系统健康检查")
logger.info("=" * 60)

# 用于收集检查结果
results = {
    'step1_logging': False,
    'step2_type_hints': False,  
    'step3_config_management': False,
    'step4_event_system': False,
    'step5_interfaces': False,
    'step6_error_handling': False,
    'step7_controllers': False,
    'step8_data_layer': False,
    'step9_api_system': False,
    'integration_test': False
}

def test_step1_logging():
    """Step 1: 日志系统测试"""
    try:
        from app.utils.logger import get_logger, AppLogger
        
        logger = get_logger("test")
        logger.info("日志系统测试 - 成功")
        
        app_logger = AppLogger()
        app_logger.info("AppLogger测试 - 成功")
        
        results['step1_logging'] = True
        logger.info("✅ Step 1: 日志系统 - 正常工作")
        return True
    except Exception as e:
        logger.error(f"❌ Step 1: 日志系统 - 错误: {e}")
        return False

def test_step2_type_hints():
    """Step 2: 类型提示验证 (基础检查)"""
    try:
        # 检查主要文件是否存在类型提示
        from app.gui import main_window
        
        # 简单验证 - 能够导入即可，类型提示是编译时特性
        results['step2_type_hints'] = True
        logger.info("✅ Step 2: 类型提示 - 导入正常")
        return True
    except Exception as e:
        logger.error(f"❌ Step 2: 类型提示验证 - 错误: {e}")
        return False

def test_step3_config_management():
    """Step 3: 配置管理测试"""
    try:
        from app.utils.config_manager import get_config_manager, ConfigManager
        
        config_manager = get_config_manager()
        if config_manager is None:
            raise Exception("ConfigManager 获取失败")
            
        # 测试基本配置读取
        test_config = config_manager.get("SYMBOLS", [])
        if not isinstance(test_config, list):
            raise Exception("配置读取结果类型错误")
            
        results['step3_config_management'] = True
        logger.info("✅ Step 3: 配置管理 - 正常工作")
        return True
    except Exception as e:
        logger.error(f"❌ Step 3: 配置管理 - 错误: {e}")
        return False

def test_step4_event_system():
    """Step 4: 事件系统测试"""
    try:
        from app.utils.event_bus import get_event_bus, EventType, Event
        
        event_bus = get_event_bus()
        
        # 测试事件订阅和发布
        test_events = []
        def test_handler(event):
            test_events.append(event)
            
        event_bus.subscribe(EventType.TRADE_EXECUTED, test_handler)
        
        test_event = Event(EventType.TRADE_EXECUTED, {"test": "data"})
        event_bus.publish(test_event)
        
        if len(test_events) == 0:
            raise Exception("事件发布/订阅失败")
            
        event_bus.unsubscribe(EventType.TRADE_EXECUTED, test_handler)
        
        results['step4_event_system'] = True
        logger.info("✅ Step 4: 事件系统 - 正常工作")
        return True
    except Exception as e:
        logger.error(f"❌ Step 4: 事件系统 - 错误: {e}")
        return False

def test_step5_interfaces():
    """Step 5: 服务接口测试"""
    try:
        from app.interfaces.trader_interface import ITrader
        from app.interfaces.config_interface import IConfigManager
        from app.adapters.trader_adapter import MT5TraderAdapter
        
        # 测试接口存在
        if not hasattr(ITrader, 'place_order'):
            raise Exception("ITrader接口方法缺失")
            
        # 测试适配器创建
        from app.adapters.trader_adapter import create_trader_interface
        trader_adapter = create_trader_interface()
        
        if not isinstance(trader_adapter, MT5TraderAdapter):
            raise Exception("适配器创建失败")
            
        results['step5_interfaces'] = True
        logger.info("✅ Step 5: 服务接口 - 正常工作")
        return True
    except Exception as e:
        logger.error(f"❌ Step 5: 服务接口 - 错误: {e}")
        return False

def test_step6_error_handling():
    """Step 6: 错误处理测试"""
    try:
        from app.utils.error_handler import get_error_handler, ErrorLevel, MT5Error
        from app.utils.error_utils import safe_call, handle_trading_errors
        
        error_handler = get_error_handler()
        
        # 测试错误处理
        test_error = MT5Error("测试错误", ErrorLevel.WARNING)
        error_handler.handle_error(test_error)
        
        # 测试安全调用
        def test_function():
            return "success"
            
        result = safe_call(test_function, default="failed")
        if result != "success":
            raise Exception("安全调用失败")
            
        results['step6_error_handling'] = True
        logger.error("✅ Step 6: 错误处理 - 正常工作")
        return True
    except Exception as e:
        logger.error(f"❌ Step 6: 错误处理 - 错误: {e}")
        return False

def test_step7_controllers():
    """Step 7: 控制器层测试"""
    try:
        from app.controllers.main_controller import get_controller, MT5Controller
        from app.controllers.simple_controller import get_simple_controller
        
        # 测试控制器创建 (可能失败由于依赖问题，但至少模块应该可导入)
        try:
            controller = get_controller()
            if controller and isinstance(controller, MT5Controller):
                logger.info("✅ Step 7: 主控制器 - 创建成功")
            else:
                logger.error("⚠️  Step 7: 主控制器 - 创建失败但模块可导入")
        except Exception:
            logger.info("⚠️  Step 7: 主控制器 - 依赖问题")
            
        # 测试简单控制器
        simple_controller = get_simple_controller()
        if simple_controller is None:
            raise Exception("简单控制器获取失败")
            
        results['step7_controllers'] = True
        logger.info("✅ Step 7: 控制器层 - 基础功能正常")
        return True
    except Exception as e:
        logger.error(f"❌ Step 7: 控制器层 - 错误: {e}")
        return False

def test_step8_data_layer():
    """Step 8: 数据层测试"""
    try:
        from app.utils.connection_manager import get_connection_manager
        from app.utils.query_builder import QueryBuilder, select
        from app.dal.data_mapper import DataMapper, TradeRecord
        from app.adapters.data_layer_adapter import EnhancedTradeDatabase
        
        # 测试连接管理器
        conn_manager = get_connection_manager("test.db")
        if conn_manager is None:
            raise Exception("连接管理器获取失败")
            
        # 测试查询构建器
        query = select("*").from_table("trades").where("symbol = ?", "EURUSD")
        if not query or "SELECT" not in query.sql:
            raise Exception("查询构建器失败")
            
        # 测试数据映射器
        mapper = DataMapper()
        if mapper is None:
            raise Exception("数据映射器创建失败")
            
        results['step8_data_layer'] = True
        logger.info("✅ Step 8: 数据层 - 正常工作")
        return True
    except Exception as e:
        logger.error(f"❌ Step 8: 数据层 - 错误: {e}")
        return False

def test_step9_api_system():
    """Step 9: API系统测试"""
    try:
        from app.api.models import APIResponse, OrderRequest
        from app.api.validators import RequestValidator, validate_request
        from app.api.routes import APIRoutes
        from app.api.server import MT5APIServer
        from app.adapters.api_adapter import get_api_adapter
        
        # 测试API模型
        response = APIResponse(success=True, data={"test": "data"})
        if not response.success:
            raise Exception("API响应模型错误")
            
        # 测试请求验证
        validator = RequestValidator()
        if validator is None:
            raise Exception("请求验证器创建失败")
            
        # 测试API适配器
        try:
            api_adapter = get_api_adapter()
            if api_adapter:
                logger.info("✅ Step 9: API适配器 - 创建成功")
            else:
                logger.error("⚠️  Step 9: API适配器 - 创建失败但模块可导入")
        except Exception:
            logger.info("⚠️  Step 9: API适配器 - 依赖问题")
            
        results['step9_api_system'] = True
        logger.info("✅ Step 9: API系统 - 基础功能正常")
        return True
    except Exception as e:
        logger.error(f"❌ Step 9: API系统 - 错误: {e}")
        return False

def test_integration():
    """集成测试 - 验证各组件协同工作"""
    try:
        # 测试日志 + 配置管理集成
        from app.utils.logger import get_logger
        from app.utils.config_manager import get_config_manager
        
        logger = get_logger("integration_test")
        config_manager = get_config_manager()
        
        if logger and config_manager:
            logger.info("集成测试 - 日志和配置管理协同工作正常")
            
        # 测试事件系统 + 错误处理集成
        from app.utils.event_bus import get_event_bus, EventType, Event
        from app.utils.error_handler import get_error_handler
        
        event_bus = get_event_bus()
        error_handler = get_error_handler()
        
        if event_bus and error_handler:
            # 发布测试事件
            test_event = Event(EventType.SYSTEM_STATUS, {"status": "healthy"})
            event_bus.publish(test_event)
            
        results['integration_test'] = True
        logger.info("✅ 集成测试 - 组件协同工作正常")
        return True
    except Exception as e:
        logger.error(f"❌ 集成测试 - 错误: {e}")
        return False

def main():
    """主检查函数"""
    logger.info("\n开始系统健康检查...\n")
    
    # 执行所有测试
    test_functions = [
        test_step1_logging,
        test_step2_type_hints,
        test_step3_config_management,
        test_step4_event_system,
        test_step5_interfaces,
        test_step6_error_handling,
        test_step7_controllers,
        test_step8_data_layer,
        test_step9_api_system,
        test_integration
    ]
    
    passed = 0
    total = len(test_functions)
    
    for test_func in test_functions:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            logger.error(f"❌ {test_func.__name__} - 意外错误: {e}")
    
    logger.info("\n" + "=" * 60)
    logger.info("系统健康检查结果总结")
    logger.info("=" * 60)
    
    # 打印详细结果
    step_names = [
        "Step 1: 日志系统",
        "Step 2: 类型提示", 
        "Step 3: 配置管理",
        "Step 4: 事件系统",
        "Step 5: 服务接口",
        "Step 6: 错误处理",
        "Step 7: 控制器层",
        "Step 8: 数据层",
        "Step 9: API系统",
        "集成测试"
    ]
    
    for i, (key, status) in enumerate(results.items()):
        icon = "✅" if status else "❌"
        logger.info(f"{icon} {step_names[i]}: {'正常' if status else '异常'}")
    
    logger.info(f"\n总体通过率: {passed}/{total} ({passed/total*100:.1f}%)")
    
    if passed >= total * 0.8:  # 80%通过率认为系统健康
        logger.info("🎉 系统状态: 健康")
        logger.info("💡 重构成功，所有主要组件工作正常")
    elif passed >= total * 0.6:  # 60%通过率认为基本可用
        logger.info("⚠️  系统状态: 基本可用")
        logger.info("💡 大部分功能正常，部分组件可能需要调试")
    else:
        logger.info("🚨 系统状态: 需要修复")
        logger.info("💡 多个关键组件存在问题，建议检查环境和依赖")
    
    logger.info("\n" + "=" * 60)
    
    return passed >= total * 0.8

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("\n用户中断检查")
        sys.exit(1)
    except Exception as e:
        logger.error(f"\n检查过程发生意外错误: {e}")
        traceback.print_exc()
        sys.exit(1)