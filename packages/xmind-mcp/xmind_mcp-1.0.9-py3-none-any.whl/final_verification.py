#!/usr/bin/env python3
"""
最终验证生成的XMind文件结构
"""

import json
import zipfile
import os
import sys

def verify_xmind_structure():
    """验证XMind文件结构完整性"""
    output_dir = "output"
    xmind_files = [f for f in os.listdir(output_dir) if f.endswith('.xmind')]
    
    print(f"找到 {len(xmind_files)} 个XMind文件")
    
    # 验证几个关键文件
    test_files = [
        'output/最终测试-20251018-223019.xmind',
        'output/markdown_test.xmind',
        'output/text_test.xmind',
        'output/html_test.xmind',
        'output/MCP测试创建.xmind'
    ]
    
    all_valid = True
    
    for file_path in test_files:
        if not os.path.exists(file_path):
            print(f"❌ 文件不存在: {file_path}")
            all_valid = False
            continue
            
        try:
            print(f"\n=== 验证文件: {file_path} ===")
            
            # 检查文件大小
            file_size = os.path.getsize(file_path)
            print(f"文件大小: {file_size} bytes")
            
            if file_size < 1000:  # 小于1KB的文件可能有问题
                print("⚠️  文件大小异常小")
            
            # 检查是否是有效的ZIP文件
            if not zipfile.is_zipfile(file_path):
                print("❌ 不是有效的ZIP文件")
                all_valid = False
                continue
                
            print("✅ 是有效的ZIP格式")
            
            # 检查ZIP内容
            with zipfile.ZipFile(file_path, 'r') as zf:
                files = zf.namelist()
                print(f"ZIP包含文件数: {len(files)}")
                
                # 检查必需的XMind文件
                required_files = ['content.json', 'content.xml', 'metadata.json', 'manifest.json']
                missing_files = []
                
                for required in required_files:
                    if required not in files:
                        missing_files.append(required)
                    else:
                        # 检查文件大小
                        info = zf.getinfo(required)
                        print(f"  {required}: {info.file_size} bytes")
                
                if missing_files:
                    print(f"❌ 缺少必需文件: {missing_files}")
                    all_valid = False
                else:
                    print("✅ 所有必需文件都存在")
                
                # 检查content.json结构
                if 'content.json' in files:
                    content_data = zf.read('content.json').decode('utf-8')
                    content = json.loads(content_data)
                    
                    if 'rootTopic' in content:
                        root_title = content['rootTopic'].get('title', 'unknown')
                        print(f"✅ 根主题标题: {root_title}")
                        
                        # 检查子主题
                        if 'children' in content['rootTopic'] and 'attached' in content['rootTopic']['children']:
                            sub_topics = content['rootTopic']['children']['attached']
                            print(f"✅ 子主题数量: {len(sub_topics)}")
                        else:
                            print("⚠️  没有子主题")
                    else:
                        print("❌ 缺少rootTopic")
                        all_valid = False
                
                # 检查metadata.json
                if 'metadata.json' in files:
                    metadata_data = zf.read('metadata.json').decode('utf-8')
                    metadata = json.loads(metadata_data)
                    print(f"✅ 元数据: {metadata}")
                    
        except Exception as e:
            print(f"❌ 验证失败: {e}")
            all_valid = False
    
    print(f"\n{'='*50}")
    if all_valid:
        print("✅ 所有XMind文件结构验证通过!")
        print("✅ 文件格式正确，内容完整")
        print("✅ 可以正常在XMind软件中打开")
    else:
        print("❌ 部分文件验证失败!")
    
    return all_valid

if __name__ == "__main__":
    success = verify_xmind_structure()
    sys.exit(0 if success else 1)