"""
API服务器

提供HTTP服务器功能，处理REST API请求
"""

import json
import threading
import socket
import logging
logger = logging.getLogger(__name__)
from typing import Dict, Any, Optional, Callable
from urllib.parse import urlparse, parse_qs
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime

from app.utils.logger import get_logger
from app.api.routes import APIRoutes
from app.api.models import APIResponse

logger = get_logger(__name__)


class MT5APIHandler(BaseHTTPRequestHandler):
    """HTTP请求处理器"""
    
    def __init__(self, *args, api_routes: APIRoutes = None, **kwargs):
        self.api_routes = api_routes or APIRoutes()
        super().__init__(*args, **kwargs)
    
    def _send_response(self, response: APIResponse, status_code: int = 200):
        """发送HTTP响应"""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-API-Key')
        self.end_headers()
        
        response_data = response.to_json().encode('utf-8')
        self.wfile.write(response_data)
    
    def _parse_request(self) -> tuple[str, Dict[str, str], str, Dict[str, str]]:
        """解析HTTP请求"""
        # 解析URL
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        query_params = {}
        
        if parsed_url.query:
            query_params = {k: v[0] if v else '' for k, v in parse_qs(parsed_url.query).items()}
        
        # 获取请求头
        headers = {k.lower(): v for k, v in self.headers.items()}
        
        # 获取请求体
        body = ""
        if 'content-length' in headers:
            content_length = int(headers['content-length'])
            if content_length > 0:
                body = self.rfile.read(content_length).decode('utf-8')
        
        return path, headers, body, query_params
    
    def _handle_request(self, method: str):
        """处理HTTP请求"""
        try:
            path, headers, body, query_params = self._parse_request()
            
            logger.info("[空日志]", "[空日志]", f"API Request: {method} {path}")
            
            # 处理请求
            response = self.api_routes.handle_request(method, path, headers, body, query_params)
            
            # 确定状态码
            status_code = 200 if response.success else 400
            if response.error_code in ['ROUTE_NOT_FOUND']:
                status_code = 404
            elif response.error_code in ['METHOD_NOT_ALLOWED']:
                status_code = 405
            elif response.error_code in ['INTERNAL_ERROR']:
                status_code = 500
            
            self._send_response(response, status_code)
            
        except Exception as e:
            logger.error("[空日志]", f"Request handling error: {e}")
            error_response = APIResponse(
                success=False,
                message=f"Server error: {str(e)}",
                error_code="SERVER_ERROR"
            )
            self._send_response(error_response, 500)
    
    def do_GET(self):
        """处理GET请求"""
        self._handle_request('GET')
    
    def do_POST(self):
        """处理POST请求"""
        self._handle_request('POST')
    
    def do_PUT(self):
        """处理PUT请求"""
        self._handle_request('PUT')
    
    def do_DELETE(self):
        """处理DELETE请求"""
        self._handle_request('DELETE')
    
    def do_OPTIONS(self):
        """处理OPTIONS请求（CORS预检）"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-API-Key')
        self.end_headers()
    
    def log_message(self, format, *args):
        """自定义日志输出"""
        logger.info("[空日志]", "[空日志]", f"HTTP: {format % args}")


class MT5APIServer:
    """MT5 API服务器"""
    
    def __init__(self, host: str = 'localhost', port: int = 8080):
        self.host = host
        self.port = port
        self.server: Optional[HTTPServer] = None
        self.server_thread: Optional[threading.Thread] = None
        self.api_routes = APIRoutes()
        self._running = False
    
    def _create_handler_class(self):
        """创建请求处理器类"""
        api_routes = self.api_routes
        
        class Handler(MT5APIHandler):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, api_routes=api_routes, **kwargs)
        
        return Handler
    
    def start(self) -> bool:
        """启动API服务器"""
        try:
            if self._running:
                logger.warning("[空日志]", "API server is already running")
                return True
            
            # 检查端口是否可用
            if not self._is_port_available(self.host, self.port):
                logger.error("[空日志]", f"Port {self.port} is already in use")
                return False
            
            # 创建HTTP服务器
            handler_class = self._create_handler_class()
            self.server = HTTPServer((self.host, self.port), handler_class)
            
            # 在单独线程中启动服务器
            self.server_thread = threading.Thread(
                target=self._run_server,
                daemon=True,
                name="MT5-API-Server"
            )
            
            self.server_thread.start()
            self._running = True
            
            logger.info("[空日志]", "[空日志]", f"MT5 API Server started on http://{self.host}:{self.port}")
            logger.info("[空日志]", "[空日志]", "Available endpoints:")
            for route in self.api_routes.routes.keys():
                logger.info("[空日志]", "[空日志]", f"  {route}")
            
            return True
            
        except Exception as e:
            logger.error("[空日志]", f"Failed to start API server: {e}")
            return False
    
    def stop(self):
        """停止API服务器"""
        try:
            if not self._running:
                logger.warning("[空日志]", "API server is not running")
                return
            
            if self.server:
                logger.info("[空日志]", "[空日志]", "Stopping MT5 API Server...")
                self.server.shutdown()
                self.server.server_close()
            
            if self.server_thread and self.server_thread.is_alive():
                self.server_thread.join(timeout=5)
            
            self._running = False
            logger.info("[空日志]", "[空日志]", "MT5 API Server stopped")
            
        except Exception as e:
            logger.error("[空日志]", f"Error stopping API server: {e}")
    
    def _run_server(self):
        """运行服务器主循环"""
        try:
            self.server.serve_forever()
        except Exception as e:
            logger.error("[空日志]", f"Server error: {e}")
            self._running = False
    
    def _is_port_available(self, host: str, port: int) -> bool:
        """检查端口是否可用"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.bind((host, port))
                return True
        except OSError:
            return False
    
    def is_running(self) -> bool:
        """检查服务器是否正在运行"""
        return self._running and self.server_thread and self.server_thread.is_alive()
    
    def get_status(self) -> Dict[str, Any]:
        """获取服务器状态"""
        return {
            "running": self.is_running(),
            "host": self.host,
            "port": self.port,
            "url": f"http://{self.host}:{self.port}",
            "start_time": datetime.now().isoformat(),
            "routes_count": len(self.api_routes.routes)
        }


