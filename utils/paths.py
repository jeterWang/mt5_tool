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
    # 获取当前文件所在的utils目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # 返回上一级目录，即应用根目录
    return os.path.dirname(current_dir)


def get_data_path(file_name=None):
    """
    获取数据目录路径

    Args:
        file_name: 可选，文件名

    Returns:
        数据目录或数据文件的完整路径
    """
    data_dir = os.path.join(get_app_root(), "data")
    # 确保目录存在
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    if file_name:
        return os.path.join(data_dir, file_name)
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
