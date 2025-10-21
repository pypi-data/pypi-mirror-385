from typing import Any, Dict, Optional, Union, Tuple
from .base import PalantirType, ValidationError, safe_json_serialize


class Range(PalantirType[Dict[str, Any]]):
    """范围类型，表示一个数值范围"""
    
    def __init__(self, start: Optional[Union[int, float]] = None, 
                 end: Optional[Union[int, float]] = None,
                 start_inclusive: bool = True,
                 end_inclusive: bool = True):
        range_data = {
            'start': start,
            'end': end,
            'start_inclusive': start_inclusive,
            'end_inclusive': end_inclusive
        }
        super().__init__(range_data)
    
    def _validate(self, value: Any) -> Dict[str, Any]:
        if isinstance(value, dict):
            start = value.get('start')
            end = value.get('end')
            start_inclusive = value.get('start_inclusive', True)
            end_inclusive = value.get('end_inclusive', True)
        elif isinstance(value, (tuple, list)) and len(value) >= 2:
            start = value[0]
            end = value[1]
            start_inclusive = value[2] if len(value) > 2 else True
            end_inclusive = value[3] if len(value) > 3 else True
        else:
            raise ValidationError(f"Range expects dict or tuple/list with at least 2 elements, got {type(value).__name__}")
        
        # 验证数值类型
        if start is not None and not isinstance(start, (int, float)):
            try:
                start = float(start)
            except (ValueError, TypeError):
                raise ValidationError(f"Range start must be numeric, got {type(start).__name__}")
        
        if end is not None and not isinstance(end, (int, float)):
            try:
                end = float(end)
            except (ValueError, TypeError):
                raise ValidationError(f"Range end must be numeric, got {type(end).__name__}")
        
        # 验证范围逻辑
        if start is not None and end is not None and start > end:
            raise ValidationError(f"Range start ({start}) cannot be greater than end ({end})")
        
        return {
            'start': start,
            'end': end,
            'start_inclusive': bool(start_inclusive),
            'end_inclusive': bool(end_inclusive)
        }
    
    @property
    def start(self) -> Optional[Union[int, float]]:
        return self._value.get('start')
    
    @property
    def end(self) -> Optional[Union[int, float]]:
        return self._value.get('end')
    
    @property
    def start_inclusive(self) -> bool:
        return self._value.get('start_inclusive', True)
    
    @property
    def end_inclusive(self) -> bool:
        return self._value.get('end_inclusive', True)
    
    def contains(self, value: Union[int, float]) -> bool:
        """检查值是否在范围内"""
        if not isinstance(value, (int, float)):
            return False
        
        if self.start is not None:
            if self.start_inclusive:
                if value < self.start:
                    return False
            else:
                if value <= self.start:
                    return False
        
        if self.end is not None:
            if self.end_inclusive:
                if value > self.end:
                    return False
            else:
                if value >= self.end:
                    return False
        
        return True
    
    def to_json(self) -> Dict[str, Any]:
        return {
            "type": "Range",
            "value": {
                "start": self.start,
                "end": self.end,
                "startInclusive": self.start_inclusive,
                "endInclusive": self.end_inclusive
            }
        }
    
    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> 'Range':
        value = data.get("value", {})
        return cls(
            start=value.get("start"),
            end=value.get("end"),
            start_inclusive=value.get("startInclusive", True),
            end_inclusive=value.get("endInclusive", True)
        )
    
    @classmethod
    def type_name(cls) -> str:
        return "Range"
    
    def __str__(self) -> str:
        start_bracket = "[" if self.start_inclusive else "("
        end_bracket = "]" if self.end_inclusive else ")"
        start_val = self.start if self.start is not None else "-∞"
        end_val = self.end if self.end is not None else "+∞"
        return f"{start_bracket}{start_val}, {end_val}{end_bracket}"


