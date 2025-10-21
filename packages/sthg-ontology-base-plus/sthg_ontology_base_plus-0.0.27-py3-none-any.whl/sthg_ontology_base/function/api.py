"""
Palantir 类型系统 API
提供统一的类型导入接口，支持从 sthg_ontology_base_plus.function.api 导入所有类型
"""

# 导入基础类型
from .primitive_types import (
    Boolean,
    String, 
    Integer,
    Long,
    Float,
    Double,
    Date,
    Timestamp,
    Binary,
    Attachment,
    Byte,
    Short,
    Decimal
)

# 导入集合类型
from .collection_types import (
    List,
    Map,
    Set
)

# 导入聚合类型
from .aggregation_types import (
    Range,
    TwoDimensionalAggregation,
    ThreeDimensionalAggregation
)

# 导入本体类型
from .ontology_types import (
    Object,
    ObjectSet,
    OntologyEdit
)

# 导入特殊类型
from .optional_types import (
    Optional
)

# 导入基础类和工具
from .base import (
    PalantirType,
    ValidationError,
    validate_type,
    safe_json_serialize
)

# 导入注册表功能
from .registry import (
    TypeRegistry,
    get_registry,
    register_type,
    get_type,
    create_instance,
    from_json
)

# 定义所有可导入的类型和工具
__all__ = [
    # 基础类型
    'Boolean',
    'String', 
    'Integer',
    'Long',
    'Float',
    'Double',
    'Date',
    'Timestamp',
    'Binary',
    'Attachment',
    'Byte',
    'Short',
    'Decimal',
    
    # 集合类型
    'List',
    'Map',
    'Set',
    
    # 聚合类型
    'Range',
    'TwoDimensionalAggregation',
    'ThreeDimensionalAggregation',
    
    # 本体类型
    'Object',
    'ObjectSet',
    'OntologyEdit',
    
    # 特殊类型
    'Optional',
    
    # 基础类和工具
    'PalantirType',
    'ValidationError',
    'validate_type',
    'safe_json_serialize',
    
    # 注册表功能
    'TypeRegistry',
    'get_registry',
    'register_type',
    'get_type',
    'create_instance',
    'from_json'
]

# 便利函数
def get_all_types():
    """获取所有可用的类型"""
    return get_registry().list_types()

def get_all_aliases():
    """获取所有类型别名"""
    return get_registry().list_aliases()

def is_palantir_type(obj):
    """检查对象是否为Palantir类型实例"""
    return isinstance(obj, PalantirType)

def get_type_name(obj):
    """获取对象的类型名称"""
    if isinstance(obj, PalantirType):
        return obj.type_name()
    elif hasattr(obj, '__class__'):
        return obj.__class__.__name__
    else:
        return type(obj).__name__

# 添加到__all__
__all__.extend([
    'get_all_types',
    'get_all_aliases', 
    'is_palantir_type',
    'get_type_name'
])