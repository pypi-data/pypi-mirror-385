from typing import Any, Dict, List as PyList, Set as PySet, Optional, TypeVar, Type
from .base import PalantirType, ValidationError, safe_json_serialize

T = TypeVar('T')


class List(PalantirType[PyList[Any]]):
    """列表类型"""
    
    def __init__(self, items: PyList[Any] = None, item_type: Optional[Type[PalantirType]] = None):
        self.item_type = item_type
        super().__init__(items or [])
    
    def _validate(self, value: Any) -> PyList[Any]:
        if not isinstance(value, (list, tuple)):
            raise ValidationError(f"Expected list or tuple, got {type(value).__name__}")
        
        validated_items = []
        for item in value:
            if self.item_type and not isinstance(item, self.item_type):
                # 尝试转换为指定类型
                try:
                    if hasattr(self.item_type, '_validate'):
                        validated_item = self.item_type(item)
                    else:
                        validated_item = item
                except Exception:
                    raise ValidationError(f"Cannot convert {type(item).__name__} to {self.item_type.__name__}")
            else:
                validated_item = item
            validated_items.append(validated_item)
        
        return validated_items
    
    def append(self, item: Any):
        """添加元素到列表"""
        if self.item_type and not isinstance(item, self.item_type):
            try:
                item = self.item_type(item)
            except Exception:
                raise ValidationError(f"Cannot convert {type(item).__name__} to {self.item_type.__name__}")
        self._value.append(item)
    
    def extend(self, items: PyList[Any]):
        """扩展列表"""
        for item in items:
            self.append(item)
    
    def __len__(self) -> int:
        return len(self._value)
    
    def __getitem__(self, index: int) -> Any:
        return self._value[index]
    
    def __setitem__(self, index: int, value: Any):
        if self.item_type and not isinstance(value, self.item_type):
            try:
                value = self.item_type(value)
            except Exception:
                raise ValidationError(f"Cannot convert {type(value).__name__} to {self.item_type.__name__}")
        self._value[index] = value
    
    def to_json(self) -> Dict[str, Any]:
        return {
            "type": "List",
            "value": [safe_json_serialize(item) for item in self._value],
            "itemType": self.item_type.type_name() if self.item_type else None
        }
    
    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> 'List':
        items = data.get("value", [])
        item_type_name = data.get("itemType")
        
        # TODO: 根据item_type_name查找对应的类型
        return cls(items)
    
    @classmethod
    def type_name(cls) -> str:
        return "List"


class Set(PalantirType[PySet[Any]]):
    """集合类型"""
    
    def __init__(self, items: PySet[Any] = None, item_type: Optional[Type[PalantirType]] = None):
        self.item_type = item_type
        super().__init__(items or set())
    
    def _validate(self, value: Any) -> PySet[Any]:
        if isinstance(value, set):
            items = value
        elif isinstance(value, (list, tuple)):
            items = set(value)
        else:
            raise ValidationError(f"Expected set, list or tuple, got {type(value).__name__}")
        
        validated_items = set()
        for item in items:
            if self.item_type and not isinstance(item, self.item_type):
                try:
                    if hasattr(self.item_type, '_validate'):
                        validated_item = self.item_type(item)
                    else:
                        validated_item = item
                except Exception:
                    raise ValidationError(f"Cannot convert {type(item).__name__} to {self.item_type.__name__}")
            else:
                validated_item = item
            
            # 确保元素是可哈希的
            try:
                hash(validated_item)
                validated_items.add(validated_item)
            except TypeError:
                raise ValidationError(f"Set items must be hashable, got {type(validated_item).__name__}")
        
        return validated_items
    
    def add(self, item: Any):
        """添加元素到集合"""
        if self.item_type and not isinstance(item, self.item_type):
            try:
                item = self.item_type(item)
            except Exception:
                raise ValidationError(f"Cannot convert {type(item).__name__} to {self.item_type.__name__}")
        
        try:
            hash(item)
            self._value.add(item)
        except TypeError:
            raise ValidationError(f"Set items must be hashable, got {type(item).__name__}")
    
    def remove(self, item: Any):
        """从集合中移除元素"""
        self._value.remove(item)
    
    def __len__(self) -> int:
        return len(self._value)
    
    def __contains__(self, item: Any) -> bool:
        return item in self._value
    
    def to_json(self) -> Dict[str, Any]:
        return {
            "type": "Set",
            "value": [safe_json_serialize(item) for item in self._value],
            "itemType": self.item_type.type_name() if self.item_type else None
        }
    
    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> 'Set':
        items = data.get("value", [])
        item_type_name = data.get("itemType")
        
        # TODO: 根据item_type_name查找对应的类型
        return cls(set(items))
    
    @classmethod
    def type_name(cls) -> str:
        return "Set"


