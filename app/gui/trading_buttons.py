"""
交易按钮模块

提供批量下单、突破下单、撤销挂单和一键平仓等交易操作按钮
"""

from PyQt6.QtWidgets import QHBoxLayout, QPushButton
import MetaTrader5 as mt5
import winsound

from config.loader import GUI_SETTINGS, BATCH_ORDER_DEFAULTS, SL_MODE, BREAKOUT_SETTINGS
from app.gui.risk_control import check_trade_limit, increment_trade_count


class TradingButtonsSection:
    """交易按钮区域"""

    def __init__(self):
        """初始化交易按钮区域"""
        self.layout = QHBoxLayout()
        self.init_ui()
        self.connect_signals()
        self.trader = None
        self.gui_window = None

    def init_ui(self):
        """初始化UI"""
        # 批量买入按钮
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

        # 批量卖出按钮
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

        # 挂高点突破按钮
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

        # 挂低点突破按钮
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

        # 撤销挂单按钮
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

        # 一键平仓按钮
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

        # 添加所有按钮到布局
        self.layout.addWidget(self.place_batch_buy_btn)
        self.layout.addWidget(self.place_batch_sell_btn)
        self.layout.addWidget(self.place_breakout_high_btn)
        self.layout.addWidget(self.place_breakout_low_btn)
        self.layout.addWidget(self.cancel_all_pending_btn)
        self.layout.addWidget(self.close_all_btn)

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
        self.close_all_btn.clicked.connect(self.close_all_positions)

    def set_trader_and_window(self, trader, gui_window):
        """设置交易者和主窗口引用"""
        self.trader = trader
        self.gui_window = gui_window

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

            # 下四个订单
            orders = []
            for i in range(4):
                # 检查手数是否为0，跳过
                if batch_order.volume_inputs[i].value() <= 0:
                    continue

                # 根据止损模式设置止损
                if sl_mode == "FIXED_POINTS":
                    # 使用固定点数止损
                    order = self.trader.place_order_with_tp_sl(
                        symbol=symbol,
                        order_type=order_type,
                        volume=batch_order.volume_inputs[i].value(),
                        sl_points=batch_order.sl_points_inputs[i].value(),
                        tp_points=batch_order.tp_points_inputs[i].value(),
                        comment=f"批量下单{i+1}",
                    )
                else:
                    # 使用K线关键位止损
                    # 获取K线数据
                    countdown = self.gui_window.components["countdown"]
                    timeframe = countdown.timeframe_combo.currentText()
                    # 使用输入框中的值作为K线回溯数量
                    lookback = batch_order.sl_points_inputs[i].value()

                    rates = mt5.copy_rates_from_pos(
                        symbol, self.get_timeframe(timeframe), 0, lookback
                    )
                    if rates is None or len(rates) < lookback:
                        self.gui_window.status_bar.showMessage(
                            f"获取K线数据失败，需要至少{lookback}根K线！"
                        )
                        return

                    # 计算最低点和最高点
                    lowest_point = min([rate["low"] for rate in rates])
                    highest_point = max([rate["high"] for rate in rates])

                    if order_type == "buy":
                        sl_price = lowest_point - sl_offset
                    else:
                        sl_price = highest_point + sl_offset

                    order = self.trader.place_order_with_key_level_sl(
                        symbol=symbol,
                        order_type=order_type,
                        volume=batch_order.volume_inputs[i].value(),
                        sl_price=sl_price,
                        tp_points=batch_order.tp_points_inputs[i].value(),
                        comment=f"批量下单{i+1}",
                    )

                if order:
                    orders.append(order)

            if orders:
                # 更新默认K线回溯数量
                if sl_mode == "CANDLE_KEY_LEVEL":
                    SL_MODE["CANDLE_LOOKBACK"] = batch_order.sl_points_inputs[0].value()
                    # 保存配置
                    trading_settings.on_sl_mode_changed(
                        trading_settings.sl_mode_combo.currentIndex()
                    )

                # 增加交易次数计数
                increment_trade_count(self.gui_window.db, self.gui_window)
                self.gui_window.status_bar.showMessage(
                    f"批量{order_type}单成功！订单号：{', '.join(map(str, orders))}"
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

            # 下四个订单
            orders = []
            order_details = []  # 用于记录和显示订单详情

            for i in range(4):
                # 检查手数是否为0，跳过
                if batch_order.volume_inputs[i].value() <= 0:
                    continue

                # 根据止损模式设置止损
                sl_price = None

                if sl_mode == "FIXED_POINTS":
                    # 使用固定点数止损 - 使用原先的逻辑
                    if breakout_type == "high":
                        sl_price = (
                            entry_price
                            - batch_order.sl_points_inputs[i].value() * point
                        )
                    else:
                        sl_price = (
                            entry_price
                            + batch_order.sl_points_inputs[i].value() * point
                        )
                else:
                    # 使用K线关键位止损
                    # 获取用户设置的K线回溯数量
                    lookback = batch_order.sl_points_inputs[i].value()

                    # 获取更多K线数据
                    candle_rates = mt5.copy_rates_from_pos(
                        symbol, self.get_timeframe(timeframe), 0, lookback
                    )
                    if candle_rates is None or len(candle_rates) < lookback:
                        self.gui_window.status_bar.showMessage(
                            f"获取K线数据失败，需要至少{lookback}根K线！"
                        )
                        return

                    # 计算最低点和最高点
                    lowest_point = min([rate["low"] for rate in candle_rates])
                    highest_point = max([rate["high"] for rate in candle_rates])

                    if breakout_type == "high":
                        sl_price = lowest_point - sl_offset * point
                    else:
                        sl_price = highest_point + sl_offset * point

                # 下单
                order = self.trader.place_pending_order(
                    symbol=symbol,
                    order_type=order_type,
                    volume=batch_order.volume_inputs[i].value(),
                    price=entry_price,
                    sl_price=sl_price,
                    tp_points=batch_order.tp_points_inputs[i].value(),  # 止盈仍使用点数
                    comment=f"{comment_prefix}{i+1}",
                )

                if order:
                    orders.append(order)
                    # 记录订单详情
                    order_details.append(
                        f"订单{i+1}: K线数={batch_order.sl_points_inputs[i].value()}, 止损价={sl_price:.5f}"
                    )

            if orders:
                # 更新默认K线回溯数量
                if sl_mode == "CANDLE_KEY_LEVEL":
                    SL_MODE["CANDLE_LOOKBACK"] = batch_order.sl_points_inputs[0].value()
                    # 保存配置
                    trading_settings.on_sl_mode_changed(
                        trading_settings.sl_mode_combo.currentIndex()
                    )

                # 增加交易次数计数
                increment_trade_count(self.gui_window.db, self.gui_window)

                # 显示更详细的成功信息，包括每个订单的止损价格
                success_message = (
                    f"{comment_prefix}成功！订单号：{', '.join(map(str, orders))}"
                )
                if sl_mode == "CANDLE_KEY_LEVEL":
                    # 添加各订单的止损详情
                    details_str = " | ".join(order_details)
                    success_message += f"\n止损详情: {details_str}"

                self.gui_window.status_bar.showMessage(success_message)

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
            else:
                self.gui_window.status_bar.showMessage(
                    f"部分订单平仓失败！成功：{success_count}/{len(positions)}"
                )
        except Exception as e:
            self.gui_window.status_bar.showMessage(f"一键平仓出错：{str(e)}")

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
