#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
直接测试核心引擎功能
"""

import sys
import os
import json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from xmind_core_engine import get_engine

def test_engine():
    """测试核心引擎"""
    print("🚀 开始测试核心引擎...")
    
    # 获取引擎实例
    engine = get_engine()
    print(f"✅ 引擎实例: {engine}")
    
    # 测试读取文件
    test_files = [
        "output/最终测试-20251018-223019.xmind",
        "output/markdown_test.xmind", 
        "output/text_test.xmind"
    ]
    
    for filepath in test_files:
        if os.path.exists(filepath):
            print(f"\n📁 测试文件: {filepath}")
            
            # 读取文件
            result = engine.read_xmind_file(filepath)
            print(f"读取状态: {result.get('status')}")
            
            if result.get('status') == 'success':
                data = result.get('data', {})
                print(f"标题: {data.get('title')}")
                print(f"总节点数: {data.get('total_nodes')}")
                print(f"最大深度: {data.get('max_depth')}")
                
                # 分析文件
                analysis = engine.analyze_mind_map(filepath)
                print(f"分析状态: {analysis.get('status')}")
                if analysis.get('status') == 'success':
                    print(f"叶子节点: {analysis.get('leaf_nodes')}")
                    print(f"分支数: {analysis.get('branch_count')}")
            else:
                print(f"错误: {result.get('error')}")
    
    # 测试创建文件
    print(f"\n📝 测试创建文件...")
    topics = [
        {"title": "测试主题1"},
        {"title": "测试主题2", "children": [{"title": "子主题2.1"}]}
    ]
    
    result = engine.create_mind_map("测试引擎创建", json.dumps(topics))
    print(f"创建状态: {result.get('status')}")
    if result.get('status') == 'success':
        print(f"文件名: {result.get('filename')}")
        print(f"主题数: {result.get('topics_count')}")
    else:
        print(f"错误: {result.get('error')}")

if __name__ == "__main__":
    test_engine()