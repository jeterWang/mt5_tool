"""
适配器模块

这个包提供适配器类，让现有的实现类可以实现新定义的接口
通过适配器模式，我们可以在不修改现有代码的情况下实现接口兼容

适配器的作用：
1. 保持现有代码不变
2. 提供接口兼容性
3. 便于单元测试
4. 支持依赖注入
"""

from .trader_adapter import MT5TraderAdapter
from .database_adapter import DatabaseAdapter
from .config_adapter import ConfigManagerAdapter

__all__ = [
    # 配置适配器
    'ConfigManagerAdapter',
    
    # 数据库适配器  
    'DatabaseAdapter',
    
    # GUI适配器
    'MT5GUIAdapter',
    'create_gui_adapter',
    'with_controller',
    
    # 交易适配器
    'MT5TraderAdapter', 
    'create_trader_interface',
    
    # 数据层适配器
    'EnhancedTradeDatabase',
    'create_enhanced_database',
    'create_standard_database',
    'DatabaseMigrationHelper',
    
    # API适配器 (新增)
    'MT5APIAdapter',
    'get_api_adapter', 
    'initialize_api_adapter',
    'create_api_adapter',
    'cleanup_api_adapter',
    'MT5APIIntegration',
    'APICompatibilityLayer'
]