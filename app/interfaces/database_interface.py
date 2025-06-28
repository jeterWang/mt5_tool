"""
数据库接口定义

定义了数据库操作类应该实现的所有方法
这个接口基于现有的 TradeDatabase 类设计
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime


class IDatabase(ABC):
    """
    数据库操作抽象接口
    只保留与trade_history、风控等相关的接口
    """

    # === 基础操作 ===

    @abstractmethod
    def create_tables(self) -> None:
        """创建数据库表"""
        pass

    # === 交易日管理 ===

    @abstractmethod
    def get_trading_day(self) -> str:
        """
        获取当前交易日

        Returns:
            str: 交易日期字符串 (YYYY-MM-DD)
        """
        pass

    # === 历史记录 ===

    @abstractmethod
    def get_history(self, days: int = 7) -> List[Dict[str, Any]]:
        """
        获取历史交易记录

        Args:
            days: 获取最近几天的记录

        Returns:
            List[Dict]: 历史记录列表
        """
        pass

    # === 风控事件 ===

    @abstractmethod
    def record_risk_event(
        self,
        event_type: str,
        description: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        记录风控事件

        Args:
            event_type: 事件类型
            description: 事件描述
            metadata: 事件元数据

        Returns:
            bool: 记录是否成功
        """
        pass

    @abstractmethod
    def get_risk_events(self, days: int = 7) -> List[Dict[str, Any]]:
        """
        获取风控事件记录

        Args:
            days: 获取最近几天的记录

        Returns:
            List[Dict]: 风控事件列表
        """
        pass

    # === Excel同步 ===

    @abstractmethod
    def auto_update_trade_count_from_xlsx(self, trader) -> bool:
        """
        从Excel文件自动更新交易计数

        Args:
            trader: 交易者对象（用于获取交易日）

        Returns:
            bool: 更新是否成功
        """
        pass

    @abstractmethod
    def filter_today_trades(self, df_trades, trading_day: str) -> Any:
        """
        过滤今日交易记录

        Args:
            df_trades: 交易记录DataFrame
            trading_day: 交易日

        Returns:
            Any: 过滤后的交易记录
        """
        pass

    @abstractmethod
    def merge_trades_within_1min(self, df_today) -> Any:
        """
        合并1分钟内的交易记录

        Args:
            df_today: 今日交易记录

        Returns:
            Any: 合并后的交易记录
        """
        pass


class IDatabaseFactory(ABC):
    """
    数据库工厂接口

    用于创建不同类型的数据库实例
    可以支持SQLite、MySQL、PostgreSQL等不同的数据库后端
    """

    @abstractmethod
    def create_database(self, db_path: str, **kwargs) -> IDatabase:
        """
        创建数据库实例

        Args:
            db_path: 数据库路径或连接字符串
            **kwargs: 其他配置参数

        Returns:
            IDatabase: 数据库操作接口实例
        """
        pass

    @abstractmethod
    def get_database_type(self) -> str:
        """
        获取数据库类型

        Returns:
            str: 数据库类型 (sqlite, mysql, postgresql等)
        """
        pass
