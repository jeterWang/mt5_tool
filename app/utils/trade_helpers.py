import MetaTrader5 as mt5
import winsound
import logging


def check_daily_loss_limit_and_notify(gui_window):
    """
    检查每日亏损限制，若超限则界面提示。
    返回True表示通过，False表示禁止操作。
    """
    if not gui_window.check_daily_loss_limit():
        gui_window.status_bar.showMessage("已触发每日最大亏损，今日禁止下单！")
        return False
    return True


def check_trade_limit_and_notify(db, gui_window):
    """
    检查交易次数限制，若超限则界面提示。
    返回True表示通过，False表示禁止操作。
    """
    from app.gui.risk_control import check_trade_limit

    if not check_trade_limit(db, gui_window):
        return False
    return True


def check_mt5_connection_and_notify(trader, gui_window):
    """
    检查MT5连接和自动交易状态，若异常则界面提示。
    返回True表示通过，False表示禁止操作。
    """
    if not trader or not trader.is_connected():
        gui_window.status_bar.showMessage("MT5未连接，请检查连接状态！")
        return False
    if not mt5.terminal_info().trade_allowed:
        gui_window.status_bar.showMessage("请在MT5平台中启用自动交易！")
        return False
    return True


def get_valid_rates(symbol, timeframe, n, gui_window):
    """
    获取有效K线数据，若不足则界面提示。
    返回rates或None。
    """
    rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, n)
    if rates is None or len(rates) < n:
        gui_window.status_bar.showMessage(f"获取K线数据失败，需要至少{n}根K线！")
        return None
    return rates


def play_trade_beep(config_manager):
    """
    播放交易提示音，频率和时长从配置读取。
    """
    freq = config_manager.get("BEEP_SETTINGS", {}).get("FREQUENCY", 0)
    dur = config_manager.get("BEEP_SETTINGS", {}).get("DURATION", 0)
    if not (37 <= freq <= 32767):
        freq = 1000
    if not (10 <= dur <= 10000):
        dur = 200
    winsound.Beep(freq, dur)


def show_status_message(gui_window, msg):
    """
    统一界面状态栏消息显示。
    """
    gui_window.status_bar.showMessage(msg)


def trade_operation_feedback(func):
    """
    装饰器：统一异常处理、日志和界面反馈。
    """

    def wrapper(*args, **kwargs):
        gui_window = None
        for arg in args:
            if hasattr(arg, "status_bar"):
                gui_window = arg
                break
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if gui_window:
                gui_window.status_bar.showMessage(f"操作出错：{str(e)}")
            logging.error(f"操作错误详情：{str(e)}")
            return None

    return wrapper


def get_timeframe(timeframe: str) -> int:
    """
    将时间周期字符串转换为MT5的时间周期常量
    Args:
        timeframe: 时间周期字符串，如'M1', 'M5'等
    Returns:
        对应的MT5时间周期常量
    """
    timeframe_map = {
        "M1": mt5.TIMEFRAME_M1,
        "M5": mt5.TIMEFRAME_M5,
        "M15": mt5.TIMEFRAME_M15,
        "M30": mt5.TIMEFRAME_M30,
        "H1": mt5.TIMEFRAME_H1,
        "H4": mt5.TIMEFRAME_H4,
    }
    return timeframe_map.get(timeframe, mt5.TIMEFRAME_M1)


def calculate_breakeven_position_size(
    trader, symbol, order_type, sl_price, batch_entry_price, batch_count
):
    """
    计算批量加仓每单盈亏平衡手数
    Args:
        trader: 交易者对象，需有get_positions_by_symbol_and_type方法
        symbol: 交易品种
        order_type: 'buy' 或 'sell'
        sl_price: 新止损价
        batch_entry_price: 本次批量下单的开仓价（市价或挂单价）
        batch_count: 本次批量下单的单数
    Returns:
        建议每单手数，若无法计算则返回0
    """
    try:
        positions = trader.get_positions_by_symbol_and_type(symbol, order_type)
        if not positions:
            return 0
        total_volume = sum(p["volume"] for p in positions)
        if total_volume == 0:
            return 0
        avg_entry_price = (
            sum(p["price_open"] * p["volume"] for p in positions) / total_volume
        )
        numerator = (sl_price - avg_entry_price) * total_volume
        denominator = batch_count * (sl_price - batch_entry_price)
        if denominator == 0:
            return 0
        v2 = -numerator / denominator
        symbol_info = mt5.symbol_info(symbol)
        if not symbol_info:
            return 0
        min_volume = symbol_info.volume_min
        max_volume = symbol_info.volume_max
        volume_step = symbol_info.volume_step
        v2 = max(min_volume, min(max_volume, v2))
        v2 = round(v2 / volume_step) * volume_step
        return v2
    except Exception as e:
        return 0
