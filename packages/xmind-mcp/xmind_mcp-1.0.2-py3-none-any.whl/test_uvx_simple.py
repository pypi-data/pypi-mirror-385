#!/usr/bin/env python3
"""
简单测试uvx部署的MCP服务器
"""
import subprocess
import json
import time
import sys

def test_uvx_deployment():
    """测试uvx部署"""
    print("测试uvx部署的XMind MCP服务器...")
    
    # 1. 测试帮助命令
    print("1. 测试帮助命令...")
    result = subprocess.run([
        'uvx', '--no-cache', '--from', 'dist/xmind_mcp-1.0.1-py3-none-any.whl', 
        'xmind-mcp', '--help'
    ], capture_output=True, text=True)
    
    if result.returncode == 0 and 'XMind MCP服务器' in result.stdout:
        print("✓ 帮助命令测试通过")
    else:
        print(f"✗ 帮助命令测试失败: {result.stderr}")
        return False
    
    # 2. 测试版本命令
    print("2. 测试版本命令...")
    result = subprocess.run([
        'uvx', '--no-cache', '--from', 'dist/xmind_mcp-1.0.1-py3-none-any.whl', 
        'xmind-mcp', '--version'
    ], capture_output=True, text=True)
    
    if result.returncode == 0 and 'XMind MCP Server 1.0.1' in result.stdout:
        print("✓ 版本命令测试通过")
    else:
        print(f"✗ 版本命令测试失败: {result.stderr}")
        return False
    
    # 3. 测试调试模式启动
    print("3. 测试调试模式启动...")
    process = subprocess.Popen([
        'uvx', '--no-cache', '--from', 'dist/xmind_mcp-1.0.1-py3-none-any.whl', 
        'xmind-mcp', '--debug'
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    # 等待服务器启动
    time.sleep(3)
    
    # 检查进程是否还在运行
    if process.poll() is None:
        print("✓ 服务器成功启动")
        process.terminate()
        process.wait()
        return True
    else:
        stdout, stderr = process.communicate()
        print(f"✗ 服务器启动失败: {stderr}")
        return False

if __name__ == "__main__":
    success = test_uvx_deployment()
    if success:
        print("\n🎉 所有测试通过！uvx部署成功")
        sys.exit(0)
    else:
        print("\n❌ 测试失败")
        sys.exit(1)