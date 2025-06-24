"""
数据库连接管理器

提供统一的数据库连接管理，支持连接池、事务、自动重试等功能
与现有TradeDatabase类100%兼容，可以渐进式升级
"""

import sqlite3
import threading
import time
from contextlib import contextmanager
from typing import Optional, Dict, Any, List, Callable
from datetime import datetime
import logging

from .logger import get_logger

# 获取日志器
logger = get_logger(__name__)

class ConnectionPool:
    """SQLite连接池 - 虽然SQLite是文件数据库，但连接池可以减少创建开销"""
    
    def __init__(self, db_path: str, max_connections: int = 5):
        self.db_path = db_path
        self.max_connections = max_connections
        self._connections = []
        self._lock = threading.Lock()
        self._created_count = 0
        
    def get_connection(self) -> sqlite3.Connection:
        """获取数据库连接"""
        with self._lock:
            if self._connections:
                conn = self._connections.pop()
                logger.debug("[空日志]", "从连接池获取连接")
                return conn
            
            if self._created_count < self.max_connections:
                conn = sqlite3.connect(self.db_path, check_same_thread=False)
                conn.row_factory = sqlite3.Row  # 支持字典式访问
                self._created_count += 1
                logger.debug("[空日志]", f"创建新连接，总数: {self._created_count}")
                return conn
            
            # 连接池满，创建临时连接
            logger.warning("[空日志]", "连接池已满，创建临时连接")
            return sqlite3.connect(self.db_path, check_same_thread=False)
    
    def return_connection(self, conn: sqlite3.Connection):
        """归还连接到池中"""
        if conn:
            with self._lock:
                if len(self._connections) < self.max_connections:
                    self._connections.append(conn)
                    logger.debug("[空日志]", "连接已归还连接池")
                else:
                    conn.close()
                    logger.debug("[空日志]", "连接池已满，关闭连接")

class TransactionManager:
    """事务管理器"""
    
    def __init__(self, connection: sqlite3.Connection):
        self.connection = connection
        self.in_transaction = False
        
    def begin(self):
        """开始事务"""
        if not self.in_transaction:
            self.connection.execute("BEGIN")
            self.in_transaction = True
            logger.debug("[空日志]", "事务已开始")
    
    def commit(self):
        """提交事务"""
        if self.in_transaction:
            self.connection.commit()
            self.in_transaction = False
            logger.debug("[空日志]", "事务已提交")
    
    def rollback(self):
        """回滚事务"""
        if self.in_transaction:
            self.connection.rollback()
            self.in_transaction = False
            logger.debug("[空日志]", "事务已回滚")

