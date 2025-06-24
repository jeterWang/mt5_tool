"""
API路由处理器

提供RESTful API端点的路由处理功能
"""

import json
from typing import Dict, Any, Optional, Callable
from datetime import datetime
from urllib.parse import parse_qs, urlparse

from app.utils.logger import get_logger
from app.controllers.main_controller import get_controller
from app.api.models import (
    APIResponse, OrderRequest, PositionRequest, ModifyPositionRequest,
    ClosePositionRequest, SymbolRequest, AccountInfoResponse, 
    PositionResponse, SymbolResponse, OrderResult, ModelConverter
)
from app.api.validators import validate_request, ValidationError, SecurityValidator

logger = get_logger(__name__)


class APIRoutes:
    """API路由处理器"""
    
    def __init__(self):
        self.controller = get_controller()
        self.routes = self._setup_routes()
    
    def _setup_routes(self) -> Dict[str, Dict[str, Callable]]:
        """设置路由映射"""
        return {
            '/api/v1/connection': {
                'GET': self._get_connection_status,
                'POST': self._connect_mt5,
                'DELETE': self._disconnect_mt5
            },
            '/api/v1/account': {
                'GET': self._get_account_info
            },
            '/api/v1/positions': {
                'GET': self._get_positions,
                'POST': self._get_positions_filtered
            },
            '/api/v1/positions/{ticket}': {
                'GET': self._get_position,
                'PUT': self._modify_position,
                'DELETE': self._close_position
            },
            '/api/v1/orders': {
                'POST': self._place_order
            },
            '/api/v1/symbols': {
                'GET': self._get_symbols,
                'POST': self._get_symbols_filtered
            },
            '/api/v1/symbols/{symbol}': {
                'GET': self._get_symbol_info
            },
            '/api/v1/trading/sync': {
                'POST': self._sync_trades
            },
            '/api/v1/trading/pnl': {
                'GET': self._get_daily_pnl
            },
            '/api/v1/status': {
                'GET': self._get_system_status
            }
        }
    
    def handle_request(self, method: str, path: str, headers: Dict[str, str], 
                      body: str = "", query_params: Dict[str, str] = None) -> APIResponse:
        """处理HTTP请求"""
        try:
            # 安全验证
            if not SecurityValidator.validate_request_source(headers):
                return APIResponse(
                    success=False,
                    message="Invalid request source",
                    error_code="INVALID_SOURCE"
                )
            
            # 解析路径参数
            route_path, path_params = self._parse_path(path)
            
            # 查找路由处理器
            if route_path not in self.routes:
                return APIResponse(
                    success=False,
                    message=f"Route not found: {path}",
                    error_code="ROUTE_NOT_FOUND"
                )
            
            if method not in self.routes[route_path]:
                return APIResponse(
                    success=False,
                    message=f"Method {method} not allowed for {path}",
                    error_code="METHOD_NOT_ALLOWED"
                )
            
            # 调用处理器
            handler = self.routes[route_path][method]
            
            # 准备请求数据
            request_data = {}
            if body:
                try:
                    request_data = json.loads(body)
                except json.JSONDecodeError:
                    return APIResponse(
                        success=False,
                        message="Invalid JSON format",
                        error_code="INVALID_JSON"
                    )
            
            if query_params:
                request_data.update(query_params)
            
            if path_params:
                request_data.update(path_params)
            
            # 执行处理器
            return handler(request_data)
        
        except Exception as e:
            logger.error("[空日志]", f"API request handling error: {e}")
            return APIResponse(
                success=False,
                message=f"Internal server error: {str(e)}",
                error_code="INTERNAL_ERROR"
            )
    
    def _parse_path(self, path: str) -> tuple[str, Dict[str, str]]:
        """解析路径参数"""
        path_params = {}
        
        # 检查是否有路径参数
        for route_pattern in self.routes.keys():
            if '{' in route_pattern:
                pattern_parts = route_pattern.split('/')
                path_parts = path.split('/')
                
                if len(pattern_parts) == len(path_parts):
                    match = True
                    params = {}
                    
                    for i, (pattern_part, path_part) in enumerate(zip(pattern_parts, path_parts)):
                        if pattern_part.startswith('{') and pattern_part.endswith('}'):
                            param_name = pattern_part[1:-1]
                            params[param_name] = path_part
                        elif pattern_part != path_part:
                            match = False
                            break
                    
                    if match:
                        return route_pattern, params
        
        return path, path_params
    
    # 连接管理
    def _get_connection_status(self, data: Dict[str, Any]) -> APIResponse:
        """获取连接状态"""
        try:
            is_connected = self.controller.is_mt5_connected()
            return APIResponse(
                success=True,
                data={"connected": is_connected},
                message="Connection status retrieved"
            )
        except Exception as e:
            return ModelConverter.error_to_response(e, "CONNECTION_CHECK_ERROR")
    
    def _connect_mt5(self, data: Dict[str, Any]) -> APIResponse:
        """连接MT5"""
        try:
            result = self.controller.connect_mt5()
            return APIResponse(
                success=True,
                data={"connected": True},
                message="Connected to MT5 successfully"
            )
        except Exception as e:
            return ModelConverter.error_to_response(e, "CONNECTION_ERROR")
    
    def _disconnect_mt5(self, data: Dict[str, Any]) -> APIResponse:
        """断开MT5连接"""
        try:
            self.controller.disconnect_mt5()
            return APIResponse(
                success=True,
                data={"connected": False},
                message="Disconnected from MT5"
            )
        except Exception as e:
            return ModelConverter.error_to_response(e, "DISCONNECTION_ERROR")
    
    # 账户信息
    def _get_account_info(self, data: Dict[str, Any]) -> APIResponse:
        """获取账户信息"""
        try:
            account_info = self.controller.get_account_info()
            if account_info:
                response_data = AccountInfoResponse.from_account_info(account_info)
                return ModelConverter.model_to_response(response_data, True, "Account info retrieved")
            else:
                return APIResponse(
                    success=False,
                    message="Failed to get account info",
                    error_code="ACCOUNT_INFO_ERROR"
                )
        except Exception as e:
            return ModelConverter.error_to_response(e, "ACCOUNT_INFO_ERROR")
    
    # 仓位管理
    def _get_positions(self, data: Dict[str, Any]) -> APIResponse:
        """获取所有仓位"""
        try:
            positions = self.controller.get_all_positions()
            if positions is not None:
                response_data = [PositionResponse.from_position(pos) for pos in positions]
                return ModelConverter.model_to_response(response_data, True, "Positions retrieved")
            else:
                return APIResponse(
                    success=False,
                    message="Failed to get positions",
                    error_code="POSITIONS_ERROR"
                )
        except Exception as e:
            return ModelConverter.error_to_response(e, "POSITIONS_ERROR")
    
    def _get_positions_filtered(self, data: Dict[str, Any]) -> APIResponse:
        """获取过滤后的仓位"""
        try:
            validated_data = validate_request('position', data)
            
            if 'ticket' in validated_data:
                # 获取特定仓位
                position = self.controller.get_position(validated_data['ticket'])
                if position:
                    response_data = PositionResponse.from_position(position)
                    return ModelConverter.model_to_response([response_data], True, "Position retrieved")
                else:
                    return APIResponse(
                        success=False,
                        message=f"Position {validated_data['ticket']} not found",
                        error_code="POSITION_NOT_FOUND"
                    )
            else:
                # 获取所有仓位并过滤
                positions = self.controller.get_all_positions()
                if positions is not None:
                    filtered_positions = positions
                    
                    # 按品种过滤
                    if 'symbol' in validated_data:
                        filtered_positions = [p for p in filtered_positions if p.symbol == validated_data['symbol']]
                    
                    # 按类型过滤
                    if 'position_type' in validated_data:
                        pos_type = 0 if validated_data['position_type'] == 'buy' else 1
                        filtered_positions = [p for p in filtered_positions if p.type == pos_type]
                    
                    response_data = [PositionResponse.from_position(pos) for pos in filtered_positions]
                    return ModelConverter.model_to_response(response_data, True, "Filtered positions retrieved")
                else:
                    return APIResponse(
                        success=False,
                        message="Failed to get positions",
                        error_code="POSITIONS_ERROR"
                    )
        except ValidationError as e:
            return ModelConverter.error_to_response(e, "VALIDATION_ERROR")
        except Exception as e:
            return ModelConverter.error_to_response(e, "POSITIONS_FILTER_ERROR")
    
    def _get_position(self, data: Dict[str, Any]) -> APIResponse:
        """获取特定仓位"""
        try:
            if 'ticket' not in data:
                return APIResponse(
                    success=False,
                    message="Missing ticket parameter",
                    error_code="MISSING_TICKET"
                )
            
            ticket = int(data['ticket'])
            position = self.controller.get_position(ticket)
            
            if position:
                response_data = PositionResponse.from_position(position)
                return ModelConverter.model_to_response(response_data, True, "Position retrieved")
            else:
                return APIResponse(
                    success=False,
                    message=f"Position {ticket} not found",
                    error_code="POSITION_NOT_FOUND"
                )
        except Exception as e:
            return ModelConverter.error_to_response(e, "POSITION_ERROR")
    
    def _modify_position(self, data: Dict[str, Any]) -> APIResponse:
        """修改仓位"""
        try:
            validated_data = validate_request('modify_position', data)
            
            # 调用控制器修改仓位（需要在控制器中添加此方法）
            # 这里假设控制器有modify_position方法
            result = self._modify_position_implementation(validated_data)
            
            if result and result.get('retcode') == 10009:  # MT5成功代码
                return APIResponse(
                    success=True,
                    data=result,
                    message="Position modified successfully"
                )
            else:
                return APIResponse(
                    success=False,
                    message=f"Failed to modify position: {result.get('comment', 'Unknown error')}",
                    error_code="MODIFY_POSITION_ERROR"
                )
        except ValidationError as e:
            return ModelConverter.error_to_response(e, "VALIDATION_ERROR")
        except Exception as e:
            return ModelConverter.error_to_response(e, "MODIFY_POSITION_ERROR")
    
    def _close_position(self, data: Dict[str, Any]) -> APIResponse:
        """平仓"""
        try:
            validated_data = validate_request('close_position', data)
            
            # 调用控制器平仓（需要在控制器中添加此方法）
            result = self._close_position_implementation(validated_data)
            
            if result and result.get('retcode') == 10009:
                return APIResponse(
                    success=True,
                    data=result,
                    message="Position closed successfully"
                )
            else:
                return APIResponse(
                    success=False,
                    message=f"Failed to close position: {result.get('comment', 'Unknown error')}",
                    error_code="CLOSE_POSITION_ERROR"
                )
        except ValidationError as e:
            return ModelConverter.error_to_response(e, "VALIDATION_ERROR")
        except Exception as e:
            return ModelConverter.error_to_response(e, "CLOSE_POSITION_ERROR")
    
    # 订单管理
    def _place_order(self, data: Dict[str, Any]) -> APIResponse:
        """下单"""
        try:
            validated_data = validate_request('order', data)
            
            # 调用控制器下单（需要在控制器中添加此方法）
            result = self._place_order_implementation(validated_data)
            
            if result and result.get('retcode') == 10009:
                order_result = OrderResult.from_order_result(result)
                return ModelConverter.model_to_response(order_result, True, "Order placed successfully")
            else:
                return APIResponse(
                    success=False,
                    message=f"Failed to place order: {result.get('comment', 'Unknown error')}",
                    error_code="PLACE_ORDER_ERROR"
                )
        except ValidationError as e:
            return ModelConverter.error_to_response(e, "VALIDATION_ERROR")
        except Exception as e:
            return ModelConverter.error_to_response(e, "PLACE_ORDER_ERROR")
    
    # 品种信息
    def _get_symbols(self, data: Dict[str, Any]) -> APIResponse:
        """获取所有品种"""
        try:
            symbols = self.controller.get_all_symbols()
            if symbols is not None:
                return ModelConverter.model_to_response(symbols, True, "Symbols retrieved")
            else:
                return APIResponse(
                    success=False,
                    message="Failed to get symbols",
                    error_code="SYMBOLS_ERROR"
                )
        except Exception as e:
            return ModelConverter.error_to_response(e, "SYMBOLS_ERROR")
    
    def _get_symbols_filtered(self, data: Dict[str, Any]) -> APIResponse:
        """获取过滤后的品种"""
        try:
            validated_data = validate_request('symbol', data)
            
            # 这里可以添加品种过滤逻辑
            symbols = self.controller.get_all_symbols()
            if symbols is not None:
                filtered_symbols = symbols
                
                # 按名称过滤
                if 'symbol' in validated_data:
                    symbol_name = validated_data['symbol']
                    filtered_symbols = [s for s in filtered_symbols if symbol_name in s]
                
                return ModelConverter.model_to_response(filtered_symbols, True, "Filtered symbols retrieved")
            else:
                return APIResponse(
                    success=False,
                    message="Failed to get symbols",
                    error_code="SYMBOLS_ERROR"
                )
        except ValidationError as e:
            return ModelConverter.error_to_response(e, "VALIDATION_ERROR")
        except Exception as e:
            return ModelConverter.error_to_response(e, "SYMBOLS_FILTER_ERROR")
    
    def _get_symbol_info(self, data: Dict[str, Any]) -> APIResponse:
        """获取品种信息"""
        try:
            if 'symbol' not in data:
                return APIResponse(
                    success=False,
                    message="Missing symbol parameter",
                    error_code="MISSING_SYMBOL"
                )
            
            symbol = data['symbol'].upper()
            symbol_info = self.controller.get_symbol_params(symbol)
            
            if symbol_info:
                return ModelConverter.model_to_response(symbol_info, True, "Symbol info retrieved")
            else:
                return APIResponse(
                    success=False,
                    message=f"Symbol {symbol} not found",
                    error_code="SYMBOL_NOT_FOUND"
                )
        except Exception as e:
            return ModelConverter.error_to_response(e, "SYMBOL_INFO_ERROR")
    
    # 交易同步
    def _sync_trades(self, data: Dict[str, Any]) -> APIResponse:
        """同步交易数据"""
        try:
            self.controller.sync_closed_trades()
            return APIResponse(
                success=True,
                message="Trades synced successfully"
            )
        except Exception as e:
            return ModelConverter.error_to_response(e, "SYNC_ERROR")
    
    # PnL信息
    def _get_daily_pnl(self, data: Dict[str, Any]) -> APIResponse:
        """获取每日PnL"""
        try:
            pnl_info = self.controller.get_daily_pnl_info()
            return ModelConverter.model_to_response(pnl_info, True, "Daily PnL retrieved")
        except Exception as e:
            return ModelConverter.error_to_response(e, "PNL_ERROR")
    
    # 系统状态
    def _get_system_status(self, data: Dict[str, Any]) -> APIResponse:
        """获取系统状态"""
        try:
            status = {
                "timestamp": datetime.now().isoformat(),
                "mt5_connected": self.controller.is_mt5_connected(),
                "api_version": "1.0.0",
                "status": "running"
            }
            return ModelConverter.model_to_response(status, True, "System status retrieved")
        except Exception as e:
            return ModelConverter.error_to_response(e, "STATUS_ERROR")
    
    # 辅助实现方法（需要在实际项目中完整实现）
    def _modify_position_implementation(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """修改仓位的实际实现"""
        # 这里应该调用MT5的实际修改仓位API
        # 暂时返回模拟结果
        return {
            "retcode": 10009,
            "comment": "Position modified",
            "request_id": 1
        }
    
    def _close_position_implementation(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """平仓的实际实现"""
        # 这里应该调用MT5的实际平仓API
        # 暂时返回模拟结果
        return {
            "retcode": 10009,
            "comment": "Position closed",
            "request_id": 1
        }
    
    def _place_order_implementation(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """下单的实际实现"""
        # 这里应该调用MT5的实际下单API
        # 暂时返回模拟结果
        return {
            "retcode": 10009,
            "deal": 12345,
            "order": 67890,
            "volume": data['volume'],
            "price": data.get('price', 1.0),
            "comment": "Order placed via API",
            "request_id": 1
        }