#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试xmind_mcp_server.py中的函数
"""

import sys
import os
import json

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 导入xmind_mcp_server中的函数
try:
    from xmind_mcp_server import read_xmind_file, analyze_mind_map, create_mind_map
    print("✓ 成功导入xmind_mcp_server函数")
except ImportError as e:
    print(f"✗ 导入失败: {e}")
    sys.exit(1)

def test_read_xmind_file():
    """测试读取XMind文件功能"""
    print("\n=== 测试 read_xmind_file 功能 ===")
    
    test_files = [
        "output/最终测试-20251018-223019.xmind",
        "output/markdown_test.xmind",
        "output/text_test.xmind"
    ]
    
    for file_path in test_files:
        if os.path.exists(file_path):
            print(f"\n测试文件: {file_path}")
            try:
                result = read_xmind_file(file_path)
                print(f"状态: {result.get('status', 'unknown')}")
                print(f"标题: {result.get('title', 'unknown')}")
                print(f"主题数量: {len(result.get('topics', []))}")
                
                if 'error' in result:
                    print(f"错误: {result['error']}")
                
                # 显示前几个主题
                topics = result.get('topics', [])
                if topics:
                    print("前3个主题:")
                    for i, topic in enumerate(topics[:3]):
                        print(f"  {i+1}. {topic.get('title', 'unknown')}")
                        
            except Exception as e:
                print(f"读取失败: {e}")
        else:
            print(f"文件不存在: {file_path}")

def test_analyze_mind_map():
    """测试分析思维导图功能"""
    print("\n=== 测试 analyze_mind_map 功能 ===")
    
    test_files = [
        "output/最终测试-20251018-223019.xmind",
        "output/markdown_test.xmind",
        "output/text_test.xmind"
    ]
    
    for file_path in test_files:
        if os.path.exists(file_path):
            print(f"\n分析文件: {file_path}")
            try:
                result = analyze_mind_map(file_path)
                print(f"状态: {result.get('status', 'unknown')}")
                print(f"标题: {result.get('title', 'unknown')}")
                print(f"总节点数: {result.get('total_nodes', 'unknown')}")
                print(f"叶子节点数: {result.get('leaf_nodes', 'unknown')}")
                print(f"深度: {result.get('depth', 'unknown')}")
                
                if 'error' in result:
                    print(f"错误: {result['error']}")
                    
            except Exception as e:
                print(f"分析失败: {e}")
        else:
            print(f"文件不存在: {file_path}")

def test_create_mind_map():
    """测试创建思维导图功能"""
    print("\n=== 测试 create_mind_map 功能 ===")
    
    # 简单的测试数据
    title = "测试创建"
    topics = ["主题1", "主题2", "主题3"]
    
    output_file = "output/test_server_create.xmind"
    
    try:
        result = create_mind_map(title, topics)
        print(f"创建结果: {result}")
        
        if result.get('status') == 'success':
            print(f"✓ 成功创建文件: {output_file}")
            
            # 验证创建的文件
            if os.path.exists(output_file):
                read_result = read_xmind_file(output_file)
                print(f"验证读取 - 标题: {read_result.get('title', 'unknown')}")
                print(f"验证读取 - 主题数量: {len(read_result.get('topics', []))}")
            else:
                print("✗ 文件未创建")
        else:
            print(f"✗ 创建失败: {result.get('error', 'unknown error')}")
            
    except Exception as e:
        print(f"创建异常: {e}")

if __name__ == "__main__":
    print("开始测试xmind_mcp_server.py功能...")
    
    test_read_xmind_file()
    test_analyze_mind_map()
    test_create_mind_map()
    
    print("\n=== 测试完成 ===")