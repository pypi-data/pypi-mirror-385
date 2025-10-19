#!/usr/bin/env python3
"""
检查生成的XMind文件结构是否正确
"""

import json
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from xmind_mcp_server import analyze_mind_map

def check_xmind_files():
    """检查output目录中的XMind文件结构"""
    output_dir = "output"
    
    # 获取所有XMind文件
    xmind_files = []
    for file in os.listdir(output_dir):
        if file.endswith('.xmind'):
            xmind_files.append(os.path.join(output_dir, file))
    
    print(f"找到 {len(xmind_files)} 个XMind文件:")
    
    # 测试几个代表性的文件
    test_files = [
        'output/最终测试-20251018-223019.xmind',
        'output/markdown_test.xmind', 
        'output/text_test.xmind',
        'output/html_test.xmind',
        'output/MCP测试创建.xmind'
    ]
    
    for file_path in test_files:
        if os.path.exists(file_path):
            try:
                print(f'\n=== 分析文件: {file_path} ===')
                result = analyze_mind_map(None, file_path)
                data = json.loads(result)
                
                print(f'状态: {data.get("status", "unknown")}')
                print(f'标题: {data.get("title", "unknown")}')
                print(f'根节点: {data.get("root_topic", "unknown")}')
                print(f'总节点数: {data.get("total_nodes", 0)}')
                print(f'叶子节点数: {data.get("leaf_nodes", 0)}')
                print(f'深度: {data.get("depth", 0)}')
                print(f'复杂度: {data.get("complexity", "unknown")}')
                
                if 'error' in data:
                    print(f'错误: {data["error"]}')
                    return False
                elif data.get('status') != 'success':
                    print(f'警告: 文件状态不是success')
                    return False
                    
            except Exception as e:
                print(f'分析 {file_path} 时出错: {e}')
                return False
        else:
            print(f'文件不存在: {file_path}')
            return False
    
    print(f'\n✅ 所有测试文件结构检查通过!')
    return True

if __name__ == "__main__":
    success = check_xmind_files()
    sys.exit(0 if success else 1)