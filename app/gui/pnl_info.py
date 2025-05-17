"""
盈亏信息显示模块

显示已实现盈亏、浮动盈亏和总盈亏
"""

import os
import pandas as pd
from PyQt6.QtWidgets import QHBoxLayout, QLabel

from utils.paths import get_data_path
from config.loader import DAILY_LOSS_LIMIT


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
        实时刷新盈亏信息

        Args:
            trader: 交易者对象
        """
        try:
            today = trader.get_trading_day()
            realized = 0
            data_dir = get_data_path()
            file_path = os.path.join(data_dir, "trade_records.xlsx")
            account_id = trader._get_account_id() if trader else "unknown"

            if os.path.exists(file_path):
                try:
                    df = pd.read_excel(file_path, sheet_name=str(account_id))
                    # 优先使用trading_day字段，如果没有再使用close_time
                    if "trading_day" in df.columns and "profit" in df.columns:
                        df_today = df[df["trading_day"] == today]
                        realized = df_today["profit"].sum()
                    elif "close_time" in df.columns and "profit" in df.columns:
                        # 兼容旧数据格式
                        df_today = df[
                            df["close_time"].astype(str).str.startswith(today)
                        ]
                        realized = df_today["profit"].sum()
                except Exception as e:
                    print(f"读取已实现盈亏数据出错: {str(e)}")
                    pass

            unrealized = 0
            if trader and trader.is_connected():
                positions = trader.get_all_positions()
                if positions:
                    unrealized = sum([p["profit"] for p in positions])

            total = realized + unrealized
            self.realized_label.setText(f"今日已实现盈亏: {realized:.2f}")
            self.unrealized_label.setText(f"当前浮动盈亏: {unrealized:.2f}")
            self.total_pnl_label.setText(f"日内总盈亏: {total:.2f}")

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

        except Exception as e:
            self.realized_label.setText("今日已实现盈亏: --")
            self.unrealized_label.setText("当前浮动盈亏: --")
            self.total_pnl_label.setText("日内总盈亏: --")
