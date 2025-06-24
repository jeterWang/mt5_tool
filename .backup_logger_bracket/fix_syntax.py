#!/usr/bin/env python3
"""
修复语法错误的脚本
"""

import os
import ast
import logging
logger = logging.getLogger(__name__)

def fix_syntax_errors():
    """修复所有Python文件的语法错误"""
    
    files_to_check = [
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
    
    for file_path in files_to_check:
        if not os.path.exists(file_path):
            continue
            
        try:
            # 检查语法
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            try:
                ast.parse(content)
                logger.info(f"OK {file_path}: 语法正确"))
                continue
            except SyntaxError as e:
                logger.error(f"ERROR {file_path}: 语法错误在第{e.lineno}行: {e.msg}"))
                
                # 修复常见的语法错误
                lines = content.split('\n')
                modified = False
                
                for i, line in enumerate(lines):
                    # 检查if/else/except/try后面没有代码的情况
                    stripped = line.strip()
                    if (stripped.endswith(':') and 
                        any(stripped.startswith(keyword) for keyword in ['if ', 'else:', 'except ', 'try:', 'for ', 'while ', 'with ']) and
                        i + 1 < len(lines)):
                        
                        next_line = lines[i + 1].strip()
                        
                        # 如果下一行是注释或空行，或者缩进不对，添加pass
                        if (not next_line or 
                            next_line.startswith('#') or
                            (i + 2 < len(lines) and 
                             lines[i + 2].strip() and 
                             not lines[i + 2].startswith(' ' * (len(line) - len(line.lstrip()) + 4)))):
                            
                            # 在当前行后插入适当缩进的pass
                            indent = len(line) - len(line.lstrip()) + 4
                            lines.insert(i + 1, ' ' * indent + 'pass')
                            modified = True
                            break
                
                if modified:
                    new_content = '\n'.join(lines)
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    logger.info(f"  → 已修复: 添加了pass语句"))
                    
                    # 再次检查
                    try:
                        ast.parse(new_content)
                        logger.info(f"  → 修复成功!"))
                    except SyntaxError:
                        logger.error(f"  → 修复失败，需要手动处理"))
                
        except Exception as e:
            logger.error(f"ERROR 处理 {file_path} 失败: {e}"))

if __name__ == "__main__":
    logger.error("修复Python语法错误..."))
    logger.info("=" * 40))
    fix_syntax_errors()
    logger.info("\n修复完成!"))
