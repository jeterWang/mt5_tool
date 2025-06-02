"""
设置页面模块

提供可视化配置界面，用于修改config.json文件的各项设置
"""

import json
import os
from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QTabWidget,
    QGroupBox,
    QLabel,
    QLineEdit,
    QSpinBox,
    QDoubleSpinBox,
    QCheckBox,
    QPushButton,
    QComboBox,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QMessageBox,
    QPlainTextEdit,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

from config.loader import (
    SYMBOLS,
    DEFAULT_TIMEFRAME,
    Delta_TIMEZONE,
    TRADING_DAY_RESET_HOUR,
    DAILY_LOSS_LIMIT,
    DAILY_TRADE_LIMIT,
    GUI_SETTINGS,
    SL_MODE,
    BREAKOUT_SETTINGS,
    BATCH_ORDER_DEFAULTS,
    save_config,
    get_config_path,
)
from utils.paths import get_icon_path


class SettingsDialog(QDialog):
    """设置对话框，提供对配置文件的可视化编辑"""

    def __init__(self, parent=None):
        """初始化设置对话框"""
        super().__init__(parent)
        self.setWindowTitle("MT5交易系统设置")
        self.setWindowIcon(QIcon(get_icon_path("settings.svg")))
        self.resize(800, 600)

        # 创建布局
        self.layout = QVBoxLayout(self)

        # 创建标签页控件
        self.tab_widget = QTabWidget()
        self.layout.addWidget(self.tab_widget)

        # 创建各个设置页
        self.create_basic_tab()
        self.create_gui_tab()
        self.create_trading_tab()
        self.create_batch_order_tab()
        self.create_advanced_tab()

        # 添加保存和取消按钮
        self.buttons_layout = QHBoxLayout()
        self.save_button = QPushButton("保存设置")
        self.cancel_button = QPushButton("取消")
        self.buttons_layout.addWidget(self.save_button)
        self.buttons_layout.addWidget(self.cancel_button)
        self.layout.addLayout(self.buttons_layout)

        # 连接信号
        self.save_button.clicked.connect(self.save_settings)
        self.cancel_button.clicked.connect(self.reject)

    def create_basic_tab(self):
        """创建基本设置标签页"""
        basic_tab = QGroupBox("基本设置")
        layout = QVBoxLayout(basic_tab)

        # 交易品种设置
        symbols_group = QGroupBox("交易品种")
        symbols_layout = QVBoxLayout(symbols_group)

        self.symbols_table = QTableWidget(10, 1)  # 预设10行
        self.symbols_table.setHorizontalHeaderLabels(["交易品种"])
        self.symbols_table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.Stretch
        )

        # 填充现有品种
        for i, symbol in enumerate(SYMBOLS):
            self.symbols_table.setItem(i, 0, QTableWidgetItem(symbol))

        symbols_layout.addWidget(self.symbols_table)

        # 默认时间框架
        timeframe_layout = QHBoxLayout()
        timeframe_layout.addWidget(QLabel("默认时间框架:"))
        self.timeframe_combo = QComboBox()
        self.timeframe_combo.addItems(
            ["M1", "M5", "M15", "M30", "H1", "H4", "D1", "W1", "MN1"]
        )
        self.timeframe_combo.setCurrentText(DEFAULT_TIMEFRAME)
        timeframe_layout.addWidget(self.timeframe_combo)

        # 时区设置
        timezone_layout = QHBoxLayout()
        timezone_layout.addWidget(QLabel("时区差值(小时):"))
        self.timezone_spin = QSpinBox()
        self.timezone_spin.setRange(-12, 12)
        self.timezone_spin.setValue(Delta_TIMEZONE)
        timezone_layout.addWidget(self.timezone_spin)

        # 交易日重置时间
        reset_layout = QHBoxLayout()
        reset_layout.addWidget(QLabel("交易日重置时间(小时):"))
        self.reset_spin = QSpinBox()
        self.reset_spin.setRange(0, 23)
        self.reset_spin.setValue(TRADING_DAY_RESET_HOUR)
        reset_layout.addWidget(self.reset_spin)

        # 添加所有组件到布局
        layout.addWidget(symbols_group)
        layout.addLayout(timeframe_layout)
        layout.addLayout(timezone_layout)
        layout.addLayout(reset_layout)

        # 添加到标签页
        self.tab_widget.addTab(basic_tab, "基本设置")

    def create_gui_tab(self):
        """创建GUI设置标签页"""
        gui_tab = QGroupBox("界面设置")
        layout = QVBoxLayout(gui_tab)

        # 窗口置顶设置
        top_layout = QHBoxLayout()
        self.window_top_check = QCheckBox("窗口置顶")
        self.window_top_check.setChecked(GUI_SETTINGS["WINDOW_TOP"])
        top_layout.addWidget(self.window_top_check)

        # 声音提醒设置
        sound_layout = QHBoxLayout()
        self.sound_alert_check = QCheckBox("启用声音提醒")
        self.sound_alert_check.setChecked(GUI_SETTINGS["SOUND_ALERT"])
        sound_layout.addWidget(self.sound_alert_check)

        # 提前提醒秒数
        alert_layout = QHBoxLayout()
        alert_layout.addWidget(QLabel("提前提醒秒数:"))
        self.alert_seconds_spin = QSpinBox()
        self.alert_seconds_spin.setRange(1, 60)
        self.alert_seconds_spin.setValue(GUI_SETTINGS["ALERT_SECONDS"])
        alert_layout.addWidget(self.alert_seconds_spin)

        # 提示音设置
        beep_layout = QHBoxLayout()
        beep_layout.addWidget(QLabel("提示音频率(Hz):"))
        self.beep_freq_spin = QSpinBox()
        self.beep_freq_spin.setRange(100, 2000)
        self.beep_freq_spin.setValue(GUI_SETTINGS["BEEP_FREQUENCY"])
        beep_layout.addWidget(self.beep_freq_spin)

        beep_layout.addWidget(QLabel("提示音持续时间(ms):"))
        self.beep_duration_spin = QSpinBox()
        self.beep_duration_spin.setRange(50, 2000)
        self.beep_duration_spin.setValue(GUI_SETTINGS["BEEP_DURATION"])
        beep_layout.addWidget(self.beep_duration_spin)

        # 一键保本偏移点数设置
        breakeven_layout = QHBoxLayout()
        breakeven_layout.addWidget(QLabel("一键保本偏移点数:"))
        self.breakeven_offset_spin = QSpinBox()
        self.breakeven_offset_spin.setRange(-1000, 1000)
        self.breakeven_offset_spin.setValue(
            GUI_SETTINGS.get("BREAKEVEN_OFFSET_POINTS", 0)
        )
        breakeven_layout.addWidget(self.breakeven_offset_spin)

        # 添加所有组件到布局
        layout.addLayout(top_layout)
        layout.addLayout(sound_layout)
        layout.addLayout(alert_layout)
        layout.addLayout(beep_layout)
        layout.addLayout(breakeven_layout)
        layout.addStretch()

        # 添加到标签页
        self.tab_widget.addTab(gui_tab, "界面设置")

    def create_trading_tab(self):
        """创建交易设置标签页"""
        trading_tab = QGroupBox("交易设置")
        layout = QVBoxLayout(trading_tab)

        # 风控设置组
        risk_group = QGroupBox("风控设置")
        risk_layout = QVBoxLayout(risk_group)

        # 日亏损限额
        loss_layout = QHBoxLayout()
        loss_layout.addWidget(QLabel("日亏损限额:"))
        self.loss_limit_spin = QDoubleSpinBox()
        self.loss_limit_spin.setRange(0, 10000)
        self.loss_limit_spin.setValue(DAILY_LOSS_LIMIT)
        loss_layout.addWidget(self.loss_limit_spin)

        # 日交易次数限制
        trade_layout = QHBoxLayout()
        trade_layout.addWidget(QLabel("日交易次数限制:"))
        self.trade_limit_spin = QSpinBox()
        self.trade_limit_spin.setRange(0, 1000)
        self.trade_limit_spin.setValue(DAILY_TRADE_LIMIT)
        trade_layout.addWidget(self.trade_limit_spin)

        risk_layout.addLayout(loss_layout)
        risk_layout.addLayout(trade_layout)

        # 止损设置
        sl_group = QGroupBox("止损设置")
        sl_layout = QVBoxLayout(sl_group)

        # 默认止损模式
        sl_mode_layout = QHBoxLayout()
        sl_mode_layout.addWidget(QLabel("默认止损模式:"))
        self.sl_mode_combo = QComboBox()
        self.sl_mode_combo.addItems(["固定点数止损", "K线关键位止损"])
        self.sl_mode_combo.setCurrentIndex(
            0 if SL_MODE["DEFAULT_MODE"] == "FIXED_POINTS" else 1
        )
        sl_mode_layout.addWidget(self.sl_mode_combo)

        # K线回溯数量
        candle_layout = QHBoxLayout()
        candle_layout.addWidget(QLabel("K线回溯数量:"))
        self.candle_lookback_spin = QSpinBox()
        self.candle_lookback_spin.setRange(1, 20)
        self.candle_lookback_spin.setValue(SL_MODE["CANDLE_LOOKBACK"])
        candle_layout.addWidget(self.candle_lookback_spin)

        sl_layout.addLayout(sl_mode_layout)
        sl_layout.addLayout(candle_layout)

        # 突破设置
        breakout_group = QGroupBox("突破设置")
        breakout_layout = QVBoxLayout(breakout_group)

        # 高点突破偏移点数
        high_layout = QHBoxLayout()
        high_layout.addWidget(QLabel("高点突破偏移点数:"))
        self.high_offset_spin = QSpinBox()
        self.high_offset_spin.setRange(0, 1000)
        self.high_offset_spin.setValue(BREAKOUT_SETTINGS["HIGH_OFFSET_POINTS"])
        high_layout.addWidget(self.high_offset_spin)

        # 低点突破偏移点数
        low_layout = QHBoxLayout()
        low_layout.addWidget(QLabel("低点突破偏移点数:"))
        self.low_offset_spin = QSpinBox()
        self.low_offset_spin.setRange(0, 1000)
        self.low_offset_spin.setValue(BREAKOUT_SETTINGS["LOW_OFFSET_POINTS"])
        low_layout.addWidget(self.low_offset_spin)

        # 止损偏移点数
        sl_offset_layout = QHBoxLayout()
        sl_offset_layout.addWidget(QLabel("止损偏移点数:"))
        self.sl_offset_spin = QSpinBox()
        self.sl_offset_spin.setRange(0, 10000)
        self.sl_offset_spin.setValue(BREAKOUT_SETTINGS["SL_OFFSET_POINTS"])
        sl_offset_layout.addWidget(self.sl_offset_spin)

        breakout_layout.addLayout(high_layout)
        breakout_layout.addLayout(low_layout)
        breakout_layout.addLayout(sl_offset_layout)

        # 添加所有组件到布局
        layout.addWidget(risk_group)
        layout.addWidget(sl_group)
        layout.addWidget(breakout_group)

        # 添加到标签页
        self.tab_widget.addTab(trading_tab, "交易设置")

    def create_batch_order_tab(self):
        """创建批量下单设置标签页"""
        batch_tab = QGroupBox("批量下单设置")
        layout = QVBoxLayout(batch_tab)

        # 创建表格
        self.batch_table = QTableWidget(4, 5)  # 增加为5列，添加sl_candle列
        self.batch_table.setHorizontalHeaderLabels(
            ["订单", "手数", "止损点数", "止盈点数", "K线回溯数"]
        )
        self.batch_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )

        # 填充现有设置
        for i in range(4):
            order_key = f"order{i+1}"
            order_data = BATCH_ORDER_DEFAULTS[order_key]

            # 订单编号
            self.batch_table.setItem(i, 0, QTableWidgetItem(f"第{i+1}单"))

            # 创建SpinBox用于手数
            volume_spin = QDoubleSpinBox()
            volume_spin.setRange(0.01, 100)
            volume_spin.setSingleStep(0.01)
            volume_spin.setValue(order_data["volume"])
            self.batch_table.setCellWidget(i, 1, volume_spin)

            # 创建SpinBox用于止损点数
            sl_spin = QSpinBox()
            sl_spin.setRange(0, 100000)
            sl_spin.setValue(order_data["sl_points"])
            self.batch_table.setCellWidget(i, 2, sl_spin)

            # 创建SpinBox用于止盈点数
            tp_spin = QSpinBox()
            tp_spin.setRange(0, 100000)
            tp_spin.setValue(order_data["tp_points"])
            self.batch_table.setCellWidget(i, 3, tp_spin)

            # 创建SpinBox用于K线回溯数
            sl_candle_spin = QSpinBox()
            sl_candle_spin.setRange(1, 20)
            sl_candle_spin.setValue(
                order_data.get("sl_candle", SL_MODE["CANDLE_LOOKBACK"])
            )  # 使用sl_candle或默认值
            self.batch_table.setCellWidget(i, 4, sl_candle_spin)

        layout.addWidget(self.batch_table)

        # 添加到标签页
        self.tab_widget.addTab(batch_tab, "批量下单")

    def create_advanced_tab(self):
        """创建高级设置标签页(直接编辑JSON)"""
        advanced_tab = QGroupBox("高级设置")
        layout = QVBoxLayout(advanced_tab)

        # 添加说明标签
        layout.addWidget(QLabel("直接编辑配置文件(JSON格式):"))

        # 创建文本编辑器
        self.json_editor = QPlainTextEdit()
        self.json_editor.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)

        # 加载当前配置JSON
        try:
            config_path = get_config_path()
            if os.path.exists(config_path):
                with open(config_path, "r", encoding="utf-8") as f:
                    config_json = json.load(f)
                    self.json_editor.setPlainText(
                        json.dumps(config_json, indent=4, ensure_ascii=False)
                    )
        except Exception as e:
            self.json_editor.setPlainText(f"加载配置出错: {str(e)}")

        layout.addWidget(self.json_editor)

        # 验证JSON按钮
        validate_button = QPushButton("验证JSON")
        validate_button.clicked.connect(self.validate_json)
        layout.addWidget(validate_button)

        # 添加到标签页
        self.tab_widget.addTab(advanced_tab, "高级设置")

    def validate_json(self):
        """验证JSON是否有效"""
        try:
            json_text = self.json_editor.toPlainText()
            json.loads(json_text)
            QMessageBox.information(self, "验证成功", "JSON格式正确!")
        except Exception as e:
            QMessageBox.critical(self, "验证失败", f"JSON格式错误: {str(e)}")

    def save_settings(self):
        """保存所有设置到配置文件"""
        try:
            # 1. 基本设置
            # 收集交易品种
            symbols = []
            for i in range(self.symbols_table.rowCount()):
                item = self.symbols_table.item(i, 0)
                if item and item.text().strip():
                    symbols.append(item.text().strip())

            # 保存前先清空当前SYMBOLS，确保删除的品种不会保留
            SYMBOLS.clear()
            # 使用extend而不是赋值，确保引用不变
            SYMBOLS.extend(symbols)

            # 默认时间周期
            DEFAULT_TIMEFRAME = self.timeframe_combo.currentText()

            # 时区差值
            Delta_TIMEZONE = self.timezone_spin.value()

            # 交易日重置时间
            TRADING_DAY_RESET_HOUR = self.reset_spin.value()

            # 2. GUI设置
            GUI_SETTINGS["WINDOW_TOP"] = self.window_top_check.isChecked()
            GUI_SETTINGS["SOUND_ALERT"] = self.sound_alert_check.isChecked()
            GUI_SETTINGS["ALERT_SECONDS"] = self.alert_seconds_spin.value()
            GUI_SETTINGS["BEEP_FREQUENCY"] = self.beep_freq_spin.value()
            GUI_SETTINGS["BEEP_DURATION"] = self.beep_duration_spin.value()
            GUI_SETTINGS["BREAKEVEN_OFFSET_POINTS"] = self.breakeven_offset_spin.value()

            # 3. 交易设置
            # 止损模式
            SL_MODE["DEFAULT_MODE"] = (
                "FIXED_POINTS"
                if self.sl_mode_combo.currentIndex() == 0
                else "CANDLE_KEY_LEVEL"
            )
            SL_MODE["CANDLE_LOOKBACK"] = self.candle_lookback_spin.value()

            # 突破设置
            BREAKOUT_SETTINGS["HIGH_OFFSET_POINTS"] = self.high_offset_spin.value()
            BREAKOUT_SETTINGS["LOW_OFFSET_POINTS"] = self.low_offset_spin.value()
            BREAKOUT_SETTINGS["SL_OFFSET_POINTS"] = self.sl_offset_spin.value()

            # 4. 风控设置
            DAILY_LOSS_LIMIT = self.loss_limit_spin.value()
            DAILY_TRADE_LIMIT = self.trade_limit_spin.value()

            # 5. 批量下单设置
            for i in range(4):
                order_key = f"order{i+1}"
                volume_spin = self.batch_table.cellWidget(i, 1)
                sl_spin = self.batch_table.cellWidget(i, 2)
                tp_spin = self.batch_table.cellWidget(i, 3)
                sl_candle_spin = self.batch_table.cellWidget(i, 4)

                BATCH_ORDER_DEFAULTS[order_key] = {
                    "volume": volume_spin.value(),
                    "sl_points": sl_spin.value(),
                    "tp_points": tp_spin.value(),
                    "sl_candle": sl_candle_spin.value(),
                }

            # 保存到文件
            success = save_config()

            if success:
                QMessageBox.information(self, "保存成功", "设置已成功保存")
                self.accept()
            else:
                QMessageBox.warning(self, "保存失败", "配置保存失败，请检查文件权限")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存设置时出错: {str(e)}")


def show_settings_dialog(parent=None):
    """显示设置对话框"""
    dialog = SettingsDialog(parent)
    return dialog.exec()
