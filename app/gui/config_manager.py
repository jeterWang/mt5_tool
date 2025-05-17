"""
配置管理模块

负责保存和加载GUI配置
"""

from config.loader import (
    GUI_SETTINGS,
    BATCH_ORDER_DEFAULTS,
    SL_MODE,
    save_config,
)


def save_gui_config(gui_window):
    """
    保存GUI配置

    Args:
        gui_window: 主窗口对象
    """
    try:
        # 更新声音提醒设置
        countdown = gui_window.components["countdown"]
        GUI_SETTINGS["SOUND_ALERT"] = countdown.sound_checkbox.isChecked()
        GUI_SETTINGS["WINDOW_TOP"] = countdown.topmost_checkbox.isChecked()

        # 更新止损模式设置
        trading_settings = gui_window.components["trading_settings"]
        SL_MODE["DEFAULT_MODE"] = (
            "FIXED_POINTS"
            if trading_settings.sl_mode_combo.currentIndex() == 0
            else "CANDLE_KEY_LEVEL"
        )

        # 更新批量下单默认值
        batch_order = gui_window.components["batch_order"]
        for i in range(4):
            order_key = f"order{i+1}"
            BATCH_ORDER_DEFAULTS[order_key]["volume"] = batch_order.volume_inputs[
                i
            ].value()
            BATCH_ORDER_DEFAULTS[order_key]["sl_points"] = batch_order.sl_points_inputs[
                i
            ].value()
            BATCH_ORDER_DEFAULTS[order_key]["tp_points"] = batch_order.tp_points_inputs[
                i
            ].value()

        # 更新K线关键位止损默认K线回溯数量
        if SL_MODE["DEFAULT_MODE"] == "CANDLE_KEY_LEVEL":
            SL_MODE["CANDLE_LOOKBACK"] = batch_order.sl_points_inputs[0].value()

        # 保存配置
        return save_config()
    except Exception as e:
        print(f"保存配置出错: {e}")
        return False
