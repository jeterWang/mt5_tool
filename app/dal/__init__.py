"""
数据访问层(Data Access Layer)

提供高级的数据库操作接口，包括：
- 仓储模式(Repository Pattern)
- 工作单元模式(Unit of Work Pattern)  
- 查询对象(Query Objects)
- 数据映射器(Data Mapper)
"""

from .base_repository import BaseRepository
from .trade_repository import TradeRepository
from .risk_repository import RiskRepository
from .unit_of_work import UnitOfWork
from .data_mapper import DataMapper

__all__ = [
    'BaseRepository',
    'TradeRepository', 
    'RiskRepository',
    'UnitOfWork',
    'DataMapper'
]