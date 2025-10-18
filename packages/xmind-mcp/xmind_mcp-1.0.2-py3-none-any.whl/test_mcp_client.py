#!/usr/bin/env python3
"""
简单的MCP客户端测试
"""

import json
import sys
import subprocess
import time
import threading
import queue

def test_mcp_client():
    """测试MCP客户端连接"""
    print("测试MCP客户端连接...")
    
    # 启动服务器进程
    print("1. 启动服务器...")
    try:
        server_process = subprocess.Popen(
            ["python", "xmind_mcp_server.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=0
        )
        
        # 等待服务器启动
        time.sleep(2)
        
        # 发送初始化请求
        print("2. 发送初始化请求...")
        init_request = {
            "jsonrpc": "2.0",
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            },
            "id": 1
        }
        
        # 发送请求
        request_json = json.dumps(init_request) + "\n"
        server_process.stdin.write(request_json)
        server_process.stdin.flush()
        
        # 读取响应
        print("3. 等待响应...")
        try:
            response = server_process.stdout.readline()
            print(f"收到响应: {response[:200]}")
            
            if response:
                response_data = json.loads(response)
                print(f"响应数据: {json.dumps(response_data, indent=2)}")
                
                # 发送关闭通知
                print("4. 发送关闭通知...")
                shutdown_request = {
                    "jsonrpc": "2.0",
                    "method": "shutdown",
                    "id": 2
                }
                shutdown_json = json.dumps(shutdown_request) + "\n"
                server_process.stdin.write(shutdown_json)
                server_process.stdin.flush()
                
                # 等待关闭响应
                time.sleep(1)
                
            else:
                print("没有收到响应")
                
        except Exception as e:
            print(f"读取响应失败: {e}")
            
        # 检查错误输出
        errors = server_process.stderr.read()
        if errors:
            print(f"错误输出: {errors[:500]}")
        
    except Exception as e:
        print(f"测试失败: {e}")
        
    finally:
        # 清理
        try:
            server_process.terminate()
            server_process.wait(timeout=5)
        except:
            server_process.kill()
            
    print("测试完成!")

if __name__ == "__main__":
    test_mcp_client()