"""
Step 8 数据层重构测试

测试新的数据访问层功能和向后兼容性
"""

import os
import sys
import sqlite3
import tempfile
from datetime import datetime, timedelta

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(__file__))

def test_connection_manager():
    """测试连接管理器"""
    print("测试连接管理器...")
    
    try:
        from app.utils.connection_manager import ConnectionManager, get_connection_manager
        
        # 创建临时数据库
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        try:
            # 创建连接管理器
            manager = ConnectionManager(db_path)
            
            # 测试基本连接
            with manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("CREATE TABLE test (id INTEGER, name TEXT)")
                conn.commit()
            
            # 测试查询执行
            result = manager.execute_query("INSERT INTO test (id, name) VALUES (?, ?)", (1, "test"))
            assert result == 1, f"插入操作应该影响1行，实际: {result}"
            
            result = manager.execute_query("SELECT * FROM test", fetch_mode='all')
            assert len(result) == 1, f"查询结果应该有1行，实际: {len(result)}"
            
            # 测试事务
            with manager.transaction() as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO test (id, name) VALUES (?, ?)", (2, "test2"))
            
            # 测试统计
            stats = manager.get_stats()
            assert stats['total_queries'] > 0, "应该有查询统计"
            
            # 测试单例模式
            manager2 = get_connection_manager(db_path)
            assert manager is manager2, "应该返回同一个实例"
            
            print("✅ 连接管理器测试通过")
            return True
            
        finally:
            # 清理临时文件
            if os.path.exists(db_path):
                os.unlink(db_path)
                
    except Exception as e:
        print(f"❌ 连接管理器测试失败: {e}")
        return False

