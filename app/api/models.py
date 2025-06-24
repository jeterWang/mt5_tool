"""
API模型定义

定义API请求和响应的数据模型
"""

from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any, List, Union
from datetime import datetime
import json


@dataclass
class APIResponse:
    """标准API响应格式"""
    success: bool
    data: Optional[Any] = None
    message: str = ""
    error_code: Optional[str] = None
    timestamp: str = ""
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return asdict(self)
    
    def to_json(self) -> str:
        """转换为JSON字符串"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)


@dataclass
class OrderRequest:
    """下单请求模型"""
    symbol: str
    order_type: str  # 'buy' or 'sell'
    volume: float
    price: Optional[float] = None
    sl: Optional[float] = None  # 止损
    tp: Optional[float] = None  # 止盈
    deviation: Optional[int] = 20
    comment: Optional[str] = ""
    
    def validate(self) -> bool:
        """验证请求参数"""
        if not self.symbol or not isinstance(self.symbol, str):
            return False
        if self.order_type not in ['buy', 'sell']:
            return False
        if not isinstance(self.volume, (int, float)) or self.volume <= 0:
            return False
        return True


@dataclass
class PositionRequest:
    """仓位查询请求模型"""
    symbol: Optional[str] = None
    position_type: Optional[str] = None  # 'buy' or 'sell'
    ticket: Optional[int] = None


@dataclass
class ModifyPositionRequest:
    """修改仓位请求模型"""
    ticket: int
    sl: Optional[float] = None
    tp: Optional[float] = None
    
    def validate(self) -> bool:
        """验证请求参数"""
        if not isinstance(self.ticket, int) or self.ticket <= 0:
            return False
        if self.sl is None and self.tp is None:
            return False
        return True


@dataclass
class ClosePositionRequest:
    """平仓请求模型"""
    ticket: int
    volume: Optional[float] = None  # 部分平仓数量，None表示全部平仓
    deviation: Optional[int] = 20
    
    def validate(self) -> bool:
        """验证请求参数"""
        if not isinstance(self.ticket, int) or self.ticket <= 0:
            return False
        if self.volume is not None and (not isinstance(self.volume, (int, float)) or self.volume <= 0):
            return False
        return True


@dataclass
class SymbolRequest:
    """品种查询请求模型"""
    symbol: Optional[str] = None
    group: Optional[str] = None  # 品种组


@dataclass
class AccountInfoResponse:
    """账户信息响应模型"""
    login: int
    balance: float
    equity: float
    margin: float
    free_margin: float
    margin_level: float
    profit: float
    currency: str
    leverage: int
    
    @classmethod
    def from_account_info(cls, account_info) -> 'AccountInfoResponse':
        """从MT5账户信息创建响应模型"""
        return cls(
            login=account_info.login,
            balance=account_info.balance,
            equity=account_info.equity,
            margin=account_info.margin,
            free_margin=account_info.free_margin,
            margin_level=account_info.margin_level,
            profit=account_info.profit,
            currency=account_info.currency,
            leverage=account_info.leverage
        )


@dataclass
class PositionResponse:
    """仓位信息响应模型"""
    ticket: int
    symbol: str
    type: int
    type_name: str
    volume: float
    price_open: float
    price_current: float
    sl: float
    tp: float
    profit: float
    swap: float
    comment: str
    time: str
    
    @classmethod
    def from_position(cls, position) -> 'PositionResponse':
        """从MT5仓位信息创建响应模型"""
        return cls(
            ticket=position.ticket,
            symbol=position.symbol,
            type=position.type,
            type_name='buy' if position.type == 0 else 'sell',
            volume=position.volume,
            price_open=position.price_open,
            price_current=position.price_current,
            sl=position.sl,
            tp=position.tp,
            profit=position.profit,
            swap=position.swap,
            comment=position.comment,
            time=datetime.fromtimestamp(position.time).isoformat()
        )


@dataclass
class SymbolResponse:
    """品种信息响应模型"""
    name: str
    bid: float
    ask: float
    spread: int
    digits: int
    point: float
    trade_mode: int
    volume_min: float
    volume_max: float
    volume_step: float
    margin_initial: float
    
    @classmethod
    def from_symbol_info(cls, symbol_info) -> 'SymbolResponse':
        """从MT5品种信息创建响应模型"""
        return cls(
            name=symbol_info.name,
            bid=symbol_info.bid,
            ask=symbol_info.ask,
            spread=symbol_info.spread,
            digits=symbol_info.digits,
            point=symbol_info.point,
            trade_mode=symbol_info.trade_mode,
            volume_min=symbol_info.volume_min,
            volume_max=symbol_info.volume_max,
            volume_step=symbol_info.volume_step,
            margin_initial=symbol_info.margin_initial
        )


@dataclass
class OrderResult:
    """下单结果模型"""
    retcode: int
    deal: int
    order: int
    volume: float
    price: float
    comment: str
    request_id: int
    
    @classmethod
    def from_order_result(cls, result) -> 'OrderResult':
        """从MT5下单结果创建响应模型"""
        return cls(
            retcode=result.retcode,
            deal=result.deal,
            order=result.order,
            volume=result.volume,
            price=result.price,
            comment=result.comment,
            request_id=result.request_id
        )


class ModelConverter:
    """模型转换器"""
    
    @staticmethod
    def request_to_dict(request_data: str) -> Dict[str, Any]:
        """将JSON请求转换为字典"""
        try:
            return json.loads(request_data)
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON format")
    
    @staticmethod
    def dict_to_model(data: Dict[str, Any], model_class):
        """将字典转换为模型对象"""
        try:
            return model_class(**data)
        except TypeError as e:
            raise ValueError(f"Invalid data format for {model_class.__name__}: {e}")
    
    @staticmethod
    def model_to_response(data: Any, success: bool = True, message: str = "") -> APIResponse:
        """将模型对象转换为API响应"""
        return APIResponse(
            success=success,
            data=asdict(data) if hasattr(data, '__dict__') else data,
            message=message
        )
    
    @staticmethod
    def error_to_response(error: Exception, error_code: str = "ERROR") -> APIResponse:
        """将错误转换为API响应"""
        return APIResponse(
            success=False,
            message=str(error),
            error_code=error_code
        )