class TwoDimensionalAggregation(PalantirType[Dict[str, Any]]):
    """二维聚合类型，用于表示二维数据的聚合结果"""
    
    def __init__(self, x_dimension: str = None, y_dimension: str = None,
                 data: Dict[Tuple[Any, Any], Any] = None):
        aggregation_data = {
            'x_dimension': x_dimension,
            'y_dimension': y_dimension,
            'data': data or {}
        }
        super().__init__(aggregation_data)
    
    def _validate(self, value: Any) -> Dict[str, Any]:
        if not isinstance(value, dict):
            raise ValidationError(f"TwoDimensionalAggregation expects dict, got {type(value).__name__}")
        
        x_dimension = value.get('x_dimension')
        y_dimension = value.get('y_dimension')
        data = value.get('data', {})
        
        if x_dimension is not None and not isinstance(x_dimension, str):
            x_dimension = str(x_dimension)
        
        if y_dimension is not None and not isinstance(y_dimension, str):
            y_dimension = str(y_dimension)
        
        if not isinstance(data, dict):
            raise ValidationError(f"TwoDimensionalAggregation data must be dict, got {type(data).__name__}")
        
        # 验证数据格式
        validated_data = {}
        for key, val in data.items():
            if isinstance(key, (list, tuple)) and len(key) == 2:
                validated_key = (key[0], key[1])
            elif isinstance(key, str) and ',' in key:
                # 尝试解析字符串格式的键
                parts = key.split(',', 1)
                validated_key = (parts[0].strip(), parts[1].strip())
            else:
                raise ValidationError(f"TwoDimensionalAggregation keys must be 2-tuples, got {type(key).__name__}")
            
            validated_data[validated_key] = val
        
        return {
            'x_dimension': x_dimension,
            'y_dimension': y_dimension,
            'data': validated_data
        }
    
    @property
    def x_dimension(self) -> Optional[str]:
        return self._value.get('x_dimension')
    
    @property
    def y_dimension(self) -> Optional[str]:
        return self._value.get('y_dimension')
    
    @property
    def data(self) -> Dict[Tuple[Any, Any], Any]:
        return self._value.get('data', {})
    
    def get(self, x_key: Any, y_key: Any, default: Any = None) -> Any:
        """获取指定坐标的值"""
        return self.data.get((x_key, y_key), default)
    
    def set(self, x_key: Any, y_key: Any, value: Any):
        """设置指定坐标的值"""
        self._value['data'][(x_key, y_key)] = value
    
    def get_x_keys(self) -> set:
        """获取所有X维度的键"""
        return {key[0] for key in self.data.keys()}
    
    def get_y_keys(self) -> set:
        """获取所有Y维度的键"""
        return {key[1] for key in self.data.keys()}
    
    def get_row(self, x_key: Any) -> Dict[Any, Any]:
        """获取指定X坐标的所有数据（行）"""
        return {key[1]: value for key, value in self.data.items() if key[0] == x_key}
    
    def get_column(self, y_key: Any) -> Dict[Any, Any]:
        """获取指定Y坐标的所有数据（列）"""
        return {key[0]: value for key, value in self.data.items() if key[1] == y_key}
    
    def to_json(self) -> Dict[str, Any]:
        # 将tuple键转换为字符串格式以便JSON序列化
        json_data = {}
        for (x, y), value in self.data.items():
            key_str = f"{x},{y}"
            json_data[key_str] = safe_json_serialize(value)
        
        return {
            "type": "TwoDimensionalAggregation",
            "value": {
                "xDimension": self.x_dimension,
                "yDimension": self.y_dimension,
                "data": json_data
            }
        }
    
    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> 'TwoDimensionalAggregation':
        value = data.get("value", {})
        x_dimension = value.get("xDimension")
        y_dimension = value.get("yDimension")
        json_data = value.get("data", {})
        
        # 将字符串键转换回tuple格式
        tuple_data = {}
        for key_str, val in json_data.items():
            if ',' in key_str:
                parts = key_str.split(',', 1)
                tuple_key = (parts[0].strip(), parts[1].strip())
                tuple_data[tuple_key] = val
        
        return cls(x_dimension, y_dimension, tuple_data)
    
    @classmethod
    def type_name(cls) -> str:
        return "TwoDimensionalAggregation"
    
    def __str__(self) -> str:
        return f"TwoDimensionalAggregation(x={self.x_dimension}, y={self.y_dimension}, size={len(self.data)})"


