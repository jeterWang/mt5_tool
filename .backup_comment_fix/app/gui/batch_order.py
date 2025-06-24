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
from config.loader import BATCH_ORDER_DEFAULTS, SL_MODE, POSITION_SIZING, save_config
from PyQt6.QtGui import QIcon
import MetaTrader5 as mt5


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
        )  # 每个元素是dict: {volume, sl_points, tp_points, sl_candle, fixed_loss, checked}
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
                    "fixed_loss": BATCH_ORDER_DEFAULTS[key].get(
                        "fixed_loss", POSITION_SIZING["DEFAULT_FIXED_LOSS"]
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
                    "fixed_loss": POSITION_SIZING["DEFAULT_FIXED_LOSS"],
                    "checked": True,
                }
            )
        self.refresh_orders_ui()
        self.update_sl_mode(SL_MODE["DEFAULT_MODE"])
        self.update_position_sizing_mode(POSITION_SIZING["DEFAULT_MODE"])

    def refresh_orders_ui(self):
        # 清除原有行
        for row in self.order_rows:
            pass
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
            check.stateChanged.connect(self.make_checked_slot(idx))
            # 如果需要禁用勾选框的逻辑在此处（如根据某些条件）
            # 例如：if not order['可用']: check.setEnabled(False); order["checked"] = False
            # 这里假设有禁用逻辑，演示如下：
            if not check.isEnabled():
                order["checked"] = False
            row_layout.addWidget(check)

            # 标签
            row_layout.addWidget(QLabel(f"第{idx+1}单:"))

            # 手数/固定亏损（根据模式显示）
            volume_label = QLabel("手数:")
            row_layout.addWidget(volume_label)
            volume_input = QDoubleSpinBox()
            volume_input.setRange(0.01, 100)
            volume_input.setSingleStep(0.01)
            volume_input.setValue(order["volume"])
            volume_input.valueChanged.connect(
                lambda val, i=idx: self.on_value_changed(i, "volume", val)
            )
            row_layout.addWidget(volume_input)

            # 固定亏损输入框
            fixed_loss_label = QLabel("亏损($):")
            row_layout.addWidget(fixed_loss_label)
            fixed_loss_input = QDoubleSpinBox()
            fixed_loss_input.setRange(1.0, 10000.0)
            fixed_loss_input.setSingleStep(1.0)
            fixed_loss_input.setValue(order["fixed_loss"])
            fixed_loss_input.valueChanged.connect(
                lambda val, i=idx: self.on_value_changed(i, "fixed_loss", val)
            )
            row_layout.addWidget(fixed_loss_input)

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
                    "volume_label": volume_label,
                    "volume": volume_input,
                    "fixed_loss_label": fixed_loss_label,
                    "fixed_loss": fixed_loss_input,
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
                "fixed_loss": POSITION_SIZING["DEFAULT_FIXED_LOSS"],
                "checked": True,
            }
        )
        self.refresh_orders_ui()
        # 重新应用当前模式设置
        self.update_sl_mode(SL_MODE["DEFAULT_MODE"])
        self.update_position_sizing_mode(POSITION_SIZING["DEFAULT_MODE"])
        self.save_batch_settings()

    def delete_order(self, idx):
        if len(self.orders) <= 1:
            return
        self.orders.pop(idx)
        self.refresh_orders_ui()
        # 重新应用当前模式设置
        self.update_sl_mode(SL_MODE["DEFAULT_MODE"])
        self.update_position_sizing_mode(POSITION_SIZING["DEFAULT_MODE"])
        self.save_batch_settings()

    def on_checked_changed(self, idx, state):
        self.orders[idx]["checked"] = state == Qt.CheckState.Checked.value
        self.save_batch_settings()

    def on_value_changed(self, idx, key, value):
        self.orders[idx][key] = value
        # 固定亏损模式下，手数在下单时计算，这里不预先计算
        # 盈亏平衡批量加仓时，参数变动后可在界面上提示用户"手数将在下单时自动计算"
        self.save_batch_settings()

    def calculate_position_size_for_order(
        self, order_idx, order_type, entry_price, symbol
    ):
        """
        为具体订单计算仓位大小（在下单时调用）

        Args:
            order_idx: 订单索引
            order_type: 交易类型 ('buy' 或 'sell')
            entry_price: 入场价格
            symbol: 交易品种

        Returns:
            计算出的仓位大小（手数）
        """
        try:
            import MetaTrader5 as mt5

            order = self.orders[order_idx]
            fixed_loss = order["fixed_loss"]

            symbol_info = mt5.symbol_info(symbol)
            if not symbol_info:
                return 0

            point = symbol_info.point

            # 根据交易方向和止损模式计算止损价格
            sl_mode = SL_MODE["DEFAULT_MODE"]
            sl_price = 0

            if sl_mode == "FIXED_POINTS":
                sl_points = order["sl_points"]
                if sl_points > 0:
                    if order_type == "buy":
                        # 买入订单，止损在入场价下方
                        sl_price = entry_price - sl_points * point
                    else:  # sell
                        # 卖出订单，止损在入场价上方
                        sl_price = entry_price + sl_points * point
            else:
                # K线关键位模式，需要获取K线数据
                from app.gui.main_window import get_current_trader_and_window

                trader, gui_window = get_current_trader_and_window()

                if gui_window:
                    countdown = gui_window.components.get("countdown")
                    if countdown:
                        timeframe = countdown.timeframe_combo.currentText()
                        lookback = order["sl_candle"]
                        timeframe_mt5 = self.get_timeframe(timeframe)
                        rates = mt5.copy_rates_from_pos(
                            symbol, timeframe_mt5, 0, lookback + 2
                        )
                        if rates is not None and len(rates) >= lookback + 2:
                            lowest_point = min([rate["low"] for rate in rates[2:]])
                            highest_point = max([rate["high"] for rate in rates[2:]])
                            # 添加偏移
                            from config.loader import BREAKOUT_SETTINGS

                            sl_offset = BREAKOUT_SETTINGS["SL_OFFSET_POINTS"] * point

                            if order_type == "buy":
                                sl_price = lowest_point - sl_offset
                            else:  # sell
                                sl_price = highest_point + sl_offset

            if sl_price <= 0:
                return 0

            # 验证止损价格的合理性
            if order_type == "buy" and sl_price >= entry_price:
                # print(
                    f"买入订单止损价格{sl_price}高于入场价格{entry_price}，无法计算仓位"
                )
                return 0
            elif order_type == "sell" and sl_price <= entry_price:
                # print(
                    f"卖出订单止损价格{sl_price}低于入场价格{entry_price}，无法计算仓位"
                )
                return 0

            # 计算价格差距（风险金额）
            price_diff = abs(entry_price - sl_price)

            # 获取合约大小
            contract_size = symbol_info.trade_contract_size

            # 计算仓位大小
            # 公式：仓位大小 = 固定亏损金额 / (价格差距 * 合约大小)
            position_size = fixed_loss / (price_diff * contract_size)

            # 确保符合品种的最小/最大手数要求
            min_volume = symbol_info.volume_min
            max_volume = symbol_info.volume_max
            volume_step = symbol_info.volume_step

            # 调整到最接近的有效手数
            position_size = max(min_volume, min(max_volume, position_size))
            position_size = round(position_size / volume_step) * volume_step

            # print(
                f"固定亏损计算: {order_type}单, 入场价{entry_price}, 止损价{sl_price}, 风险金额{price_diff}, 计算手数{position_size}"
            )

            return position_size

        except Exception as e:
            # print(f"计算仓位大小出错: {str(e)}")
            return 0

    def calculate_position_size(self, order_idx):
        """
        旧方法，保留用于向后兼容，但不再使用
        """
        return 0

    def get_timeframe(self, timeframe: str) -> int:
        """将时间周期字符串转换为MT5的时间周期常量"""
        timeframe_map = {
            "M1": mt5.TIMEFRAME_M1,
            "M5": mt5.TIMEFRAME_M5,
            "M15": mt5.TIMEFRAME_M15,
            "M30": mt5.TIMEFRAME_M30,
            "H1": mt5.TIMEFRAME_H1,
            "H4": mt5.TIMEFRAME_H4,
        }
        return timeframe_map.get(timeframe, mt5.TIMEFRAME_M1)

    def save_batch_settings(self):
        """实时保存批量订单设置"""
        try:
            # print("正在保存批量订单设置...")
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
                    "fixed_loss": order["fixed_loss"],
                    "checked": order["checked"],
                }
                # print(
                #     f"批量订单{valid_count+1}设置: 手数={order['volume']}, "
                #     f"止损点数={order['sl_points']}, "
                #     f"止盈点数={order['tp_points']}, "
                #     f"K线回溯={order['sl_candle']}, "
                #     f"固定亏损={order['fixed_loss']}"
                # )
                valid_count += 1
            # 清理多余的orderN
            for i in range(valid_count + 1, self.MAX_ORDERS + 1):
                BATCH_ORDER_DEFAULTS.pop(f"order{i}", None)

            # 保存配置到文件
            result = save_config()
            if result:
                # print("批量订单设置已成功保存")
                from config.loader import (
                    load_config,
                    BATCH_ORDER_DEFAULTS as updated_defaults,
                )

                load_config()
                for i in range(valid_count):
                    order_key = f"order{i+1}"

                    # 验证所有字段是否正确保存
                    expected_volume = self.orders[i]["volume"]
                    actual_volume = updated_defaults[order_key].get("volume")
                    if abs(expected_volume - actual_volume) > 0.001:
                        # print(
                        #     f"警告: {order_key}手数值不一致, UI:{expected_volume}, 内存:{actual_volume}"
                        # )
                        self.orders[i]["volume"] = actual_volume
                    else:
                        # print(f"{order_key}手数保存成功: {actual_volume}")
                        pass

                    # 验证fixed_loss字段
                    expected_fixed_loss = self.orders[i]["fixed_loss"]
                    actual_fixed_loss = updated_defaults[order_key].get("fixed_loss")
                    if abs(expected_fixed_loss - actual_fixed_loss) > 0.001:
                        # print(
                        #     f"警告: {order_key}固定亏损值不一致, UI:{expected_fixed_loss}, 内存:{actual_fixed_loss}"
                        # )
                        self.orders[i]["fixed_loss"] = actual_fixed_loss
                    else:
                        # print(f"{order_key}固定亏损保存成功: {actual_fixed_loss}")
                        pass

                    # 验证其他关键字段
                    self.orders[i]["sl_points"] = updated_defaults[order_key].get(
                        "sl_points", self.orders[i]["sl_points"]
                    )
                    self.orders[i]["tp_points"] = updated_defaults[order_key].get(
                        "tp_points", self.orders[i]["tp_points"]
                    )
                    self.orders[i]["sl_candle"] = updated_defaults[order_key].get(
                        "sl_candle", self.orders[i]["sl_candle"]
                    )
                    self.orders[i]["checked"] = updated_defaults[order_key].get(
                        "checked", self.orders[i]["checked"]
                    )
            else:
                pass
                # print("批量订单设置保存失败")
            return result
        except Exception as e:
            # print(f"保存批量订单设置失败: {e}")
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

    def update_position_sizing_mode(self, mode):
        """
        更新仓位计算模式

        Args:
            mode: 仓位计算模式，'MANUAL'或'FIXED_LOSS'
        """
        # 根据仓位计算模式切换显示
        for row in self.order_rows:
            if mode == "MANUAL":
                row["volume_label"].setText("手数:")
                row["volume"].setVisible(True)
                row["volume"].setEnabled(True)
                row["volume"].setSuffix("")  # 清除后缀
                row["fixed_loss_label"].setVisible(False)
                row["fixed_loss"].setVisible(False)
            else:  # FIXED_LOSS
                row["volume_label"].setText("计算手数:")
                row["volume"].setVisible(True)
                row["volume"].setEnabled(False)  # 禁用手动编辑
                row["volume"].setValue(0.0)  # 设置为0，表示待计算
                row["volume"].setSuffix(" (下单时自动计算)")  # 添加后缀说明
                row["fixed_loss_label"].setVisible(True)
                row["fixed_loss"].setVisible(True)

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

    def make_checked_slot(self, idx):
        def slot(state):
            self.on_checked_changed(idx, state)

        return slot

    def sync_checked_from_ui(self):
        for idx, row in enumerate(self.order_rows):
            self.orders[idx]["checked"] = row["check"].isChecked()


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


def update_position_sizing_mode(mode):
    """
    更新仓位计算模式，供外部模块调用

    Args:
        mode: 仓位计算模式，'MANUAL'或'FIXED_LOSS'
    """
    global _instance
    if _instance:
        _instance.update_position_sizing_mode(mode)


def update_symbol_params(symbol_params):
    """
    更新交易品种参数，供外部模块调用

    Args:
        symbol_params: 交易品种参数字典
    """
    global _instance
    if _instance:
        _instance.update_symbol_params(symbol_params)
