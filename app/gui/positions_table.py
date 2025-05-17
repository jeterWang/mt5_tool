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
        更新持仓信息

        Args:
            trader: 交易者对象
            gui_window: 主窗口对象，用于获取状态栏
        """
        try:
            positions = trader.get_all_positions()
            if positions is None:
                return

            self.positions_table.setRowCount(len(positions))
            for i, position in enumerate(positions):
                self.positions_table.setItem(
                    i, 0, QTableWidgetItem(str(position["ticket"]))
                )
                self.positions_table.setItem(i, 1, QTableWidgetItem(position["symbol"]))
                self.positions_table.setItem(
                    i,
                    2,
                    QTableWidgetItem(
                        "买入" if position["type"] == mt5.POSITION_TYPE_BUY else "卖出"
                    ),
                )
                self.positions_table.setItem(
                    i, 3, QTableWidgetItem(str(position["volume"]))
                )
                self.positions_table.setItem(
                    i, 4, QTableWidgetItem(str(position["price_open"]))
                )
                self.positions_table.setItem(
                    i, 5, QTableWidgetItem(str(position["profit"]))
                )

                # 添加平仓按钮
                close_btn = QPushButton("平仓")
                close_btn.clicked.connect(
                    lambda checked, ticket=position["ticket"]: self.close_position(
                        ticket, trader, gui_window
                    )
                )
                self.positions_table.setCellWidget(i, 6, close_btn)
        except Exception as e:
            print(f"更新持仓信息出错：{str(e)}")

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
            else:
                gui_window.status_bar.showMessage(f"订单 {ticket} 平仓失败！")
        except Exception as e:
            gui_window.status_bar.showMessage(f"平仓出错：{str(e)}")
