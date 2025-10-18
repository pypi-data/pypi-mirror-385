#!/usr/bin/env python3
"""
测试uvx部署的MCP服务器
"""

import json
import subprocess
import time
import os
import signal

def test_uvx_server():
    """测试uvx部署的服务器"""
    print("测试uvx部署的MCP服务器...")
    
    # 启动服务器进程
    print("1. 使用uvx启动服务器...")
    try:
        server_process = subprocess.Popen(
            ["uvx", "--no-cache", "xmind-mcp", "--debug"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=0,
            encoding='utf-8',
            errors='replace'
        )
        
        # 等待服务器启动
        time.sleep(3)
        
        # 检查进程是否还在运行
        if server_process.poll() is not None:
            print("服务器进程已经退出")
            stdout, stderr = server_process.communicate()
            print(f"stdout: {stdout}")
            print(f"stderr: {stderr}")
            return False
        
        print("2. 服务器已启动，正在运行...")
        
        def send_request(method, params=None, request_id=None):
            """发送请求并等待响应"""
            request = {
                "jsonrpc": "2.0",
                "method": method,
                "params": params or {}
            }
            if request_id is not None:
                request["id"] = request_id
            
            request_json = json.dumps(request) + "\n"
            try:
                server_process.stdin.write(request_json)
                server_process.stdin.flush()
                
                # 读取响应
                response = server_process.stdout.readline()
                if response:
                    return json.loads(response)
            except Exception as e:
                print(f"发送请求失败: {e}")
            return None
        
        # 测试初始化
        print("3. 测试初始化...")
        init_response = send_request("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {
                "name": "test-client",
                "version": "1.0.0"
            }
        }, 1)
        
        if init_response:
            print(f"初始化成功: {init_response.get('result', {}).get('serverInfo', {})}")
        else:
            print("初始化失败或没有响应")
        
        # 测试工具列表
        print("4. 测试工具列表...")
        tools_response = send_request("tools/list", {}, 2)
        
        if tools_response:
            tools = tools_response.get('result', {}).get('tools', [])
            print(f"可用工具: {len(tools)} 个")
            for tool in tools:
                print(f"  - {tool.get('name', 'unknown')}: {tool.get('description', 'no description')}")
        else:
            print("工具列表失败或没有响应")
        
        print("5. 测试完成，正在关闭服务器...")
        
    except Exception as e:
        print(f"测试失败: {e}")
        
    finally:
        # 确保关闭所有资源
        try:
            if server_process.poll() is None:
                print("发送终止信号...")
                server_process.terminate()
                try:
                    server_process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    print("强制终止进程...")
                    server_process.kill()
                    server_process.wait()
        except:
            pass
            
        # 关闭管道
        try:
            server_process.stdin.close()
        except:
            pass
            
        try:
            server_process.stdout.close()
        except:
            pass
            
        try:
            server_process.stderr.close()
        except:
            pass
        
        # 获取最终输出
        try:
            stdout, stderr = server_process.communicate()
            if stdout:
                print(f"最终stdout: {stdout}")
            if stderr:
                print(f"最终stderr: {stderr}")
        except:
            pass
            
    print("测试完成!")

if __name__ == "__main__":
    test_uvx_server()