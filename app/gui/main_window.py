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
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QIcon, QFont, QFontDatabase
import os

from utils.paths import get_icon_path, get_font_path
from app.trader import MT5Trader
from app.database import TradeDatabase
from config.loader import GUI_SETTINGS
from app.gui.account_info import AccountInfoSection
from app.gui.pnl_info import PnlInfoSection
from app.gui.countdown import CountdownSection
from app.gui.trading_settings import TradingSettingsSection
from app.gui.batch_order import BatchOrderSection
from app.gui.trading_buttons import TradingButtonsSection
from app.gui.positions_table import PositionsTableSection


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
        self.trader = None

        # 初始化数据库
        self.db = TradeDatabase()

        # 设置字体
        self.setup_font()

        # 设置窗口标题和大小
        self.setWindowTitle("MT5交易系统")
        self.setGeometry(100, 100, 1000, 800)

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

        # 添加账户信息和交易次数显示
        self.components["account_info"] = AccountInfoSection()
        main_layout.addLayout(self.components["account_info"].layout)

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

        trading_settings = self.components["trading_settings"]
        trading_settings.update_symbols_list(self.trader)

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
