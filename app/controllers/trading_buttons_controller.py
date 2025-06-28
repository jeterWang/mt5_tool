from app.commands.place_batch_order import PlaceBatchOrderCommand
from app.commands.place_breakout_order import PlaceBreakoutOrderCommand
from app.commands.cancel_all_pending_orders import CancelAllPendingOrdersCommand
from app.commands.close_all_positions import CloseAllPositionsCommand
from app.commands.breakeven_all_positions import BreakevenAllPositionsCommand
from app.commands.move_stoploss_to_candle import MoveStoplossToCandleCommand


class TradingButtonsController:
    def __init__(self, trader, gui_window):
        self.trader = trader
        self.gui_window = gui_window

    def on_batch_buy(self):
        PlaceBatchOrderCommand(self.trader, self.gui_window, "buy").execute()

    def on_batch_sell(self):
        PlaceBatchOrderCommand(self.trader, self.gui_window, "sell").execute()

    def on_breakout_high(self):
        PlaceBreakoutOrderCommand(self.trader, self.gui_window, "high").execute()

    def on_breakout_low(self):
        PlaceBreakoutOrderCommand(self.trader, self.gui_window, "low").execute()

    def on_cancel_all_pending(self):
        CancelAllPendingOrdersCommand(self.trader, self.gui_window).execute()

    def on_breakeven_all(self):
        BreakevenAllPositionsCommand(self.trader, self.gui_window).execute()

    def on_close_all(self):
        CloseAllPositionsCommand(self.trader, self.gui_window).execute()

    def on_move_sl_1(self):
        MoveStoplossToCandleCommand(self.trader, self.gui_window, 1).execute()

    def on_move_sl_2(self):
        MoveStoplossToCandleCommand(self.trader, self.gui_window, 2).execute()

    def on_move_sl_3(self):
        MoveStoplossToCandleCommand(self.trader, self.gui_window, 3).execute()
