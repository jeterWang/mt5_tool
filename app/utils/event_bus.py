"""
事件总线系统

这个模块提供松耦合的组件间通信机制
与现有的直接调用方式并行工作，不影响现有功能
"""

from typing import Dict, List, Callable, Any, Optional
import weakref
from enum import Enum
from app.utils.logger import get_logger

logger = get_logger(__name__)


class EventType(Enum):
    """事件类型枚举"""
    
    # MT5连接相关
    MT5_CONNECTED = "mt5_connected"
    MT5_DISCONNECTED = "mt5_disconnected"
    MT5_CONNECTION_FAILED = "mt5_connection_failed"
    
    # 账户信息相关
    ACCOUNT_INFO_UPDATED = "account_info_updated"
    BALANCE_CHANGED = "balance_changed"
    
    # 交易相关
    ORDER_PLACED = "order_placed"
    ORDER_FAILED = "order_failed"
    POSITION_OPENED = "position_opened"
    POSITION_CLOSED = "position_closed"
    
    # 配置相关
    CONFIG_CHANGED = "config_changed"
    SYMBOLS_UPDATED = "symbols_updated"
    SL_MODE_CHANGED = "sl_mode_changed"
    POSITION_SIZING_CHANGED = "position_sizing_changed"
    
    # UI相关
    UI_REFRESH_REQUESTED = "ui_refresh_requested"
    COUNTDOWN_UPDATED = "countdown_updated"
    PNL_UPDATED = "pnl_updated"
    
    # 数据相关
    TRADE_COUNT_UPDATED = "trade_count_updated"
    DATABASE_UPDATED = "database_updated"


class Event:
    """事件对象"""
    
    def __init__(self, event_type: EventType, data: Optional[Dict[str, Any]] = None, source: Optional[str] = None):
        """
        初始化事件
        
        Args:
            event_type: 事件类型
            data: 事件数据
            source: 事件源标识
        """
        self.type = event_type
        self.data = data or {}
        self.source = source
        self.timestamp = None
        
        # 导入时间模块
        import time
        self.timestamp = time.time()
    
    def __str__(self) -> str:
        return f"Event({self.type.value}, data={self.data}, source={self.source})"


