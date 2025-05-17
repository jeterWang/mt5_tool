import os
import sys
import shutil
import subprocess


def main():
    print("开始打包MT5TradeManager...")

    # 确保输出目录存在
    os.makedirs("dist", exist_ok=True)

    # PyInstaller命令及参数
    cmd = [
        "pyinstaller",
        "--noconfirm",
        "--onedir",  # 创建目录而不是单文件
        "--windowed",  # 不显示控制台窗口
        "--icon=resources/icons/icon.svg",  # 设置图标
        "--name=MT5TradeManager",  # 输出名称
        # 添加所有必要的数据文件
        "--add-data=resources/fonts;resources/fonts/",
        "--add-data=resources/icons;resources/icons/",
        "--add-data=resources/sounds;resources/sounds/",
        "--add-data=config;config/",
        "--add-data=app;app/",
        "--add-data=utils;utils/",
        "main.py",  # 主程序文件
    ]

    # 执行打包命令
    subprocess.call(cmd)

    print("打包完成！")
    print("可执行文件位于: dist/MT5TradeManager/MT5TradeManager.exe")


if __name__ == "__main__":
    main()
