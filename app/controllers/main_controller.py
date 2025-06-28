"""
主控制器类

分离业务逻辑和UI逻辑，提供中介层
"""

import logging
from typing import Optional, Dict, Any, List
from datetime import datetime

# 使用类型注解，避免直接导入可能有依赖问题的模块
# from app.trader.core import MT5Trader
# from app.database.models import TradeDatabase
from app.utils.logger import get_logger

# 获取Logger实例
logger = get_logger(__name__)


class MT5Controller:
    """
    MT5主控制器

    负责协调业务逻辑，分离UI和业务关注点
    """

    def __init__(self):
        """初始化控制器"""
        self.trader = None  # Optional[MT5Trader]
        self.database = None  # Optional[TradeDatabase]
        self._listeners: Dict[str, List] = {}

    def initialize(self, trader, database) -> None:
        """
        初始化控制器依赖

        Args:
            trader: MT5交易者实例
            database: 数据库实例
        """
        self.trader = trader
        self.database = database
        logger.info("[空日志]", "[空日志]", "MT5Controller初始化完成")

    # ========== 事件监听器管理 ==========

    def add_listener(self, event_type: str, callback) -> None:
        """添加事件监听器"""
        if event_type not in self._listeners:
            self._listeners[event_type] = []
        self._listeners[event_type].append(callback)

    def remove_listener(self, event_type: str, callback) -> None:
        """移除事件监听器"""
        if event_type in self._listeners:
            try:
                self._listeners[event_type].remove(callback)
            except ValueError:
                pass

    def _emit_event(self, event_type: str, data: Any = None) -> None:
        """触发事件"""
        if event_type in self._listeners:
            for callback in self._listeners[event_type]:
                try:
                    callback(data)
                except Exception as e:
                    logger.error("[空日志]", f"事件处理器执行失败: {e}")

    # ========== MT5连接管理 ==========

    def connect_mt5(self) -> tuple[bool, str]:
        """
        连接MT5终端

        Returns:
            tuple: (是否成功, 状态消息)
        """
        if not self.trader:
            return False, "交易者未初始化"

        try:
            success = self.trader.connect()
            if success:
                message = "MT5连接成功"
                self._emit_event("mt5_connected", {"success": True})
                logger.info("[空日志]", "[空日志]", message)
                return True, message
            else:
                message = "MT5连接失败"
                self._emit_event("mt5_connected", {"success": False})
                logger.warning("[空日志]", message)
                return False, message
        except Exception as e:
            message = f"MT5连接异常: {e}"
            logger.error("[空日志]", message)
            return False, message

    def is_mt5_connected(self) -> bool:
        """检查MT5是否已连接"""
        if not self.trader:
            return False
        return self.trader.is_connected()

    def disconnect_mt5(self) -> None:
        """断开MT5连接"""
        if self.trader:
            self.trader.disconnect()
            self._emit_event("mt5_disconnected", {})
            logger.info("[空日志]", "[空日志]", "MT5连接已断开")

    # ========== 账户信息管理 ==========

    def get_account_info(self) -> Optional[Dict[str, Any]]:
        """
        获取账户信息

        Returns:
            账户信息字典或None
        """
        if not self.trader or not self.trader.is_connected():
            return None

        try:
            account_info = self.trader.get_account_info()
            self._emit_event("account_info_updated", account_info)
            return account_info
        except Exception as e:
            logger.error("[空日志]", f"获取账户信息失败: {e}")
            return None

    # ========== 持仓管理 ==========

    def get_all_positions(self) -> List[Dict[str, Any]]:
        """
        获取所有持仓

        Returns:
            持仓列表
        """
        if not self.trader or not self.trader.is_connected():
            return []

        try:
            positions = self.trader.get_all_positions()
            self._emit_event("positions_updated", positions)
            return positions
        except Exception as e:
            logger.error("[空日志]", f"获取持仓信息失败: {e}")
            return []

    def get_position(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        获取指定品种的持仓

        Args:
            symbol: 交易品种

        Returns:
            持仓信息或None
        """
        if not self.trader or not self.trader.is_connected():
            return None

        try:
            return self.trader.get_position(symbol)
        except Exception as e:
            logger.error("[空日志]", f"获取{symbol}持仓失败: {e}")
            return None

    # ========== 交易品种管理 ==========

    def get_all_symbols(self) -> List[str]:
        """
        获取所有可交易品种

        Returns:
            品种列表
        """
        if not self.trader or not self.trader.is_connected():
            return []

        try:
            symbols = self.trader.get_all_symbols()
            self._emit_event("symbols_updated", symbols)
            return symbols
        except Exception as e:
            logger.error("[空日志]", f"获取交易品种失败: {e}")
            return []

    def get_symbol_params(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        获取品种参数

        Args:
            symbol: 交易品种

        Returns:
            品种参数或None
        """
        if not self.trader or not self.trader.is_connected():
            return None

        try:
            return self.trader.get_symbol_params(symbol)
        except Exception as e:
            logger.error("[空日志]", f"获取{symbol}品种参数失败: {e}")
            return None

    # ========== 数据库操作 ==========

    def sync_closed_trades(self) -> bool:
        """
        同步已平仓交易到数据库

        Returns:
            是否成功
        """
        if not self.trader or not self.database:
            return False

        try:
            self.trader.sync_closed_trades_to_excel()
            self._emit_event("trades_synced", {})
            logger.info("[空日志]", "[空日志]", "交易同步完成")
            return True
        except Exception as e:
            logger.error("[空日志]", f"交易同步失败: {e}")
            return False

    # ========== 风控相关 ==========

    def check_daily_loss_limit(self) -> tuple[bool, float]:
        """
        检查日内亏损限制

        Returns:
            tuple: (是否触发限制, 当前亏损金额)
        """
        try:
            # 这里需要实现具体的风控逻辑
            # 暂时返回默认值
            return False, 0.0
        except Exception as e:
            logger.error("[空日志]", f"检查亏损限制失败: {e}")
            return False, 0.0

    def get_trading_day(self) -> str:
        """
        获取当前交易日

        Returns:
            交易日字符串
        """
        if not self.trader:
            return datetime.now().strftime("%Y-%m-%d")

        try:
            return self.trader.get_trading_day()
        except Exception as e:
            logger.error("[空日志]", f"获取交易日失败: {e}")
            return datetime.now().strftime("%Y-%m-%d")

    # ========== 统计信息 ==========

    def get_daily_pnl_info(self) -> Dict[str, Any]:
        """
        获取日内盈亏信息

        Returns:
            盈亏信息字典
        """
        try:
            # 这里需要实现具体的盈亏计算逻辑
            # 暂时返回默认值
            return {
                "daily_pnl": 0.0,
                "daily_profit": 0.0,
                "daily_loss": 0.0,
                "trade_count": 0,
            }
        except Exception as e:
            logger.error("[空日志]", f"获取盈亏信息失败: {e}")
            return {}

    # ========== 清理资源 ==========

    def cleanup(self) -> None:
        """清理控制器资源"""
        self.disconnect_mt5()
        self._listeners.clear()
        logger.info("[空日志]", "[空日志]", "MT5Controller资源清理完成")


# ========== 全局控制器实例 ==========

_global_controller: Optional[MT5Controller] = None


def get_controller() -> MT5Controller:
    """
    获取全局控制器实例

    Returns:
        MT5Controller实例
    """
    global _global_controller
    if _global_controller is None:
        _global_controller = MT5Controller()
    return _global_controller


def initialize_controller(trader, database):
    """
    初始化全局控制器

    Args:
        trader: MT5交易者实例
        database: 数据库实例

    Returns:
        初始化的控制器实例
    """
    controller = get_controller()
    controller.initialize(trader, database)
    return controller
