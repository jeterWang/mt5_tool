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


def get_db_close_time_range(account_id, db_path=None):
    """
    查询数据库中该账户的最早和最晚close_time，返回(datetime_min, datetime_max)
    """
    if db_path is None:
        db_path = get_data_path("trade_history.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT MIN(close_time), MAX(close_time) FROM trade_history WHERE account=?",
        (str(account_id),),
    )
    result = cursor.fetchone()
    conn.close()
    min_time, max_time = result if result else (None, None)

    def parse_time(s):
        try:
            return datetime.strptime(s, "%Y-%m-%d %H:%M:%S") if s else None
        except Exception:
            return None

    return parse_time(min_time), parse_time(max_time)


def sync_closed_trades_to_db(account_id, db_path=None, days=365, batch_days=30):
    """
    同步近一年所有平仓单，仅补齐数据库缺失区间，分批拉取，避免重复。
    Args:
        account_id: 账号ID
        db_path: 数据库路径
        days: 目标同步天数（默认一年）
        batch_days: 每批拉取天数（默认30天）
    Returns:
        是否有新平仓记录
    """
    if db_path is None:
        db_path = get_data_path("trade_history.db")
    now = datetime.now()
    start_time = now - timedelta(days=days)
    end_time = now
    db_min, db_max = get_db_close_time_range(account_id, db_path)
    # 只同步缺失区间
    sync_ranges = []
    if db_min is None or db_min > start_time:
        sync_ranges.append((start_time, db_min or end_time))
    if db_max is None or db_max < end_time:
        sync_ranges.append((db_max or start_time, end_time))
    # 合并重叠区间
    sync_ranges = [(s, e) for s, e in sync_ranges if s < e]
    if not sync_ranges:
        return False  # 已覆盖，无需同步
    has_new = False
    for s, e in sync_ranges:
        batch_start = s
        while batch_start < e:
            batch_end = min(batch_start + timedelta(days=batch_days), e)
            deals = mt5.history_deals_get(batch_start, batch_end)
            if deals is None:
                batch_start = batch_end
                continue
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT order_id FROM trade_history WHERE account=?", (str(account_id),)
            )
            recorded_order_ids = set(str(row[0]) for row in cursor.fetchall())
            new_records = []
            tz_delta = Delta_TIMEZONE
            for deal in deals:
                if deal.entry != mt5.DEAL_ENTRY_OUT:
                    continue
                order_id = str(deal.position_id)
                if order_id in recorded_order_ids:
                    continue
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
                has_new = True
            conn.close()
            batch_start = batch_end
    return has_new
