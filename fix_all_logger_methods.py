#!/usr/bin/env python3
"""
自动修复所有 logger 方法（info/warning/error/debug/exception/critical）缺少msg参数的问题。
会将空的 logger.xxx() 替换为 logger.xxx("[空日志]")，
并在参数为关键字参数但无msg时插入占位内容。
"""
import os
import re

TARGET_DIRS = [
    "app/",
    "config/"
]
LOGGER_METHODS = ["info", "warning", "error", "debug", "exception", "critical"]

def fix_logger_methods_in_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    total_n1 = total_n2 = 0
    for method in LOGGER_METHODS:
        # 1. 完全空的 logger.xxx()
        content, n1 = re.subn(rf'logger\.{method}\(\s*\)', f'logger.{method}("[空日志]")', content)
        # 2. 只有关键字参数但无msg
        def repl_keyword_only(m):
            args = m.group(1)
            if 'msg=' not in args:
                return f'logger.{method}("[空日志]", {args})'
            return m.group(0)
        content, n2 = re.subn(rf'logger\.{method}\(([^\)]*)\)', repl_keyword_only, content)
        total_n1 += n1
        total_n2 += n2
    if total_n1 or total_n2:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"修复 {file_path}: 空logger方法 {total_n1}处，关键字参数无msg {total_n2}处")

def walk_and_fix():
    for base in TARGET_DIRS:
        for root, dirs, files in os.walk(base):
            for file in files:
                if file.endswith('.py'):
                    fix_logger_methods_in_file(os.path.join(root, file))

if __name__ == "__main__":
    walk_and_fix()
    print("全部logger方法修复完成！")
