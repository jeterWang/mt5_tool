"""
SQL查询构建器

提供安全、可读的SQL查询构建工具，防止SQL注入，支持复杂查询
"""

from typing import Dict, List, Any, Optional, Union
from datetime import datetime, date


class QueryBuilder:
    """SQL查询构建器"""

    def __init__(self):
        self.reset()

    def reset(self):
        """重置构建器状态"""
        self._select_fields = []
        self._from_table = ""
        self._joins = []
        self._where_conditions = []
        self._group_by = []
        self._having_conditions = []
        self._order_by = []
        self._limit_count = None
        self._offset_count = None
        self._params = []
        return self

    def select(self, *fields: str):
        """设置SELECT字段"""
        self._select_fields.extend(fields)
        return self

    def from_table(self, table: str):
        """设置FROM表"""
        self._from_table = table
        return self

    def join(self, table: str, condition: str, join_type: str = "INNER"):
        """添加JOIN"""
        self._joins.append(f"{join_type} JOIN {table} ON {condition}")
        return self

    def left_join(self, table: str, condition: str):
        """添加LEFT JOIN"""
        return self.join(table, condition, "LEFT")

    def right_join(self, table: str, condition: str):
        """添加RIGHT JOIN"""
        return self.join(table, condition, "RIGHT")

    def where(self, condition: str, *params):
        """添加WHERE条件"""
        self._where_conditions.append(condition)
        self._params.extend(params)
        return self

    def where_equals(self, field: str, value: Any):
        """添加等于条件"""
        return self.where(f"{field} = ?", value)

    def where_not_equals(self, field: str, value: Any):
        """添加不等于条件"""
        return self.where(f"{field} != ?", value)

    def where_in(self, field: str, values: List[Any]):
        """添加IN条件"""
        placeholders = ",".join(["?"] * len(values))
        return self.where(f"{field} IN ({placeholders})", *values)

    def where_between(self, field: str, start: Any, end: Any):
        """添加BETWEEN条件"""
        return self.where(f"{field} BETWEEN ? AND ?", start, end)

    def where_like(self, field: str, pattern: str):
        """添加LIKE条件"""
        return self.where(f"{field} LIKE ?", pattern)

    def where_is_null(self, field: str):
        """添加IS NULL条件"""
        return self.where(f"{field} IS NULL")

    def where_is_not_null(self, field: str):
        """添加IS NOT NULL条件"""
        return self.where(f"{field} IS NOT NULL")

    def where_date_equals(self, field: str, target_date: Union[str, date, datetime]):
        """添加日期等于条件"""
        if isinstance(target_date, (date, datetime)):
            target_date = target_date.strftime("%Y-%m-%d")
        return self.where_equals(field, target_date)

    def where_date_range(
        self,
        field: str,
        start_date: Union[str, date, datetime],
        end_date: Union[str, date, datetime],
    ):
        """添加日期范围条件"""
        if isinstance(start_date, (date, datetime)):
            start_date = start_date.strftime("%Y-%m-%d")
        if isinstance(end_date, (date, datetime)):
            end_date = end_date.strftime("%Y-%m-%d")
        return self.where_between(field, start_date, end_date)

    def group_by_field(self, *fields: str):
        """添加GROUP BY"""
        self._group_by.extend(fields)
        return self

    def having(self, condition: str, *params):
        """添加HAVING条件"""
        self._having_conditions.append(condition)
        self._params.extend(params)
        return self

    def order_by_field(self, field: str, direction: str = "ASC"):
        """添加ORDER BY"""
        self._order_by.append(f"{field} {direction.upper()}")
        return self

    def order_by_desc(self, field: str):
        """添加ORDER BY DESC"""
        return self.order_by_field(field, "DESC")

    def limit(self, count: int):
        """设置LIMIT"""
        self._limit_count = count
        return self

    def offset(self, count: int):
        """设置OFFSET"""
        self._offset_count = count
        return self

    def paginate(self, page: int, per_page: int):
        """分页"""
        offset = (page - 1) * per_page
        return self.limit(per_page).offset(offset)

    def build_select(self) -> tuple:
        """构建SELECT查询"""
        if not self._from_table:
            raise ValueError("必须指定FROM表")

        # SELECT子句
        if self._select_fields:
            select_clause = "SELECT " + ", ".join(self._select_fields)
        else:
            select_clause = "SELECT *"

        # FROM子句
        from_clause = f"FROM {self._from_table}"

        # 构建完整查询
        query_parts = [select_clause, from_clause]

        # JOIN子句
        if self._joins:
            query_parts.extend(self._joins)

        # WHERE子句
        if self._where_conditions:
            where_clause = "WHERE " + " AND ".join(self._where_conditions)
            query_parts.append(where_clause)

        # GROUP BY子句
        if self._group_by:
            group_clause = "GROUP BY " + ", ".join(self._group_by)
            query_parts.append(group_clause)

        # HAVING子句
        if self._having_conditions:
            having_clause = "HAVING " + " AND ".join(self._having_conditions)
            query_parts.append(having_clause)

        # ORDER BY子句
        if self._order_by:
            order_clause = "ORDER BY " + ", ".join(self._order_by)
            query_parts.append(order_clause)

        # LIMIT子句
        if self._limit_count is not None:
            query_parts.append(f"LIMIT {self._limit_count}")

        # OFFSET子句
        if self._offset_count is not None:
            query_parts.append(f"OFFSET {self._offset_count}")

        query = " ".join(query_parts)
        return query, tuple(self._params)

    def build_insert(self, table: str, data: Dict[str, Any]) -> tuple:
        """构建INSERT查询"""
        fields = list(data.keys())
        values = list(data.values())
        placeholders = ",".join(["?"] * len(fields))

        query = f"INSERT INTO {table} ({','.join(fields)}) VALUES ({placeholders})"
        return query, tuple(values)

    def build_update(self, table: str, data: Dict[str, Any]) -> tuple:
        """构建UPDATE查询"""
        set_clauses = [f"{field} = ?" for field in data.keys()]
        set_clause = "SET " + ", ".join(set_clauses)

        query_parts = [f"UPDATE {table}", set_clause]
        params = list(data.values())

        # WHERE子句
        if self._where_conditions:
            where_clause = "WHERE " + " AND ".join(self._where_conditions)
            query_parts.append(where_clause)
            params.extend(self._params)

        query = " ".join(query_parts)
        return query, tuple(params)

    def build_delete(self, table: str) -> tuple:
        """构建DELETE查询"""
        query_parts = [f"DELETE FROM {table}"]

        # WHERE子句
        if self._where_conditions:
            where_clause = "WHERE " + " AND ".join(self._where_conditions)
            query_parts.append(where_clause)

        query = " ".join(query_parts)
        return query, tuple(self._params)


