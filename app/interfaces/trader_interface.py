"""
交易者接口定义

定义了交易者类应该实现的所有方法
这个接口基于现有的 MT5Trader 类设计，但提供了抽象层
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime


class ITrader(ABC):
    """
    交易者抽象接口
    
    定义了所有交易相关操作的契约
    现有的MT5Trader类可以实现这个接口，而不需要修改现有代码
    """
    
    # === 连接管理 ===
    
    @abstractmethod
    def connect(self) -> bool:
        """
        连接到交易服务器
        
        Returns:
            bool: 连接是否成功
        """
        pass
    
    @abstractmethod
    def disconnect(self) -> None:
        """断开连接"""
        pass
    
    @abstractmethod
    def is_connected(self) -> bool:
        """
        检查连接状态
        
        Returns:
            bool: 是否已连接
        """
        pass
    
    # === 账户信息 ===
    
    @abstractmethod
    def get_account_info(self) -> Optional[Dict[str, Any]]:
        """
        获取账户信息
        
        Returns:
            Optional[Dict]: 账户信息字典，包含余额、净值等
        """
        pass
    
    @abstractmethod
    def _get_account_id(self) -> str:
        """
        获取账户ID
        
        Returns:
            str: 账户ID
        """
        pass
    
    # === 仓位管理 ===
    
    @abstractmethod
    def get_all_positions(self) -> Optional[List[Dict[str, Any]]]:
        """
        获取所有持仓
        
        Returns:
            Optional[List[Dict]]: 持仓列表
        """
        pass
    
    @abstractmethod
    def get_position(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        获取指定品种的持仓
        
        Args:
            symbol: 交易品种
            
        Returns:
            Optional[Dict]: 持仓信息
        """
        pass
    
    @abstractmethod
    def get_positions_by_symbol_and_type(self, symbol: str, position_type: str) -> List[Dict[str, Any]]:
        """
        根据品种和类型获取持仓
        
        Args:
            symbol: 交易品种
            position_type: 持仓类型
            
        Returns:
            List[Dict]: 符合条件的持仓列表
        """
        pass
    
    # === 交易操作 ===
    
    @abstractmethod
    def place_order(self, symbol: str, order_type: str, volume: float, 
                   price: Optional[float] = None, **kwargs) -> bool:
        """
        下单
        
        Args:
            symbol: 交易品种
            order_type: 订单类型
            volume: 交易量
            price: 价格（市价单可为None）
            **kwargs: 其他参数
            
        Returns:
            bool: 下单是否成功
        """
        pass
    
    @abstractmethod
    def place_order_with_tp_sl(self, symbol: str, order_type: str, volume: float,
                              tp_points: Optional[float] = None, 
                              sl_points: Optional[float] = None, **kwargs) -> bool:
        """
        带止盈止损的下单
        
        Args:
            symbol: 交易品种
            order_type: 订单类型  
            volume: 交易量
            tp_points: 止盈点数
            sl_points: 止损点数
            **kwargs: 其他参数
            
        Returns:
            bool: 下单是否成功
        """
        pass
    
    @abstractmethod
    def place_order_with_key_level_sl(self, symbol: str, order_type: str, volume: float,
                                     tp_points: Optional[float] = None,
                                     sl_candle_count: int = 3, **kwargs) -> bool:
        """
        带关键位止损的下单
        
        Args:
            symbol: 交易品种
            order_type: 订单类型
            volume: 交易量
            tp_points: 止盈点数
            sl_candle_count: 止损K线数量
            **kwargs: 其他参数
            
        Returns:
            bool: 下单是否成功
        """
        pass
    
    @abstractmethod
    def place_pending_order(self, symbol: str, order_type: str, volume: float,
                           price: float, **kwargs) -> bool:
        """
        下挂单
        
        Args:
            symbol: 交易品种
            order_type: 订单类型
            volume: 交易量
            price: 挂单价格
            **kwargs: 其他参数
            
        Returns:
            bool: 下单是否成功
        """
        pass
    
    @abstractmethod
    def place_order_with_partial_tp(self, symbol: str, order_type: str, volume: float,
                                   tp_levels: List[Tuple[float, float]], **kwargs) -> bool:
        """
        带分批止盈的下单
        
        Args:
            symbol: 交易品种
            order_type: 订单类型
            volume: 交易量
            tp_levels: 止盈级别列表 [(价格1, 数量1), (价格2, 数量2)]
            **kwargs: 其他参数
            
        Returns:
            bool: 下单是否成功
        """
        pass
    
    @abstractmethod
    def close_position(self, symbol: str, volume: Optional[float] = None) -> bool:
        """
        平仓
        
        Args:
            symbol: 交易品种
            volume: 平仓量（None表示全部平仓）
            
        Returns:
            bool: 平仓是否成功
        """
        pass
    
    @abstractmethod
    def cancel_order(self, order_id: int) -> bool:
        """
        取消订单
        
        Args:
            order_id: 订单ID
            
        Returns:
            bool: 取消是否成功
        """
        pass
    
    @abstractmethod
    def modify_position_sl_tp(self, symbol: str, sl_price: Optional[float] = None,
                            tp_price: Optional[float] = None) -> bool:
        """
        修改持仓止损止盈
        
        Args:
            symbol: 交易品种
            sl_price: 止损价格
            tp_price: 止盈价格
            
        Returns:
            bool: 修改是否成功
        """
        pass
    
    # === 数据获取 ===
    
    @abstractmethod
    def get_trading_day(self) -> str:
        """
        获取当前交易日
        
        Returns:
            str: 交易日期字符串 (YYYY-MM-DD)
        """
        pass
    
    @abstractmethod
    def get_trading_day_from_datetime(self, dt: datetime) -> str:
        """
        从datetime获取交易日
        
        Args:
            dt: 日期时间对象
            
        Returns:
            str: 交易日期字符串 (YYYY-MM-DD)
        """
        pass
    
    @abstractmethod
    def get_symbol_params(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        获取品种参数
        
        Args:
            symbol: 交易品种
            
        Returns:
            Optional[Dict]: 品种参数字典
        """
        pass
    
    @abstractmethod
    def get_all_symbols(self) -> List[str]:
        """
        获取所有可交易品种
        
        Returns:
            List[str]: 品种列表
        """
        pass
    
    # === 数据同步 ===
    
    @abstractmethod
    def sync_closed_trades_to_excel(self, file_path: str) -> bool:
        """
        同步已平仓交易到Excel
        
        Args:
            file_path: Excel文件路径
            
        Returns:
            bool: 同步是否成功
        """
        pass