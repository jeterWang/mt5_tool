"""
交易设置模块

包含交易品种选择和止损模式设置
"""

from PyQt6.QtWidgets import QGroupBox, QVBoxLayout, QHBoxLayout, QLabel, QComboBox
from config.loader import SYMBOLS, SL_MODE, POSITION_SIZING


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
        self.symbol_input.addItems(SYMBOLS)
        row1_layout.addWidget(QLabel("交易品种:"))
        row1_layout.addWidget(self.symbol_input)

        # 止损模式选择（只用 config 的 SL_MODE 字段初始化，切换时实时保存）
        self.sl_mode_combo = QComboBox()
        self.sl_mode_combo.addItems(["固定点数止损", "K线关键位止损"])
        # 初始化时读取 config
        from app.config.config_manager import config_manager

        mode = config_manager.get("SL_MODE", "FIXED_POINTS")
        self.sl_mode_combo.setCurrentIndex(0 if mode == "FIXED_POINTS" else 1)
        self.sl_mode_combo.currentIndexChanged.connect(self.on_sl_mode_changed)
        row1_layout.addWidget(QLabel("止损模式:"))
        row1_layout.addWidget(self.sl_mode_combo)

        self.layout.addLayout(row1_layout)

        # 添加仓位计算模式选择
        row2_layout = QHBoxLayout()
        self.position_sizing_combo = QComboBox()
        self.position_sizing_combo.addItems(["手动设置手数", "固定亏损计算仓位"])
        if POSITION_SIZING["DEFAULT_MODE"] == "MANUAL":
            self.position_sizing_combo.setCurrentIndex(0)
        else:
            self.position_sizing_combo.setCurrentIndex(1)

        row2_layout.addWidget(QLabel("仓位计算:"))
        row2_layout.addWidget(self.position_sizing_combo)

        self.layout.addLayout(row2_layout)

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
        当止损模式改变时，保存到 config
        """
        from app.config.config_manager import config_manager

        mode = "FIXED_POINTS" if index == 0 else "CANDLE_KEY_LEVEL"
        config_manager.set("SL_MODE", mode)
        config_manager.save()
        # 通知批量下单设置更新UI
        from app.gui.batch_order import update_sl_mode

        update_sl_mode(mode)
        return mode

    def on_position_sizing_changed(self, index):
        """
        当仓位计算模式改变时更新UI和参数

        Args:
            index: 选择的索引，0表示手动设置手数，1表示固定亏损计算仓位
        """
        # 保存当前选择的仓位计算模式
        POSITION_SIZING["DEFAULT_MODE"] = "MANUAL" if index == 0 else "FIXED_LOSS"

        # 通知批量下单设置更新UI
        from app.gui.batch_order import update_position_sizing_mode

        return POSITION_SIZING["DEFAULT_MODE"]

    def update_symbols_list(self, trader):
        """
        更新交易品种列表

        Args:
            trader: 交易者对象
        """
        try:
            # 先清空当前列表
            self.symbol_input.clear()

            # print(f"trading_settings.update_symbols_list: 当前SYMBOLS = {SYMBOLS}")

            # 获取交易品种列表
            symbols = trader.get_all_symbols()

            # 获取配置文件中的交易品种（保持原有顺序）
            config_symbols = SYMBOLS.copy()  # 创建副本以避免引用问题
            # print(
            #     f"trading_settings.update_symbols_list: 使用配置中的SYMBOLS = {config_symbols}"
            # )

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
            # print(f"更新交易品种列表出错：{str(e)}")
            return None
