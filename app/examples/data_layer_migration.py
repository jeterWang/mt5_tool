"""
数据层迁移示例

展示如何从现有TradeDatabase迁移到新的数据访问层
包含渐进式迁移策略和兼容性示例
"""

import os
import sys
import logging
logger = logging.getLogger(__name__)
from datetime import datetime, timedelta
from typing import Dict, Any, List

# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from app.database import TradeDatabase
from app.adapters.data_layer_adapter import EnhancedTradeDatabase, DatabaseMigrationHelper
from app.dal import TradeRepository, RiskRepository, UnitOfWork, DataMapper
from app.dal.data_mapper import TradeRecord, RiskEvent

def demonstrate_original_usage():
    """演示原有数据库用法"""
    # print("=== 原有数据库用法演示 ===")
    
    try:
        # 使用原有的TradeDatabase
        db = TradeDatabase()
        
        # 原有方法调用
        # print(f"今日交易次数: {db.get_today_count()}")
        # print(f"交易日: {db.get_trading_day()}")
        
        # 增加交易次数
        if db.increment_count():
            pass
            # print("交易次数增加成功")
        
        # 获取历史记录
        history = db.get_history(3)
        # print(f"最近3天历史: {history}")
        
        # 记录风控事件
        if db.record_risk_event("测试事件", "数据层迁移演示"):
            pass
            # print("风控事件记录成功")
        
        # 获取风控事件
        events = db.get_risk_events(3)
        # print(f"最近风控事件数量: {len(events) if events else 0}")
        
    except Exception as e:
        logger.error("[空日志]", f"原有数据库演示失败: {e}")

def demonstrate_enhanced_compatibility():
    """演示增强数据库的兼容性"""
    # print("\n=== 增强数据库兼容性演示 ===")
    
    try:
        # 创建增强版数据库（但不启用增强模式）
        enhanced_db = EnhancedTradeDatabase()
        
        # print("未启用增强模式 - 使用原有实现:")
        # print(f"今日交易次数: {enhanced_db.get_today_count()}")
        
        # 启用增强模式
        enhanced_db.enable_enhanced_mode()
        # print("已启用增强模式 - 使用增强实现:")
        # print(f"今日交易次数: {enhanced_db.get_today_count()}")
        
        # 测试原有方法（现在使用增强实现）
        if enhanced_db.increment_count():
            pass
            # print("增强模式交易次数增加成功")
        
        history = enhanced_db.get_history(3)
        # print(f"增强模式历史记录: {len(history) if history else 0} 条")
        
        # 测试新功能
        stats = enhanced_db.get_trade_statistics(7)
        # print(f"交易统计 - 总交易数: {stats.get('total_trades', 0)}")
        
        health = enhanced_db.get_system_health()
        # print(f"系统健康状况: {health.get('health_status', 'unknown')}")
        
        # 可以随时禁用增强模式
        enhanced_db.disable_enhanced_mode()
        # print("已禁用增强模式 - 回退到原有实现")
        
    except Exception as e:
        logger.error("[空日志]", f"增强数据库演示失败: {e}")

def demonstrate_repository_pattern():
    """演示仓储模式的使用"""
    # print("\n=== 仓储模式演示 ===")
    
    try:
        # 获取数据库路径
        from utils.paths import get_data_path
        db_path = get_data_path("trade_history.db")
        
        # 创建仓储实例
        trade_repo = TradeRepository(db_path)
        risk_repo = RiskRepository(db_path)
        
        # 使用仓储模式操作数据
        trading_day = trade_repo.get_trading_day()
        # print(f"当前交易日: {trading_day}")
        
        # 获取交易统计
        stats = trade_repo.get_statistics(7)
        # print(f"7天交易统计: {stats}")
        
        # 记录风控事件
        risk_id = risk_repo.record_risk_event(
            "仓储模式测试", 
            "演示仓储模式的风控事件记录",
            {"source": "migration_demo", "severity": "low"}
        )
        # print(f"风控事件记录ID: {risk_id}")
        
        # 搜索风控事件
        search_results = risk_repo.search_events("测试", 7)
        # print(f"搜索到风控事件: {len(search_results)} 条")
        
    except Exception as e:
        logger.error("[空日志]", f"仓储模式演示失败: {e}")

def demonstrate_unit_of_work():
    """演示工作单元模式"""
    # print("\n=== 工作单元模式演示 ===")
    
    try:
        from utils.paths import get_data_path
        db_path = get_data_path("trade_history.db")
        
        # 创建工作单元
        uow = UnitOfWork(db_path)
        
        # 使用事务操作
        with uow.transaction():
            # 同时记录交易和风控事件
            result = uow.record_trade_and_risk_event(
                trading_day=uow.trades.get_trading_day(),
                risk_event_type="工作单元测试",
                risk_details="演示事务性操作",
                risk_metadata={"demo": True, "timestamp": datetime.now().isoformat()}
            )
            # print(f"事务操作结果: {result}")
        
        # 生成日报告
        report = uow.generate_daily_report()
        # print(f"日报告生成: 交易 {report.get('trade_summary', {}).get('today_count', 0)} 次")
        
        # 获取系统健康状况
        health = uow.get_system_health()
        # print(f"系统健康分数: {health.get('health_score', 0)}")
        
    except Exception as e:
        logger.error("[空日志]", f"工作单元演示失败: {e}")

