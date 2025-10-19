#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试MCP服务器功能
"""

import sys
import os
import json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 模拟Context类
class MockContext:
    def __init__(self):
        pass

# 导入MCP服务器函数
from xmind_mcp_server import read_xmind_file, create_mind_map, analyze_mind_map, list_xmind_files

def test_mcp_server():
    """测试MCP服务器功能"""
    print("🚀 开始测试MCP服务器...")
    
    ctx = MockContext()
    
    # 测试读取文件
    test_files = [
        "output/最终测试-20251018-223019.xmind",
        "output/markdown_test.xmind", 
        "output/text_test.xmind"
    ]
    
    for filepath in test_files:
        if os.path.exists(filepath):
            print(f"\n📁 测试读取: {filepath}")
            
            try:
                result = read_xmind_file(ctx, filepath)
                result_data = json.loads(result)
                print(f"读取状态: {result_data.get('status')}")
                
                if result_data.get('status') == 'success':
                    data = result_data.get('data', {})
                    print(f"标题: {data.get('title')}")
                    print(f"总节点数: {data.get('total_nodes')}")
                    print(f"最大深度: {data.get('max_depth')}")
            except Exception as e:
                print(f"读取错误: {e}")
                print(f"原始结果: {result}")
    
    # 测试分析文件
    print(f"\n🔍 测试分析文件...")
    for filepath in test_files:
        if os.path.exists(filepath):
            print(f"\n📊 分析: {filepath}")
            
            try:
                result = analyze_mind_map(ctx, filepath)
                result_data = json.loads(result)
                print(f"分析状态: {result_data.get('status')}")
                
                if result_data.get('status') == 'success':
                    print(f"总节点数: {result_data.get('total_nodes')}")
                    print(f"叶子节点: {result_data.get('leaf_nodes')}")
                    print(f"分支数: {result_data.get('branch_count')}")
            except Exception as e:
                print(f"分析错误: {e}")
                print(f"原始结果: {result}")
    
    # 测试创建文件
    print(f"\n📝 测试创建文件...")
    topics_json = json.dumps([
        {"title": "测试主题1"},
        {"title": "测试主题2", "children": [{"title": "子主题2.1"}]}
    ], ensure_ascii=False)
    
    try:
        result = create_mind_map(ctx, "测试MCP创建", topics_json)
        result_data = json.loads(result)
        print(f"创建状态: {result_data.get('status')}")
        if result_data.get('status') == 'success':
            print(f"文件名: {result_data.get('filename')}")
            print(f"主题数: {result_data.get('topics_count')}")
        else:
            print(f"创建错误: {result_data.get('error')}")
    except Exception as e:
        print(f"创建错误: {e}")
        print(f"原始结果: {result}")
    
    # 测试列出文件
    print(f"\n📋 测试列出文件...")
    try:
        result = list_xmind_files(ctx, "output")
        result_data = json.loads(result)
        print(f"列出状态: {result_data.get('status')}")
        if result_data.get('status') == 'success':
            print(f"文件数量: {result_data.get('file_count')}")
            files = result_data.get('files', [])
            print(f"找到的文件:")
            for file_info in files[:5]:  # 只显示前5个
                print(f"  - {file_info.get('name')}")
    except Exception as e:
        print(f"列出错误: {e}")
        print(f"原始结果: {result}")

if __name__ == "__main__":
    test_mcp_server()