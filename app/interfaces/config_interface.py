"""
配置管理接口定义

定义了配置管理器应该实现的所有方法
这个接口可以被不同的配置管理实现类使用
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Callable, List, Optional


class IConfigManager(ABC):
    """
    配置管理抽象接口
    
    定义了配置管理的标准操作
    可以有多种实现：JSON文件、数据库、远程配置等
    """
    
    # === 基础配置操作 ===
    
    @abstractmethod
    def load(self) -> None:
        """从存储源加载配置"""
        pass
    
    @abstractmethod
    def save(self) -> None:
        """保存配置到存储源"""
        pass
    
    @abstractmethod
    def reload(self) -> None:
        """重新加载配置"""
        pass
    
    # === 配置读写 ===
    
    @abstractmethod
    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置值
        
        Args:
            key: 配置键，支持点分割路径
            default: 默认值
            
        Returns:
            Any: 配置值
        """
        pass
    
    @abstractmethod
    def set(self, key: str, value: Any) -> None:
        """
        设置配置值
        
        Args:
            key: 配置键，支持点分割路径
            value: 配置值
        """
        pass
    
    @abstractmethod
    def update(self, updates: Dict[str, Any]) -> None:
        """
        批量更新配置
        
        Args:
            updates: 配置更新字典
        """
        pass
    
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """
        返回配置的字典表示
        
        Returns:
            Dict[str, Any]: 配置字典
        """
        pass
    
    # === 配置监听 ===
    
    @abstractmethod
    def add_listener(self, callback: Callable[[str, Any], None]) -> None:
        """
        添加配置变更监听器
        
        Args:
            callback: 回调函数 (key, value) -> None
        """
        pass
    
    @abstractmethod
    def remove_listener(self, callback: Callable[[str, Any], None]) -> None:
        """
        移除配置变更监听器
        
        Args:
            callback: 要移除的回调函数
        """
        pass
    
    # === 配置验证 ===
    
    @abstractmethod
    def validate(self) -> List[str]:
        """
        验证配置的有效性
        
        Returns:
            List[str]: 验证错误列表，空列表表示验证通过
        """
        pass
    
    @abstractmethod
    def has_required_fields(self) -> bool:
        """
        检查是否包含所有必需字段
        
        Returns:
            bool: 是否包含所有必需字段
        """
        pass
    
    # === 便捷属性访问 ===
    
    @property
    @abstractmethod
    def symbols(self) -> List[str]:
        """交易品种列表"""
        pass
    
    @property
    @abstractmethod
    def daily_trade_limit(self) -> int:
        """日交易次数限制"""
        pass
    
    @property
    @abstractmethod
    def daily_loss_limit(self) -> float:
        """日亏损限额"""
        pass


class IConfigValidator(ABC):
    """
    配置验证器接口
    
    用于验证配置的有效性和完整性
    """
    
    @abstractmethod
    def validate_config(self, config: Dict[str, Any]) -> List[str]:
        """
        验证配置
        
        Args:
            config: 配置字典
            
        Returns:
            List[str]: 错误信息列表
        """
        pass
    
    @abstractmethod
    def get_required_fields(self) -> List[str]:
        """
        获取必需字段列表
        
        Returns:
            List[str]: 必需字段列表
        """
        pass
    
    @abstractmethod
    def get_field_types(self) -> Dict[str, type]:
        """
        获取字段类型映射
        
        Returns:
            Dict[str, type]: 字段类型字典
        """
        pass


class IConfigSource(ABC):
    """
    配置源接口
    
    定义了配置数据的来源，可以是文件、数据库、网络等
    """
    
    @abstractmethod
    def read_config(self) -> Dict[str, Any]:
        """
        读取配置数据
        
        Returns:
            Dict[str, Any]: 配置数据
        """
        pass
    
    @abstractmethod
    def write_config(self, config: Dict[str, Any]) -> bool:
        """
        写入配置数据
        
        Args:
            config: 配置数据
            
        Returns:
            bool: 写入是否成功
        """
        pass
    
    @abstractmethod
    def exists(self) -> bool:
        """
        检查配置源是否存在
        
        Returns:
            bool: 配置源是否存在
        """
        pass
    
    @abstractmethod
    def backup(self) -> bool:
        """
        备份配置
        
        Returns:
            bool: 备份是否成功
        """
        pass