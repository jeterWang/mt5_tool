from app.commands.base_command import BaseCommand
from app.utils.trade_helpers import (
    check_mt5_connection_and_notify,
    show_status_message,
    play_trade_beep,
)
import MetaTrader5 as mt5
import logging
from app.config.config_manager import config_manager


class BreakevenAllPositionsCommand(BaseCommand):
    def __init__(self, trader, gui_window):
        self.trader = trader
        self.gui_window = gui_window

    def execute(self):
        try:
            if not check_mt5_connection_and_notify(self.trader, self.gui_window):
                return
            positions = mt5.positions_get()
            if positions is None:
                show_status_message(self.gui_window, "获取持仓失败！")
                return
            if len(positions) == 0:
                show_status_message(self.gui_window, "当前没有持仓！")
                return
            offset_points = config_manager.get("GUI_SETTINGS", {}).get(
                "BREAKEVEN_OFFSET_POINTS", 0
            )
            success_count = 0
            failed_positions = []
            modified_positions = []
            for position in positions:
                position_id = position.ticket
                entry_price = position.price_open
                point = mt5.symbol_info(position.symbol).point
                current_sl = position.sl
                if position.type == mt5.POSITION_TYPE_BUY:
                    sl_price = entry_price - offset_points * point
                    if (
                        current_sl is not None
                        and current_sl > 0
                        and sl_price <= current_sl
                    ):
                        continue
                else:
                    sl_price = entry_price + offset_points * point
                    if (
                        current_sl is not None
                        and current_sl > 0
                        and sl_price >= current_sl
                    ):
                        continue
                if self.trader.modify_position_sl_tp(position_id, sl=sl_price, tp=None):
                    success_count += 1
                    modified_positions.append(position_id)
                else:
                    failed_positions.append(position_id)
                    logging.error(f"修改止损失败，订单号: {position_id}")
            if success_count > 0:
                offset_text = ""
                if offset_points > 0:
                    offset_text = f"偏移{abs(offset_points)}点"
                elif offset_points < 0:
                    offset_text = f"提前{abs(offset_points)}点"
                else:
                    offset_text = "无偏移"
                message = f"成功将{success_count}个持仓的止损移动到入场价({offset_text})！订单号: {', '.join(map(str, modified_positions))}"
                show_status_message(self.gui_window, message)
                play_trade_beep(config_manager)
            if failed_positions:
                if success_count == 0:
                    show_status_message(self.gui_window, "所有持仓保本操作失败！")
        except Exception as e:
            show_status_message(self.gui_window, f"保本操作出错：{str(e)}")
            logging.error(f"保本操作错误详情：{str(e)}")
