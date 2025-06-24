#!/usr/bin/env python3
"""
查找所有活跃的print语句
"""

import os
import re
import logging
logger = logging.getLogger(__name__)

def find_active_prints():
    """查找未被注释的print语句"""
    
    files_to_search = [
        "config/loader.py",
        "app/database.py", 
        "app/gui/account_info.py",
        "app/gui/config_manager.py",
        "app/gui/batch_order.py",
        "app/gui/main_window.py",
        "app/gui/trading_settings.py",
        "app/gui/pnl_info.py",
        "utils/paths.py"
    ]
    
    for file_path in files_to_search:
        if not os.path.exists(file_path):
            continue
            
        logger.info(f"\n=== {file_path} ===")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            # 查找未被注释的print语句
            if 'print(' in line and not stripped.startswith('#') and not stripped.startswith('//'):
                logger.info(f"第{i}行: {line.rstrip()}")

if __name__ == "__main__":
    find_active_prints()