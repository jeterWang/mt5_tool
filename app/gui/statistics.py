from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QTabWidget,
    QLabel,
    QPushButton,
    QDateEdit,
    QComboBox,
    QWidget,
    QDoubleSpinBox,
)
from PyQt6.QtCore import Qt, QDate, QTimer
from app.utils.statistics_utils import get_win_rate_statistics
from app.orm_models import TradeHistory
from sqlalchemy.orm import sessionmaker
from app.database import TradeDatabase
from app.config.config_manager import config_manager


class StatisticsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("盈利率统计")
        self.resize(400, 380)
        layout = QVBoxLayout(self)
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        self.init_winrate_tab()
        self.query_statistics()  # 弹窗初始化时自动查表

    def init_winrate_tab(self):
        tab = QWidget()
        tab_layout = QVBoxLayout(tab)

        # 读取config
        settings = config_manager.get_statistics_settings()
        # 日期选择器
        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel("起始日期:"))
        self.start_date_edit = QDateEdit()
        self.start_date_edit.setCalendarPopup(True)
        start_date = QDate.fromString(
            settings.get("start_date", "2000-01-01"), "yyyy-MM-dd"
        )
        self.start_date_edit.setDate(start_date)
        date_layout.addWidget(self.start_date_edit)
        date_layout.addWidget(QLabel("结束日期:"))
        self.end_date_edit = QDateEdit()
        self.end_date_edit.setCalendarPopup(True)
        end_date = QDate.fromString(
            settings.get("end_date", "2025-12-31"), "yyyy-MM-dd"
        )
        self.end_date_edit.setDate(end_date)
        date_layout.addWidget(self.end_date_edit)
        tab_layout.addLayout(date_layout)

        # 账户下拉框（支持全部）
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("账户:"))
        self.account_combo = QComboBox()
        self.account_combo.setEnabled(True)
        self.load_accounts(settings.get("account", ""))
        filter_layout.addWidget(self.account_combo)
        filter_layout.addWidget(QLabel("品种:"))
        self.symbol_combo = QComboBox()
        self.symbol_combo.setEnabled(False)
        filter_layout.addWidget(self.symbol_combo)
        tab_layout.addLayout(filter_layout)

        # 目标设置区
        target_layout = QHBoxLayout()
        target_layout.addWidget(QLabel("日目标%:"))
        self.day_target_spin = QDoubleSpinBox()
        self.day_target_spin.setRange(0, 100)
        self.day_target_spin.setDecimals(2)
        self.day_target_spin.setSingleStep(0.01)
        self.day_target_spin.setValue(settings.get("day_target", 0.3) * 100)
        target_layout.addWidget(self.day_target_spin)
        target_layout.addWidget(QLabel("周目标%:"))
        self.week_target_spin = QDoubleSpinBox()
        self.week_target_spin.setRange(0, 100)
        self.week_target_spin.setDecimals(2)
        self.week_target_spin.setSingleStep(0.01)
        self.week_target_spin.setValue(settings.get("week_target", 0.5) * 100)
        target_layout.addWidget(self.week_target_spin)
        target_layout.addWidget(QLabel("月目标%:"))
        self.month_target_spin = QDoubleSpinBox()
        self.month_target_spin.setRange(0, 100)
        self.month_target_spin.setDecimals(2)
        self.month_target_spin.setSingleStep(0.01)
        self.month_target_spin.setValue(settings.get("month_target", 0.6) * 100)
        target_layout.addWidget(self.month_target_spin)
        self.save_btn = QPushButton("保存设置")
        self.save_btn.clicked.connect(self.save_settings)
        target_layout.addWidget(self.save_btn)
        tab_layout.addLayout(target_layout)

        # 查询按钮
        self.query_btn = QPushButton("查询")
        self.query_btn.clicked.connect(self.query_statistics)
        tab_layout.addWidget(self.query_btn)

        # 盈利率展示
        self.day_label = QLabel("日盈利率：--%")
        self.week_label = QLabel("周盈利率：--%")
        self.month_label = QLabel("月盈利率：--%")
        for lbl in [self.day_label, self.week_label, self.month_label]:
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setStyleSheet("font-size: 18px; font-weight: bold;")
            tab_layout.addWidget(lbl)
        tab_layout.addStretch()

        self.tab_widget.addTab(tab, "盈利率统计")

    def load_accounts(self, selected_account):
        db = TradeDatabase()
        Session = sessionmaker(bind=db.engine)
        session = Session()
        try:
            accounts = session.query(TradeHistory.account).distinct().all()
            account_list = [a[0] for a in accounts if a[0]]
            account_list = sorted(set(account_list))
            self.account_combo.clear()
            self.account_combo.addItem("全部")
            self.account_combo.addItems(account_list)
            # 恢复选中项
            if selected_account and selected_account in account_list:
                self.account_combo.setCurrentText(selected_account)
            else:
                self.account_combo.setCurrentIndex(0)
        except Exception as e:
            self.account_combo.clear()
            self.account_combo.addItem("全部")
        finally:
            session.close()

    def save_settings(self):
        account = self.account_combo.currentText()
        if account == "全部":
            account = ""
        settings = {
            "start_date": self.start_date_edit.date().toString("yyyy-MM-dd"),
            "end_date": self.end_date_edit.date().toString("yyyy-MM-dd"),
            "account": account,
            "symbol": "",  # 预留
            "day_target": self.day_target_spin.value() / 100,
            "week_target": self.week_target_spin.value() / 100,
            "month_target": self.month_target_spin.value() / 100,
        }
        config_manager.set_statistics_settings(settings)
        self.save_btn.setText("已保存")
        self.save_btn.setEnabled(False)
        QTimer.singleShot(
            1500,
            lambda: (self.save_btn.setText("保存设置"), self.save_btn.setEnabled(True)),
        )

    def query_statistics(self):
        # 获取参数
        start_date = self.start_date_edit.date().toPyDate()
        end_date = self.end_date_edit.date().toPyDate()
        account = self.account_combo.currentText()
        if account == "全部":
            account = ""
        # 账户、品种后续可加
        db = TradeDatabase()
        Session = sessionmaker(bind=db.engine)
        session = Session()
        try:
            stats = get_win_rate_statistics(
                session, start_date, end_date, account=account
            )
            # 读取目标
            day_target = self.day_target_spin.value() / 100
            week_target = self.week_target_spin.value() / 100
            month_target = self.month_target_spin.value() / 100
            # 日
            day_val = stats["day_win_rate"]
            self.day_label.setText(f"日盈利率：{day_val*100:.2f}%")
            if day_val >= day_target:
                self.day_label.setStyleSheet(
                    "font-size: 18px; font-weight: bold; color: #27ae60;"
                )
            else:
                self.day_label.setStyleSheet(
                    "font-size: 18px; font-weight: bold; color: #e74c3c;"
                )
            # 周
            week_val = stats["week_win_rate"]
            self.week_label.setText(f"周盈利率：{week_val*100:.2f}%")
            if week_val >= week_target:
                self.week_label.setStyleSheet(
                    "font-size: 18px; font-weight: bold; color: #27ae60;"
                )
            else:
                self.week_label.setStyleSheet(
                    "font-size: 18px; font-weight: bold; color: #e74c3c;"
                )
            # 月
            month_val = stats["month_win_rate"]
            self.month_label.setText(f"月盈利率：{month_val*100:.2f}%")
            if month_val >= month_target:
                self.month_label.setStyleSheet(
                    "font-size: 18px; font-weight: bold; color: #27ae60;"
                )
            else:
                self.month_label.setStyleSheet(
                    "font-size: 18px; font-weight: bold; color: #e74c3c;"
                )
        except Exception as e:
            self.day_label.setText("日盈利率：--%")
            self.week_label.setText("周盈利率：--%")
            self.month_label.setText("月盈利率：--%")
            for lbl in [self.day_label, self.week_label, self.month_label]:
                lbl.setStyleSheet("font-size: 18px; font-weight: bold; color: gray;")
        finally:
            session.close()
