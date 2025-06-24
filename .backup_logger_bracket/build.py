"""
MT5交易系统打包脚本

将项目打包成可执行文件
"""

import os
import shutil
import subprocess
import sys
import logging
logger = logging.getLogger(__name__)
from pathlib import Path
import urllib.request
import json


def ensure_icon_exists():
    """确保图标文件存在"""
    ico_path = Path("resources/icons/icon.ico")

    # 如果已经存在ico文件且文件大小合理，则使用现有文件
    if ico_path.exists() and ico_path.stat().st_size > 1000:
        logger.info(f"使用现有图标文件: {ico_path}"))
        return True

    logger.info("图标文件不存在或无效，尝试下载..."))

    # 确保目录存在
    ico_path.parent.mkdir(exist_ok=True, parents=True)

    # 尝试下载默认图标
    try:
        # MetaTrader5官方图标URL
        default_icon_url = "https://raw.githubusercontent.com/MetaTrader5/MetaTrader5/main/Icons/mt5.ico"
        logger.info(f"下载图标从: {default_icon_url}"))
        urllib.request.urlretrieve(default_icon_url, ico_path)
        logger.info(f"成功下载图标到: {ico_path}"))
        return True
    except Exception as e:
        logger.error(f"下载图标失败: {e}"))

        # 如果下载失败，检查是否有备用图标
        backup_ico = Path("resources/icons/backup_icon.ico")
        if backup_ico.exists():
            shutil.copy(backup_ico, ico_path)
            logger.info(f"使用备用图标: {backup_ico}"))
            return True

        logger.info("无法获取有效的图标文件"))
        return False


def verify_config():
    """验证配置文件是否存在且有效，如果不存在则创建默认配置"""
    try:
        config_path = Path("config/config.json")
        if not config_path.exists():
            # 从配置加载器导入默认设置
            logger.info("配置文件不存在，将创建默认配置"))
            sys.path.append(".")
            from config.loader import (
                SYMBOLS,
                DEFAULT_TIMEFRAME,
                Delta_TIMEZONE,
                TRADING_DAY_RESET_HOUR,
                DAILY_LOSS_LIMIT,
                DAILY_TRADE_LIMIT,
                GUI_SETTINGS,
                SL_MODE,
                BREAKOUT_SETTINGS,
                BATCH_ORDER_DEFAULTS,
            )

            # 创建默认配置
            default_config = {
                "SYMBOLS": SYMBOLS.copy(),
                "DEFAULT_TIMEFRAME": DEFAULT_TIMEFRAME,
                "Delta_TIMEZONE": Delta_TIMEZONE,
                "TRADING_DAY_RESET_HOUR": TRADING_DAY_RESET_HOUR,
                "DAILY_LOSS_LIMIT": DAILY_LOSS_LIMIT,
                "DAILY_TRADE_LIMIT": DAILY_TRADE_LIMIT,
                "GUI_SETTINGS": GUI_SETTINGS,
                "SL_MODE": SL_MODE,
                "BREAKOUT_SETTINGS": BREAKOUT_SETTINGS,
                "BATCH_ORDER_DEFAULTS": BATCH_ORDER_DEFAULTS,
            }

            # 确保config目录存在
            config_path.parent.mkdir(exist_ok=True)

            # 保存默认配置
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(default_config, f, indent=4, ensure_ascii=False)

            logger.info(f"已创建默认配置文件: {config_path}"))
        else:
            # 验证配置文件格式
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
                logger.info(f"验证配置文件成功，当前DAILY_TRADE_LIMIT: {config.get('DAILY_TRADE_LIMIT', '未设置')}"
                ))

                # 确保配置文件包含必要的字段
                required_fields = [
                    "SYMBOLS",
                    "DEFAULT_TIMEFRAME",
                    "DAILY_TRADE_LIMIT",
                    "DAILY_LOSS_LIMIT",
                    "GUI_SETTINGS",
                    "SL_MODE",
                    "BREAKOUT_SETTINGS",
                    "BATCH_ORDER_DEFAULTS",
                ]

                missing_fields = [
                    field for field in required_fields if field not in config
                ]
                if missing_fields:
                    logger.info(f"配置文件缺少必要字段: {missing_fields}"))

                    # 更新缺失的字段
                    from config.loader import (
                        SYMBOLS,
                        DEFAULT_TIMEFRAME,
                        Delta_TIMEZONE,
                        TRADING_DAY_RESET_HOUR,
                        DAILY_LOSS_LIMIT,
                        DAILY_TRADE_LIMIT,
                        GUI_SETTINGS,
                        SL_MODE,
                        BREAKOUT_SETTINGS,
                        BATCH_ORDER_DEFAULTS,
                    )

                    for field in missing_fields:
                        if field == "SYMBOLS":
                            config["SYMBOLS"] = SYMBOLS.copy()
                        elif field == "DEFAULT_TIMEFRAME":
                            config["DEFAULT_TIMEFRAME"] = DEFAULT_TIMEFRAME
                        elif field == "DAILY_LOSS_LIMIT":
                            config["DAILY_LOSS_LIMIT"] = DAILY_LOSS_LIMIT
                        elif field == "DAILY_TRADE_LIMIT":
                            config["DAILY_TRADE_LIMIT"] = DAILY_TRADE_LIMIT
                        elif field == "GUI_SETTINGS":
                            config["GUI_SETTINGS"] = GUI_SETTINGS
                        elif field == "SL_MODE":
                            config["SL_MODE"] = SL_MODE
                        elif field == "BREAKOUT_SETTINGS":
                            config["BREAKOUT_SETTINGS"] = BREAKOUT_SETTINGS
                        elif field == "BATCH_ORDER_DEFAULTS":
                            config["BATCH_ORDER_DEFAULTS"] = BATCH_ORDER_DEFAULTS

                    # 保存更新后的配置
                    with open(config_path, "w", encoding="utf-8") as f:
                        json.dump(config, f, indent=4, ensure_ascii=False)

                    logger.info(f"已更新配置文件: {config_path}"))
    except Exception as e:
        logger.error(f"验证配置文件失败: {e}"))


