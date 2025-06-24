import os
import re
import shutil

# 需要遍历的根目录
ROOT = os.path.dirname(os.path.abspath(__file__))

# 备份目录
BACKUP_DIR = os.path.join(ROOT, ".backup_comment_fix")
os.makedirs(BACKUP_DIR, exist_ok=True)


def fix_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    new_lines = []
    i = 0
    changed = False
    while i < len(lines):
        line = lines[i]
        # 检查被注释掉的print(
        if re.match(r"^\s*#\s*print\s*\(.*", line):
            # 检查下一行是否是未注释的f-string
            if i + 1 < len(lines) and re.match(r"^\s*f\"|^\s*f'", lines[i + 1]):
                # 注释掉print和后续所有未闭合的行，直到遇到只包含)的行
                indent = re.match(r"^(\s*)", line).group(1)
                new_lines.append(line if line.strip().startswith("#") else "# " + line)
                i += 1
                while i < len(lines):
                    l = lines[i]
                    # 如果已经注释，直接加
                    if l.strip().startswith("#"):
                        new_lines.append(l)
                    else:
                        new_lines.append(indent + "# " + l.lstrip())
                    # 检查是否是只包含)的行
                    if l.strip() == ")":
                        i += 1
                        break
                    i += 1
                changed = True
                continue
        new_lines.append(line)
        i += 1
    if changed:
        # 备份原文件
        backup_path = os.path.join(BACKUP_DIR, os.path.relpath(filepath, ROOT))
        os.makedirs(os.path.dirname(backup_path), exist_ok=True)
        shutil.copy2(filepath, backup_path)
        with open(filepath, "w", encoding="utf-8") as f:
            f.writelines(new_lines)
    return changed


def main():
    py_files = []
    for root, dirs, files in os.walk(ROOT):
        # 跳过备份目录和虚拟环境
        if ".venv" in root or BACKUP_DIR in root:
            continue
        for file in files:
            if file.endswith(".py"):
                py_files.append(os.path.join(root, file))
    total = 0
    for f in py_files:
        if fix_file(f):
            print(f"已修复: {f}")
            total += 1
    print(f"共修复文件数: {total}")


if __name__ == "__main__":
    main()
