"""
MT5交易核心模块

提供与MetaTrader5平台的基础连接和账户操作
"""

import MetaTrader5 as mt5
import logging

logger = logging.getLogger(__name__)
from datetime import datetime, timedelta
import os
from typing import Dict, List, Optional
from dotenv import load_dotenv

from utils.paths import get_data_path
from config.loader import Delta_TIMEZONE, SYMBOLS, TRADING_DAY_RESET_HOUR
from app.trader.symbol_info import get_symbol_params, get_all_symbols
from app.trader.orders import (
    place_order,
    place_order_with_tp_sl,
    place_order_with_key_level_sl,
)
from app.trader.orders import (
    place_pending_order,
    place_order_with_partial_tp,
    close_position,
)
from app.trader.orders import cancel_order, modify_position_sl_tp
from app.trader.data_sync import sync_closed_trades_to_db


class MT5Trader:
    """
    MT5交易类

    提供MT5交易平台的基础连接和账户操作
    """

    def __init__(self):
        """初始化交易者"""
        self.connected = False
        # 加载环境变量
        load_dotenv()

    def connect(self) -> bool:
        """连接到MT5"""
        try:
            # 初始化MT5
            if not mt5.initialize():
                return False

            # 检查是否已经登录
            account_info = mt5.account_info()
            if account_info is None:
                return False

            self.connected = True
            return True
        except Exception as e:
            return False

    def disconnect(self):
        """断开MT5连接"""
        mt5.shutdown()
        self.connected = False

    def is_connected(self) -> bool:
        """检查是否已连接到MT5"""
        return self.connected

    def get_account_info(self) -> Optional[Dict]:
        """
        获取账户信息

        Returns:
            账户信息字典，包含余额、净值、保证金等
        """
        try:
            account_info = mt5.account_info()
            if account_info is None:
                return None
            return {
                "balance": account_info.balance,
                "equity": account_info.equity,
                "margin": account_info.margin,
                "free_margin": account_info.margin_free,
                "margin_level": account_info.margin_level,
            }
        except Exception as e:
            logger.error("[空日志]", f"获取账户信息失败: {str(e)}")
            return None

    def get_all_positions(self) -> List[Dict]:
        """
        获取所有持仓信息

        Returns:
            持仓信息列表，无持仓或出错返回空列表
        """
        if not self.connected:
            return []

        try:
            positions = mt5.positions_get()
            if positions is None:
                return []

            return [position._asdict() for position in positions]
        except Exception as e:
            # print(f"获取持仓信息出错：{str(e)}")
            return []

    def get_position(self, ticket: int) -> Optional[Dict]:
        """
        获取持仓信息

        Args:
            ticket: 订单号

        Returns:
            持仓信息字典，未找到返回None
        """
        position = mt5.positions_get(ticket=ticket)
        if not position:
            return None
        return position[0]._asdict()

    def _get_account_id(self):
        """获取当前登录的MT5账号ID"""
        info = mt5.account_info()
        return info.login if info else "unknown"

    def get_trading_day(self):
        """
        获取当前交易日，考虑重置时间

        Returns:
            交易日期字符串，格式为YYYY-MM-DD
        """
        now = datetime.now()
        # 如果当前时间已经过了重置时间，使用当天日期，否则使用前一天日期
        if now.hour >= TRADING_DAY_RESET_HOUR:
            return now.strftime("%Y-%m-%d")
        else:
            yesterday = now - timedelta(days=1)
            return yesterday.strftime("%Y-%m-%d")

    def get_trading_day_from_datetime(self, dt):
        """
        从指定时间获取交易日

        Args:
            dt: 日期时间对象

        Returns:
            交易日期字符串，格式为YYYY-MM-DD
        """
        # 如果当前时间已经过了重置时间，使用当天日期，否则使用前一天日期
        if dt.hour >= TRADING_DAY_RESET_HOUR:
            return dt.strftime("%Y-%m-%d")
        else:
            yesterday = dt - timedelta(days=1)
            return yesterday.strftime("%Y-%m-%d")

    # 委托订单操作方法
    def place_order(self, *args, **kwargs):
        """下单函数"""
        return place_order(*args, **kwargs)

    def place_order_with_tp_sl(self, *args, **kwargs):
        """下带止损止盈的订单"""
        return place_order_with_tp_sl(*args, **kwargs)

    def place_order_with_key_level_sl(self, *args, **kwargs):
        """下带K线关键位止损的订单"""
        return place_order_with_key_level_sl(*args, **kwargs)

    def place_pending_order(self, *args, **kwargs):
        """下挂单"""
        return place_pending_order(*args, **kwargs)

    def place_order_with_partial_tp(self, *args, **kwargs):
        """下带分批止盈的订单"""
        return place_order_with_partial_tp(*args, **kwargs)

    def close_position(self, ticket: int) -> bool:
        """平仓"""
        return close_position(ticket)

    def cancel_order(self, ticket: int) -> bool:
        """撤销挂单"""
        return cancel_order(ticket)

    def modify_position_sl_tp(
        self, ticket: int, sl: float = None, tp: float = None
    ) -> bool:
        """修改持仓的止损止盈"""
        return modify_position_sl_tp(ticket, sl, tp)

    # 交易品种信息方法
    def get_symbol_params(self, symbol: str) -> Dict:
        """获取交易品种参数"""
        return get_symbol_params(symbol, self.connected)

    def get_all_symbols(self) -> List[str]:
        """获取所有可交易品种"""
        return get_all_symbols(self.connected)

    def get_positions_by_symbol_and_type(
        self, symbol: str, order_type: str
    ) -> List[Dict]:
        """
        获取指定品种和方向的所有持仓

        Args:
            symbol: 交易品种
            order_type: 订单方向（'buy' 或 'sell'）

        Returns:
            满足条件的持仓列表
        """
        if not self.connected:
            return []
        try:
            positions = mt5.positions_get(symbol=symbol)
            if positions is None:
                return []
            mt5_type = (
                mt5.POSITION_TYPE_BUY if order_type == "buy" else mt5.POSITION_TYPE_SELL
            )
            return [p._asdict() for p in positions if p.type == mt5_type]
        except Exception as e:
            # print(f"获取指定品种和方向持仓出错：{str(e)}")
            return []

    def get_all_pending_orders(self) -> list:
        """
        获取所有挂单信息，结构与持仓兼容，增加status字段
        Returns:
            挂单信息列表
        """
        if not self.connected:
            return []
        try:
            orders = mt5.orders_get()
            if orders is None:
                return []
            result = []
            for order in orders:
                d = order._asdict()
                d["status"] = "挂单"
                # 字段兼容处理
                d.setdefault("profit", "-")
                d.setdefault("price_open", d.get("price_open", d.get("price", "-")))
                d.setdefault(
                    "volume", d.get("volume_current", d.get("volume_initial", 0))
                )
                d.setdefault("type", d.get("type", "-"))
                d.setdefault("ticket", d.get("ticket", "-"))
                d.setdefault("symbol", d.get("symbol", "-"))
                result.append(d)
            return result
        except Exception as e:
            return []

    def sync_closed_trades_to_db(self, days=365, batch_days=30):
        """
        自动同步当前账号的平仓单到数据库
        Args:
            days: 目标同步天数（默认一年）
            batch_days: 每批拉取天数（默认30天）
        Returns:
            是否有新平仓记录
        """
        account_id = self._get_account_id()
        try:
            return sync_closed_trades_to_db(
                account_id, days=days, batch_days=batch_days
            )
        except Exception as e:
            logger.error("[自动同步] 交易历史同步到数据库失败: %s", str(e))
            return False
