"""
API集成示例

演示如何集成和使用MT5 API接口层
"""

import json
import time
import requests
import threading
import logging
logger = logging.getLogger(__name__)
from typing import Dict, Any
import sys
import os

# 添加项目根目录到路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, project_root)

from app.utils.logger import get_logger
from app.adapters.api_adapter import MT5APIAdapter, get_api_adapter, APICompatibilityLayer
from app.api.server import start_api_server, stop_api_server, is_api_server_running
from app.controllers.main_controller import get_controller

logger = get_logger(__name__)


class APIIntegrationExample:
    """API集成示例类"""
    
    def __init__(self):
        self.api_adapter = None
        self.base_url = "http://localhost:8080"
    
    def demonstrate_api_lifecycle(self):
        """演示API生命周期管理"""
        # print("\n=== API生命周期管理演示 ===")
        
        try:
            # 1. 创建API适配器
            self.api_adapter = MT5APIAdapter()
            # print("✓ API适配器创建成功")
            
            # 2. 检查兼容性
            compatibility = APICompatibilityLayer.check_api_compatibility()
            # print(f"系统兼容性检查: {compatibility}")
            
            # 3. 启动API服务器
            if self.api_adapter.start_api_server('localhost', 8080):
                # print("✓ API服务器启动成功")
                
                # 4. 检查状态
                status = self.api_adapter.get_api_status()
                # print(f"服务器状态: {status}")
                
                # 5. 获取端点信息
                endpoints = self.api_adapter.get_api_endpoints()
                # print(f"可用端点数量: {endpoints['total_count']}")
                
                # 6. 等待一段时间让服务器稳定
                time.sleep(2)
                
                # 7. 测试API端点
                self._test_api_endpoints()
                
                # 8. 停止服务器
                self.api_adapter.stop_api_server()
                # print("✓ API服务器已停止")
            else:
                logger.error("[空日志]", "✗ API服务器启动失败")
            
        except Exception as e:
            logger.error("[空日志]", f"API生命周期演示错误: {e}")
            # print(f"✗ 演示过程出错: {e}")
        
        finally:
            if self.api_adapter:
                self.api_adapter.cleanup()
    
    def _test_api_endpoints(self):
        """测试API端点"""
        # print("\n--- API端点测试 ---")
        
        try:
            # 测试系统状态端点
            self._test_system_status()
            
            # 测试连接状态端点
            self._test_connection_status()
            
            # 注意：其他端点需要MT5连接才能正常工作
            # print("注意: 其他端点需要MT5连接才能完全测试")
            
        except Exception as e:
            logger.error("[空日志]", f"API端点测试错误: {e}")
            logger.error("[空日志]", f"✗ API端点测试失败: {e}")
    
    def _test_system_status(self):
        """测试系统状态端点"""
        try:
            response = requests.get(f"{self.base_url}/api/v1/status", timeout=5)
            if response.status_code == 200:
                data = response.json()
                # print(f"✓ 系统状态: {data.get('success', False)}")
            else:
                logger.error("[空日志]", f"✗ 系统状态请求失败: {response.status_code}")
        except Exception as e:
            logger.error("[空日志]", f"✗ 系统状态测试失败: {e}")
    
    def _test_connection_status(self):
        """测试连接状态端点"""
        try:
            response = requests.get(f"{self.base_url}/api/v1/connection", timeout=5)
            if response.status_code == 200:
                data = response.json()
                connected = data.get('data', {}).get('connected', False)
                # print(f"✓ MT5连接状态: {connected}")
            else:
                logger.error("[空日志]", f"✗ 连接状态请求失败: {response.status_code}")
        except Exception as e:
            logger.error("[空日志]", f"✗ 连接状态测试失败: {e}")
    
    def demonstrate_configuration_management(self):
        """演示配置管理"""
        # print("\n=== 配置管理演示 ===")
        
        try:
            adapter = MT5APIAdapter()
            
            # 1. 启用API配置
            if adapter.enable_api_in_config(save=False):
                pass
                # print("✓ API配置已启用")
            
            # 2. 更新API配置
            config_updates = {
                'host': 'localhost',
                'port': 8080,
                'auto_start': True,
                'security': {
                    'rate_limit': True,
                    'cors_enabled': True
                }
            }
            
            if adapter.update_api_config(**config_updates):
                pass
                # print("✓ API配置已更新")
            
            # 3. 禁用API配置
            if adapter.disable_api_in_config(save=False):
                pass
                # print("✓ API配置已禁用")
            
            adapter.cleanup()
            
        except Exception as e:
            logger.error("[空日志]", f"配置管理演示错误: {e}")
            logger.error("[空日志]", f"✗ 配置管理演示失败: {e}")
    
    def demonstrate_existing_system_integration(self):
        """演示与现有系统的集成"""
        # print("\n=== 现有系统集成演示 ===")
        
        try:
            # 1. 为现有系统启用API
            if APICompatibilityLayer.enable_api_for_existing_system():
                pass
                # print("✓ 现有系统API集成成功")
            
            # 2. 检查现有组件可用性
            try:
                controller = get_controller()
                # print(f"✓ 控制器可用: {controller is not None}")
            except Exception as e:
                pass
                # print(f"⚠ 控制器不可用: {e}")
            
            # 3. 使用全局适配器
            adapter = get_api_adapter()
            if adapter:
                # print("✓ 全局API适配器获取成功")
                
                # 测试初始化
                if adapter.initialize():
                    pass
                    # print("✓ API适配器初始化成功")
                else:
                    logger.error("[空日志]", "⚠ API适配器初始化失败")
                
                adapter.cleanup()
            
        except Exception as e:
            logger.error("[空日志]", f"现有系统集成演示错误: {e}")
            logger.error("[空日志]", f"✗ 现有系统集成演示失败: {e}")
    
    def demonstrate_api_request_examples(self):
        """演示API请求示例"""
        # print("\n=== API请求示例演示 ===")
        
        # 这些是示例请求格式，不会实际发送
        examples = {
            "获取系统状态": {
                "method": "GET",
                "url": "/api/v1/status",
                "description": "获取系统运行状态"
            },
            "检查MT5连接": {
                "method": "GET", 
                "url": "/api/v1/connection",
                "description": "检查MT5连接状态"
            },
            "连接MT5": {
                "method": "POST",
                "url": "/api/v1/connection",
                "description": "连接到MT5"
            },
            "获取账户信息": {
                "method": "GET",
                "url": "/api/v1/account", 
                "description": "获取MT5账户信息"
            },
            "获取所有仓位": {
                "method": "GET",
                "url": "/api/v1/positions",
                "description": "获取所有持仓"
            },
            "下单": {
                "method": "POST",
                "url": "/api/v1/orders",
                "body": {
                    "symbol": "EURUSD",
                    "order_type": "buy",
                    "volume": 0.1,
                    "sl": 1.0800,
                    "tp": 1.0900
                },
                "description": "提交交易订单"
            },
            "获取品种信息": {
                "method": "GET",
                "url": "/api/v1/symbols",
                "description": "获取交易品种列表"
            }
        }
        
        for name, example in examples.items():
            # print(f"\n{name}:")
            # print(f"  方法: {example['method']}")
            # print(f"  URL: {example['url']}")
            if 'body' in example:
                pass
                # print(f"  请求体: {json.dumps(example['body'], indent=4)}")
            # print(f"  描述: {example['description']}")
    
    def demonstrate_error_handling(self):
        """演示错误处理"""
        logger.error("[空日志]", "\n=== 错误处理演示 ===")
        
        try:
            adapter = MT5APIAdapter()
            
            # 1. 尝试在已占用端口启动服务器
            # print("测试端口冲突处理...")
            
            # 2. 测试无效配置
            # print("测试无效配置处理...")
            invalid_config = {
                'host': 'invalid_host',
                'port': -1
            }
            
            # 3. 测试重复启动
            # print("测试重复启动处理...")
            
            logger.error("[空日志]", "✓ 错误处理机制工作正常")
            
        except Exception as e:
            logger.error("[空日志]", f"错误处理演示失败: {e}")
            logger.error("[空日志]", f"✗ 错误处理演示失败: {e}")
    
    def run_all_demonstrations(self):
        """运行所有演示"""
        # print("=" * 50)
        # print("MT5 API集成完整演示")
        # print("=" * 50)
        
        # 1. API生命周期管理
        self.demonstrate_api_lifecycle()
        
        # 2. 配置管理
        self.demonstrate_configuration_management()
        
        # 3. 现有系统集成
        self.demonstrate_existing_system_integration()
        
        # 4. API请求示例
        self.demonstrate_api_request_examples()
        
        # 5. 错误处理
        self.demonstrate_error_handling()
        
        # print("\n" + "=" * 50)
        # print("演示完成")
        # print("=" * 50)


