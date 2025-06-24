import os
import re
import shutil

ROOT = os.path.dirname(os.path.abspath(__file__))
BACKUP_DIR = os.path.join(ROOT, ".backup_print2log")
os.makedirs(BACKUP_DIR, exist_ok=True)

LOGGER_INIT = "import logging\nlogger = logging.getLogger(__name__)\n"
LOG_CONFIG = """import logging\n\nlogging.basicConfig(\n    level=logging.INFO,\n    format='[%(asctime)s] [%(levelname)s] %(name)s: %(message)s',\n    handlers=[\n        logging.StreamHandler(),\n    ]\n)\n"""


def guess_log_level(s):
    s = s.lower()
    if any(w in s for w in ["错误", "失败", "exception", "error"]):
        return "error"
    if any(w in s for w in ["警告", "warning"]):
        return "warning"
    return "info"


def fix_file(filepath, is_main=False):
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    changed = False
    new_lines = []
    has_logger = any("getLogger(__name__" in l for l in lines)
    has_import = any("import logging" in l for l in lines)
    inserted_logger = False
    i = 0
    while i < len(lines):
        line = lines[i]
        # 跳过注释掉的print
        if re.match(r"^\s*#\s*print\s*\(.*", line):
            new_lines.append(line)
            i += 1
            continue
        # 匹配print(单行或多行)
        m = re.match(r"^(\s*)print\s*\((.*)", line)
        if m:
            indent = m.group(1)
            content = m.group(2)
            # 检查是否多行print
            if not line.rstrip().endswith(")") or content.count("(") > content.count(
                ")"
            ):
                # 多行print，收集到闭合)
                print_block = [content]
                i += 1
                while i < len(lines):
                    l = lines[i]
                    print_block.append(l)
                    if l.strip() == ")":
                        i += 1
                        break
                    i += 1
                full_content = "".join(print_block)
                # 取首行内容判断级别
                level = guess_log_level(full_content)
                new_lines.append(f"{indent}logger.{level}({full_content.strip()})\n")
                changed = True
                continue
            else:
                # 单行print
                level = guess_log_level(content)
                new_lines.append(f"{indent}logger.{level}({content.strip()})\n")
                changed = True
                i += 1
                continue
        new_lines.append(line)
        i += 1
    # 插入logger初始化
    if changed and not has_logger:
        # 找到第一个非注释import后插入
        for idx, l in enumerate(new_lines):
            if l.strip().startswith("import") and not l.strip().startswith(
                "import logging"
            ):
                # 检查下一个不是import的地方
                if idx + 1 < len(new_lines) and not new_lines[
                    idx + 1
                ].strip().startswith("import"):
                    new_lines.insert(idx + 1, LOGGER_INIT)
                    inserted_logger = True
                    break
        if not inserted_logger:
            # 没有import，插到文件最前面
            new_lines.insert(0, LOGGER_INIT)
    # main.py插入全局日志配置
    if is_main and "logging.basicConfig" not in "".join(new_lines):
        # 插入到所有import logging后
        for idx, l in enumerate(new_lines):
            if "import logging" in l:
                new_lines.insert(idx + 1, LOG_CONFIG)
                break
    if changed:
        backup_path = os.path.join(BACKUP_DIR, os.path.relpath(filepath, ROOT))
        os.makedirs(os.path.dirname(backup_path), exist_ok=True)
        shutil.copy2(filepath, backup_path)
        with open(filepath, "w", encoding="utf-8") as f:
            f.writelines(new_lines)
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
        is_main = os.path.basename(f) == "main.py"
        if fix_file(f, is_main):
            print(f"已替换: {f}")
            total += 1
    print(f"共替换文件数: {total}")


if __name__ == "__main__":
    main()
