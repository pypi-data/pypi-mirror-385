#!/usr/bin/env python3
"""测试uvx行为对路径的影响"""

import os
import sys

def print_path_info():
    """打印路径信息"""
    print("=== 路径信息分析 ===")
    print(f"当前工作目录: {os.getcwd()}")
    print(f"__file__: {__file__}")
    print(f"脚本目录: {os.path.dirname(os.path.abspath(__file__))}")
    print(f"sys.executable: {sys.executable}")
    print(f"sys.prefix: {sys.prefix}")
    
    # 检查是否存在uvx缓存路径
    if 'cache' in sys.executable:
        print("⚠️  警告：在uvx缓存环境中运行！")
        cache_dir = os.path.dirname(sys.executable)
        print(f"缓存目录: {cache_dir}")
        
        # 检查相对路径行为
        test_file = "output/test_file.txt"
        print(f"\n测试相对路径: {test_file}")
        print(f"绝对路径: {os.path.abspath(test_file)}")
        
        # 如果缓存目录存在，相对路径会指向缓存目录
        if os.path.exists(cache_dir):
            os.chdir(cache_dir)
            print(f"切换到缓存目录后: {os.getcwd()}")
            print(f"相对路径绝对化: {os.path.abspath('output')}")
    
    # 检查环境变量
    print(f"\n=== 环境变量 ===")
    relevant_vars = ['LOCALAPPDATA', 'APPDATA', 'TEMP', 'TMP', 'UVX_CACHE_DIR']
    for var in relevant_vars:
        value = os.environ.get(var, "未设置")
        print(f"{var}: {value}")

if __name__ == "__main__":
    print_path_info()