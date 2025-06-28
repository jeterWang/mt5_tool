"""
MT5订单操作模块

提供下单、平仓、修改订单等操作
"""

import MetaTrader5 as mt5
import logging

logger = logging.getLogger(__name__)
from typing import Dict, List, Optional, Union


def place_order(
    symbol: str,
    order_type: str,
    volume: float,
    price: Optional[float] = None,
    sl: Optional[float] = None,
    tp: Optional[float] = None,
    comment: str = "",
) -> Optional[int]:
    """
    下单函数

    Args:
        symbol: 交易品种
        order_type: 订单类型 ('buy' 或 'sell')
        volume: 交易量
        price: 价格（市价单为None）
        sl: 止损价格
        tp: 止盈价格
        comment: 订单注释

    Returns:
        订单号，失败返回None
    """
    try:
        symbol_info = mt5.symbol_info(symbol)
        if symbol_info is None:
            # print(f"未找到交易品种: {symbol}")
            return None

        if not symbol_info.visible:
            if not mt5.symbol_select(symbol, True):
                logger.error("[空日志]", f"选择交易品种失败: {symbol}")
                return None

        point = symbol_info.point
        if order_type.lower() == "buy":
            order_type = mt5.ORDER_TYPE_BUY
        elif order_type.lower() == "sell":
            order_type = mt5.ORDER_TYPE_SELL
        else:
            # print("无效的订单类型")
            return None

        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": volume,
            "type": order_type,
            "price": (
                price or mt5.symbol_info_tick(symbol).ask
                if order_type == mt5.ORDER_TYPE_BUY
                else mt5.symbol_info_tick(symbol).bid
            ),
            "deviation": 20,
            "magic": 234000,
            "comment": comment,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }

        if sl:
            request["sl"] = sl
        if tp:
            request["tp"] = tp

        result = mt5.order_send(request)
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            logger.error("[空日志]", f"下单失败: {result.comment}")
            return None
        return result.order
    except Exception as e:
        # print(f"下单出错: {str(e)}")
        return None


def place_order_with_tp_sl(
    symbol: str,
    order_type: str,
    volume: float,
    sl_points: int = 0,
    tp_points: int = 0,
    price: float = None,
    comment: str = "",
) -> Optional[int]:
    """
    下单（支持带止损止盈的市价单和挂单）

    Args:
        symbol: 交易品种
        order_type: 订单类型 ('buy' 或 'sell')
        volume: 交易量
        sl_points: 止损点数
        tp_points: 止盈点数
        price: 价格（市价单为None，挂单需指定价格）
        comment: 订单注释

    Returns:
        订单号，失败返回None
    """
    try:
        # 获取当前价格
        symbol_info = mt5.symbol_info(symbol)
        if symbol_info is None:
            logger.error("[空日志]", f"获取{symbol}信息失败")
            return None

        # 计算止损止盈价格
        if order_type == "buy":
            if sl_points > 0:
                sl_price = symbol_info.bid - sl_points * symbol_info.point
            else:
                sl_price = 0

            if tp_points > 0:
                tp_price = symbol_info.bid + tp_points * symbol_info.point
            else:
                tp_price = 0

            # 如果是挂单，使用指定价格，否则使用当前买入价
            order_price = price if price is not None else symbol_info.bid

        else:  # sell
            if sl_points > 0:
                sl_price = symbol_info.ask + sl_points * symbol_info.point
            else:
                sl_price = 0

            if tp_points > 0:
                tp_price = symbol_info.ask - tp_points * symbol_info.point
            else:
                tp_price = 0

            # 如果是挂单，使用指定价格，否则使用当前卖出价
            order_price = price if price is not None else symbol_info.ask

        # 准备订单请求
        request = {
            "action": (
                mt5.TRADE_ACTION_DEAL if price is None else mt5.TRADE_ACTION_PENDING
            ),
            "symbol": symbol,
            "volume": volume,
            "type": (
                mt5.ORDER_TYPE_BUY if order_type == "buy" else mt5.ORDER_TYPE_SELL
            ),
            "price": order_price,
            "sl": sl_price,
            "tp": tp_price,
            "deviation": 20,
            "magic": 234000,
            "comment": comment,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }

        # 如果是挂单，需要设置挂单类型
        if price is not None:
            if order_type == "buy":
                request["type"] = mt5.ORDER_TYPE_BUY_STOP
            else:
                request["type"] = mt5.ORDER_TYPE_SELL_STOP

        # 发送订单
        result = mt5.order_send(request)
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            logger.error("[空日志]", f"下单失败，错误代码：{result.retcode}")
            return None
        return result.order
    except Exception as e:
        # print(f"下单出错：{str(e)}")
        return None


def place_order_with_partial_tp(
    symbol: str,
    order_type: str,
    volume: float,
    sl_points: float,
    tp_levels: List[Dict[str, float]],
    comment: str = "",
) -> Optional[int]:
    """
    带分批止盈的下单函数

    Args:
        symbol: 交易品种
        order_type: 订单类型 ('buy' 或 'sell')
        volume: 交易量
        sl_points: 止损点数
        tp_levels: 分批止盈设置列表，每个元素为字典，包含 'points' 和 'volume' 键
        comment: 订单注释

    Returns:
        主订单号，失败返回None
    """
    # 验证分批止盈设置
    total_volume = sum(level["volume"] for level in tp_levels)
    if total_volume > volume:
        # print("分批止盈总量不能超过订单总量")
        return None

    # 创建主订单
    main_order = place_order_with_tp_sl(
        symbol,
        order_type,
        volume,
        sl_points,
        tp_levels[-1]["points"],
        comment=comment,
    )
    if not main_order:
        return None

    # 创建分批止盈订单
    for i, level in enumerate(tp_levels[:-1]):
        tp_comment = f"{comment}_TP_{i+1}"
        place_order_with_tp_sl(
            symbol,
            order_type,
            level["volume"],
            sl_points,
            level["points"],
            comment=tp_comment,
        )
    return main_order


def close_position(ticket: int) -> bool:
    """
    平仓

    Args:
        ticket: 订单号

    Returns:
        是否成功
    """
    try:
        position = mt5.positions_get(ticket=ticket)
        if not position:
            return False

        position = position[0]._asdict()

        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": position["symbol"],
            "volume": position["volume"],
            "type": (
                mt5.ORDER_TYPE_SELL
                if position["type"] == mt5.POSITION_TYPE_BUY
                else mt5.ORDER_TYPE_BUY
            ),
            "position": ticket,
            "price": (
                mt5.symbol_info_tick(position["symbol"]).bid
                if position["type"] == mt5.POSITION_TYPE_BUY
                else mt5.symbol_info_tick(position["symbol"]).ask
            ),
            "deviation": 20,
            "magic": 234000,
            "comment": "close position",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }

        result = mt5.order_send(request)
        return result.retcode == mt5.TRADE_RETCODE_DONE
    except Exception as e:
        # print(f"平仓出错：{str(e)}")
        return False


def cancel_order(ticket: int) -> bool:
    """
    撤销指定订单

    Args:
        ticket: 订单号

    Returns:
        是否成功
    """
    try:
        # 获取订单信息
        order = mt5.orders_get(ticket=ticket)
        if order is None or len(order) == 0:
            # print(f"未找到订单：{ticket}")
            return False

        order = order[0]

        # 准备撤销请求
        request = {
            "action": mt5.TRADE_ACTION_REMOVE,
            "order": ticket,
            "comment": "撤销订单",
        }

        # 发送撤销请求
        result = mt5.order_send(request)
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            logger.error("[空日志]", f"撤销订单失败，错误代码：{result.retcode}")
            return False

        return True
    except Exception as e:
        # print(f"撤销订单出错：{str(e)}")
        return False


def place_pending_order(
    symbol: str,
    order_type: str,
    volume: float,
    price: float,
    sl_price: float = None,
    tp_points: int = 0,
    comment: str = "",
) -> Optional[int]:
    """
    下挂单，支持使用具体价格设置止损

    Args:
        symbol: 交易品种
        order_type: 订单类型 ('buy_stop' 或 'sell_stop')
        volume: 交易量
        price: 挂单价格
        sl_price: 止损价格（直接指定价格而非点数）
        tp_points: 止盈点数
        comment: 订单注释

    Returns:
        订单号，失败返回None
    """
    try:
        # 获取交易品种信息
        symbol_info = mt5.symbol_info(symbol)
        if symbol_info is None:
            logger.error("[空日志]", f"获取{symbol}信息失败")
            return None

        # 确保交易品种可见
        if not symbol_info.visible:
            if not mt5.symbol_select(symbol, True):
                logger.error("[空日志]", f"选择交易品种失败: {symbol}")
                return None

        # 设置订单类型
        mt5_order_type = None
        if order_type == "buy_stop":
            mt5_order_type = mt5.ORDER_TYPE_BUY_STOP
            # 计算止盈价格（如果提供了止盈点数）
            tp_price = price + tp_points * symbol_info.point if tp_points > 0 else 0
        elif order_type == "sell_stop":
            mt5_order_type = mt5.ORDER_TYPE_SELL_STOP
            # 计算止盈价格（如果提供了止盈点数）
            tp_price = price - tp_points * symbol_info.point if tp_points > 0 else 0
        else:
            # print(f"不支持的订单类型: {order_type}")
            return None

        # 准备订单请求
        request = {
            "action": mt5.TRADE_ACTION_PENDING,
            "symbol": symbol,
            "volume": volume,
            "type": mt5_order_type,
            "price": price,
            "deviation": 20,
            "magic": 234000,
            "comment": comment,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }

        # 添加止损价格（如果提供）
        if sl_price:
            request["sl"] = sl_price

        # 添加止盈价格（如果计算了）
        if tp_price:
            request["tp"] = tp_price

        # 发送订单
        result = mt5.order_send(request)
        if result is None or result.retcode != mt5.TRADE_RETCODE_DONE:
            logger.error(
                f"[空日志] 挂单失败，错误代码：{result.retcode}，描述：{result.comment}"
            )
            return None

        return result.order

    except Exception as e:
        # print(f"挂单出错：{str(e)}")
        return None


