import os
import re
import shutil

ROOT = os.path.dirname(os.path.abspath(__file__))
BACKUP_DIR = os.path.join(ROOT, ".backup_logger_bracket")
os.makedirs(BACKUP_DIR, exist_ok=True)

# 匹配 logger.xxx(...)) 变成 logger.xxx(...)
LOGGER_PATTERN = re.compile(
    r"(logger\.(?:info|warning|error|debug|critical)\s*\(.*?)(\)\)+)"
)


def fix_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    new_content = content
    changed = False

    # 替换所有 logger.xxx(...)) 为 logger.xxx(...)
    def repl(m):
        before = m.group(1)
        after = before.rstrip()
        # 只保留一个右括号
        return after + ")"

    new_content, n = LOGGER_PATTERN.subn(repl, content)
    if n > 0:
        changed = True
    if changed:
        backup_path = os.path.join(BACKUP_DIR, os.path.relpath(filepath, ROOT))
        os.makedirs(os.path.dirname(backup_path), exist_ok=True)
        shutil.copy2(filepath, backup_path)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(new_content)
    return changed


def main():
    py_files = []
    for root, dirs, files in os.walk(ROOT):
        if ".venv" in root or BACKUP_DIR in root:
            continue
        for file in files:
            if file.endswith(".py"):
                py_files.append(os.path.join(root, file))
    total = 0
    for f in py_files:
        if fix_file(f):
            print(f"已修正: {f}")
            total += 1
    print(f"共修正文件数: {total}")


if __name__ == "__main__":
    main()
