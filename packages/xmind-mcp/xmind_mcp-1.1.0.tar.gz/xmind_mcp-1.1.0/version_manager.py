#!/usr/bin/env python3
"""
版本管理工具
统一管理项目中所有版本号
"""

import re
import os
from pathlib import Path

# 版本号配置
VERSION = "1.0.9"
VERSION_TUPLE = (1, 0, 9)

# 需要更新版本号的文件列表
VERSION_FILES = {
    "pyproject.toml": {
        "pattern": r'version = "([0-9.]+)"',
        "replacement": f'version = "{VERSION}"'
    },
    "_version.py": {
        "pattern": r"__version__ = version = '([0-9.]+)'",
        "replacement": f"__version__ = version = '{VERSION}'",
        "patterns": [
            (r"__version__ = version = '([0-9.]+)'", f"__version__ = version = '{VERSION}'"),
            (r"__version_tuple__ = version_tuple = \(([0-9, ]+)\)", f"__version_tuple__ = version_tuple = {VERSION_TUPLE}")
        ]
    },
    "package.json": {
        "pattern": r'"version": "([0-9.]+)"',
        "replacement": f'"version": "{VERSION}"'
    }
}

def update_file_version(file_path, patterns):
    """更新单个文件的版本号"""
    if not os.path.exists(file_path):
        print(f"文件不存在: {file_path}")
        return False
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # 处理多种模式（如_version.py）
        if isinstance(patterns, dict) and 'patterns' in patterns:
            for pattern, replacement in patterns['patterns']:
                content = re.sub(pattern, replacement, content)
        else:
            # 单一模式
            pattern = patterns['pattern']
            replacement = patterns['replacement']
            content = re.sub(pattern, replacement, content)
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"[SUCCESS] 已更新 {file_path}")
            return True
        else:
            print(f"ℹ️  {file_path} 无需更新")
            return False
            
    except Exception as e:
        print(f"[ERROR] 更新 {file_path} 失败: {e}")
        return False

def update_all_versions():
    """更新所有文件的版本号"""
    print(f"开始更新版本号到 {VERSION}")
    
    updated_files = []
    for file_path, patterns in VERSION_FILES.items():
        if update_file_version(file_path, patterns):
            updated_files.append(file_path)
    
    if updated_files:
        print(f"\n[SUCCESS] 成功更新 {len(updated_files)} 个文件:")
        for file in updated_files:
            print(f"  - {file}")
    else:
        print("\n[INFO] 所有文件版本号已是最新")
    
    return updated_files

def get_current_versions():
    """获取当前各文件的版本号"""
    print("[INFO] 当前版本号信息:")
    
    for file_path, patterns in VERSION_FILES.items():
        if not os.path.exists(file_path):
            print(f"  [ERROR] {file_path}: 文件不存在")
            continue
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 提取版本号
            pattern = patterns.get('pattern', '')
            if 'patterns' in patterns:
                pattern = patterns['patterns'][0][0]  # 使用第一个模式
            
            match = re.search(pattern, content)
            if match:
                version = match.group(1)
                print(f"  [INFO] {file_path}: {version}")
            else:
                print(f"  [WARNING] {file_path}: 未找到版本号")
                
        except Exception as e:
            print(f"  [ERROR] {file_path}: 读取失败 - {e}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='版本管理工具')
    parser.add_argument('--show', action='store_true', help='显示当前版本号')
    parser.add_argument('--update', action='store_true', help='更新所有版本号')
    parser.add_argument('--version', type=str, help='设置新版本号（格式：x.x.x）')
    
    args = parser.parse_args()
    
    if args.version:
        # 验证版本号格式
        if re.match(r'^\d+\.\d+\.\d+$', args.version):
            VERSION = args.version
            VERSION_TUPLE = tuple(map(int, VERSION.split('.')))
            # 更新VERSION_FILES中的replacement
            for file_info in VERSION_FILES.values():
                if 'replacement' in file_info:
                    file_info['replacement'] = file_info['replacement'].replace(
                        file_info['replacement'].split('"')[1] if '"' in file_info['replacement'] else 
                        file_info['replacement'].split("'")[1], VERSION
                    )
            print(f"[INFO] 版本号已设置为: {VERSION}")
        else:
            print("[ERROR] 版本号格式错误，应为 x.x.x 格式")
            exit(1)
    
    if args.show:
        get_current_versions()
    elif args.update:
        update_all_versions()
    else:
        # 默认显示当前版本并询问是否更新
        get_current_versions()
        print(f"\n[INFO] 当前工具版本: {VERSION}")
        response = input("是否更新到当前版本号？(y/N): ")
        if response.lower() == 'y':
            update_all_versions()