def place_order_with_key_level_sl(
    symbol: str,
    order_type: str,
    volume: float,
    sl_price: float,
    tp_points: int = 0,
    comment: str = "",
) -> Optional[int]:
    """
    下单，使用K线关键位作为止损价格

    Args:
        symbol: 交易品种
        order_type: 订单类型 ('buy' 或 'sell')
        volume: 交易量
        sl_price: 止损价格（直接指定价格而非点数）
        tp_points: 止盈点数
        comment: 订单注释

    Returns:
        订单号，失败返回None
    """
    try:
        # 获取交易品种信息
        symbol_info = mt5.symbol_info(symbol)
        if symbol_info is None:
            logger.error("[空日志]", f"获取{symbol}信息失败")
            return None

        # 确保交易品种可见
        if not symbol_info.visible:
            if not mt5.symbol_select(symbol, True):
                logger.error("[空日志]", f"选择交易品种失败: {symbol}")
                return None

        # 设置订单类型
        mt5_order_type = None
        if order_type == "buy":
            mt5_order_type = mt5.ORDER_TYPE_BUY
            # 当前买入价格
            price = symbol_info.ask
            # 计算止盈价格（如果提供了止盈点数）
            tp_price = price + tp_points * symbol_info.point if tp_points > 0 else 0
        elif order_type == "sell":
            mt5_order_type = mt5.ORDER_TYPE_SELL
            # 当前卖出价格
            price = symbol_info.bid
            # 计算止盈价格（如果提供了止盈点数）
            tp_price = price - tp_points * symbol_info.point if tp_points > 0 else 0
        else:
            # print(f"不支持的订单类型: {order_type}")
            return None

        # 准备订单请求
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": volume,
            "type": mt5_order_type,
            "price": price,
            "deviation": 20,
            "magic": 234000,
            "comment": comment,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }

        # 添加止损价格
        if sl_price:
            request["sl"] = sl_price

        # 添加止盈价格（如果计算了）
        if tp_price:
            request["tp"] = tp_price

        # 发送订单
        result = mt5.order_send(request)
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            logger.error(
                "[空日志]",
                f"下单失败，错误代码：{result.retcode}，描述：{result.comment}",
            )
            return None

        return result.order

    except Exception as e:
        # print(f"下单出错：{str(e)}")
        return None


def modify_position_sl_tp(ticket: int, sl: float = None, tp: float = None) -> bool:
    """
    修改持仓的止损止盈

    Args:
        ticket: 持仓订单号
        sl: 新的止损价格，None表示不修改
        tp: 新的止盈价格，None表示不修改

    Returns:
        是否修改成功
    """
    try:
        # 获取持仓信息
        position = mt5.positions_get(ticket=ticket)
        if not position:
            # print(f"未找到持仓: {ticket}")
            return False

        position = position[0]._asdict()

        # 准备修改请求
        request = {
            "action": mt5.TRADE_ACTION_SLTP,
            "symbol": position["symbol"],
            "position": ticket,
        }

        # 只有当参数不为None时才添加到请求中
        if sl is not None:
            request["sl"] = sl
        else:
            # 如果不修改止损，保持原来的止损价格
            request["sl"] = position["sl"]

        if tp is not None:
            request["tp"] = tp
        else:
            # 如果不修改止盈，保持原来的止盈价格
            request["tp"] = position["tp"]

        # 发送修改请求
        result = mt5.order_send(request)
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            # print(
            # f"修改止损止盈失败，错误代码：{result.retcode}，描述：{result.comment}"
            # )
            return False

        return True

    except Exception as e:
        # print(f"修改止损止盈出错：{str(e)}")
        return False
