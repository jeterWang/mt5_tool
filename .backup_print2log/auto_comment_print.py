import os
import re

# 只保留包含这些关键词的print（错误/异常/失败）
KEEP_KEYWORDS = ["错误", "失败", "异常", "Error", "Exception"]

# 需要处理的目录
TARGET_DIRS = [
    "app", "config", "utils"
]

def should_keep(line):
    return any(k in line for k in KEEP_KEYWORDS)

def process_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    changed = False
    for i, line in enumerate(lines):
        # 跳过已注释、logger、格式化字符串等
        if 'print(' in line and not line.strip().startswith('#') and 'logger.' not in line:
            if not should_keep(line):
                # 注释掉该行
                lines[i] = re.sub(r'^(\s*)', r'\1# ', line)
                changed = True
    if changed:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        print(f"已处理: {file_path}")

def main():
    for target_dir in TARGET_DIRS:
        for root, dirs, files in os.walk(target_dir):
            for file in files:
                if file.endswith('.py'):
                    process_file(os.path.join(root, file))
    print("\n所有print已批量静默（只保留错误/异常相关输出）！")

if __name__ == "__main__":
    main()
