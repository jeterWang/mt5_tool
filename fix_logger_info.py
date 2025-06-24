#!/usr/bin/env python3
"""
自动修复所有 logger.info() 缺少msg参数的问题。
会将空的 logger.info() 替换为 logger.info("[空日志]")，
并在参数为关键字参数但无msg时插入占位内容。
"""
import os
import re

# 需要处理的目录
TARGET_DIRS = [
    "app/",
    "config/"
]

def fix_logger_info_in_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 修复 logger.info() 无参数
    # 1. 完全空的 logger.info()
    content, n1 = re.subn(r'logger\.info\(\s*\)', 'logger.info("[空日志]")', content)
    # 2. 只有关键字参数但无msg
    def repl_keyword_only(m):
        args = m.group(1)
        if 'msg=' not in args:
            return f'logger.info("[空日志]", {args})'
        return m.group(0)
    content, n2 = re.subn(r'logger\.info\(([^\)]*)\)', repl_keyword_only, content)

    if n1 or n2:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"修复 {file_path}: 空logger.info() {n1}处，关键字参数无msg {n2}处")


def walk_and_fix():
    for base in TARGET_DIRS:
        for root, dirs, files in os.walk(base):
            for file in files:
                if file.endswith('.py'):
                    fix_logger_info_in_file(os.path.join(root, file))

if __name__ == "__main__":
    walk_and_fix()
    print("全部修复完成！")
