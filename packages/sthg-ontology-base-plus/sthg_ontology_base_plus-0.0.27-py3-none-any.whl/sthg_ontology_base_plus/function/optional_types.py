from typing import Any, Dict, Optional as OptionalType, Generic, TypeVar
from .base import PalantirType, ValidationError, safe_json_serialize

T = TypeVar('T')


class Optional(PalantirType[OptionalType[Any]], Generic[T]):
    """可选类型，表示可能为空的值"""
    
    def __init__(self, value: OptionalType[T] = None, inner_type: OptionalType[type] = None):
        self.inner_type = inner_type
        super().__init__(value)
    
    def _validate(self, value: Any) -> OptionalType[T]:
        if value is None:
            return None
        
        # 如果指定了内部类型，验证值是否匹配
        if self.inner_type is not None:
            if isinstance(self.inner_type, type) and issubclass(self.inner_type, PalantirType):
                # 如果是Palantir类型，使用其验证
                inner_instance = self.inner_type(value)
                return inner_instance.value
            elif hasattr(self.inner_type, '__call__'):
                # 如果是可调用类型（如int, str等），尝试转换
                try:
                    return self.inner_type(value)
                except (ValueError, TypeError):
                    raise ValidationError(f"Cannot convert {value} to {self.inner_type.__name__}")
        
        return value
    
    @property
    def is_none(self) -> bool:
        """检查值是否为None"""
        return self._value is None
    
    @property
    def has_value(self) -> bool:
        """检查是否有值"""
        return self._value is not None
    
    def get_value(self, default: T = None) -> OptionalType[T]:
        """获取值，如果为None则返回默认值"""
        return self._value if self._value is not None else default
    
    def or_else(self, default: T) -> T:
        """获取值，如果为None则返回指定的默认值"""
        return self._value if self._value is not None else default
    
    def map(self, func) -> 'Optional':
        """如果有值，应用函数并返回新的Optional，否则返回None的Optional"""
        if self._value is not None:
            try:
                return Optional(func(self._value))
            except Exception as e:
                raise ValidationError(f"Error in map function: {e}")
        return Optional(None)
    
    def filter(self, predicate) -> 'Optional':
        """如果有值且满足条件，返回当前Optional，否则返回None的Optional"""
        if self._value is not None and predicate(self._value):
            return self
        return Optional(None)
    
    def to_json(self) -> Dict[str, Any]:
        return {
            "type": "Optional",
            "value": safe_json_serialize(self._value) if self._value is not None else None,
            "innerType": self.inner_type.__name__ if self.inner_type else None
        }
    
    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> 'Optional':
        value = data.get("value")
        inner_type_name = data.get("innerType")
        
        # 尝试重建内部类型
        inner_type = None
        if inner_type_name:
            # 简单的类型映射
            type_map = {
                'int': int,
                'str': str,
                'float': float,
                'bool': bool
            }
            inner_type = type_map.get(inner_type_name)
        
        return cls(value, inner_type)
    
    @classmethod
    def type_name(cls) -> str:
        return "Optional"
    
    def __str__(self) -> str:
        if self._value is None:
            return "Optional(None)"
        else:
            return f"Optional({repr(self._value)})"
    
    def __bool__(self) -> bool:
        return self._value is not None