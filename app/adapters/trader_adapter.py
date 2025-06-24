"""
MT5Trader适配器

将现有的MT5Trader类适配到ITrader接口
这样可以在不修改现有代码的情况下实现接口兼容性
"""

from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime

from ..interfaces.trader_interface import ITrader


class MT5TraderAdapter(ITrader):
    """
    MT5Trader适配器类
    
    将现有的MT5Trader实例包装成符合ITrader接口的对象
    
    用法示例:
        # 现有代码保持不变
        trader = MT5Trader()
        
        # 需要接口时，用适配器包装
        trader_interface = MT5TraderAdapter(trader)
        
        # 现在可以把trader_interface当作ITrader使用
        process_trader(trader_interface)
    """
    
    def __init__(self, mt5_trader):
        """
        初始化适配器
        
        Args:
            mt5_trader: 现有的MT5Trader实例
        """
        self._trader = mt5_trader
    
    # === 连接管理 ===
    
    def connect(self) -> bool:
        """连接到交易服务器"""
        return self._trader.connect()
    
    def disconnect(self) -> None:
        """断开连接"""
        return self._trader.disconnect()
    
    def is_connected(self) -> bool:
        """检查连接状态"""
        return self._trader.is_connected()
    
    # === 账户信息 ===
    
    def get_account_info(self) -> Optional[Dict[str, Any]]:
        """获取账户信息"""
        return self._trader.get_account_info()
    
    def _get_account_id(self) -> str:
        """获取账户ID"""
        return self._trader._get_account_id()
    
    # === 仓位管理 ===
    
    def get_all_positions(self) -> Optional[List[Dict[str, Any]]]:
        """获取所有持仓"""
        return self._trader.get_all_positions()
    
    def get_position(self, symbol: str) -> Optional[Dict[str, Any]]:
        """获取指定品种的持仓"""
        return self._trader.get_position(symbol)
    
    def get_positions_by_symbol_and_type(self, symbol: str, position_type: str) -> List[Dict[str, Any]]:
        """根据品种和类型获取持仓"""
        return self._trader.get_positions_by_symbol_and_type(symbol, position_type)
    
    # === 交易操作 ===
    
    def place_order(self, symbol: str, order_type: str, volume: float, 
                   price: Optional[float] = None, **kwargs) -> bool:
        """下单"""
        return self._trader.place_order(symbol, order_type, volume, price, **kwargs)
    
    def place_order_with_tp_sl(self, symbol: str, order_type: str, volume: float,
                              tp_points: Optional[float] = None, 
                              sl_points: Optional[float] = None, **kwargs) -> bool:
        """带止盈止损的下单"""
        return self._trader.place_order_with_tp_sl(symbol, order_type, volume, tp_points, sl_points, **kwargs)
    
    def place_order_with_key_level_sl(self, symbol: str, order_type: str, volume: float,
                                     tp_points: Optional[float] = None,
                                     sl_candle_count: int = 3, **kwargs) -> bool:
        """带关键位止损的下单"""
        return self._trader.place_order_with_key_level_sl(symbol, order_type, volume, tp_points, sl_candle_count, **kwargs)
    
    def place_pending_order(self, symbol: str, order_type: str, volume: float,
                           price: float, **kwargs) -> bool:
        """下挂单"""
        return self._trader.place_pending_order(symbol, order_type, volume, price, **kwargs)
    
    def place_order_with_partial_tp(self, symbol: str, order_type: str, volume: float,
                                   tp_levels: List[Tuple[float, float]], **kwargs) -> bool:
        """带分批止盈的下单"""
        return self._trader.place_order_with_partial_tp(symbol, order_type, volume, tp_levels, **kwargs)
    
    def close_position(self, symbol: str, volume: Optional[float] = None) -> bool:
        """平仓"""
        return self._trader.close_position(symbol, volume)
    
    def cancel_order(self, order_id: int) -> bool:
        """取消订单"""
        return self._trader.cancel_order(order_id)
    
    def modify_position_sl_tp(self, symbol: str, sl_price: Optional[float] = None,
                            tp_price: Optional[float] = None) -> bool:
        """修改持仓止损止盈"""
        return self._trader.modify_position_sl_tp(symbol, sl_price, tp_price)
    
    # === 数据获取 ===
    
    def get_trading_day(self) -> str:
        """获取当前交易日"""
        return self._trader.get_trading_day()
    
    def get_trading_day_from_datetime(self, dt: datetime) -> str:
        """从datetime获取交易日"""
        return self._trader.get_trading_day_from_datetime(dt)
    
    def get_symbol_params(self, symbol: str) -> Optional[Dict[str, Any]]:
        """获取品种参数"""
        return self._trader.get_symbol_params(symbol)
    
    def get_all_symbols(self) -> List[str]:
        """获取所有可交易品种"""
        return self._trader.get_all_symbols()
    
    # === 数据同步 ===
    
    def sync_closed_trades_to_excel(self, file_path: str) -> bool:
        """同步已平仓交易到Excel"""
        return self._trader.sync_closed_trades_to_excel(file_path)
    
    # === 额外的便捷方法 ===
    
    def get_original_trader(self):
        """
        获取原始的MT5Trader实例
        
        在需要访问原始对象特有方法时使用
        
        Returns:
            MT5Trader: 原始交易者实例
        """
        return self._trader
    
    @property
    def connected(self) -> bool:
        """连接状态属性"""
        return getattr(self._trader, 'connected', False)


# === 工厂函数 ===

def create_trader_interface(mt5_trader) -> ITrader:
    """
    创建交易者接口实例的工厂函数
    
    Args:
        mt5_trader: MT5Trader实例
        
    Returns:
        ITrader: 交易者接口实例
    """
    return MT5TraderAdapter(mt5_trader)