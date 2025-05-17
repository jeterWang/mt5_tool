"""
MT5交易系统启动入口

运行此模块可启动MT5交易系统GUI界面
"""

import sys
from PyQt6.QtWidgets import QApplication
from app.gui import MT5GUI


def main():
    """启动应用程序"""
    app = QApplication(sys.argv)
    window = MT5GUI()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
