#!/usr/bin/env python3
"""
检查content.json的实际结构
"""

import json
import zipfile
import os

def check_content_structure():
    """检查content.json结构"""
    test_files = [
        'output/最终测试-20251018-223019.xmind',
        'output/markdown_test.xmind',
        'output/text_test.xmind'
    ]
    
    for file_path in test_files:
        if not os.path.exists(file_path):
            print(f"文件不存在: {file_path}")
            continue
            
        try:
            print(f'\n=== 检查content.json结构: {file_path} ===')
            
            with zipfile.ZipFile(file_path, 'r') as zf:
                if 'content.json' in zf.namelist():
                    content_data = zf.read('content.json').decode('utf-8')
                    content = json.loads(content_data)
                    
                    print(f'content.json类型: {type(content).__name__}')
                    
                    if isinstance(content, list):
                        print(f'数组长度: {len(content)}')
                        if content:
                            # 检查第一个元素
                            first_item = content[0]
                            print(f'第一个元素类型: {type(first_item).__name__}')
                            if isinstance(first_item, dict):
                                print('第一个元素的键:')
                                for key in first_item.keys():
                                    print(f'  - {key}')
                                    
                                # 检查主要结构
                                print(f'工作表标题: {first_item.get("title", "unknown")}')
                                
                                if 'rootTopic' in first_item:
                                    root_topic = first_item['rootTopic']
                                    print(f'根主题标题: {root_topic.get("title", "unknown")}')
                                    
                                    if 'children' in root_topic and isinstance(root_topic['children'], dict):
                                        if 'attached' in root_topic['children'] and isinstance(root_topic['children']['attached'], list):
                                            attached_children = root_topic['children']['attached']
                                            print(f'直接子主题数量: {len(attached_children)}')
                                            
                                            # 显示前几个子主题
                                            for i, child in enumerate(attached_children[:3]):
                                                print(f'  子主题{i+1}: {child.get("title", "unknown")}')
                                        else:
                                            print('没有attached子主题')
                                    else:
                                        print('根主题没有children或children格式不正确')
                                else:
                                    print('工作表中没有rootTopic')
                    elif isinstance(content, dict):
                        print('顶层键:')
                        for key in content.keys():
                            print(f'  - {key}')
                    
                    # 保存完整的content.json用于调试
                    debug_file = f"debug_{os.path.basename(file_path).replace('.xmind', '.json')}"
                    with open(debug_file, 'w', encoding='utf-8') as f:
                        json.dump(content, f, ensure_ascii=False, indent=2)
                    print(f'完整的content.json已保存到: {debug_file}')
                    
        except Exception as e:
            print(f'检查失败: {e}')

if __name__ == "__main__":
    check_content_structure()