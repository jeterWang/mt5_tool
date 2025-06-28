"""
持仓信息表格模块

显示当前持仓信息并提供平仓操作
"""

import MetaTrader5 as mt5
from PyQt6.QtWidgets import (
    QGroupBox,
    QVBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QPushButton,
)


class PositionsTableSection:
    """持仓信息表格区域"""

    def __init__(self):
        """初始化持仓信息表格区域"""
        self.group_box = QGroupBox("持仓信息")
        self.layout = QVBoxLayout()
        self.group_box.setLayout(self.layout)
        self.init_ui()

    def init_ui(self):
        """初始化UI"""
        self.positions_table = QTableWidget()
        self.positions_table.setColumnCount(7)  # 包含平仓按钮列
        self.positions_table.setHorizontalHeaderLabels(
            ["订单号", "交易品种", "类型", "交易量", "开仓价", "当前盈亏", "操作"]
        )
        self.positions_table.horizontalHeader().setStretchLastSection(True)

        self.layout.addWidget(self.positions_table)

    def update_positions(self, trader, gui_window):
        """
        更新持仓信息（合并持仓和挂单）
        """
        try:
            positions = trader.get_all_positions() or []
            for p in positions:
                p["status"] = "持仓"
            pendings = (
                trader.get_all_pending_orders()
                if hasattr(trader, "get_all_pending_orders")
                else []
            )
            all_orders = positions + pendings
            self.positions_table.setRowCount(len(all_orders))
            for i, order in enumerate(all_orders):
                self.positions_table.setItem(
                    i, 0, QTableWidgetItem(str(order.get("ticket", "-")))
                )
                self.positions_table.setItem(
                    i, 1, QTableWidgetItem(order.get("symbol", "-"))
                )
                # 类型字段：持仓-买入/卖出，挂单-买入/卖出
                if order.get("status") == "挂单":
                    order_type = order.get("type", "-")
                    if order_type in [mt5.ORDER_TYPE_BUY, mt5.ORDER_TYPE_BUY_STOP]:
                        type_str = "挂单-买入"
                    elif order_type in [mt5.ORDER_TYPE_SELL, mt5.ORDER_TYPE_SELL_STOP]:
                        type_str = "挂单-卖出"
                    else:
                        type_str = "挂单"
                else:
                    order_type = order.get("type", "-")
                    if order_type == mt5.POSITION_TYPE_BUY:
                        type_str = "持仓-买入"
                    elif order_type == mt5.POSITION_TYPE_SELL:
                        type_str = "持仓-卖出"
                    else:
                        type_str = "持仓"
                self.positions_table.setItem(i, 2, QTableWidgetItem(type_str))
                self.positions_table.setItem(
                    i, 3, QTableWidgetItem(str(order.get("volume", "-")))
                )
                self.positions_table.setItem(
                    i, 4, QTableWidgetItem(str(order.get("price_open", "-")))
                )
                self.positions_table.setItem(
                    i, 5, QTableWidgetItem(str(order.get("profit", "-")))
                )
                # 操作按钮
                if order.get("status") == "挂单":
                    cancel_btn = QPushButton("撤单")
                    cancel_btn.clicked.connect(
                        lambda checked, ticket=order.get("ticket"): self.cancel_order(
                            ticket, trader, gui_window
                        )
                    )
                    self.positions_table.setCellWidget(i, 6, cancel_btn)
                else:
                    close_btn = QPushButton("平仓")
                    close_btn.clicked.connect(
                        lambda checked, ticket=order.get("ticket"): self.close_position(
                            ticket, trader, gui_window
                        )
                    )
                    self.positions_table.setCellWidget(i, 6, close_btn)
        except Exception as e:
            pass
            # print(f"更新持仓信息出错：{str(e)}")

    def close_position(self, ticket, trader, gui_window):
        """
        平仓指定订单

        Args:
            ticket: 订单号
            trader: 交易者对象
            gui_window: 主窗口对象，用于获取状态栏
        """
        try:
            if trader.close_position(ticket):
                gui_window.status_bar.showMessage(f"订单 {ticket} 平仓成功！")
                try:
                    trader.sync_closed_trades_to_db()
                    gui_window.status_bar.showMessage("交易历史已同步", 2000)
                except Exception as e:
                    gui_window.status_bar.showMessage(f"数据库同步失败: {str(e)}")
            else:
                gui_window.status_bar.showMessage(f"订单 {ticket} 平仓失败！")
        except Exception as e:
            gui_window.status_bar.showMessage(f"平仓出错：{str(e)}")

    def cancel_order(self, ticket, trader, gui_window):
        """
        撤销指定挂单
        """
        try:
            if trader.cancel_order(ticket):
                gui_window.status_bar.showMessage(f"挂单 {ticket} 撤销成功！")
                try:
                    trader.sync_closed_trades_to_db()
                    gui_window.status_bar.showMessage("交易历史已同步", 2000)
                except Exception as e:
                    gui_window.status_bar.showMessage(f"数据库同步失败: {str(e)}")
            else:
                gui_window.status_bar.showMessage(f"挂单 {ticket} 撤销失败！")
        except Exception as e:
            gui_window.status_bar.showMessage(f"撤销挂单出错：{str(e)}")
