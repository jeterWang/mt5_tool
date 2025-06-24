"""
MT5交易系统API层模块

提供RESTful API接口访问MT5交易功能
"""

__all__ = [
    # 服务器
    'MT5APIServer',
    'create_api_server', 
    'start_api_server',
    'stop_api_server',
    'is_api_server_running',
    'APIServerManager',
    
    # 路由
    'APIRoutes',
    
    # 模型
    'APIResponse',
    'OrderRequest',
    'PositionRequest', 
    'ModifyPositionRequest',
    'ClosePositionRequest',
    'SymbolRequest',
    'AccountInfoResponse',
    'PositionResponse',
    'SymbolResponse', 
    'OrderResult',
    'ModelConverter',
    
    # 验证器
    'RequestValidator',
    'SecurityValidator',
    'ValidationError',
    'validate_request',
    
    # 适配器
    'MT5APIAdapter',
    'get_api_adapter',
    'initialize_api_adapter',
    'APICompatibilityLayer'
]

__version__ = '1.0.0'