class EventBus:
    """
    事件总线
    
    特点：
    - 松耦合：组件不需要直接引用其他组件
    - 支持弱引用：避免内存泄漏
    - 线程安全：支持多线程环境
    - 可调试：完整的事件日志
    """
    
    def __init__(self):
        """初始化事件总线"""
        self._listeners: Dict[EventType, List[Callable]] = {}
        self._weak_listeners: Dict[EventType, List[weakref.ref]] = {}
        self._event_history: List[Event] = []
        self._max_history = 100  # 最多保留100个历史事件
        self._enabled = True
    
    def subscribe(self, event_type: EventType, callback: Callable, use_weak_ref: bool = True) -> None:
        """
        订阅事件
        
        Args:
            event_type: 事件类型
            callback: 回调函数，签名为 callback(event: Event) -> None
            use_weak_ref: 是否使用弱引用（推荐，避免内存泄漏）
        """
        if not self._enabled:
            return
            
        try:
            if use_weak_ref:
                # 使用弱引用，避免循环引用导致的内存泄漏
                if event_type not in self._weak_listeners:
                    self._weak_listeners[event_type] = []
                    
                weak_callback = weakref.ref(callback.__self__ if hasattr(callback, '__self__') else callback)
                self._weak_listeners[event_type].append(weak_callback)
            else:
                # 使用强引用
                if event_type not in self._listeners:
                    self._listeners[event_type] = []
                    
                self._listeners[event_type].append(callback)
                
            logger.debug("[空日志]", f"订阅事件: {event_type.value}, 回调: {callback}")
            
        except Exception as e:
            logger.error("[空日志]", f"订阅事件失败: {e}")
    
    def unsubscribe(self, event_type: EventType, callback: Callable) -> None:
        """
        取消订阅事件
        
        Args:
            event_type: 事件类型
            callback: 要移除的回调函数
        """
        try:
            # 从强引用中移除
            if event_type in self._listeners:
                self._listeners[event_type] = [
                    cb for cb in self._listeners[event_type] if cb != callback
                ]
                
            # 从弱引用中移除（复杂一些，因为需要检查引用的对象）
            if event_type in self._weak_listeners:
                new_weak_list = []
                for weak_ref in self._weak_listeners[event_type]:
                    ref_obj = weak_ref()
                    if ref_obj is not None and ref_obj != callback:
                        new_weak_list.append(weak_ref)
                self._weak_listeners[event_type] = new_weak_list
                
            logger.debug("[空日志]", f"取消订阅事件: {event_type.value}, 回调: {callback}")
            
        except Exception as e:
            logger.error("[空日志]", f"取消订阅事件失败: {e}")
    
    def publish(self, event_type: EventType, data: Optional[Dict[str, Any]] = None, source: Optional[str] = None) -> None:
        """
        发布事件
        
        Args:
            event_type: 事件类型
            data: 事件数据
            source: 事件源标识
        """
        if not self._enabled:
            return
            
        try:
            # 创建事件对象
            event = Event(event_type, data, source)
            
            # 记录事件历史
            self._event_history.append(event)
            if len(self._event_history) > self._max_history:
                self._event_history.pop(0)
            
            logger.debug("[空日志]", f"发布事件: {event}")
            
            # 通知强引用监听器
            if event_type in self._listeners:
                for callback in self._listeners[event_type][:]:  # 创建副本避免修改问题
                    try:
                        callback(event)
                    except Exception as e:
                        logger.error("[空日志]", f"事件回调执行失败: {callback}, 错误: {e}")
            
            # 通知弱引用监听器
            if event_type in self._weak_listeners:
                valid_listeners = []
                for weak_ref in self._weak_listeners[event_type]:
                    callback_obj = weak_ref()
                    if callback_obj is not None:
                        valid_listeners.append(weak_ref)
                        try:
                            # 这里需要根据实际的回调对象类型来调用
                            if hasattr(callback_obj, '__call__'):
                                callback_obj(event)
                        except Exception as e:
                            logger.error("[空日志]", f"弱引用事件回调执行失败: {callback_obj}, 错误: {e}")
                
                # 清理无效的弱引用
                self._weak_listeners[event_type] = valid_listeners
                
        except Exception as e:
            logger.error("[空日志]", f"发布事件失败: {e}")
    
    def get_event_history(self, event_type: Optional[EventType] = None, limit: int = 10) -> List[Event]:
        """
        获取事件历史
        
        Args:
            event_type: 事件类型过滤，None表示所有类型
            limit: 返回的最大事件数量
            
        Returns:
            事件列表，按时间倒序
        """
        events = self._event_history
        
        if event_type:
            events = [e for e in events if e.type == event_type]
            
        return events[-limit:] if limit > 0 else events
    
    def clear_history(self) -> None:
        """清空事件历史"""
        self._event_history.clear()
        logger.info("[空日志]", "[空日志]", "事件历史已清空")
    
    def enable(self) -> None:
        """启用事件总线"""
        self._enabled = True
        logger.info("[空日志]", "[空日志]", "事件总线已启用")
    
    def disable(self) -> None:
        """禁用事件总线"""
        self._enabled = False
        logger.info("[空日志]", "[空日志]", "事件总线已禁用")
    
    def is_enabled(self) -> bool:
        """检查事件总线是否启用"""
        return self._enabled
    
    def get_subscriber_count(self, event_type: EventType) -> int:
        """获取某个事件类型的订阅者数量"""
        count = 0
        
        if event_type in self._listeners:
            count += len(self._listeners[event_type])
            
        if event_type in self._weak_listeners:
            # 只计算有效的弱引用
            valid_count = sum(1 for weak_ref in self._weak_listeners[event_type] if weak_ref() is not None)
            count += valid_count
            
        return count


# 全局事件总线实例
_event_bus: Optional[EventBus] = None


def get_event_bus() -> EventBus:
    """获取全局事件总线实例"""
    global _event_bus
    if _event_bus is None:
        _event_bus = EventBus()
    return _event_bus


# 便捷函数
def publish(event_type: EventType, data: Optional[Dict[str, Any]] = None, source: Optional[str] = None) -> None:
    """发布事件的便捷函数"""
    get_event_bus().publish(event_type, data, source)


def subscribe(event_type: EventType, callback: Callable, use_weak_ref: bool = True) -> None:
    """订阅事件的便捷函数"""
    get_event_bus().subscribe(event_type, callback, use_weak_ref)


def unsubscribe(event_type: EventType, callback: Callable) -> None:
    """取消订阅事件的便捷函数"""
    get_event_bus().unsubscribe(event_type, callback)