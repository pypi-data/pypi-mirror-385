#!/usr/bin/env python3
"""测试MCP函数调试脚本"""

import logging
import json
import os
from xmind_mcp_server import create_mind_map

# 配置日志显示
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_mcp_create():
    """测试MCP创建功能"""
    title = '直接测试MCP功能-最终版'
    topics = ['功能验证', 'MCP集成', '最终测试']
    
    print(f'测试标题: {title}')
    print(f'测试主题: {topics}')
    
    try:
        result = create_mind_map(None, title, topics)
        print('结果:', result)
        
        # 解析结果
        result_dict = json.loads(result)
        print('解析结果:', result_dict)
        
        # 检查文件是否存在
        filename = result_dict.get('filename', '')
        print(f'文件名: {filename}')
        if filename:
            exists = os.path.exists(filename)
            print(f'文件存在: {exists}')
            if exists:
                file_size = os.path.getsize(filename)
                print(f'文件大小: {file_size} 字节')
        else:
            print('无文件名')
        
        return result_dict
        
    except Exception as e:
        print(f'错误: {e}')
        import traceback
        traceback.print_exc()
        return None

if __name__ == '__main__':
    test_mcp_create()