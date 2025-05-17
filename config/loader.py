"""
配置加载模块

加载和保存MT5系统配置
"""

import os
import json
import sys

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
    "order1": {"volume": 0.10, "sl_points": 3000, "tp_points": 1000, "sl_candle": 3},
    "order2": {"volume": 0.10, "sl_points": 3000, "tp_points": 1500, "sl_candle": 3},
    "order3": {"volume": 0.10, "sl_points": 3000, "tp_points": 2000, "sl_candle": 3},
    "order4": {"volume": 0.10, "sl_points": 3000, "tp_points": 2500, "sl_candle": 3},
}


def get_config_path():
    """
    获取配置文件路径

    Returns:
        配置文件的完整路径
    """
    try:
        # 获取当前执行文件的目录
        if getattr(sys, "frozen", False):
            # 如果是打包后的可执行文件
            base_dir = os.path.dirname(sys.executable)
            config_dir = os.path.join(base_dir, "config")

            # 确保目录存在
            if not os.path.exists(config_dir):
                os.makedirs(config_dir, exist_ok=True)
                print(f"创建打包环境的配置目录: {config_dir}")

            # 打包后的配置文件放在可执行文件同级目录的config文件夹中
            config_path = os.path.join(config_dir, "config.json")
            print(f"打包环境配置路径: {config_path}")

            # 确保配置文件存在
            if not os.path.exists(config_path):
                # 如果配置文件不存在，则需要创建一个默认配置
                save_config()
                print(f"在打包环境中创建了默认配置文件: {config_path}")

            return config_path
        else:
            # 如果是开发环境
            current_dir = os.path.dirname(os.path.abspath(__file__))
            config_path = os.path.join(current_dir, "config.json")
            print(f"开发环境配置路径: {config_path}")
            return config_path
    except Exception as e:
        print(f"获取配置文件路径出错: {str(e)}")
        # 返回一个相对路径作为备选
        return "config/config.json"


