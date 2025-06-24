"""
接口使用示例

展示如何在不修改现有代码的情况下使用新的接口系统
这些示例展示了接口的价值和使用方法
"""

from typing import List, Dict, Any, Optional, Tuple
from ..interfaces.trader_interface import ITrader
from ..interfaces.database_interface import IDatabase
from ..adapters.trader_adapter import MT5TraderAdapter


# === 1. 依赖注入示例 ===

class TradingService:
    """
    交易服务类 - 使用接口而不是具体实现
    
    这个类可以使用任何实现了ITrader接口的交易者，
    不仅仅是MT5Trader，也可以是其他broker的实现
    """
    
    def __init__(self, trader: ITrader, database: IDatabase):
        self.trader = trader
        self.database = database
    
    def execute_trade(self, symbol: str, volume: float) -> bool:
        """
        执行交易的业务逻辑
        
        这个方法不关心trader的具体实现，只要实现了ITrader接口即可
        """
        # 检查连接
        if not self.trader.is_connected():
            if not self.trader.connect():
                return False
        
        # 获取当前持仓
        position = self.trader.get_position(symbol)
        
        # 检查交易次数限制
        today_count = self.database.get_today_count()
        if today_count >= 10:  # 假设限制10次
            self.database.record_risk_event(
                "TRADE_LIMIT_EXCEEDED", 
                f"今日交易次数已达限制: {today_count}"
            )
            return False
        
        # 执行交易
        success = self.trader.place_order(symbol, "BUY", volume)
        
        if success:
            # 增加交易计数
            self.database.increment_count()
        
        return success


# === 2. 策略模式示例 ===

class TradingStrategy:
    """交易策略基类"""
    
    def execute(self, trader: ITrader, symbol: str) -> bool:
        raise NotImplementedError


class BreakoutStrategy(TradingStrategy):
    """突破策略"""
    
    def execute(self, trader: ITrader, symbol: str) -> bool:
        # 获取品种参数
        params = trader.get_symbol_params(symbol)
        if not params:
            return False
        
        # 突破交易逻辑
        return trader.place_order_with_tp_sl(
            symbol, "BUY", 0.1, 
            tp_points=50, sl_points=30
        )


class ScalpingStrategy(TradingStrategy):
    """剥头皮策略"""
    
    def execute(self, trader: ITrader, symbol: str) -> bool:
        # 剥头皮交易逻辑
        return trader.place_order_with_tp_sl(
            symbol, "BUY", 0.05,
            tp_points=10, sl_points=5
        )


class StrategyExecutor:
    """策略执行器"""
    
    def __init__(self, trader: ITrader):
        self.trader = trader
        self.strategies = {}
    
    def register_strategy(self, name: str, strategy: TradingStrategy):
        """注册策略"""
        self.strategies[name] = strategy
    
    def execute_strategy(self, name: str, symbol: str) -> bool:
        """执行指定策略"""
        strategy = self.strategies.get(name)
        if not strategy:
            return False
        
        return strategy.execute(self.trader, symbol)


# === 3. 单元测试支持示例 ===

