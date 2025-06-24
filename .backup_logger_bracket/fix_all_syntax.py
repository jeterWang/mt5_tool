#!/usr/bin/env python3
"""
一次性修复所有语法错误
"""

import os
import re
import logging
logger = logging.getLogger(__name__)

def fix_empty_blocks(file_path):
    """修复空代码块"""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    modified = False
    
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        
        # 检查是否是需要代码块的语句
        if (stripped.endswith(':') and 
            any(stripped.startswith(keyword) for keyword in 
                ['if ', 'elif ', 'else:', 'except ', 'try:', 'for ', 'while ', 'with ', 'def ', 'class '])):
            
            # 检查下一行
            next_i = i + 1
            needs_pass = True
            
            # 跳过空行和注释找到下一个有意义的行
            while next_i < len(lines):
                next_line = lines[next_i].strip()
                if not next_line or next_line.startswith('#'):
                    next_i += 1
                    continue
                    
                # 检查缩进是否正确
                if lines[next_i].startswith(' '):
                    expected_indent = len(line) - len(line.lstrip()) + 4
                    actual_indent = len(lines[next_i]) - len(lines[next_i].lstrip())
                    if actual_indent >= expected_indent:
                        needs_pass = False
                break
            
            # 如果需要pass，在合适位置插入
            if needs_pass:
                indent = len(line) - len(line.lstrip()) + 4
                lines.insert(i + 1, ' ' * indent + 'pass')
                modified = True
                i += 1  # 跳过新插入的行
        
        i += 1
    
    if modified:
        new_content = '\n'.join(lines)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True
    return False

def main():
    files_to_fix = [
        "app/gui/batch_order.py",
        "app/gui/account_info.py",
        "config/loader.py",
        "app/database.py",
        "app/gui/config_manager.py",
        "app/gui/main_window.py"
    ]
    
    logger.error("修复语法错误..."))
    
    for file_path in files_to_fix:
        if not os.path.exists(file_path):
            continue
            
        logger.info(f"处理 {file_path}..."))
        
        # 尝试修复
        if fix_empty_blocks(file_path):
            logger.info(f"  -> 已修复空代码块"))
        
        # 验证语法
        try:
            import ast
            with open(file_path, 'r', encoding='utf-8') as f:
                ast.parse(f.read())
            logger.info(f"  -> 语法正确"))
        except SyntaxError as e:
            logger.error(f"  -> 仍有语法错误: 第{e.lineno}行: {e.msg}"))
    
    logger.info("完成!"))

if __name__ == "__main__":
    main()