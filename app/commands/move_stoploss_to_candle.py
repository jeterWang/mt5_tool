from app.commands.base_command import BaseCommand
from app.utils.trade_helpers import (
    check_mt5_connection_and_notify,
    show_status_message,
    play_trade_beep,
    get_valid_rates,
    get_timeframe,
)
import MetaTrader5 as mt5
import logging


class MoveStoplossToCandleCommand(BaseCommand):
    def __init__(self, trader, gui_window, n):
        self.trader = trader
        self.gui_window = gui_window
        self.n = n

    def execute(self):
        try:
            if not check_mt5_connection_and_notify(self.trader, self.gui_window):
                return
            positions = self.trader.get_all_positions()
            if not positions:
                show_status_message(self.gui_window, "当前没有持仓！")
                return
            positions = sorted(positions, key=lambda x: x.get("time", 0))
            success_count = 0
            failed_positions = []
            modified_positions = []
            details = []
            countdown = self.gui_window.components["countdown"]
            timeframe = countdown.timeframe_combo.currentText()
            for position in positions[: self.n]:
                position_id = position["ticket"]
                symbol = position["symbol"]
                pos_type = position["type"]
                rates = get_valid_rates(
                    symbol, get_timeframe(timeframe), 3, self.gui_window
                )
                if rates is None:
                    failed_positions.append(position_id)
                    details.append(f"{symbol}订单{position_id}获取K线失败")
                    continue
                prev_candle = rates[1]
                if pos_type == mt5.POSITION_TYPE_BUY:
                    new_sl = prev_candle["low"]
                else:
                    new_sl = prev_candle["high"]
                if self.trader.modify_position_sl_tp(position_id, sl=new_sl, tp=None):
                    success_count += 1
                    modified_positions.append(position_id)
                    details.append(f"{symbol}订单{position_id}止损已移动到{new_sl:.5f}")
                else:
                    failed_positions.append(position_id)
                    details.append(f"{symbol}订单{position_id}止损修改失败")
            if success_count > 0:
                message = f"成功移动{success_count}个持仓的止损！订单号: {', '.join(map(str, modified_positions))}"
                if failed_positions:
                    message += f"\n失败订单: {', '.join(map(str, failed_positions))}"
                show_status_message(self.gui_window, message)
                play_trade_beep(self.gui_window.config_manager)
            else:
                show_status_message(self.gui_window, "所有持仓止损移动失败！")
        except Exception as e:
            show_status_message(self.gui_window, f"移动止损出错：{str(e)}")
            logging.error(f"移动止损错误详情：{str(e)}")
