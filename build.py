"""
MT5交易系统打包脚本

将项目打包成可执行文件
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path
import urllib.request


def ensure_icon_exists():
    """确保图标文件存在"""
    ico_path = Path("resources/icons/icon.ico")

    # 如果已经存在ico文件且文件大小合理，则使用现有文件
    if ico_path.exists() and ico_path.stat().st_size > 1000:
        print(f"使用现有图标文件: {ico_path}")
        return True

    print("图标文件不存在或无效，尝试下载...")

    # 确保目录存在
    ico_path.parent.mkdir(exist_ok=True, parents=True)

    # 尝试下载默认图标
    try:
        # MetaTrader5官方图标URL
        default_icon_url = "https://raw.githubusercontent.com/MetaTrader5/MetaTrader5/main/Icons/mt5.ico"
        print(f"下载图标从: {default_icon_url}")
        urllib.request.urlretrieve(default_icon_url, ico_path)
        print(f"成功下载图标到: {ico_path}")
        return True
    except Exception as e:
        print(f"下载图标失败: {e}")

        # 如果下载失败，检查是否有备用图标
        backup_ico = Path("resources/icons/backup_icon.ico")
        if backup_ico.exists():
            shutil.copy(backup_ico, ico_path)
            print(f"使用备用图标: {backup_ico}")
            return True

        print("无法获取有效的图标文件")
        return False


def build_exe():
    """将项目打包成可执行文件"""
    print("开始打包MT5交易系统...")

    # 清理之前的构建
    for folder in ["build", "dist"]:
        if os.path.exists(folder):
            print(f"正在删除旧的{folder}文件夹...")
            shutil.rmtree(folder)

    if os.path.exists("MT5交易系统.spec"):
        print("正在删除旧的.spec文件...")
        os.remove("MT5交易系统.spec")

    # 确保resources文件夹存在
    resources_dir = Path("resources")
    if not resources_dir.exists():
        resources_dir.mkdir(exist_ok=True)

    # 确保fonts文件夹存在
    fonts_dir = resources_dir / "fonts"
    if not fonts_dir.exists():
        fonts_dir.mkdir(exist_ok=True)

    # 确保icons文件夹存在并且有有效的ico文件
    icons_dir = resources_dir / "icons"
    if not icons_dir.exists():
        icons_dir.mkdir(exist_ok=True)

    # 确保有有效的图标文件
    ensure_icon_exists()

    # 图标的绝对路径
    icon_path = os.path.abspath("resources/icons/icon.ico")
    print(f"使用图标: {icon_path}")

    # 构建命令
    # 在Windows上使用分号作为分隔符，在其他平台使用冒号
    separator = ";" if sys.platform.startswith("win") else ":"

    cmd = [
        "pyinstaller",
        "--name=MT5交易系统",
        "--windowed",  # 无控制台窗口
        f"--icon={icon_path}",  # 使用绝对路径指定图标
        "--clean",  # 在构建前清理
        "--noconfirm",  # 不要询问确认
        # 确保图标包含在打包中
        "--add-data",
        f"{icon_path}{separator}resources/icons/",
        # 添加资源文件夹
        "--add-data",
        f"resources{separator}resources",
        "main.py",  # 入口脚本
    ]

    # 执行打包命令
    print("执行PyInstaller命令...")
    print(f"命令行: {' '.join(cmd)}")

    try:
        subprocess.run(cmd, check=True)
        print("PyInstaller执行成功")
    except subprocess.CalledProcessError as e:
        print(f"PyInstaller执行失败: {e}")
        return

    # 后处理：复制必要的文件和目录
    print("正在复制资源文件和配置文件...")
    dist_dir = Path("dist/MT5交易系统")

    # 复制resources目录
    if resources_dir.exists():
        dst_resources = dist_dir / "resources"
        if dst_resources.exists():
            shutil.rmtree(dst_resources)
        shutil.copytree(resources_dir, dst_resources)
        print(f"已复制资源目录: {resources_dir} -> {dst_resources}")

    # 复制config目录
    config_dir = Path("config")
    if config_dir.exists():
        dst_config = dist_dir / "config"
        if dst_config.exists():
            shutil.rmtree(dst_config)
        shutil.copytree(config_dir, dst_config)
        print(f"已复制配置目录: {config_dir} -> {dst_config}")

    # 额外检查，确保EXE中包含了图标
    try:
        exe_file = dist_dir / "MT5交易系统.exe"
        if exe_file.exists():
            print(f"确保可执行文件图标已设置: {exe_file}")
            # 直接复制图标文件到exe同级目录，有些Windows版本会从这里读取图标
            icon_dst = dist_dir / "icon.ico"
            shutil.copy(icon_path, icon_dst)
            print(f"已复制图标到: {icon_dst}")
    except Exception as e:
        print(f"处理可执行文件图标时出错: {e}")

    print("打包完成！")
    print(f"可执行文件位于: {os.path.abspath(dist_dir / 'MT5交易系统.exe')}")


if __name__ == "__main__":
    build_exe()
