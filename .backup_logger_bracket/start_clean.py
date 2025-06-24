#!/usr/bin/env python3
"""
MT5交易系统清洁启动脚本

提供一个无冗余日志的启动方式
"""

import sys
import os
import logging
logger = logging.getLogger(__name__)
from contextlib import redirect_stdout, redirect_stderr
from io import StringIO

def start_clean():
    """启动MT5交易系统，过滤不必要的日志输出"""
    
    logger.info("启动MT5交易系统..."))
    logger.info("=" * 50))
    logger.info("正在初始化系统组件..."))
    
    # 导入主模块
    try:
        from PyQt6.QtWidgets import QApplication
        from app.gui import MT5GUI
        from config.loader import load_config, SYMBOLS
        
        # 加载配置（静默）
        load_config()
        
        logger.info(f"[OK] 配置已加载"))
        logger.info(f"[OK] 交易品种: {', '.join(SYMBOLS)}"))
        logger.info(f"[OK] GUI系统已就绪"))
        logger.info("=" * 50))
        logger.info("启动完成! 正在显示交易界面..."))
        logger.info())
        
        # 启动应用
        app = QApplication(sys.argv)
        window = MT5GUI()
        window.show()
        
        # 只显示关键信息
        logger.info("MT5交易系统已启动"))
        logger.info("交易界面已显示"))
        logger.info("系统监控中..."))
        logger.info("\n按 Ctrl+C 或关闭窗口退出"))
        
        sys.exit(app.exec())
        
    except ImportError as e:
        logger.error(f"错误: 缺少必要依赖: {e}"))
        logger.info("请运行: pip install PyQt6"))
        return False
    except Exception as e:
        logger.error(f"错误: 启动失败: {e}"))
        return False

def start_verbose():
    """启动MT5交易系统，显示所有日志"""
    logger.info("详细模式启动MT5交易系统..."))
    logger.info("=" * 50))
    
    # 直接调用原始main函数
    try:
        from main import main
        main()
    except Exception as e:
        logger.error(f"错误: 启动失败: {e}"))
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1].lower() in ['verbose', 'debug', '-v', '--verbose']:
        start_verbose()
    else:
        start_clean()