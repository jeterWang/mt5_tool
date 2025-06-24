"""
API适配器

提供向后兼容的API接口适配器，保持现有GUI接口不变
"""

from typing import Dict, Any, Optional, Callable
import threading
import time

from app.utils.logger import get_logger
from app.api.server import MT5APIServer, create_api_server, APIServerManager
from app.controllers.main_controller import get_controller
from app.utils.config_manager import get_config_manager

logger = get_logger(__name__)


class MT5APIAdapter:
    """MT5 API适配器
    
    提供API服务器的集成和管理功能，同时保持与现有系统的兼容性
    """
    
    def __init__(self, auto_start: bool = False):
        self.controller = get_controller()
        self.config_manager = get_config_manager()
        self.api_server: Optional[MT5APIServer] = None
        self.auto_start = auto_start
        self._initialized = False
        
        if auto_start:
            self.initialize()
    
    def initialize(self) -> bool:
        """初始化API适配器"""
        try:
            if self._initialized:
                logger.warning("API adapter already initialized")
                return True
            
            # 从配置获取API设置
            api_config = self._get_api_config()
            
            if api_config.get('enabled', False):
                success = self._start_api_server(api_config)
                if success:
                    logger.info("API adapter initialized successfully")
                    self._initialized = True
                    return True
                else:
                    logger.error("Failed to start API server")
                    return False
            else:
                logger.info("API server disabled in configuration")
                self._initialized = True
                return True
                
        except Exception as e:
            logger.error(f"API adapter initialization error: {e}")
            return False
    
    def _get_api_config(self) -> Dict[str, Any]:
        """获取API配置"""
        try:
            config = self.config_manager.get_config()
            return config.get('api', {
                'enabled': False,
                'host': 'localhost',
                'port': 8080,
                'auto_start': False,
                'security': {
                    'require_api_key': False,
                    'rate_limit': True,
                    'cors_enabled': True
                }
            })
        except Exception as e:
            logger.error(f"Failed to get API config: {e}")
            return {
                'enabled': False,
                'host': 'localhost',
                'port': 8080
            }
    
    def _start_api_server(self, config: Dict[str, Any]) -> bool:
        """启动API服务器"""
        try:
            host = config.get('host', 'localhost')
            port = config.get('port', 8080)
            
            self.api_server = create_api_server(host, port)
            
            if self.api_server.start():
                logger.info(f"API server started on {host}:{port}")
                return True
            else:
                logger.error("Failed to start API server")
                return False
                
        except Exception as e:
            logger.error(f"Error starting API server: {e}")
            return False
    
    def start_api_server(self, host: str = None, port: int = None) -> bool:
        """手动启动API服务器"""
        try:
            config = self._get_api_config()
            
            if host:
                config['host'] = host
            if port:
                config['port'] = port
            
            return self._start_api_server(config)
            
        except Exception as e:
            logger.error(f"Error starting API server: {e}")
            return False
    
    def stop_api_server(self) -> bool:
        """停止API服务器"""
        try:
            if self.api_server and self.api_server.is_running():
                self.api_server.stop()
                logger.info("API server stopped")
                return True
            else:
                logger.warning("API server is not running")
                return False
                
        except Exception as e:
            logger.error(f"Error stopping API server: {e}")
            return False
    
    def restart_api_server(self) -> bool:
        """重启API服务器"""
        try:
            self.stop_api_server()
            time.sleep(1)  # 等待端口释放
            return self.start_api_server()
            
        except Exception as e:
            logger.error(f"Error restarting API server: {e}")
            return False
    
    def is_api_running(self) -> bool:
        """检查API服务器是否运行中"""
        return self.api_server is not None and self.api_server.is_running()
    
    def get_api_status(self) -> Dict[str, Any]:
        """获取API服务器状态"""
        if self.api_server:
            return self.api_server.get_status()
        else:
            return {
                "running": False,
                "message": "API server not initialized"
            }
    
    def get_api_endpoints(self) -> Dict[str, Any]:
        """获取API端点信息"""
        if not self.api_server:
            return {"endpoints": [], "message": "API server not running"}
        
        status = self.api_server.get_status()
        base_url = status.get('url', 'http://localhost:8080')
        
        endpoints = [
            {
                "path": "/api/v1/status",
                "methods": ["GET"],
                "description": "获取系统状态",
                "url": f"{base_url}/api/v1/status"
            },
            {
                "path": "/api/v1/connection",
                "methods": ["GET", "POST", "DELETE"],
                "description": "MT5连接管理",
                "url": f"{base_url}/api/v1/connection"
            },
            {
                "path": "/api/v1/account",
                "methods": ["GET"],
                "description": "获取账户信息",
                "url": f"{base_url}/api/v1/account"
            },
            {
                "path": "/api/v1/positions",
                "methods": ["GET", "POST"],
                "description": "仓位管理",
                "url": f"{base_url}/api/v1/positions"
            },
            {
                "path": "/api/v1/orders",
                "methods": ["POST"],
                "description": "下单操作",
                "url": f"{base_url}/api/v1/orders"
            },
            {
                "path": "/api/v1/symbols",
                "methods": ["GET", "POST"],
                "description": "交易品种信息",
                "url": f"{base_url}/api/v1/symbols"
            }
        ]
        
        return {
            "base_url": base_url,
            "endpoints": endpoints,
            "total_count": len(endpoints)
        }
    
    def enable_api_in_config(self, save: bool = True) -> bool:
        """在配置中启用API"""
        try:
            config = self.config_manager.get_config()
            
            if 'api' not in config:
                config['api'] = {}
            
            config['api']['enabled'] = True
            
            if save:
                success = self.config_manager.save_config(config)
                if success:
                    logger.info("API enabled in configuration")
                    return True
                else:
                    logger.error("Failed to save API configuration")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error enabling API in config: {e}")
            return False
    
    def disable_api_in_config(self, save: bool = True) -> bool:
        """在配置中禁用API"""
        try:
            config = self.config_manager.get_config()
            
            if 'api' not in config:
                config['api'] = {}
            
            config['api']['enabled'] = False
            
            if save:
                success = self.config_manager.save_config(config)
                if success:
                    logger.info("API disabled in configuration")
                    return True
                else:
                    logger.error("Failed to save API configuration")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error disabling API in config: {e}")
            return False
    
    def update_api_config(self, **kwargs) -> bool:
        """更新API配置"""
        try:
            config = self.config_manager.get_config()
            
            if 'api' not in config:
                config['api'] = {}
            
            # 更新配置
            for key, value in kwargs.items():
                config['api'][key] = value
            
            success = self.config_manager.save_config(config)
            if success:
                logger.info(f"API configuration updated: {kwargs}")
                return True
            else:
                logger.error("Failed to save updated API configuration")
                return False
                
        except Exception as e:
            logger.error(f"Error updating API config: {e}")
            return False
    
    def cleanup(self):
        """清理资源"""
        try:
            if self.api_server and self.api_server.is_running():
                self.api_server.stop()
            self._initialized = False
            logger.info("API adapter cleaned up")
            
        except Exception as e:
            logger.error(f"Error during API adapter cleanup: {e}")


