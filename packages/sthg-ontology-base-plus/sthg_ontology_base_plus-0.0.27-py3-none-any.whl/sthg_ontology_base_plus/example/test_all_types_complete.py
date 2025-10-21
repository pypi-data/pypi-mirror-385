#!/usr/bin/env python3
"""
完整的 Palantir 类型系统测试，按照 simple_test.py 的样式
"""
import sys
import os

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.join(current_dir, '..', '..')
sys.path.insert(0, project_root)

def test_direct_imports():
    """直接测试类型导入"""
    print("测试直接导入...")
    
    try:
        # 直接从模块导入所有类型
        from sthg_ontology_base_plus.function.primitive_types import (
            Integer, String, Boolean, Long, Float, Double, Date, Timestamp, Binary,
            Attachment, Byte, Short, Decimal
        )
        from sthg_ontology_base_plus.function.collection_types import List, Map, Set
        from sthg_ontology_base_plus.function.aggregation_types import Range, TwoDimensionalAggregation, ThreeDimensionalAggregation
        from sthg_ontology_base_plus.function.ontology_types import Object, ObjectSet, OntologyEdit
        from sthg_ontology_base_plus.function.optional_types import Optional
        
        print("✓ 直接导入成功")
        
        # 测试基础类型
        int_val = Integer(42)
        assert int_val.value == 42
        print("✓ Integer 创建成功")
        
        str_val = String("Hello")
        assert str_val.value == "Hello"
        print("✓ String 创建成功")
        
        bool_val = Boolean(True)
        assert bool_val.value is True
        print("✓ Boolean 创建成功")
        
        long_val = Long(9223372036854775807)
        assert long_val.value == 9223372036854775807
        print("✓ Long 创建成功")
        
        float_val = Float(3.14)
        assert abs(float_val.value - 3.14) < 0.001
        print("✓ Float 创建成功")
        
        double_val = Double(2.718)
        assert abs(double_val.value - 2.718) < 0.001
        print("✓ Double 创建成功")
        
        # 测试新增基础类型
        attachment = Attachment("test.txt", b"Hello", "text/plain")
        assert attachment.filename == "test.txt"
        assert attachment.size == 5
        print("✓ Attachment 创建成功")
        
        byte_val = Byte(127)
        assert byte_val.value == 127
        print("✓ Byte 创建成功")
        
        short_val = Short(32767)
        assert short_val.value == 32767
        print("✓ Short 创建成功")
        
        decimal_val = Decimal("123.456")
        assert str(decimal_val.value) == "123.456"
        print("✓ Decimal 创建成功")
        
        # 测试集合类型
        list_val = List([1, 2, 3])
        assert len(list_val) == 3
        print("✓ List 创建成功")
        
        map_val = Map({'a': 1})
        assert map_val.get('a') == 1
        print("✓ Map 创建成功")
        
        set_val = Set([1, 2, 2, 3])
        assert len(set_val) == 3  # 去重后
        print("✓ Set 创建成功")
        
        # 测试聚合类型
        range_val = Range(10, 100)
        assert range_val.contains(50)
        print("✓ Range 创建成功")
        
        agg_2d = TwoDimensionalAggregation("X", "Y", {("a", "b"): 100})
        assert agg_2d.get("a", "b") == 100
        print("✓ TwoDimensionalAggregation 创建成功")
        
        agg_3d = ThreeDimensionalAggregation("X", "Y", "Z", {("a", "b", "c"): 200})
        assert agg_3d.get("a", "b", "c") == 200
        print("✓ ThreeDimensionalAggregation 创建成功")
        
        # 测试本体类型
        obj = Object("User", "123")
        obj.set_property("name", "测试")
        assert obj.get_property("name") == "测试"
        print("✓ Object 创建成功")
        
        obj_set = ObjectSet("User", [obj])
        assert len(obj_set) == 1
        print("✓ ObjectSet 创建成功")
        
        edit = OntologyEdit("User", "123", "UPDATE", {"name": {"new_value": "新名字"}})
        assert edit.operation == "UPDATE"
        print("✓ OntologyEdit 创建成功")
        
        # 测试特殊类型
        opt_val = Optional("test")
        assert opt_val.has_value
        print("✓ Optional 创建成功")
        
        opt_none = Optional(None)
        assert opt_none.is_none
        print("✓ Optional(None) 创建成功")
        
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
            # 基础类型
            Integer, Float, String, Boolean, Date, Long, Double, Timestamp, Binary,
            # 新增基础类型
            Attachment, Byte, Short, Decimal,
            # 集合类型
            List, Map, Set, 
            # 聚合类型
            Range, TwoDimensionalAggregation, ThreeDimensionalAggregation,
            # 本体类型
            Object, ObjectSet, OntologyEdit,
            # 特殊类型
            Optional
        )
        
        print("✓ API 导入成功")
        
        # 快速功能测试每个类型
        val = Integer(100)
        assert val.value == 100
        print("✓ Integer 正常工作")
        
        str_val = String("API测试")
        assert str_val.value == "API测试"
        print("✓ String 正常工作")
        
        attachment = Attachment("api_test.txt", b"API content")
        assert attachment.filename == "api_test.txt"
        print("✓ Attachment 正常工作")
        
        byte_val = Byte(100)
        assert byte_val.value == 100
        print("✓ Byte 正常工作")
        
        short_val = Short(1000)
        assert short_val.value == 1000
        print("✓ Short 正常工作")
        
        decimal_val = Decimal("99.99")
        assert str(decimal_val.value) == "99.99"
        print("✓ Decimal 正常工作")
        
        opt = Optional("API Optional")
        assert opt.value == "API Optional"
        print("✓ Optional 正常工作")
        
        agg_3d = ThreeDimensionalAggregation()
        agg_3d.set("x", "y", "z", 999)
        assert agg_3d.get("x", "y", "z") == 999
        print("✓ ThreeDimensionalAggregation 正常工作")
        
        edit = OntologyEdit("Product", "p001", "CREATE")
        assert edit.is_create_operation()
        print("✓ OntologyEdit 正常工作")
        
        return True
    except Exception as e:
        print(f"✗ API 导入失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_type_properties():
    """测试类型属性和方法"""
    print("\n测试类型属性和方法...")
    
    try:
        from sthg_ontology_base_plus.function.api import (
            Attachment, Optional, Range, Object, OntologyEdit, ThreeDimensionalAggregation
        )
        
        # 测试 Attachment 属性
        att = Attachment("document.pdf", b"PDF content", "application/pdf")
        assert att.filename == "document.pdf"
        assert att.content_type == "application/pdf"
        assert att.size == 11
        print("✓ Attachment 属性正常")
        
        # 测试 Optional 方法
        opt = Optional(42)
        doubled = opt.map(lambda x: x * 2)
        assert doubled.value == 84
        print("✓ Optional map 方法正常")
        
        filtered = opt.filter(lambda x: x > 40)
        assert filtered.has_value
        print("✓ Optional filter 方法正常")
        
        # 测试 Range 方法
        range_val = Range(1, 10)
        assert range_val.contains(5)
        assert not range_val.contains(15)
        print("✓ Range contains 方法正常")
        
        # 测试 Object 方法
        obj = Object("User", "u001", {"name": "张三", "age": 30})
        assert obj.get_property("name") == "张三"
        obj.set_property("city", "北京")
        assert obj.has_property("city")
        print("✓ Object 属性方法正常")
        
        # 测试 OntologyEdit 方法
        edit = OntologyEdit("User", "u001", "UPDATE", {
            "age": {"new_value": 31, "old_value": 30}
        })
        assert edit.get_new_value("age") == 31
        assert edit.get_old_value("age") == 30
        assert edit.is_update_operation()
        print("✓ OntologyEdit 方法正常")
        
        # 测试 ThreeDimensionalAggregation 方法
        data = {("A", "X", "2023"): 100, ("A", "Y", "2023"): 200}
        agg_3d = ThreeDimensionalAggregation("产品", "地区", "年份", data)
        assert agg_3d.get_x_keys() == {"A"}
        assert agg_3d.get_y_keys() == {"X", "Y"}
        assert agg_3d.get_z_keys() == {"2023"}
        
        # 测试切片功能
        xy_slice = agg_3d.get_slice_xy("2023")
        assert len(xy_slice) == 2
        print("✓ ThreeDimensionalAggregation 方法正常")
        
        return True
    except Exception as e:
        print(f"✗ 属性方法测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_error_handling():
    """测试错误处理"""
    print("\n测试错误处理...")
    
    try:
        from sthg_ontology_base_plus.function.api import Byte, Short, Decimal, ValidationError
        
        # 测试 Byte 范围错误
        try:
            Byte(300)  # 超出范围
            assert False, "应该抛出异常"
        except ValidationError:
            print("✓ Byte 范围验证正常")
        
        # 测试 Short 范围错误
        try:
            Short(50000)  # 超出范围
            assert False, "应该抛出异常"
        except ValidationError:
            print("✓ Short 范围验证正常")
        
        # 测试 Decimal 格式错误
        try:
            Decimal("invalid_number")
            assert False, "应该抛出异常"
        except ValidationError:
            print("✓ Decimal 格式验证正常")
        
        return True
    except Exception as e:
        print(f"✗ 错误处理测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_json_serialization():
    """测试JSON序列化"""
    print("\n测试JSON序列化...")
    
    try:
        from sthg_ontology_base_plus.function.api import (
            Integer, Attachment, Decimal, Optional, ThreeDimensionalAggregation
        )
        
        # 测试基础类型序列化
        int_val = Integer(42)
        json_data = int_val.to_json()
        restored = Integer.from_json(json_data)
        assert restored.value == 42
        print("✓ Integer JSON序列化正常")
        
        # 测试 Attachment 序列化
        att = Attachment("test.txt", b"Hello World", "text/plain")
        json_data = att.to_json()
        restored = Attachment.from_json(json_data)
        assert restored.filename == "test.txt"
        assert restored.content == b"Hello World"
        print("✓ Attachment JSON序列化正常")
        
        # 测试 Decimal 序列化
        dec = Decimal("123.456789")
        json_data = dec.to_json()
        restored = Decimal.from_json(json_data)
        assert str(restored.value) == "123.456789"
        print("✓ Decimal JSON序列化正常")
        
        # 测试 Optional 序列化
        opt = Optional("test value")
        json_data = opt.to_json()
        restored = Optional.from_json(json_data)
        assert restored.value == "test value"
        print("✓ Optional JSON序列化正常")
        
        # 测试 ThreeDimensionalAggregation 序列化
        agg = ThreeDimensionalAggregation("X", "Y", "Z", {("a", "b", "c"): 100})
        json_data = agg.to_json()
        restored = ThreeDimensionalAggregation.from_json(json_data)
        assert restored.get("a", "b", "c") == 100
        print("✓ ThreeDimensionalAggregation JSON序列化正常")
        
        return True
    except Exception as e:
        print(f"✗ JSON序列化测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("开始完整类型系统测试...")
    
    tests = [
        test_direct_imports, 
        test_api_imports,
        test_type_properties,
        test_error_handling,
        test_json_serialization
    ]
    passed = sum(1 for test in tests if test())
    
    print(f"\n测试结果: {passed}/{len(tests)} 通过")
    
    if passed == len(tests):
        print("🎉 所有类型系统功能正常！")
        print("\n已实现的新类型:")
        print("- Attachment: 文件附件类型")
        print("- Byte: 8位有符号整数 (-128到127)")
        print("- Short: 16位有符号整数 (-32768到32767)")
        print("- Decimal: 高精度十进制数")
        print("- Optional: 可选值类型，支持函数式操作")
        print("- ThreeDimensionalAggregation: 三维聚合，支持切片操作")
        print("- OntologyEdit: 本体编辑操作，支持变更跟踪")
    else:
        print("⚠️  部分测试失败")

if __name__ == "__main__":
    main()