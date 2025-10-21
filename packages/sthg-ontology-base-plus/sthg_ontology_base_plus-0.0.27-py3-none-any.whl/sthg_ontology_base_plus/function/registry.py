from typing import Dict, Type, Any, Optional
from .base import PalantirType


class TypeRegistry:
    """Palantir类型注册表，用于管理所有可用的类型"""
    
    def __init__(self):
        self._types: Dict[str, Type[PalantirType]] = {}
        self._aliases: Dict[str, str] = {}
        self._register_builtin_types()
    
    def _register_builtin_types(self):
        """注册内置类型"""
        from .primitive_types import (
            Boolean, String, Integer, Long, Float, Double, 
            Date, Timestamp, Binary
        )
        from .collection_types import List, Map, Set
        from .aggregation_types import Range, TwoDimensionalAggregation
        from .ontology_types import Object, ObjectSet
        
        # 注册基础类型
        self.register(Boolean)
        self.register(String)
        self.register(Integer)
        self.register(Long)
        self.register(Float)
        self.register(Double)
        self.register(Date)
        self.register(Timestamp)
        self.register(Binary)
        
        # 注册集合类型
        self.register(List)
        self.register(Map)
        self.register(Set)
        
        # 注册聚合类型
        self.register(Range)
        self.register(TwoDimensionalAggregation)
        
        # 注册本体类型
        self.register(Object)
        self.register(ObjectSet)
        
        # 设置别名
        self.add_alias("bool", "Boolean")
        self.add_alias("str", "String")
        self.add_alias("int", "Integer")
        self.add_alias("float", "Float")
        self.add_alias("list", "List")
        self.add_alias("dict", "Map")
        self.add_alias("set", "Set")
    
    def register(self, type_class: Type[PalantirType]):
        """注册新的类型"""
        if not issubclass(type_class, PalantirType):
            raise ValueError(f"Type must be a subclass of PalantirType, got {type_class}")
        
        type_name = type_class.type_name()
        if type_name in self._types:
            raise ValueError(f"Type {type_name} is already registered")
        
        self._types[type_name] = type_class
    
    def unregister(self, type_name: str):
        """取消注册类型"""
        if type_name in self._types:
            del self._types[type_name]
        
        # 移除相关别名
        aliases_to_remove = [alias for alias, target in self._aliases.items() if target == type_name]
        for alias in aliases_to_remove:
            del self._aliases[alias]
    
    def add_alias(self, alias: str, type_name: str):
        """为类型添加别名"""
        if type_name not in self._types:
            raise ValueError(f"Type {type_name} is not registered")
        
        self._aliases[alias] = type_name
    
    def remove_alias(self, alias: str):
        """移除别名"""
        if alias in self._aliases:
            del self._aliases[alias]
    
    def get_type(self, name: str) -> Optional[Type[PalantirType]]:
        """根据名称或别名获取类型"""
        # 先检查别名
        actual_name = self._aliases.get(name, name)
        return self._types.get(actual_name)
    
    def has_type(self, name: str) -> bool:
        """检查是否存在指定名称的类型"""
        actual_name = self._aliases.get(name, name)
        return actual_name in self._types
    
    def list_types(self) -> Dict[str, Type[PalantirType]]:
        """列出所有注册的类型"""
        return self._types.copy()
    
    def list_aliases(self) -> Dict[str, str]:
        """列出所有别名"""
        return self._aliases.copy()
    
    def create_instance(self, type_name: str, value: Any = None) -> Optional[PalantirType]:
        """根据类型名创建实例"""
        type_class = self.get_type(type_name)
        if type_class is None:
            raise ValueError(f"Unknown type: {type_name}")
        
        return type_class(value)
    
    def from_json(self, data: Dict[str, Any]) -> Optional[PalantirType]:
        """从JSON数据反序列化对象"""
        if not isinstance(data, dict) or "type" not in data:
            raise ValueError("Invalid JSON data format")
        
        type_name = data["type"]
        type_class = self.get_type(type_name)
        if type_class is None:
            raise ValueError(f"Unknown type: {type_name}")
        
        return type_class.from_json(data)


# 全局类型注册表实例
_global_registry = TypeRegistry()


def get_registry() -> TypeRegistry:
    """获取全局类型注册表"""
    return _global_registry


def register_type(type_class: Type[PalantirType]):
    """注册类型到全局注册表"""
    _global_registry.register(type_class)


def get_type(name: str) -> Optional[Type[PalantirType]]:
    """从全局注册表获取类型"""
    return _global_registry.get_type(name)


def create_instance(type_name: str, value: Any = None) -> Optional[PalantirType]:
    """从全局注册表创建类型实例"""
    return _global_registry.create_instance(type_name, value)


def from_json(data: Dict[str, Any]) -> Optional[PalantirType]:
    """从全局注册表反序列化JSON"""
    return _global_registry.from_json(data)