"""
基础仓储类

实现仓储模式的基础功能，提供通用的CRUD操作
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Type, Union
from datetime import datetime

from ..utils.connection_manager import ConnectionManager, get_connection_manager
from ..utils.query_builder import QueryBuilder
from ..utils.logger import get_logger

logger = get_logger(__name__)

class BaseRepository(ABC):
    """基础仓储类"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.connection_manager = get_connection_manager(db_path)
        self.query_builder = QueryBuilder()
    
    @property
    @abstractmethod
    def table_name(self) -> str:
        """子类必须定义表名"""
        pass
    
    def find_by_id(self, id_value: Any) -> Optional[Dict[str, Any]]:
        """根据ID查找记录"""
        query, params = (self.query_builder.reset()
                        .from_table(self.table_name)
                        .where_equals("id", id_value)
                        .build_select())
        
        result = self.connection_manager.execute_query(query, params, 'one')
        return dict(result) if result else None
    
    def find_all(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """查找所有记录"""
        builder = (self.query_builder.reset()
                  .from_table(self.table_name))
        
        if limit:
            builder.limit(limit)
        
        query, params = builder.build_select()
        results = self.connection_manager.execute_query(query, params, 'all')
        return [dict(row) for row in results] if results else []
    
    def find_where(self, conditions: Dict[str, Any], 
                  limit: Optional[int] = None,
                  order_by: Optional[str] = None,
                  order_direction: str = "ASC") -> List[Dict[str, Any]]:
        """根据条件查找记录"""
        builder = self.query_builder.reset().from_table(self.table_name)
        
        # 添加WHERE条件
        for field, value in conditions.items():
            builder.where_equals(field, value)
        
        # 添加排序
        if order_by:
            builder.order_by_field(order_by, order_direction)
        
        # 添加限制
        if limit:
            builder.limit(limit)
        
        query, params = builder.build_select()
        results = self.connection_manager.execute_query(query, params, 'all')
        return [dict(row) for row in results] if results else []
    
    def create(self, data: Dict[str, Any]) -> int:
        """创建新记录"""
        # 添加时间戳
        if 'created_at' not in data:
            data['created_at'] = datetime.now().isoformat()
        
        query, params = self.query_builder.build_insert(self.table_name, data)
        
        with self.connection_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            record_id = cursor.lastrowid
            
        logger.info("[空日志]", "[空日志]", f"创建记录成功: {self.table_name}, ID: {record_id}")
        return record_id
    
    def update(self, id_value: Any, data: Dict[str, Any]) -> bool:
        """更新记录"""
        # 添加更新时间戳
        data['updated_at'] = datetime.now().isoformat()
        
        builder = self.query_builder.reset()
        builder.where_equals("id", id_value)
        query, params = builder.build_update(self.table_name, data)
        
        rowcount = self.connection_manager.execute_query(query, params)
        success = rowcount > 0
        
        if success:
            logger.info("[空日志]", "[空日志]", f"更新记录成功: {self.table_name}, ID: {id_value}")
        else:
            logger.warning("[空日志]", f"更新记录失败: {self.table_name}, ID: {id_value}")
        
        return success
    
    def delete(self, id_value: Any) -> bool:
        """删除记录"""
        builder = self.query_builder.reset()
        builder.where_equals("id", id_value)
        query, params = builder.build_delete(self.table_name)
        
        rowcount = self.connection_manager.execute_query(query, params)
        success = rowcount > 0
        
        if success:
            logger.info("[空日志]", "[空日志]", f"删除记录成功: {self.table_name}, ID: {id_value}")
        else:
            logger.warning("[空日志]", f"删除记录失败: {self.table_name}, ID: {id_value}")
        
        return success
    
    def delete_where(self, conditions: Dict[str, Any]) -> int:
        """根据条件删除记录"""
        builder = self.query_builder.reset()
        
        for field, value in conditions.items():
            builder.where_equals(field, value)
        
        query, params = builder.build_delete(self.table_name)
        rowcount = self.connection_manager.execute_query(query, params)
        
        logger.info("[空日志]", "[空日志]", f"批量删除记录: {self.table_name}, 影响行数: {rowcount}")
        return rowcount
    
    def count(self, conditions: Optional[Dict[str, Any]] = None) -> int:
        """统计记录数"""
        builder = (self.query_builder.reset()
                  .select("COUNT(*) as count")
                  .from_table(self.table_name))
        
        if conditions:
            for field, value in conditions.items():
                builder.where_equals(field, value)
        
        query, params = builder.build_select()
        result = self.connection_manager.execute_query(query, params, 'one')
        return result['count'] if result else 0
    
    def exists(self, conditions: Dict[str, Any]) -> bool:
        """检查记录是否存在"""
        return self.count(conditions) > 0
    
    def paginate(self, page: int, per_page: int = 10, 
                conditions: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """分页查询"""
        # 计算总数
        total = self.count(conditions)
        
        # 查询数据
        builder = self.query_builder.reset().from_table(self.table_name)
        
        if conditions:
            for field, value in conditions.items():
                builder.where_equals(field, value)
        
        builder.paginate(page, per_page)
        query, params = builder.build_select()
        
        results = self.connection_manager.execute_query(query, params, 'all')
        data = [dict(row) for row in results] if results else []
        
        return {
            'data': data,
            'page': page,
            'per_page': per_page,
            'total': total,
            'pages': (total + per_page - 1) // per_page
        }
    
    def bulk_create(self, data_list: List[Dict[str, Any]]) -> List[int]:
        """批量创建记录"""
        if not data_list:
            return []
        
        # 确保所有记录有相同的字段
        fields = list(data_list[0].keys())
        
        # 添加时间戳
        timestamp = datetime.now().isoformat()
        for data in data_list:
            if 'created_at' not in data:
                data['created_at'] = timestamp
        
        # 构建批量插入SQL
        placeholders = ",".join(["?"] * len(fields))
        query = f"INSERT INTO {self.table_name} ({','.join(fields)}) VALUES ({placeholders})"
        
        # 准备参数
        params_list = []
        for data in data_list:
            params_list.append(tuple(data[field] for field in fields))
        
        # 执行批量插入
        with self.connection_manager.transaction() as conn:
            cursor = conn.cursor()
            cursor.executemany(query, params_list)
            
            # 获取插入的ID范围（SQLite的简化实现）
            last_id = cursor.lastrowid
            first_id = last_id - len(data_list) + 1
            record_ids = list(range(first_id, last_id + 1))
        
        logger.info("[空日志]", "[空日志]", f"批量创建记录成功: {self.table_name}, 数量: {len(data_list)}")
        return record_ids
    
    def execute_raw_query(self, query: str, params: tuple = None, 
                         fetch_mode: str = 'all') -> Any:
        """执行原始SQL查询"""
        logger.debug("[空日志]", f"执行原始查询: {query}")
        return self.connection_manager.execute_query(query, params, fetch_mode)
    
    def get_stats(self) -> Dict[str, Any]:
        """获取连接管理器统计信息"""
        return self.connection_manager.get_stats()