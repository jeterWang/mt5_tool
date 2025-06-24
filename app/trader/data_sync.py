"""
MT5数据同步模块

负责交易记录的同步和处理
"""

import MetaTrader5 as mt5
import pandas as pd
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional

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


def sync_closed_trades_to_excel(account_id):
    """
    扫描近3天所有平仓单（包括自动止损/止盈），并将未记录过的平仓单写入excel。
    只用order_id（position_id）去重。
    建议每分钟调用一次。

    Args:
        account_id: 账号ID

    Returns:
        是否有新的平仓记录
    """
    try:
        start_time = datetime.now() - timedelta(days=3)
        end_time = datetime.now() + timedelta(days=1)  # 修正时区问题，取未来一天
        deals = mt5.history_deals_get(start_time, end_time)
        if deals is None:
            return False

        # 数据路径
        data_dir = get_data_path()
        file_path = os.path.join(data_dir, "trade_records.xlsx")
        sheet_name = str(account_id)

        # 读取已记录的order_id（position_id）
        recorded_order_ids = set()
        if os.path.exists(file_path):
            try:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
                if "order_id" in df.columns:
                    recorded_order_ids = set(df["order_id"].astype(str))
            except Exception:
                pass

        # 遍历所有平仓deal
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

            # 时间转换：MT5时间+tz_delta小时=本地时间
            open_time = (
                datetime.fromtimestamp(open_deal.time + tz_delta * 3600)
                if open_deal
                else ""
            )
            open_price = open_deal.price if open_deal else ""
            close_time = datetime.fromtimestamp(deal.time + tz_delta * 3600)

            # 使用交易日概念的日期（不是实际平仓的日期）
            trading_day = get_trading_day_from_datetime(close_time)

            close_price = deal.price
            profit = deal.profit
            direction = "buy" if deal.type == mt5.ORDER_TYPE_BUY else "sell"
            close_info = {
                "close_time": close_time.strftime("%Y-%m-%d %H:%M:%S"),
                "trading_day": trading_day,  # 添加交易日字段
                "order_id": order_id,
                "account": account_id,
                "symbol": deal.symbol,
                "volume": deal.volume,
                "direction": direction,
                "open_price": open_price,
                "close_price": close_price,
                "open_time": (
                    open_time.strftime("%Y-%m-%d %H:%M:%S") if open_time else ""
                ),
                "profit": profit,
                "comment": deal.comment,
            }
            new_records.append(close_info)

        if new_records:
            df_new = pd.DataFrame(new_records)
            if os.path.exists(file_path):
                with pd.ExcelWriter(
                    file_path, engine="openpyxl", mode="a", if_sheet_exists="overlay"
                ) as writer:
                    try:
                        df_old = pd.read_excel(file_path, sheet_name=sheet_name)
                        df_all = pd.concat([df_old, df_new], ignore_index=True)
                    except Exception:
                        df_all = df_new
                    df_all.to_excel(writer, sheet_name=sheet_name, index=False)
            else:
                with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
                    df_new.to_excel(writer, sheet_name=sheet_name, index=False)
            return True

        return False
    except Exception as e:
        # print(f"同步平仓记录出错: {str(e)}")
        return False
