"""
交易数据仓储类

专门处理交易相关的数据库操作
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta, date

from .base_repository import BaseRepository
from ..utils.query_builder import TradeQueryBuilder
from ..utils.logger import get_logger
from app.orm_models import TradeHistory
from sqlalchemy import func

logger = get_logger(__name__)


class TradeRepository(BaseRepository):
    """交易数据仓储（仅基于trade_history表聚合统计）"""

    @property
    def table_name(self) -> str:
        return "trade_count"

    def __init__(self, db_path: str, session_factory):
        super().__init__(db_path)
        self.trade_query_builder = TradeQueryBuilder()
        self.session_factory = session_factory

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

    def get_today_count(self, account_id=None) -> int:
        """
        获取指定交易日的交易次数

        Args:
            account_id: 账户ID，为None时使用所有账户

        Returns:
            int: 交易次数
        """
        today = self.get_trading_day()
        with self.session_factory() as session:
            q = session.query(func.count()).filter(TradeHistory.trading_day == today)
            if account_id:
                q = q.filter(TradeHistory.account == str(account_id))
            return q.scalar() or 0

    def get_history(self, days: int = 7, account_id=None) -> list:
        """
        获取历史交易记录

        Args:
            days: 获取天数
            account_id: 账户ID，为None时使用所有账户

        Returns:
            list: 历史记录列表
        """
        today = datetime.now().date()
        with self.session_factory() as session:
            q = session.query(TradeHistory.trading_day, func.count())
            if account_id:
                q = q.filter(TradeHistory.account == str(account_id))
            q = (
                q.group_by(TradeHistory.trading_day)
                .order_by(TradeHistory.trading_day.desc())
                .limit(days)
            )
            return [(r[0], r[1]) for r in q.all()]

    def get_statistics(self, days: int = 30, account_id=None) -> dict:
        """
        获取交易统计信息

        Args:
            days: 统计天数
            account_id: 账户ID，为None时使用所有账户

        Returns:
            dict: 统计信息
        """
        history = self.get_history(days, account_id)
        if not history:
            return {
                "total_trades": 0,
                "avg_daily_trades": 0.0,
                "max_daily_trades": 0,
                "min_daily_trades": 0,
                "trading_days": 0,
            }
        counts = [record[1] for record in history]
        return {
            "total_trades": sum(counts),
            "avg_daily_trades": sum(counts) / len(counts),
            "max_daily_trades": max(counts),
            "min_daily_trades": min(counts),
            "trading_days": len(history),
            "period_days": days,
        }

    def get_date_range_trades(
        self, start_date: str, end_date: str, account_id=None
    ) -> list:
        """
        获取日期范围内的交易记录

        Args:
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
            account_id: 账户ID，为None时使用所有账户

        Returns:
            list: 交易记录列表
        """
        with self.session_factory() as session:
            q = session.query(TradeHistory.trading_day, func.count())
            q = q.filter(
                TradeHistory.trading_day >= start_date,
                TradeHistory.trading_day <= end_date,
            )
            if account_id:
                q = q.filter(TradeHistory.account == str(account_id))
            q = q.group_by(TradeHistory.trading_day).order_by(TradeHistory.trading_day)
            return [(r[0], r[1]) for r in q.all()]

    def get_weekly_summary(self, week_offset: int = 0, account_id=None) -> dict:
        """
        获取周交易汇总

        Args:
            week_offset: 周偏移量，0为本周，-1为上周
            account_id: 账户ID，为None时使用所有账户

        Returns:
            dict: 周汇总信息
        """
        today = datetime.now().date()
        days_since_monday = today.weekday()
        week_start = (
            today - timedelta(days=days_since_monday) + timedelta(weeks=week_offset)
        )
        week_end = week_start + timedelta(days=6)
        trades = self.get_date_range_trades(
            week_start.strftime("%Y-%m-%d"), week_end.strftime("%Y-%m-%d"), account_id
        )
        total_trades = sum(record[1] for record in trades)
        return {
            "week_start": week_start.strftime("%Y-%m-%d"),
            "week_end": week_end.strftime("%Y-%m-%d"),
            "total_trades": total_trades,
            "trading_days": len(trades),
            "avg_daily_trades": total_trades / len(trades) if trades else 0,
            "details": trades,
        }

    def get_monthly_summary(self, month_offset: int = 0, account_id=None) -> dict:
        """
        获取月交易汇总

        Args:
            month_offset: 月偏移量，0为本月，-1为上月
            account_id: 账户ID，为None时使用所有账户

        Returns:
            dict: 月汇总信息
        """
        today = datetime.now().date()
        if month_offset == 0:
            target_month = today.replace(day=1)
        else:
            year = today.year
            month = today.month + month_offset
            while month <= 0:
                month += 12
                year -= 1
            while month > 12:
                month -= 12
                year += 1
            target_month = date(year, month, 1)
        next_month = target_month.replace(day=28) + timedelta(days=4)
        month_end = (next_month - timedelta(days=next_month.day)).replace(
            day=1
        ) + timedelta(days=32)
        month_end = month_end - timedelta(days=month_end.day)
        trades = self.get_date_range_trades(
            target_month.strftime("%Y-%m-%d"),
            month_end.strftime("%Y-%m-%d"),
            account_id,
        )
        total_trades = sum(record[1] for record in trades)
        return {
            "month": target_month.strftime("%Y-%m"),
            "month_start": target_month.strftime("%Y-%m-%d"),
            "month_end": month_end.strftime("%Y-%m-%d"),
            "total_trades": total_trades,
            "trading_days": len(trades),
            "avg_daily_trades": total_trades / len(trades) if trades else 0,
            "details": trades,
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

        query, params = (
            self.trade_query_builder.reset()
            .where("date < ?", cutoff_date)
            .build_delete("trade_count")
        )

        rowcount = self.connection_manager.execute_query(query, params)

        if rowcount > 0:
            logger.info("[空日志]", "[空日志]", f"清理旧记录: 删除了 {rowcount} 条记录")

        return rowcount
