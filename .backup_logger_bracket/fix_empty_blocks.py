import os
import re
import logging
logger = logging.getLogger(__name__)

def fix_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    changed = False
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        # 检查需要代码块的语句
        if (stripped.endswith(':') and any(stripped.startswith(k) for k in ['except', 'else', 'if', 'for', 'while', 'try', 'with', 'def', 'class'])):
            # 跳过空行和注释，找到下一个有意义的行
            j = i + 1
            while j < len(lines) and (lines[j].strip() == '' or lines[j].strip().startswith('#')):
                j += 1
            # 如果下一个有意义的行不是更深缩进，说明块是空的
            if j == len(lines) or (len(lines[j]) - len(lines[j].lstrip()) <= len(line) - len(line.lstrip())):
                indent = len(line) - len(line.lstrip()) + 4
                lines.insert(i + 1, ' ' * indent + 'pass\n')
                changed = True
                i += 1
        i += 1
    if changed:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        logger.info(f"已修复: {file_path}"))

def main():
    for root, dirs, files in os.walk('app'):
        for file in files:
            if file.endswith('.py'):
                fix_file(os.path.join(root, file))
    for root, dirs, files in os.walk('config'):
        for file in files:
            if file.endswith('.py'):
                fix_file(os.path.join(root, file))
    for root, dirs, files in os.walk('utils'):
        for file in files:
            if file.endswith('.py'):
                fix_file(os.path.join(root, file))
    logger.info("所有空代码块已自动修复！"))

if __name__ == "__main__":
    main()
