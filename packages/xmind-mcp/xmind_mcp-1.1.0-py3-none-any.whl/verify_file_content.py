#!/usr/bin/env python3
"""
验证XMind文件内容完整性
"""

import json
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from xmind_core_engine import read_xmind_file as core_read_xmind_file

def verify_file_content():
    """验证XMind文件内容"""
    test_files = [
        'output/最终测试-20251018-223019.xmind',
        'output/markdown_test.xmind', 
        'output/text_test.xmind'
    ]
    
    all_success = True
    
    for file_path in test_files:
        if os.path.exists(file_path):
            try:
                print(f'=== 读取文件内容: {file_path} ===')
                result = core_read_xmind_file(file_path)
                
                print(f'状态: {result.get("status", "unknown")}')
                print(f'标题: {result.get("title", "unknown")}')
                print(f'主题数: {len(result.get("topics", []))}')
                
                # 显示前几个主题
                topics = result.get('topics', [])
                if topics:
                    print('前3个主题:')
                    for i, topic in enumerate(topics[:3]):
                        print(f'  {i+1}. {topic.get("title", "unknown")}')
                
                # 检查状态
                if result.get('status') != 'success':
                    print(f'[ERROR] 文件状态异常: {result.get("status")}')
                    all_success = False
                else:
                    print('[SUCCESS] 文件内容正常')
                    
                print()
                
            except Exception as e:
                print(f'[ERROR] 读取 {file_path} 时出错: {e}')
                all_success = False
                print()
        else:
            print(f'[ERROR] 文件不存在: {file_path}')
            all_success = False
    
    return all_success

if __name__ == "__main__":
    success = verify_file_content()
    if success:
        print('[SUCCESS] 所有文件内容验证通过!')
    else:
        print('[ERROR] 部分文件验证失败!')
    sys.exit(0 if success else 1)