"""
盈亏信息显示模块

显示已实现盈亏、浮动盈亏和总盈亏
"""

import os
import pandas as pd
from PyQt6.QtWidgets import QHBoxLayout, QLabel
import sqlite3

from utils.paths import get_data_path
from config.loader import DAILY_LOSS_LIMIT
from app.database import TradeDatabase
from app.orm_models import TradeHistory
from sqlalchemy import func


class PnlInfoSection:
    """盈亏信息区域"""

    def __init__(self):
        """初始化盈亏信息区域"""
        self.layout = QHBoxLayout()
        self.init_ui()

    def init_ui(self):
        """初始化UI"""
        self.realized_label = QLabel("今日已实现盈亏: 0.00")
        self.unrealized_label = QLabel("当前浮动盈亏: 0.00")
        self.total_pnl_label = QLabel("日内总盈亏: 0.00")

        self.layout.addWidget(self.realized_label)
        self.layout.addWidget(self.unrealized_label)
        self.layout.addWidget(self.total_pnl_label)
        self.layout.addStretch()

    def update_daily_pnl_info(self, trader):
        """
        更新每日盈亏信息
        """
        try:
            # 获取当前交易日
            trading_day = trader.get_trading_day()
            # 获取账户ID
            account_id = trader._get_account_id()
            # 读取已实现盈亏（ORM查询trade_history表）
            realized_pnl = 0
            try:
                db = TradeDatabase()
                with db.Session() as session:
                    result = (
                        session.query(func.sum(TradeHistory.profit))
                        .filter(
                            TradeHistory.trading_day == trading_day,
                            TradeHistory.account == str(account_id),
                        )
                        .scalar()
                    )
                    if result is not None:
                        realized_pnl = result
            except Exception as e:
                realized_pnl = 0
            # 获取浮动盈亏
            positions = trader.get_all_positions()
            unrealized_pnl = (
                sum(position["profit"] for position in positions) if positions else 0
            )
            # 计算总盈亏
            total = realized_pnl + unrealized_pnl
            # 更新显示
            self.realized_label.setText(f"今日已实现盈亏: {realized_pnl:.2f}")
            self.unrealized_label.setText(f"当前浮动盈亏: {unrealized_pnl:.2f}")
            # 风控高亮
            if total <= -DAILY_LOSS_LIMIT:
                self.total_pnl_label.setStyleSheet(
                    "QLabel { color: red; font-weight: bold; }"
                )
                self.total_pnl_label.setText(f"日内总盈亏: {total:.2f}（已禁止交易）")
            else:
                self.total_pnl_label.setStyleSheet(
                    "QLabel { color: black; font-weight: bold; }"
                )
                self.total_pnl_label.setText(f"日内总盈亏: {total:.2f}")
        except Exception as e:
            self.realized_label.setText("今日已实现盈亏: --")
            self.unrealized_label.setText("当前浮动盈亏: --")
            self.total_pnl_label.setText("日内总盈亏: --")
