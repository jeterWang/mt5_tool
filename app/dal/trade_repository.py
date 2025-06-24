"""
交易数据仓储类

专门处理交易相关的数据库操作
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta, date

from .base_repository import BaseRepository
from ..utils.query_builder import TradeQueryBuilder
from ..utils.logger import get_logger

logger = get_logger(__name__)

class TradeRepository(BaseRepository):
    """交易数据仓储"""
    
    @property
    def table_name(self) -> str:
        return "trade_count"
    
    def __init__(self, db_path: str):
        super().__init__(db_path)
        self.trade_query_builder = TradeQueryBuilder()
    
    def get_trading_day(self, reset_hour: int = 6) -> str:
        """
        获取当前交易日
        
        Args:
            reset_hour: 交易日重置小时（默认6点）
            
        Returns:
            str: 交易日期字符串 (YYYY-MM-DD)
        """
        now = datetime.now()
        if now.hour >= reset_hour:
            return now.strftime("%Y-%m-%d")
        else:
            yesterday = now - timedelta(days=1)
            return yesterday.strftime("%Y-%m-%d")
    
    def get_today_count(self, trading_day: Optional[str] = None) -> int:
        """
        获取指定交易日的交易次数
        
        Args:
            trading_day: 交易日期，为None时使用当前交易日
            
        Returns:
            int: 交易次数
        """
        if not trading_day:
            trading_day = self.get_trading_day()
        
        result = self.find_where({"date": trading_day})
        return result[0]["count"] if result else 0
    
    def set_today_count(self, count: int, trading_day: Optional[str] = None) -> bool:
        """
        设置指定交易日的交易次数
        
        Args:
            count: 交易次数
            trading_day: 交易日期，为None时使用当前交易日
            
        Returns:
            bool: 操作是否成功
        """
        if not trading_day:
            trading_day = self.get_trading_day()
        
        try:
            # 检查记录是否存在
            existing = self.find_where({"date": trading_day})
            
            if existing:
                # 更新现有记录
                return self.update(existing[0]["id"], {"count": count})
            else:
                # 创建新记录
                self.create({"date": trading_day, "count": count})
                return True
                
        except Exception as e:
            logger.error("[空日志]", f"设置交易次数失败: {e}")
            return False
    
    def increment_count(self, trading_day: Optional[str] = None) -> bool:
        """
        增加交易次数
        
        Args:
            trading_day: 交易日期，为None时使用当前交易日
            
        Returns:
            bool: 操作是否成功
        """
        if not trading_day:
            trading_day = self.get_trading_day()
        
        try:
            current_count = self.get_today_count(trading_day)
            return self.set_today_count(current_count + 1, trading_day)
        except Exception as e:
            logger.error("[空日志]", f"增加交易次数失败: {e}")
            return False
    
    def get_history(self, days: int = 7, 
                   end_date: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        获取历史交易记录
        
        Args:
            days: 获取天数
            end_date: 结束日期，为None时使用当前交易日
            
        Returns:
            List[Dict]: 历史记录列表
        """
        if not end_date:
            end_date = self.get_trading_day()
        
        query, params = (self.trade_query_builder.reset()
                        .trade_count_table()
                        .select("date", "count")
                        .order_by_desc("date")
                        .limit(days)
                        .build_select())
        
        results = self.connection_manager.execute_query(query, params, 'all')
        return [dict(row) for row in results] if results else []
    
    def get_statistics(self, days: int = 30) -> Dict[str, Any]:
        """
        获取交易统计信息
        
        Args:
            days: 统计天数
            
        Returns:
            Dict: 统计信息
        """
        # 获取历史数据
        history = self.get_history(days)
        
        if not history:
            return {
                "total_trades": 0,
                "avg_daily_trades": 0.0,
                "max_daily_trades": 0,
                "min_daily_trades": 0,
                "trading_days": 0
            }
        
        counts = [record["count"] for record in history]
        
        return {
            "total_trades": sum(counts),
            "avg_daily_trades": sum(counts) / len(counts),
            "max_daily_trades": max(counts),
            "min_daily_trades": min(counts),
            "trading_days": len(history),
            "period_days": days
        }
    
    def get_date_range_trades(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """
        获取日期范围内的交易记录
        
        Args:
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
            
        Returns:
            List[Dict]: 交易记录列表
        """
        query, params = (self.trade_query_builder.reset()
                        .trade_count_table()
                        .select("date", "count")
                        .where_date_range("date", start_date, end_date)
                        .order_by_field("date")
                        .build_select())
        
        results = self.connection_manager.execute_query(query, params, 'all')
        return [dict(row) for row in results] if results else []
    
    def get_weekly_summary(self, week_offset: int = 0) -> Dict[str, Any]:
        """
        获取周交易汇总
        
        Args:
            week_offset: 周偏移量，0为本周，-1为上周
            
        Returns:
            Dict: 周汇总信息
        """
        today = datetime.now().date()
        
        # 计算周的开始和结束日期
        days_since_monday = today.weekday()
        week_start = today - timedelta(days=days_since_monday) + timedelta(weeks=week_offset)
        week_end = week_start + timedelta(days=6)
        
        trades = self.get_date_range_trades(
            week_start.strftime("%Y-%m-%d"),
            week_end.strftime("%Y-%m-%d")
        )
        
        total_trades = sum(record["count"] for record in trades)
        
        return {
            "week_start": week_start.strftime("%Y-%m-%d"),
            "week_end": week_end.strftime("%Y-%m-%d"),
            "total_trades": total_trades,
            "trading_days": len(trades),
            "avg_daily_trades": total_trades / len(trades) if trades else 0,
            "details": trades
        }
    
    def get_monthly_summary(self, month_offset: int = 0) -> Dict[str, Any]:
        """
        获取月交易汇总
        
        Args:
            month_offset: 月偏移量，0为本月，-1为上月
            
        Returns:
            Dict: 月汇总信息
        """
        today = datetime.now().date()
        
        # 计算月份
        if month_offset == 0:
            target_month = today.replace(day=1)
        else:
            year = today.year
            month = today.month + month_offset
            
            # 处理年份跨越
            while month <= 0:
                month += 12
                year -= 1
            while month > 12:
                month -= 12
                year += 1
            
            target_month = date(year, month, 1)
        
        # 计算月的结束日期
        next_month = target_month.replace(day=28) + timedelta(days=4)
        month_end = (next_month - timedelta(days=next_month.day)).replace(day=1) + timedelta(days=32)
        month_end = month_end - timedelta(days=month_end.day)
        
        trades = self.get_date_range_trades(
            target_month.strftime("%Y-%m-%d"),
            month_end.strftime("%Y-%m-%d")
        )
        
        total_trades = sum(record["count"] for record in trades)
        
        return {
            "month": target_month.strftime("%Y-%m"),
            "month_start": target_month.strftime("%Y-%m-%d"),
            "month_end": month_end.strftime("%Y-%m-%d"),
            "total_trades": total_trades,
            "trading_days": len(trades),
            "avg_daily_trades": total_trades / len(trades) if trades else 0,
            "details": trades
        }
    
    def cleanup_old_records(self, keep_days: int = 90) -> int:
        """
        清理旧记录
        
        Args:
            keep_days: 保留天数
            
        Returns:
            int: 删除的记录数
        """
        cutoff_date = (datetime.now() - timedelta(days=keep_days)).strftime("%Y-%m-%d")
        
        query, params = (self.trade_query_builder.reset()
                        .where("date < ?", cutoff_date)
                        .build_delete("trade_count"))
        
        rowcount = self.connection_manager.execute_query(query, params)
        
        if rowcount > 0:
            logger.info("[空日志]", "[空日志]", f"清理旧记录: 删除了 {rowcount} 条记录")
        
        return rowcount