"""
交易按钮模块

提供批量下单、突破下单、撤销挂单和一键平仓等交易操作按钮
"""

from PyQt6.QtWidgets import QHBoxLayout, QVBoxLayout, QPushButton
import MetaTrader5 as mt5
import winsound
import logging

logger = logging.getLogger(__name__)

from app.config.config_manager import config_manager
from app.gui.risk_control import check_trade_limit
from app.utils.trade_helpers import (
    check_daily_loss_limit_and_notify,
    check_trade_limit_and_notify,
    check_mt5_connection_and_notify,
    get_valid_rates,
    play_trade_beep,
    show_status_message,
)
from app.commands.place_batch_order import PlaceBatchOrderCommand
from app.commands.place_breakout_order import PlaceBreakoutOrderCommand
from app.commands.cancel_all_pending_orders import CancelAllPendingOrdersCommand
from app.commands.close_all_positions import CloseAllPositionsCommand
from app.commands.breakeven_all_positions import BreakevenAllPositionsCommand
from app.commands.move_stoploss_to_candle import MoveStoplossToCandleCommand


class TradingButtonsSection:
    """交易按钮区域"""

    def __init__(self):
        """初始化交易按钮区域"""
        self.layout = QVBoxLayout()  # 改为垂直布局，便于分两行
        self.init_ui()
        self.connect_signals()
        self.trader = None
        self.gui_window = None

    def init_ui(self):
        """初始化UI"""
        # 第一行按钮
        self.row1 = QHBoxLayout()
        self.place_batch_buy_btn = QPushButton("批量买入")
        self.place_batch_buy_btn.setEnabled(False)
        self.place_batch_buy_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border: none;
                padding: 5px;
                font-weight: bold;
                min-width: 100px;
                min-height: 30px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
            }
            """
        )
        self.row1.addWidget(self.place_batch_buy_btn)

        self.place_batch_sell_btn = QPushButton("批量卖出")
        self.place_batch_sell_btn.setEnabled(False)
        self.place_batch_sell_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 5px;
                font-weight: bold;
                min-width: 100px;
                min-height: 30px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
            }
            """
        )
        self.row1.addWidget(self.place_batch_sell_btn)

        self.place_breakout_high_btn = QPushButton("挂高点突破")
        self.place_breakout_high_btn.setEnabled(False)
        self.place_breakout_high_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border: none;
                padding: 5px;
                font-weight: bold;
                min-width: 100px;
                min-height: 30px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
            }
            """
        )
        self.row1.addWidget(self.place_breakout_high_btn)

        self.place_breakout_low_btn = QPushButton("挂低点突破")
        self.place_breakout_low_btn.setEnabled(False)
        self.place_breakout_low_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 5px;
                font-weight: bold;
                min-width: 100px;
                min-height: 30px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
            }
            """
        )
        self.row1.addWidget(self.place_breakout_low_btn)

        self.cancel_all_pending_btn = QPushButton("撤销挂单")
        self.cancel_all_pending_btn.setEnabled(False)
        self.cancel_all_pending_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #f1c40f;
                color: white;
                border: none;
                padding: 5px;
                font-weight: bold;
                min-width: 100px;
                min-height: 30px;
            }
            QPushButton:hover {
                background-color: #f39c12;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
            }
            """
        )
        self.row1.addWidget(self.cancel_all_pending_btn)

        # 第二行按钮
        self.row2 = QHBoxLayout()
        self.breakeven_all_btn = QPushButton("一键保本")
        self.breakeven_all_btn.setEnabled(False)
        self.breakeven_all_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #9b59b6;
                color: white;
                border: none;
                padding: 5px;
                font-weight: bold;
                min-width: 100px;
                min-height: 30px;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
            }
            """
        )
        self.row2.addWidget(self.breakeven_all_btn)

        self.close_all_btn = QPushButton("一键平仓")
        self.close_all_btn.setEnabled(False)
        self.close_all_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 5px;
                font-weight: bold;
                min-width: 100px;
                min-height: 30px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
            }
            """
        )
        self.row2.addWidget(self.close_all_btn)

        # 新增移动止盈按钮
        self.move_sl_1_btn = QPushButton("移动1单止盈")
        self.move_sl_2_btn = QPushButton("移动2单止盈")
        self.move_sl_3_btn = QPushButton("移动3单止盈")
        for btn in [self.move_sl_1_btn, self.move_sl_2_btn, self.move_sl_3_btn]:
            btn.setEnabled(False)
            btn.setStyleSheet(
                """
                QPushButton {
                    background-color: #16a085;
                    color: white;
                    border: none;
                    padding: 5px;
                    font-weight: bold;
                    min-width: 100px;
                    min-height: 30px;
                }
                QPushButton:hover {
                    background-color: #138d75;
                }
                QPushButton:disabled {
                    background-color: #95a5a6;
                }
                """
            )
            self.row2.addWidget(btn)

        # 添加两行到主布局
        self.layout.addLayout(self.row1)
        self.layout.addLayout(self.row2)

    def connect_signals(self):
        """连接信号到对应的槽函数"""
        self.place_batch_buy_btn.clicked.connect(
            lambda: PlaceBatchOrderCommand(
                self.trader, self.gui_window, "buy"
            ).execute()
        )
        self.place_batch_sell_btn.clicked.connect(
            lambda: PlaceBatchOrderCommand(
                self.trader, self.gui_window, "sell"
            ).execute()
        )
        self.place_breakout_high_btn.clicked.connect(
            lambda: PlaceBreakoutOrderCommand(
                self.trader, self.gui_window, "high"
            ).execute()
        )
        self.place_breakout_low_btn.clicked.connect(
            lambda: PlaceBreakoutOrderCommand(
                self.trader, self.gui_window, "low"
            ).execute()
        )
        self.cancel_all_pending_btn.clicked.connect(
            lambda: CancelAllPendingOrdersCommand(
                self.trader, self.gui_window
            ).execute()
        )
        self.breakeven_all_btn.clicked.connect(
            lambda: BreakevenAllPositionsCommand(self.trader, self.gui_window).execute()
        )
        self.close_all_btn.clicked.connect(
            lambda: CloseAllPositionsCommand(self.trader, self.gui_window).execute()
        )
        self.move_sl_1_btn.clicked.connect(
            lambda: MoveStoplossToCandleCommand(
                self.trader, self.gui_window, 1
            ).execute()
        )
        self.move_sl_2_btn.clicked.connect(
            lambda: MoveStoplossToCandleCommand(
                self.trader, self.gui_window, 2
            ).execute()
        )
        self.move_sl_3_btn.clicked.connect(
            lambda: MoveStoplossToCandleCommand(
                self.trader, self.gui_window, 3
            ).execute()
        )

    def set_trader_and_window(self, trader, gui_window):
        """设置交易者和主窗口引用"""
        self.trader = trader
        self.gui_window = gui_window

        # 在设置完trader引用后，如果已连接就启用按钮
        if self.trader and self.trader.is_connected():
            self.place_batch_buy_btn.setEnabled(True)
            self.place_batch_sell_btn.setEnabled(True)
            self.place_breakout_high_btn.setEnabled(True)
            self.place_breakout_low_btn.setEnabled(True)
            self.cancel_all_pending_btn.setEnabled(True)
            self.breakeven_all_btn.setEnabled(True)
            self.close_all_btn.setEnabled(True)
            self.move_sl_1_btn.setEnabled(True)
            self.move_sl_2_btn.setEnabled(True)
            self.move_sl_3_btn.setEnabled(True)

    def get_timeframe(self, timeframe: str) -> int:
        """
        将时间周期字符串转换为MT5的时间周期常量

        Args:
            timeframe: 时间周期字符串，如'M1', 'M5'等

        Returns:
            对应的MT5时间周期常量
        """
        timeframe_map = {
            "M1": mt5.TIMEFRAME_M1,
            "M5": mt5.TIMEFRAME_M5,
            "M15": mt5.TIMEFRAME_M15,
            "M30": mt5.TIMEFRAME_M30,
            "H1": mt5.TIMEFRAME_H1,
            "H4": mt5.TIMEFRAME_H4,
        }
        return timeframe_map.get(timeframe, mt5.TIMEFRAME_M1)
