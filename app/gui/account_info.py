"""
账户信息显示模块

显示账户余额、净值、保证金以及交易次数等信息
"""

from PyQt6.QtWidgets import QHBoxLayout, QLabel
from app.config.config_manager import config_manager
import os


class AccountInfoSection:
    """账户信息区域"""

    def __init__(self):
        """初始化账户信息区域"""
        self.layout = QHBoxLayout()
        self.init_ui()

    def init_ui(self):
        """初始化UI"""
        self.balance_label = QLabel("余额: 0.00")
        self.equity_label = QLabel("净值: 0.00")
        self.margin_label = QLabel("保证金: 0.00")
        self.free_margin_label = QLabel("可用保证金: 0.00")
        self.margin_level_label = QLabel("保证金水平: 0%")
        self.trade_count_label = QLabel(
            f"今日剩余交易次数: {config_manager.get('DAILY_TRADE_LIMIT')}"
        )
        self.trade_count_label.setStyleSheet(
            "QLabel { color: blue; font-weight: bold; }"
        )

        self.layout.addWidget(self.balance_label)
        self.layout.addWidget(self.equity_label)
        self.layout.addWidget(self.margin_label)
        self.layout.addWidget(self.free_margin_label)
        self.layout.addWidget(self.margin_level_label)
        self.layout.addWidget(self.trade_count_label)

    def update_account_info(self, trader):
        """
        更新账户信息

        Args:
            trader: 交易者对象
        """
        if not trader or not trader.is_connected():
            return

        account_info = trader.get_account_info()
        if account_info:
            self.balance_label.setText(f"余额: {account_info['balance']:.2f}")
            self.equity_label.setText(f"净值: {account_info['equity']:.2f}")
            self.margin_label.setText(f"保证金: {account_info['margin']:.2f}")
            self.free_margin_label.setText(
                f"可用保证金: {account_info['free_margin']:.2f}"
            )
            self.margin_level_label.setText(
                f"保证金水平: {account_info['margin_level']:.2f}%"
            )

    def update_trade_count_display(self, db):
        """
        更新交易次数显示

        Args:
            db: 数据库对象
        """
        # 获取今日实际交易次数
        count = db.get_today_count()
        # 计算剩余交易次数
        daily_limit = config_manager.get("DAILY_TRADE_LIMIT")
        remaining = max(0, daily_limit - count)
        # 更新UI显示，同时显示总限制和已用次数
        self.trade_count_label.setText(
            f"今日剩余交易次数: {remaining} ({count}/{daily_limit})"
        )
        if remaining == 0:
            self.trade_count_label.setStyleSheet(
                "QLabel { color: red; font-weight: bold; }"
            )
        else:
            self.trade_count_label.setStyleSheet(
                "QLabel { color: blue; font-weight: bold; }"
            )