class MockTrader(ITrader):
    """
    模拟交易者 - 用于单元测试
    
    实现ITrader接口，但不执行真实交易
    可以验证业务逻辑而不依赖MT5连接
    """
    
    def __init__(self):
        self.connected = False
        self.positions = {}
        self.orders = []
        self.account_info = {
            'balance': 10000.0,
            'equity': 10000.0,
            'margin': 0.0
        }
    
    def connect(self) -> bool:
        self.connected = True
        return True
    
    def disconnect(self) -> None:
        self.connected = False
    
    def is_connected(self) -> bool:
        return self.connected
    
    def get_account_info(self) -> Optional[Dict[str, Any]]:
        return self.account_info if self.connected else None
    
    def _get_account_id(self) -> str:
        return "MOCK_ACCOUNT_12345"
    
    def get_all_positions(self) -> Optional[List[Dict[str, Any]]]:
        return list(self.positions.values()) if self.connected else None
    
    def get_position(self, symbol: str) -> Optional[Dict[str, Any]]:
        return self.positions.get(symbol) if self.connected else None
    
    def get_positions_by_symbol_and_type(self, symbol: str, position_type: str) -> List[Dict[str, Any]]:
        if not self.connected:
            return []
        position = self.positions.get(symbol)
        if position and position.get('type') == position_type:
            return [position]
        return []
    
    def place_order(self, symbol: str, order_type: str, volume: float, 
                   price=None, **kwargs) -> bool:
        if not self.connected:
            return False
        
        order = {
            'symbol': symbol,
            'type': order_type,
            'volume': volume,
            'price': price
        }
        self.orders.append(order)
        
        # 模拟成交，创建持仓
        self.positions[symbol] = {
            'symbol': symbol,
            'type': order_type,
            'volume': volume,
            'price': price or 1.0
        }
        return True
    
    def place_order_with_tp_sl(self, symbol: str, order_type: str, volume: float,
                              tp_points=None, sl_points=None, **kwargs) -> bool:
        return self.place_order(symbol, order_type, volume, **kwargs)
    
    def place_order_with_key_level_sl(self, symbol: str, order_type: str, volume: float,
                                     tp_points=None, sl_candle_count=3, **kwargs) -> bool:
        return self.place_order(symbol, order_type, volume, **kwargs)
    
    def place_pending_order(self, symbol: str, order_type: str, volume: float,
                           price: float, **kwargs) -> bool:
        return self.place_order(symbol, order_type, volume, price, **kwargs)
    
    def place_order_with_partial_tp(self, symbol: str, order_type: str, volume: float,
                                   tp_levels, **kwargs) -> bool:
        return self.place_order(symbol, order_type, volume, **kwargs)
    
    def close_position(self, symbol: str, volume=None) -> bool:
        if not self.connected:
            return False
        if symbol in self.positions:
            del self.positions[symbol]
            return True
        return False
    
    def cancel_order(self, order_id: int) -> bool:
        return self.connected
    
    def modify_position_sl_tp(self, symbol: str, sl_price=None, tp_price=None) -> bool:
        return self.connected
    
    def get_trading_day(self) -> str:
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d")
    
    def get_trading_day_from_datetime(self, dt) -> str:
        return dt.strftime("%Y-%m-%d")
    
    def get_symbol_params(self, symbol: str) -> Optional[Dict[str, Any]]:
        if not self.connected:
            return None
        return {
            'symbol': symbol,
            'digits': 5,
            'point': 0.00001,
            'spread': 1
        }
    
    def get_all_symbols(self) -> List[str]:
        return ['EURUSD', 'GBPUSD', 'USDJPY'] if self.connected else []
    
    def sync_closed_trades_to_excel(self, file_path: str) -> bool:
        return self.connected


# === 4. 使用示例函数 ===

def example_usage():
    """展示如何使用接口系统"""
    
    # === 现有代码保持不变 ===
    from app.trader.core import MT5Trader
    from app.database import TradeDatabase
    
    # 创建现有对象
    mt5_trader = MT5Trader()
    database = TradeDatabase()
    
    # === 新接口用法 ===
    
    # 1. 用适配器包装现有对象
    trader_interface = MT5TraderAdapter(mt5_trader)
    
    # 2. 创建使用接口的服务
    trading_service = TradingService(trader_interface, database)
    
    # 3. 执行交易（使用接口）
    success = trading_service.execute_trade("EURUSD", 0.1)
    
    # 4. 策略模式用法
    executor = StrategyExecutor(trader_interface)
    executor.register_strategy("breakout", BreakoutStrategy())
    executor.register_strategy("scalping", ScalpingStrategy())
    
    # 执行不同策略
    executor.execute_strategy("breakout", "EURUSD")
    executor.execute_strategy("scalping", "GBPUSD")
    
    # 5. 单元测试用法
    mock_trader = MockTrader()
    test_service = TradingService(mock_trader, database)
    
    # 可以测试业务逻辑而不需要真实的MT5连接
    test_success = test_service.execute_trade("EURUSD", 0.1)
    
    return success


def example_benefits():
    """
    接口系统的好处示例
    """
    # print("=== 接口系统的主要好处 ===")
    
    # print("1. 代码解耦:")
    # print("   - TradingService不依赖具体的MT5Trader实现")
    # print("   - 可以轻松替换为其他broker的交易者")
    
    # print("2. 便于测试:")
    # print("   - 可以用MockTrader进行单元测试")
    # print("   - 不需要真实的MT5连接就能测试业务逻辑")
    
    # print("3. 策略模式:")
    # print("   - 不同策略可以使用相同的接口")
    # print("   - 策略之间可以轻松切换")
    
    # print("4. 向后兼容:")
    # print("   - 现有代码完全不需要修改")
    # print("   - 通过适配器实现接口兼容")
    
    # print("5. 依赖注入:")
    # print("   - 服务类可以接收接口而不是具体实现")
    # print("   - 提高了代码的灵活性和可维护性")


if __name__ == "__main__":
    example_benefits()
    # example_usage()  # 取消注释来运行实际示例