class TradeQueryBuilder(QueryBuilder):
    """交易数据专用查询构建器"""

    def __init__(self):
        super().__init__()

    def risk_events_table(self):
        """使用risk_events表"""
        return self.from_table("risk_events")

    def recent_risk_events(self, days: int = 7):
        """查询最近的风控事件"""
        return self.risk_events_table().order_by_desc("timestamp").limit(100)

    def risk_events_by_type(self, event_type: str):
        """按类型查询风控事件"""
        return (
            self.risk_events_table()
            .where_equals("event_type", event_type)
            .order_by_desc("timestamp")
        )


# 便捷函数
def select(*fields):
    """创建SELECT查询构建器"""
    return QueryBuilder().select(*fields)


def trade_select(*fields):
    """创建交易数据SELECT查询构建器"""
    return TradeQueryBuilder().select(*fields)


def insert_into(table: str, data: Dict[str, Any]):
    """创建INSERT查询"""
    return QueryBuilder().build_insert(table, data)


def update_table(table: str, data: Dict[str, Any]):
    """创建UPDATE查询构建器"""
    builder = QueryBuilder()
    return builder, builder.build_update(table, data)


def delete_from(table: str):
    """创建DELETE查询构建器"""
    return QueryBuilder().from_table(table)


# 示例用法函数
def example_usage():
    """查询构建器使用示例"""

    # 基础SELECT查询
    query, params = (
        select("date", "count")
        .from_table("trade_count")
        .where_equals("date", "2024-01-15")
        .build_select()
    )
    # print(f"查询: {query}")
    # print(f"参数: {params}")

    # 复杂查询
    query, params = trade_select("date", "count").recent_trades(7).build_select()
    # print(f"最近7天交易: {query}")

    # INSERT查询
    query, params = insert_into("trade_count", {"date": "2024-01-15", "count": 5})
    # print(f"插入: {query}")
    # print(f"参数: {params}")

    # UPDATE查询
    builder = QueryBuilder()
    query, params = builder.where_equals("date", "2024-01-15").build_update(
        "trade_count", {"count": 10}
    )
    # print(f"更新: {query}")
    # print(f"参数: {params}")


if __name__ == "__main__":
    example_usage()
