import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 交易品种配置
SYMBOLS = ["NAS100", "US100.cash"]

# 默认K线周期
DEFAULT_TIMEFRAME = "M1"  # 可选值: M1, M5, M15, M30, H1, H4

# 每日交易限制
DAILY_TRADE_LIMIT = 5  # 每天最大交易次数

# 每日最大亏损限制（单位：账户货币）
DAILY_LOSS_LIMIT = 100

# 界面设置
GUI_SETTINGS = {
    "SOUND_ALERT": False,     # 收盘提醒声音默认开启
    "WINDOW_TOP": True,     # 窗口置顶默认关闭
    "ALERT_SECONDS": 5,      # 收盘前5秒开始提醒
    "BEEP_FREQUENCY": 1000,  # 提示音频率
    "BEEP_DURATION": 200     # 提示音持续时间(毫秒)
}

# 批量下单默认参数
BATCH_ORDER_DEFAULTS = {
    "order1": {
        "volume": 0.20,
        "sl_points": 3000,
        "tp_points": 50000
    },
    "order2": {
        "volume": 0.20,
        "sl_points": 3000,
        "tp_points": 50000
    },
    "order3": {
        "volume": 0.20,
        "sl_points": 3000,
        "tp_points": 50000
    },
    "order4": {
        "volume": 0.20,
        "sl_points": 3000,
        "tp_points": 50000
    }
}

# 每个交易品种的默认参数
DEFAULT_PARAMS = {
    "NAS100": {
        "volume": 0.10,
        "min_volume": 0.01,
        "max_volume": 100.0,
        "volume_step": 0.01,
        "min_sl_points": 0,
        "max_sl_points": 100000,
        "min_tp_points": 0,
        "max_tp_points": 100000
    },
    "US100.cash": {
        "volume": 0.10,
        "min_volume": 0.01,
        "max_volume": 100.0,
        "volume_step": 0.01,
        "min_sl_points": 0,
        "max_sl_points": 100000,
        "min_tp_points": 0,
        "max_tp_points": 100000
    }   
}


# 时间差
Delta_TIMEZONE = -3
