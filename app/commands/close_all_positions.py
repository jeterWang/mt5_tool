from app.commands.base_command import BaseCommand
from app.utils.trade_helpers import show_status_message
import logging


class CloseAllPositionsCommand(BaseCommand):
    def __init__(self, trader, gui_window):
        self.trader = trader
        self.gui_window = gui_window

    def execute(self):
        try:
            positions = self.trader.get_all_positions()
            if not positions:
                show_status_message(self.gui_window, "当前没有持仓！")
                return
            success_count = 0
            for position in positions:
                if self.trader.close_position(position["ticket"]):
                    success_count += 1
            if success_count == len(positions):
                show_status_message(self.gui_window, "所有订单平仓成功！")
                try:
                    self.trader.sync_closed_trades_to_db()
                except Exception as e:
                    logging.error(f"同步平仓记录到数据库失败: {str(e)}")
                try:
                    pnl_info = self.gui_window.components["pnl_info"]
                    pnl_info.update_daily_pnl_info(self.trader)
                except Exception as e:
                    logging.error(f"更新盈亏显示失败: {str(e)}")
            else:
                show_status_message(
                    self.gui_window,
                    f"部分订单平仓失败！成功：{success_count}/{len(positions)}",
                )
        except Exception as e:
            show_status_message(self.gui_window, f"一键平仓出错：{str(e)}")
            logging.error(f"一键平仓错误详情：{str(e)}")
