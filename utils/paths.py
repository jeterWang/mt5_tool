"""
路径工具模块

提供获取数据、配置、图标等路径的函数
"""

import os
import sys


def get_app_root():
    """
    获取应用根目录路径

    Returns:
        应用根目录的绝对路径
    """
    if getattr(sys, "frozen", False):
        # 如果是打包后的可执行文件，返回执行文件所在目录
        return os.path.dirname(sys.executable)
    else:
        # 如果是开发环境，返回项目根目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.dirname(current_dir)


def get_data_path(file_name=None):
    """
    获取数据目录路径

    Args:
        file_name: 可选，文件名

    Returns:
        数据目录或数据文件的完整路径
    """
    app_root = get_app_root()

    # 检测是否是打包环境
    if getattr(sys, "frozen", False):
        # 打包环境下，数据目录应该在可执行文件同级目录下的data目录
        data_dir = os.path.join(app_root, "data")
        print(f"打包环境: 使用可执行文件同级的data目录: {data_dir}")
    else:
        # 开发环境下，数据目录在项目根目录下的data目录
        data_dir = os.path.join(app_root, "data")
        print(f"开发环境: 使用项目根目录下的data目录: {data_dir}")

    # 确保目录存在
    if not os.path.exists(data_dir):
        try:
            os.makedirs(data_dir)
            print(f"创建数据目录成功: {data_dir}")
        except Exception as e:
            print(f"创建数据目录失败: {data_dir}, 错误: {str(e)}")
            # 尝试使用备用目录
            temp_dir = os.path.join(os.path.expanduser("~"), "mt5_data")
            print(f"尝试使用备用数据目录: {temp_dir}")
            try:
                os.makedirs(temp_dir, exist_ok=True)
                data_dir = temp_dir
                print(f"使用备用数据目录: {data_dir}")
            except Exception as e2:
                print(f"创建备用数据目录也失败: {str(e2)}")
    else:
        print(f"数据目录已存在: {data_dir}")

    # 如果是请求特定文件
    if file_name:
        full_path = os.path.join(data_dir, file_name)
        if os.path.exists(full_path):
            print(f"数据文件已存在: {full_path}")
        else:
            print(f"数据文件不存在，将在需要时创建: {full_path}")

        # 检查文件权限
        if os.path.exists(full_path):
            try:
                # 尝试打开文件验证权限
                with open(full_path, "a") as f:
                    pass
                print(f"数据文件权限正常，可读写: {full_path}")
            except Exception as e:
                print(f"数据文件权限异常，可能无法读写: {full_path}, 错误: {str(e)}")

        return full_path
    return data_dir


def get_icon_path(icon_name):
    """
    获取图标文件路径

    Args:
        icon_name: 图标文件名

    Returns:
        图标文件的完整路径
    """
    icon_dir = os.path.join(get_app_root(), "resources", "icons")
    # 确保目录存在
    if not os.path.exists(icon_dir):
        os.makedirs(icon_dir)

    return os.path.join(icon_dir, icon_name)


def get_font_path(font_name):
    """
    获取字体文件路径

    Args:
        font_name: 字体文件名

    Returns:
        字体文件的完整路径
    """
    font_dir = os.path.join(get_app_root(), "resources", "fonts")
    # 确保目录存在
    if not os.path.exists(font_dir):
        os.makedirs(font_dir)

    return os.path.join(font_dir, font_name)


def get_sound_path(sound_filename):
    """获取音效文件的路径"""
    return get_app_root() + "/resources/sounds/" + sound_filename


def get_config_path(config_filename="config.json"):
    """获取配置文件的路径"""
    return get_app_root() + "/config/" + config_filename
