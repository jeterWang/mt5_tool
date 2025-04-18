import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime
import time
from typing import List, Dict, Optional
import os
from dotenv import load_dotenv

class MT5Trader:
    def __init__(self, login: int, password: str, server: str):
        """
        初始化MT5交易类
        :param login: MT5账号
        :param password: MT5密码
        :param server: MT5服务器
        """
        self.login = login
        self.password = password
        self.server = server
        self.connected = False
        self.connect()

    def connect(self) -> bool:
        """连接到MT5平台"""
        if not mt5.initialize():
            print(f"初始化失败: {mt5.last_error()}")
            return False

        if not mt5.login(login=self.login, password=self.password, server=self.server):
            print(f"登录失败: {mt5.last_error()}")
            return False

        self.connected = True
        print("MT5连接成功")
        return True

    def disconnect(self):
        """断开MT5连接"""
        mt5.shutdown()
        self.connected = False

    def place_order(self, 
                   symbol: str, 
                   order_type: str, 
                   volume: float,
                   price: Optional[float] = None,
                   sl: Optional[float] = None,
                   tp: Optional[float] = None,
                   comment: str = "") -> Optional[int]:
        """
        下单函数
        :param symbol: 交易品种
        :param order_type: 订单类型 ('buy' 或 'sell')
        :param volume: 交易量
        :param price: 价格（市价单为None）
        :param sl: 止损价格
        :param tp: 止盈价格
        :param comment: 订单注释
        :return: 订单号
        """
        if not self.connected:
            print("未连接到MT5")
            return None

        symbol_info = mt5.symbol_info(symbol)
        if symbol_info is None:
            print(f"未找到交易品种: {symbol}")
            return None

        if not symbol_info.visible:
            if not mt5.symbol_select(symbol, True):
                print(f"选择交易品种失败: {symbol}")
                return None

        point = symbol_info.point
        if order_type.lower() == "buy":
            order_type = mt5.ORDER_TYPE_BUY
        elif order_type.lower() == "sell":
            order_type = mt5.ORDER_TYPE_SELL
        else:
            print("无效的订单类型")
            return None

        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": volume,
            "type": order_type,
            "price": price or mt5.symbol_info_tick(symbol).ask if order_type == mt5.ORDER_TYPE_BUY else mt5.symbol_info_tick(symbol).bid,
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
            print(f"下单失败: {result.comment}")
            return None

        return result.order

    def place_order_with_tp_sl(self, symbol: str, order_type: str, volume: float, 
                             sl_points: int = 0, tp_points: int = 0, price: float = None, comment: str = ""):
        """下单（支持挂单）"""
        try:
            # 获取当前价格
            symbol_info = mt5.symbol_info(symbol)
            if symbol_info is None:
                print(f"获取{symbol}信息失败")
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
                "action": mt5.TRADE_ACTION_DEAL if price is None else mt5.TRADE_ACTION_PENDING,
                "symbol": symbol,
                "volume": volume,
                "type": mt5.ORDER_TYPE_BUY if order_type == "buy" else mt5.ORDER_TYPE_SELL,
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
                print(f"下单失败，错误代码：{result.retcode}")
                return None
                
            return result.order
        except Exception as e:
            print(f"下单出错：{str(e)}")
            return None

    def place_order_with_partial_tp(self,
                                  symbol: str,
                                  order_type: str,
                                  volume: float,
                                  sl_points: float,
                                  tp_levels: List[Dict[str, float]],
                                  comment: str = "") -> Optional[int]:
        """
        带分批止盈的下单函数
        :param symbol: 交易品种
        :param order_type: 订单类型 ('buy' 或 'sell')
        :param volume: 交易量
        :param sl_points: 止损点数
        :param tp_levels: 分批止盈设置列表，每个元素为字典，包含 'points' 和 'volume' 键
        :param comment: 订单注释
        :return: 主订单号
        """
        # 验证分批止盈设置
        total_volume = sum(level['volume'] for level in tp_levels)
        if total_volume > volume:
            print("分批止盈总量不能超过订单总量")
            return None

        # 创建主订单
        main_order = self.place_order_with_tp_sl(
            symbol, order_type, volume, sl_points, tp_levels[-1]['points'], comment
        )
        if not main_order:
            return None

        # 创建分批止盈订单
        for i, level in enumerate(tp_levels[:-1]):  # 除了最后一个止盈点
            tp_comment = f"{comment}_TP_{i+1}"
            self.place_order_with_tp_sl(
                symbol, order_type, level['volume'], sl_points, level['points'], comment
            )

        return main_order

    def get_position(self, ticket: int) -> Optional[Dict]:
        """
        获取持仓信息
        :param ticket: 订单号
        :return: 持仓信息字典
        """
        position = mt5.positions_get(ticket=ticket)
        if not position:
            return None
        return position[0]._asdict()

    def close_position(self, ticket: int) -> bool:
        """
        平仓
        :param ticket: 订单号
        :return: 是否成功
        """
        position = self.get_position(ticket)
        if not position:
            return False

        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": position["symbol"],
            "volume": position["volume"],
            "type": mt5.ORDER_TYPE_SELL if position["type"] == mt5.POSITION_TYPE_BUY else mt5.ORDER_TYPE_BUY,
            "position": ticket,
            "price": mt5.symbol_info_tick(position["symbol"]).bid if position["type"] == mt5.POSITION_TYPE_BUY else mt5.symbol_info_tick(position["symbol"]).ask,
            "deviation": 20,
            "magic": 234000,
            "comment": "close position",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }

        result = mt5.order_send(request)
        return result.retcode == mt5.TRADE_RETCODE_DONE

    def get_all_positions(self) -> List[Dict]:
        """
        获取所有持仓信息
        :return: 持仓信息列表
        """
        if not self.connected:
            return None
            
        try:
            positions = mt5.positions_get()
            if positions is None:
                return []
                
            return [position._asdict() for position in positions]
        except Exception as e:
            print(f"获取持仓信息出错：{str(e)}")
            return None

    def cancel_order(self, ticket: int) -> bool:
        """撤销指定订单"""
        try:
            # 获取订单信息
            order = mt5.orders_get(ticket=ticket)
            if order is None or len(order) == 0:
                print(f"未找到订单：{ticket}")
                return False
                
            order = order[0]
            
            # 准备撤销请求
            request = {
                "action": mt5.TRADE_ACTION_REMOVE,
                "order": ticket,
                "comment": "撤销订单"
            }
            
            # 发送撤销请求
            result = mt5.order_send(request)
            if result.retcode != mt5.TRADE_RETCODE_DONE:
                print(f"撤销订单失败，错误代码：{result.retcode}")
                return False
                
            return True
        except Exception as e:
            print(f"撤销订单出错：{str(e)}")
            return False

# 使用示例
if __name__ == "__main__":
    # 加载环境变量
    load_dotenv()
    
    # 创建交易实例
    trader = MT5Trader(
        login=int(os.getenv("MT5_LOGIN", "123456")),
        password=os.getenv("MT5_PASSWORD", "password"),
        server=os.getenv("MT5_SERVER", "server")
    )

    # 示例1：简单下单（带止盈止损）
    order1 = trader.place_order_with_tp_sl(
        symbol="EURUSD",
        order_type="buy",
        volume=0.1,
        sl_points=50,
        tp_points=100,
        comment="测试订单1"
    )

    # 示例2：分批止盈下单
    tp_levels = [
        {"points": 30, "volume": 0.03},  # 30点止盈，平仓0.03手
        {"points": 60, "volume": 0.03},  # 60点止盈，平仓0.03手
        {"points": 100, "volume": 0.04}  # 100点止盈，平仓0.04手
    ]
    
    order2 = trader.place_order_with_partial_tp(
        symbol="EURUSD",
        order_type="buy",
        volume=0.1,
        sl_points=50,
        tp_levels=tp_levels,
        comment="测试订单2"
    )

    # 断开连接
    trader.disconnect() 