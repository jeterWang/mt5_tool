"""
GUI适配器

为现有MT5GUI提供控制器集成，保持向后兼容
"""

from typing import Optional, Any, Callable
import logging

# 延迟导入避免循环依赖
# from app.controllers.main_controller import MT5Controller, get_controller
from app.utils.logger import get_logger

logger = get_logger()


class MT5GUIAdapter:
    """
    MT5GUI适配器
    
    在不修改现有MT5GUI代码的前提下，提供控制器功能
    """
    
    def __init__(self, gui_instance):
        """
        初始化适配器
        
        Args:
            gui_instance: MT5GUI实例
        """
        self.gui = gui_instance
        self.controller = None  # Optional[MT5Controller]
        self._initialized = False
        
    def initialize_controller(self) -> bool:
        """
        初始化控制器（如果GUI有trader和db属性）
        
        Returns:
            是否成功初始化
        """
        try:
            # 检查GUI是否有必要的属性
            if hasattr(self.gui, 'trader') and hasattr(self.gui, 'db'):
                from app.controllers.main_controller import initialize_controller
                self.controller = initialize_controller(self.gui.trader, self.gui.db)
                self._setup_event_listeners()
                self._initialized = True
                logger.info("[空日志]", "[空日志]", "GUI适配器初始化成功")
                return True
            else:
                logger.warning("[空日志]", "GUI缺少trader或db属性，无法初始化控制器")
                return False
        except Exception as e:
            logger.error("[空日志]", f"GUI适配器初始化失败: {e}")
            return False
    
    def _setup_event_listeners(self):
        """设置事件监听器"""
        if not self.controller:
            return
        
        # MT5连接事件
        self.controller.add_listener('mt5_connected', self._on_mt5_connected)
        self.controller.add_listener('mt5_disconnected', self._on_mt5_disconnected)
        
        # 数据更新事件
        self.controller.add_listener('account_info_updated', self._on_account_info_updated)
        self.controller.add_listener('positions_updated', self._on_positions_updated)
        self.controller.add_listener('symbols_updated', self._on_symbols_updated)
        
    def _on_mt5_connected(self, data):
        """MT5连接事件处理"""
        try:
            if hasattr(self.gui, 'enable_trading_buttons'):
                self.gui.enable_trading_buttons()
            if hasattr(self.gui, 'status_bar'):
                status = "连接成功" if data.get('success') else "连接失败"
                self.gui.status_bar.showMessage(status)
        except Exception as e:
            logger.error("[空日志]", f"处理MT5连接事件失败: {e}")
    
    def _on_mt5_disconnected(self, data):
        """MT5断开事件处理"""
        try:
            if hasattr(self.gui, 'status_bar'):
                self.gui.status_bar.showMessage("连接已断开")
        except Exception as e:
            logger.error("[空日志]", f"处理MT5断开事件失败: {e}")
    
    def _on_account_info_updated(self, data):
        """账户信息更新事件处理"""
        try:
            # 可以在这里触发GUI的账户信息更新
            logger.debug("[空日志]", "账户信息已更新")
        except Exception as e:
            logger.error("[空日志]", f"处理账户信息更新事件失败: {e}")
    
    def _on_positions_updated(self, data):
        """持仓更新事件处理"""
        try:
            # 可以在这里触发GUI的持仓表格更新
            logger.debug("[空日志]", "持仓信息已更新")
        except Exception as e:
            logger.error("[空日志]", f"处理持仓更新事件失败: {e}")
    
    def _on_symbols_updated(self, data):
        """品种更新事件处理"""
        try:
            # 可以在这里触发GUI的品种列表更新
            logger.debug("[空日志]", "品种列表已更新")
        except Exception as e:
            logger.error("[空日志]", f"处理品种更新事件失败: {e}")
    
    # ========== 委托方法 ==========
    
    def connect_mt5_via_controller(self) -> tuple[bool, str]:
        """
        通过控制器连接MT5
        
        Returns:
            tuple: (是否成功, 状态消息)
        """
        if not self.controller:
            # 回退到原有方法
            if hasattr(self.gui, 'connect_mt5'):
                try:
                    self.gui.connect_mt5()
                    return True, "连接成功（原有方式）"
                except:
                    return False, "连接失败（原有方式）"
            return False, "控制器未初始化"
        
        return self.controller.connect_mt5()
    
    def get_account_info_via_controller(self):
        """通过控制器获取账户信息"""
        if not self.controller:
            # 回退到原有方法
            if hasattr(self.gui, 'trader') and self.gui.trader:
                return self.gui.trader.get_account_info()
            return None
        
        return self.controller.get_account_info()
    
    def get_all_positions_via_controller(self):
        """通过控制器获取所有持仓"""
        if not self.controller:
            # 回退到原有方法
            if hasattr(self.gui, 'trader') and self.gui.trader:
                return self.gui.trader.get_all_positions()
            return []
        
        return self.controller.get_all_positions()
    
    def sync_closed_trades_via_controller(self) -> bool:
        """通过控制器同步交易"""
        if not self.controller:
            # 回退到原有方法
            if hasattr(self.gui, 'sync_closed_trades'):
                try:
                    self.gui.sync_closed_trades()
                    return True
                except:
                    return False
            return False
        
        return self.controller.sync_closed_trades()
    
    # ========== 便捷方法 ==========
    
    def is_controller_available(self) -> bool:
        """检查控制器是否可用"""
        return self._initialized and self.controller is not None
    
    def enable_controller_mode(self, enable: bool = True):
        """
        启用/禁用控制器模式
        
        Args:
            enable: 是否启用控制器模式
        """
        if enable and not self._initialized:
            self.initialize_controller()
        
        logger.info("[空日志]", "[空日志]", f"控制器模式{'启用' if enable else '禁用'}")
    
    def cleanup(self):
        """清理适配器资源"""
        if self.controller:
            self.controller.cleanup()
        logger.info("[空日志]", "[空日志]", "GUI适配器清理完成")


# ========== 工厂函数 ==========

def create_gui_adapter(gui_instance) -> MT5GUIAdapter:
    """
    创建GUI适配器
    
    Args:
        gui_instance: MT5GUI实例
        
    Returns:
        MT5GUIAdapter实例
    """
    adapter = MT5GUIAdapter(gui_instance)
    adapter.initialize_controller()
    return adapter


# ========== 装饰器支持 ==========

def with_controller(method_name: str):
    """
    装饰器：为GUI方法添加控制器支持
    
    Args:
        method_name: 控制器中对应的方法名
    """
    def decorator(gui_method):
        def wrapper(self, *args, **kwargs):
            # 检查是否有适配器
            if hasattr(self, '_adapter') and self._adapter.is_controller_available():
                controller_method = getattr(self._adapter.controller, method_name, None)
                if controller_method:
                    try:
                        return controller_method(*args, **kwargs)
                    except Exception as e:
                        logger.error("[空日志]", f"控制器方法{method_name}执行失败: {e}")
            
            # 回退到原有方法
            return gui_method(self, *args, **kwargs)
        
        return wrapper
    return decorator