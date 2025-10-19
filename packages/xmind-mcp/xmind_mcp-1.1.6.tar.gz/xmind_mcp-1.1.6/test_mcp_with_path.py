#!/usr/bin/env python3
"""测试MCP指定路径功能"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from xmind_mcp_server import create_mind_map

def test_mcp_create_with_path():
    """测试MCP创建思维导图并指定路径"""
    print("=== 测试MCP指定路径创建思维导图 ===")
    
    # 测试数据
    title = "MCP指定路径测试"
    topics_json = '[{"title": "主题1", "children": [{"title": "子主题1", "children": []}]}, {"title": "主题2", "children": []}]'
    
    # 测试1: 不指定路径（默认行为）
    print("\n--- 测试1: 默认路径 ---")
    result1 = create_mind_map(None, title + "_默认", topics_json)
    print(f"结果: {result1}")
    
    # 测试2: 指定相对路径
    print("\n--- 测试2: 指定相对路径 ---")
    custom_path = "test_output/mcp自定义路径.xmind"
    result2 = create_mind_map(None, title + "_自定义", topics_json, custom_path)
    print(f"结果: {result2}")
    
    # 测试3: 指定绝对路径
    print("\n--- 测试3: 指定绝对路径 ---")
    abs_path = os.path.abspath("test_output/mcp绝对路径.xmind")
    result3 = create_mind_map(None, title + "_绝对", topics_json, abs_path)
    print(f"结果: {result3}")
    
    # 测试4: 测试深层目录
    print("\n--- 测试4: 深层目录 ---")
    deep_path = "test_output/深层/目录/结构/mcp深层测试.xmind"
    result4 = create_mind_map(None, title + "_深层", topics_json, deep_path)
    print(f"结果: {result4}")

if __name__ == "__main__":
    test_mcp_create_with_path()