def demonstrate_data_mapper():
    """演示数据映射器"""
    # print("\n=== 数据映射器演示 ===")
    
    try:
        mapper = DataMapper()
        
        # 创建数据对象
        trade_record = TradeRecord(
            date="2024-01-15",
            count=5
        )
        
        risk_event = RiskEvent(
            event_type="映射器测试",
            details="演示数据映射功能",
            metadata={"test": True, "priority": "low"}
        )
        
        # print(f"交易记录: {trade_record}")
        # print(f"风控事件: {risk_event}")
        
        # 转换为字典
        trade_dict = mapper.trade_record_to_dict(trade_record)
        risk_dict = mapper.risk_event_to_dict(risk_event)
        
        # print(f"交易记录字典: {trade_dict}")
        # print(f"风控事件字典: {risk_dict}")
        
        # 验证数据
        trade_validation = mapper.validate_trade_record(trade_dict)
        risk_validation = mapper.validate_risk_event(risk_dict)
        
        logger.error("[空日志]", f"交易记录验证: {'通过' if trade_validation['valid'] else '失败'}")
        logger.error("[空日志]", f"风控事件验证: {'通过' if risk_validation['valid'] else '失败'}")
        
    except Exception as e:
        logger.error("[空日志]", f"数据映射器演示失败: {e}")

def demonstrate_migration_strategies():
    """演示迁移策略"""
    # print("\n=== 迁移策略演示 ===")
    
    try:
        # 策略1: 直接替换（推荐用于新项目）
        # print("策略1: 直接使用增强数据库")
        enhanced_db = EnhancedTradeDatabase()
        enhanced_db.enable_enhanced_mode()
        
        # 策略2: 渐进式迁移（推荐用于现有项目）
        # print("策略2: 从现有数据库迁移")
        original_db = TradeDatabase()
        migrated_db = DatabaseMigrationHelper.migrate_to_enhanced(original_db)
        
        # 测试兼容性
        compatibility = DatabaseMigrationHelper.test_compatibility(migrated_db)
        logger.error("[空日志]", f"兼容性测试: {'通过' if compatibility['compatible'] else '失败'}")
        
        if compatibility['recommendations']:
            # print("建议:")
            for rec in compatibility['recommendations']:
                pass
                # print(f"  - {rec}")
        
        # 策略3: 混合使用（适合过渡期）
        # print("策略3: 混合使用模式")
        
        # 对于关键操作使用原有方法
        trade_count_original = original_db.get_today_count()
        
        # 对于新功能使用增强方法
        if migrated_db.is_enhanced_mode_enabled():
            stats = migrated_db.get_trade_statistics(7)
            health = migrated_db.get_system_health()
            # print(f"混合模式 - 原有: {trade_count_original}, 增强: {stats.get('total_trades', 0)}")
        
    except Exception as e:
        logger.error("[空日志]", f"迁移策略演示失败: {e}")

def demonstrate_performance_comparison():
    """演示性能对比"""
    # print("\n=== 性能对比演示 ===")
    
    try:
        import time
        
        # 创建两个数据库实例
        original_db = TradeDatabase()
        enhanced_db = EnhancedTradeDatabase()
        enhanced_db.enable_enhanced_mode()
        
        # 测试原有方法性能
        start_time = time.time()
        for i in range(10):
            count = original_db.get_today_count()
        original_time = time.time() - start_time
        
        # 测试增强方法性能
        start_time = time.time()
        for i in range(10):
            count = enhanced_db.get_today_count()
        enhanced_time = time.time() - start_time
        
        # print(f"原有方法平均耗时: {original_time/10*1000:.2f}ms")
        # print(f"增强方法平均耗时: {enhanced_time/10*1000:.2f}ms")
        
        if enhanced_time < original_time:
            improvement = (original_time - enhanced_time) / original_time * 100
            # print(f"性能提升: {improvement:.1f}%")
        
        # 展示连接统计
        if enhanced_db.is_enhanced_mode_enabled():
            conn_stats = enhanced_db.get_connection_stats()
            # print(f"连接统计: {conn_stats}")
        
    except Exception as e:
        logger.error("[空日志]", f"性能对比演示失败: {e}")

def main():
    """主函数 - 运行所有演示"""
    # print("数据层迁移演示\n" + "="*50)
    
    try:
        # 演示各种迁移模式和功能
        demonstrate_original_usage()
        demonstrate_enhanced_compatibility()
        demonstrate_repository_pattern()
        demonstrate_unit_of_work()
        demonstrate_data_mapper()
        demonstrate_migration_strategies()
        demonstrate_performance_comparison()
        
        # print("\n" + "="*50)
        # print("数据层迁移演示完成")
        # print("\n迁移建议:")
        # print("1. 对于新项目: 直接使用EnhancedTradeDatabase + enable_enhanced_mode()")
        # print("2. 对于现有项目: 使用DatabaseMigrationHelper.migrate_to_enhanced()")
        # print("3. 迁移期间: 可以随时disable_enhanced_mode()回退到原有实现")
        # print("4. 性能监控: 使用get_system_health()和get_connection_stats()")
        # print("5. 数据管理: 使用UnitOfWork进行复杂事务操作")
        
    except Exception as e:
        logger.error("[空日志]", f"演示过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()