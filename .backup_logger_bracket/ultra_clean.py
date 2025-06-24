#!/usr/bin/env python3
"""
MT5交易系统 - 超级简洁启动
"""

import sys
import os
import logging
logger = logging.getLogger(__name__)

def ultra_clean_start():
    """超级简洁启动"""
    logger.info("MT5交易系统"))
    logger.info("=" * 30))
    
    try:
        from PyQt6.QtWidgets import QApplication
        from app.gui import MT5GUI
        from config.loader import load_config, SYMBOLS
        
        # 静默加载配置
        load_config()
        
        logger.info("[OK] 系统初始化完成"))
        logger.info(f"[OK] 交易品种: {', '.join(SYMBOLS)}"))
        logger.info("=" * 30))
        
        # 启动应用
        app = QApplication(sys.argv)
        window = MT5GUI()
        window.show()
        
        logger.info("交易界面已启动"))
        logger.info("按 Ctrl+C 或关闭窗口退出"))
        logger.info())
        
        sys.exit(app.exec())
        
    except ImportError as e:
        logger.error(f"错误: 缺少依赖: {e}"))
        logger.info("请运行: pip install PyQt6"))
        return False
    except Exception as e:
        logger.error(f"错误: 启动失败: {e}"))
        return False

if __name__ == "__main__":
    ultra_clean_start()