from app.commands.base_command import BaseCommand
from app.utils.trade_helpers import (
    check_daily_loss_limit_and_notify,
    check_trade_limit_and_notify,
    check_mt5_connection_and_notify,
    get_valid_rates,
    play_trade_beep,
    show_status_message,
    get_timeframe,
    calculate_breakeven_position_size,
)
import MetaTrader5 as mt5
import logging
from app.config.config_manager import config_manager


class PlaceBatchOrderCommand(BaseCommand):
    def __init__(self, trader, gui_window, order_type):
        self.trader = trader
        self.gui_window = gui_window
        self.order_type = order_type

    def execute(self):
        if not check_daily_loss_limit_and_notify(self.gui_window):
            return
        try:
            batch_order = self.gui_window.components["batch_order"]
            for idx, row in enumerate(batch_order.order_rows):
                pass
            if not check_trade_limit_and_notify(self.gui_window.db, self.gui_window):
                return
            if not check_mt5_connection_and_notify(self.trader, self.gui_window):
                return
            trading_settings = self.gui_window.components["trading_settings"]
            symbol = trading_settings.symbol_input.currentText()
            show_status_message(self.gui_window, f"正在执行批量{self.order_type}单...")
            sl_mode = (
                "FIXED_POINTS"
                if trading_settings.sl_mode_combo.currentIndex() == 0
                else "CANDLE_KEY_LEVEL"
            )
            positions = self.trader.get_positions_by_symbol_and_type(
                symbol, self.order_type
            )
            has_positions = bool(positions)
            batch_order.sync_checked_from_ui()
            checked_orders = [order for order in batch_order.orders if order["checked"]]
            batch_count = len(checked_orders)
            if batch_count == 0:
                show_status_message(self.gui_window, "未勾选任何批量下单订单！")
                return
            if sl_mode == "FIXED_POINTS":
                tick = mt5.symbol_info_tick(symbol)
                if not tick:
                    show_status_message(self.gui_window, f"无法获取{symbol}当前价格！")
                    return
                batch_entry_price = tick.ask if self.order_type == "buy" else tick.bid
                sl_points = checked_orders[0]["sl_points"]
                point = mt5.symbol_info(symbol).point
                spread = tick.ask - tick.bid
                if self.order_type == "buy":
                    sl_price = batch_entry_price - sl_points * point
                else:
                    sl_price = batch_entry_price + sl_points * point + spread
            else:
                countdown = self.gui_window.components.get("countdown")
                if not countdown:
                    show_status_message(self.gui_window, "未找到倒计时组件！")
                    return
                timeframe = countdown.timeframe_combo.currentText()
                lookback = checked_orders[0]["sl_candle"]
                timeframe_mt5 = batch_order.get_timeframe(timeframe)
                rates = get_valid_rates(
                    symbol, timeframe_mt5, lookback + 2, self.gui_window
                )
                if rates is None:
                    return
                lowest_point = min([rate["low"] for rate in rates[2:]])
                highest_point = max([rate["high"] for rate in rates[2:]])
                sl_offset = (
                    config_manager.get("BREAKOUT_SETTINGS", {}).get(
                        "SL_OFFSET_POINTS", 0
                    )
                    * mt5.symbol_info(symbol).point
                )
                tick = mt5.symbol_info_tick(symbol)
                spread = tick.ask - tick.bid if tick else 0
                if self.order_type == "buy":
                    sl_price = lowest_point - sl_offset
                    batch_entry_price = tick.ask if tick else 0
                else:
                    sl_price = highest_point + sl_offset + spread
                    batch_entry_price = tick.bid if tick else 0
            if has_positions:
                breakeven_volume = calculate_breakeven_position_size(
                    self.trader,
                    symbol,
                    self.order_type,
                    sl_price,
                    batch_entry_price,
                    batch_count,
                )
                if breakeven_volume <= 0:
                    show_status_message(
                        self.gui_window, "盈亏平衡手数计算失败，无法批量下单！"
                    )
                    return
                for order in batch_order.orders:
                    if order["checked"]:
                        order["volume"] = breakeven_volume
            orders = []
            for i, order in enumerate(batch_order.orders):
                if not order["checked"]:
                    continue
                position_sizing_mode = config_manager.get("POSITION_SIZING", {}).get(
                    "DEFAULT_MODE", "FIXED_LOSS"
                )
                volume = order["volume"]
                if not has_positions and position_sizing_mode == "FIXED_LOSS":
                    if order["fixed_loss"] <= 0:
                        continue
                    tick = mt5.symbol_info_tick(symbol)
                    if not tick:
                        continue
                    entry_price = tick.ask if self.order_type == "buy" else tick.bid
                    calculated_volume = batch_order.calculate_position_size_for_order(
                        i, self.order_type, entry_price, symbol
                    )
                    if calculated_volume <= 0:
                        logging.error(f"订单{i+1}：仓位计算失败，跳过")
                        logging.error(f"调试信息 - 订单参数: {order}")
                        logging.error(f"调试信息 - 入场价格: {entry_price}")
                        logging.error(f"调试信息 - 交易品种: {symbol}")
                        logging.error(f"调试信息 - 固定损失: {order.get('fixed_loss', 0)}")
                        continue
                    volume = calculated_volume
                elif volume <= 0:
                    continue
                tick = mt5.symbol_info_tick(symbol)
                spread = tick.ask - tick.bid if tick else 0
                if sl_mode == "FIXED_POINTS":
                    if self.order_type == "buy":
                        sl_price = batch_entry_price - order["sl_points"] * point
                    else:
                        sl_price = (
                            batch_entry_price + order["sl_points"] * point + spread
                        )
                    mt5_order = self.trader.place_order_with_tp_sl(
                        symbol=symbol,
                        order_type=self.order_type,
                        volume=volume,
                        sl_points=order["sl_points"],
                        tp_points=order["tp_points"],
                        comment=f"批量下单{i+1}",
                    )
                else:
                    countdown = self.gui_window.components["countdown"]
                    timeframe = countdown.timeframe_combo.currentText()
                    lookback = order["sl_candle"]
                    rates = get_valid_rates(
                        symbol,
                        get_timeframe(timeframe),
                        lookback + 2,
                        self.gui_window,
                    )
                    if rates is None:
                        return
                    lowest_point = min([rate["low"] for rate in rates[2:]])
                    highest_point = max([rate["high"] for rate in rates[2:]])
                    tick = mt5.symbol_info_tick(symbol)
                    spread = tick.ask - tick.bid if tick else 0
                    if self.order_type == "buy":
                        sl_price = lowest_point - sl_offset
                    else:
                        sl_price = highest_point + sl_offset + spread
                    mt5_order = self.trader.place_order_with_key_level_sl(
                        symbol=symbol,
                        order_type=self.order_type,
                        volume=volume,
                        sl_price=sl_price,
                        tp_points=order["tp_points"],
                        comment=f"批量下单{i+1}",
                    )
                if mt5_order:
                    orders.append(mt5_order)
            if orders:
                if sl_mode == "CANDLE_KEY_LEVEL" and batch_order.orders:
                    config_manager.set(
                        "SL_MODE",
                        {"CANDLE_LOOKBACK": batch_order.orders[0]["sl_candle"]},
                    )
                    trading_settings.on_sl_mode_changed(
                        trading_settings.sl_mode_combo.currentIndex()
                    )
                self.gui_window.components["pnl_info"].update_daily_pnl_info(
                    self.trader
                )
                self.gui_window.components["account_info"].update_account_info(
                    self.trader
                )
                show_status_message(
                    self.gui_window, f"批量{self.order_type}订单已成功下单"
                )
                play_trade_beep(config_manager)
            else:
                show_status_message(self.gui_window, f"批量{self.order_type}单失败！")
        except Exception as e:
            show_status_message(self.gui_window, f"批量下单出错：{str(e)}")
            logging.error(f"下单错误详情：{str(e)}")
