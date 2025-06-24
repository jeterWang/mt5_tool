"""
数据层适配器

为现有TradeDatabase类提供新数据层功能，保持100%向后兼容性
支持渐进式迁移到新的数据访问层
"""

from typing import Any, Dict, List, Optional
import os
from datetime import datetime

from ..database import TradeDatabase
from ..dal import TradeRepository, RiskRepository, UnitOfWork, DataMapper
from ..dal.data_mapper import TradeRecord, RiskEvent
from ..utils.connection_manager import get_connection_manager
from ..utils.logger import get_logger

logger = get_logger(__name__)

class EnhancedTradeDatabase(TradeDatabase):
    """增强版交易数据库类"""
    
    def __init__(self):
        super().__init__()
        
        # 初始化新的数据访问层组件
        self._trade_repository = None
        self._risk_repository = None
        self._unit_of_work = None
        self._data_mapper = DataMapper()
        self._enhanced_mode = False
        
    def enable_enhanced_mode(self):
        """启用增强模式（使用新的数据访问层）"""
        try:
            self._trade_repository = TradeRepository(self.db_path)
            self._risk_repository = RiskRepository(self.db_path)
            self._unit_of_work = UnitOfWork(self.db_path)
            self._enhanced_mode = True
            logger.info("[空日志]", "[空日志]", "数据层增强模式已启用")
        except Exception as e:
            logger.error("[空日志]", f"启用增强模式失败: {e}")
            self._enhanced_mode = False
    
    def disable_enhanced_mode(self):
        """禁用增强模式（回退到原有实现）"""
        self._enhanced_mode = False
        logger.info("[空日志]", "[空日志]", "数据层增强模式已禁用")
    
    def is_enhanced_mode_enabled(self) -> bool:
        """检查是否启用了增强模式"""
        return self._enhanced_mode
    
    # === 重写原有方法，提供增强功能 ===
    
    def get_today_count(self):
        """获取今日交易次数（增强版）"""
        if self._enhanced_mode and self._trade_repository:
            try:
                return self._trade_repository.get_today_count()
            except Exception as e:
                logger.warning("[空日志]", f"增强模式获取交易次数失败，回退到原方法: {e}")
        
        # 回退到原有实现
        return super().get_today_count()
    
    def increment_count(self):
        """增加交易次数（增强版）"""
        if self._enhanced_mode and self._trade_repository:
            try:
                return self._trade_repository.increment_count()
            except Exception as e:
                logger.warning("[空日志]", f"增强模式增加交易次数失败，回退到原方法: {e}")
        
        # 回退到原有实现
        return super().increment_count()
    
    def set_today_count(self, count):
        """设置今日交易次数（增强版）"""
        if self._enhanced_mode and self._trade_repository:
            try:
                return self._trade_repository.set_today_count(count)
            except Exception as e:
                logger.warning("[空日志]", f"增强模式设置交易次数失败，回退到原方法: {e}")
        
        # 回退到原有实现
        return super().set_today_count(count)
    
    def get_history(self, days: int = 7):
        """获取交易历史（增强版）"""
        if self._enhanced_mode and self._trade_repository:
            try:
                # 使用新方法获取数据
                history = self._trade_repository.get_history(days)
                
                # 转换为原有格式（tuple列表）
                return [(record["date"], record["count"]) for record in history]
            except Exception as e:
                logger.warning("[空日志]", f"增强模式获取历史失败，回退到原方法: {e}")
        
        # 回退到原有实现
        return super().get_history(days)
    
    def record_risk_event(self, event_type, details):
        """记录风控事件（增强版）"""
        if self._enhanced_mode and self._risk_repository:
            try:
                return self._risk_repository.record_risk_event(event_type, details)
            except Exception as e:
                logger.warning("[空日志]", f"增强模式记录风控事件失败，回退到原方法: {e}")
        
        # 回退到原有实现
        return super().record_risk_event(event_type, details)
    
    def get_risk_events(self, days=7):
        """获取风控事件（增强版）"""
        if self._enhanced_mode and self._risk_repository:
            try:
                # 使用新方法获取数据
                events = self._risk_repository.get_recent_events(days)
                
                # 转换为原有格式（tuple列表）
                return [
                    (event["id"], event["timestamp"], event["event_type"], event["details"])
                    for event in events
                ]
            except Exception as e:
                logger.warning("[空日志]", f"增强模式获取风控事件失败，回退到原方法: {e}")
        
        # 回退到原有实现
        return super().get_risk_events(days)
    
    # === 新增的增强功能 ===
    
    def get_trade_statistics(self, days: int = 30) -> Dict[str, Any]:
        """获取交易统计信息（新功能）"""
        if not self._enhanced_mode or not self._trade_repository:
            logger.warning("[空日志]", "获取交易统计需要启用增强模式")
            return {}
        
        try:
            return self._trade_repository.get_statistics(days)
        except Exception as e:
            logger.error("[空日志]", f"获取交易统计失败: {e}")
            return {}
    
    def get_risk_statistics(self, days: int = 30) -> Dict[str, Any]:
        """获取风控统计信息（新功能）"""
        if not self._enhanced_mode or not self._risk_repository:
            logger.warning("[空日志]", "获取风控统计需要启用增强模式")
            return {}
        
        try:
            return self._risk_repository.get_event_statistics(days)
        except Exception as e:
            logger.error("[空日志]", f"获取风控统计失败: {e}")
            return {}
    
    def search_risk_events(self, keyword: str, days: int = 30) -> List[Dict[str, Any]]:
        """搜索风控事件（新功能）"""
        if not self._enhanced_mode or not self._risk_repository:
            logger.warning("[空日志]", "搜索风控事件需要启用增强模式")
            return []
        
        try:
            return self._risk_repository.search_events(keyword, days)
        except Exception as e:
            logger.error("[空日志]", f"搜索风控事件失败: {e}")
            return []
    
    def generate_daily_report(self, trading_day: Optional[str] = None) -> Dict[str, Any]:
        """生成日报告（新功能）"""
        if not self._enhanced_mode or not self._unit_of_work:
            logger.warning("[空日志]", "生成日报告需要启用增强模式")
            return {}
        
        try:
            return self._unit_of_work.generate_daily_report(trading_day)
        except Exception as e:
            logger.error("[空日志]", f"生成日报告失败: {e}")
            return {}
    
    def get_system_health(self) -> Dict[str, Any]:
        """获取系统健康状况（新功能）"""
        if not self._enhanced_mode or not self._unit_of_work:
            logger.warning("[空日志]", "获取系统健康状况需要启用增强模式")
            return {"health_status": "unknown", "message": "需要启用增强模式"}
        
        try:
            return self._unit_of_work.get_system_health()
        except Exception as e:
            logger.error("[空日志]", f"获取系统健康状况失败: {e}")
            return {"health_status": "error", "error": str(e)}
    
    def batch_process_trades(self, operations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """批量处理交易（新功能）"""
        if not self._enhanced_mode or not self._unit_of_work:
            logger.warning("[空日志]", "批量处理交易需要启用增强模式")
            return {"success": False, "message": "需要启用增强模式"}
        
        try:
            return self._unit_of_work.batch_process_trades(operations)
        except Exception as e:
            logger.error("[空日志]", f"批量处理交易失败: {e}")
            return {"success": False, "error": str(e)}
    
    def cleanup_old_data(self, keep_days: int = 90) -> Dict[str, Any]:
        """清理旧数据（新功能）"""
        if not self._enhanced_mode or not self._unit_of_work:
            logger.warning("[空日志]", "清理旧数据需要启用增强模式")
            return {"success": False, "message": "需要启用增强模式"}
        
        try:
            return self._unit_of_work.cleanup_old_data(keep_days)
        except Exception as e:
            logger.error("[空日志]", f"清理旧数据失败: {e}")
            return {"success": False, "error": str(e)}
    
    def export_data(self, days: int = 30) -> Dict[str, Any]:
        """导出数据（新功能）"""
        if not self._enhanced_mode:
            logger.warning("[空日志]", "导出数据需要启用增强模式")
            return {}
        
        try:
            # 获取交易记录
            trade_history = self._trade_repository.get_history(days)
            trade_records = self._data_mapper.map_trade_records(trade_history)
            
            # 获取风控事件
            risk_events_data = self._risk_repository.get_recent_events(days)
            risk_events = self._data_mapper.map_risk_events(risk_events_data)
            
            # 格式化导出数据
            return self._data_mapper.export_to_excel_format(trade_records, risk_events)
            
        except Exception as e:
            logger.error("[空日志]", f"导出数据失败: {e}")
            return {}
    
    def get_connection_stats(self) -> Dict[str, Any]:
        """获取连接统计（新功能）"""
        if not self._enhanced_mode:
            return {"message": "需要启用增强模式"}
        
        try:
            connection_manager = get_connection_manager(self.db_path)
            return connection_manager.get_stats()
        except Exception as e:
            logger.error("[空日志]", f"获取连接统计失败: {e}")
            return {"error": str(e)}

# 工厂函数
def create_enhanced_database() -> EnhancedTradeDatabase:
    """创建增强版数据库实例"""
    return EnhancedTradeDatabase()

def create_standard_database() -> TradeDatabase:
    """创建标准数据库实例（原版）"""
    return TradeDatabase()

# 迁移助手
class DatabaseMigrationHelper:
    """数据库迁移助手"""
    
    @staticmethod
    def migrate_to_enhanced(database: TradeDatabase) -> EnhancedTradeDatabase:
        """从标准数据库迁移到增强数据库"""
        enhanced_db = EnhancedTradeDatabase()
        enhanced_db.db_path = database.db_path
        enhanced_db.conn = database.conn
        
        # 启用增强模式
        enhanced_db.enable_enhanced_mode()
        
        logger.info("[空日志]", "[空日志]", "数据库已迁移到增强模式")
        return enhanced_db
    
    @staticmethod
    def test_compatibility(database: Any) -> Dict[str, Any]:
        """测试兼容性"""
        results = {
            "compatible": True,
            "issues": [],
            "recommendations": []
        }
        
        try:
            # 测试基本方法
            methods_to_test = [
                'get_today_count',
                'get_trading_day',
                'get_history',
                'get_risk_events'
            ]
            
            for method_name in methods_to_test:
                if not hasattr(database, method_name):
                    results["compatible"] = False
                    results["issues"].append(f"缺少方法: {method_name}")
                
        except Exception as e:
            results["compatible"] = False
            results["issues"].append(f"兼容性测试失败: {e}")
        
        if isinstance(database, EnhancedTradeDatabase) and not database.is_enhanced_mode_enabled():
            results["recommendations"].append("建议启用增强模式以获得更好的性能")
        
        return results

# 使用示例
def example_usage():
    """使用示例"""
    # 创建增强版数据库
    db = create_enhanced_database()
    
    # 启用增强模式
    db.enable_enhanced_mode()
    
    # 使用原有方法（自动使用增强实现）
    # print(f"今日交易次数: {db.get_today_count()}")
    
    # 使用新功能
    stats = db.get_trade_statistics(30)
    # print(f"交易统计: {stats}")
    
    health = db.get_system_health()
    # print(f"系统健康: {health['health_status']}")
    
    # 可以随时禁用增强模式回退到原有实现
    db.disable_enhanced_mode()
    # print(f"回退后今日交易次数: {db.get_today_count()}")

if __name__ == "__main__":
    example_usage()