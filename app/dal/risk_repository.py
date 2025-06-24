"""
风控事件仓储类

专门处理风控相关的数据库操作
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json

from .base_repository import BaseRepository
from ..utils.query_builder import TradeQueryBuilder
from ..utils.logger import get_logger

logger = get_logger(__name__)

class RiskRepository(BaseRepository):
    """风控事件仓储"""
    
    @property
    def table_name(self) -> str:
        return "risk_events"
    
    def __init__(self, db_path: str):
        super().__init__(db_path)
        self.trade_query_builder = TradeQueryBuilder()
    
    def record_risk_event(self, event_type: str, details: str, 
                         metadata: Optional[Dict[str, Any]] = None) -> int:
        """
        记录风控事件
        
        Args:
            event_type: 事件类型
            details: 事件详情
            metadata: 附加元数据
            
        Returns:
            int: 记录ID
        """
        data = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "event_type": event_type,
            "details": details
        }
        
        # 如果有元数据，将其序列化为JSON
        if metadata:
            data["metadata"] = json.dumps(metadata, ensure_ascii=False)
        
        record_id = self.create(data)
        logger.info("[空日志]", "[空日志]", f"记录风控事件: {event_type} - {details}")
        return record_id
    
    def get_recent_events(self, days: int = 7, 
                         event_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        获取最近的风控事件
        
        Args:
            days: 获取天数
            event_type: 事件类型过滤
            
        Returns:
            List[Dict]: 风控事件列表
        """
        # 计算时间范围
        start_time = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d %H:%M:%S")
        
        builder = (self.trade_query_builder.reset()
                  .risk_events_table()
                  .where("timestamp >= ?", start_time)
                  .order_by_desc("timestamp")
                  .limit(100))
        
        if event_type:
            builder.where_equals("event_type", event_type)
        
        query, params = builder.build_select()
        results = self.connection_manager.execute_query(query, params, 'all')
        
        # 处理结果，解析metadata
        events = []
        for row in results:
            event = dict(row)
            
            # 尝试解析metadata JSON
            if event.get("metadata"):
                try:
                    event["metadata"] = json.loads(event["metadata"])
                except (json.JSONDecodeError, TypeError):
                    event["metadata"] = None
            
            events.append(event)
        
        return events
    
    def get_events_by_type(self, event_type: str, 
                          limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        按类型获取风控事件
        
        Args:
            event_type: 事件类型
            limit: 记录限制
            
        Returns:
            List[Dict]: 风控事件列表
        """
        builder = (self.trade_query_builder.reset()
                  .risk_events_by_type(event_type))
        
        if limit:
            builder.limit(limit)
        
        query, params = builder.build_select()
        results = self.connection_manager.execute_query(query, params, 'all')
        
        # 处理结果
        events = []
        for row in results:
            event = dict(row)
            if event.get("metadata"):
                try:
                    event["metadata"] = json.loads(event["metadata"])
                except (json.JSONDecodeError, TypeError):
                    event["metadata"] = None
            events.append(event)
        
        return events
    
    def get_event_statistics(self, days: int = 30) -> Dict[str, Any]:
        """
        获取风控事件统计
        
        Args:
            days: 统计天数
            
        Returns:
            Dict: 统计信息
        """
        events = self.get_recent_events(days)
        
        if not events:
            return {
                "total_events": 0,
                "event_types": {},
                "daily_average": 0.0,
                "period_days": days
            }
        
        # 按类型统计
        type_counts = {}
        for event in events:
            event_type = event["event_type"]
            type_counts[event_type] = type_counts.get(event_type, 0) + 1
        
        return {
            "total_events": len(events),
            "event_types": type_counts,
            "daily_average": len(events) / days,
            "period_days": days,
            "most_common_type": max(type_counts.items(), key=lambda x: x[1])[0] if type_counts else None
        }
    
    def get_events_timeline(self, days: int = 7) -> Dict[str, List[Dict[str, Any]]]:
        """
        获取事件时间线
        
        Args:
            days: 天数
            
        Returns:
            Dict: 按日期分组的事件
        """
        events = self.get_recent_events(days)
        timeline = {}
        
        for event in events:
            # 提取日期部分
            timestamp = event["timestamp"]
            if isinstance(timestamp, str):
                date_part = timestamp.split()[0]  # YYYY-MM-DD部分
            else:
                date_part = timestamp.strftime("%Y-%m-%d")
            
            if date_part not in timeline:
                timeline[date_part] = []
            
            timeline[date_part].append(event)
        
        return timeline
    
    def search_events(self, keyword: str, days: int = 30) -> List[Dict[str, Any]]:
        """
        搜索包含关键词的风控事件
        
        Args:
            keyword: 搜索关键词
            days: 搜索天数范围
            
        Returns:
            List[Dict]: 匹配的风控事件
        """
        start_time = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d %H:%M:%S")
        
        query, params = (self.trade_query_builder.reset()
                        .risk_events_table()
                        .where("timestamp >= ?", start_time)
                        .where("(details LIKE ? OR event_type LIKE ?)", f"%{keyword}%", f"%{keyword}%")
                        .order_by_desc("timestamp")
                        .build_select())
        
        results = self.connection_manager.execute_query(query, params, 'all')
        
        # 处理结果
        events = []
        for row in results:
            event = dict(row)
            if event.get("metadata"):
                try:
                    event["metadata"] = json.loads(event["metadata"])
                except (json.JSONDecodeError, TypeError):
                    event["metadata"] = None
            events.append(event)
        
        return events
    
    def get_severity_levels(self) -> Dict[str, int]:
        """
        获取事件严重级别统计
        
        Returns:
            Dict: 严重级别统计
        """
        # 定义严重级别映射
        severity_mapping = {
            "CRITICAL": ["账户异常", "连接失败", "系统错误", "致命错误"],
            "HIGH": ["风控触发", "交易失败", "网络错误"],
            "MEDIUM": ["警告", "超时", "重试"],
            "LOW": ["信息", "调试", "统计"]
        }
        
        events = self.get_recent_events(30)
        severity_counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
        
        for event in events:
            event_type = event["event_type"]
            details = event["details"]
            
            # 根据事件类型和详情判断严重级别
            severity = "LOW"  # 默认低级别
            
            for level, keywords in severity_mapping.items():
                if any(keyword in event_type or keyword in details for keyword in keywords):
                    severity = level
                    break
            
            severity_counts[severity] += 1
        
        return severity_counts
    
    def cleanup_old_events(self, keep_days: int = 90) -> int:
        """
        清理旧的风控事件
        
        Args:
            keep_days: 保留天数
            
        Returns:
            int: 删除的记录数
        """
        cutoff_time = (datetime.now() - timedelta(days=keep_days)).strftime("%Y-%m-%d %H:%M:%S")
        
        query, params = (self.trade_query_builder.reset()
                        .where("timestamp < ?", cutoff_time)
                        .build_delete("risk_events"))
        
        rowcount = self.connection_manager.execute_query(query, params)
        
        if rowcount > 0:
            logger.info("[空日志]", "[空日志]", f"清理旧风控事件: 删除了 {rowcount} 条记录")
        
        return rowcount
    
    def export_events_to_dict(self, days: int = 30) -> Dict[str, Any]:
        """
        导出风控事件为字典格式
        
        Args:
            days: 导出天数
            
        Returns:
            Dict: 导出数据
        """
        events = self.get_recent_events(days)
        statistics = self.get_event_statistics(days)
        severity = self.get_severity_levels()
        
        return {
            "export_time": datetime.now().isoformat(),
            "period_days": days,
            "statistics": statistics,
            "severity_levels": severity,
            "events": events
        }