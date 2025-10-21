from typing import Any, Dict, Optional, Union, List as PyList, Set as PySet
from datetime import datetime
from .base import PalantirType, ValidationError, safe_json_serialize


class Object(PalantirType[Dict[str, Any]]):
    """本体对象类型，表示Palantir中的对象实例"""
    
    def __init__(self, object_type: str = None, primary_key: Any = None, 
                 properties: Dict[str, Any] = None):
        object_data = {
            'object_type': object_type,
            'primary_key': primary_key,
            'properties': properties or {}
        }
        super().__init__(object_data)
    
    def _validate(self, value: Any) -> Dict[str, Any]:
        if isinstance(value, dict):
            object_type = value.get('object_type')
            primary_key = value.get('primary_key')
            properties = value.get('properties', {})
        elif hasattr(value, '__dict__'):
            # 支持从其他对象转换
            object_data = value.__dict__.copy()
            object_type = object_data.pop('object_type', None)
            primary_key = object_data.pop('primary_key', None)
            properties = object_data
        else:
            raise ValidationError(f"Object expects dict or object with attributes, got {type(value).__name__}")
        
        if object_type is not None and not isinstance(object_type, str):
            object_type = str(object_type)
        
        if not isinstance(properties, dict):
            raise ValidationError(f"Object properties must be dict, got {type(properties).__name__}")
        
        return {
            'object_type': object_type,
            'primary_key': primary_key,
            'properties': properties
        }
    
    @property
    def object_type(self) -> Optional[str]:
        """获取对象类型"""
        return self._value.get('object_type')
    
    @object_type.setter
    def object_type(self, value: str):
        """设置对象类型"""
        self._value['object_type'] = str(value) if value is not None else None
    
    @property
    def primary_key(self) -> Any:
        """获取主键"""
        return self._value.get('primary_key')
    
    @primary_key.setter
    def primary_key(self, value: Any):
        """设置主键"""
        self._value['primary_key'] = value
    
    @property
    def properties(self) -> Dict[str, Any]:
        """获取属性字典"""
        return self._value.get('properties', {})
    
    def get_property(self, name: str, default: Any = None) -> Any:
        """获取属性值"""
        return self.properties.get(name, default)
    
    def set_property(self, name: str, value: Any):
        """设置属性值"""
        self.properties[name] = value
    
    def has_property(self, name: str) -> bool:
        """检查是否有指定属性"""
        return name in self.properties
    
    def remove_property(self, name: str):
        """移除属性"""
        if name in self.properties:
            del self.properties[name]
    
    def get_property_names(self) -> PyList[str]:
        """获取所有属性名"""
        return list(self.properties.keys())
    
    def to_json(self) -> Dict[str, Any]:
        return {
            "type": "Object",
            "value": {
                "objectType": self.object_type,
                "primaryKey": safe_json_serialize(self.primary_key),
                "properties": {k: safe_json_serialize(v) for k, v in self.properties.items()}
            }
        }
    
    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> 'Object':
        value = data.get("value", {})
        return cls(
            object_type=value.get("objectType"),
            primary_key=value.get("primaryKey"),
            properties=value.get("properties", {})
        )
    
    @classmethod
    def type_name(cls) -> str:
        return "Object"
    
    def __str__(self) -> str:
        return f"Object(type={self.object_type}, key={self.primary_key}, properties={len(self.properties)})"


