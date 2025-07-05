"""
调试版本的交易按钮控制器
使用调试版本的下单命令来找出问题
"""

import logging
from app.commands.place_breakout_order import PlaceBreakoutOrderCommand
from app.commands.cancel_all_pending_orders import CancelAllPendingOrdersCommand
from app.commands.close_all_positions import CloseAllPositionsCommand
from app.commands.breakeven_all_positions import BreakevenAllPositionsCommand
from app.commands.move_stoploss_to_candle import MoveStoplossToCandleCommand
from debug_place_batch_order import DebugPlaceBatchOrderCommand

logger = logging.getLogger(__name__)

class DebugTradingButtonsController:
    def __init__(self, trader, gui_window):
        self.trader = trader
        self.gui_window = gui_window
        logger.info("初始化调试版交易按钮控制器")

    def on_batch_buy(self):
        logger.info("点击批量买入按钮")
        DebugPlaceBatchOrderCommand(self.trader, self.gui_window, "buy").execute()

    def on_batch_sell(self):
        logger.info("点击批量卖出按钮")
        DebugPlaceBatchOrderCommand(self.trader, self.gui_window, "sell").execute()

    def on_breakout_high(self):
        logger.info("点击突破做多按钮")
        PlaceBreakoutOrderCommand(self.trader, self.gui_window, "high").execute()

    def on_breakout_low(self):
        logger.info("点击突破做空按钮")
        PlaceBreakoutOrderCommand(self.trader, self.gui_window, "low").execute()

    def on_cancel_all_pending(self):
        logger.info("点击取消所有挂单按钮")
        CancelAllPendingOrdersCommand(self.trader, self.gui_window).execute()

    def on_breakeven_all(self):
        logger.info("点击全部保本按钮")
        BreakevenAllPositionsCommand(self.trader, self.gui_window).execute()

    def on_close_all(self):
        logger.info("点击全部平仓按钮")
        CloseAllPositionsCommand(self.trader, self.gui_window).execute()

    def on_move_sl_1(self):
        logger.info("点击移动止损1按钮")
        MoveStoplossToCandleCommand(self.trader, self.gui_window, 1).execute()

    def on_move_sl_2(self):
        logger.info("点击移动止损2按钮")
        MoveStoplossToCandleCommand(self.trader, self.gui_window, 2).execute()

    def on_move_sl_3(self):
        logger.info("点击移动止损3按钮")
        MoveStoplossToCandleCommand(self.trader, self.gui_window, 3).execute()