def build_exe():
    """将项目打包成可执行文件"""
    logger.info("开始打包MT5交易系统..."))

    # 清理之前的构建
    for folder in ["build", "dist"]:
        if os.path.exists(folder):
            logger.info(f"正在删除旧的{folder}文件夹..."))
            shutil.rmtree(folder)

    if os.path.exists("MT5交易系统.spec"):
        logger.info("正在删除旧的.spec文件..."))
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

    # 确保配置文件有效
    verify_config()

    # 图标的绝对路径
    icon_path = os.path.abspath("resources/icons/icon.ico")
    logger.info(f"使用图标: {icon_path}"))

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
        # 添加配置文件夹
        "--add-data",
        f"config{separator}config",
        "main.py",  # 入口脚本
    ]

    # 执行打包命令
    logger.info("执行PyInstaller命令..."))
    logger.info(f"命令行: {' '.join(cmd)}"))

    try:
        subprocess.run(cmd, check=True)
        logger.info("PyInstaller执行成功"))
    except subprocess.CalledProcessError as e:
        logger.error(f"PyInstaller执行失败: {e}"))
        return

    # 后处理：复制必要的文件和目录
    logger.info("正在复制资源文件和配置文件..."))
    dist_dir = Path("dist/MT5交易系统")

    # 复制resources目录
    if resources_dir.exists():
        dst_resources = dist_dir / "resources"
        if dst_resources.exists():
            shutil.rmtree(dst_resources)
        shutil.copytree(resources_dir, dst_resources)
        logger.info(f"已复制资源目录: {resources_dir} -> {dst_resources}"))

    # 复制config目录
    config_dir = Path("config")
    if config_dir.exists():
        dst_config = dist_dir / "config"
        if dst_config.exists():
            shutil.rmtree(dst_config)
        shutil.copytree(config_dir, dst_config)
        logger.info(f"已复制配置目录: {config_dir} -> {dst_config}"))

        # 确保配置文件权限正确（可写）
        config_file = dst_config / "config.json"
        if config_file.exists():
            if sys.platform.startswith("win"):
                try:
                    import stat

                    # 在Windows上设置为可读写
                    os.chmod(config_file, stat.S_IWRITE | stat.S_IREAD)
                    logger.info(f"已设置配置文件权限: {config_file}"))

                    # 额外检查权限
                    try:
                        # 尝试写入配置文件验证权限
                        with open(config_file, "r", encoding="utf-8") as f:
                            config_content = json.load(f)

                        # 无修改地写回配置
                        with open(config_file, "w", encoding="utf-8") as f:
                            json.dump(config_content, f, indent=4, ensure_ascii=False)

                        logger.info(f"配置文件权限验证成功: {config_file}"))
                    except Exception as perm_e:
                        logger.error(f"配置文件权限验证失败: {perm_e}"))

                except Exception as e:
                    logger.info(f"设置配置文件权限时出错: {e}"))
            else:
                # 在类Unix系统上设置为可读写
                try:
                    os.chmod(config_file, 0o644)  # rw-r--r--
                    logger.info(f"在非Windows系统设置配置文件权限: {config_file}"))
                except Exception as e:
                    logger.info(f"设置配置文件权限时出错: {e}"))

    # 创建data目录并复制数据库文件
    data_dir = Path("data")
    dst_data = dist_dir / "data"
    if not dst_data.exists():
        dst_data.mkdir(exist_ok=True)
        logger.info(f"已创建数据目录: {dst_data}"))

    # 如果是第一次创建，添加一个空的readme文件说明目录用途
    readme_file = dst_data / "README.txt"
    if not readme_file.exists():
        with open(readme_file, "w", encoding="utf-8") as f:
            f.write(
                "此目录用于存储交易数据和历史记录。请勿手动删除或修改此目录下的文件。"
            )
        logger.info(f"已创建数据目录说明文件: {readme_file}"))

    # 如果开发环境中存在数据库文件，复制到打包目录
    db_file = data_dir / "trade_history.db"
    if db_file.exists():
        dst_db = dst_data / "trade_history.db"
        shutil.copy(db_file, dst_db)
        logger.info(f"已复制数据库文件: {db_file} -> {dst_db}"))

        # 确保数据库文件权限正确（可读写）
        try:
            if sys.platform.startswith("win"):
                import stat

                os.chmod(dst_db, stat.S_IWRITE | stat.S_IREAD)
            else:
                os.chmod(dst_db, 0o644)  # rw-r--r--
            logger.info(f"已设置数据库文件权限: {dst_db}"))
        except Exception as e:
            logger.info(f"设置数据库文件权限时出错: {e}"))
    else:
        # 如果开发环境中不存在数据库文件，创建一个新的空数据库
        try:
            import sqlite3

            dst_db = dst_data / "trade_history.db"
            conn = sqlite3.connect(dst_db)
            cursor = conn.cursor()

            # 创建基本表结构
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS trade_count (
                    id INTEGER PRIMARY KEY,
                    date TEXT,
                    count INTEGER
                )
                """
            )

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS risk_events (
                    id INTEGER PRIMARY KEY,
                    timestamp TEXT,
                    event_type TEXT,
                    details TEXT
                )
                """
            )

            conn.commit()
            conn.close()

            logger.info(f"已创建新的空数据库文件: {dst_db}"))

            # 设置适当的权限
            if sys.platform.startswith("win"):
                import stat

                os.chmod(dst_db, stat.S_IWRITE | stat.S_IREAD)
            else:
                os.chmod(dst_db, 0o644)  # rw-r--r--
        except Exception as e:
            logger.error(f"创建新数据库失败: {e}"))

        logger.info(f"开发环境中不存在数据库文件: {db_file}，已创建新的空数据库"))

    # 额外检查，确保EXE中包含了图标
    try:
        exe_file = dist_dir / "MT5交易系统.exe"
        if exe_file.exists():
            logger.info(f"确保可执行文件图标已设置: {exe_file}"))
            # 直接复制图标文件到exe同级目录，有些Windows版本会从这里读取图标
            icon_dst = dist_dir / "icon.ico"
            shutil.copy(icon_path, icon_dst)
            logger.info(f"已复制图标到: {icon_dst}"))
    except Exception as e:
        logger.info(f"处理可执行文件图标时出错: {e}"))

    logger.info("打包完成！"))
    logger.info(f"可执行文件位于: {os.path.abspath(dist_dir / 'MT5交易系统.exe')}"))


if __name__ == "__main__":
    build_exe()
