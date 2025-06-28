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


class PlaceBreakoutOrderCommand(BaseCommand):
    def __init__(self, trader, gui_window, breakout_type):
        self.trader = trader
        self.gui_window = gui_window
        self.breakout_type = breakout_type  # 'high' or 'low'

    def execute(self):
        if not check_daily_loss_limit_and_notify(self.gui_window):
            return
        try:
            if not check_trade_limit_and_notify(self.gui_window.db, self.gui_window):
                return
            if not check_mt5_connection_and_notify(self.trader, self.gui_window):
                return
            trading_settings = self.gui_window.components["trading_settings"]
            batch_order = self.gui_window.components["batch_order"]
            countdown = self.gui_window.components["countdown"]
            symbol = trading_settings.symbol_input.currentText()
            timeframe = countdown.timeframe_combo.currentText()
            symbol_info = mt5.symbol_info(symbol)
            if symbol_info is None:
                show_status_message(self.gui_window, f"获取{symbol}信息失败！")
                return
            point = symbol_info.point
            rates = get_valid_rates(
                symbol, get_timeframe(timeframe), 3, self.gui_window
            )
            if rates is None:
                return
            previous_high = rates[1]["high"]
            previous_low = rates[1]["low"]
            high_offset = config_manager.get("BREAKEVEN_SETTINGS", {}).get(
                "HIGH_OFFSET_POINTS", 0
            )
            low_offset = config_manager.get("BREAKEVEN_SETTINGS", {}).get(
                "LOW_OFFSET_POINTS", 0
            )
            sl_offset = config_manager.get("BREAKEVEN_SETTINGS", {}).get(
                "SL_OFFSET_POINTS", 0
            )
            sl_mode = (
                "FIXED_POINTS"
                if trading_settings.sl_mode_combo.currentIndex() == 0
                else "CANDLE_KEY_LEVEL"
            )
            if self.breakout_type == "high":
                tick = mt5.symbol_info_tick(symbol)
                if tick is None or tick.ask is None or tick.bid is None:
                    show_status_message(self.gui_window, f"获取点差失败，无法挂单！")
                    return
                spread = tick.ask - tick.bid
                entry_price = previous_high + high_offset * point + spread
                order_type = "buy_stop"
                comment_prefix = f"{timeframe}高点突破买入"
            else:
                tick = mt5.symbol_info_tick(symbol)
                spread = tick.ask - tick.bid if tick else 0
                entry_price = previous_low - low_offset * point
                order_type = "sell_stop"
                comment_prefix = f"{timeframe}低点突破卖出"
            order_direction = "buy" if self.breakout_type == "high" else "sell"
            positions = self.trader.get_positions_by_symbol_and_type(
                symbol, order_direction
            )
            has_positions = bool(positions)
            orders = []
            batch_count = sum(1 for order in batch_order.orders if order["checked"])
            if has_positions:
                if sl_mode == "FIXED_POINTS":
                    if self.breakout_type == "high":
                        sl_price = (
                            entry_price - batch_order.orders[0]["sl_points"] * point
                        )
                    else:
                        sl_price = (
                            entry_price
                            + batch_order.orders[0]["sl_points"] * point
                            + spread
                        )
                else:
                    if self.breakout_type == "high":
                        sl_price = previous_low - sl_offset * point
                    else:
                        sl_price = previous_high + sl_offset * point + spread
                breakeven_volume = calculate_breakeven_position_size(
                    self.trader,
                    symbol,
                    order_direction,
                    sl_price,
                    entry_price,
                    batch_count,
                )
                if breakeven_volume <= 0:
                    show_status_message(
                        self.gui_window, "盈亏平衡手数计算失败，无法挂突破单！"
                    )
                    return
                for order in batch_order.orders:
                    if order["checked"]:
                        order["volume"] = breakeven_volume
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
                    calculated_volume = batch_order.calculate_position_size_for_order(
                        i, order_direction, entry_price, symbol
                    )
                    if calculated_volume <= 0:
                        logging.error(f"突破订单{i+1}：仓位计算失败，跳过")
                        continue
                    volume = calculated_volume
                elif volume <= 0:
                    continue
                sl_price = None
                if sl_mode == "FIXED_POINTS":
                    if self.breakout_type == "high":
                        sl_price = entry_price - order["sl_points"] * point
                    else:
                        sl_price = entry_price + order["sl_points"] * point + spread
                else:
                    lookback = order.get("sl_candle", 1)
                    rates = get_valid_rates(
                        symbol,
                        get_timeframe(timeframe),
                        lookback + 2,
                        self.gui_window,
                    )
                    if rates is None or len(rates) < 3:
                        logging.error(f"突破订单{i+1}：K线数据获取失败，跳过")
                        continue
                    lowest_point = min([rate["low"] for rate in rates[2:]])
                    highest_point = max([rate["high"] for rate in rates[2:]])
                    sl_offset_points = config_manager.get("BREAKEVEN_SETTINGS", {}).get(
                        "SL_OFFSET_POINTS", 0
                    )
                    sl_offset = sl_offset_points * point
                    tick = mt5.symbol_info_tick(symbol)
                    spread = tick.ask - tick.bid if tick else 0
                    if self.breakout_type == "high":
                        sl_price = lowest_point - sl_offset
                    else:
                        sl_price = highest_point + sl_offset + spread
                mt5_order = self.trader.place_pending_order(
                    symbol=symbol,
                    order_type=order_type,
                    volume=volume,
                    price=entry_price,
                    sl_price=sl_price,
                    tp_points=order["tp_points"],
                    comment=f"{comment_prefix}{i+1}",
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
                show_status_message(self.gui_window, f"突破订单已成功下单")
                play_trade_beep(config_manager)
            else:
                show_status_message(self.gui_window, f"{comment_prefix}失败！")
        except Exception as e:
            show_status_message(self.gui_window, f"挂突破单出错：{str(e)}")
            logging.error(f"下单错误详情：{str(e)}")
