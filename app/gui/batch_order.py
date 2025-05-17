"""
批量下单设置模块

提供批量下单的参数设置界面
"""

from PyQt6.QtWidgets import (
    QGroupBox,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QDoubleSpinBox,
    QSpinBox,
)
from config.loader import BATCH_ORDER_DEFAULTS, SL_MODE


# 全局变量，用于存储当前实例
_instance = None


class BatchOrderSection:
    """批量下单设置区域"""

    def __init__(self):
        """初始化批量下单设置区域"""
        global _instance
        _instance = self

        self.group_box = QGroupBox("批量下单设置")
        self.layout = QVBoxLayout()
        self.group_box.setLayout(self.layout)

        # 批量下单设置控件
        self.volume_inputs = []
        self.sl_points_inputs = []  # 固定点数止损
        self.sl_candle_inputs = []  # K线回溯数量
        self.tp_points_inputs = []
        self.sl_labels = []  # 存储止损标签的引用，以便动态修改

        self.init_ui()

    def init_ui(self):
        """初始化UI"""
        # 创建4个批量订单输入行
        for i in range(1, 5):
            order_layout = QHBoxLayout()
            order_layout.addWidget(QLabel(f"第{i}单:"))

            # 手数输入
            volume_input = QDoubleSpinBox()
            volume_input.setRange(0.01, 100)
            volume_input.setSingleStep(0.01)
            volume_input.setValue(BATCH_ORDER_DEFAULTS[f"order{i}"]["volume"])
            self.volume_inputs.append(volume_input)

            # 止损点数/K线个数
            sl_label = QLabel("止损点数:")
            self.sl_labels.append(sl_label)  # 保存标签引用以便后续修改

            sl_points_input = QSpinBox()
            sl_points_input.setRange(0, 100000)
            sl_points_input.setValue(BATCH_ORDER_DEFAULTS[f"order{i}"]["sl_points"])
            self.sl_points_inputs.append(sl_points_input)

            # K线回溯数量输入（初始隐藏）
            sl_candle_input = QSpinBox()
            sl_candle_input.setRange(1, 20)
            # 使用get方法获取sl_candle字段，如果不存在则使用CANDLE_LOOKBACK作为默认值
            sl_candle_input.setValue(
                BATCH_ORDER_DEFAULTS[f"order{i}"].get(
                    "sl_candle", SL_MODE["CANDLE_LOOKBACK"]
                )
            )
            sl_candle_input.setVisible(False)  # 初始隐藏
            self.sl_candle_inputs.append(sl_candle_input)

            # 止盈点数输入
            tp_points_input = QSpinBox()
            tp_points_input.setRange(0, 100000)
            tp_points_input.setValue(BATCH_ORDER_DEFAULTS[f"order{i}"]["tp_points"])
            self.tp_points_inputs.append(tp_points_input)

            order_layout.addWidget(QLabel("手数:"))
            order_layout.addWidget(volume_input)
            order_layout.addWidget(sl_label)
            order_layout.addWidget(sl_points_input)
            order_layout.addWidget(sl_candle_input)  # 添加控件但初始隐藏
            order_layout.addWidget(QLabel("止盈点数:"))
            order_layout.addWidget(tp_points_input)

            self.layout.addLayout(order_layout)

        # 检查当前的止损模式并更新UI
        self.update_sl_mode(SL_MODE["DEFAULT_MODE"])

    def update_sl_mode(self, mode):
        """
        更新止损模式

        Args:
            mode: 止损模式，'FIXED_POINTS'或'CANDLE_KEY_LEVEL'
        """
        # 根据止损模式更新标签和输入范围
        if mode == "FIXED_POINTS":  # 固定点数止损
            # 更新标签文本
            for label in self.sl_labels:
                label.setText("止损点数:")

            # 切换显示固定点数控件，隐藏K线回溯控件
            for i in range(len(self.sl_points_inputs)):
                self.sl_points_inputs[i].setVisible(True)
                self.sl_candle_inputs[i].setVisible(False)

            # 更新输入范围（针对点数）
            for sl_input in self.sl_points_inputs:
                sl_input.setRange(0, 100000)
                sl_input.setSingleStep(100)  # 以100点为步进
                # 使用默认值
                sl_input.setValue(BATCH_ORDER_DEFAULTS["order1"]["sl_points"])
        else:  # K线关键位止损
            # 更新标签文本
            for label in self.sl_labels:
                label.setText("K线回溯:")

            # 切换显示K线回溯控件，隐藏固定点数控件
            for i in range(len(self.sl_points_inputs)):
                self.sl_points_inputs[i].setVisible(False)
                self.sl_candle_inputs[i].setVisible(True)

            # 更新K线回溯输入范围
            for i, sl_input in enumerate(self.sl_candle_inputs):
                sl_input.setRange(1, 20)  # 最少1根K线，最多20根
                sl_input.setSingleStep(1)  # 以1为步进
                # 使用配置中的默认值
                order_key = f"order{i+1}"
                sl_input.setValue(
                    BATCH_ORDER_DEFAULTS[order_key].get(
                        "sl_candle", SL_MODE["CANDLE_LOOKBACK"]
                    )
                )

    def update_symbol_params(self, symbol_params):
        """
        更新交易品种参数

        Args:
            symbol_params: 交易品种参数字典
        """
        # 设置手数范围
        for volume_input in self.volume_inputs:
            volume_input.setRange(
                symbol_params["min_volume"], symbol_params["max_volume"]
            )
            volume_input.setSingleStep(symbol_params["volume_step"])

        # 根据止损模式设置止损范围
        sl_mode = SL_MODE["DEFAULT_MODE"]

        if sl_mode == "FIXED_POINTS":
            # 使用点数止损
            for sl_input in self.sl_points_inputs:
                sl_input.setRange(
                    symbol_params["min_sl_points"], symbol_params["max_sl_points"]
                )
        else:
            # 使用K线止损，范围已在update_sl_mode中设置
            pass

        # 设置止盈范围
        for tp_input in self.tp_points_inputs:
            tp_input.setRange(
                symbol_params["min_tp_points"], symbol_params["max_tp_points"]
            )

        # 设置默认值 (使用BATCH_ORDER_DEFAULTS)
        for i in range(4):
            order_key = f"order{i+1}"
            if order_key in BATCH_ORDER_DEFAULTS:
                self.volume_inputs[i].setValue(
                    BATCH_ORDER_DEFAULTS[order_key]["volume"]
                )
                if sl_mode == "FIXED_POINTS":
                    self.sl_points_inputs[i].setValue(
                        BATCH_ORDER_DEFAULTS[order_key]["sl_points"]
                    )
                else:
                    # K线止损模式
                    self.sl_candle_inputs[i].setValue(
                        BATCH_ORDER_DEFAULTS[order_key].get(
                            "sl_candle", SL_MODE["CANDLE_LOOKBACK"]
                        )
                    )

                self.tp_points_inputs[i].setValue(
                    BATCH_ORDER_DEFAULTS[order_key]["tp_points"]
                )


# 模块级函数，供其他模块调用
def update_sl_mode(mode):
    """
    更新止损模式，供外部模块调用

    Args:
        mode: 止损模式，'FIXED_POINTS'或'CANDLE_KEY_LEVEL'
    """
    global _instance
    if _instance:
        _instance.update_sl_mode(mode)


def update_symbol_params(symbol_params):
    """
    更新交易品种参数，供外部模块调用

    Args:
        symbol_params: 交易品种参数字典
    """
    global _instance
    if _instance:
        _instance.update_symbol_params(symbol_params)
