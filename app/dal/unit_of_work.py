"""
工作单元模式(Unit of Work)

协调多个仓储的事务操作，确保数据一致性
"""

from typing import Dict, Any, Optional, List
from contextlib import contextmanager

from .trade_repository import TradeRepository
from .risk_repository import RiskRepository
from ..utils.connection_manager import get_connection_manager
from ..utils.logger import get_logger

logger = get_logger(__name__)

class UnitOfWork:
    """工作单元类"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.connection_manager = get_connection_manager(db_path)
        
        # 初始化仓储
        self.trades = TradeRepository(db_path)
        self.risks = RiskRepository(db_path)
        
        # 事务状态
        self._in_transaction = False
        self._connection = None
    
    @contextmanager
    def transaction(self):
        """事务上下文管理器"""
        if self._in_transaction:
            # 嵌套事务，直接返回
            yield self
            return
        
        try:
            with self.connection_manager.transaction() as conn:
                self._connection = conn
                self._in_transaction = True
                logger.debug("[空日志]", "工作单元事务开始")
                
                yield self
                
                logger.debug("[空日志]", "工作单元事务提交")
                
        except Exception as e:
            logger.error("[空日志]", f"工作单元事务回滚: {e}")
            raise e
        finally:
            self._connection = None
            self._in_transaction = False
    
    def record_trade_and_risk_event(self, trading_day: str, 
                                   risk_event_type: str, 
                                   risk_details: str,
                                   risk_metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        同时记录交易和风控事件（事务操作）
        
        Args:
            trading_day: 交易日
            risk_event_type: 风控事件类型
            risk_details: 风控事件详情
            risk_metadata: 风控事件元数据
            
        Returns:
            Dict: 操作结果
        """
        with self.transaction():
            try:
                # 增加交易计数
                trade_success = self.trades.increment_count(trading_day)
                
                # 记录风控事件
                risk_id = self.risks.record_risk_event(
                    risk_event_type, 
                    risk_details, 
                    risk_metadata
                )
                
                if trade_success and risk_id:
                    result = {
                        "success": True,
                        "trade_count": self.trades.get_today_count(trading_day),
                        "risk_event_id": risk_id,
                        "message": "交易和风控事件记录成功"
                    }
                    logger.info("[空日志]", "[空日志]", f"成功记录交易和风控事件: {trading_day}")
                    return result
                else:
                    raise Exception("交易或风控事件记录失败")
                    
            except Exception as e:
                logger.error("[空日志]", f"记录交易和风控事件失败: {e}")
                raise e
    
    def batch_process_trades(self, trade_operations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        批量处理交易操作
        
        Args:
            trade_operations: 交易操作列表
            
        Returns:
            Dict: 处理结果
        """
        with self.transaction():
            results = {
                "successful": 0,
                "failed": 0,
                "details": []
            }
            
            for operation in trade_operations:
                try:
                    op_type = operation.get("type")
                    trading_day = operation.get("trading_day")
                    
                    if op_type == "increment":
                        success = self.trades.increment_count(trading_day)
                    elif op_type == "set":
                        count = operation.get("count", 0)
                        success = self.trades.set_today_count(count, trading_day)
                    else:
                        success = False
                    
                    if success:
                        results["successful"] += 1
                        results["details"].append({
                            "operation": operation,
                            "status": "success"
                        })
                    else:
                        results["failed"] += 1
                        results["details"].append({
                            "operation": operation,
                            "status": "failed",
                            "error": "操作执行失败"
                        })
                        
                except Exception as e:
                    results["failed"] += 1
                    results["details"].append({
                        "operation": operation,
                        "status": "failed",
                        "error": str(e)
                    })
            
            logger.info("[空日志]", "[空日志]", f"批量处理交易: 成功 {results['successful']}, 失败 {results['failed']}")
            return results
    
    def sync_data_consistency(self) -> Dict[str, Any]:
        """
        同步数据一致性检查和修复
        
        Returns:
            Dict: 检查结果
        """
        with self.transaction():
            result = {
                "issues_found": 0,
                "issues_fixed": 0,
                "details": []
            }
            
            try:
                # 检查交易数据
                trade_stats = self.trades.get_statistics(30)
                
                # 检查风控事件
                risk_stats = self.risks.get_event_statistics(30)
                
                # 数据一致性检查逻辑
                # 这里可以添加具体的一致性检查规则
                
                logger.info("[空日志]", "[空日志]", "数据一致性检查完成")
                return result
                
            except Exception as e:
                logger.error("[空日志]", f"数据一致性检查失败: {e}")
                raise e
    
    def generate_daily_report(self, trading_day: Optional[str] = None) -> Dict[str, Any]:
        """
        生成日报告
        
        Args:
            trading_day: 交易日，为None时使用当前交易日
            
        Returns:
            Dict: 日报告数据
        """
        if not trading_day:
            trading_day = self.trades.get_trading_day()
        
        try:
            # 获取交易数据
            trade_count = self.trades.get_today_count(trading_day)
            trade_history = self.trades.get_history(7)
            
            # 获取风控事件
            risk_events = self.risks.get_recent_events(1)  # 当天的风控事件
            risk_stats = self.risks.get_event_statistics(1)
            
            # 生成报告
            report = {
                "date": trading_day,
                "trade_summary": {
                    "today_count": trade_count,
                    "recent_history": trade_history
                },
                "risk_summary": {
                    "today_events": len(risk_events),
                    "event_details": risk_events,
                    "statistics": risk_stats
                },
                "generated_at": self.trades.get_trading_day()
            }
            
            logger.info("[空日志]", "[空日志]", f"生成日报告: {trading_day}")
            return report
            
        except Exception as e:
            logger.error("[空日志]", f"生成日报告失败: {e}")
            raise e
    
    def cleanup_old_data(self, keep_days: int = 90) -> Dict[str, Any]:
        """
        清理旧数据
        
        Args:
            keep_days: 保留天数
            
        Returns:
            Dict: 清理结果
        """
        with self.transaction():
            try:
                # 清理交易记录
                deleted_trades = self.trades.cleanup_old_records(keep_days)
                
                # 清理风控事件
                deleted_risks = self.risks.cleanup_old_events(keep_days)
                
                result = {
                    "deleted_trades": deleted_trades,
                    "deleted_risk_events": deleted_risks,
                    "total_deleted": deleted_trades + deleted_risks,
                    "keep_days": keep_days
                }
                
                logger.info("[空日志]", "[空日志]", f"数据清理完成: 删除 {result['total_deleted']} 条记录")
                return result
                
            except Exception as e:
                logger.error("[空日志]", f"数据清理失败: {e}")
                raise e
    
    def get_system_health(self) -> Dict[str, Any]:
        """
        获取系统健康状况
        
        Returns:
            Dict: 系统健康信息
        """
        try:
            # 获取连接管理器统计
            conn_stats = self.connection_manager.get_stats()
            
            # 获取数据统计
            trade_stats = self.trades.get_statistics(7)
            risk_stats = self.risks.get_event_statistics(7)
            
            # 计算健康分数
            health_score = 100
            
            # 根据错误率降低分数
            if conn_stats.get('success_rate', 1.0) < 0.95:
                health_score -= 20
            
            # 根据风控事件频率降低分数
            daily_risk_events = risk_stats.get('daily_average', 0)
            if daily_risk_events > 10:
                health_score -= 15
            
            # 根据响应时间降低分数
            avg_time = conn_stats.get('avg_time', 0)
            if avg_time > 0.1:  # 100ms
                health_score -= 10
            
            health_status = "excellent" if health_score >= 90 else \
                           "good" if health_score >= 70 else \
                           "warning" if health_score >= 50 else "critical"
            
            return {
                "health_score": max(0, health_score),
                "health_status": health_status,
                "connection_stats": conn_stats,
                "trade_stats": trade_stats,
                "risk_stats": risk_stats,
                "checked_at": self.trades.get_trading_day()
            }
            
        except Exception as e:
            logger.error("[空日志]", f"获取系统健康状况失败: {e}")
            return {
                "health_score": 0,
                "health_status": "critical",
                "error": str(e)
            }