class MT5APIIntegration:
    """MT5 API集成类
    
    提供与现有主窗口的集成功能
    """
    
    def __init__(self, main_window=None):
        self.main_window = main_window
        self.api_adapter = MT5APIAdapter()
    
    def integrate_with_main_window(self):
        """与主窗口集成"""
        if not self.main_window:
            logger.warning("No main window provided for API integration")
            return
        
        try:
            # 在主窗口中添加API状态显示
            self._add_api_status_to_gui()
            
            # 添加API控制按钮
            self._add_api_controls_to_gui()
            
            logger.info("API integration with main window completed")
            
        except Exception as e:
            logger.error(f"Error integrating API with main window: {e}")
    
    def _add_api_status_to_gui(self):
        """在GUI中添加API状态显示"""
        # 这里应该在主窗口中添加API状态显示
        # 具体实现取决于主窗口的结构
        pass
    
    def _add_api_controls_to_gui(self):
        """在GUI中添加API控制按钮"""
        # 这里应该在主窗口中添加API启动/停止按钮
        # 具体实现取决于主窗口的结构
        pass


# 全局API适配器实例
_api_adapter: Optional[MT5APIAdapter] = None
_adapter_lock = threading.Lock()


def get_api_adapter() -> MT5APIAdapter:
    """获取全局API适配器实例"""
    global _api_adapter
    
    with _adapter_lock:
        if _api_adapter is None:
            _api_adapter = MT5APIAdapter()
        return _api_adapter


