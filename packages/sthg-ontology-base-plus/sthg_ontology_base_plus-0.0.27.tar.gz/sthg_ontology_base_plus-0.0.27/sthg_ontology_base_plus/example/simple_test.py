#!/usr/bin/env python3
"""
简单的 Palantir 类型系统测试，不依赖现有包
"""
import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_direct_imports():
    """直接测试类型导入"""
    print("测试直接导入...")
    
    try:
        # 直接从模块导入，避免现有包的依赖问题
        from sthg_ontology_base_plus.function.primitive_types import Integer, String, Boolean
        from sthg_ontology_base_plus.function.collection_types import List, Map
        from sthg_ontology_base_plus.function.ontology_types import Object
        
        print("✓ 直接导入成功")
        
        # 测试基本功能
        int_val = Integer(42)
        assert int_val.value == 42
        print("✓ Integer 创建成功")
        
        str_val = String("Hello")
        assert str_val.value == "Hello"
        print("✓ String 创建成功")
        
        bool_val = Boolean(True)
        assert bool_val.value is True
        print("✓ Boolean 创建成功")
        
        list_val = List([1, 2, 3])
        assert len(list_val) == 3
        print("✓ List 创建成功")
        
        map_val = Map({'a': 1})
        assert map_val.get('a') == 1
        print("✓ Map 创建成功")
        
        obj = Object("User", "123")
        obj.set_property("name", "测试")
        assert obj.get_property("name") == "测试"
        print("✓ Object 创建成功")
        
        return True
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_api_imports():
    """测试API导入"""
    print("\n测试API导入...")
    
    try:
        from sthg_ontology_base_plus.function.api import (
            Integer, Float, String, Boolean, Date,
            List, Map, Set, Range, Object, ObjectSet, Double, Long, Timestamp, TwoDimensionalAggregation
        )
        
        print("✓ API 导入成功")
        
        # 快速功能测试
        val = Integer(100)
        assert val.value == 100

        print("✓ API 中的类型正常工作")
        
        return True
    except Exception as e:
        print(f"✗ API 导入失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("开始简单类型系统测试...")
    
    tests = [test_direct_imports, test_api_imports]
    passed = sum(1 for test in tests if test())
    
    print(f"\n测试结果: {passed}/{len(tests)} 通过")
    
    if passed == len(tests):
        print("🎉 类型系统基本功能正常！")
    else:
        print("⚠️  部分测试失败")

if __name__ == "__main__":
    from sthg_ontology_base_plus.function.api import Integer, String, Boolean


    def with_strin(func):
        def wrapper(*args, **kwargs):
            # 自动将传入的str类型参数转换为String类型
            new_args = [String(arg) if isinstance(arg, str) else arg for arg in args]
            new_kwargs = {k: String(v) if isinstance(v, str) else v for k, v in kwargs.items()}
            return func(*new_args, **new_kwargs)

        return wrapper
    @with_strin
    def mytesr(param1: String):

        print(param1)
    # main()
    # a = String("jl")
    a = "hlhghigii"
    mytesr(param1=a)