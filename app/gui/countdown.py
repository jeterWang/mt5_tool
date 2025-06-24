"""
K线倒计时显示模块

显示当前K线剩余时间，并提供声音提醒和窗口置顶功能
"""

import winsound
from datetime import datetime
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QComboBox, QCheckBox
from PyQt6.QtCore import Qt

from config.loader import DEFAULT_TIMEFRAME, GUI_SETTINGS
from app.trader.symbol_info import get_timeframe_constant


class CountdownSection:
    """K线倒计时区域"""

    def __init__(self):
        """初始化K线倒计时区域"""
        self.layout = QHBoxLayout()
        self.init_ui()

    def init_ui(self):
        """初始化UI"""
        # 添加K线周期选择
        self.timeframe_combo = QComboBox()
        self.timeframe_combo.addItems(["M1", "M5", "M15", "M30", "H1", "H4"])
        self.timeframe_combo.setCurrentText(DEFAULT_TIMEFRAME)
        self.timeframe_combo.currentTextChanged.connect(self.on_timeframe_changed)

        self.layout.addWidget(QLabel("K线周期:"))
        self.layout.addWidget(self.timeframe_combo)

        # 添加声音提醒选项
        self.sound_checkbox = QCheckBox("收盘提醒")
        self.sound_checkbox.setChecked(GUI_SETTINGS["SOUND_ALERT"])
        self.layout.addWidget(self.sound_checkbox)

        # 添加窗口置顶选项
        self.topmost_checkbox = QCheckBox("窗口置顶")
        self.topmost_checkbox.setChecked(GUI_SETTINGS["WINDOW_TOP"])
        self.layout.addWidget(self.topmost_checkbox)

        # 倒计时显示
        self.countdown_label = QLabel("距离K线收线还有: 00秒")
        self.countdown_label.setStyleSheet(
            "QLabel { color: red; font-size: 14px; font-weight: bold; }"
        )
        self.layout.addWidget(self.countdown_label)
        self.layout.addStretch()

    def on_timeframe_changed(self, timeframe: str):
        """
        当K线周期改变时重置倒计时

        Args:
            timeframe: 新选择的时间周期
        """
        # 实际刷新在下一次倒计时更新中完成
        pass

    def update_countdown(self, last_beep_time):
        """
        更新倒计时显示

        Args:
            last_beep_time: 上次声音提示的时间戳
        """
        try:
            current_time = datetime.now()
            timeframe = self.timeframe_combo.currentText()

            if timeframe == "M1":
                seconds_left = 60 - current_time.second
            elif timeframe == "M5":
                minutes_passed = current_time.minute % 5
                seconds_left = (4 - minutes_passed) * 60 + (60 - current_time.second)
            elif timeframe == "M15":
                minutes_passed = current_time.minute % 15
                seconds_left = (14 - minutes_passed) * 60 + (60 - current_time.second)
            elif timeframe == "M30":
                minutes_passed = current_time.minute % 30
                seconds_left = (29 - minutes_passed) * 60 + (60 - current_time.second)
            elif timeframe == "H1":
                minutes_passed = current_time.minute
                seconds_left = (59 - minutes_passed) * 60 + (60 - current_time.second)
            else:  # H4
                hours_passed = current_time.hour % 4
                minutes_passed = current_time.minute
                seconds_left = (
                    (3 - hours_passed) * 60 + (59 - minutes_passed)
                ) * 60 + (60 - current_time.second)

            # 转换为分钟和秒的显示
            minutes = seconds_left // 60
            seconds = seconds_left % 60

            if minutes > 0:
                self.countdown_label.setText(
                    f"距离{timeframe}收线还有: {minutes}分{seconds:02d}秒"
                )
            else:
                self.countdown_label.setText(
                    f"距离{timeframe}收线还有: {seconds:02d}秒"
                )

            # 当剩余30秒时改变颜色
            if seconds_left <= 30:
                self.countdown_label.setStyleSheet(
                    "QLabel { color: red; font-size: 14px; font-weight: bold; }"
                )
            else:
                self.countdown_label.setStyleSheet(
                    "QLabel { color: black; font-size: 14px; font-weight: bold; }"
                )

            # 声音提醒
            if (
                self.sound_checkbox.isChecked()
                and seconds_left <= GUI_SETTINGS["ALERT_SECONDS"]
            ):
                current_timestamp = current_time.timestamp()
                # 确保提示音间隔至少1秒
                if current_timestamp - last_beep_time >= 1:
                    freq = GUI_SETTINGS["BEEP_FREQUENCY"]
                    dur = GUI_SETTINGS["BEEP_DURATION"]
                    if not (37 <= freq <= 32767):
                        freq = 1000
                    if not (10 <= dur <= 10000):
                        dur = 200
                    winsound.Beep(freq, dur)
                    # 更新最近一次提示音时间
                    return current_timestamp

        except Exception as e:
            pass
            # print(f"更新倒计时出错：{str(e)}")

        return last_beep_time
