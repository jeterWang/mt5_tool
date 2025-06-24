#!/usr/bin/env python3
"""
接口系统验证脚本

验证新创建的接口系统是否能够正常导入和工作
"""

def test_interface_imports():
    """测试接口导入"""
    try:
        # 测试接口导入
        from app.interfaces import ITrader, IDatabase, IConfigManager
        print("[OK] 接口导入成功")
        
        # 测试适配器导入
        from app.adapters import MT5TraderAdapter
        print("[OK] \1")
        
        # 测试示例导入
        from app.examples.interface_usage import TradingService, MockTrader
        print("[OK] \1")
        
        return True
        
    except ImportError as e:
        print(f"[ERROR] 导入失败: {e}")
        return False


def test_interface_compatibility():
    """测试接口兼容性"""
    try:
        from app.interfaces.trader_interface import ITrader
        from app.examples.interface_usage import MockTrader
        
        # 测试MockTrader是否实现了ITrader接口
        mock_trader = MockTrader()
        
        # 测试基本方法是否存在
        assert hasattr(mock_trader, 'connect')
        assert hasattr(mock_trader, 'disconnect')
        assert hasattr(mock_trader, 'is_connected')
        assert hasattr(mock_trader, 'place_order')
        
        # 测试方法调用
        assert mock_trader.connect() == True
        assert mock_trader.is_connected() == True
        assert mock_trader.place_order("EURUSD", "BUY", 0.1) == True
        
        print("[OK] \1")
        return True
        
    except Exception as e:
        print(f"[ERROR] \1: {e}")
        return False


def test_adapter_pattern():
    """测试适配器模式"""
    try:
        # 创建一个简单的MT5Trader模拟类
        class SimpleMT5Trader:
            def __init__(self):
                self.connected = False
            
            def connect(self):
                self.connected = True
                return True
            
            def disconnect(self):
                self.connected = False
            
            def is_connected(self):
                return self.connected
            
            def place_order(self, symbol, order_type, volume, price=None, **kwargs):
                return True
        
        from app.adapters.trader_adapter import MT5TraderAdapter
        
        # 创建原始对象
        original_trader = SimpleMT5Trader()
        
        # 用适配器包装
        adapted_trader = MT5TraderAdapter(original_trader)
        
        # 测试适配器方法
        assert adapted_trader.connect() == True
        assert adapted_trader.is_connected() == True
        assert adapted_trader.place_order("EURUSD", "BUY", 0.1) == True
        
        print("[OK] \1")
        return True
        
    except Exception as e:
        print(f"[ERROR] \1: {e}")
        return False


def main():
    """主测试函数"""
    print("=== 接口系统验证测试 ===\n")
    
    all_passed = True
    
    # 测试1: 导入测试
    print("测试1: 模块导入")
    all_passed &= test_interface_imports()
    print()
    
    # 测试2: 接口兼容性
    print("测试2: 接口兼容性")
    all_passed &= test_interface_compatibility()
    print()
    
    # 测试3: 适配器模式
    print("测试3: 适配器模式")
    all_passed &= test_adapter_pattern()
    print()
    
    # 总结
    if all_passed:
        print("[SUCCESS] 所有测试通过！接口系统运行正常")
        print("\n=== 接口系统已就绪 ===")
        print("- ITrader: 交易者接口")
        print("- IDatabase: 数据库接口")
        print("- IConfigManager: 配置管理接口")
        print("- MT5TraderAdapter: 现有代码适配器")
        print("- 完整的使用示例和测试支持")
    else:
        print("[ERROR] \1")
    
    return all_passed


if __name__ == "__main__":
    main()