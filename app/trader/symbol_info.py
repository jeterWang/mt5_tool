"""
MT5交易品种信息模块

提供与交易品种相关的参数和信息获取功能
"""

import MetaTrader5 as mt5
from typing import Dict, List

from config.loader import SYMBOLS


def get_symbol_params(symbol: str, is_connected: bool = False) -> Dict:
    """
    从MT5获取交易品种的参数

    Args:
        symbol: 交易品种名称
        is_connected: 是否已连接到MT5

    Returns:
        包含交易品种参数的字典
    """
    try:
        # 确保已连接
        if not is_connected:
            # 尝试初始化
            if not mt5.initialize():
                # 返回默认参数
                return {
                    "volume": 0.10,
                    "min_volume": 0.01,
                    "max_volume": 100.0,
                    "volume_step": 0.01,
                    "min_sl_points": 0,
                    "max_sl_points": 100000,
                    "min_tp_points": 0,
                    "max_tp_points": 100000,
                }

        # 获取交易品种信息
        symbol_info = mt5.symbol_info(symbol)
        if symbol_info is None:
            # 返回默认参数
            return {
                "volume": 0.10,
                "min_volume": 0.01,
                "max_volume": 100.0,
                "volume_step": 0.01,
                "min_sl_points": 0,
                "max_sl_points": 100000,
                "min_tp_points": 0,
                "max_tp_points": 100000,
            }

        # 从MT5获取品种参数
        params = {
            "volume": 0.10,  # 默认手数
            "min_volume": symbol_info.volume_min,
            "max_volume": symbol_info.volume_max,
            "volume_step": symbol_info.volume_step,
            "min_sl_points": 0,  # 最小止损点数
            "max_sl_points": 100000,  # 最大止损点数
            "min_tp_points": 0,  # 最小止盈点数
            "max_tp_points": 100000,  # 最大止盈点数
        }

        return params
    except Exception as e:
        # print(f"获取{symbol}参数出错：{str(e)}")
        # 返回默认参数
        return {
            "volume": 0.10,
            "min_volume": 0.01,
            "max_volume": 100.0,
            "volume_step": 0.01,
            "min_sl_points": 0,
            "max_sl_points": 100000,
            "min_tp_points": 0,
            "max_tp_points": 100000,
        }


def get_all_symbols(is_connected: bool = False) -> List[str]:
    """
    获取所有可交易的品种

    Args:
        is_connected: 是否已连接到MT5

    Returns:
        品种列表
    """
    try:
        if not is_connected:
            if not mt5.initialize():
                return SYMBOLS  # 连接失败时直接返回配置文件中的品种

        # 获取所有可见的品种
        try:
            symbols = mt5.symbols_get()
            if symbols is None:
                return SYMBOLS  # 获取失败时返回配置文件中的品种

            symbol_names = [s.name for s in symbols if s.visible]
            return symbol_names
        except Exception as e:
            return SYMBOLS  # 获取出错时返回配置文件中的品种
    except Exception as e:
        # 返回默认品种列表
        return SYMBOLS


def get_timeframe_constant(timeframe: str) -> int:
    """
    将时间周期字符串转换为MT5的时间周期常量

    Args:
        timeframe: 时间周期字符串，如'M1', 'M5'等

    Returns:
        对应的MT5时间周期常量
    """
    timeframe_map = {
        "M1": mt5.TIMEFRAME_M1,
        "M5": mt5.TIMEFRAME_M5,
        "M15": mt5.TIMEFRAME_M15,
        "M30": mt5.TIMEFRAME_M30,
        "H1": mt5.TIMEFRAME_H1,
        "H4": mt5.TIMEFRAME_H4,
        "D1": mt5.TIMEFRAME_D1,
        "W1": mt5.TIMEFRAME_W1,
        "MN1": mt5.TIMEFRAME_MN1,
    }
    return timeframe_map.get(timeframe, mt5.TIMEFRAME_M1)
