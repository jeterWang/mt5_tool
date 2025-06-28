"""
MT5数据同步模块

负责交易记录的同步和处理
"""

import MetaTrader5 as mt5
import pandas as pd
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import sqlite3

from utils.paths import get_data_path
from config.loader import Delta_TIMEZONE, TRADING_DAY_RESET_HOUR


def get_trading_day_from_datetime(dt):
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


def sync_closed_trades_to_db(account_id, db_path=None):
    """
    扫描近3天所有平仓单（包括自动止损/止盈），并将未记录过的平仓单写入trade_history表。
    只用order_id（position_id）去重。
    建议每分钟调用一次。

    Args:
        account_id: 账号ID
        db_path: 数据库路径（可选，默认与TradeDatabase一致）

    Returns:
        是否有新的平仓记录
    """
    try:
        start_time = datetime.now() - timedelta(days=3)
        end_time = datetime.now() + timedelta(days=1)
        deals = mt5.history_deals_get(start_time, end_time)
        if deals is None:
            return False

        # 数据库路径
        if db_path is None:
            from utils.paths import get_data_path

            db_path = get_data_path("trade_history.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 读取已记录的order_id
        cursor.execute("SELECT order_id FROM trade_history")
        recorded_order_ids = set(str(row[0]) for row in cursor.fetchall())

        new_records = []
        tz_delta = Delta_TIMEZONE
        for deal in deals:
            if deal.entry != mt5.DEAL_ENTRY_OUT:
                continue
            order_id = str(deal.position_id)
            if order_id in recorded_order_ids:
                continue

            # 获取开仓deal
            open_deal = None
            for d in deals:
                if (
                    hasattr(d, "position_id")
                    and d.position_id == deal.position_id
                    and d.entry == mt5.DEAL_ENTRY_IN
                ):
                    open_deal = d
                    break

            open_time = (
                datetime.fromtimestamp(open_deal.time + tz_delta * 3600)
                if open_deal
                else ""
            )
            open_price = open_deal.price if open_deal else ""
            close_time = datetime.fromtimestamp(deal.time + tz_delta * 3600)
            trading_day = get_trading_day_from_datetime(close_time)
            close_price = deal.price
            profit = deal.profit
            direction = "buy" if deal.type == mt5.ORDER_TYPE_BUY else "sell"
            close_info = (
                order_id,
                str(account_id),
                deal.symbol,
                deal.volume,
                direction,
                open_time.strftime("%Y-%m-%d %H:%M:%S") if open_time else "",
                close_time.strftime("%Y-%m-%d %H:%M:%S"),
                trading_day,
                open_price,
                close_price,
                profit,
                deal.comment,
            )
            new_records.append(close_info)

        if new_records:
            cursor.executemany(
                """
                INSERT OR IGNORE INTO trade_history (
                    order_id, account, symbol, volume, direction, open_time, close_time, trading_day, open_price, close_price, profit, comment
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                new_records,
            )
            conn.commit()
            conn.close()
            return True
        conn.close()
        return False
    except Exception as e:
        # print(f"同步平仓记录到DB出错: {str(e)}")
        return False
