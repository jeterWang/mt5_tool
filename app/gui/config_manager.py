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

    Returns:
        bool: 保存是否成功
    """
    try:
        print("正在保存GUI配置...")

        # 更新声音提醒设置
        countdown = gui_window.components["countdown"]
        GUI_SETTINGS["SOUND_ALERT"] = countdown.sound_checkbox.isChecked()
        GUI_SETTINGS["WINDOW_TOP"] = countdown.topmost_checkbox.isChecked()

        # 保存一键保本偏移点数设置
        if "BREAKEVEN_OFFSET_POINTS" in GUI_SETTINGS:
            print(
                f"当前一键保本偏移点数设置为: {GUI_SETTINGS['BREAKEVEN_OFFSET_POINTS']}"
            )

        # 更新止损模式设置
        trading_settings = gui_window.components["trading_settings"]
        SL_MODE["DEFAULT_MODE"] = (
            "FIXED_POINTS"
            if trading_settings.sl_mode_combo.currentIndex() == 0
            else "CANDLE_KEY_LEVEL"
        )

        # 打印保存前的批量下单设置
        print(f"保存前BATCH_ORDER_DEFAULTS: {BATCH_ORDER_DEFAULTS}")

        # 更新批量下单默认值
        batch_order = gui_window.components["batch_order"]
        for i in range(4):
            order_key = f"order{i+1}"
            # 保存当前批量订单值
            current_volume = batch_order.volume_inputs[i].value()
            current_sl_points = batch_order.sl_points_inputs[i].value()
            current_tp_points = batch_order.tp_points_inputs[i].value()
            current_sl_candle = batch_order.sl_candle_inputs[i].value()

            # 调试信息
            print(
                f"保存批量订单{i+1}设置: 手数={current_volume}, 止损点数={current_sl_points}, 止盈点数={current_tp_points}, K线回溯={current_sl_candle}"
            )

            # 创建新的订单设置字典，确保包含所有必要字段
            BATCH_ORDER_DEFAULTS[order_key] = {
                "volume": current_volume,
                "sl_points": current_sl_points,
                "tp_points": current_tp_points,
                "sl_candle": current_sl_candle,
            }

        # 更新K线关键位止损默认K线回溯数量
        if SL_MODE["DEFAULT_MODE"] == "CANDLE_KEY_LEVEL":
            SL_MODE["CANDLE_LOOKBACK"] = batch_order.sl_candle_inputs[0].value()
            print(f"设置K线回溯数量: {SL_MODE['CANDLE_LOOKBACK']}")

        # 打印保存后的批量下单设置
        print(f"保存后BATCH_ORDER_DEFAULTS: {BATCH_ORDER_DEFAULTS}")

        # 保存配置
        result = save_config()
        print(f"配置保存结果: {result}")

        # 更新交易次数显示，确保UI显示是最新的
        if gui_window.db:
            account_info = gui_window.components["account_info"]
            account_info.update_trade_count_display(gui_window.db)

        return result
    except Exception as e:
        print(f"保存配置出错: {e}")
        return False
