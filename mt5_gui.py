import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                           QComboBox, QSpinBox, QDoubleSpinBox, QTableWidget, 
                           QTableWidgetItem, QMessageBox, QGroupBox, QStatusBar,
                           QCheckBox)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QIcon
import winsound  # 用于Windows系统的蜂鸣器
from mt5_trader import MT5Trader
import os
from dotenv import load_dotenv
import importlib.util
import pandas as pd

def resource_path(filename):
    if getattr(sys, 'frozen', False):
        return os.path.join(os.path.dirname(sys.executable), filename)
    else:
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)

def load_external_config():
    # 兼容pyinstaller打包后路径，优先加载exe同目录下的config.py
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(base_path, "config.py")
    if os.path.exists(config_path):
        spec = importlib.util.spec_from_file_location("config", config_path)
        config = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(config)
        sys.modules["config"] = config  # 覆盖全局config模块
        return config
    else:
        import config  # fallback
        return config

config = load_external_config()

from database import TradeDatabase
import MetaTrader5 as mt5
from datetime import datetime

class MT5GUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.trader = None
        # 初始化数据库
        self.db = TradeDatabase()
        self.init_ui()
        self.setup_timer()
        # 添加状态栏
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        # 自动连接
        self.connect_mt5()
        # 用于控制提示音间隔
        self.last_beep_time = 0
        
        # 设置窗口图标（修正）
        self.setWindowIcon(QIcon(resource_path("icon.svg")))
        
        # 初始化交易次数显示
        self.update_trade_count_display()
        
    def init_ui(self):
        """初始化UI界面"""
        self.setWindowTitle('MT5一键交易系统')
        self.setGeometry(100, 100, 1000, 800)

        # 创建主窗口部件
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        # 添加账户信息和交易次数显示
        account_info_layout = QHBoxLayout()
        self.balance_label = QLabel("余额: 0.00")
        self.equity_label = QLabel("净值: 0.00")
        self.margin_label = QLabel("保证金: 0.00")
        self.free_margin_label = QLabel("可用保证金: 0.00")
        self.margin_level_label = QLabel("保证金水平: 0%")
        self.trade_count_label = QLabel(f"今日剩余交易次数: {config.DAILY_TRADE_LIMIT}")
        self.trade_count_label.setStyleSheet("QLabel { color: blue; font-weight: bold; }")
        account_info_layout.addWidget(self.balance_label)
        account_info_layout.addWidget(self.equity_label)
        account_info_layout.addWidget(self.margin_label)
        account_info_layout.addWidget(self.free_margin_label)
        account_info_layout.addWidget(self.margin_level_label)
        account_info_layout.addWidget(self.trade_count_label)
        layout.addLayout(account_info_layout)

        # 新增盈亏信息行
        pnl_info_layout = QHBoxLayout()
        self.realized_label = QLabel("今日已实现盈亏: 0.00")
        self.unrealized_label = QLabel("当前浮动盈亏: 0.00")
        self.total_pnl_label = QLabel("日内总盈亏: 0.00")
        pnl_info_layout.addWidget(self.realized_label)
        pnl_info_layout.addWidget(self.unrealized_label)
        pnl_info_layout.addWidget(self.total_pnl_label)
        pnl_info_layout.addStretch()
        layout.addLayout(pnl_info_layout)

        # 添加倒计时显示
        countdown_layout = QHBoxLayout()
        
        # 添加K线周期选择
        self.timeframe_combo = QComboBox()
        self.timeframe_combo.addItems(["M1", "M5", "M15", "M30", "H1", "H4"])
        self.timeframe_combo.setCurrentText(config.DEFAULT_TIMEFRAME)
        self.timeframe_combo.currentTextChanged.connect(self.on_timeframe_changed)
        countdown_layout.addWidget(QLabel("K线周期:"))
        countdown_layout.addWidget(self.timeframe_combo)
        
        # 添加声音提醒选项
        self.sound_checkbox = QCheckBox("收盘提醒")
        self.sound_checkbox.setChecked(config.GUI_SETTINGS["SOUND_ALERT"])
        countdown_layout.addWidget(self.sound_checkbox)
        
        # 添加窗口置顶选项
        self.topmost_checkbox = QCheckBox("窗口置顶")
        self.topmost_checkbox.setChecked(config.GUI_SETTINGS["WINDOW_TOP"])
        self.topmost_checkbox.stateChanged.connect(self.toggle_topmost)
        countdown_layout.addWidget(self.topmost_checkbox)
        
        self.countdown_label = QLabel("距离K线收线还有: 00秒")
        self.countdown_label.setStyleSheet("QLabel { color: red; font-size: 14px; font-weight: bold; }")
        countdown_layout.addWidget(self.countdown_label)
        countdown_layout.addStretch()
        layout.addLayout(countdown_layout)

        # 交易设置组
        trading_group = QGroupBox("交易设置")
        trading_layout = QVBoxLayout()
        
        # 第一行：交易品种和订单类型
        row1_layout = QHBoxLayout()
        self.symbol_input = QComboBox()
        self.symbol_input.addItems(config.SYMBOLS)
        self.symbol_input.currentTextChanged.connect(self.on_symbol_changed)
        
        row1_layout.addWidget(QLabel("交易品种:"))
        row1_layout.addWidget(self.symbol_input)
        trading_layout.addLayout(row1_layout)

        # 批量下单设置组
        batch_group = QGroupBox("批量下单设置")
        batch_layout = QVBoxLayout()

        # 第一单设置
        order1_layout = QHBoxLayout()
        order1_layout.addWidget(QLabel("第一单:"))
        self.volume1 = QDoubleSpinBox()
        self.volume1.setRange(0.01, 100)
        self.volume1.setSingleStep(0.01)
        self.volume1.setValue(0.2)
        self.sl_points1 = QSpinBox()
        self.sl_points1.setRange(0, 100000)
        self.sl_points1.setValue(1500)
        self.tp_points1 = QSpinBox()
        self.tp_points1.setRange(0, 100000)
        self.tp_points1.setValue(0)
        order1_layout.addWidget(QLabel("手数:"))
        order1_layout.addWidget(self.volume1)
        order1_layout.addWidget(QLabel("止损点数:"))
        order1_layout.addWidget(self.sl_points1)
        order1_layout.addWidget(QLabel("止盈点数:"))
        order1_layout.addWidget(self.tp_points1)
        batch_layout.addLayout(order1_layout)

        # 第二单设置
        order2_layout = QHBoxLayout()
        order2_layout.addWidget(QLabel("第二单:"))
        self.volume2 = QDoubleSpinBox()
        self.volume2.setRange(0.01, 100)
        self.volume2.setSingleStep(0.01)
        self.volume2.setValue(0.2)
        self.sl_points2 = QSpinBox()
        self.sl_points2.setRange(0, 100000)
        self.sl_points2.setValue(1500)
        self.tp_points2 = QSpinBox()
        self.tp_points2.setRange(0, 100000)
        self.tp_points2.setValue(0)
        order2_layout.addWidget(QLabel("手数:"))
        order2_layout.addWidget(self.volume2)
        order2_layout.addWidget(QLabel("止损点数:"))
        order2_layout.addWidget(self.sl_points2)
        order2_layout.addWidget(QLabel("止盈点数:"))
        order2_layout.addWidget(self.tp_points2)
        batch_layout.addLayout(order2_layout)

        # 第三单设置
        order3_layout = QHBoxLayout()
        order3_layout.addWidget(QLabel("第三单:"))
        self.volume3 = QDoubleSpinBox()
        self.volume3.setRange(0.01, 100)
        self.volume3.setSingleStep(0.01)
        self.volume3.setValue(0.2)
        self.sl_points3 = QSpinBox()
        self.sl_points3.setRange(0, 100000)
        self.sl_points3.setValue(1500)
        self.tp_points3 = QSpinBox()
        self.tp_points3.setRange(0, 100000)
        self.tp_points3.setValue(0)
        order3_layout.addWidget(QLabel("手数:"))
        order3_layout.addWidget(self.volume3)
        order3_layout.addWidget(QLabel("止损点数:"))
        order3_layout.addWidget(self.sl_points3)
        order3_layout.addWidget(QLabel("止盈点数:"))
        order3_layout.addWidget(self.tp_points3)
        batch_layout.addLayout(order3_layout)

        # 第四单设置
        order4_layout = QHBoxLayout()
        order4_layout.addWidget(QLabel("第四单:"))
        self.volume4 = QDoubleSpinBox()
        self.volume4.setRange(0.01, 100)
        self.volume4.setSingleStep(0.01)
        self.volume4.setValue(0.2)
        self.sl_points4 = QSpinBox()
        self.sl_points4.setRange(0, 100000)
        self.sl_points4.setValue(1500)
        self.tp_points4 = QSpinBox()
        self.tp_points4.setRange(0, 100000)
        self.tp_points4.setValue(0)
        order4_layout.addWidget(QLabel("手数:"))
        order4_layout.addWidget(self.volume4)
        order4_layout.addWidget(QLabel("止损点数:"))
        order4_layout.addWidget(self.sl_points4)
        order4_layout.addWidget(QLabel("止盈点数:"))
        order4_layout.addWidget(self.tp_points4)
        batch_layout.addLayout(order4_layout)

        batch_group.setLayout(batch_layout)
        trading_layout.addWidget(batch_group)
        
        # 交易按钮
        trading_buttons = QHBoxLayout()
        self.place_batch_buy_btn = QPushButton("批量买入")
        self.place_batch_buy_btn.clicked.connect(lambda: self.place_batch_orders("buy"))
        self.place_batch_buy_btn.setEnabled(False)
        self.place_batch_buy_btn.setStyleSheet("""
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
        """)
        
        self.place_batch_sell_btn = QPushButton("批量卖出")
        self.place_batch_sell_btn.clicked.connect(lambda: self.place_batch_orders("sell"))
        self.place_batch_sell_btn.setEnabled(False)
        self.place_batch_sell_btn.setStyleSheet("""
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
        """)
        
        self.place_breakout_high_btn = QPushButton("挂高点突破")
        self.place_breakout_high_btn.clicked.connect(lambda: self.place_breakout_order("high"))
        self.place_breakout_high_btn.setEnabled(False)
        self.place_breakout_high_btn.setStyleSheet("""
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
        """)
        
        self.place_breakout_low_btn = QPushButton("挂低点突破")
        self.place_breakout_low_btn.clicked.connect(lambda: self.place_breakout_order("low"))
        self.place_breakout_low_btn.setEnabled(False)
        self.place_breakout_low_btn.setStyleSheet("""
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
        """)
        
        self.cancel_all_pending_btn = QPushButton("撤销挂单")
        self.cancel_all_pending_btn.clicked.connect(self.cancel_all_pending_orders)
        self.cancel_all_pending_btn.setEnabled(False)
        self.cancel_all_pending_btn.setStyleSheet("""
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
        """)
        
        self.close_all_btn = QPushButton("一键平仓")
        self.close_all_btn.clicked.connect(self.close_all_positions)
        self.close_all_btn.setEnabled(False)
        self.close_all_btn.setStyleSheet("""
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
        """)
        
        trading_buttons.addWidget(self.place_batch_buy_btn)
        trading_buttons.addWidget(self.place_batch_sell_btn)
        trading_buttons.addWidget(self.place_breakout_high_btn)
        trading_buttons.addWidget(self.place_breakout_low_btn)
        trading_buttons.addWidget(self.cancel_all_pending_btn)
        trading_buttons.addWidget(self.close_all_btn)
        trading_layout.addLayout(trading_buttons)
        
        trading_group.setLayout(trading_layout)
        layout.addWidget(trading_group)

        # 持仓信息表格
        positions_group = QGroupBox("持仓信息")
        positions_layout = QVBoxLayout()
        
        self.positions_table = QTableWidget()
        self.positions_table.setColumnCount(7)  # 添加平仓按钮列
        self.positions_table.setHorizontalHeaderLabels(["订单号", "交易品种", "类型", "交易量", "开仓价", "当前盈亏", "操作"])
        self.positions_table.horizontalHeader().setStretchLastSection(True)
        
        positions_layout.addWidget(self.positions_table)
        positions_group.setLayout(positions_layout)
        layout.addWidget(positions_group)

        # 初始化第一个品种的参数
        self.on_symbol_changed(config.SYMBOLS[0])

    def load_config(self):
        """加载配置文件"""
        pass  # 不再需要加载账号信息

    def setup_timer(self):
        """设置定时器更新持仓信息和倒计时"""
        # 持仓更新定时器
        self.positions_timer = QTimer()
        self.positions_timer.timeout.connect(self.update_positions)
        self.positions_timer.start(1000)  # 每秒更新一次
        
        # 倒计时更新定时器
        self.countdown_timer = QTimer()
        self.countdown_timer.timeout.connect(self.update_countdown)
        self.countdown_timer.start(1000)  # 每秒更新一次

        # 添加账户信息更新定时器
        self.account_timer = QTimer()
        self.account_timer.timeout.connect(self.update_account_info)
        self.account_timer.start(5000)  # 每5秒更新一次账户信息

        # 每分钟自动同步所有平仓单到excel
        self.closed_trade_timer = QTimer()
        self.closed_trade_timer.timeout.connect(self.sync_closed_trades)
        # self.closed_trade_timer.start(60 * 1000)  # 每分钟执行一次
        self.closed_trade_timer.start(5 * 1000)  # 每5s执行一次

        # 新增盈亏信息定时器
        self.pnl_timer = QTimer()
        self.pnl_timer.timeout.connect(self.update_daily_pnl_info)
        self.pnl_timer.start(2000)  # 每2秒刷新一次

    def connect_mt5(self):
        """连接MT5"""
        try:
            if self.trader is None:
                # 检查是否已经登录
                if not mt5.initialize():
                    self.status_bar.showMessage("MT5初始化失败！")
                    return
                    
                # 获取当前登录的账号信息
                account_info = mt5.account_info()
                if account_info is None:
                    self.status_bar.showMessage("未检测到MT5登录账号，请先在MT5中登录！")
                    return
                    
                self.trader = MT5Trader()
                self.trader.connected = True
                self.status_bar.showMessage(f"MT5连接成功！当前账号：{account_info.login}")
                self.update_account_info()  # 更新账户信息
                
                # 启用按钮
                self.place_batch_buy_btn.setEnabled(True)
                self.place_batch_sell_btn.setEnabled(True)
                self.place_breakout_high_btn.setEnabled(True)
                self.place_breakout_low_btn.setEnabled(True)
                self.cancel_all_pending_btn.setEnabled(True)
                self.close_all_btn.setEnabled(True)
            else:
                self.status_bar.showMessage("MT5已经连接！")
        except Exception as e:
            self.status_bar.showMessage(f"连接MT5出错：{str(e)}")

    def update_trade_count_display(self):
        """更新交易次数显示"""
        count = self.db.get_today_count()
        remaining = max(0, config.DAILY_TRADE_LIMIT - count)
        self.trade_count_label.setText(f"今日剩余交易次数: {remaining}")
        if remaining == 0:
            self.trade_count_label.setStyleSheet("QLabel { color: red; font-weight: bold; }")
        else:
            self.trade_count_label.setStyleSheet("QLabel { color: blue; font-weight: bold; }")
            
    def check_trade_limit(self) -> bool:
        """检查是否超过每日交易限制"""
        count = self.db.get_today_count()
        if count >= config.DAILY_TRADE_LIMIT:
            self.status_bar.showMessage("已达到每日交易次数限制！")
            return False
        return True
        
    def increment_trade_count(self):
        """增加交易次数计数"""
        if self.db.increment_count():
            self.update_trade_count_display()

    def place_batch_orders(self, order_type: str):
        """批量下单，增加风控检查"""
        try:
            # 检查风控
            if not self.check_daily_loss_limit():
                return
            # 检查交易次数限制
            if not self.check_trade_limit():
                return
            # 检查MT5连接状态
            if not self.trader or not self.trader.is_connected():
                self.status_bar.showMessage("MT5未连接，请检查连接状态！")
                return
            # 检查MT5自动交易是否启用
            if not mt5.terminal_info().trade_allowed:
                self.status_bar.showMessage("请在MT5平台中启用自动交易！")
                return
            # 检查账户状态
            account_info = mt5.account_info()
            if account_info is None:
                self.status_bar.showMessage("无法获取账户信息！")
                return
            # 检查可用保证金
            if account_info.margin_free <= 0:
                self.status_bar.showMessage("可用保证金不足！")
                return
            symbol = self.symbol_input.currentText()
            # 显示正在下单的提示
            self.status_bar.showMessage(f"正在执行批量{order_type}单...")
            
            # 下第一单
            order1 = self.trader.place_order_with_tp_sl(
                symbol=symbol,
                order_type=order_type,
                volume=self.volume1.value(),
                sl_points=self.sl_points1.value(),
                tp_points=self.tp_points1.value(),
                comment="批量下单1"
            )
            
            if not order1:
                self.status_bar.showMessage("第一单下单失败！")
                return
            
            # 下第二单
            order2 = self.trader.place_order_with_tp_sl(
                symbol=symbol,
                order_type=order_type,
                volume=self.volume2.value(),
                sl_points=self.sl_points2.value(),
                tp_points=self.tp_points2.value(),
                comment="批量下单2"
            )
            
            if not order2:
                self.status_bar.showMessage("第二单下单失败！")
                return

            # 下第三单
            order3 = self.trader.place_order_with_tp_sl(
                symbol=symbol,
                order_type=order_type,
                volume=self.volume3.value(),
                sl_points=self.sl_points3.value(),
                tp_points=self.tp_points3.value(),
                comment="批量下单3"
            )
            
            if not order3:
                self.status_bar.showMessage("第三单下单失败！")
                return

            # 下第四单
            order4 = self.trader.place_order_with_tp_sl(
                symbol=symbol,
                order_type=order_type,
                volume=self.volume4.value(),
                sl_points=self.sl_points4.value(),
                tp_points=self.tp_points4.value(),
                comment="批量下单4"
            )
            
            if order1 and order2 and order3 and order4:
                # 增加交易次数计数
                self.increment_trade_count()
                self.status_bar.showMessage(f"批量{order_type}单成功！订单号：{order1}, {order2}, {order3}, {order4}")
                # 播放提示音
                winsound.Beep(1000, 200)
            else:
                self.status_bar.showMessage(f"批量{order_type}单失败！")
        except Exception as e:
            self.status_bar.showMessage(f"批量下单出错：{str(e)}")
            print(f"下单错误详情：{str(e)}")

    def place_breakout_order(self, breakout_type: str):
        """挂突破单"""
        try:
            # 检查交易次数限制
            if not self.check_trade_limit():
                return
                
            # 检查MT5连接状态
            if not self.trader or not self.trader.is_connected():
                self.status_bar.showMessage("MT5未连接，请检查连接状态！")
                return
                
            # 检查MT5自动交易是否启用
            if not mt5.terminal_info().trade_allowed:
                self.status_bar.showMessage("请在MT5平台中启用自动交易！")
                return
                
            symbol = self.symbol_input.currentText()
            timeframe = self.timeframe_combo.currentText()
            
            # 获取当前K线的高低点
            rates = mt5.copy_rates_from_pos(symbol, self.get_timeframe(timeframe), 0, 1)
            if rates is None or len(rates) < 1:
                self.status_bar.showMessage("获取K线数据失败！")
                return
                
            current_high = rates[0]['high']
            current_low = rates[0]['low']
            
            # 根据突破类型设置价格和订单类型
            if breakout_type == "high":
                price = current_high
                order_type = "buy"
                comment_prefix = f"{timeframe}高点突破买入"
            else:
                price = current_low
                order_type = "sell"
                comment_prefix = f"{timeframe}低点突破卖出"
            
            # 下第一单
            order1 = self.trader.place_order_with_tp_sl(
                symbol=symbol,
                order_type=order_type,
                volume=self.volume1.value(),
                sl_points=self.sl_points1.value(),
                tp_points=self.tp_points1.value(),
                price=price,
                comment=f"{comment_prefix}1"
            )
            
            # 下第二单
            order2 = self.trader.place_order_with_tp_sl(
                symbol=symbol,
                order_type=order_type,
                volume=self.volume2.value(),
                sl_points=self.sl_points2.value(),
                tp_points=self.tp_points2.value(),
                price=price,
                comment=f"{comment_prefix}2"
            )
            
            # 下第三单
            order3 = self.trader.place_order_with_tp_sl(
                symbol=symbol,
                order_type=order_type,
                volume=self.volume3.value(),
                sl_points=self.sl_points3.value(),
                tp_points=self.tp_points3.value(),
                price=price,
                comment=f"{comment_prefix}3"
            )
            
            # 下第四单
            order4 = self.trader.place_order_with_tp_sl(
                symbol=symbol,
                order_type=order_type,
                volume=self.volume4.value(),
                sl_points=self.sl_points4.value(),
                tp_points=self.tp_points4.value(),
                price=price,
                comment=f"{comment_prefix}4"
            )
            
            if order1 and order2 and order3 and order4:
                # 增加交易次数计数
                self.increment_trade_count()
                self.status_bar.showMessage(f"{comment_prefix}成功！订单号：{order1}, {order2}, {order3}, {order4}，价格：{price}")
                # 播放提示音
                winsound.Beep(1000, 200)
            else:
                self.status_bar.showMessage(f"{comment_prefix}失败！")
        except Exception as e:
            self.status_bar.showMessage(f"挂突破单出错：{str(e)}")
            print(f"下单错误详情：{str(e)}")

    def get_timeframe(self, timeframe: str) -> int:
        """将时间周期字符串转换为MT5的时间周期常量"""
        timeframe_map = {
            "M1": mt5.TIMEFRAME_M1,
            "M5": mt5.TIMEFRAME_M5,
            "M15": mt5.TIMEFRAME_M15,
            "M30": mt5.TIMEFRAME_M30,
            "H1": mt5.TIMEFRAME_H1,
            "H4": mt5.TIMEFRAME_H4
        }
        return timeframe_map.get(timeframe, mt5.TIMEFRAME_M1)

    def close_position(self, ticket: int):
        """平仓指定订单"""
        try:
            if self.trader.close_position(ticket):
                self.status_bar.showMessage(f"订单 {ticket} 平仓成功！")
            else:
                self.status_bar.showMessage(f"订单 {ticket} 平仓失败！")
        except Exception as e:
            self.status_bar.showMessage(f"平仓出错：{str(e)}")

    def close_all_positions(self):
        """一键平仓所有订单"""
        try:
            positions = self.trader.get_all_positions()
            if not positions:
                self.status_bar.showMessage("当前没有持仓！")
                return

            success_count = 0
            for position in positions:
                if self.trader.close_position(position['ticket']):
                    success_count += 1

            if success_count == len(positions):
                self.status_bar.showMessage("所有订单平仓成功！")
            else:
                self.status_bar.showMessage(f"部分订单平仓失败！成功：{success_count}/{len(positions)}")
        except Exception as e:
            self.status_bar.showMessage(f"一键平仓出错：{str(e)}")

    def update_positions(self):
        """更新持仓信息，并检查风控"""
        if not self.trader or not self.trader.connected:
            return
        # 风控检查
        if not self.check_daily_loss_limit():
            return
        try:
            positions = self.trader.get_all_positions()
            if positions is None:
                return
            self.positions_table.setRowCount(len(positions))
            for i, position in enumerate(positions):
                self.positions_table.setItem(i, 0, QTableWidgetItem(str(position['ticket'])))
                self.positions_table.setItem(i, 1, QTableWidgetItem(position['symbol']))
                self.positions_table.setItem(i, 2, QTableWidgetItem("买入" if position['type'] == mt5.POSITION_TYPE_BUY else "卖出"))
                self.positions_table.setItem(i, 3, QTableWidgetItem(str(position['volume'])))
                self.positions_table.setItem(i, 4, QTableWidgetItem(str(position['price_open'])))
                self.positions_table.setItem(i, 5, QTableWidgetItem(str(position['profit'])))
                # 添加平仓按钮
                close_btn = QPushButton("平仓")
                close_btn.clicked.connect(lambda checked, ticket=position['ticket']: self.close_position(ticket))
                self.positions_table.setCellWidget(i, 6, close_btn)
        except Exception as e:
            print(f"更新持仓信息出错：{str(e)}")

    def update_countdown(self):
        """更新倒计时显示"""
        try:
            current_time = datetime.now()
            timeframe = self.timeframe_combo.currentText()
            
            if timeframe == "M1":
                seconds_left = 60 - current_time.second
            elif timeframe == "M5":
                minutes_passed = current_time.minute % 5
                seconds_left = (4 - minutes_passed) * 60 + (60 - current_time.second)
            elif timeframe == "M15":
                minutes_passed = current_time.minute % 15
                seconds_left = (14 - minutes_passed) * 60 + (60 - current_time.second)
            elif timeframe == "M30":
                minutes_passed = current_time.minute % 30
                seconds_left = (29 - minutes_passed) * 60 + (60 - current_time.second)
            elif timeframe == "H1":
                minutes_passed = current_time.minute
                seconds_left = (59 - minutes_passed) * 60 + (60 - current_time.second)
            else:  # H4
                hours_passed = current_time.hour % 4
                minutes_passed = current_time.minute
                seconds_left = ((3 - hours_passed) * 60 + (59 - minutes_passed)) * 60 + (60 - current_time.second)
            
            # 转换为分钟和秒的显示
            minutes = seconds_left // 60
            seconds = seconds_left % 60
            
            if minutes > 0:
                self.countdown_label.setText(f"距离{timeframe}收线还有: {minutes}分{seconds:02d}秒")
            else:
                self.countdown_label.setText(f"距离{timeframe}收线还有: {seconds:02d}秒")
            
            # 当剩余30秒时改变颜色
            if seconds_left <= 30:
                self.countdown_label.setStyleSheet("QLabel { color: red; font-size: 14px; font-weight: bold; }")
            else:
                self.countdown_label.setStyleSheet("QLabel { color: black; font-size: 14px; font-weight: bold; }")

            # 声音提醒
            if self.sound_checkbox.isChecked() and seconds_left <= config.GUI_SETTINGS["ALERT_SECONDS"]:
                current_timestamp = current_time.timestamp()
                # 确保提示音间隔至少1秒
                if current_timestamp - self.last_beep_time >= 1:
                    winsound.Beep(config.GUI_SETTINGS["BEEP_FREQUENCY"], 
                                config.GUI_SETTINGS["BEEP_DURATION"])
                    self.last_beep_time = current_timestamp

        except Exception as e:
            print(f"更新倒计时出错：{str(e)}")

    def on_timeframe_changed(self, timeframe: str):
        """当K线周期改变时重置倒计时"""
        self.update_countdown()

    def closeEvent(self, event):
        """关闭窗口时断开MT5连接"""
        if self.trader:
            self.trader.disconnect()
        event.accept()

    def on_symbol_changed(self, symbol: str):
        """当交易品种改变时调整参数"""
        # 设置交易品种的限制
        symbol_params = config.DEFAULT_PARAMS[symbol]
        
        # 设置手数范围
        for volume_input in [self.volume1, self.volume2, self.volume3, self.volume4]:
            volume_input.setRange(symbol_params["min_volume"], symbol_params["max_volume"])
            volume_input.setSingleStep(symbol_params["volume_step"])
        
        # 设置止损止盈范围
        for sl_input in [self.sl_points1, self.sl_points2, self.sl_points3, self.sl_points4]:
            sl_input.setRange(symbol_params["min_sl_points"], symbol_params["max_sl_points"])
            
        for tp_input in [self.tp_points1, self.tp_points2, self.tp_points3, self.tp_points4]:
            tp_input.setRange(symbol_params["min_tp_points"], symbol_params["max_tp_points"])
        
        # 设置默认值
        self.volume1.setValue(config.BATCH_ORDER_DEFAULTS["order1"]["volume"])
        self.sl_points1.setValue(config.BATCH_ORDER_DEFAULTS["order1"]["sl_points"])
        self.tp_points1.setValue(config.BATCH_ORDER_DEFAULTS["order1"]["tp_points"])
        
        self.volume2.setValue(config.BATCH_ORDER_DEFAULTS["order2"]["volume"])
        self.sl_points2.setValue(config.BATCH_ORDER_DEFAULTS["order2"]["sl_points"])
        self.tp_points2.setValue(config.BATCH_ORDER_DEFAULTS["order2"]["tp_points"])
        
        self.volume3.setValue(config.BATCH_ORDER_DEFAULTS["order3"]["volume"])
        self.sl_points3.setValue(config.BATCH_ORDER_DEFAULTS["order3"]["sl_points"])
        self.tp_points3.setValue(config.BATCH_ORDER_DEFAULTS["order3"]["tp_points"])
        
        self.volume4.setValue(config.BATCH_ORDER_DEFAULTS["order4"]["volume"])
        self.sl_points4.setValue(config.BATCH_ORDER_DEFAULTS["order4"]["sl_points"])
        self.tp_points4.setValue(config.BATCH_ORDER_DEFAULTS["order4"]["tp_points"])

    def cancel_all_pending_orders(self):
        """撤销所有挂单"""
        try:
            # 获取所有挂单
            orders = mt5.orders_get()
            if orders is None:
                self.status_bar.showMessage("没有挂单！")
                return
                
            success_count = 0
            for order in orders:
                # 只撤销挂单（包括突破单）
                if order.type in [mt5.ORDER_TYPE_BUY_STOP, mt5.ORDER_TYPE_SELL_STOP]:
                    if self.trader.cancel_order(order.ticket):
                        success_count += 1
            
            if success_count > 0:
                self.status_bar.showMessage(f"成功撤销{success_count}个挂单！")
            else:
                self.status_bar.showMessage("没有需要撤销的挂单！")
        except Exception as e:
            self.status_bar.showMessage(f"撤销挂单出错：{str(e)}")

    def toggle_topmost(self, state):
        """切换窗口置顶状态"""
        if state == Qt.CheckState.Checked.value:
            self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
        else:
            self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowStaysOnTopHint)
        self.show()  # 重新显示窗口以应用新的窗口标志

    def update_account_info(self):
        """更新账户信息"""
        if self.trader and self.trader.is_connected():
            account_info = self.trader.get_account_info()
            if account_info:
                self.balance_label.setText(f"余额: {account_info['balance']:.2f}")
                self.equity_label.setText(f"净值: {account_info['equity']:.2f}")
                self.margin_label.setText(f"保证金: {account_info['margin']:.2f}")
                self.free_margin_label.setText(f"可用保证金: {account_info['free_margin']:.2f}")
                self.margin_level_label.setText(f"保证金水平: {account_info['margin_level']:.2f}%")
                
    def sync_closed_trades(self):
        if self.trader and self.trader.is_connected():
            try:
                self.trader.sync_closed_trades_to_excel()
            except Exception as e:
                print(f"同步平仓单到excel出错: {str(e)}")

    def check_daily_loss_limit(self) -> bool:
        """检查是否超过日内最大亏损，超过则自动平仓并禁止交易，返回是否允许继续交易"""
        # 1. 统计今日已实现亏损（从trade_records.xlsx或数据库/MT5历史）
        # 2. 统计当前未实现浮动盈亏（所有持仓profit）
        # 3. 合计后判断
        try:
            # 1. 统计今日已实现亏损
            today = datetime.now().strftime('%Y-%m-%d')
            realized_loss = 0
            data_dir = 'data'
            file_path = os.path.join(data_dir, 'trade_records.xlsx')
            account_id = self.trader._get_account_id() if self.trader else 'unknown'
            if os.path.exists(file_path):
                try:
                    df = pd.read_excel(file_path, sheet_name=str(account_id))
                    if 'close_time' in df.columns and 'profit' in df.columns:
                        df_today = df[df['close_time'].astype(str).str.startswith(today)]
                        realized_loss = df_today['profit'].sum()
                except Exception:
                    pass
            # 2. 统计当前未实现浮动盈亏
            unrealized = 0
            if self.trader and self.trader.connected:
                positions = self.trader.get_all_positions()
                if positions:
                    unrealized = sum([p['profit'] for p in positions])
            # 3. 合计
            total = realized_loss + unrealized
            if total <= -config.DAILY_LOSS_LIMIT:
                # 超过最大亏损，自动平仓并禁止交易
                self.close_all_positions()
                self.disable_trading_for_today()
                # 记录风控事件
                detail = f"日内亏损已达{total:.2f}，已自动平仓并禁止交易"
                self.db.record_risk_event('DAILY_LOSS_LIMIT', detail)
                self.status_bar.showMessage(detail)
                return False
            return True
        except Exception as e:
            print(f"风控检查出错：{str(e)}")
            return True

    def disable_trading_for_today(self):
        """禁止今日交易（禁用所有下单按钮）"""
        self.place_batch_buy_btn.setEnabled(False)
        self.place_batch_sell_btn.setEnabled(False)
        self.place_breakout_high_btn.setEnabled(False)
        self.place_breakout_low_btn.setEnabled(False)
        self.status_bar.showMessage("已触发日内最大亏损，今日禁止交易！")

    def update_daily_pnl_info(self):
        """实时刷新盈亏信息"""
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            realized = 0
            data_dir = 'data'
            file_path = os.path.join(data_dir, 'trade_records.xlsx')
            account_id = self.trader._get_account_id() if self.trader else 'unknown'
            if os.path.exists(file_path):
                try:
                    df = pd.read_excel(file_path, sheet_name=str(account_id))
                    if 'close_time' in df.columns and 'profit' in df.columns:
                        df_today = df[df['close_time'].astype(str).str.startswith(today)]
                        realized = df_today['profit'].sum()
                except Exception:
                    pass
            unrealized = 0
            if self.trader and self.trader.connected:
                positions = self.trader.get_all_positions()
                if positions:
                    unrealized = sum([p['profit'] for p in positions])
            total = realized + unrealized
            self.realized_label.setText(f"今日已实现盈亏: {realized:.2f}")
            self.unrealized_label.setText(f"当前浮动盈亏: {unrealized:.2f}")
            self.total_pnl_label.setText(f"日内总盈亏: {total:.2f}")
            # 风控高亮
            if total <= -config.DAILY_LOSS_LIMIT:
                self.total_pnl_label.setStyleSheet("QLabel { color: red; font-weight: bold; }")
                self.total_pnl_label.setText(f"日内总盈亏: {total:.2f}（已禁止交易）")
            else:
                self.total_pnl_label.setStyleSheet("QLabel { color: black; font-weight: bold; }")
        except Exception as e:
            self.realized_label.setText("今日已实现盈亏: --")
            self.unrealized_label.setText("当前浮动盈亏: --")
            self.total_pnl_label.setText("日内总盈亏: --")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MT5GUI()
    window.show()
    sys.exit(app.exec()) 