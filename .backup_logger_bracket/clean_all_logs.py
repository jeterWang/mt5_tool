#!/usr/bin/env python3
"""
彻底清理所有调试日志的脚本
"""

import os
import re
import logging
logger = logging.getLogger(__name__)
from pathlib import Path

def clean_all_debug_logs():
    """
    彻底清理系统中的所有调试日志
    """
    
    # 需要清理的关键词
    debug_keywords = [
        "开发环境:",
        "数据目录",
        "数据库路径",
        "数据库文件",
        "正在保存",
        "批量订单",
        "save_config:",
        "保存前",
        "保存后",
        "配置中的",
        "文件中的",
        "设置为:",
        "当前DAILY_TRADE_LIMIT",
        "BATCH_ORDER_DEFAULTS",
        "更新前SYMBOLS",
        "更新后SYMBOLS",
        "使用配置中的",
        "已将文件中的配置应用到内存",
        "手数保存成功",
        "固定亏损保存成功",
        "手数值不一致",
        "MT5GUI初始化",
        "config/loader.py模块被导入"
    ]
    
    # 需要处理的文件列表
    files_to_clean = [
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
    
    logger.info("开始彻底清理调试日志..."))
    
    total_cleaned = 0
    
    for file_path in files_to_clean:
        if not os.path.exists(file_path):
            logger.warning(f"警告: 文件不存在: {file_path}"))
            continue
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            modified_lines = []
            cleaned_count = 0
            
            for line_num, line in enumerate(lines):
                original_line = line
                
                # 检查是否包含调试信息
                should_comment = False
                if 'print(' in line:
                    for keyword in debug_keywords:
                        if keyword in line:
                            should_comment = True
                            break
                
                # 如果需要注释且还没有被注释
                if should_comment and not line.strip().startswith('#'):
                    # 保持原有缩进，添加注释
                    indent = len(line) - len(line.lstrip())
                    modified_lines.append(' ' * indent + '# ' + line.strip())
                    cleaned_count += 1
                else:
                    modified_lines.append(line)
            
            if cleaned_count > 0:
                new_content = '\n'.join(modified_lines)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                logger.info(f"已清理 {file_path}: 注释了 {cleaned_count} 行调试日志"))
                total_cleaned += cleaned_count
            else:
                logger.info(f"{file_path}: 无需清理"))
                
        except Exception as e:
            logger.error(f"错误: 处理文件失败 {file_path}: {e}"))
    
    logger.info(f"\n清理完成! 总共注释了 {total_cleaned} 行调试日志"))
    return total_cleaned

def create_ultra_clean_starter():
    """
    创建超级简洁的启动脚本
    """
    
    content = '''#!/usr/bin/env python3
"""
MT5交易系统 - 超级简洁启动
"""

import sys
import os
from contextlib import redirect_stdout, redirect_stderr
from io import StringIO

class QuietLogger:
    """静默日志捕获器"""
    def write(self, msg):
        # 只显示重要信息
        important_keywords = [
            "错误", "失败", "异常", "Error", "Exception", 
            "MT5交易系统", "启动完成", "交易界面"
        ]
        if any(keyword in str(msg) for keyword in important_keywords):
            sys.__stdout__.write(msg)
        
    def flush(self):
        pass

def ultra_clean_start():
    """超级简洁启动"""
    logger.info("MT5交易系统"))
    logger.info("━" * 30))
    
    try:
        # 重定向输出到静默日志
        quiet_logger = QuietLogger()
        
        with redirect_stdout(quiet_logger):
            from PyQt6.QtWidgets import QApplication
            from app.gui import MT5GUI
            from config.loader import load_config, SYMBOLS
            
            # 静默加载配置
            load_config()
            
        logger.info("[OK] 系统初始化完成"))
        logger.info(f"[OK] 交易品种: {', '.join(SYMBOLS)}"))
        logger.info("━" * 30))
        
        # 启动应用
        app = QApplication(sys.argv)
        window = MT5GUI()
        window.show()
        
        logger.info("交易界面已启动"))
        logger.info("按 Ctrl+C 或关闭窗口退出\n"))
        
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
'''
    
    with open('ultra_clean_start.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    logger.info("已创建超级简洁启动脚本: ultra_clean_start.py"))

if __name__ == "__main__":
    logger.info("MT5交易系统日志清理工具"))
    logger.info("=" * 50))
    
    # 执行清理
    cleaned_count = clean_all_debug_logs()
    
    # 创建超级简洁启动器
    create_ultra_clean_starter()
    
    logger.info("\n建议使用:"))
    logger.info("  uv run python ultra_clean_start.py"))
    logger.info("\n清理完成! 系统将更加简洁."))
