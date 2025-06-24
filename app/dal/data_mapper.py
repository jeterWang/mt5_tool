"""
数据映射器

处理数据库记录与业务对象之间的转换
"""

from typing import Any, Dict, List, Optional, Type, Union
from datetime import datetime, date
from dataclasses import dataclass, asdict
import json

from ..utils.logger import get_logger

logger = get_logger(__name__)

@dataclass
class TradeRecord:
    """交易记录数据类"""
    id: Optional[int] = None
    date: str = ""
    count: int = 0
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    def __post_init__(self):
        """初始化后处理"""
        if not self.date:
            self.date = datetime.now().strftime("%Y-%m-%d")
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TradeRecord':
        """从字典创建对象"""
        return cls(**{k: v for k, v in data.items() if k in cls.__annotations__})
    
    def to_dict(self, exclude_none: bool = True) -> Dict[str, Any]:
        """转换为字典"""
        data = asdict(self)
        if exclude_none:
            data = {k: v for k, v in data.items() if v is not None}
        return data

@dataclass
class RiskEvent:
    """风控事件数据类"""
    id: Optional[int] = None
    timestamp: str = ""
    event_type: str = ""
    details: str = ""
    metadata: Optional[Dict[str, Any]] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    def __post_init__(self):
        """初始化后处理"""
        if not self.timestamp:
            self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RiskEvent':
        """从字典创建对象"""
        # 处理metadata字段
        if 'metadata' in data and isinstance(data['metadata'], str):
            try:
                data['metadata'] = json.loads(data['metadata'])
            except (json.JSONDecodeError, TypeError):
                data['metadata'] = None
        
        return cls(**{k: v for k, v in data.items() if k in cls.__annotations__})
    
    def to_dict(self, exclude_none: bool = True) -> Dict[str, Any]:
        """转换为字典"""
        data = asdict(self)
        
        # 序列化metadata
        if data.get('metadata'):
            data['metadata'] = json.dumps(data['metadata'], ensure_ascii=False)
        
        if exclude_none:
            data = {k: v for k, v in data.items() if v is not None}
        
        return data

