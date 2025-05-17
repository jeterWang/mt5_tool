"""
交易数据库模块

管理交易系统的数据存储和记录，包括交易次数统计和风控事件记录
"""

import sqlite3
from datetime import datetime, timedelta
import os
from utils.paths import get_data_path
from config.loader import TRADING_DAY_RESET_HOUR
import logging


class TradeDatabase:
    """交易数据库类，用于记录交易历史和风控事件"""

    def __init__(self):
        """初始化数据库"""
        self.db_path = get_data_path("trade_history.db")
        self.conn = None
        self.create_tables()

    def create_tables(self):
        """创建数据库表"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            cursor = self.conn.cursor()

            # 创建交易计数表
            cursor.execute(
                """
            CREATE TABLE IF NOT EXISTS trade_count (
                id INTEGER PRIMARY KEY,
                date TEXT,
                count INTEGER
            )
            """
            )

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

            self.conn.commit()
        except Exception as e:
            logging.error(f"创建数据库表出错: {str(e)}")
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

    def get_today_count(self):
        """获取今日交易次数"""
        today = self.get_trading_day()
        try:
            self.conn = sqlite3.connect(self.db_path)
            cursor = self.conn.cursor()
            cursor.execute("SELECT count FROM trade_count WHERE date = ?", (today,))
            result = cursor.fetchone()
            if result:
                return result[0]
            return 0
        except Exception as e:
            logging.error(f"获取今日交易次数出错: {str(e)}")
            return 0
        finally:
            if self.conn:
                self.conn.close()

    def increment_count(self):
        """增加今日交易次数"""
        today = self.get_trading_day()
        try:
            self.conn = sqlite3.connect(self.db_path)
            cursor = self.conn.cursor()

            # 查询今日记录是否存在
            cursor.execute("SELECT count FROM trade_count WHERE date = ?", (today,))
            result = cursor.fetchone()

            if result:
                # 如果记录存在，增加计数
                new_count = result[0] + 1
                cursor.execute(
                    "UPDATE trade_count SET count = ? WHERE date = ?",
                    (new_count, today),
                )
            else:
                # 如果记录不存在，创建新记录
                cursor.execute(
                    "INSERT INTO trade_count (date, count) VALUES (?, ?)", (today, 1)
                )

            self.conn.commit()
            return True
        except Exception as e:
            logging.error(f"增加交易次数出错: {str(e)}")
            return False
        finally:
            if self.conn:
                self.conn.close()

    def get_history(self, days: int = 7) -> list:
        """获取最近几天的交易历史"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            cursor = self.conn.cursor()

            cursor.execute(
                """
                SELECT date, count FROM trade_count 
                ORDER BY date DESC LIMIT ?
            """,
                (days,),
            )

            history = cursor.fetchall()
            return history

        except Exception as e:
            logging.error(f"获取交易历史出错: {str(e)}")
            return []
        finally:
            if self.conn:
                self.conn.close()

    def record_risk_event(self, event_type, details):
        """记录风控事件"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            self.conn = sqlite3.connect(self.db_path)
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT INTO risk_events (timestamp, event_type, details) VALUES (?, ?, ?)",
                (timestamp, event_type, details),
            )
            self.conn.commit()
            return True
        except Exception as e:
            logging.error(f"记录风控事件出错: {str(e)}")
            return False
        finally:
            if self.conn:
                self.conn.close()

    def get_risk_events(self, days=7):
        """获取最近n天的风控事件"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT * FROM risk_events ORDER BY timestamp DESC LIMIT 100"
            )
            return cursor.fetchall()
        except Exception as e:
            logging.error(f"获取风控事件出错: {str(e)}")
            return []
        finally:
            if self.conn:
                self.conn.close()