# 全局API服务器实例
_api_server: Optional[MT5APIServer] = None
_server_lock = threading.Lock()


def create_api_server(host: str = 'localhost', port: int = 8080) -> MT5APIServer:
    """创建API服务器实例"""
    return MT5APIServer(host, port)


def get_api_server() -> Optional[MT5APIServer]:
    """获取全局API服务器实例"""
    global _api_server
    return _api_server


def start_api_server(host: str = 'localhost', port: int = 8080) -> bool:
    """启动全局API服务器"""
    global _api_server
    
    with _server_lock:
        if _api_server and _api_server.is_running():
            logger.warning("[空日志]", "API server is already running")
            return True
        
        _api_server = create_api_server(host, port)
        return _api_server.start()


def stop_api_server():
    """停止全局API服务器"""
    global _api_server
    
    with _server_lock:
        if _api_server:
            _api_server.stop()
            _api_server = None


def is_api_server_running() -> bool:
    """检查API服务器是否正在运行"""
    return _api_server is not None and _api_server.is_running()


class APIServerManager:
    """API服务器管理器"""
    
    @staticmethod
    def start_with_config(config: Dict[str, Any]) -> bool:
        """使用配置启动服务器"""
        host = config.get('api_host', 'localhost')
        port = config.get('api_port', 8080)
        enabled = config.get('api_enabled', False)
        
        if not enabled:
            logger.info("[空日志]", "[空日志]", "API server is disabled in configuration")
            return False
        
        return start_api_server(host, port)
    
    @staticmethod
    def get_server_info() -> Dict[str, Any]:
        """获取服务器信息"""
        server = get_api_server()
        if server:
            return server.get_status()
        else:
            return {
                "running": False,
                "message": "API server not initialized"
            }
    
    @staticmethod
    def restart_server(host: str = 'localhost', port: int = 8080) -> bool:
        """重启服务器"""
        stop_api_server()
        return start_api_server(host, port)


def example_usage():
    """示例用法"""
    # 启动API服务器
    if start_api_server('localhost', 8080):
        pass
        # print("API服务器启动成功")
        # print("访问 http://localhost:8080/api/v1/status 查看状态")
        # print("访问 http://localhost:8080/api/v1/connection 查看连接状态")
        
        # 服务器将在后台运行
        # 要停止服务器，调用：
        # stop_api_server()
    else:
        logger.error("[空日志]", "API服务器启动失败")


if __name__ == "__main__":
    example_usage()