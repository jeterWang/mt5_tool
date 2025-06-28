"""
交易数据库模块

管理交易系统的数据存储和记录，包括交易次数统计和风控事件记录
"""

import sqlite3
import logging
from app.orm_models import Base, TradeHistory, RiskEvent
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
import os
from utils.paths import get_data_path
from config.loader import TRADING_DAY_RESET_HOUR
import logging
import pandas as pd

logger = logging.getLogger(__name__)


class TradeDatabase:
    """交易数据库类，用于记录交易历史和风控事件"""

    def __init__(self):
        """初始化数据库"""
        self.db_path = get_data_path("trade_history.db")
        self.engine = create_engine(f"sqlite:///{self.db_path}")
        self.Session = sessionmaker(bind=self.engine)
        # 自动建表
        Base.metadata.create_all(self.engine)
        # print(f"初始化交易数据库: {self.db_path}")
        self.create_tables()

    def create_tables(self):
        """创建数据库表"""
        try:
            # print(f"连接数据库并创建表: {self.db_path}")
            self.conn = sqlite3.connect(self.db_path)
            cursor = self.conn.cursor()

            # 创建风控事件表
            cursor.execute(
                """
            CREATE TABLE IF NOT EXISTS risk_events (
                id INTEGER PRIMARY KEY,
                timestamp TEXT,
                event_type TEXT,
                details TEXT
            )
            """
            )

            # 创建历史订单明细表
            cursor.execute(
                """
            CREATE TABLE IF NOT EXISTS trade_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id TEXT UNIQUE,
                account TEXT,
                symbol TEXT,
                volume REAL,
                direction TEXT,
                open_time TEXT,
                close_time TEXT,
                trading_day TEXT,
                open_price REAL,
                close_price REAL,
                profit REAL,
                comment TEXT
            )
            """
            )

            # 创建索引
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_trade_history_order_id ON trade_history(order_id)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_trade_history_close_time ON trade_history(close_time)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_trade_history_trading_day ON trade_history(trading_day)"
            )

            self.conn.commit()
            # print("数据库表创建成功")

        except Exception as e:
            logging.error(f"创建数据库表出错: {str(e)}")
            # print(f"创建数据库表出错: {str(e)}")
        finally:
            if self.conn:
                self.conn.close()

    def get_trading_day(self):
        """
        获取当前交易日，考虑重置时间

        如果当前时间已经过了重置时间，使用当天日期，否则使用前一天日期
        """
        now = datetime.now()
        if now.hour >= TRADING_DAY_RESET_HOUR:
            return now.strftime("%Y-%m-%d")
        else:
            yesterday = now - timedelta(days=1)
            return yesterday.strftime("%Y-%m-%d")

    def get_today_count(self, account_id=None):
        """获取今日交易次数（基于trade_history聚合）"""
        today = self.get_trading_day()
        with self.Session() as session:
            q = session.query(func.count()).filter(TradeHistory.trading_day == today)
            if account_id:
                q = q.filter(TradeHistory.account == str(account_id))
            return q.scalar() or 0

    def get_today_count_merged(self, account_id=None, threshold_seconds=10) -> int:
        """获取今日交易次数（10秒内合并为一笔）"""
        today = self.get_trading_day()
        with self.Session() as session:
            q = session.query(TradeHistory).filter(TradeHistory.trading_day == today)
            if account_id:
                q = q.filter(TradeHistory.account == str(account_id))
            orders = q.order_by(TradeHistory.open_time.asc()).all()
            count = 0
            last_time = None
            for order in orders:
                if not order.open_time:
                    continue
                if (
                    last_time is None
                    or (order.open_time - last_time).total_seconds() > threshold_seconds
                ):
                    count += 1
                    last_time = order.open_time
            return count

    def get_history(self, days: int = 7, account_id=None) -> list:
        """获取最近几天的交易历史（基于trade_history聚合）"""
        with self.Session() as session:
            q = session.query(TradeHistory.trading_day, func.count())
            if account_id:
                q = q.filter(TradeHistory.account == str(account_id))
            q = (
                q.group_by(TradeHistory.trading_day)
                .order_by(TradeHistory.trading_day.desc())
                .limit(days)
            )
            return [(r[0], r[1]) for r in q.all()]

    def record_risk_event(self, event_type, details):
        """记录风控事件（ORM版）"""
        from datetime import datetime

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self.Session() as session:
            event = RiskEvent(
                timestamp=timestamp, event_type=event_type, details=details
            )
            session.add(event)
            session.commit()
            return True

    def get_risk_events(self, days=7):
        """获取最近n天的风控事件（ORM版）"""
        with self.Session() as session:
            events = (
                session.query(RiskEvent)
                .order_by(RiskEvent.timestamp.desc())
                .limit(100)
                .all()
            )
            return [(e.timestamp, e.event_type, e.details) for e in events]
