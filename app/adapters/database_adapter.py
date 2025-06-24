"""
数据库适配器

将现有的TradeDatabase类适配到IDatabase接口
"""

from typing import Optional, List, Dict, Any
from datetime import datetime

from ..interfaces.database_interface import IDatabase


class DatabaseAdapter(IDatabase):
    """
    数据库适配器类
    
    将现有的TradeDatabase实例包装成符合IDatabase接口的对象
    """
    
    def __init__(self, database):
        """
        初始化适配器
        
        Args:
            database: 现有的TradeDatabase实例
        """
        self._database = database
    
    def create_tables(self) -> None:
        """创建数据库表"""
        return self._database.create_tables()
    
    def get_trading_day(self) -> str:
        """获取当前交易日"""
        return self._database.get_trading_day()
    
    def get_today_count(self) -> int:
        """获取今日交易次数"""
        return self._database.get_today_count()
    
    def increment_count(self) -> bool:
        """增加交易计数"""
        return self._database.increment_count()
    
    def set_today_count(self, count: int) -> bool:
        """设置今日交易次数"""
        return self._database.set_today_count(count)
    
    def get_history(self, days: int = 7) -> List[Dict[str, Any]]:
        """获取历史交易记录"""
        return self._database.get_history(days)
    
    def record_risk_event(self, event_type: str, description: str, 
                         metadata: Optional[Dict[str, Any]] = None) -> bool:
        """记录风控事件"""
        return self._database.record_risk_event(event_type, description, metadata)
    
    def get_risk_events(self, days: int = 7) -> List[Dict[str, Any]]:
        """获取风控事件记录"""
        return self._database.get_risk_events(days)
    
    def auto_update_trade_count_from_xlsx(self, trader) -> bool:
        """从Excel文件自动更新交易计数"""
        return self._database.auto_update_trade_count_from_xlsx(trader)
    
    def filter_today_trades(self, df_trades, trading_day: str):
        """过滤今日交易记录"""
        return self._database.filter_today_trades(df_trades, trading_day)
    
    def merge_trades_within_1min(self, df_today):
        """合并1分钟内的交易记录"""
        return self._database.merge_trades_within_1min(df_today)