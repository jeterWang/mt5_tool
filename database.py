import sqlite3
from datetime import datetime
import os

class TradeDatabase:
    def __init__(self):
        self.db_path = 'trade_history.db'
        self.init_database()
    
    def init_database(self):
        """初始化数据库"""
        try:
            # 如果数据库文件不存在，创建数据库和表
            is_new_db = not os.path.exists(self.db_path)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 创建交易记录表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS trade_counts (
                    date TEXT PRIMARY KEY,
                    count INTEGER DEFAULT 0
                )
            ''')
            
            conn.commit()
            conn.close()
            
            # 如果是新数据库，初始化今天的记录
            if is_new_db:
                self.get_today_count()
                
        except Exception as e:
            print(f"初始化数据库出错：{str(e)}")
    
    def get_today_count(self) -> int:
        """获取今天的交易次数"""
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 查询今天的记录
            cursor.execute('SELECT count FROM trade_counts WHERE date = ?', (today,))
            result = cursor.fetchone()
            
            if result is None:
                # 如果没有今天的记录，创建一条新记录
                cursor.execute('INSERT INTO trade_counts (date, count) VALUES (?, 0)', (today,))
                conn.commit()
                count = 0
            else:
                count = result[0]
            
            conn.close()
            return count
            
        except Exception as e:
            print(f"获取今日交易次数出错：{str(e)}")
            return 0
    
    def increment_count(self) -> bool:
        """增加今天的交易次数"""
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 更新今天的交易次数
            cursor.execute('''
                INSERT INTO trade_counts (date, count) 
                VALUES (?, 1)
                ON CONFLICT(date) DO UPDATE SET count = count + 1
            ''', (today,))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"增加交易次数出错：{str(e)}")
            return False
    
    def get_history(self, days: int = 7) -> list:
        """获取最近几天的交易历史"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT date, count FROM trade_counts 
                ORDER BY date DESC LIMIT ?
            ''', (days,))
            
            history = cursor.fetchall()
            conn.close()
            
            return history
            
        except Exception as e:
            print(f"获取交易历史出错：{str(e)}")
            return [] 