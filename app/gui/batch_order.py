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
    QCheckBox,
    QPushButton,
    QWidget,
)
from PyQt6.QtCore import Qt
from config.loader import BATCH_ORDER_DEFAULTS, SL_MODE, save_config
from PyQt6.QtGui import QIcon


# 全局变量，用于存储当前实例
_instance = None


class BatchOrderSection:
    """批量下单设置区域"""

    MAX_ORDERS = 10

    def __init__(self):
        """初始化批量下单设置区域"""
        global _instance
        _instance = self

        self.group_box = QGroupBox("批量下单设置")
        self.layout = QVBoxLayout()
        self.group_box.setLayout(self.layout)

        # 订单数据结构
        self.orders = (
            []
        )  # 每个元素是dict: {volume, sl_points, tp_points, sl_candle, checked}
        self.order_rows = []  # 每行控件的引用，便于删除

        # 添加新单按钮
        self.add_btn = QPushButton()
        self.add_btn.setIcon(QIcon.fromTheme("list-add"))  # 使用系统加号图标
        self.add_btn.setText("")
        self.add_btn.setFixedSize(32, 32)
        self.add_btn.setStyleSheet(
            "QPushButton { background-color: #27ae60; color: white; border-radius: 16px; font-size: 20px; } QPushButton:hover { background-color: #2ecc71; }"
        )
        self.add_btn.clicked.connect(self.add_order)
        btn_layout = QHBoxLayout()
        btn_layout.addStretch(1)
        btn_layout.addWidget(self.add_btn)
        self.layout.addLayout(btn_layout)

        # 初始化订单（从BATCH_ORDER_DEFAULTS加载所有已保存的单子，最多10单）
        for i in range(1, self.MAX_ORDERS + 1):
            key = f"order{i}"
            if key in BATCH_ORDER_DEFAULTS:
                order = {
                    "volume": BATCH_ORDER_DEFAULTS[key].get("volume", 0.01),
                    "sl_points": BATCH_ORDER_DEFAULTS[key].get("sl_points", 0),
                    "tp_points": BATCH_ORDER_DEFAULTS[key].get("tp_points", 0),
                    "sl_candle": BATCH_ORDER_DEFAULTS[key].get(
                        "sl_candle", SL_MODE["CANDLE_LOOKBACK"]
                    ),
                    "checked": BATCH_ORDER_DEFAULTS[key].get("checked", True),
                }
                self.orders.append(order)
        # 如果没有任何订单，至少加一个默认单
        if not self.orders:
            self.orders.append(
                {
                    "volume": 0.01,
                    "sl_points": 0,
                    "tp_points": 0,
                    "sl_candle": SL_MODE["CANDLE_LOOKBACK"],
                    "checked": True,
                }
            )
        self.refresh_orders_ui()
        self.update_sl_mode(SL_MODE["DEFAULT_MODE"])

    def refresh_orders_ui(self):
        # 清除原有行
        for row in self.order_rows:
            row["widget"].setParent(None)
        self.order_rows.clear()

        # 逐行添加
        for idx, order in enumerate(self.orders):
            row_widget = QWidget()
            row_layout = QHBoxLayout(row_widget)
            row_layout.setContentsMargins(0, 0, 0, 0)

            # 勾选框
            check = QCheckBox()
            check.setChecked(order["checked"])
            check.stateChanged.connect(
                lambda state, i=idx: self.on_checked_changed(i, state)
            )
            row_layout.addWidget(check)

            # 标签
            row_layout.addWidget(QLabel(f"第{idx+1}单:"))

            # 手数
            volume_input = QDoubleSpinBox()
            volume_input.setRange(0.01, 100)
            volume_input.setSingleStep(0.01)
            volume_input.setValue(order["volume"])
            volume_input.valueChanged.connect(
                lambda val, i=idx: self.on_value_changed(i, "volume", val)
            )
            row_layout.addWidget(QLabel("手数:"))
            row_layout.addWidget(volume_input)

            # 止损点数/K线回溯
            sl_label = QLabel("止损点数:")
            row_layout.addWidget(sl_label)
            sl_points_input = QSpinBox()
            sl_points_input.setRange(0, 100000)
            sl_points_input.setValue(order["sl_points"])
            sl_points_input.valueChanged.connect(
                lambda val, i=idx: self.on_value_changed(i, "sl_points", val)
            )
            row_layout.addWidget(sl_points_input)

            sl_candle_input = QSpinBox()
            sl_candle_input.setRange(1, 20)
            sl_candle_input.setValue(order["sl_candle"])
            sl_candle_input.valueChanged.connect(
                lambda val, i=idx: self.on_value_changed(i, "sl_candle", val)
            )
            sl_candle_input.setVisible(False)
            row_layout.addWidget(sl_candle_input)

            # 止盈点数
            row_layout.addWidget(QLabel("止盈点数:"))
            tp_points_input = QSpinBox()
            tp_points_input.setRange(0, 100000)
            tp_points_input.setValue(order["tp_points"])
            tp_points_input.valueChanged.connect(
                lambda val, i=idx: self.on_value_changed(i, "tp_points", val)
            )
            row_layout.addWidget(tp_points_input)

            # 删除按钮
            del_btn = QPushButton("删除")
            del_btn.setStyleSheet(
                "QPushButton { background-color: #e74c3c; color: white; font-weight: bold; border: none; } QPushButton:hover { background-color: #c0392b; color: white; border: none; }"
            )
            del_btn.clicked.connect(lambda _, i=idx: self.delete_order(i))
            row_layout.addWidget(del_btn)

            self.layout.addWidget(row_widget)
            self.order_rows.append(
                {
                    "widget": row_widget,
                    "check": check,
                    "volume": volume_input,
                    "sl_label": sl_label,
                    "sl_points": sl_points_input,
                    "sl_candle": sl_candle_input,
                    "tp_points": tp_points_input,
                    "del_btn": del_btn,
                }
            )

    def add_order(self):
        if len(self.orders) >= self.MAX_ORDERS:
            return
        self.orders.append(
            {
                "volume": 0.01,
                "sl_points": 0,
                "tp_points": 0,
                "sl_candle": SL_MODE["CANDLE_LOOKBACK"],
                "checked": True,
            }
        )
        self.refresh_orders_ui()
        self.save_batch_settings()

    def delete_order(self, idx):
        if len(self.orders) <= 1:
            return
        self.orders.pop(idx)
        self.refresh_orders_ui()
        self.save_batch_settings()

    def on_checked_changed(self, idx, state):
        self.orders[idx]["checked"] = state == Qt.CheckState.Checked.value
        self.save_batch_settings()

    def on_value_changed(self, idx, key, value):
        self.orders[idx][key] = value
        self.save_batch_settings()

    def save_batch_settings(self):
        """实时保存批量订单设置"""
        try:
            print("正在保存批量订单设置...")
            # 只保存volume>0的订单
            valid_count = 0
            for i, order in enumerate(self.orders[: self.MAX_ORDERS]):
                if order["volume"] <= 0:
                    continue  # 跳过空单
                order_key = f"order{valid_count+1}"
                BATCH_ORDER_DEFAULTS[order_key] = {
                    "volume": order["volume"],
                    "sl_points": order["sl_points"],
                    "tp_points": order["tp_points"],
                    "sl_candle": order["sl_candle"],
                    "checked": order["checked"],
                }
                print(
                    f"批量订单{valid_count+1}设置: 手数={order['volume']}, "
                    f"止损点数={order['sl_points']}, "
                    f"止盈点数={order['tp_points']}, "
                    f"K线回溯={order['sl_candle']}"
                )
                valid_count += 1
            # 清理多余的orderN
            for i in range(valid_count + 1, self.MAX_ORDERS + 1):
                BATCH_ORDER_DEFAULTS.pop(f"order{i}", None)

            # 保存配置到文件
            result = save_config()
            if result:
                print("批量订单设置已成功保存")
                from config.loader import (
                    load_config,
                    BATCH_ORDER_DEFAULTS as updated_defaults,
                )

                load_config()
                for i in range(valid_count):
                    order_key = f"order{i+1}"
                    expected_volume = self.orders[i]["volume"]
                    actual_volume = updated_defaults[order_key].get("volume")
                    if abs(expected_volume - actual_volume) > 0.001:
                        print(
                            f"警告: {order_key}手数值不一致, UI:{expected_volume}, 内存:{actual_volume}"
                        )
                        self.orders[i]["volume"] = actual_volume
                    else:
                        print(f"{order_key}手数保存成功: {actual_volume}")
            else:
                print("批量订单设置保存失败")
            return result
        except Exception as e:
            print(f"保存批量订单设置失败: {e}")
            return False

    def update_sl_mode(self, mode):
        """
        更新止损模式

        Args:
            mode: 止损模式，'FIXED_POINTS'或'CANDLE_KEY_LEVEL'
        """
        # 根据止损模式切换显示
        for row in self.order_rows:
            if mode == "FIXED_POINTS":
                row["sl_label"].setText("止损点数:")
                row["sl_points"].setVisible(True)
                row["sl_candle"].setVisible(False)
            else:
                row["sl_label"].setText("K线回溯:")
                row["sl_points"].setVisible(False)
                row["sl_candle"].setVisible(True)

    def update_symbol_params(self, symbol_params):
        """
        更新交易品种参数

        Args:
            symbol_params: 交易品种参数字典
        """
        # 更新每行输入控件的范围
        for row in self.order_rows:
            row["volume"].setRange(
                symbol_params["min_volume"], symbol_params["max_volume"]
            )
            row["volume"].setSingleStep(symbol_params["volume_step"])
            row["sl_points"].setRange(
                symbol_params["min_sl_points"], symbol_params["max_sl_points"]
            )
            row["tp_points"].setRange(
                symbol_params["min_tp_points"], symbol_params["max_tp_points"]
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
