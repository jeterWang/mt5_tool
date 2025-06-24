"""
事件系统使用示例

展示如何在现有代码中逐步引入事件系统
所有示例都与现有代码并行，不影响原有功能
"""

from app.utils.event_bus import get_event_bus, EventType, publish, subscribe
from app.utils.logger import get_logger

logger = get_logger(__name__)


class EventDrivenAccountInfo:
    """
    基于事件的账户信息组件示例
    
    这个类展示了如何使用事件系统重构账户信息组件
    它与现有的 AccountInfoSection 并行工作
    """
    
    def __init__(self):
        """初始化事件驱动的账户信息组件"""
        self.bus = get_event_bus()
        self._setup_event_listeners()
        logger.info("[空日志]", "[空日志]", "事件驱动账户信息组件已初始化")
    
    def _setup_event_listeners(self):
        """设置事件监听器"""
        # 监听MT5连接事件
        self.bus.subscribe(EventType.MT5_CONNECTED, self._on_mt5_connected, use_weak_ref=False)
        
        # 监听账户信息更新事件
        self.bus.subscribe(EventType.ACCOUNT_INFO_UPDATED, self._on_account_updated, use_weak_ref=False)
        
        # 监听交易数量更新事件
        self.bus.subscribe(EventType.TRADE_COUNT_UPDATED, self._on_trade_count_updated, use_weak_ref=False)
    
    def _on_mt5_connected(self, event):
        """处理MT5连接事件"""
        logger.info("[空日志]", "[空日志]", f"检测到MT5连接事件: {event.data}")
        # 这里可以自动更新账户信息，而不需要被主窗口直接调用
        # print("事件驱动：MT5连接成功，自动更新账户信息")
    
    def _on_account_updated(self, event):
        """处理账户信息更新事件"""
        account_data = event.data
        logger.info("[空日志]", "[空日志]", f"账户信息已更新: {account_data}")
        # print(f"事件驱动：账户余额 {account_data.get('balance', 'N/A')}")
    
    def _on_trade_count_updated(self, event):
        """处理交易数量更新事件"""
        trade_data = event.data
        logger.info("[空日志]", "[空日志]", f"交易数量已更新: {trade_data}")
        # print(f"事件驱动：今日交易 {trade_data.get('count', 0)} 次")


class EventDrivenConfigManager:
    """
    基于事件的配置管理器示例
    
    展示如何在配置变更时自动通知相关组件
    """
    
    def __init__(self):
        """初始化事件驱动配置管理器"""
        self.bus = get_event_bus()
        logger.info("[空日志]", "[空日志]", "事件驱动配置管理器已初始化")
    
    def update_symbols(self, new_symbols):
        """
        更新交易品种列表（示例方法）
        
        这个方法展示了如何在配置更新时发布事件
        而不是直接调用其他组件的方法
        """
        # 原来的方式：直接调用其他组件
        # batch_order.update_symbol_params(symbol_params)
        # trading_settings.update_symbols_list(trader)
        
        # 新的方式：发布事件，让相关组件自己响应
        publish(
            EventType.SYMBOLS_UPDATED,
            {"symbols": new_symbols, "timestamp": "2025-06-24"},
            source="ConfigManager"
        )
        
        logger.info("[空日志]", "[空日志]", f"已发布品种更新事件: {new_symbols}")
        # print("事件驱动：品种列表已更新，相关组件将自动响应")
    
    def update_sl_mode(self, new_mode):
        """更新止损模式（示例方法）"""
        publish(
            EventType.SL_MODE_CHANGED,
            {"mode": new_mode, "previous_mode": "old_mode"},
            source="ConfigManager"
        )
        
        logger.info("[空日志]", "[空日志]", f"已发布止损模式变更事件: {new_mode}")
        # print(f"事件驱动：止损模式已改为 {new_mode}")


def demonstrate_event_system():
    """
    演示事件系统的使用
    
    这个函数展示了事件系统如何工作
    可以在开发时调用来测试事件流
    """
    # print("\n=== 事件系统演示开始 ===")
    
    # 创建事件驱动组件
    account_info = EventDrivenAccountInfo()
    config_manager = EventDrivenConfigManager()
    
    # print("\n1. 模拟MT5连接事件")
    publish(
        EventType.MT5_CONNECTED,
        {"account_id": "12345", "server": "demo-server"},
        source="MT5Trader"
    )
    
    # print("\n2. 模拟账户信息更新")
    publish(
        EventType.ACCOUNT_INFO_UPDATED,
        {"balance": 10000.0, "equity": 10000.0, "margin": 0.0},
        source="MT5Trader"
    )
    
    # print("\n3. 模拟配置更新")
    config_manager.update_symbols(["EURUSD", "GBPUSD", "USDJPY"])
    config_manager.update_sl_mode("fixed_points")
    
    # print("\n4. 查看事件历史")
    bus = get_event_bus()
    history = bus.get_event_history(limit=5)
    for event in history:
        pass
        # print(f"  - {event}")
    
    # print("\n=== 事件系统演示结束 ===\n")


def integrate_with_existing_main_window():
    """
    展示如何在现有的主窗口中集成事件系统
    
    这个函数展示了集成方法，但不会真正修改现有代码
    """
    # print("\n=== 现有代码集成示例 ===")
    # print("""
    在现有的 MT5GUI 类中，可以这样添加事件支持：
    
    # 在 __init__ 方法中
    def __init__(self):
        # ... 现有代码不变 ...
        
        # 可选：初始化事件系统
        self.use_events = True  # 可以通过配置控制
        if self.use_events:
            self.event_bus = get_event_bus()
            self._setup_event_listeners()
    
    # 在 connect_mt5 方法中
    def connect_mt5(self):
        # ... 现有代码不变 ...
        
        if self.trader.connect():
            # 原有代码继续工作
            self.status_bar.showMessage("MT5连接成功！")
            self.update_account_info()
            
            # 可选：发布事件，让其他组件也能响应
            if hasattr(self, 'use_events') and self.use_events:
                publish(EventType.MT5_CONNECTED, {
                    "account_id": self.trader._get_account_id()
                }, source="MainWindow")
    
    这样，原有功能完全不受影响，但新功能可以使用事件系统！
    """)
    # print("=== 集成示例结束 ===\n")


if __name__ == "__main__":
    # 如果直接运行这个文件，就演示事件系统
    demonstrate_event_system()
    integrate_with_existing_main_window()