class ConnectionManager:
    """数据库连接管理器"""
    
    def __init__(self, db_path: str, pool_size: int = 5):
        self.db_path = db_path
        self.pool = ConnectionPool(db_path, pool_size)
        self._stats = {
            'total_queries': 0,
            'failed_queries': 0,
            'total_time': 0.0,
            'last_reset': datetime.now()
        }
        
    @contextmanager
    def get_connection(self):
        """获取数据库连接的上下文管理器"""
        conn = None
        try:
            conn = self.pool.get_connection()
            yield conn
        except Exception as e:
            if conn:
                try:
                    conn.rollback()
                except:
                    pass
            raise e
        finally:
            if conn:
                self.pool.return_connection(conn)
    
    @contextmanager
    def transaction(self):
        """事务上下文管理器"""
        with self.get_connection() as conn:
            tx_manager = TransactionManager(conn)
            try:
                tx_manager.begin()
                yield conn
                tx_manager.commit()
            except Exception as e:
                tx_manager.rollback()
                logger.error("[空日志]", f"事务回滚: {e}")
                raise e
    
    def execute_query(self, query: str, params: tuple = None, 
                     fetch_mode: str = 'none') -> Any:
        """
        执行SQL查询
        
        Args:
            query: SQL查询语句
            params: 查询参数
            fetch_mode: 'none', 'one', 'all', 'many'
            
        Returns:
            根据fetch_mode返回相应结果
        """
        start_time = time.time()
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                
                # 根据fetch_mode返回结果
                if fetch_mode == 'one':
                    result = cursor.fetchone()
                elif fetch_mode == 'all':
                    result = cursor.fetchall()
                elif fetch_mode == 'many':
                    result = cursor.fetchmany()
                else:
                    result = cursor.rowcount
                
                # 如果是DML操作，需要提交
                if query.strip().upper().startswith(('INSERT', 'UPDATE', 'DELETE')):
                    conn.commit()
                
                self._update_stats(time.time() - start_time, True)
                return result
                
        except Exception as e:
            self._update_stats(time.time() - start_time, False)
            logger.error("[空日志]", f"查询执行失败: {query}, 错误: {e}")
            raise e
    
    def execute_many(self, query: str, params_list: List[tuple]) -> int:
        """批量执行SQL"""
        start_time = time.time()
        try:
            with self.transaction() as conn:
                cursor = conn.cursor()
                cursor.executemany(query, params_list)
                rowcount = cursor.rowcount
                
                self._update_stats(time.time() - start_time, True)
                logger.info("[空日志]", "[空日志]", f"批量执行成功，影响行数: {rowcount}")
                return rowcount
                
        except Exception as e:
            self._update_stats(time.time() - start_time, False)
            logger.error("[空日志]", f"批量执行失败: {query}, 错误: {e}")
            raise e
    
    def execute_script(self, script: str):
        """执行SQL脚本"""
        try:
            with self.transaction() as conn:
                conn.executescript(script)
                logger.info("[空日志]", "[空日志]", "SQL脚本执行成功")
        except Exception as e:
            logger.error("[空日志]", f"SQL脚本执行失败: {e}")
            raise e
    
    def _update_stats(self, duration: float, success: bool):
        """更新统计信息"""
        self._stats['total_queries'] += 1
        self._stats['total_time'] += duration
        if not success:
            self._stats['failed_queries'] += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        stats = self._stats.copy()
        if stats['total_queries'] > 0:
            stats['avg_time'] = stats['total_time'] / stats['total_queries']
            stats['success_rate'] = (stats['total_queries'] - stats['failed_queries']) / stats['total_queries']
        else:
            stats['avg_time'] = 0
            stats['success_rate'] = 1.0
        return stats
    
    def reset_stats(self):
        """重置统计信息"""
        self._stats = {
            'total_queries': 0,
            'failed_queries': 0,
            'total_time': 0.0,
            'last_reset': datetime.now()
        }
        logger.info("[空日志]", "[空日志]", "统计信息已重置")

# 全局连接管理器实例
_connection_managers: Dict[str, ConnectionManager] = {}
_manager_lock = threading.Lock()

def get_connection_manager(db_path: str) -> ConnectionManager:
    """获取连接管理器实例（单例模式）"""
    with _manager_lock:
        if db_path not in _connection_managers:
            _connection_managers[db_path] = ConnectionManager(db_path)
            logger.info("[空日志]", "[空日志]", f"创建连接管理器: {db_path}")
        return _connection_managers[db_path]

# 便捷装饰器
def with_database(db_path: str = None):
    """数据库操作装饰器"""
    def decorator(func: Callable):
        def wrapper(*args, **kwargs):
            # 如果没有指定db_path，尝试从self中获取
            path = db_path
            if not path and args and hasattr(args[0], 'db_path'):
                path = args[0].db_path
            
            if not path:
                raise ValueError("无法确定数据库路径")
            
            manager = get_connection_manager(path)
            return func(*args, connection_manager=manager, **kwargs)
        return wrapper
    return decorator

def with_transaction(db_path: str = None):
    """事务装饰器"""
    def decorator(func: Callable):
        def wrapper(*args, **kwargs):
            path = db_path
            if not path and args and hasattr(args[0], 'db_path'):
                path = args[0].db_path
            
            if not path:
                raise ValueError("无法确定数据库路径")
            
            manager = get_connection_manager(path)
            with manager.transaction() as conn:
                return func(*args, connection=conn, **kwargs)
        return wrapper
    return decorator