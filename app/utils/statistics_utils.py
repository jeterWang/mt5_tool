from sqlalchemy import func, and_
from app.orm_models import TradeHistory
from datetime import datetime


def get_win_rate_statistics(
    session, start_date=None, end_date=None, account=None, symbol=None
):
    """
    统计指定区间、账户、品种的日/周/月盈利率（盈利天/周/月占比）。
    返回dict: {day_win_rate, week_win_rate, month_win_rate}
    """
    filters = []
    if start_date:
        filters.append(TradeHistory.close_time >= start_date)
    if end_date:
        filters.append(TradeHistory.close_time <= end_date)
    if account:
        filters.append(TradeHistory.account == account)
    if symbol:
        filters.append(TradeHistory.symbol == symbol)

    # 日盈利率
    day_query = (
        session.query(
            func.strftime("%Y-%m-%d", TradeHistory.close_time).label("day"),
            func.sum(TradeHistory.profit).label("total_profit"),
        )
        .filter(*filters)
        .group_by("day")
    )
    day_results = day_query.all()
    day_total = len(day_results)
    day_win = sum(1 for r in day_results if r.total_profit > 0)
    day_win_rate = (day_win / day_total) if day_total > 0 else 0

    # 周盈利率
    week_query = (
        session.query(
            func.strftime("%Y-%W", TradeHistory.close_time).label("week"),
            func.sum(TradeHistory.profit).label("total_profit"),
        )
        .filter(*filters)
        .group_by("week")
    )
    week_results = week_query.all()
    week_total = len(week_results)
    week_win = sum(1 for r in week_results if r.total_profit > 0)
    week_win_rate = (week_win / week_total) if week_total > 0 else 0

    # 月盈利率
    month_query = (
        session.query(
            func.strftime("%Y-%m", TradeHistory.close_time).label("month"),
            func.sum(TradeHistory.profit).label("total_profit"),
        )
        .filter(*filters)
        .group_by("month")
    )
    month_results = month_query.all()
    month_total = len(month_results)
    month_win = sum(1 for r in month_results if r.total_profit > 0)
    month_win_rate = (month_win / month_total) if month_total > 0 else 0

    return {
        "day_win_rate": day_win_rate,
        "week_win_rate": week_win_rate,
        "month_win_rate": month_win_rate,
    }