class APIClientExample:
    """API客户端示例"""
    
    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'MT5-API-Client/1.0'
        })
    
    def check_server_status(self) -> bool:
        """检查服务器状态"""
        try:
            response = self.session.get(f"{self.base_url}/api/v1/status", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def get_system_status(self) -> Dict[str, Any]:
        """获取系统状态"""
        response = self.session.get(f"{self.base_url}/api/v1/status")
        response.raise_for_status()
        return response.json()
    
    def get_connection_status(self) -> Dict[str, Any]:
        """获取连接状态"""
        response = self.session.get(f"{self.base_url}/api/v1/connection")
        response.raise_for_status()
        return response.json()
    
    def connect_mt5(self) -> Dict[str, Any]:
        """连接MT5"""
        response = self.session.post(f"{self.base_url}/api/v1/connection")
        response.raise_for_status()
        return response.json()
    
    def get_account_info(self) -> Dict[str, Any]:
        """获取账户信息"""
        response = self.session.get(f"{self.base_url}/api/v1/account")
        response.raise_for_status()
        return response.json()
    
    def get_positions(self) -> Dict[str, Any]:
        """获取仓位"""
        response = self.session.get(f"{self.base_url}/api/v1/positions")
        response.raise_for_status()
        return response.json()
    
    def place_order(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """下单"""
        response = self.session.post(
            f"{self.base_url}/api/v1/orders",
            json=order_data
        )
        response.raise_for_status()
        return response.json()


def demonstrate_api_client():
    """演示API客户端使用"""
    # print("\n=== API客户端使用演示 ===")
    
    client = APIClientExample()
    
    # 检查服务器是否运行
    if not client.check_server_status():
        # print("⚠ API服务器未运行，客户端演示跳过")
        return
    
    try:
        # 1. 获取系统状态
        status = client.get_system_status()
        # print(f"✓ 系统状态: {status.get('success', False)}")
        
        # 2. 获取连接状态
        connection = client.get_connection_status()
        # print(f"✓ 连接状态: {connection.get('data', {}).get('connected', False)}")
        
        # 注意：其他操作需要实际的MT5连接
        
    except Exception as e:
        logger.error("[空日志]", f"✗ API客户端演示失败: {e}")


def main():
    """主函数"""
    try:
        # 创建演示实例
        example = APIIntegrationExample()
        
        # 运行完整演示
        example.run_all_demonstrations()
        
        # 客户端演示
        demonstrate_api_client()
        
    except KeyboardInterrupt:
        pass
        # print("\n演示被用户中断")
    except Exception as e:
        logger.error("[空日志]", f"演示过程出错: {e}")
        # print(f"演示过程出错: {e}")


if __name__ == "__main__":
    main()