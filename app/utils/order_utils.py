def calc_stoploss_price(order_type, entry_price, sl_points, point, spread=0.0):
    """
    统一止损价计算函数。
    买入止损不加spread，卖出止损加spread。

    Args:
        order_type (str): 'buy' 或 'sell'
        entry_price (float): 入场价
        sl_points (float): 止损点数
        point (float): 品种点值
        spread (float): 点差，默认0
    Returns:
        float: 止损价
    """
    if order_type == "buy":
        return entry_price - sl_points * point
    elif order_type == "sell":
        return entry_price + sl_points * point + spread
    else:
        raise ValueError(f"未知order_type: {order_type}")