class Map(PalantirType[Dict[Any, Any]]):
    """映射类型"""
    
    def __init__(self, data: Dict[Any, Any] = None, 
                 key_type: Optional[Type[PalantirType]] = None,
                 value_type: Optional[Type[PalantirType]] = None):
        self.key_type = key_type
        self.value_type = value_type
        super().__init__(data or {})
    
    def _validate(self, value: Any) -> Dict[Any, Any]:
        if not isinstance(value, dict):
            raise ValidationError(f"Expected dict, got {type(value).__name__}")
        
        validated_dict = {}
        for key, val in value.items():
            # 验证键
            validated_key = key
            if self.key_type and not isinstance(key, self.key_type):
                try:
                    if hasattr(self.key_type, '_validate'):
                        validated_key = self.key_type(key)
                    else:
                        validated_key = key
                except Exception:
                    raise ValidationError(f"Cannot convert key {type(key).__name__} to {self.key_type.__name__}")
            
            # 确保键是可哈希的
            try:
                hash(validated_key)
            except TypeError:
                raise ValidationError(f"Map keys must be hashable, got {type(validated_key).__name__}")
            
            # 验证值
            validated_val = val
            if self.value_type and not isinstance(val, self.value_type):
                try:
                    if hasattr(self.value_type, '_validate'):
                        validated_val = self.value_type(val)
                    else:
                        validated_val = val
                except Exception:
                    raise ValidationError(f"Cannot convert value {type(val).__name__} to {self.value_type.__name__}")
            
            validated_dict[validated_key] = validated_val
        
        return validated_dict
    
    def put(self, key: Any, value: Any):
        """添加键值对"""
        if self.key_type and not isinstance(key, self.key_type):
            try:
                key = self.key_type(key)
            except Exception:
                raise ValidationError(f"Cannot convert key {type(key).__name__} to {self.key_type.__name__}")
        
        if self.value_type and not isinstance(value, self.value_type):
            try:
                value = self.value_type(value)
            except Exception:
                raise ValidationError(f"Cannot convert value {type(value).__name__} to {self.value_type.__name__}")
        
        try:
            hash(key)
            self._value[key] = value
        except TypeError:
            raise ValidationError(f"Map keys must be hashable, got {type(key).__name__}")
    
    def get(self, key: Any, default: Any = None) -> Any:
        """获取值"""
        return self._value.get(key, default)
    
    def remove(self, key: Any):
        """移除键值对"""
        if key in self._value:
            del self._value[key]
    
    def keys(self):
        """获取所有键"""
        return self._value.keys()
    
    def values(self):
        """获取所有值"""
        return self._value.values()
    
    def items(self):
        """获取所有键值对"""
        return self._value.items()
    
    def __len__(self) -> int:
        return len(self._value)
    
    def __getitem__(self, key: Any) -> Any:
        return self._value[key]
    
    def __setitem__(self, key: Any, value: Any):
        self.put(key, value)
    
    def __contains__(self, key: Any) -> bool:
        return key in self._value
    
    def to_json(self) -> Dict[str, Any]:
        return {
            "type": "Map",
            "value": {str(k): safe_json_serialize(v) for k, v in self._value.items()},
            "keyType": self.key_type.type_name() if self.key_type else None,
            "valueType": self.value_type.type_name() if self.value_type else None
        }
    
    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> 'Map':
        value_dict = data.get("value", {})
        key_type_name = data.get("keyType")
        value_type_name = data.get("valueType")
        
        # TODO: 根据type_name查找对应的类型
        return cls(value_dict)
    
    @classmethod
    def type_name(cls) -> str:
        return "Map"