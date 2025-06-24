"""
接口定义模块

这个包包含了系统中主要组件的抽象接口定义
通过接口抽象，可以实现：
1. 更好的代码解耦
2. 更容易的单元测试（Mock接口）
3. 更清晰的架构设计
4. 更容易的功能扩展

所有接口都与现有实现并行，不影响现有代码的正常运行
"""

from .trader_interface import ITrader
from .database_interface import IDatabase  
from .config_interface import IConfigManager

__all__ = [
    'ITrader',
    'IDatabase', 
    'IConfigManager'
]