import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime
import time
from typing import List, Dict, Optional
import os
from dotenv import load_dotenv

class MT5Trader:
    def __init__(self):
        """初始化交易者"""
        self.connected = False
        
    def connect(self) -> bool:
        """连接到MT5"""
        try:
            if not mt5.initialize():
                print("MT5初始化失败")
                return False
                
            # 检查是否已经登录
            account_info = mt5.account_info()
            if account_info is None:
                print("未检测到MT5登录账号，请先在MT5中登录")
                return False
                
            self.connected = True
            return True
        except Exception as e:
            print(f"连接MT5出错: {str(e)}")
            return False

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
        for i, level in enumerate(tp_levels[:-1]):
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

    def is_connected(self) -> bool:
        """检查是否已连接到MT5"""
        return self.connected

    def get_account_info(self):
        """获取账户信息"""
        try:
            account_info = mt5.account_info()
            if account_info is None:
                return None
            return {
                "balance": account_info.balance,
                "equity": account_info.equity,
                "margin": account_info.margin,
                "free_margin": account_info.margin_free,
                "margin_level": account_info.margin_level
            }
        except Exception as e:
            print(f"获取账户信息失败: {str(e)}")
            return None

    def _record_trade_to_excel(self, account_id, trade_info):
        """
        记录交易到excel，按账号分sheet
        :param account_id: 账号ID
        :param trade_info: 交易信息dict
        """
        data_dir = 'data'
        os.makedirs(data_dir, exist_ok=True)
        file_path = os.path.join(data_dir, 'trade_records.xlsx')
        sheet_name = str(account_id)
        df_new = pd.DataFrame([trade_info])
        if os.path.exists(file_path):
            with pd.ExcelWriter(file_path, engine='openpyxl', mode='a', if_sheet_exists='overlay') as writer:
                try:
                    df_old = pd.read_excel(file_path, sheet_name=sheet_name)
                    df_all = pd.concat([df_old, df_new], ignore_index=True)
                except Exception:
                    df_all = df_new
                df_all.to_excel(writer, sheet_name=sheet_name, index=False)
        else:
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                df_new.to_excel(writer, sheet_name=sheet_name, index=False)

    def _get_account_id(self):
        info = mt5.account_info()
        return info.login if info else 'unknown'

    def sync_closed_trades_to_excel(self):
        """
        扫描近3天所有平仓单（包括自动止损/止盈），并将未记录过的平仓单写入excel。
        只用order_id（position_id）去重。
        建议每分钟调用一次。
        """
        from openpyxl import load_workbook
        from datetime import timedelta
        start_time = datetime.now() - timedelta(days=3)
        deals = mt5.history_deals_get(start_time, datetime.now())
        if deals is None:
            print('未获取到历史成交（deals）')
            return
        print(f'开始同步平仓单，deals数量: {len(deals)}')
        for deal in deals:
            print(f'deal_id={deal.ticket}, position_id={deal.position_id}, symbol={deal.symbol}, entry={deal.entry}, type={deal.type}, volume={deal.volume}, price={deal.price}, profit={deal.profit}, comment={deal.comment}')
        # 按账号分组
        account_id = self._get_account_id()
        data_dir = 'data'
        os.makedirs(data_dir, exist_ok=True)
        file_path = os.path.join(data_dir, 'trade_records.xlsx')
        sheet_name = str(account_id)
        # 读取已记录的order_id（position_id）
        recorded_order_ids = set()
        if os.path.exists(file_path):
            try:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
                if 'order_id' in df.columns:
                    recorded_order_ids = set(df['order_id'].astype(str))
            except Exception:
                pass
        # 遍历所有平仓deal
        new_records = []
        for deal in deals:
            if deal.entry != mt5.DEAL_ENTRY_OUT:
                continue
            order_id = str(deal.position_id)
            if order_id in recorded_order_ids:
                continue
            # 获取开仓deal
            open_deal = None
            for d in deals:
                if hasattr(d, 'position_id') and d.position_id == deal.position_id and d.entry == mt5.DEAL_ENTRY_IN:
                    open_deal = d
                    break
            open_time = datetime.fromtimestamp(open_deal.time) if open_deal else ''
            open_price = open_deal.price if open_deal else ''
            close_time = datetime.fromtimestamp(deal.time)
            close_price = deal.price
            profit = deal.profit
            direction = 'buy' if deal.type == mt5.ORDER_TYPE_BUY else 'sell'
            close_info = {
                'close_time': close_time.strftime('%Y-%m-%d %H:%M:%S'),
                'order_id': order_id,
                'account': account_id,
                'symbol': deal.symbol,
                'volume': deal.volume,
                'direction': direction,
                'open_price': open_price,
                'close_price': close_price,
                'open_time': open_time.strftime('%Y-%m-%d %H:%M:%S') if open_time else '',
                'profit': profit,
                'comment': deal.comment
            }
            print(f'发现新平仓单，准备写入excel: {close_info}')
            new_records.append(close_info)
        if new_records:
            df_new = pd.DataFrame(new_records)
            if os.path.exists(file_path):
                with pd.ExcelWriter(file_path, engine='openpyxl', mode='a', if_sheet_exists='overlay') as writer:
                    try:
                        df_old = pd.read_excel(file_path, sheet_name=sheet_name)
                        df_all = pd.concat([df_old, df_new], ignore_index=True)
                    except Exception:
                        df_all = df_new
                    df_all.to_excel(writer, sheet_name=sheet_name, index=False)
            else:
                with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                    df_new.to_excel(writer, sheet_name=sheet_name, index=False)
            print(f'已写入{len(new_records)}条新平仓单到excel')
        else:
            print('本次无新平仓单写入excel')

# 使用示例
if __name__ == "__main__":
    # 加载环境变量
    load_dotenv()
    
    # 创建交易实例
    trader = MT5Trader()

    # 连接到MT5
    if not trader.connect():
        print("无法连接到MT5")
        exit(1)

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