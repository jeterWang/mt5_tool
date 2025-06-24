"""
配置管理适配器

将现有的ConfigManager类适配到IConfigManager接口
"""

from typing import Any, Dict, Callable, List, Optional

from ..interfaces.config_interface import IConfigManager


class ConfigManagerAdapter(IConfigManager):
    """
    配置管理适配器类
    """
    
    def __init__(self, config_manager):
        """
        初始化适配器
        
        Args:
            config_manager: 现有的ConfigManager实例
        """
        self._config_manager = config_manager
    
    def load(self) -> None:
        """从存储源加载配置"""
        return self._config_manager.load()
    
    def save(self) -> None:
        """保存配置到存储源"""
        return self._config_manager.save()
    
    def reload(self) -> None:
        """重新加载配置"""
        return self._config_manager.reload()
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        return self._config_manager.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """设置配置值"""
        return self._config_manager.set(key, value)
    
    def update(self, updates: Dict[str, Any]) -> None:
        """批量更新配置"""
        return self._config_manager.update(updates)
    
    def to_dict(self) -> Dict[str, Any]:
        """返回配置的字典表示"""
        return self._config_manager.to_dict()
    
    def add_listener(self, callback: Callable[[str, Any], None]) -> None:
        """添加配置变更监听器"""
        return self._config_manager.add_listener(callback)
    
    def remove_listener(self, callback: Callable[[str, Any], None]) -> None:
        """移除配置变更监听器"""
        return self._config_manager.remove_listener(callback)
    
    def validate(self) -> List[str]:
        """验证配置的有效性"""
        return self._config_manager.validate()
    
    def has_required_fields(self) -> bool:
        """检查是否包含所有必需字段"""
        return self._config_manager.has_required_fields()
    
    @property
    def symbols(self) -> List[str]:
        """交易品种列表"""
        return self._config_manager.symbols
    
    @property
    def daily_trade_limit(self) -> int:
        """日交易次数限制"""
        return self._config_manager.daily_trade_limit
    
    @property
    def daily_loss_limit(self) -> float:
        """日亏损限额"""
        return self._config_manager.daily_loss_limit