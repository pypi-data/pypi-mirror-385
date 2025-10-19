#!/usr/bin/env python3
"""调试MCP路径问题的脚本"""

import os
import sys
import json

# 模拟MCP服务器环境
print("=== 模拟MCP服务器环境 ===")
print(f"当前工作目录: {os.getcwd()}")
print(f"脚本文件路径: {__file__}")
print(f"脚本所在目录: {os.path.dirname(os.path.abspath(__file__))}")

# 测试相对路径行为
print(f"\n相对路径 'output' 测试:")
print(f"os.path.exists('output'): {os.path.exists('output')}")
print(f"os.path.abspath('output'): {os.path.abspath('output')}")

# 测试绝对路径行为
print(f"\n绝对路径测试:")
current_dir = os.getcwd()
output_dir = os.path.join(current_dir, "output")
print(f"os.path.join(current_dir, 'output'): {output_dir}")
print(f"os.path.exists(output_dir): {os.path.exists(output_dir)}")

# 测试核心引擎导入
print(f"\n=== 测试核心引擎导入 ===")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    from xmind_core_engine import get_engine, create_mind_map
    engine = get_engine()
    print("核心引擎导入成功")
    
    # 测试引擎的路径行为
    print(f"\n=== 测试核心引擎路径行为 ===")
    result = create_mind_map('调试测试', '[{"title": "测试主题"}]')
    print(f"创建结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
    
    # 检查文件创建位置
    if os.path.exists('output'):
        files = [f for f in os.listdir('output') if '调试测试' in f]
        if files:
            print(f"创建的文件: {files[0]}")
            print(f"文件绝对路径: {os.path.abspath(os.path.join('output', files[0]))}")
    
except Exception as e:
    print(f"核心引擎导入失败: {e}")
    import traceback
    traceback.print_exc()