class DataMapper:
    """数据映射器类"""
    
    @staticmethod
    def map_trade_records(raw_data: List[Dict[str, Any]]) -> List[TradeRecord]:
        """映射交易记录"""
        return [TradeRecord.from_dict(record) for record in raw_data]
    
    @staticmethod
    def map_risk_events(raw_data: List[Dict[str, Any]]) -> List[RiskEvent]:
        """映射风控事件"""
        return [RiskEvent.from_dict(event) for event in raw_data]
    
    @staticmethod
    def trade_record_to_dict(record: TradeRecord) -> Dict[str, Any]:
        """交易记录转字典"""
        return record.to_dict()
    
    @staticmethod
    def risk_event_to_dict(event: RiskEvent) -> Dict[str, Any]:
        """风控事件转字典"""
        return event.to_dict()
    
    @staticmethod
    def format_trade_summary(records: List[TradeRecord]) -> Dict[str, Any]:
        """格式化交易汇总"""
        if not records:
            return {
                "total_records": 0,
                "total_trades": 0,
                "date_range": None,
                "average_daily": 0.0
            }
        
        total_trades = sum(record.count for record in records)
        dates = [record.date for record in records if record.date]
        
        return {
            "total_records": len(records),
            "total_trades": total_trades,
            "date_range": {
                "start": min(dates) if dates else None,
                "end": max(dates) if dates else None
            },
            "average_daily": total_trades / len(records) if records else 0.0,
            "records": [record.to_dict() for record in records]
        }
    
    @staticmethod
    def format_risk_summary(events: List[RiskEvent]) -> Dict[str, Any]:
        """格式化风控事件汇总"""
        if not events:
            return {
                "total_events": 0,
                "event_types": {},
                "time_range": None,
                "severity_levels": {}
            }
        
        # 按类型统计
        type_counts = {}
        for event in events:
            event_type = event.event_type
            type_counts[event_type] = type_counts.get(event_type, 0) + 1
        
        # 按严重程度统计
        severity_levels = {"high": 0, "medium": 0, "low": 0}
        for event in events:
            # 简单的严重程度判断逻辑
            details_lower = event.details.lower()
            if any(keyword in details_lower for keyword in ["错误", "失败", "异常", "critical"]):
                severity_levels["high"] += 1
            elif any(keyword in details_lower for keyword in ["警告", "warning", "超时"]):
                severity_levels["medium"] += 1
            else:
                severity_levels["low"] += 1
        
        # 时间范围
        timestamps = [event.timestamp for event in events if event.timestamp]
        
        return {
            "total_events": len(events),
            "event_types": type_counts,
            "time_range": {
                "start": min(timestamps) if timestamps else None,
                "end": max(timestamps) if timestamps else None
            },
            "severity_levels": severity_levels,
            "events": [event.to_dict() for event in events]
        }
    
    @staticmethod
    def format_daily_report(trade_data: Dict[str, Any], 
                           risk_data: Dict[str, Any]) -> Dict[str, Any]:
        """格式化日报告"""
        return {
            "report_type": "daily",
            "generated_at": datetime.now().isoformat(),
            "trade_summary": trade_data,
            "risk_summary": risk_data,
            "overall_status": DataMapper._calculate_overall_status(trade_data, risk_data)
        }
    
    @staticmethod
    def _calculate_overall_status(trade_data: Dict[str, Any], 
                                 risk_data: Dict[str, Any]) -> str:
        """计算整体状态"""
        # 简单的状态判断逻辑
        high_risk_count = risk_data.get("severity_levels", {}).get("high", 0)
        total_trades = trade_data.get("total_trades", 0)
        
        if high_risk_count > 5:
            return "critical"
        elif high_risk_count > 2 or total_trades == 0:
            return "warning"
        elif total_trades > 0:
            return "normal"
        else:
            return "idle"
    
    @staticmethod
    def export_to_excel_format(trade_records: List[TradeRecord], 
                              risk_events: List[RiskEvent]) -> Dict[str, Any]:
        """导出为Excel格式的数据"""
        return {
            "trade_data": {
                "headers": ["日期", "交易次数", "创建时间", "更新时间"],
                "rows": [
                    [record.date, record.count, record.created_at, record.updated_at]
                    for record in trade_records
                ]
            },
            "risk_data": {
                "headers": ["时间戳", "事件类型", "详情", "元数据"],
                "rows": [
                    [
                        event.timestamp, 
                        event.event_type, 
                        event.details,
                        json.dumps(event.metadata, ensure_ascii=False) if event.metadata else ""
                    ]
                    for event in risk_events
                ]
            },
            "export_info": {
                "exported_at": datetime.now().isoformat(),
                "trade_count": len(trade_records),
                "risk_event_count": len(risk_events)
            }
        }
    
    @staticmethod
    def validate_trade_record(data: Dict[str, Any]) -> Dict[str, Any]:
        """验证交易记录数据"""
        errors = []
        
        # 检查必需字段
        if not data.get("date"):
            errors.append("日期字段不能为空")
        
        if "count" not in data:
            errors.append("交易次数字段不能为空")
        elif not isinstance(data["count"], int) or data["count"] < 0:
            errors.append("交易次数必须是非负整数")
        
        # 检查日期格式
        if data.get("date"):
            try:
                datetime.strptime(data["date"], "%Y-%m-%d")
            except ValueError:
                errors.append("日期格式必须是YYYY-MM-DD")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
    
    @staticmethod
    def validate_risk_event(data: Dict[str, Any]) -> Dict[str, Any]:
        """验证风控事件数据"""
        errors = []
        
        # 检查必需字段
        if not data.get("event_type"):
            errors.append("事件类型不能为空")
        
        if not data.get("details"):
            errors.append("事件详情不能为空")
        
        # 检查时间戳格式
        if data.get("timestamp"):
            try:
                datetime.strptime(data["timestamp"], "%Y-%m-%d %H:%M:%S")
            except ValueError:
                errors.append("时间戳格式必须是YYYY-MM-DD HH:MM:SS")
        
        # 检查元数据
        if data.get("metadata") and isinstance(data["metadata"], str):
            try:
                json.loads(data["metadata"])
            except json.JSONDecodeError:
                errors.append("元数据必须是有效的JSON格式")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }

# 便捷函数
def create_trade_record(date: str, count: int) -> TradeRecord:
    """创建交易记录"""
    return TradeRecord(date=date, count=count)

def create_risk_event(event_type: str, details: str, 
                     metadata: Optional[Dict[str, Any]] = None) -> RiskEvent:
    """创建风控事件"""
    return RiskEvent(event_type=event_type, details=details, metadata=metadata)