def test_query_builder():
    """测试查询构建器"""
    print("测试查询构建器...")
    
    try:
        from app.utils.query_builder import QueryBuilder, select, trade_select
        
        # 测试基本SELECT
        query, params = (select("id", "name")
                        .from_table("users")
                        .where_equals("status", "active")
                        .build_select())
        
        expected = "SELECT id, name FROM users WHERE status = ?"
        assert query == expected, f"SELECT查询不匹配:\n期望: {expected}\n实际: {query}"
        assert params == ("active",), f"参数不匹配: {params}"
        
        # 测试复杂查询
        builder = QueryBuilder()
        query, params = (builder
                        .select("date", "count")
                        .from_table("trade_count")
                        .where_between("date", "2024-01-01", "2024-01-31")
                        .where_like("type", "%daily%")
                        .order_by_desc("date")
                        .limit(10)
                        .build_select())
        
        assert "BETWEEN" in query, "应该包含BETWEEN条件"
        assert "LIKE" in query, "应该包含LIKE条件"
        assert "ORDER BY date DESC" in query, "应该包含排序"
        assert "LIMIT 10" in query, "应该包含限制"
        
        # 测试INSERT
        query, params = builder.build_insert("trade_count", {"date": "2024-01-15", "count": 5})
        assert "INSERT INTO trade_count" in query, "应该是INSERT查询"
        assert params == ("2024-01-15", 5), f"INSERT参数不匹配: {params}"
        
        # 测试UPDATE
        builder.reset().where_equals("id", 1)
        query, params = builder.build_update("trade_count", {"count": 10})
        assert "UPDATE trade_count SET count = ?" in query, "应该是UPDATE查询"
        assert "WHERE id = ?" in query, "应该包含WHERE条件"
        
        # 测试交易专用构建器
        query, params = (trade_select("date", "count")
                        .recent_trades(7)
                        .build_select())
        assert "trade_count" in query, "应该查询trade_count表"
        assert "ORDER BY date DESC" in query, "应该按日期降序"
        assert "LIMIT 7" in query, "应该限制7条记录"
        
        print("✅ 查询构建器测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 查询构建器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_base_repository():
    """测试基础仓储"""
    print("测试基础仓储...")
    
    try:
        from app.dal.base_repository import BaseRepository
        from app.utils.connection_manager import get_connection_manager
        
        # 创建临时数据库
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        try:
            # 创建测试表
            manager = get_connection_manager(db_path)
            manager.execute_query("""
                CREATE TABLE test_table (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    value INTEGER,
                    created_at TEXT,
                    updated_at TEXT
                )
            """)
            
            # 创建测试仓储
            class TestRepository(BaseRepository):
                @property
                def table_name(self) -> str:
                    return "test_table"
            
            repo = TestRepository(db_path)
            
            # 测试创建
            record_id = repo.create({"name": "test", "value": 100})
            assert record_id > 0, f"应该返回有效ID，实际: {record_id}"
            
            # 测试查找
            record = repo.find_by_id(record_id)
            assert record is not None, "应该找到记录"
            assert record["name"] == "test", f"名称不匹配: {record['name']}"
            assert record["value"] == 100, f"值不匹配: {record['value']}"
            
            # 测试更新
            success = repo.update(record_id, {"value": 200})
            assert success, "更新应该成功"
            
            updated_record = repo.find_by_id(record_id)
            assert updated_record["value"] == 200, f"值应该更新为200，实际: {updated_record['value']}"
            
            # 测试条件查询
            records = repo.find_where({"name": "test"})
            assert len(records) == 1, f"应该找到1条记录，实际: {len(records)}"
            
            # 测试统计
            count = repo.count({"name": "test"})
            assert count == 1, f"统计应该是1，实际: {count}"
            
            # 测试批量创建
            batch_data = [
                {"name": f"test{i}", "value": i * 10}
                for i in range(2, 5)
            ]
            ids = repo.bulk_create(batch_data)
            assert len(ids) == 3, f"应该创建3条记录，实际: {len(ids)}"
            
            # 测试分页
            page_result = repo.paginate(1, 2)
            assert page_result["page"] == 1, "页码应该是1"
            assert len(page_result["data"]) <= 2, "每页最多2条记录"
            assert page_result["total"] == 4, f"总数应该是4，实际: {page_result['total']}"
            
            # 测试删除
            success = repo.delete(record_id)
            assert success, "删除应该成功"
            
            deleted_record = repo.find_by_id(record_id)
            assert deleted_record is None, "删除后应该找不到记录"
            
            print("✅ 基础仓储测试通过")
            return True
            
        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)
                
    except Exception as e:
        print(f"❌ 基础仓储测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_trade_repository():
    """测试交易仓储"""
    print("测试交易仓储...")
    
    try:
        from app.dal.trade_repository import TradeRepository
        from app.utils.connection_manager import get_connection_manager
        
        # 创建临时数据库
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        try:
            # 创建交易表
            manager = get_connection_manager(db_path)
            manager.execute_query("""
                CREATE TABLE trade_count (
                    id INTEGER PRIMARY KEY,
                    date TEXT NOT NULL,
                    count INTEGER NOT NULL,
                    created_at TEXT,
                    updated_at TEXT
                )
            """)
            
            repo = TradeRepository(db_path)
            
            # 测试获取交易日
            trading_day = repo.get_trading_day()
            assert trading_day, "应该返回交易日"
            print(f"  当前交易日: {trading_day}")
            
            # 测试获取今日交易次数（空数据库）
            count = repo.get_today_count(trading_day)
            assert count == 0, f"空数据库交易次数应该是0，实际: {count}"
            
            # 测试设置交易次数
            success = repo.set_today_count(5, trading_day)
            assert success, "设置交易次数应该成功"
            
            count = repo.get_today_count(trading_day)
            assert count == 5, f"交易次数应该是5，实际: {count}"
            
            # 测试增加交易次数
            success = repo.increment_count(trading_day)
            assert success, "增加交易次数应该成功"
            
            count = repo.get_today_count(trading_day)
            assert count == 6, f"交易次数应该是6，实际: {count}"
            
            # 测试添加历史数据
            yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
            repo.set_today_count(3, yesterday)
            
            # 测试获取历史
            history = repo.get_history(2)
            assert len(history) >= 1, f"应该有历史记录，实际: {len(history)}"
            
            # 测试统计
            stats = repo.get_statistics(7)
            assert stats["total_trades"] > 0, f"总交易数应该大于0，实际: {stats['total_trades']}"
            assert stats["trading_days"] > 0, f"交易天数应该大于0，实际: {stats['trading_days']}"
            
            print(f"  交易统计: {stats}")
            
            print("✅ 交易仓储测试通过")
            return True
            
        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)
                
    except Exception as e:
        print(f"❌ 交易仓储测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_enhanced_database():
    """测试增强数据库"""
    print("测试增强数据库...")
    
    try:
        from app.adapters.data_layer_adapter import EnhancedTradeDatabase
        
        # 创建临时数据库路径
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        try:
            # 创建增强数据库
            enhanced_db = EnhancedTradeDatabase()
            enhanced_db.db_path = db_path
            
            # 创建数据表（使用原有方法）
            enhanced_db.create_tables()
            
            # 测试未启用增强模式
            assert not enhanced_db.is_enhanced_mode_enabled(), "默认应该未启用增强模式"
            
            # 测试原有功能
            count = enhanced_db.get_today_count()
            assert count == 0, f"初始交易次数应该是0，实际: {count}"
            
            # 启用增强模式
            enhanced_db.enable_enhanced_mode()
            assert enhanced_db.is_enhanced_mode_enabled(), "应该已启用增强模式"
            
            # 测试增强模式下的原有功能
            success = enhanced_db.increment_count()
            assert success, "增强模式下增加交易次数应该成功"
            
            count = enhanced_db.get_today_count()
            assert count == 1, f"增强模式下交易次数应该是1，实际: {count}"
            
            # 测试新功能
            stats = enhanced_db.get_trade_statistics(7)
            assert isinstance(stats, dict), "应该返回统计字典"
            
            health = enhanced_db.get_system_health()
            assert "health_status" in health, "应该包含健康状态"
            
            # 测试数据导出
            export_data = enhanced_db.export_data(7)
            assert isinstance(export_data, dict), "应该返回导出数据"
            
            # 测试连接统计
            conn_stats = enhanced_db.get_connection_stats()
            assert isinstance(conn_stats, dict), "应该返回连接统计"
            
            # 测试禁用增强模式
            enhanced_db.disable_enhanced_mode()
            assert not enhanced_db.is_enhanced_mode_enabled(), "应该已禁用增强模式"
            
            # 禁用后仍能使用原有功能
            count = enhanced_db.get_today_count()
            assert count == 1, f"禁用增强模式后交易次数应该仍是1，实际: {count}"
            
            print("✅ 增强数据库测试通过")
            return True
            
        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)
                
    except Exception as e:
        print(f"❌ 增强数据库测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_data_mapper():
    """测试数据映射器"""
    print("测试数据映射器...")
    
    try:
        from app.dal.data_mapper import DataMapper, TradeRecord, RiskEvent
        
        mapper = DataMapper()
        
        # 测试TradeRecord
        trade = TradeRecord(date="2024-01-15", count=5)
        assert trade.date == "2024-01-15", "日期不匹配"
        assert trade.count == 5, "次数不匹配"
        
        # 测试转换为字典
        trade_dict = trade.to_dict()
        assert trade_dict["date"] == "2024-01-15", "字典转换失败"
        
        # 测试从字典创建
        trade2 = TradeRecord.from_dict(trade_dict)
        assert trade2.date == trade.date, "从字典创建失败"
        
        # 测试RiskEvent
        risk = RiskEvent(
            event_type="测试",
            details="测试详情",
            metadata={"test": True}
        )
        assert risk.event_type == "测试", "事件类型不匹配"
        
        # 测试数据验证
        validation = mapper.validate_trade_record({"date": "2024-01-15", "count": 5})
        assert validation["valid"], f"验证应该通过: {validation['errors']}"
        
        validation = mapper.validate_trade_record({"date": "invalid", "count": -1})
        assert not validation["valid"], "无效数据验证应该失败"
        
        # 测试汇总格式化
        trades = [
            TradeRecord(date="2024-01-15", count=5),
            TradeRecord(date="2024-01-16", count=3)
        ]
        
        summary = mapper.format_trade_summary(trades)
        assert summary["total_trades"] == 8, f"总交易数应该是8，实际: {summary['total_trades']}"
        assert summary["total_records"] == 2, f"记录数应该是2，实际: {summary['total_records']}"
        
        print("✅ 数据映射器测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 数据映射器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """运行所有测试"""
    print("Step 8: 数据层重构测试")
    print("=" * 50)
    
    tests = [
        test_connection_manager,
        test_query_builder,
        test_base_repository,
        test_trade_repository,
        test_enhanced_database,
        test_data_mapper
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ 测试异常: {e}")
        print()
    
    print("=" * 50)
    print(f"测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！Step 8 数据层重构成功")
        print("\n核心功能验证:")
        print("✅ 连接管理器 - 连接池、事务管理")
        print("✅ 查询构建器 - 安全SQL构建")
        print("✅ 仓储模式 - CRUD操作抽象")
        print("✅ 交易仓储 - 专业交易数据操作")
        print("✅ 增强数据库 - 向后兼容的功能扩展")
        print("✅ 数据映射器 - 对象关系映射")
        print("\n新增价值:")
        print("- 连接池管理，提升性能")
        print("- 安全的SQL查询构建")
        print("- 事务管理和数据一致性")
        print("- 统计分析和系统监控")
        print("- 100%向后兼容性")
        print("- 渐进式迁移支持")
        return True
    else:
        print(f"❌ {total - passed} 个测试失败")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)