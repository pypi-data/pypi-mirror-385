#!/usr/bin/env python3
"""
测试XMind MCP服务器
"""

import subprocess
import json
import sys
import time
import os

def test_server():
    """测试服务器基本功能"""
    print("测试XMind MCP服务器...")
    
    # 设置环境变量
    env = os.environ.copy()
    env['XMIND_DATA_DIR'] = './xmind_data'
    
    # 测试1: 检查帮助信息
    print("\n1. 测试帮助信息...")
    try:
        result = subprocess.run(
            ["uvx", "xmind-mcp", "--help"],
            capture_output=True,
            text=True,
            timeout=10,
            cwd="d:\\project\\XmindMcp"
        )
        print(f"返回码: {result.returncode}")
        if result.stdout:
            print(f"标准输出: {result.stdout[:200]}")
        if result.stderr:
            print(f"错误输出: {result.stderr[:200]}")
    except Exception as e:
        print(f"帮助测试失败: {e}")
    
    # 测试2: 检查包是否可导入
    print("\n2. 测试包导入...")
    try:
        result = subprocess.run(
            ["python", "-c", "import xmind_mcp_server; print('导入成功')"],
            capture_output=True,
            text=True,
            timeout=10,
            cwd="d:\\project\\XmindMcp"
        )
        print(f"导入测试返回码: {result.returncode}")
        if result.stdout:
            print(f"导入输出: {result.stdout}")
        if result.stderr:
            print(f"导入错误: {result.stderr}")
    except Exception as e:
        print(f"导入测试失败: {e}")
    
    print("\n测试完成!")

if __name__ == "__main__":
    test_server()