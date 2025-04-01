import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# MT5账号配置
username = int(os.getenv('MT5_USERNAME'))
password = os.getenv('MT5_PASSWORD')
server = os.getenv('MT5_SERVER')

# 交易品种配置
SYMBOLS = ["XAUUSDm"]

# 默认K线周期
DEFAULT_TIMEFRAME = "M5"  # 可选值: M1, M5, M15, M30, H1, H4

# 批量下单默认参数
BATCH_ORDER_DEFAULTS = {
    "order1": {
        "volume": 0.01,
        "sl_points": 1500,
        "tp_points": 1000
    },
    "order2": {
        "volume": 0.01,
        "sl_points": 1500,
        "tp_points": 1000
    },
    "order3": {
        "volume": 0.01,
        "sl_points": 1500,
        "tp_points": 20000  # 第三单默认20000
    }
}

# 每个交易品种的默认参数
DEFAULT_PARAMS = {
    "XAUUSDm": {
        "volume": 0.1,
        "min_volume": 0.01,
        "max_volume": 100.0,
        "volume_step": 0.01,
        "min_sl_points": 0,
        "max_sl_points": 100000,
        "min_tp_points": 0,
        "max_tp_points": 100000
    }
}
