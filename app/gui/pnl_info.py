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
        更新每日盈亏信息
        """
        try:
            # 获取当前交易日
            trading_day = trader.get_trading_day()
            # 获取账户ID
            account_id = trader._get_account_id()
            # 获取Excel文件路径（改为trade_records.xlsx）
            excel_path = os.path.join(get_data_path(), "trade_records.xlsx")
            # 读取已实现盈亏
            realized_pnl = 0
            if os.path.exists(excel_path):
                try:
                    df = pd.read_excel(excel_path, sheet_name=str(account_id))
                    if not df.empty and "profit" in df.columns:
                        # 优先使用trading_day字段，如果没有再使用close_time
                        if "trading_day" in df.columns:
                            # 直接按trading_day字段过滤
                            today_df = df[df["trading_day"] == trading_day]
                            realized_pnl = today_df["profit"].sum()
                        elif "close_time" in df.columns:
                            # 兼容旧数据格式，按close_time过滤
                            df["close_time"] = pd.to_datetime(df["close_time"])
                            today_df = df[
                                df["close_time"].dt.strftime("%Y-%m-%d") == trading_day
                            ]
                            realized_pnl = today_df["profit"].sum()
                        print(f"今日({trading_day})已实现盈亏: {realized_pnl:.2f}")
                    else:
                        print("trade_records.xlsx中缺少profit字段或文件为空")
                except Exception as e:
                    print(f"读取已实现盈亏数据出错: {str(e)}")
                    realized_pnl = 0
            else:
                print(f"trade_records.xlsx文件不存在: {excel_path}")

            # 获取浮动盈亏
            positions = trader.get_all_positions()
            unrealized_pnl = (
                sum(position["profit"] for position in positions) if positions else 0
            )
            print(f"当前浮动盈亏: {unrealized_pnl:.2f}")

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
            print(f"更新盈亏信息出错: {str(e)}")
            self.realized_label.setText("今日已实现盈亏: --")
            self.unrealized_label.setText("当前浮动盈亏: --")
            self.total_pnl_label.setText("日内总盈亏: --")
