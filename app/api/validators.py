"""
API请求验证器

提供HTTP请求验证和参数校验功能
"""

from typing import Dict, Any, Optional, List, Union
import re
from datetime import datetime

from app.utils.logger import get_logger

logger = get_logger(__name__)


class ValidationError(Exception):
    """验证错误异常"""
    pass


class RequestValidator:
    """请求验证器"""
    
    # 支持的交易品种模式
    SYMBOL_PATTERNS = [
        r'^[A-Z]{6}$',  # 外汇对，如EURUSD
        r'^[A-Z]{3}USD$',  # 加密货币，如BTCUSD
        r'^[A-Z]+\d*$',  # 其他品种
    ]
    
    # 支持的订单类型
    ORDER_TYPES = ['buy', 'sell', 'buy_limit', 'sell_limit', 'buy_stop', 'sell_stop']
    
    # 支持的仓位类型
    POSITION_TYPES = ['buy', 'sell']
    
    @classmethod
    def validate_symbol(cls, symbol: str) -> bool:
        """验证交易品种"""
        if not symbol or not isinstance(symbol, str):
            return False
        
        symbol = symbol.upper().strip()
        return any(re.match(pattern, symbol) for pattern in cls.SYMBOL_PATTERNS)
    
    @classmethod
    def validate_order_type(cls, order_type: str) -> bool:
        """验证订单类型"""
        if not order_type or not isinstance(order_type, str):
            return False
        return order_type.lower() in cls.ORDER_TYPES
    
    @classmethod
    def validate_position_type(cls, position_type: str) -> bool:
        """验证仓位类型"""
        if not position_type or not isinstance(position_type, str):
            return False
        return position_type.lower() in cls.POSITION_TYPES
    
    @classmethod
    def validate_volume(cls, volume: Union[int, float], min_volume: float = 0.01, max_volume: float = 100.0) -> bool:
        """验证交易量"""
        if not isinstance(volume, (int, float)):
            return False
        return min_volume <= volume <= max_volume
    
    @classmethod
    def validate_price(cls, price: Union[int, float]) -> bool:
        """验证价格"""
        if not isinstance(price, (int, float)):
            return False
        return price > 0
    
    @classmethod
    def validate_ticket(cls, ticket: Union[int, str]) -> bool:
        """验证交易单号"""
        try:
            ticket_int = int(ticket)
            return ticket_int > 0
        except (ValueError, TypeError):
            return False
    
    @classmethod
    def validate_deviation(cls, deviation: Union[int, float]) -> bool:
        """验证滑点"""
        if not isinstance(deviation, (int, float)):
            return False
        return 0 <= deviation <= 100
    
    @classmethod
    def validate_order_request(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """验证下单请求"""
        errors = []
        
        # 验证必需字段
        required_fields = ['symbol', 'order_type', 'volume']
        for field in required_fields:
            if field not in data:
                errors.append(f"Missing required field: {field}")
        
        if errors:
            raise ValidationError(f"Validation errors: {'; '.join(errors)}")
        
        # 验证字段值
        if not cls.validate_symbol(data['symbol']):
            errors.append("Invalid symbol format")
        
        if not cls.validate_order_type(data['order_type']):
            errors.append(f"Invalid order type. Supported: {cls.ORDER_TYPES}")
        
        if not cls.validate_volume(data['volume']):
            errors.append("Invalid volume. Must be between 0.01 and 100.0")
        
        # 验证可选字段
        if 'price' in data and data['price'] is not None:
            if not cls.validate_price(data['price']):
                errors.append("Invalid price. Must be positive")
        
        if 'sl' in data and data['sl'] is not None:
            if not cls.validate_price(data['sl']):
                errors.append("Invalid stop loss. Must be positive")
        
        if 'tp' in data and data['tp'] is not None:
            if not cls.validate_price(data['tp']):
                errors.append("Invalid take profit. Must be positive")
        
        if 'deviation' in data and data['deviation'] is not None:
            if not cls.validate_deviation(data['deviation']):
                errors.append("Invalid deviation. Must be between 0 and 100")
        
        if errors:
            raise ValidationError(f"Validation errors: {'; '.join(errors)}")
        
        # 标准化数据
        result = data.copy()
        result['symbol'] = result['symbol'].upper().strip()
        result['order_type'] = result['order_type'].lower()
        
        return result
    
    @classmethod
    def validate_position_request(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """验证仓位查询请求"""
        errors = []
        result = data.copy()
        
        # 验证可选字段
        if 'symbol' in data and data['symbol'] is not None:
            if not cls.validate_symbol(data['symbol']):
                errors.append("Invalid symbol format")
            else:
                result['symbol'] = data['symbol'].upper().strip()
        
        if 'position_type' in data and data['position_type'] is not None:
            if not cls.validate_position_type(data['position_type']):
                errors.append(f"Invalid position type. Supported: {cls.POSITION_TYPES}")
            else:
                result['position_type'] = data['position_type'].lower()
        
        if 'ticket' in data and data['ticket'] is not None:
            if not cls.validate_ticket(data['ticket']):
                errors.append("Invalid ticket number")
            else:
                result['ticket'] = int(data['ticket'])
        
        if errors:
            raise ValidationError(f"Validation errors: {'; '.join(errors)}")
        
        return result
    
    @classmethod
    def validate_modify_position_request(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """验证修改仓位请求"""
        errors = []
        
        # 验证必需字段
        if 'ticket' not in data:
            errors.append("Missing required field: ticket")
        elif not cls.validate_ticket(data['ticket']):
            errors.append("Invalid ticket number")
        
        # 至少需要sl或tp之一
        if 'sl' not in data and 'tp' not in data:
            errors.append("At least one of 'sl' or 'tp' is required")
        
        # 验证sl和tp
        if 'sl' in data and data['sl'] is not None:
            if not cls.validate_price(data['sl']):
                errors.append("Invalid stop loss. Must be positive")
        
        if 'tp' in data and data['tp'] is not None:
            if not cls.validate_price(data['tp']):
                errors.append("Invalid take profit. Must be positive")
        
        if errors:
            raise ValidationError(f"Validation errors: {'; '.join(errors)}")
        
        result = data.copy()
        result['ticket'] = int(data['ticket'])
        
        return result
    
    @classmethod
    def validate_close_position_request(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """验证平仓请求"""
        errors = []
        
        # 验证必需字段
        if 'ticket' not in data:
            errors.append("Missing required field: ticket")
        elif not cls.validate_ticket(data['ticket']):
            errors.append("Invalid ticket number")
        
        # 验证可选字段
        if 'volume' in data and data['volume'] is not None:
            if not cls.validate_volume(data['volume']):
                errors.append("Invalid volume. Must be between 0.01 and 100.0")
        
        if 'deviation' in data and data['deviation'] is not None:
            if not cls.validate_deviation(data['deviation']):
                errors.append("Invalid deviation. Must be between 0 and 100")
        
        if errors:
            raise ValidationError(f"Validation errors: {'; '.join(errors)}")
        
        result = data.copy()
        result['ticket'] = int(data['ticket'])
        
        return result
    
    @classmethod
    def validate_symbol_request(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """验证品种查询请求"""
        errors = []
        result = data.copy()
        
        # 验证可选字段
        if 'symbol' in data and data['symbol'] is not None:
            if not cls.validate_symbol(data['symbol']):
                errors.append("Invalid symbol format")
            else:
                result['symbol'] = data['symbol'].upper().strip()
        
        if errors:
            raise ValidationError(f"Validation errors: {'; '.join(errors)}")
        
        return result


class SecurityValidator:
    """安全验证器"""
    
    # API密钥格式（示例）
    API_KEY_PATTERN = r'^[A-Za-z0-9]{32,64}$'
    
    # 请求频率限制（每分钟）
    RATE_LIMITS = {
        'default': 60,      # 默认限制
        'trading': 20,      # 交易操作限制
        'query': 120,       # 查询操作限制
    }
    
    @classmethod
    def validate_api_key(cls, api_key: str) -> bool:
        """验证API密钥格式"""
        if not api_key or not isinstance(api_key, str):
            return False
        return re.match(cls.API_KEY_PATTERN, api_key) is not None
    
    @classmethod
    def validate_request_source(cls, headers: Dict[str, str]) -> bool:
        """验证请求来源"""
        # 检查必要的请求头
        required_headers = ['user-agent', 'content-type']
        for header in required_headers:
            if header not in headers:
                logger.warning("[空日志]", f"Missing required header: {header}")
                return False
        
        # 检查Content-Type
        content_type = headers.get('content-type', '').lower()
        if 'application/json' not in content_type:
            logger.warning("[空日志]", f"Invalid content type: {content_type}")
            return False
        
        return True
    
    @classmethod
    def check_rate_limit(cls, client_id: str, operation_type: str = 'default') -> bool:
        """检查请求频率限制"""
        # 这里应该实现实际的频率限制逻辑
        # 简化版本，实际项目中需要使用Redis或内存存储
        return True
    
    @classmethod
    def sanitize_input(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """清理输入数据"""
        sanitized = {}
        
        for key, value in data.items():
            if isinstance(value, str):
                # 移除潜在的危险字符
                value = value.strip()
                # 简单的XSS防护
                dangerous_chars = ['<', '>', '"', "'", '&']
                for char in dangerous_chars:
                    value = value.replace(char, '')
            
            sanitized[key] = value
        
        return sanitized


def validate_request(request_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """通用请求验证函数"""
    try:
        # 安全清理
        data = SecurityValidator.sanitize_input(data)
        
        # 根据请求类型进行验证
        if request_type == 'order':
            return RequestValidator.validate_order_request(data)
        elif request_type == 'position':
            return RequestValidator.validate_position_request(data)
        elif request_type == 'modify_position':
            return RequestValidator.validate_modify_position_request(data)
        elif request_type == 'close_position':
            return RequestValidator.validate_close_position_request(data)
        elif request_type == 'symbol':
            return RequestValidator.validate_symbol_request(data)
        else:
            raise ValidationError(f"Unknown request type: {request_type}")
    
    except ValidationError:
        raise
    except Exception as e:
        logger.error("[空日志]", f"Validation error: {e}")
        raise ValidationError(f"Validation failed: {e}")