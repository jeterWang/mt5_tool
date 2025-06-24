"""
配置管理模块

负责保存和加载GUI配置
"""

from app.config.config_manager import config_manager


def save_gui_config(gui_window):
    """
    保存GUI配置

    Args:
        gui_window: 主窗口对象

    Returns:
        bool: 保存是否成功
    """
    try:
        # print("正在保存GUI配置...")

        # 更新声音提醒设置
        countdown = gui_window.components["countdown"]
        gui_settings = config_manager.get("GUI_SETTINGS")
        gui_settings["SOUND_ALERT"] = countdown.sound_checkbox.isChecked()
        gui_settings["WINDOW_TOP"] = countdown.topmost_checkbox.isChecked()
        config_manager.set("GUI_SETTINGS", gui_settings)

        # 自动修正声音提醒频率和时长，防止非法值
        if "BEEP_FREQUENCY" in gui_settings:
            freq = gui_settings["BEEP_FREQUENCY"]
            if not (37 <= freq <= 32767):
                gui_settings["BEEP_FREQUENCY"] = 1000
        if "BEEP_DURATION" in gui_settings:
            dur = gui_settings["BEEP_DURATION"]
            if not (10 <= dur <= 10000):
                gui_settings["BEEP_DURATION"] = 200

        # 保存一键保本偏移点数设置
        # （如有其它相关设置可在此补充）

        # 更新止损模式设置
        trading_settings = gui_window.components["trading_settings"]
        sl_mode = config_manager.get("SL_MODE")
        sl_mode["DEFAULT_MODE"] = (
            "FIXED_POINTS"
            if trading_settings.sl_mode_combo.currentIndex() == 0
            else "CANDLE_KEY_LEVEL"
        )
        # 防御：如果sl_mode缺少DEFAULT_MODE，自动补全
        if "DEFAULT_MODE" not in sl_mode:
            sl_mode["DEFAULT_MODE"] = "FIXED_POINTS"
        config_manager.set("SL_MODE", sl_mode)

        # 打印保存前的批量下单设置
        # print(f"保存前BATCH_ORDER_DEFAULTS: {BATCH_ORDER_DEFAULTS}")

        # 更新批量下单默认值
        batch_order = gui_window.components["batch_order"]
        batch_defaults = config_manager.get("BATCH_ORDER_DEFAULTS")
        for i, order in enumerate(batch_order.orders):
            order_key = f"order{i+1}"
            batch_defaults[order_key] = {
                "volume": order["volume"],
                "sl_points": order["sl_points"],
                "tp_points": order["tp_points"],
                "sl_candle": order["sl_candle"],
                "fixed_loss": order["fixed_loss"],
                "checked": order["checked"],
            }

        # 更新K线关键位止损默认K线回溯数量
        if (
            sl_mode.get("DEFAULT_MODE", "FIXED_POINTS") == "CANDLE_KEY_LEVEL"
            and batch_order.orders
        ):
            sl_mode["CANDLE_LOOKBACK"] = batch_order.orders[0]["sl_candle"]
            config_manager.set("SL_MODE", sl_mode)
            # print(f"设置K线回溯数量: {SL_MODE['CANDLE_LOOKBACK']}")

        # 打印保存后的批量下单设置
        # print(f"保存后BATCH_ORDER_DEFAULTS: {BATCH_ORDER_DEFAULTS}")

        # 保存配置
        result = config_manager.save()
        # print(f"配置保存结果: {result}")

        # 更新交易次数显示，确保UI显示是最新的
        if gui_window.db:
            account_info = gui_window.components["account_info"]
            account_info.update_trade_count_display(gui_window.db)

        return result
    except Exception as e:
        # print(f"保存配置出错: {e}")
        return False
