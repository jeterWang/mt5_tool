"""
控制器集成示例

展示如何在不修改现有MT5GUI代码的情况下集成控制器
"""

import sys
import os
import logging
logger = logging.getLogger(__name__)

# 添加路径
current_dir = os.path.dirname(__file__)
project_root = os.path.join(current_dir, '..', '..')
sys.path.insert(0, project_root)

from app.controllers.main_controller import MT5Controller, get_controller
from app.adapters.gui_adapter import MT5GUIAdapter, create_gui_adapter


class ControllerIntegrationExample:
    """控制器集成示例类"""
    
    def __init__(self):
        """初始化示例"""
        # print("=== MT5控制器集成示例 ===")
    
    def example_1_standalone_controller(self):
        """示例1: 独立使用控制器"""
        # print("\n1. 独立使用控制器")
        # print("-" * 30)
        
        # 创建控制器实例
        controller = MT5Controller()
        
        # 模拟初始化（实际使用中需要真实的trader和database）
        # print("  控制器创建成功")
        
        # 检查连接状态
        connected = controller.is_mt5_connected()
        # print(f"  MT5连接状态: {connected}")
        
        # 添加事件监听器
        def on_connection_change(data):
            pass
            # print(f"  事件触发: MT5连接变化 - {data}")
        
        controller.add_listener('mt5_connected', on_connection_change)
        # print("  事件监听器已添加")
        
        # 清理
        controller.cleanup()
        # print("  控制器已清理")
    
    def example_2_gui_adapter_usage(self):
        """示例2: GUI适配器使用"""
        # print("\n2. GUI适配器使用模式")
        # print("-" * 30)
        
        # 模拟GUI类
        class MockGUI:
            def __init__(self):
                self.trader = None  # 实际使用中会是MT5Trader实例
                self.db = None      # 实际使用中会是TradeDatabase实例
                self.status_bar = MockStatusBar()
            
            def connect_mt5(self):
                pass
                # print("    [原有方法] 连接MT5")
            
            def enable_trading_buttons(self):
                pass
                # print("    [原有方法] 启用交易按钮")
        
        class MockStatusBar:
            def showMessage(self, msg):
                pass
                # print(f"    [状态栏] {msg}")
        
        # 创建模拟GUI
        mock_gui = MockGUI()
        
        # 创建适配器
        adapter = MT5GUIAdapter(mock_gui)
        # print("  GUI适配器创建成功")
        
        # 检查控制器可用性
        available = adapter.is_controller_available()
        # print(f"  控制器可用性: {available}")
        
        # 启用控制器模式
        adapter.enable_controller_mode(True)
        # print("  控制器模式已启用")
        
        # 使用适配器方法
        success, message = adapter.connect_mt5_via_controller()
        # print(f"  连接结果: {success}, 消息: {message}")
        
        # 清理
        adapter.cleanup()
        # print("  适配器已清理")
    
    def example_3_gradual_migration(self):
        """示例3: 渐进式迁移策略"""
        # print("\n3. 渐进式迁移策略")
        # print("-" * 30)
        
        # 阶段1: 保持原有代码不变
        # print("  阶段1: 原有代码并行运行")
        # print("    - MT5GUI继续使用原有方法")
        # print("    - 控制器在后台静默运行")
        # print("    - 逐步添加事件监听")
        
        # 阶段2: 可选使用控制器
        # print("  阶段2: 可选使用控制器功能")
        # print("    - 通过适配器调用控制器方法")
        # print("    - 出错时自动回退到原有方法")
        # print("    - 新功能优先使用控制器")
        
        # 阶段3: 全面迁移
        # print("  阶段3: 全面迁移到控制器")
        # print("    - 所有业务逻辑通过控制器")
        # print("    - GUI只负责界面显示")
        # print("    - 清理旧的直接调用代码")
    
    def example_4_event_driven_architecture(self):
        """示例4: 事件驱动架构"""
        # print("\n4. 事件驱动架构示例")
        # print("-" * 30)
        
        # 创建控制器
        controller = get_controller()
        
        # 模拟多个监听器
        def ui_listener(data):
            pass
            # print(f"    [UI监听器] 收到数据: {data}")
        
        def log_listener(data):
            pass
            # print(f"    [日志监听器] 记录事件: {data}")
        
        def notification_listener(data):
            pass
            # print(f"    [通知监听器] 发送通知: {data}")
        
        # 注册监听器
        controller.add_listener('account_info_updated', ui_listener)
        controller.add_listener('account_info_updated', log_listener)
        controller.add_listener('positions_updated', notification_listener)
        
        # print("  事件监听器已注册")
        
        # 模拟事件触发
        controller._emit_event('account_info_updated', {'balance': 10000})
        controller._emit_event('positions_updated', {'count': 3})
        
        # print("  事件触发完成")
    
    def example_5_compatibility_verification(self):
        """示例5: 兼容性验证"""
        # print("\n5. 兼容性验证")
        # print("-" * 30)
        
        # 验证导入
        try:
            from app.controllers.main_controller import MT5Controller
            from app.adapters.gui_adapter import MT5GUIAdapter
            # print("  ✅ 模块导入成功")
        except ImportError as e:
            logger.error("[空日志]", f"  ❌ 模块导入失败: {e}")
            return
        
        # 验证实例化
        try:
            controller = MT5Controller()
            # print("  ✅ 控制器实例化成功")
        except Exception as e:
            logger.error("[空日志]", f"  ❌ 控制器实例化失败: {e}")
            return
        
        # 验证基本功能
        try:
            # 检查基本方法
            assert hasattr(controller, 'connect_mt5')
            assert hasattr(controller, 'get_account_info')
            assert hasattr(controller, 'get_all_positions')
            # print("  ✅ 基本功能验证成功")
        except AssertionError:
            logger.error("[空日志]", "  ❌ 基本功能验证失败")
            return
        
        # 验证事件系统
        try:
            callback_called = False
            
            def test_callback(data):
                nonlocal callback_called
                callback_called = True
            
            controller.add_listener('test_event', test_callback)
            controller._emit_event('test_event', {})
            
            assert callback_called
            # print("  ✅ 事件系统验证成功")
        except Exception as e:
            logger.error("[空日志]", f"  ❌ 事件系统验证失败: {e}")
            return
        
        # print("  ✅ 所有兼容性验证通过")
    
    def run_all_examples(self):
        """运行所有示例"""
        self.example_1_standalone_controller()
        self.example_2_gui_adapter_usage()
        self.example_3_gradual_migration()
        self.example_4_event_driven_architecture()
        self.example_5_compatibility_verification()
        
        # print("\n" + "="*50)
        # print("控制器集成示例完成!")
        # print()
        # print("核心优势:")
        # print("  - 100%向后兼容，不修改现有代码")
        # print("  - 支持渐进式迁移策略")
        # print("  - 事件驱动架构，松耦合设计")
        # print("  - 业务逻辑与UI逻辑分离")
        # print("  - 便于单元测试和维护")
        # print("="*50)


if __name__ == "__main__":
    example = ControllerIntegrationExample()
    example.run_all_examples()