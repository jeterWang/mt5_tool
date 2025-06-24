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
import pandas as pd


class TradeDatabase:
    """交易数据库类，用于记录交易历史和风控事件"""

    def __init__(self):
        """初始化数据库"""
        self.db_path = get_data_path("trade_history.db")
        self.conn = None
        # print(f"初始化交易数据库: {self.db_path}")
        self.create_tables()

    def create_tables(self):
        """创建数据库表"""
        try:
            # print(f"连接数据库并创建表: {self.db_path}")
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
            # print("数据库表创建成功")

            # 检查数据库是否包含今日交易记录
            today = self.get_trading_day()
            cursor.execute("SELECT count FROM trade_count WHERE date = ?", (today,))
            result = cursor.fetchone()
            # print(f"今日({today})交易记录: {result}")

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

    def get_today_count(self):
        """获取今日交易次数"""
        today = self.get_trading_day()
        try:
        # print(f"正在获取今日({today})交易次数，数据库路径: {self.db_path}")
            self.conn = sqlite3.connect(self.db_path)
            cursor = self.conn.cursor()
            cursor.execute("SELECT count FROM trade_count WHERE date = ?", (today,))
            result = cursor.fetchone()
            if result:
        # print(f"数据库中今日交易次数: {result[0]}")
                return result[0]
            # print("数据库中今日无交易记录")
            return 0
        except Exception as e:
            logging.error(f"获取今日交易次数出错: {str(e)}")
            # print(f"获取今日交易次数出错: {str(e)}")
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

    def set_today_count(self, count):
        """直接设置今日交易次数（用于从xlsx自动统计后更新）"""
        today = self.get_trading_day()
        try:
            self.conn = sqlite3.connect(self.db_path)
            cursor = self.conn.cursor()

            # 查询今日记录是否存在
            cursor.execute("SELECT count FROM trade_count WHERE date = ?", (today,))
            result = cursor.fetchone()

            if result:
                # 如果记录存在，更新计数
                cursor.execute(
                    "UPDATE trade_count SET count = ? WHERE date = ?",
                    (count, today),
                )
            else:
                # 如果记录不存在，创建新记录
                cursor.execute(
                    "INSERT INTO trade_count (date, count) VALUES (?, ?)",
                    (today, count),
                )

            self.conn.commit()
            # print(f"已更新今日({today})交易次数为: {count}")
            return True
        except Exception as e:
            logging.error(f"设置交易次数出错: {str(e)}")
            return False
        finally:
            if self.conn:
                self.conn.close()

    def auto_update_trade_count_from_xlsx(self, trader=None):
        """从trade_records.xlsx自动统计并更新交易次数"""
        try:
            data_dir = get_data_path()
            file_path = os.path.join(data_dir, "trade_records.xlsx")

            if not os.path.exists(file_path):
                # print("trade_records.xlsx文件不存在，跳过交易次数更新")
                return False

            # 获取账户ID
            account_id = "unknown"
            if trader and hasattr(trader, "_get_account_id"):
                try:
                    account_id = trader._get_account_id()
                except:
                    pass

            # 读取Excel文件
            try:
                df = pd.read_excel(file_path, sheet_name=str(account_id))
            except Exception as e:
                print(f"读取账户{account_id}的sheet失败: {e}")
                return False

            if df.empty or "open_time" not in df.columns:
                # print("xlsx文件为空或缺少open_time字段")
                return False

            # 获取交易日
            today = self.get_trading_day()
            # print(f"统计交易日 {today} 的交易次数")

            # 过滤今日交易记录
            today_trades = self.filter_today_trades(df, today)

            if today_trades.empty:
                # print(f"今日({today})无交易记录")
                self.set_today_count(0)
                return True

            # 合并1分钟内的交易为一笔
            merged_count = self.merge_trades_within_1min(today_trades)

            # 更新数据库
            self.set_today_count(merged_count)
            # print(
            #     f"今日共有 {len(today_trades)} 笔原始交易，合并后为 {merged_count} 笔"
            # )

            return True

        except Exception as e:
            logging.error(f"自动更新交易次数出错: {str(e)}")
            # print(f"自动更新交易次数出错: {str(e)}")
            return False

    def filter_today_trades(self, df, today):
        """根据交易日重置时间过滤今日交易"""
        try:
            # 确保open_time是datetime类型
            df["open_time"] = pd.to_datetime(df["open_time"])

            # 获取今日开始时间（考虑重置时间）
            today_date = datetime.strptime(today, "%Y-%m-%d")
            today_start = today_date.replace(
                hour=TRADING_DAY_RESET_HOUR, minute=0, second=0, microsecond=0
            )

            # 获取明日开始时间
            tomorrow_start = today_start + timedelta(days=1)

            # 过滤时间范围内的交易
            today_trades = df[
                (df["open_time"] >= today_start) & (df["open_time"] < tomorrow_start)
            ].copy()

            return today_trades.sort_values("open_time")

        except Exception as e:
            # print(f"过滤今日交易出错: {e}")
            return pd.DataFrame()

    def merge_trades_within_1min(self, trades_df):
        """将1分钟内的交易合并为一笔交易"""
        if trades_df.empty:
            return 0

        merged_count = 0
        last_time = None

        for _, trade in trades_df.iterrows():
            current_time = trade["open_time"]

            if last_time is None or (current_time - last_time).total_seconds() > 60:
                # 超过1分钟，算作新的一笔交易
                merged_count += 1
                last_time = current_time
            # 否则，1分钟内的交易不计新的一笔

        return merged_count