class ObjectSet(PalantirType[Dict[str, Any]]):
    """本体对象集合类型，表示一组相同类型的对象"""
    
    def __init__(self, object_type: str = None, objects: PyList[Object] = None):
        object_set_data = {
            'object_type': object_type,
            'objects': objects or []
        }
        super().__init__(object_set_data)
    
    def _validate(self, value: Any) -> Dict[str, Any]:
        if isinstance(value, dict):
            object_type = value.get('object_type')
            objects = value.get('objects', [])
        elif isinstance(value, (list, tuple)):
            # 如果直接传入对象列表
            objects = list(value)
            object_type = None
            # 尝试从第一个对象推断类型
            if objects and hasattr(objects[0], 'object_type'):
                object_type = objects[0].object_type
        else:
            raise ValidationError(f"ObjectSet expects dict or list, got {type(value).__name__}")
        
        if object_type is not None and not isinstance(object_type, str):
            object_type = str(object_type)
        
        if not isinstance(objects, (list, tuple)):
            raise ValidationError(f"ObjectSet objects must be list, got {type(objects).__name__}")
        
        # 验证并转换对象
        validated_objects = []
        for obj in objects:
            if isinstance(obj, Object):
                validated_obj = obj
            elif isinstance(obj, dict):
                validated_obj = Object(
                    object_type=obj.get('object_type', object_type),
                    primary_key=obj.get('primary_key'),
                    properties=obj.get('properties', {})
                )
            else:
                raise ValidationError(f"ObjectSet contains invalid object type: {type(obj).__name__}")
            
            # 检查对象类型一致性
            if object_type and validated_obj.object_type and validated_obj.object_type != object_type:
                raise ValidationError(f"Object type mismatch: expected {object_type}, got {validated_obj.object_type}")
            
            validated_objects.append(validated_obj)
        
        return {
            'object_type': object_type,
            'objects': validated_objects
        }
    
    @property
    def object_type(self) -> Optional[str]:
        """获取对象集合的类型"""
        return self._value.get('object_type')
    
    @object_type.setter
    def object_type(self, value: str):
        """设置对象集合的类型"""
        self._value['object_type'] = str(value) if value is not None else None
    
    @property
    def objects(self) -> PyList[Object]:
        """获取对象列表"""
        return self._value.get('objects', [])
    
    def add_object(self, obj: Union[Object, Dict[str, Any]]):
        """添加对象到集合"""
        if isinstance(obj, Object):
            validated_obj = obj
        elif isinstance(obj, dict):
            validated_obj = Object(
                object_type=obj.get('object_type', self.object_type),
                primary_key=obj.get('primary_key'),
                properties=obj.get('properties', {})
            )
        else:
            raise ValidationError(f"Invalid object type: {type(obj).__name__}")
        
        # 检查类型一致性
        if self.object_type and validated_obj.object_type and validated_obj.object_type != self.object_type:
            raise ValidationError(f"Object type mismatch: expected {self.object_type}, got {validated_obj.object_type}")
        
        self.objects.append(validated_obj)
    
    def remove_object(self, primary_key: Any):
        """根据主键移除对象"""
        self._value['objects'] = [obj for obj in self.objects if obj.primary_key != primary_key]
    
    def get_object(self, primary_key: Any) -> Optional[Object]:
        """根据主键获取对象"""
        for obj in self.objects:
            if obj.primary_key == primary_key:
                return obj
        return None
    
    def filter_by_property(self, property_name: str, property_value: Any) -> 'ObjectSet':
        """根据属性值过滤对象"""
        filtered_objects = [
            obj for obj in self.objects 
            if obj.get_property(property_name) == property_value
        ]
        return ObjectSet(self.object_type, filtered_objects)
    
    def get_primary_keys(self) -> PyList[Any]:
        """获取所有主键"""
        return [obj.primary_key for obj in self.objects]
    
    def get_unique_property_values(self, property_name: str) -> PySet[Any]:
        """获取指定属性的所有唯一值"""
        values = set()
        for obj in self.objects:
            if obj.has_property(property_name):
                values.add(obj.get_property(property_name))
        return values
    
    def __len__(self) -> int:
        return len(self.objects)
    
    def __iter__(self):
        return iter(self.objects)
    
    def __getitem__(self, index: int) -> Object:
        return self.objects[index]
    
    def to_json(self) -> Dict[str, Any]:
        return {
            "type": "ObjectSet",
            "value": {
                "objectType": self.object_type,
                "objects": [obj.to_json()["value"] for obj in self.objects]
            }
        }
    
    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> 'ObjectSet':
        value = data.get("value", {})
        object_type = value.get("objectType")
        objects_data = value.get("objects", [])
        
        objects = []
        for obj_data in objects_data:
            obj = Object(
                object_type=obj_data.get("objectType", object_type),
                primary_key=obj_data.get("primaryKey"),
                properties=obj_data.get("properties", {})
            )
            objects.append(obj)
        
        return cls(object_type, objects)
    
    @classmethod
    def type_name(cls) -> str:
        return "ObjectSet"
    
    def __str__(self) -> str:
        return f"ObjectSet(type={self.object_type}, count={len(self.objects)})"


