#!/usr/bin/env python3
"""测试路径问题的脚本"""

import os
import json
from xmind_core_engine import create_mind_map, convert_to_xmind

def test_core_engine_paths():
    """测试核心引擎的路径行为"""
    print("=== 测试核心引擎路径行为 ===")
    print(f"当前工作目录: {os.getcwd()}")
    
    # 测试1: 核心引擎create_mind_map
    print("\n--- 测试 create_mind_map ---")
    result1 = create_mind_map('核心引擎创建测试', '[{"title": "测试主题", "subtopics": [{"title": "子主题1"}, {"title": "子主题2"}]}]')
    print(f"创建结果: {json.dumps(result1, ensure_ascii=False, indent=2)}")
    
    # 测试2: 核心引擎convert_to_xmind
    print("\n--- 测试 convert_to_xmind ---")
    # 创建一个测试文件
    test_content = "# 测试标题\n\n## 子标题1\n内容1\n\n## 子标题2\n内容2"
    with open('test_md.md', 'w', encoding='utf-8') as f:
        f.write(test_content)
    
    result2 = convert_to_xmind('test_md.md')
    print(f"转换结果: {json.dumps(result2, ensure_ascii=False, indent=2)}")
    
    # 清理测试文件
    if os.path.exists('test_md.md'):
        os.remove('test_md.md')
    
    # 检查文件创建位置
    print(f"\noutput目录是否存在: {os.path.exists('output')}")
    if os.path.exists('output'):
        files = os.listdir('output')
        print(f"output目录内容: {files}")
        
        # 检查新创建的文件
        for file in files:
            if '核心引擎创建测试' in file or 'test_md' in file:
                full_path = os.path.join('output', file)
                print(f"新文件路径: {full_path}")
                print(f"绝对路径: {os.path.abspath(full_path)}")

if __name__ == "__main__":
    test_core_engine_paths()