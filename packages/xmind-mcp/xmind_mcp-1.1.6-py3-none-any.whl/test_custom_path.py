#!/usr/bin/env python3
"""测试指定路径创建XMind文件"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from xmind_core_engine import XMindCoreEngine

def test_create_with_custom_path():
    """测试指定路径创建思维导图"""
    print("=== 测试指定路径创建思维导图 ===")
    
    # 创建核心引擎实例
    engine = XMindCoreEngine()
    
    # 测试数据
    title = "自定义路径测试"
    topics_json = '[{"title": "主题1", "children": [{"title": "子主题1", "children": []}]}, {"title": "主题2", "children": []}]'
    
    # 指定输出路径
    custom_output_path = "test_output/自定义路径测试.xmind"
    
    print(f"标题: {title}")
    print(f"自定义输出路径: {custom_output_path}")
    
    # 调用核心引擎创建
    result = engine.create_mind_map(title, topics_json, custom_output_path)
    
    print(f"返回结果: {result}")
    
    # 验证文件是否创建
    if result.get("status") == "success":
        output_file = result.get("filename")
        if os.path.exists(output_file):
            file_size = os.path.getsize(output_file)
            print(f"✅ 文件创建成功！大小: {file_size} 字节")
            print(f"文件路径: {output_file}")
            print(f"绝对路径: {os.path.abspath(output_file)}")
        else:
            print(f"❌ 文件未找到: {output_file}")
    else:
        print(f"❌ 创建失败: {result.get('error')}")

def test_create_with_relative_path():
    """测试相对路径创建"""
    print("\n=== 测试相对路径创建 ===")
    
    engine = XMindCoreEngine()
    
    title = "相对路径测试"
    topics_json = '[{"title": "相对路径主题", "children": []}]'
    
    # 测试不同的相对路径
    test_paths = [
        "output/相对路径1.xmind",
        "test_output/相对路径2.xmind", 
        "./output/相对路径3.xmind",
        "深层/目录/测试/相对路径4.xmind"
    ]
    
    for i, path in enumerate(test_paths):
        print(f"\n测试路径 {i+1}: {path}")
        result = engine.create_mind_map(f"{title}_{i+1}", topics_json, path)
        
        if result.get("status") == "success":
            output_file = result.get("filename")
            if os.path.exists(output_file):
                print(f"✅ 成功: {output_file}")
            else:
                print(f"❌ 文件不存在: {output_file}")
        else:
            print(f"❌ 失败: {result.get('error')}")

if __name__ == "__main__":
    test_create_with_custom_path()
    test_create_with_relative_path()