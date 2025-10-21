from abc import ABC, abstractmethod
from typing import Any, Dict, Type, TypeVar, Generic, Optional, Union
import json
from datetime import datetime, date
from decimal import Decimal

T = TypeVar('T')

class PalantirType(ABC, Generic[T]):
    """Palantir类型系统的抽象基类"""
    
    def __init__(self, value: T = None):
        if value is not None:
            self._value = self._validate(value)
        else:
            self._value = None
    
    @property
    def value(self) -> T:
        return self._value
    
    @value.setter 
    def value(self, val: T):
        self._value = self._validate(val)
    
    @abstractmethod
    def _validate(self, value: Any) -> T:
        """验证并转换值"""
        pass
    
    @abstractmethod
    def to_json(self) -> Dict[str, Any]:
        """序列化为JSON格式"""
        pass
    
    @classmethod
    @abstractmethod
    def from_json(cls, data: Dict[str, Any]) -> 'PalantirType[T]':
        """从JSON格式反序列化"""
        pass
    
    @classmethod
    @abstractmethod
    def type_name(cls) -> str:
        """获取类型名称"""
        pass
    
    def __str__(self) -> str:
        return str(self._value)
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._value!r})"
    
    def __eq__(self, other) -> bool:
        if isinstance(other, PalantirType):
            return self._value == other._value
        return self._value == other


class ValidationError(Exception):
    """类型验证异常"""
    pass


def validate_type(value: Any, expected_type: Type, allow_none: bool = False) -> Any:
    """通用类型验证函数"""
    if allow_none and value is None:
        return None
        
    if not isinstance(value, expected_type):
        raise ValidationError(f"Expected {expected_type.__name__}, got {type(value).__name__}")
    
    return value


def safe_json_serialize(obj: Any) -> Any:
    """安全的JSON序列化"""
    if obj is None:
        return None
    elif isinstance(obj, (str, int, float, bool)):
        return obj
    elif isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, date):
        return obj.isoformat()
    elif isinstance(obj, Decimal):
        return float(obj)
    elif isinstance(obj, (list, tuple)):
        return [safe_json_serialize(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: safe_json_serialize(value) for key, value in obj.items()}
    elif hasattr(obj, 'to_json'):
        return obj.to_json()
    else:
        return str(obj)