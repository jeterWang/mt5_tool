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
import config.loader as config_loader
from app.config.config_manager import config_manager


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
        # 移除批量下单标签页 - 统一在主界面配置
        # self.create_batch_order_tab()
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
        for i, symbol in enumerate(config_manager.get("SYMBOLS")):
            self.symbols_table.setItem(i, 0, QTableWidgetItem(symbol))

        symbols_layout.addWidget(self.symbols_table)

        # 默认时间框架
        timeframe_layout = QHBoxLayout()
        timeframe_layout.addWidget(QLabel("默认时间框架:"))
        self.timeframe_combo = QComboBox()
        self.timeframe_combo.addItems(
            ["M1", "M5", "M15", "M30", "H1", "H4", "D1", "W1", "MN1"]
        )
        self.timeframe_combo.setCurrentText(config_manager.get("DEFAULT_TIMEFRAME"))
        timeframe_layout.addWidget(self.timeframe_combo)

        # 时区设置
        timezone_layout = QHBoxLayout()
        timezone_layout.addWidget(QLabel("时区差值(小时):"))
        self.timezone_spin = QSpinBox()
        self.timezone_spin.setRange(-12, 12)
        self.timezone_spin.setValue(config_manager.get("Delta_TIMEZONE"))
        timezone_layout.addWidget(self.timezone_spin)

        # 交易日重置时间
        reset_layout = QHBoxLayout()
        reset_layout.addWidget(QLabel("交易日重置时间(小时):"))
        self.reset_spin = QSpinBox()
        self.reset_spin.setRange(0, 23)
        self.reset_spin.setValue(config_manager.get("TRADING_DAY_RESET_HOUR"))
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
        gui_settings = config_manager.get("GUI_SETTINGS")
        # 窗口置顶设置
        top_layout = QHBoxLayout()
        self.window_top_check = QCheckBox("窗口置顶")
        self.window_top_check.setChecked(gui_settings["WINDOW_TOP"])
        top_layout.addWidget(self.window_top_check)
        # 声音提醒设置
        sound_layout = QHBoxLayout()
        self.sound_alert_check = QCheckBox("启用声音提醒")
        self.sound_alert_check.setChecked(gui_settings["SOUND_ALERT"])
        sound_layout.addWidget(self.sound_alert_check)
        # 提前提醒秒数
        alert_layout = QHBoxLayout()
        alert_layout.addWidget(QLabel("提前提醒秒数:"))
        self.alert_seconds_spin = QSpinBox()
        self.alert_seconds_spin.setRange(1, 60)
        self.alert_seconds_spin.setValue(gui_settings["ALERT_SECONDS"])
        alert_layout.addWidget(self.alert_seconds_spin)
        # 提示音设置
        beep_layout = QHBoxLayout()
        beep_layout.addWidget(QLabel("提示音频率(Hz):"))
        self.beep_freq_spin = QSpinBox()
        self.beep_freq_spin.setRange(100, 2000)
        self.beep_freq_spin.setValue(gui_settings["BEEP_FREQUENCY"])
        beep_layout.addWidget(self.beep_freq_spin)
        beep_layout.addWidget(QLabel("提示音持续时间(ms):"))
        self.beep_duration_spin = QSpinBox()
        self.beep_duration_spin.setRange(50, 2000)
        self.beep_duration_spin.setValue(gui_settings["BEEP_DURATION"])
        beep_layout.addWidget(self.beep_duration_spin)
        # 一键保本偏移点数设置
        breakeven_layout = QHBoxLayout()
        breakeven_layout.addWidget(QLabel("一键保本偏移点数:"))
        self.breakeven_offset_spin = QSpinBox()
        self.breakeven_offset_spin.setRange(-1000, 1000)
        self.breakeven_offset_spin.setValue(
            gui_settings.get("BREAKEVEN_OFFSET_POINTS", 0)
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
        # 风控设置
        risk_group = QGroupBox("风控设置")
        risk_layout = QHBoxLayout(risk_group)
        self.loss_limit_spin = QDoubleSpinBox()
        self.loss_limit_spin.setRange(0, 100000)
        self.loss_limit_spin.setValue(config_manager.get("DAILY_LOSS_LIMIT"))
        risk_layout.addWidget(QLabel("每日最大亏损:"))
        risk_layout.addWidget(self.loss_limit_spin)
        self.trade_limit_spin = QSpinBox()
        self.trade_limit_spin.setRange(0, 1000)
        self.trade_limit_spin.setValue(config_manager.get("DAILY_TRADE_LIMIT"))
        risk_layout.addWidget(QLabel("每日最大交易次数:"))
        risk_layout.addWidget(self.trade_limit_spin)
        # 突破设置
        breakout_group = QGroupBox("突破设置")
        breakout_layout = QVBoxLayout(breakout_group)
        breakout_settings = config_manager.get("BREAKOUT_SETTINGS")
        high_layout = QHBoxLayout()
        high_layout.addWidget(QLabel("高点突破偏移点数:"))
        self.high_offset_spin = QSpinBox()
        self.high_offset_spin.setRange(0, 10000)
        self.high_offset_spin.setValue(breakout_settings["HIGH_OFFSET_POINTS"])
        high_layout.addWidget(self.high_offset_spin)
        low_layout = QHBoxLayout()
        low_layout.addWidget(QLabel("低点突破偏移点数:"))
        self.low_offset_spin = QSpinBox()
        self.low_offset_spin.setRange(0, 10000)
        self.low_offset_spin.setValue(breakout_settings["LOW_OFFSET_POINTS"])
        low_layout.addWidget(self.low_offset_spin)
        sl_offset_layout = QHBoxLayout()
        sl_offset_layout.addWidget(QLabel("止损偏移点数:"))
        self.sl_offset_spin = QSpinBox()
        self.sl_offset_spin.setRange(0, 10000)
        self.sl_offset_spin.setValue(breakout_settings["SL_OFFSET_POINTS"])
        sl_offset_layout.addWidget(self.sl_offset_spin)
        breakout_layout.addLayout(high_layout)
        breakout_layout.addLayout(low_layout)
        breakout_layout.addLayout(sl_offset_layout)
        # 添加所有组件到布局
        layout.addWidget(risk_group)
        layout.addWidget(breakout_group)
        # 添加到标签页
        self.tab_widget.addTab(trading_tab, "交易设置")

    def create_batch_order_tab(self):
        """创建批量下单设置标签页"""
        batch_tab = QGroupBox("批量下单设置")
        layout = QVBoxLayout(batch_tab)
        batch_defaults = config_manager.get("BATCH_ORDER_DEFAULTS")
        self.batch_table = QTableWidget(4, 6)  # 增加为6列，添加fixed_loss列
        self.batch_table.setHorizontalHeaderLabels(
            ["订单", "手数", "止损点数", "止盈点数", "K线回溯数", "亏损($)"]
        )
        self.batch_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        # 填充现有设置
        for i in range(4):
            order_key = f"order{i+1}"
            order_data = batch_defaults[order_key]
            self.batch_table.setItem(i, 0, QTableWidgetItem(f"第{i+1}单"))
            volume_spin = QDoubleSpinBox()
            volume_spin.setRange(0.01, 100)
            volume_spin.setSingleStep(0.01)
            volume_spin.setValue(order_data["volume"])
            self.batch_table.setCellWidget(i, 1, volume_spin)
            sl_spin = QSpinBox()
            sl_spin.setRange(0, 100000)
            sl_spin.setValue(order_data["sl_points"])
            self.batch_table.setCellWidget(i, 2, sl_spin)
            tp_spin = QSpinBox()
            tp_spin.setRange(0, 100000)
            tp_spin.setValue(order_data["tp_points"])
            self.batch_table.setCellWidget(i, 3, tp_spin)
            sl_candle_spin = QSpinBox()
            sl_candle_spin.setRange(1, 20)
            sl_candle_spin.setValue(order_data.get("sl_candle", 3))
            self.batch_table.setCellWidget(i, 4, sl_candle_spin)
            fixed_loss_spin = QDoubleSpinBox()
            fixed_loss_spin.setRange(0.01, 10000)
            fixed_loss_spin.setSingleStep(0.01)
            fixed_loss_spin.setValue(order_data.get("fixed_loss", 5.0))
            self.batch_table.setCellWidget(i, 5, fixed_loss_spin)
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
            symbols = []
            for i in range(self.symbols_table.rowCount()):
                item = self.symbols_table.item(i, 0)
                if item and item.text().strip():
                    symbols.append(item.text().strip())
            config_manager.set("SYMBOLS", symbols)
            config_manager.set("DEFAULT_TIMEFRAME", self.timeframe_combo.currentText())
            config_manager.set("Delta_TIMEZONE", self.timezone_spin.value())
            config_manager.set("TRADING_DAY_RESET_HOUR", self.reset_spin.value())
            # 2. GUI设置
            gui_settings = config_manager.get("GUI_SETTINGS")
            gui_settings["WINDOW_TOP"] = self.window_top_check.isChecked()
            gui_settings["SOUND_ALERT"] = self.sound_alert_check.isChecked()
            gui_settings["ALERT_SECONDS"] = self.alert_seconds_spin.value()
            gui_settings["BEEP_FREQUENCY"] = self.beep_freq_spin.value()
            gui_settings["BEEP_DURATION"] = self.beep_duration_spin.value()
            gui_settings["BREAKEVEN_OFFSET_POINTS"] = self.breakeven_offset_spin.value()
            config_manager.set("GUI_SETTINGS", gui_settings)
            # 3. 交易设置
            breakout_settings = config_manager.get("BREAKOUT_SETTINGS")
            breakout_settings["HIGH_OFFSET_POINTS"] = self.high_offset_spin.value()
            breakout_settings["LOW_OFFSET_POINTS"] = self.low_offset_spin.value()
            breakout_settings["SL_OFFSET_POINTS"] = self.sl_offset_spin.value()
            config_manager.set("BREAKOUT_SETTINGS", breakout_settings)
            # 4. 风控设置
            config_manager.set("DAILY_LOSS_LIMIT", self.loss_limit_spin.value())
            config_manager.set("DAILY_TRADE_LIMIT", self.trade_limit_spin.value())
            # 5. 批量下单设置 - 已移除，统一在主界面管理
            # 批量下单配置现在完全由主界面的批量下单组件管理
            # 避免两个地方配置同一个设置造成混淆
            # 保存到文件
            print("[Settings] 开始保存配置...")
            success = config_manager.save()
            print(f"[Settings] 保存结果: {success}")

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