def initialize_api_adapter(auto_start: bool = False) -> bool:
    """初始化API适配器"""
    adapter = get_api_adapter()
    adapter.auto_start = auto_start
    return adapter.initialize()


def create_api_adapter(auto_start: bool = False) -> MT5APIAdapter:
    """创建新的API适配器实例"""
    return MT5APIAdapter(auto_start)


def cleanup_api_adapter():
    """清理API适配器"""
    global _api_adapter
    
    with _adapter_lock:
        if _api_adapter:
            _api_adapter.cleanup()
            _api_adapter = None


class APICompatibilityLayer:
    """API兼容性层
    
    提供与现有代码的兼容性，确保添加API不影响现有功能
    """
    
    @staticmethod
    def enable_api_for_existing_system():
        """为现有系统启用API"""
        try:
            # 获取配置管理器
            config_manager = get_config_manager()
            config = config_manager.get_config()
            
            # 检查是否已有API配置
            if 'api' not in config:
                config['api'] = {
                    'enabled': False,
                    'host': 'localhost',
                    'port': 8080,
                    'auto_start': False
                }
                config_manager.save_config(config)
                logger.info("API configuration added to existing system")
            
            return True
            
        except Exception as e:
            logger.error(f"Error enabling API for existing system: {e}")
            return False
    
    @staticmethod
    def check_api_compatibility() -> Dict[str, bool]:
        """检查API兼容性"""
        compatibility = {
            "controller_available": False,
            "config_manager_available": False,
            "logger_available": False,
            "trader_interface_available": False
        }
        
        try:
            # 检查控制器
            controller = get_controller()
            compatibility["controller_available"] = controller is not None
        except:
            pass
        
        try:
            # 检查配置管理器
            config_manager = get_config_manager()
            compatibility["config_manager_available"] = config_manager is not None
        except:
            pass
        
        try:
            # 检查日志器
            logger_test = get_logger(__name__)
            compatibility["logger_available"] = logger_test is not None
        except:
            pass
        
        # 检查trader接口
        try:
            from app.interfaces.trader_interface import ITrader
            compatibility["trader_interface_available"] = True
        except:
            pass
        
        return compatibility


def demonstrate_api_usage():
    """演示API使用"""
    # print("=== MT5 API适配器演示 ===")
    
    # 检查兼容性
    compatibility = APICompatibilityLayer.check_api_compatibility()
    # print(f"兼容性检查: {compatibility}")
    
    # 创建API适配器
    adapter = create_api_adapter()
    
    # 启用API配置
    if adapter.enable_api_in_config():
        pass
        # print("✓ API已在配置中启用")
    
    # 启动API服务器
    if adapter.start_api_server():
        # print("✓ API服务器启动成功")
        
        # 获取状态
        status = adapter.get_api_status()
        # print(f"服务器状态: {status}")
        
        # 获取端点
        endpoints = adapter.get_api_endpoints()
        # print(f"可用端点: {len(endpoints['endpoints'])}个")
        
        # 停止服务器
        adapter.stop_api_server()
        # print("✓ API服务器已停止")
    else:
        print("✗ API服务器启动失败")
    
    # 清理
    adapter.cleanup()
    # print("✓ 清理完成")


if __name__ == "__main__":
    demonstrate_api_usage()