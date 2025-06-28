from app.commands.base_command import BaseCommand
from app.utils.trade_helpers import (
    check_mt5_connection_and_notify,
    show_status_message,
)
import MetaTrader5 as mt5
import logging


class CancelAllPendingOrdersCommand(BaseCommand):
    def __init__(self, trader, gui_window):
        self.trader = trader
        self.gui_window = gui_window

    def execute(self):
        try:
            if not check_mt5_connection_and_notify(self.trader, self.gui_window):
                return
            orders = mt5.orders_get()
            if orders is None or len(orders) == 0:
                show_status_message(self.gui_window, "没有挂单！")
                return
            success_count = 0
            for order in orders:
                if order.type in [mt5.ORDER_TYPE_BUY_STOP, mt5.ORDER_TYPE_SELL_STOP]:
                    if self.trader.cancel_order(order.ticket):
                        success_count += 1
            if success_count > 0:
                show_status_message(self.gui_window, f"成功撤销{success_count}个挂单！")
            else:
                show_status_message(self.gui_window, "没有需要撤销的挂单！")
        except Exception as e:
            show_status_message(self.gui_window, f"撤销挂单出错：{str(e)}")
            logging.error(f"撤销挂单错误详情：{str(e)}")
