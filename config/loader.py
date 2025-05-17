"""
配置加载模块

加载和保存MT5系统配置
"""

import os
import json

# 基础配置
SYMBOLS = ["BTCUSD", "ETHUSD", "EURUSD", "GBPUSD", "XAUUSD", "XAGUSD"]
DEFAULT_TIMEFRAME = "M1"
Delta_TIMEZONE = 7  # MT5服务器时区与本地时区的差值(小时)
TRADING_DAY_RESET_HOUR = 6  # 每天6点作为新交易日的开始

# 风控设置
DAILY_LOSS_LIMIT = 50  # 日亏损限额，单位为账户货币
DAILY_TRADE_LIMIT = 20  # 日交易次数限制

# GUI设置
GUI_SETTINGS = {
    "WINDOW_TOP": True,  # 窗口置顶
    "SOUND_ALERT": True,  # 声音提醒
    "ALERT_SECONDS": 30,  # 提前30秒提醒
    "BEEP_FREQUENCY": 750,  # 提示音频率
    "BEEP_DURATION": 800,  # 提示音持续时间
}

# 止损模式
SL_MODE = {
    "DEFAULT_MODE": "FIXED_POINTS",  # 默认固定点数止损
    "CANDLE_LOOKBACK": 3,  # 使用K线关键位模式时，向前看几根K线
}

# 突破设置
BREAKOUT_SETTINGS = {
    "HIGH_OFFSET_POINTS": 10,  # 高点突破偏移点数
    "LOW_OFFSET_POINTS": 10,  # 低点突破偏移点数
    "SL_OFFSET_POINTS": 100,  # 止损偏移点数
}

# 批量订单默认参数
BATCH_ORDER_DEFAULTS = {
    "order1": {"volume": 0.10, "sl_points": 500, "tp_points": 1000},
    "order2": {"volume": 0.10, "sl_points": 500, "tp_points": 1500},
    "order3": {"volume": 0.10, "sl_points": 500, "tp_points": 2000},
    "order4": {"volume": 0.10, "sl_points": 500, "tp_points": 2500},
}


def get_config_path():
    """
    获取配置文件路径

    Returns:
        配置文件的完整路径
    """
    # 获取当前文件所在的目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(current_dir, "config.json")


def load_config():
    """
    加载配置

    Returns:
        配置字典
    """
    try:
        config_path = get_config_path()
        if os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)

                # 更新全局变量
                global SYMBOLS, DEFAULT_TIMEFRAME, Delta_TIMEZONE, TRADING_DAY_RESET_HOUR
                global DAILY_LOSS_LIMIT, DAILY_TRADE_LIMIT, GUI_SETTINGS, SL_MODE, BATCH_ORDER_DEFAULTS
                global BREAKOUT_SETTINGS

                if "SYMBOLS" in config:
                    SYMBOLS = config["SYMBOLS"]
                if "DEFAULT_TIMEFRAME" in config:
                    DEFAULT_TIMEFRAME = config["DEFAULT_TIMEFRAME"]
                if "Delta_TIMEZONE" in config:
                    Delta_TIMEZONE = config["Delta_TIMEZONE"]
                if "TRADING_DAY_RESET_HOUR" in config:
                    TRADING_DAY_RESET_HOUR = config["TRADING_DAY_RESET_HOUR"]
                if "DAILY_LOSS_LIMIT" in config:
                    DAILY_LOSS_LIMIT = config["DAILY_LOSS_LIMIT"]
                if "DAILY_TRADE_LIMIT" in config:
                    DAILY_TRADE_LIMIT = config["DAILY_TRADE_LIMIT"]
                if "GUI_SETTINGS" in config:
                    GUI_SETTINGS.update(config["GUI_SETTINGS"])
                if "SL_MODE" in config:
                    SL_MODE.update(config["SL_MODE"])
                if "BREAKOUT_SETTINGS" in config:
                    BREAKOUT_SETTINGS.update(config["BREAKOUT_SETTINGS"])
                if "BATCH_ORDER_DEFAULTS" in config:
                    BATCH_ORDER_DEFAULTS.update(config["BATCH_ORDER_DEFAULTS"])

                return config
        return {}
    except Exception as e:
        print(f"加载配置出错：{str(e)}")
        return {}


def save_config():
    """
    保存配置

    Returns:
        是否保存成功
    """
    try:
        config = {
            "SYMBOLS": SYMBOLS,
            "DEFAULT_TIMEFRAME": DEFAULT_TIMEFRAME,
            "Delta_TIMEZONE": Delta_TIMEZONE,
            "TRADING_DAY_RESET_HOUR": TRADING_DAY_RESET_HOUR,
            "DAILY_LOSS_LIMIT": DAILY_LOSS_LIMIT,
            "DAILY_TRADE_LIMIT": DAILY_TRADE_LIMIT,
            "GUI_SETTINGS": GUI_SETTINGS,
            "SL_MODE": SL_MODE,
            "BREAKOUT_SETTINGS": BREAKOUT_SETTINGS,
            "BATCH_ORDER_DEFAULTS": BATCH_ORDER_DEFAULTS,
        }

        config_path = get_config_path()
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"保存配置出错：{str(e)}")
        return False


# 加载配置
load_config()
