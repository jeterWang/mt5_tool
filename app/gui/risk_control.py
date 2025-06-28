"""
风控模块

提供交易系统的风控功能，包括交易次数限制和亏损控制
"""

import os
import pandas as pd
from datetime import datetime, timedelta
import winsound
import json
import sqlite3

from utils.paths import get_data_path
from config.loader import (
    DAILY_LOSS_LIMIT,
    DAILY_TRADE_LIMIT,
    TRADING_DAY_RESET_HOUR,
    GUI_SETTINGS,
    get_config_path,
)


def check_trade_limit(db, gui_window):
    """
    检查是否超过每日交易限制

    Args:
        db: TradeDatabase实例
        gui_window: 主窗口实例

    Returns:
        bool: 是否允许继续交易
    """
    try:
        # 重新从配置文件加载最新的DAILY_TRADE_LIMIT
        from config.loader import DAILY_TRADE_LIMIT, load_config, get_config_path

        # 先执行一次load_config确保内存中的值是最新的
        load_config()

        # 直接从配置文件读取，确保获取最新值
        config_path = get_config_path()
        # print(f"检查交易次数限制，配置文件路径: {config_path}")

        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
                file_limit = config.get("DAILY_TRADE_LIMIT", DAILY_TRADE_LIMIT)
                # print(f"从配置文件读取DAILY_TRADE_LIMIT = {file_limit}")
        except Exception as e:
            # print(f"读取配置文件出错: {str(e)}, 使用内存中的值: {DAILY_TRADE_LIMIT}")
            file_limit = DAILY_TRADE_LIMIT

        # 比较内存中的值和文件中的值，如果不一致则使用文件中的值
        if DAILY_TRADE_LIMIT != file_limit:
            # print(
            # f"警告：内存中的DAILY_TRADE_LIMIT({DAILY_TRADE_LIMIT})与文件中的值({file_limit})不一致"
            # )
            # 使用文件中的值
            limit_to_use = file_limit
        else:
            limit_to_use = DAILY_TRADE_LIMIT

        # print(f"检查交易次数限制，当前设置为: {limit_to_use}")

        # 获取今日实际交易次数
        count = db.get_today_count()
        # print(f"今日已交易次数: {count}, 最大允许次数: {limit_to_use}")

        if count >= limit_to_use:
            message = f"已达到每日交易次数限制({count}/{limit_to_use})！"
            gui_window.status_bar.showMessage(message)
            # print(message)
            # 播放警告声音
            winsound.Beep(1000, 1000)  # 频率1000，持续1秒
            return False

        return True
    except Exception as e:
        # print(f"检查交易次数限制出错: {str(e)}")
        return True  # 出错时允许继续交易，避免错误阻止用户交易


def check_daily_loss_limit(trader, db, gui_window):
    """
    检查是否超过日内最大亏损，超过则自动平仓并禁止交易

    Args:
        trader: MT5Trader实例
        db: TradeDatabase实例
        gui_window: 主窗口实例

    Returns:
        bool: 是否允许继续交易
    """
    try:
        # 1. 统计今日已实现亏损（改为trade_history表SQL查询）
        today = get_trading_day()
        realized_loss = 0
        account_id = trader._get_account_id() if trader else "unknown"
        db_path = get_data_path("trade_history.db")
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT SUM(profit) FROM trade_history WHERE trading_day = ? AND account = ?
                """,
                (today, str(account_id)),
            )
            result = cursor.fetchone()
            if result and result[0] is not None:
                realized_loss = result[0]
            conn.close()
        except Exception as e:
            pass

        # 2. 统计当前未实现浮动盈亏
        unrealized = 0
        if trader and trader.is_connected():
            positions = trader.get_all_positions()
            if positions:
                unrealized = sum([p["profit"] for p in positions])

        # 3. 合计
        total = realized_loss + unrealized
        if total <= -DAILY_LOSS_LIMIT:
            # 超过最大亏损，自动平仓并禁止交易
            gui_window.components["trading_buttons"].close_all_positions()
            gui_window.disable_trading_for_today()
            # 记录风控事件
            detail = f"日内亏损已达{total:.2f}，已自动平仓并禁止交易"
            db.record_risk_event("DAILY_LOSS_LIMIT", detail)
            gui_window.status_bar.showMessage(detail)
            return False
        return True
    except Exception as e:
        return True  # 出错时允许继续交易，避免错误阻止用户交易


def get_trading_day():
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