class OntologyEdit(PalantirType[Dict[str, Any]]):
    """本体编辑类型，用于表示对本体对象的修改操作"""
    
    def __init__(self, object_type: str = None, primary_key: Any = None,
                 operation: str = "UPDATE", changes: Dict[str, Any] = None,
                 timestamp: datetime = None, user_id: str = None):
        edit_data = {
            'object_type': object_type,
            'primary_key': primary_key,
            'operation': operation,
            'changes': changes or {},
            'timestamp': timestamp or datetime.now(),
            'user_id': user_id
        }
        super().__init__(edit_data)
    
    def _validate(self, value: Any) -> Dict[str, Any]:
        if isinstance(value, dict):
            object_type = value.get('object_type')
            primary_key = value.get('primary_key')
            operation = value.get('operation', 'UPDATE')
            changes = value.get('changes', {})
            timestamp = value.get('timestamp', datetime.now())
            user_id = value.get('user_id')
        else:
            raise ValidationError(f"OntologyEdit expects dict, got {type(value).__name__}")
        
        # 验证对象类型
        if object_type is not None and not isinstance(object_type, str):
            object_type = str(object_type)
        
        # 验证操作类型
        valid_operations = ['CREATE', 'UPDATE', 'DELETE', 'LINK', 'UNLINK']
        if operation not in valid_operations:
            raise ValidationError(f"Invalid operation: {operation}. Valid operations: {valid_operations}")
        
        # 验证更改内容
        if not isinstance(changes, dict):
            raise ValidationError(f"Changes must be dict, got {type(changes).__name__}")
        
        # 验证时间戳
        if timestamp is not None:
            if isinstance(timestamp, str):
                try:
                    timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                except ValueError:
                    raise ValidationError(f"Invalid timestamp format: {timestamp}")
            elif not isinstance(timestamp, datetime):
                raise ValidationError(f"Timestamp must be datetime or string, got {type(timestamp).__name__}")
        
        # 验证用户ID
        if user_id is not None and not isinstance(user_id, str):
            user_id = str(user_id)
        
        return {
            'object_type': object_type,
            'primary_key': primary_key,
            'operation': operation,
            'changes': changes,
            'timestamp': timestamp,
            'user_id': user_id
        }
    
    @property
    def object_type(self) -> Optional[str]:
        """获取目标对象类型"""
        return self._value.get('object_type')
    
    @property
    def primary_key(self) -> Any:
        """获取目标对象主键"""
        return self._value.get('primary_key')
    
    @property
    def operation(self) -> str:
        """获取操作类型"""
        return self._value.get('operation', 'UPDATE')
    
    @property
    def changes(self) -> Dict[str, Any]:
        """获取变更内容"""
        return self._value.get('changes', {})
    
    @property
    def timestamp(self) -> datetime:
        """获取操作时间戳"""
        return self._value.get('timestamp', datetime.now())
    
    @property
    def user_id(self) -> Optional[str]:
        """获取操作用户ID"""
        return self._value.get('user_id')
    
    def add_change(self, property_name: str, new_value: Any, old_value: Any = None):
        """添加属性变更"""
        self.changes[property_name] = {
            'new_value': new_value,
            'old_value': old_value
        }
    
    def remove_change(self, property_name: str):
        """移除属性变更"""
        if property_name in self.changes:
            del self.changes[property_name]
    
    def get_changed_properties(self) -> PyList[str]:
        """获取所有变更的属性名"""
        return list(self.changes.keys())
    
    def get_new_value(self, property_name: str, default: Any = None) -> Any:
        """获取属性的新值"""
        change = self.changes.get(property_name, {})
        return change.get('new_value', default)
    
    def get_old_value(self, property_name: str, default: Any = None) -> Any:
        """获取属性的旧值"""
        change = self.changes.get(property_name, {})
        return change.get('old_value', default)
    
    def is_create_operation(self) -> bool:
        """检查是否为创建操作"""
        return self.operation == 'CREATE'
    
    def is_update_operation(self) -> bool:
        """检查是否为更新操作"""
        return self.operation == 'UPDATE'
    
    def is_delete_operation(self) -> bool:
        """检查是否为删除操作"""
        return self.operation == 'DELETE'
    
    def is_link_operation(self) -> bool:
        """检查是否为链接操作"""
        return self.operation == 'LINK'
    
    def is_unlink_operation(self) -> bool:
        """检查是否为解除链接操作"""
        return self.operation == 'UNLINK'
    
    def apply_to_object(self, target_object: Object) -> Object:
        """将编辑应用到目标对象"""
        if self.object_type and target_object.object_type != self.object_type:
            raise ValidationError(f"Object type mismatch: expected {self.object_type}, got {target_object.object_type}")
        
        if self.primary_key and target_object.primary_key != self.primary_key:
            raise ValidationError(f"Primary key mismatch: expected {self.primary_key}, got {target_object.primary_key}")
        
        if self.is_delete_operation():
            raise ValidationError("Cannot apply DELETE operation to existing object")
        
        # 应用属性变更
        for property_name, change in self.changes.items():
            new_value = change.get('new_value')
            if new_value is not None:
                target_object.set_property(property_name, new_value)
            elif 'new_value' in change and change['new_value'] is None:
                # 显式设置为None，表示删除属性
                target_object.remove_property(property_name)
        
        return target_object
    
    def to_json(self) -> Dict[str, Any]:
        return {
            "type": "OntologyEdit",
            "value": {
                "objectType": self.object_type,
                "primaryKey": safe_json_serialize(self.primary_key),
                "operation": self.operation,
                "changes": {k: safe_json_serialize(v) for k, v in self.changes.items()},
                "timestamp": self.timestamp.isoformat() if self.timestamp else None,
                "userId": self.user_id
            }
        }
    
    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> 'OntologyEdit':
        value = data.get("value", {})
        timestamp_str = value.get("timestamp")
        timestamp = None
        if timestamp_str:
            timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        
        return cls(
            object_type=value.get("objectType"),
            primary_key=value.get("primaryKey"),
            operation=value.get("operation", "UPDATE"),
            changes=value.get("changes", {}),
            timestamp=timestamp,
            user_id=value.get("userId")
        )
    
    @classmethod
    def type_name(cls) -> str:
        return "OntologyEdit"
    
    def __str__(self) -> str:
        return f"OntologyEdit(operation={self.operation}, type={self.object_type}, key={self.primary_key}, changes={len(self.changes)})"