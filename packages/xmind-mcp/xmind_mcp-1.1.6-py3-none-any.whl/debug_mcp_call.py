#!/usr/bin/env python3
"""调试MCP调用参数"""

import json

def debug_mcp_parameters():
    """调试MCP参数类型"""
    
    # 测试不同的参数类型
    test_cases = [
        {
            "name": "字符串JSON",
            "topics_json": '[{"title": "主题1", "children": []}]',
            "expected_type": "str"
        },
        {
            "name": "字典对象", 
            "topics_json": [{"title": "主题1", "children": []}],
            "expected_type": "list"
        }
    ]
    
    for case in test_cases:
        print(f"\n--- {case['name']} ---")
        print(f"topics_json类型: {type(case['topics_json'])}")
        print(f"topics_json内容: {case['topics_json']}")
        
        # 模拟MCP服务器中的类型检查
        if isinstance(case['topics_json'], (dict, list)):
            print("✅ 检测到Python对象，将转换为JSON字符串")
            topics_json_str = json.dumps(case['topics_json'], ensure_ascii=False)
            print(f"转换后的字符串: {topics_json_str}")
            print(f"转换后的类型: {type(topics_json_str)}")
        else:
            print("✅ 已经是字符串类型")
            topics_json_str = str(case['topics_json'])
            print(f"转换后的类型: {type(topics_json_str)}")

if __name__ == "__main__":
    debug_mcp_parameters()