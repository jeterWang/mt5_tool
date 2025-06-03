"""
交易按钮模块

提供批量下单、突破下单、撤销挂单和一键平仓等交易操作按钮
"""

from PyQt6.QtWidgets import QHBoxLayout, QVBoxLayout, QPushButton
import MetaTrader5 as mt5
import winsound

from config.loader import GUI_SETTINGS, BATCH_ORDER_DEFAULTS, SL_MODE, BREAKOUT_SETTINGS
from app.gui.risk_control import check_trade_limit


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
        self.place_batch_buy_btn.clicked.connect(lambda: self.place_batch_orders("buy"))
        self.place_batch_sell_btn.clicked.connect(
            lambda: self.place_batch_orders("sell")
        )
        self.place_breakout_high_btn.clicked.connect(
            lambda: self.place_breakout_order("high")
        )
        self.place_breakout_low_btn.clicked.connect(
            lambda: self.place_breakout_order("low")
        )
        self.cancel_all_pending_btn.clicked.connect(self.cancel_all_pending_orders)
        self.breakeven_all_btn.clicked.connect(self.breakeven_all_positions)
        self.close_all_btn.clicked.connect(self.close_all_positions)
        self.move_sl_1_btn.clicked.connect(lambda: self.move_stoploss_to_candle(1))
        self.move_sl_2_btn.clicked.connect(lambda: self.move_stoploss_to_candle(2))
        self.move_sl_3_btn.clicked.connect(lambda: self.move_stoploss_to_candle(3))

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

    def place_batch_orders(self, order_type: str):
        """
        批量下单，包含风控检查

        Args:
            order_type: 订单类型，'buy' 或 'sell'
        """
        try:
            # 检查交易次数限制
            if not check_trade_limit(self.gui_window.db, self.gui_window):
                return

            # 检查MT5连接状态
            if not self.trader or not self.trader.is_connected():
                self.gui_window.status_bar.showMessage("MT5未连接，请检查连接状态！")
                return

            # 检查MT5自动交易是否启用
            if not mt5.terminal_info().trade_allowed:
                self.gui_window.status_bar.showMessage("请在MT5平台中启用自动交易！")
                return

            # 获取交易设置
            trading_settings = self.gui_window.components["trading_settings"]
            batch_order = self.gui_window.components["batch_order"]

            symbol = trading_settings.symbol_input.currentText()

            # 显示正在下单的提示
            self.gui_window.status_bar.showMessage(f"正在执行批量{order_type}单...")

            # 检查止损模式
            sl_mode = (
                "FIXED_POINTS"
                if trading_settings.sl_mode_combo.currentIndex() == 0
                else "CANDLE_KEY_LEVEL"
            )

            # 如果是K线关键位止损，需要获取K线数据
            if sl_mode == "CANDLE_KEY_LEVEL":
                # 获取交易品种点值
                symbol_info = mt5.symbol_info(symbol)
                if symbol_info is None:
                    self.gui_window.status_bar.showMessage(f"获取{symbol}信息失败！")
                    return

                point = symbol_info.point
                sl_offset = BREAKOUT_SETTINGS["SL_OFFSET_POINTS"] * point

            # 下所有勾选的订单
            orders = []
            for i, order in enumerate(batch_order.orders):
                if not order["checked"] or order["volume"] <= 0:
                    continue
                if sl_mode == "FIXED_POINTS":
                    mt5_order = self.trader.place_order_with_tp_sl(
                        symbol=symbol,
                        order_type=order_type,
                        volume=order["volume"],
                        sl_points=order["sl_points"],
                        tp_points=order["tp_points"],
                        comment=f"批量下单{i+1}",
                    )
                else:
                    countdown = self.gui_window.components["countdown"]
                    timeframe = countdown.timeframe_combo.currentText()
                    lookback = order["sl_candle"]
                    rates = mt5.copy_rates_from_pos(
                        symbol, self.get_timeframe(timeframe), 0, lookback + 2
                    )
                    if rates is None or len(rates) < lookback + 2:
                        self.gui_window.status_bar.showMessage(
                            f"获取K线数据失败，需要至少{lookback + 2}根K线！"
                        )
                        return
                    lowest_point = min([rate["low"] for rate in rates[2:]])
                    highest_point = max([rate["high"] for rate in rates[2:]])
                    if order_type == "buy":
                        sl_price = lowest_point - sl_offset
                    else:
                        sl_price = highest_point + sl_offset
                    mt5_order = self.trader.place_order_with_key_level_sl(
                        symbol=symbol,
                        order_type=order_type,
                        volume=order["volume"],
                        sl_price=sl_price,
                        tp_points=order["tp_points"],
                        comment=f"批量下单{i+1}",
                    )
                if mt5_order:
                    orders.append(mt5_order)

            if orders:
                # 更新默认K线回溯数量
                if sl_mode == "CANDLE_KEY_LEVEL" and batch_order.orders:
                    SL_MODE["CANDLE_LOOKBACK"] = batch_order.orders[0]["sl_candle"]
                    # 保存配置
                    trading_settings.on_sl_mode_changed(
                        trading_settings.sl_mode_combo.currentIndex()
                    )

                # 更新界面
                self.gui_window.components["pnl_info"].update_daily_pnl_info(
                    self.trader
                )
                self.gui_window.components["account_info"].update_account_info(
                    self.trader
                )
                self.gui_window.status_bar.showMessage(
                    f"批量{order_type}订单已成功下单"
                )
                # 播放提示音
                winsound.Beep(
                    GUI_SETTINGS["BEEP_FREQUENCY"], GUI_SETTINGS["BEEP_DURATION"]
                )
            else:
                self.gui_window.status_bar.showMessage(f"批量{order_type}单失败！")
        except Exception as e:
            self.gui_window.status_bar.showMessage(f"批量下单出错：{str(e)}")
            print(f"下单错误详情：{str(e)}")

    def place_breakout_order(self, breakout_type: str):
        """
        挂突破单

        Args:
            breakout_type: 'high' 或 'low'，表示高点或低点突破
        """
        try:
            # 检查交易次数限制
            if not check_trade_limit(self.gui_window.db, self.gui_window):
                return

            # 检查MT5连接状态
            if not self.trader or not self.trader.is_connected():
                self.gui_window.status_bar.showMessage("MT5未连接，请检查连接状态！")
                return

            # 检查MT5自动交易是否启用
            if not mt5.terminal_info().trade_allowed:
                self.gui_window.status_bar.showMessage("请在MT5平台中启用自动交易！")
                return

            # 获取交易设置
            trading_settings = self.gui_window.components["trading_settings"]
            batch_order = self.gui_window.components["batch_order"]
            countdown = self.gui_window.components["countdown"]

            symbol = trading_settings.symbol_input.currentText()
            timeframe = countdown.timeframe_combo.currentText()

            # 获取交易品种点值
            symbol_info = mt5.symbol_info(symbol)
            if symbol_info is None:
                self.gui_window.status_bar.showMessage(f"获取{symbol}信息失败！")
                return

            point = symbol_info.point

            # 前一根K线的高点和低点（索引1是前一根，因为索引0是当前正在形成的K线）
            rates = mt5.copy_rates_from_pos(symbol, self.get_timeframe(timeframe), 0, 3)
            if rates is None or len(rates) < 3:
                self.gui_window.status_bar.showMessage(
                    "获取K线数据失败，需要至少3根K线！"
                )
                return

            previous_high = rates[1]["high"]
            previous_low = rates[1]["low"]

            # 从配置文件获取偏移量设置
            high_offset = BREAKOUT_SETTINGS["HIGH_OFFSET_POINTS"]
            low_offset = BREAKOUT_SETTINGS["LOW_OFFSET_POINTS"]
            sl_offset = BREAKOUT_SETTINGS["SL_OFFSET_POINTS"]

            # 检查止损模式
            sl_mode = (
                "FIXED_POINTS"
                if trading_settings.sl_mode_combo.currentIndex() == 0
                else "CANDLE_KEY_LEVEL"
            )

            # 根据突破类型设置价格、订单类型
            if breakout_type == "high":
                # 买入价格 = 前一根K线高点 + 高点偏移量 * 点值
                entry_price = previous_high + high_offset * point
                order_type = "buy_stop"  # 使用buy_stop而不是buy
                comment_prefix = f"{timeframe}高点突破买入"
            else:
                # 卖出价格 = 前一根K线低点 - 低点偏移量 * 点值
                entry_price = previous_low - low_offset * point
                order_type = "sell_stop"  # 使用sell_stop而不是sell
                comment_prefix = f"{timeframe}低点突破卖出"

            # 下所有勾选的订单
            orders = []
            order_details = []
            for i, order in enumerate(batch_order.orders):
                if not order["checked"] or order["volume"] <= 0:
                    continue
                sl_price = None
                if sl_mode == "FIXED_POINTS":
                    if breakout_type == "high":
                        sl_price = entry_price - order["sl_points"] * point
                    else:
                        sl_price = entry_price + order["sl_points"] * point
                else:
                    countdown = self.gui_window.components["countdown"]
                    timeframe = countdown.timeframe_combo.currentText()
                    lookback = order["sl_candle"]
                    rates = mt5.copy_rates_from_pos(
                        symbol, self.get_timeframe(timeframe), 0, lookback + 2
                    )
                    if rates is None or len(rates) < lookback + 2:
                        self.gui_window.status_bar.showMessage(
                            f"获取K线数据失败，需要至少{lookback + 2}根K线！"
                        )
                        return
                    lowest_point = min([rate["low"] for rate in rates[2:]])
                    highest_point = max([rate["high"] for rate in rates[2:]])
                    if breakout_type == "high":
                        sl_price = lowest_point - sl_offset * point
                    else:
                        sl_price = highest_point + sl_offset * point
                mt5_order = self.trader.place_pending_order(
                    symbol=symbol,
                    order_type=order_type,
                    volume=order["volume"],
                    price=entry_price,
                    sl_price=sl_price,
                    tp_points=order["tp_points"],
                    comment=f"{comment_prefix}{i+1}",
                )
                if mt5_order:
                    orders.append(mt5_order)
                    order_details.append(
                        f"订单{i+1}: K线数={order['sl_candle']}, 止损价={sl_price:.5f}"
                    )

            if orders:
                # 更新默认K线回溯数量
                if sl_mode == "CANDLE_KEY_LEVEL" and batch_order.orders:
                    SL_MODE["CANDLE_LOOKBACK"] = batch_order.orders[0]["sl_candle"]
                    # 保存配置
                    trading_settings.on_sl_mode_changed(
                        trading_settings.sl_mode_combo.currentIndex()
                    )

                # 更新界面
                self.gui_window.components["pnl_info"].update_daily_pnl_info(
                    self.trader
                )
                self.gui_window.components["account_info"].update_account_info(
                    self.trader
                )
                self.gui_window.status_bar.showMessage(f"突破订单已成功下单")

                # 播放提示音
                winsound.Beep(
                    GUI_SETTINGS["BEEP_FREQUENCY"], GUI_SETTINGS["BEEP_DURATION"]
                )
            else:
                self.gui_window.status_bar.showMessage(f"{comment_prefix}失败！")
        except Exception as e:
            self.gui_window.status_bar.showMessage(f"挂突破单出错：{str(e)}")
            print(f"下单错误详情：{str(e)}")

    def cancel_all_pending_orders(self):
        """撤销所有挂单"""
        try:
            # 获取所有挂单
            orders = mt5.orders_get()
            if orders is None or len(orders) == 0:
                self.gui_window.status_bar.showMessage("没有挂单！")
                return

            success_count = 0
            for order in orders:
                # 只撤销挂单（包括突破单）
                if order.type in [mt5.ORDER_TYPE_BUY_STOP, mt5.ORDER_TYPE_SELL_STOP]:
                    if self.trader.cancel_order(order.ticket):
                        success_count += 1

            if success_count > 0:
                self.gui_window.status_bar.showMessage(
                    f"成功撤销{success_count}个挂单！"
                )
            else:
                self.gui_window.status_bar.showMessage("没有需要撤销的挂单！")
        except Exception as e:
            self.gui_window.status_bar.showMessage(f"撤销挂单出错：{str(e)}")

    def close_all_positions(self):
        """一键平仓所有订单"""
        try:
            positions = self.trader.get_all_positions()
            if not positions:
                self.gui_window.status_bar.showMessage("当前没有持仓！")
                return

            success_count = 0
            for position in positions:
                if self.trader.close_position(position["ticket"]):
                    success_count += 1

            if success_count == len(positions):
                self.gui_window.status_bar.showMessage("所有订单平仓成功！")

                # 立即同步平仓记录到Excel
                try:
                    self.trader.sync_closed_trades_to_excel()
                    print("已同步平仓记录到Excel")
                except Exception as e:
                    print(f"同步平仓记录到Excel失败: {str(e)}")

                # 立即重新统计交易次数
                try:
                    if self.gui_window.db.auto_update_trade_count_from_xlsx(
                        self.trader
                    ):
                        # 更新界面显示
                        account_info = self.gui_window.components["account_info"]
                        account_info.update_trade_count_display(self.gui_window.db)
                        print("已更新交易次数统计")
                except Exception as e:
                    print(f"更新交易次数统计失败: {str(e)}")

                # 更新盈亏显示
                try:
                    pnl_info = self.gui_window.components["pnl_info"]
                    pnl_info.update_daily_pnl_info(self.trader)
                    print("已更新盈亏显示")
                except Exception as e:
                    print(f"更新盈亏显示失败: {str(e)}")

            else:
                self.gui_window.status_bar.showMessage(
                    f"部分订单平仓失败！成功：{success_count}/{len(positions)}"
                )
        except Exception as e:
            self.gui_window.status_bar.showMessage(f"一键平仓出错：{str(e)}")

    def breakeven_all_positions(self):
        """将所有持仓的止损移动到入场价（保本）"""
        try:
            # 检查MT5连接状态
            if not self.trader or not self.trader.is_connected():
                self.gui_window.status_bar.showMessage("MT5未连接，请检查连接状态！")
                return

            # 检查MT5自动交易是否启用
            if not mt5.terminal_info().trade_allowed:
                self.gui_window.status_bar.showMessage("请在MT5平台中启用自动交易！")
                return

            # 获取所有持仓
            positions = mt5.positions_get()
            if positions is None:
                self.gui_window.status_bar.showMessage("获取持仓失败！")
                return

            if len(positions) == 0:
                self.gui_window.status_bar.showMessage("当前没有持仓！")
                return

            # 获取保本偏移点数
            offset_points = GUI_SETTINGS.get("BREAKEVEN_OFFSET_POINTS", 0)

            # 统计成功和失败的订单
            success_count = 0
            failed_positions = []
            modified_positions = []

            # 遍历所有持仓
            for position in positions:
                # 获取订单属性
                position_id = position.ticket
                entry_price = position.price_open
                point = mt5.symbol_info(position.symbol).point

                # 根据订单类型和偏移点数计算止损价格
                if position.type == mt5.POSITION_TYPE_BUY:
                    # 买入订单，止损设置在入场价偏移offset_points个点
                    # 如果偏移为正，则止损设在入场价下方；如果为负，则设在入场价上方
                    sl_price = entry_price - offset_points * point
                else:
                    # 卖出订单，止损设置在入场价偏移offset_points个点
                    # 如果偏移为正，则止损设在入场价上方；如果为负，则设在入场价下方
                    sl_price = entry_price + offset_points * point

                # 使用trader中的修改止损止盈方法
                if self.trader.modify_position_sl_tp(position_id, sl=sl_price, tp=None):
                    success_count += 1
                    modified_positions.append(position_id)
                else:
                    failed_positions.append(position_id)
                    print(f"修改止损失败，订单号: {position_id}")

            # 显示操作结果
            if success_count > 0:
                # 构建消息，显示偏移点数
                offset_text = ""
                if offset_points > 0:
                    offset_text = f"偏移{abs(offset_points)}点"
                elif offset_points < 0:
                    offset_text = f"提前{abs(offset_points)}点"
                else:
                    offset_text = "无偏移"

                message = f"成功将{success_count}个持仓的止损移动到入场价({offset_text})！订单号: {', '.join(map(str, modified_positions))}"
                self.gui_window.status_bar.showMessage(message)
                # 播放提示音
                winsound.Beep(
                    GUI_SETTINGS["BEEP_FREQUENCY"], GUI_SETTINGS["BEEP_DURATION"]
                )

            if failed_positions:
                print(f"以下订单修改失败: {', '.join(map(str, failed_positions))}")
                # 如果有失败的，在日志中显示
                if success_count == 0:
                    self.gui_window.status_bar.showMessage(f"所有持仓保本操作失败！")
                else:
                    # 已经在上面显示了成功信息，这里只记录日志
                    pass

        except Exception as e:
            self.gui_window.status_bar.showMessage(f"保本操作出错：{str(e)}")
            print(f"保本操作错误详情：{str(e)}")

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

    def move_stoploss_to_candle(self, n: int):
        """
        移动前n个持仓的止损到前一根K线的低点/高点
        买单移动到前一根K线的high，卖单到low

        Args:
            n: 要移动的持仓数量
        """
        try:
            # 检查MT5连接状态
            if not self.trader or not self.trader.is_connected():
                self.gui_window.status_bar.showMessage("MT5未连接，请检查连接状态！")
                return

            # 检查MT5自动交易是否启用
            if not mt5.terminal_info().trade_allowed:
                self.gui_window.status_bar.showMessage("请在MT5平台中启用自动交易！")
                return

            # 获取所有持仓
            positions = self.trader.get_all_positions()
            if not positions:
                self.gui_window.status_bar.showMessage("当前没有持仓！")
                return

            # 按开仓时间排序（ticket越小越早）
            positions = sorted(positions, key=lambda x: x.get("time", 0))

            # 统计成功和失败的订单
            success_count = 0
            failed_positions = []
            modified_positions = []
            details = []

            # 获取当前K线周期
            countdown = self.gui_window.components["countdown"]
            timeframe = countdown.timeframe_combo.currentText()

            # 处理前n个持仓
            for position in positions[:n]:
                position_id = position["ticket"]
                symbol = position["symbol"]
                pos_type = position["type"]

                # 获取前两根K线数据
                rates = mt5.copy_rates_from_pos(
                    symbol, self.get_timeframe(timeframe), 0, 3
                )
                if rates is None or len(rates) < 3:
                    failed_positions.append(position_id)
                    details.append(f"{symbol}订单{position_id}获取K线失败")
                    continue

                # 获取前一根K线的最高点和最低点（索引1是前一根K线，因为索引0是当前K线）
                prev_candle = rates[1]  # 使用索引1获取前一根K线
                print(prev_candle)
                if pos_type == mt5.POSITION_TYPE_BUY:
                    # 买单移动到前一根K线的最低价
                    new_sl = prev_candle["low"]
                else:
                    # 卖单移动到前一根K线的最高价
                    new_sl = prev_candle["high"]

                # 修改止损
                if self.trader.modify_position_sl_tp(position_id, sl=new_sl, tp=None):
                    success_count += 1
                    modified_positions.append(position_id)
                    details.append(f"{symbol}订单{position_id}止损已移动到{new_sl:.5f}")
                else:
                    failed_positions.append(position_id)
                    details.append(f"{symbol}订单{position_id}止损修改失败")

            # 显示操作结果
            if success_count > 0:
                message = f"成功移动{success_count}个持仓的止损！订单号: {', '.join(map(str, modified_positions))}"
                if failed_positions:
                    message += f"\n失败订单: {', '.join(map(str, failed_positions))}"
                self.gui_window.status_bar.showMessage(message)
                # 播放提示音
                winsound.Beep(
                    GUI_SETTINGS["BEEP_FREQUENCY"], GUI_SETTINGS["BEEP_DURATION"]
                )
            else:
                self.gui_window.status_bar.showMessage("所有持仓止损移动失败！")

            # 打印详细信息
            print("\n".join(details))

        except Exception as e:
            self.gui_window.status_bar.showMessage(f"移动止损出错：{str(e)}")
            print(f"移动止损错误详情：{str(e)}")
