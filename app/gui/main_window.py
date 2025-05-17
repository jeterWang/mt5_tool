"""
MT5交易系统主窗口

提供MT5交易系统主窗口的框架
"""

import sys
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QStatusBar,
    QCheckBox,
    QMenuBar,
    QMenu,
    QPushButton,
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QIcon, QFont, QFontDatabase, QAction
import os

from utils.paths import get_icon_path, get_font_path
from app.trader import MT5Trader
from app.database import TradeDatabase
from config.loader import GUI_SETTINGS, SL_MODE, SYMBOLS, load_config, DAILY_TRADE_LIMIT
from app.gui.account_info import AccountInfoSection
from app.gui.pnl_info import PnlInfoSection
from app.gui.countdown import CountdownSection
from app.gui.trading_settings import TradingSettingsSection
from app.gui.batch_order import BatchOrderSection
from app.gui.trading_buttons import TradingButtonsSection
from app.gui.positions_table import PositionsTableSection
from app.gui.settings import show_settings_dialog


def load_chinese_font():
    """加载中文字体"""
    font_path = get_font_path("simhei.ttf")
    if os.path.exists(font_path):
        font_id = QFontDatabase.addApplicationFont(font_path)
        if font_id != -1:
            font_families = QFontDatabase.applicationFontFamilies(font_id)
            if font_families:
                return font_families[0]
    return ""


