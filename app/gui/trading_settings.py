"""
交易设置模块

包含交易品种选择和止损模式设置
"""

from PyQt6.QtWidgets import QGroupBox, QVBoxLayout, QHBoxLayout, QLabel, QComboBox
from config.loader import SYMBOLS, SL_MODE


class TradingSettingsSection:
    """交易设置区域"""

    def __init__(self):
        """初始化交易设置区域"""
        self.group_box = QGroupBox("交易设置")
        self.layout = QVBoxLayout()
        self.group_box.setLayout(self.layout)
        self.init_ui()

    def init_ui(self):
        """初始化UI"""
        # 交易品种选择
        row1_layout = QHBoxLayout()
        self.symbol_input = QComboBox()

        # 初始时使用配置中的品种，连接成功后会更新
        self.symbol_input.addItems(SYMBOLS)

        row1_layout.addWidget(QLabel("交易品种:"))
        row1_layout.addWidget(self.symbol_input)

        # 添加止损模式选择
        self.sl_mode_combo = QComboBox()
        self.sl_mode_combo.addItems(["固定点数止损", "K线关键位止损"])
        if SL_MODE["DEFAULT_MODE"] == "FIXED_POINTS":
            self.sl_mode_combo.setCurrentIndex(0)
        else:
            self.sl_mode_combo.setCurrentIndex(1)

        row1_layout.addWidget(QLabel("止损模式:"))
        row1_layout.addWidget(self.sl_mode_combo)

        self.layout.addLayout(row1_layout)

    def on_symbol_changed(self, symbol: str, trader):
        """
        当交易品种改变时调整参数

        Args:
            symbol: 新选择的交易品种
            trader: 交易者对象
        """
        # 从trader获取交易品种参数
        if trader and trader.is_connected():
            symbol_params = trader.get_symbol_params(symbol)
        else:
            # 使用默认参数
            symbol_params = {
                "volume": 0.10,
                "min_volume": 0.01,
                "max_volume": 100.0,
                "volume_step": 0.01,
                "min_sl_points": 0,
                "max_sl_points": 100000,
                "min_tp_points": 0,
                "max_tp_points": 100000,
            }

        # 通知批量下单设置更新UI
        from app.gui.batch_order import update_symbol_params

        return symbol_params

    def on_sl_mode_changed(self, index):
        """
        当止损模式改变时更新UI和参数

        Args:
            index: 选择的索引，0表示固定点数止损，1表示K线关键位止损
        """
        # 保存当前选择的止损模式
        SL_MODE["DEFAULT_MODE"] = "FIXED_POINTS" if index == 0 else "CANDLE_KEY_LEVEL"

        # 通知批量下单设置更新UI
        from app.gui.batch_order import update_sl_mode

        return SL_MODE["DEFAULT_MODE"]

    def update_symbols_list(self, trader):
        """
        更新交易品种列表

        Args:
            trader: 交易者对象
        """
        try:
            # 先清空当前列表
            self.symbol_input.clear()

            print(f"trading_settings.update_symbols_list: 当前SYMBOLS = {SYMBOLS}")

            # 获取交易品种列表
            symbols = trader.get_all_symbols()

            # 获取配置文件中的交易品种（保持原有顺序）
            config_symbols = SYMBOLS.copy()  # 创建副本以避免引用问题
            print(
                f"trading_settings.update_symbols_list: 使用配置中的SYMBOLS = {config_symbols}"
            )

            # 添加品种到下拉列表，保持配置文件中的顺序
            for symbol in config_symbols:
                # 只添加在MT5中存在的品种
                if not symbols or symbol in symbols:
                    self.symbol_input.addItem(symbol)

            # 如果列表不为空，选择第一个品种
            if self.symbol_input.count() > 0:
                self.symbol_input.setCurrentIndex(0)
                return self.symbol_input.currentText()

            return None
        except Exception as e:
            print(f"更新交易品种列表出错：{str(e)}")
            return None
