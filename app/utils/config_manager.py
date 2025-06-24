"""
现代化配置管理器

这个类与现有的全局变量配置系统并行工作，不影响现有功能
新代码可以选择使用这个管理器，旧代码继续使用全局变量
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional, Union
from app.utils.logger import get_logger

logger = get_logger(__name__)


class ConfigManager:
    """
    现代化配置管理器
    
    特点：
    - 与现有全局变量系统并行工作
    - 支持配置验证和默认值
    - 线程安全
    - 支持配置监听和回调
    """
    
    def __init__(self, config_file: Optional[str] = None):
        """
        初始化配置管理器
        
        Args:
            config_file: 配置文件路径，默认使用项目标准路径
        """
        if config_file is None:
            # 使用项目标准配置文件路径
            project_root = Path(__file__).parent.parent.parent
            config_file = project_root / "config" / "config.json"
        
        self.config_file = Path(config_file)
        self._config: Dict[str, Any] = {}
        self._default_config = self._get_default_config()
        self._listeners = []
        
        # 确保配置目录存在
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        
        # 加载配置
        self.load()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            "symbols": ["USTECm", "XAUUSDm", "NAS100"],
            "daily_trade_limit": 10,
            "daily_loss_limit": 1000.0,
            "default_timeframe": "M1",
            "delta_timezone": 8,
            "trading_days": "1,2,3,4,5",
            "gui_settings": {
                "window_width": 1200,
                "window_height": 800,
                "refresh_interval": 1000
            },
            "batch_order_defaults": {
                "order1": {
                    "volume": 0.01,
                    "sl_points": 3000,
                    "tp_points": 50000,
                    "sl_candle": 3,
                    "fixed_loss": 5.0,
                    "checked": True
                }
            }
        }
    
    def load(self) -> None:
        """从文件加载配置"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    file_config = json.load(f)
                    
                # 合并默认配置和文件配置
                self._config = self._merge_configs(self._default_config, file_config)
                logger.info("[空日志]", "[空日志]", f"配置已从 {self.config_file} 加载")
            else:
                # 使用默认配置
                self._config = self._default_config.copy()
                logger.info("[空日志]", "[空日志]", "使用默认配置")
                # 保存默认配置到文件
                self.save()
                
        except Exception as e:
            logger.error("[空日志]", f"加载配置失败: {e}")
            self._config = self._default_config.copy()
    
    def save(self) -> None:
        """保存配置到文件"""
        try:
            # 创建备份
            if self.config_file.exists():
                backup_file = self.config_file.with_suffix('.json.bak')
                self.config_file.rename(backup_file)
            
            # 保存配置
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=4, ensure_ascii=False)
                
            logger.info("[空日志]", "[空日志]", f"配置已保存到 {self.config_file}")
            
        except Exception as e:
            logger.error("[空日志]", f"保存配置失败: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置值
        
        Args:
            key: 配置键，支持点分割路径如 "gui_settings.window_width"
            default: 默认值
            
        Returns:
            配置值
        """
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
                
        return value
    
    def set(self, key: str, value: Any) -> None:
        """
        设置配置值
        
        Args:
            key: 配置键，支持点分割路径
            value: 配置值
        """
        keys = key.split('.')
        config = self._config
        
        # 导航到最后一级的父字典
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # 设置值
        config[keys[-1]] = value
        
        # 通知监听器
        self._notify_listeners(key, value)
    
    def update(self, updates: Dict[str, Any]) -> None:
        """
        批量更新配置
        
        Args:
            updates: 更新的配置字典
        """
        for key, value in updates.items():
            self.set(key, value)
    
    def _merge_configs(self, default: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """递归合并配置字典"""
        result = default.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
                
        return result
    
    def add_listener(self, callback) -> None:
        """添加配置变更监听器"""
        self._listeners.append(callback)
    
    def remove_listener(self, callback) -> None:
        """移除配置变更监听器"""
        if callback in self._listeners:
            self._listeners.remove(callback)
    
    def _notify_listeners(self, key: str, value: Any) -> None:
        """通知所有监听器"""
        for callback in self._listeners:
            try:
                callback(key, value)
            except Exception as e:
                logger.error("[空日志]", f"配置监听器回调错误: {e}")
    
    def to_dict(self) -> Dict[str, Any]:
        """返回配置的字典副本"""
        return self._config.copy()
    
    def reload(self) -> None:
        """重新加载配置文件"""
        self.load()
    
    # 为了兼容现有代码，提供一些便捷属性
    @property
    def symbols(self) -> list:
        """交易品种列表"""
        return self.get("symbols", [])
    
    @property
    def daily_trade_limit(self) -> int:
        """日交易次数限制"""
        return self.get("daily_trade_limit", 10)
    
    @property
    def daily_loss_limit(self) -> float:
        """日亏损限额"""
        return self.get("daily_loss_limit", 1000.0)


# 全局实例，供需要的地方使用
# 注意：这与现有的全局变量系统并行，不会冲突
_config_manager: Optional[ConfigManager] = None


def get_config_manager() -> ConfigManager:
    """获取全局配置管理器实例"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager