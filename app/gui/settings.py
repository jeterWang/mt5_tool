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

        # 添加所有组件到布局
        layout.addLayout(top_layout)
        layout.addLayout(sound_layout)
        layout.addLayout(alert_layout)
        layout.addLayout(beep_layout)
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
        # 声明全局变量
        global SYMBOLS, DEFAULT_TIMEFRAME, Delta_TIMEZONE, TRADING_DAY_RESET_HOUR
        global DAILY_LOSS_LIMIT, DAILY_TRADE_LIMIT, GUI_SETTINGS, SL_MODE, BREAKOUT_SETTINGS
        global BATCH_ORDER_DEFAULTS

        print(f"保存前SYMBOLS: {SYMBOLS}")  # 调试信息
        print(f"保存前DAILY_TRADE_LIMIT: {DAILY_TRADE_LIMIT}")  # 调试信息

        # 检查当前标签页，如果是高级设置，则尝试从JSON编辑器保存
        if self.tab_widget.currentIndex() == 4:  # 高级设置标签页
            try:
                json_text = self.json_editor.toPlainText()
                config_data = json.loads(json_text)

                # 更新全局变量
                if "SYMBOLS" in config_data:
                    SYMBOLS.clear()
                    SYMBOLS.extend(config_data["SYMBOLS"])
                if "DEFAULT_TIMEFRAME" in config_data:
                    DEFAULT_TIMEFRAME = config_data["DEFAULT_TIMEFRAME"]
                if "Delta_TIMEZONE" in config_data:
                    Delta_TIMEZONE = config_data["Delta_TIMEZONE"]
                if "TRADING_DAY_RESET_HOUR" in config_data:
                    TRADING_DAY_RESET_HOUR = config_data["TRADING_DAY_RESET_HOUR"]
                if "DAILY_LOSS_LIMIT" in config_data:
                    DAILY_LOSS_LIMIT = config_data["DAILY_LOSS_LIMIT"]
                if "DAILY_TRADE_LIMIT" in config_data:
                    DAILY_TRADE_LIMIT = config_data["DAILY_TRADE_LIMIT"]
                if "GUI_SETTINGS" in config_data:
                    GUI_SETTINGS.update(config_data["GUI_SETTINGS"])
                if "SL_MODE" in config_data:
                    SL_MODE.update(config_data["SL_MODE"])
                if "BREAKOUT_SETTINGS" in config_data:
                    BREAKOUT_SETTINGS.update(config_data["BREAKOUT_SETTINGS"])
                if "BATCH_ORDER_DEFAULTS" in config_data:
                    BATCH_ORDER_DEFAULTS.update(config_data["BATCH_ORDER_DEFAULTS"])

                # 保存到配置文件
                config_path = get_config_path()
                with open(config_path, "w", encoding="utf-8") as f:
                    json.dump(config_data, f, indent=4, ensure_ascii=False)

                print(f"高级设置保存后SYMBOLS: {SYMBOLS}")  # 调试信息
                print(
                    f"高级设置保存后DAILY_TRADE_LIMIT: {DAILY_TRADE_LIMIT}"
                )  # 调试信息

                # 验证保存后的配置
                try:
                    with open(config_path, "r", encoding="utf-8") as f:
                        saved_config = json.load(f)
                        print(
                            f"文件中的SYMBOLS: {saved_config.get('SYMBOLS', '未找到')}"
                        )  # 调试信息
                        print(
                            f"文件中的DAILY_TRADE_LIMIT: {saved_config.get('DAILY_TRADE_LIMIT', '未找到')}"
                        )  # 调试信息
                except Exception as e:
                    print(f"验证配置时出错: {str(e)}")

                QMessageBox.information(self, "保存成功", "配置已保存!")
                self.accept()
                return
            except Exception as e:
                QMessageBox.critical(self, "保存失败", f"保存配置出错: {str(e)}")
                return

        # 从各个标签页收集设置
        try:
            # 收集交易品种
            symbols = []
            for i in range(self.symbols_table.rowCount()):
                item = self.symbols_table.item(i, 0)
                if item and item.text().strip():
                    symbols.append(item.text().strip())

            print(f"表格中收集到的SYMBOLS: {symbols}")  # 调试信息

            # 保存前先清空当前SYMBOLS，确保删除的品种不会保留
            SYMBOLS.clear()
            # 使用extend而不是赋值，确保引用不变
            SYMBOLS.extend(symbols)

            print(f"清空并添加后SYMBOLS: {SYMBOLS}")  # 调试信息

            DEFAULT_TIMEFRAME = self.timeframe_combo.currentText()
            Delta_TIMEZONE = self.timezone_spin.value()
            TRADING_DAY_RESET_HOUR = self.reset_spin.value()

            # GUI设置
            GUI_SETTINGS["WINDOW_TOP"] = self.window_top_check.isChecked()
            GUI_SETTINGS["SOUND_ALERT"] = self.sound_alert_check.isChecked()
            GUI_SETTINGS["ALERT_SECONDS"] = self.alert_seconds_spin.value()
            GUI_SETTINGS["BEEP_FREQUENCY"] = self.beep_freq_spin.value()
            GUI_SETTINGS["BEEP_DURATION"] = self.beep_duration_spin.value()

            # 交易设置
            DAILY_LOSS_LIMIT = self.loss_limit_spin.value()
            # 先保存spin中的值到临时变量
            trade_limit_value = self.trade_limit_spin.value()
            DAILY_TRADE_LIMIT = trade_limit_value
            print(f"更新后DAILY_TRADE_LIMIT: {DAILY_TRADE_LIMIT}")  # 调试信息

            SL_MODE["DEFAULT_MODE"] = (
                "FIXED_POINTS"
                if self.sl_mode_combo.currentIndex() == 0
                else "CANDLE_KEY_LEVEL"
            )
            SL_MODE["CANDLE_LOOKBACK"] = self.candle_lookback_spin.value()

            BREAKOUT_SETTINGS["HIGH_OFFSET_POINTS"] = self.high_offset_spin.value()
            BREAKOUT_SETTINGS["LOW_OFFSET_POINTS"] = self.low_offset_spin.value()
            BREAKOUT_SETTINGS["SL_OFFSET_POINTS"] = self.sl_offset_spin.value()

            # 批量下单设置
            for i in range(4):
                order_key = f"order{i+1}"
                volume_spin = self.batch_table.cellWidget(i, 1)
                sl_spin = self.batch_table.cellWidget(i, 2)
                tp_spin = self.batch_table.cellWidget(i, 3)
                sl_candle_spin = self.batch_table.cellWidget(i, 4)

                # 检查是否存在sl_candle字段，如果不存在则创建并设置默认值
                if "sl_candle" not in BATCH_ORDER_DEFAULTS[order_key]:
                    # 使用SL_MODE["CANDLE_LOOKBACK"]作为默认值
                    sl_candle_value = SL_MODE["CANDLE_LOOKBACK"]
                else:
                    # 从表格中获取值
                    sl_candle_value = (
                        sl_candle_spin.value()
                        if sl_candle_spin
                        else SL_MODE["CANDLE_LOOKBACK"]
                    )

                BATCH_ORDER_DEFAULTS[order_key] = {
                    "volume": volume_spin.value(),
                    "sl_points": sl_spin.value(),
                    "tp_points": tp_spin.value(),
                    "sl_candle": sl_candle_value,
                }

            print(f"调用save_config前SYMBOLS: {SYMBOLS}")  # 调试信息
            print(
                f"调用save_config前DAILY_TRADE_LIMIT: {DAILY_TRADE_LIMIT}"
            )  # 调试信息

            # 在save_config前创建一个配置字典并手动保存，确保数据正确写入
            config = {
                "SYMBOLS": SYMBOLS.copy(),  # 使用copy确保不会有引用问题
                "DEFAULT_TIMEFRAME": DEFAULT_TIMEFRAME,
                "Delta_TIMEZONE": Delta_TIMEZONE,
                "TRADING_DAY_RESET_HOUR": TRADING_DAY_RESET_HOUR,
                "DAILY_LOSS_LIMIT": DAILY_LOSS_LIMIT,
                "DAILY_TRADE_LIMIT": trade_limit_value,  # 确保使用spin的值
                "GUI_SETTINGS": GUI_SETTINGS,
                "SL_MODE": SL_MODE,
                "BREAKOUT_SETTINGS": BREAKOUT_SETTINGS,
                "BATCH_ORDER_DEFAULTS": BATCH_ORDER_DEFAULTS,
            }

            config_path = get_config_path()
            print(f"保存配置到: {config_path}")  # 调试信息

            # 确保目录存在
            config_dir = os.path.dirname(config_path)
            if not os.path.exists(config_dir):
                os.makedirs(config_dir, exist_ok=True)
                print(f"创建目录: {config_dir}")

            # 直接保存配置文件，不使用save_config函数
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=4, ensure_ascii=False)

            print(f"直接写入配置后DAILY_TRADE_LIMIT: {config['DAILY_TRADE_LIMIT']}")

            # 重新加载配置，确保内存中的值与文件一致
            from config.loader import load_config

            load_config()

            # 验证加载后的值
            from config.loader import DAILY_TRADE_LIMIT as loaded_limit

            print(f"重新加载后DAILY_TRADE_LIMIT: {loaded_limit}")

            # 手动确认保存的数据是否正确写入文件
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    saved_config = json.load(f)
                    print(
                        f"文件中的SYMBOLS: {saved_config.get('SYMBOLS', '未找到')}"
                    )  # 调试信息
                    print(
                        f"文件中的DAILY_TRADE_LIMIT: {saved_config.get('DAILY_TRADE_LIMIT', '未找到')}"
                    )  # 调试信息

                    # 最后再次确认DAILY_TRADE_LIMIT的值与用户设置一致
                    if saved_config.get("DAILY_TRADE_LIMIT") != trade_limit_value:
                        print(
                            f"警告：保存的DAILY_TRADE_LIMIT值不匹配！设置值: {trade_limit_value}, 文件值: {saved_config.get('DAILY_TRADE_LIMIT')}"
                        )
                        # 再次尝试强制更新文件
                        saved_config["DAILY_TRADE_LIMIT"] = trade_limit_value
                        with open(config_path, "w", encoding="utf-8") as f:
                            json.dump(saved_config, f, indent=4, ensure_ascii=False)
                        print(f"已强制更新DAILY_TRADE_LIMIT为: {trade_limit_value}")
            except Exception as e:
                print(f"验证配置时出错: {str(e)}")
                success = False

            QMessageBox.information(self, "保存成功", "配置已保存!")
            self.accept()

        except Exception as e:
            print(f"保存过程中出错: {str(e)}")  # 调试信息
            QMessageBox.critical(self, "保存失败", f"保存配置出错: {str(e)}")
            return


def show_settings_dialog(parent=None):
    """显示设置对话框"""
    dialog = SettingsDialog(parent)
    return dialog.exec()
