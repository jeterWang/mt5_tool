"""
MT5交易系统启动入口

运行此模块可启动MT5交易系统GUI界面
"""

import sys
import logging
logger = logging.getLogger(__name__)
import logging

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.StreamHandler(),
    ]
)
from PyQt6.QtWidgets import QApplication
from app.gui import MT5GUI


def main():
    """启动应用程序"""
    # 确保正确加载配置
    from config.loader import load_config, SYMBOLS

    logger.info(f"程序启动前SYMBOLS = {SYMBOLS}"))
    load_config()
    logger.info(f"程序启动后SYMBOLS = {SYMBOLS}"))

    app = QApplication(sys.argv)
    window = MT5GUI()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