def load_config():
    """
    加载配置

    Returns:
        配置字典
    """
    # 声明使用全局变量
    global SYMBOLS, DEFAULT_TIMEFRAME, Delta_TIMEZONE, TRADING_DAY_RESET_HOUR
    global DAILY_LOSS_LIMIT, DAILY_TRADE_LIMIT, GUI_SETTINGS, SL_MODE, BATCH_ORDER_DEFAULTS
    global BREAKOUT_SETTINGS

    try:
        config_path = get_config_path()
        if os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
                print(
                    f"load_config: 读取到的配置文件SYMBOLS = {config.get('SYMBOLS', '未找到')}"
                )  # 调试信息
                print(
                    f"load_config: 读取到的配置文件DAILY_TRADE_LIMIT = {config.get('DAILY_TRADE_LIMIT', '未找到')}"
                )  # 调试信息
                print(
                    f"load_config: 读取到的配置文件BATCH_ORDER_DEFAULTS = {config.get('BATCH_ORDER_DEFAULTS', '未找到')}"
                )  # 调试信息

                # 更新全局变量
                if "SYMBOLS" in config:
                    # 清空当前列表并扩展，而不是直接赋值
                    SYMBOLS.clear()
                    SYMBOLS.extend(config["SYMBOLS"])
                    print(f"load_config: 加载后SYMBOLS = {SYMBOLS}")  # 调试信息
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
                    print(
                        f"load_config: 加载后DAILY_TRADE_LIMIT = {DAILY_TRADE_LIMIT}"
                    )  # 调试信息
                if "GUI_SETTINGS" in config:
                    GUI_SETTINGS.update(config["GUI_SETTINGS"])
                if "SL_MODE" in config:
                    SL_MODE.update(config["SL_MODE"])
                if "BREAKOUT_SETTINGS" in config:
                    BREAKOUT_SETTINGS.update(config["BREAKOUT_SETTINGS"])
                if "BATCH_ORDER_DEFAULTS" in config:
                    # 使用深拷贝避免引用问题
                    import copy

                    batch_defaults_copy = copy.deepcopy(config["BATCH_ORDER_DEFAULTS"])
                    BATCH_ORDER_DEFAULTS.clear()
                    BATCH_ORDER_DEFAULTS.update(batch_defaults_copy)
                    print(
                        f"load_config: 加载后BATCH_ORDER_DEFAULTS = {BATCH_ORDER_DEFAULTS}"
                    )  # 调试信息

                # 验证批量下单设置中的关键字段
                for order_key, order_data in BATCH_ORDER_DEFAULTS.items():
                    # 确保每个订单设置都包含所有必要字段
                    if "volume" not in order_data:
                        print(f"load_config: {order_key}缺少volume字段，使用默认值0.1")
                        order_data["volume"] = 0.1
                    if "sl_points" not in order_data:
                        print(
                            f"load_config: {order_key}缺少sl_points字段，使用默认值3000"
                        )
                        order_data["sl_points"] = 3000
                    if "tp_points" not in order_data:
                        print(
                            f"load_config: {order_key}缺少tp_points字段，使用默认值1000"
                        )
                        order_data["tp_points"] = 1000
                    if "sl_candle" not in order_data:
                        print(f"load_config: {order_key}缺少sl_candle字段，使用默认值3")
                        order_data["sl_candle"] = 3

                return config
        else:
            print(f"配置文件不存在，将使用默认配置")
            # 如果配置文件不存在，保存当前默认配置
            save_config()
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
    # 声明所有全局变量
    global SYMBOLS, DEFAULT_TIMEFRAME, Delta_TIMEZONE, TRADING_DAY_RESET_HOUR
    global DAILY_LOSS_LIMIT, DAILY_TRADE_LIMIT, GUI_SETTINGS, SL_MODE, BREAKOUT_SETTINGS
    global BATCH_ORDER_DEFAULTS

    try:
        print(f"save_config: 保存前SYMBOLS = {SYMBOLS}")  # 调试信息
        print(f"save_config: 保存前DAILY_TRADE_LIMIT = {DAILY_TRADE_LIMIT}")  # 调试信息
        print(
            f"save_config: 保存前BATCH_ORDER_DEFAULTS = {BATCH_ORDER_DEFAULTS}"
        )  # 调试信息

        # 创建配置字典前检查批量下单设置中的关键字段
        for order_key, order_data in BATCH_ORDER_DEFAULTS.items():
            # 确保每个订单设置都包含所有必要字段
            if "volume" not in order_data:
                print(f"save_config: {order_key}缺少volume字段，使用默认值0.1")
                order_data["volume"] = 0.1
            if "sl_points" not in order_data:
                print(f"save_config: {order_key}缺少sl_points字段，使用默认值3000")
                order_data["sl_points"] = 3000
            if "tp_points" not in order_data:
                print(f"save_config: {order_key}缺少tp_points字段，使用默认值1000")
                order_data["tp_points"] = 1000
            if "sl_candle" not in order_data:
                print(f"save_config: {order_key}缺少sl_candle字段，使用默认值3")
                order_data["sl_candle"] = 3

        # 使用深拷贝避免引用问题
        import copy

        batch_defaults_copy = copy.deepcopy(BATCH_ORDER_DEFAULTS)

        config = {
            "SYMBOLS": SYMBOLS.copy(),  # 使用copy确保不会有引用问题
            "DEFAULT_TIMEFRAME": DEFAULT_TIMEFRAME,
            "Delta_TIMEZONE": Delta_TIMEZONE,
            "TRADING_DAY_RESET_HOUR": TRADING_DAY_RESET_HOUR,
            "DAILY_LOSS_LIMIT": DAILY_LOSS_LIMIT,
            "DAILY_TRADE_LIMIT": DAILY_TRADE_LIMIT,
            "GUI_SETTINGS": GUI_SETTINGS.copy(),  # 使用深拷贝确保不会有引用问题
            "SL_MODE": SL_MODE.copy(),  # 使用深拷贝确保不会有引用问题
            "BREAKOUT_SETTINGS": BREAKOUT_SETTINGS.copy(),  # 使用深拷贝确保不会有引用问题
            "BATCH_ORDER_DEFAULTS": batch_defaults_copy,
        }

        config_path = get_config_path()
        print(f"save_config: 尝试保存到 {config_path}")  # 调试信息
        print(f"save_config: 配置中的DAILY_TRADE_LIMIT = {config['DAILY_TRADE_LIMIT']}")
        print(
            f"save_config: 配置中的BATCH_ORDER_DEFAULTS = {config['BATCH_ORDER_DEFAULTS']}"
        )

        # 确保config目录存在
        config_dir = os.path.dirname(config_path)
        if not os.path.exists(config_dir):
            print(f"save_config: 创建目录 {config_dir}")
            os.makedirs(config_dir, exist_ok=True)

        # 保存到临时文件，然后重命名，以减少文件损坏风险
        temp_path = f"{config_path}.temp"
        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4, ensure_ascii=False)

        # 如果临时文件写入成功，则重命名为正式文件
        if os.path.exists(temp_path):
            # 如果目标文件已存在，先备份
            if os.path.exists(config_path):
                backup_path = f"{config_path}.bak"
                try:
                    # 删除旧的备份文件
                    if os.path.exists(backup_path):
                        os.remove(backup_path)
                    # 将当前配置文件重命名为备份
                    os.rename(config_path, backup_path)
                    print(f"save_config: 创建备份文件 {backup_path}")
                except Exception as e:
                    print(f"save_config: 创建备份文件失败: {str(e)}")

            # 将临时文件重命名为正式文件
            try:
                os.rename(temp_path, config_path)
                print(f"save_config: 临时文件重命名为 {config_path}")
            except Exception as e:
                print(f"save_config: 重命名临时文件失败: {str(e)}")
                # 如果重命名失败，直接复制内容
                try:
                    with open(temp_path, "r", encoding="utf-8") as src:
                        with open(config_path, "w", encoding="utf-8") as dst:
                            dst.write(src.read())
                    print(f"save_config: 使用复制代替重命名")
                    os.remove(temp_path)
                except Exception as copy_e:
                    print(f"save_config: 复制文件也失败: {str(copy_e)}")
                    return False

        # 验证保存是否成功
        if os.path.exists(config_path):
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    saved_config = json.load(f)
                    print(
                        f"save_config: 文件中的SYMBOLS = {saved_config.get('SYMBOLS', '未找到')}"
                    )  # 调试信息
                    print(
                        f"save_config: 文件中的DAILY_TRADE_LIMIT = {saved_config.get('DAILY_TRADE_LIMIT', '未找到')}"
                    )  # 调试信息
                    print(
                        f"save_config: 文件中的BATCH_ORDER_DEFAULTS = {saved_config.get('BATCH_ORDER_DEFAULTS', '未找到')}"
                    )  # 调试信息

                    # 验证交易限制是否正确保存
                    if saved_config.get("DAILY_TRADE_LIMIT") != DAILY_TRADE_LIMIT:
                        print(
                            f"save_config: 警告 - 文件中的DAILY_TRADE_LIMIT({saved_config.get('DAILY_TRADE_LIMIT')})与内存中的值({DAILY_TRADE_LIMIT})不一致!"
                        )
                        # 更新全局变量，确保内存与文件一致
                        DAILY_TRADE_LIMIT = saved_config.get("DAILY_TRADE_LIMIT")
                        print(
                            f"save_config: 已更新内存中的DAILY_TRADE_LIMIT为{DAILY_TRADE_LIMIT}"
                        )

                    # 验证批量订单设置是否正确保存
                    saved_batch = saved_config.get("BATCH_ORDER_DEFAULTS", {})
                    for order_key, order_data in BATCH_ORDER_DEFAULTS.items():
                        if order_key in saved_batch:
                            saved_volume = saved_batch[order_key].get("volume")
                            if saved_volume != order_data.get("volume"):
                                print(
                                    f"save_config: 警告 - 文件中的{order_key}手数({saved_volume})与内存中的值({order_data.get('volume')})不一致!"
                                )

                    # 应用文件中的配置到内存中，确保内存与文件一致
                    load_saved_config_to_memory(saved_config)

                    return True
            except Exception as e:
                print(f"save_config: 验证保存失败: {str(e)}")
                return False
        else:
            print(f"save_config: 配置文件未创建成功")
            return False
    except Exception as e:
        print(f"保存配置出错: {str(e)}")
        # 尝试保存到备选位置
        try:
            backup_path = os.path.join(
                (
                    os.path.dirname(sys.executable)
                    if getattr(sys, "frozen", False)
                    else "."
                ),
                "config.json",
            )
            print(f"save_config: 尝试保存到备选位置 {backup_path}")
            with open(backup_path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            print(f"save_config: 已保存到备选位置 {backup_path}")
            return True
        except Exception as backup_e:
            print(f"save_config: 备选保存也失败: {str(backup_e)}")
            return False


def load_saved_config_to_memory(saved_config):
    """
    将保存的配置直接加载到内存中，确保内存与文件一致

    Args:
        saved_config: 从文件中读取的配置字典
    """
    global SYMBOLS, DEFAULT_TIMEFRAME, Delta_TIMEZONE, TRADING_DAY_RESET_HOUR
    global DAILY_LOSS_LIMIT, DAILY_TRADE_LIMIT, GUI_SETTINGS, SL_MODE, BATCH_ORDER_DEFAULTS
    global BREAKOUT_SETTINGS

    if "SYMBOLS" in saved_config:
        SYMBOLS.clear()
        SYMBOLS.extend(saved_config["SYMBOLS"])

    if "DEFAULT_TIMEFRAME" in saved_config:
        DEFAULT_TIMEFRAME = saved_config["DEFAULT_TIMEFRAME"]

    if "Delta_TIMEZONE" in saved_config:
        Delta_TIMEZONE = saved_config["Delta_TIMEZONE"]

    if "TRADING_DAY_RESET_HOUR" in saved_config:
        TRADING_DAY_RESET_HOUR = saved_config["TRADING_DAY_RESET_HOUR"]

    if "DAILY_LOSS_LIMIT" in saved_config:
        DAILY_LOSS_LIMIT = saved_config["DAILY_LOSS_LIMIT"]

    if "DAILY_TRADE_LIMIT" in saved_config:
        DAILY_TRADE_LIMIT = saved_config["DAILY_TRADE_LIMIT"]

    if "GUI_SETTINGS" in saved_config:
        GUI_SETTINGS.update(saved_config["GUI_SETTINGS"])

    if "SL_MODE" in saved_config:
        SL_MODE.update(saved_config["SL_MODE"])

    if "BREAKOUT_SETTINGS" in saved_config:
        BREAKOUT_SETTINGS.update(saved_config["BREAKOUT_SETTINGS"])

    if "BATCH_ORDER_DEFAULTS" in saved_config:
        # 使用深拷贝避免引用问题
        import copy

        batch_defaults_copy = copy.deepcopy(saved_config["BATCH_ORDER_DEFAULTS"])
        BATCH_ORDER_DEFAULTS.clear()
        BATCH_ORDER_DEFAULTS.update(batch_defaults_copy)

    print("load_saved_config_to_memory: 已将文件中的配置应用到内存")


# 加载配置
print("config/loader.py模块被导入，执行load_config()")
load_config()