class MT5GUI(QMainWindow):
    """MT5交易系统GUI界面类"""

    def __init__(self):
        """初始化GUI界面"""
        super().__init__()

        # 确保在初始化前加载最新配置
        print(f"MT5GUI初始化前SYMBOLS = {SYMBOLS}")
        load_config()

        # 重要：打印交易次数限制配置
        print(f"MT5GUI初始化 - 当前DAILY_TRADE_LIMIT = {DAILY_TRADE_LIMIT}")

        print(f"MT5GUI初始化后SYMBOLS = {SYMBOLS}")

        self.trader = None

        # 初始化数据库
        self.db = TradeDatabase()

        # 设置字体
        self.setup_font()

        # 设置窗口标题和大小
        self.setWindowTitle("MT5交易系统")
        self.setGeometry(100, 100, 1000, 800)

        # 创建菜单栏
        self.create_menu_bar()

        # 创建UI组件
        self.components = {}

        # 设置UI元素
        self.init_ui()

        # 设置定时器
        self.setup_timer()

        # 添加状态栏
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # 自动连接
        self.connect_mt5()

        # 用于控制提示音间隔
        self.last_beep_time = 0

        # 设置窗口图标
        self.setWindowIcon(QIcon(get_icon_path("icon.svg")))

        # 应用初始窗口置顶状态
        if GUI_SETTINGS["WINDOW_TOP"]:
            self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
            self.show()

    def create_menu_bar(self):
        """创建菜单栏"""
        menu_bar = QMenuBar(self)
        self.setMenuBar(menu_bar)

        # 文件菜单
        file_menu = QMenu("文件(&F)", self)
        menu_bar.addMenu(file_menu)

        # 退出菜单项
        exit_action = QAction("退出(&Q)", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # 设置菜单（与文件菜单平级）
        settings_menu = QMenu("设置(&S)", self)
        menu_bar.addMenu(settings_menu)

        # 系统设置菜单项
        system_settings_action = QAction("系统设置(&S)", self)
        system_settings_action.setShortcut("Ctrl+S")
        system_settings_action.triggered.connect(self.open_settings)
        settings_menu.addAction(system_settings_action)

        # 帮助菜单
        help_menu = QMenu("帮助(&H)", self)
        menu_bar.addMenu(help_menu)

        # 关于菜单项
        about_action = QAction("关于(&A)", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def setup_font(self):
        """设置全局字体"""
        font_family = load_chinese_font()
        if font_family:
            font = QFont(font_family, 9)
            QApplication.setFont(font)
        else:
            # 备选方案，使用系统字体
            font = QFont("SimHei", 9)
            QApplication.setFont(font)

    def init_ui(self):
        """初始化UI界面"""
        # 创建主窗口部件
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)

        # 添加顶部区域（账户信息和系统设置按钮）
        top_layout = QHBoxLayout()

        # 添加账户信息和交易次数显示
        self.components["account_info"] = AccountInfoSection()
        top_layout.addLayout(self.components["account_info"].layout)

        # 添加一个伸缩空间，使系统设置按钮靠右
        top_layout.addStretch()

        # 右上角添加系统设置按钮
        settings_button = QPushButton("系统设置")
        settings_button.setFixedWidth(100)  # 设置固定宽度
        settings_button.setStyleSheet("background-color: #f0f0f0;")  # 设置背景颜色
        settings_button.clicked.connect(self.open_settings)
        top_layout.addWidget(settings_button)

        main_layout.addLayout(top_layout)

        # 添加盈亏信息行
        self.components["pnl_info"] = PnlInfoSection()
        main_layout.addLayout(self.components["pnl_info"].layout)

        # 添加K线倒计时显示
        self.components["countdown"] = CountdownSection()
        main_layout.addLayout(self.components["countdown"].layout)

        # 获取窗口置顶复选框引用
        self.topmost_checkbox = self.components["countdown"].topmost_checkbox
        self.topmost_checkbox.stateChanged.connect(self.toggle_topmost)

        # 添加交易设置组
        self.components["trading_settings"] = TradingSettingsSection()
        main_layout.addWidget(self.components["trading_settings"].group_box)

        # 连接止损模式改变信号
        self.components["trading_settings"].sl_mode_combo.currentIndexChanged.connect(
            self.on_sl_mode_changed
        )

        # 添加批量下单设置组
        self.components["batch_order"] = BatchOrderSection()
        main_layout.addWidget(self.components["batch_order"].group_box)

        # 添加交易按钮
        self.components["trading_buttons"] = TradingButtonsSection()
        main_layout.addLayout(self.components["trading_buttons"].layout)

        # 添加持仓信息表格
        self.components["positions_table"] = PositionsTableSection()
        main_layout.addWidget(self.components["positions_table"].group_box)

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
        self.closed_trade_timer.start(5000)  # 每5秒执行一次

        # 新增盈亏信息定时器
        self.pnl_timer = QTimer()
        self.pnl_timer.timeout.connect(self.update_daily_pnl_info)
        self.pnl_timer.start(2000)  # 每2秒刷新一次

    def on_sl_mode_changed(self, index):
        """
        处理止损模式变更

        Args:
            index: 止损模式索引，0为固定点数止损，1为K线关键位止损
        """
        # 更新trading_settings模块中的设置
        mode = self.components["trading_settings"].on_sl_mode_changed(index)

        # 通过模块级函数更新批量下单设置
        from app.gui.batch_order import update_sl_mode

        update_sl_mode(mode)

    def connect_mt5(self):
        """连接到MT5"""
        try:
            if self.trader is None:
                # 创建交易者对象
                self.trader = MT5Trader()

                # 尝试连接MT5
                if not self.trader.connect():
                    self.status_bar.showMessage("MT5初始化失败！")
                    return

                # 获取当前登录的账号信息
                account_info = self.trader.get_account_info()
                if account_info is None:
                    self.status_bar.showMessage(
                        "未检测到MT5登录账号，请先在MT5中登录！"
                    )
                    return

                self.status_bar.showMessage(
                    f"MT5连接成功！当前账号：{self.trader._get_account_id()}"
                )
                self.update_account_info()  # 更新账户信息

                # 动态设置DEFAULT_PARAMS，替代config中的静态定义
                self.update_default_params()

                # 更新交易品种列表
                self.update_symbols_list()

                # 启用按钮
                self.enable_trading_buttons()

                # 设置交易按钮中的trader和gui_window引用
                self.components["trading_buttons"].set_trader_and_window(
                    self.trader, self
                )
            else:
                self.status_bar.showMessage("MT5已经连接！")
        except Exception as e:
            self.status_bar.showMessage(f"连接MT5出错：{str(e)}")

    def enable_trading_buttons(self):
        """启用交易按钮"""
        trading_buttons = self.components["trading_buttons"]
        trading_buttons.place_batch_buy_btn.setEnabled(True)
        trading_buttons.place_batch_sell_btn.setEnabled(True)
        trading_buttons.place_breakout_high_btn.setEnabled(True)
        trading_buttons.place_breakout_low_btn.setEnabled(True)
        trading_buttons.cancel_all_pending_btn.setEnabled(True)
        trading_buttons.close_all_btn.setEnabled(True)

    def update_default_params(self):
        """从trader获取交易品种参数"""
        # 这个方法已经移到trader.py中处理
        pass

    def update_symbols_list(self):
        """更新交易品种列表"""
        if not self.trader or not self.trader.is_connected():
            return

        # 打印更新前的SYMBOLS
        print(f"update_symbols_list: 更新前SYMBOLS = {SYMBOLS}")

        # 重新加载配置，确保使用最新的SYMBOLS列表
        load_config()

        # 打印更新后的SYMBOLS
        print(f"update_symbols_list: 更新后SYMBOLS = {SYMBOLS}")

        trading_settings = self.components["trading_settings"]
        trading_settings.update_symbols_list(self.trader)

        # 更新完成后强制刷新UI
        self.status_bar.showMessage("交易品种列表已更新")

    def update_positions(self):
        """更新持仓信息，并检查风控"""
        if not self.trader or not self.trader.is_connected():
            return

        # 风控检查
        if not self.check_daily_loss_limit():
            return

        positions_table = self.components["positions_table"]
        positions_table.update_positions(self.trader, self)

    def update_countdown(self):
        """更新倒计时显示"""
        countdown = self.components["countdown"]
        new_beep_time = countdown.update_countdown(self.last_beep_time)
        if new_beep_time:
            self.last_beep_time = new_beep_time

    def toggle_topmost(self, state):
        """切换窗口置顶状态"""
        if state == Qt.CheckState.Checked.value:
            self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
        else:
            self.setWindowFlags(
                self.windowFlags() & ~Qt.WindowType.WindowStaysOnTopHint
            )
        self.show()  # 重新显示窗口以应用新的窗口标志

    def update_account_info(self):
        """更新账户信息"""
        if not self.trader or not self.trader.is_connected():
            return

        account_info = self.components["account_info"]
        account_info.update_account_info(self.trader)
        account_info.update_trade_count_display(self.db)

    def sync_closed_trades(self):
        """同步平仓交易到Excel"""
        if self.trader and self.trader.is_connected():
            try:
                self.trader.sync_closed_trades_to_excel()
            except Exception as e:
                print(f"同步平仓单到excel出错: {str(e)}")

    def update_daily_pnl_info(self):
        """实时刷新盈亏信息"""
        if not self.trader or not self.trader.is_connected():
            return

        pnl_info = self.components["pnl_info"]
        pnl_info.update_daily_pnl_info(self.trader)

    def check_daily_loss_limit(self) -> bool:
        """检查是否超过日内最大亏损，超过则自动平仓并禁止交易"""
        # 将在risk_control.py中实现
        from app.gui.risk_control import check_daily_loss_limit

        return check_daily_loss_limit(self.trader, self.db, self)

    def disable_trading_for_today(self):
        """禁止今日交易（禁用所有下单按钮）"""
        trading_buttons = self.components["trading_buttons"]
        trading_buttons.place_batch_buy_btn.setEnabled(False)
        trading_buttons.place_batch_sell_btn.setEnabled(False)
        trading_buttons.place_breakout_high_btn.setEnabled(False)
        trading_buttons.place_breakout_low_btn.setEnabled(False)
        self.status_bar.showMessage("已触发日内最大亏损，今日禁止交易！")

    def closeEvent(self, event):
        """关闭窗口时断开MT5连接，并保存配置"""
        # 保存配置
        from app.gui.config_manager import save_gui_config

        save_gui_config(self)

        # 断开MT5连接
        if self.trader:
            self.trader.disconnect()

        event.accept()

    def open_settings(self):
        """打开设置对话框"""
        if show_settings_dialog(self):
            # 如果设置已保存，更新UI显示
            self.update_ui_from_settings()

    def update_ui_from_settings(self):
        """从配置更新UI显示"""
        # 更新窗口置顶状态
        if GUI_SETTINGS["WINDOW_TOP"]:
            if not (self.windowFlags() & Qt.WindowType.WindowStaysOnTopHint):
                self.setWindowFlags(
                    self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint
                )
                self.show()
        else:
            if self.windowFlags() & Qt.WindowType.WindowStaysOnTopHint:
                self.setWindowFlags(
                    self.windowFlags() & ~Qt.WindowType.WindowStaysOnTopHint
                )
                self.show()

        # 更新复选框状态
        self.topmost_checkbox.setChecked(GUI_SETTINGS["WINDOW_TOP"])
        self.components["countdown"].sound_checkbox.setChecked(
            GUI_SETTINGS["SOUND_ALERT"]
        )

        # 更新交易设置
        trading_settings = self.components["trading_settings"]
        trading_settings.sl_mode_combo.setCurrentIndex(
            0 if SL_MODE["DEFAULT_MODE"] == "FIXED_POINTS" else 1
        )

        # 更新批量下单设置
        from app.gui.batch_order import update_sl_mode

        update_sl_mode(SL_MODE["DEFAULT_MODE"])

        # 重新加载交易限制设置
        self.update_trading_limits()

        # 立即更新交易次数显示
        if self.trader and self.trader.is_connected():
            account_info = self.components["account_info"]
            account_info.update_trade_count_display(self.db)
            print("已更新交易次数显示")

        # 更新状态栏提示
        self.status_bar.showMessage("配置已更新")

    def update_trading_limits(self):
        """重新加载并应用交易限制设置"""
        # 重新加载配置
        from config.loader import load_config, DAILY_TRADE_LIMIT, get_config_path
        import json

        # 先直接从文件读取最新值
        try:
            config_path = get_config_path()
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
                file_limit = config.get("DAILY_TRADE_LIMIT")
                print(f"从配置文件读取到DAILY_TRADE_LIMIT = {file_limit}")
        except Exception as e:
            print(f"读取配置文件失败: {e}")

        # 再次加载配置以更新内存中的值
        load_config()

        # 打印更新后的值
        from config.loader import DAILY_TRADE_LIMIT as updated_limit

        print(f"内存中更新后的DAILY_TRADE_LIMIT = {updated_limit}")

        # 检查是否真的更新了
        if "file_limit" in locals() and file_limit != updated_limit:
            print(
                f"警告: 文件中的值({file_limit})与更新后内存中的值({updated_limit})不一致!"
            )

        # 立即更新界面显示
        if self.trader and self.trader.is_connected():
            account_info = self.components["account_info"]
            account_info.update_trade_count_display(self.db)

    def show_about(self):
        """显示关于对话框"""
        from PyQt6.QtWidgets import QMessageBox

        QMessageBox.about(
            self,
            "关于MT5交易系统",
            "MT5交易系统 v1.0\n\n"
            "一个与MetaTrader 5集成的自动化交易系统\n"
            "支持批量下单、突破交易和风控管理\n\n"
            "© 2023 All Rights Reserved",
        )