class ThreeDimensionalAggregation(PalantirType[Dict[str, Any]]):
    """三维聚合类型，用于表示三维数据的聚合结果"""
    
    def __init__(self, x_dimension: str = None, y_dimension: str = None, z_dimension: str = None,
                 data: Dict[Tuple[Any, Any, Any], Any] = None):
        aggregation_data = {
            'x_dimension': x_dimension,
            'y_dimension': y_dimension,
            'z_dimension': z_dimension,
            'data': data or {}
        }
        super().__init__(aggregation_data)
    
    def _validate(self, value: Any) -> Dict[str, Any]:
        if not isinstance(value, dict):
            raise ValidationError(f"ThreeDimensionalAggregation expects dict, got {type(value).__name__}")
        
        x_dimension = value.get('x_dimension')
        y_dimension = value.get('y_dimension')
        z_dimension = value.get('z_dimension')
        data = value.get('data', {})
        
        # 验证维度名称
        if x_dimension is not None and not isinstance(x_dimension, str):
            x_dimension = str(x_dimension)
        if y_dimension is not None and not isinstance(y_dimension, str):
            y_dimension = str(y_dimension)
        if z_dimension is not None and not isinstance(z_dimension, str):
            z_dimension = str(z_dimension)
        
        if not isinstance(data, dict):
            raise ValidationError(f"ThreeDimensionalAggregation data must be dict, got {type(data).__name__}")
        
        # 验证数据格式
        validated_data = {}
        for key, val in data.items():
            if isinstance(key, (list, tuple)) and len(key) == 3:
                validated_key = (key[0], key[1], key[2])
            elif isinstance(key, str) and key.count(',') == 2:
                # 尝试解析字符串格式的键
                parts = key.split(',', 2)
                validated_key = (parts[0].strip(), parts[1].strip(), parts[2].strip())
            else:
                raise ValidationError(f"ThreeDimensionalAggregation keys must be 3-tuples, got {type(key).__name__}")
            
            validated_data[validated_key] = val
        
        return {
            'x_dimension': x_dimension,
            'y_dimension': y_dimension,
            'z_dimension': z_dimension,
            'data': validated_data
        }
    
    @property
    def x_dimension(self) -> Optional[str]:
        return self._value.get('x_dimension')
    
    @property
    def y_dimension(self) -> Optional[str]:
        return self._value.get('y_dimension')
    
    @property
    def z_dimension(self) -> Optional[str]:
        return self._value.get('z_dimension')
    
    @property
    def data(self) -> Dict[Tuple[Any, Any, Any], Any]:
        return self._value.get('data', {})
    
    def get(self, x_key: Any, y_key: Any, z_key: Any, default: Any = None) -> Any:
        """获取指定坐标的值"""
        return self.data.get((x_key, y_key, z_key), default)
    
    def set(self, x_key: Any, y_key: Any, z_key: Any, value: Any):
        """设置指定坐标的值"""
        self._value['data'][(x_key, y_key, z_key)] = value
    
    def get_x_keys(self) -> set:
        """获取所有X维度的键"""
        return {key[0] for key in self.data.keys()}
    
    def get_y_keys(self) -> set:
        """获取所有Y维度的键"""
        return {key[1] for key in self.data.keys()}
    
    def get_z_keys(self) -> set:
        """获取所有Z维度的键"""
        return {key[2] for key in self.data.keys()}
    
    def get_slice_xy(self, z_key: Any) -> Dict[Tuple[Any, Any], Any]:
        """获取指定Z坐标的XY平面数据"""
        return {(key[0], key[1]): value for key, value in self.data.items() if key[2] == z_key}
    
    def get_slice_xz(self, y_key: Any) -> Dict[Tuple[Any, Any], Any]:
        """获取指定Y坐标的XZ平面数据"""
        return {(key[0], key[2]): value for key, value in self.data.items() if key[1] == y_key}
    
    def get_slice_yz(self, x_key: Any) -> Dict[Tuple[Any, Any], Any]:
        """获取指定X坐标的YZ平面数据"""
        return {(key[1], key[2]): value for key, value in self.data.items() if key[0] == x_key}
    
    def get_line_x(self, y_key: Any, z_key: Any) -> Dict[Any, Any]:
        """获取指定Y,Z坐标的X轴线数据"""
        return {key[0]: value for key, value in self.data.items() if key[1] == y_key and key[2] == z_key}
    
    def get_line_y(self, x_key: Any, z_key: Any) -> Dict[Any, Any]:
        """获取指定X,Z坐标的Y轴线数据"""
        return {key[1]: value for key, value in self.data.items() if key[0] == x_key and key[2] == z_key}
    
    def get_line_z(self, x_key: Any, y_key: Any) -> Dict[Any, Any]:
        """获取指定X,Y坐标的Z轴线数据"""
        return {key[2]: value for key, value in self.data.items() if key[0] == x_key and key[1] == y_key}
    
    def get_dimensions(self) -> Tuple[set, set, set]:
        """获取所有三个维度的键"""
        return self.get_x_keys(), self.get_y_keys(), self.get_z_keys()
    
    def to_json(self) -> Dict[str, Any]:
        # 将tuple键转换为字符串格式以便JSON序列化
        json_data = {}
        for (x, y, z), value in self.data.items():
            key_str = f"{x},{y},{z}"
            json_data[key_str] = safe_json_serialize(value)
        
        return {
            "type": "ThreeDimensionalAggregation",
            "value": {
                "xDimension": self.x_dimension,
                "yDimension": self.y_dimension,
                "zDimension": self.z_dimension,
                "data": json_data
            }
        }
    
    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> 'ThreeDimensionalAggregation':
        value = data.get("value", {})
        x_dimension = value.get("xDimension")
        y_dimension = value.get("yDimension")
        z_dimension = value.get("zDimension")
        json_data = value.get("data", {})
        
        # 将字符串键转换回tuple格式
        tuple_data = {}
        for key_str, val in json_data.items():
            if key_str.count(',') == 2:
                parts = key_str.split(',', 2)
                tuple_key = (parts[0].strip(), parts[1].strip(), parts[2].strip())
                tuple_data[tuple_key] = val
        
        return cls(x_dimension, y_dimension, z_dimension, tuple_data)
    
    @classmethod
    def type_name(cls) -> str:
        return "ThreeDimensionalAggregation"
    
    def __str__(self) -> str:
        return f"ThreeDimensionalAggregation(x={self.x_dimension}, y={self.y_dimension}, z={self.z_dimension}, size={len(self.data)})"