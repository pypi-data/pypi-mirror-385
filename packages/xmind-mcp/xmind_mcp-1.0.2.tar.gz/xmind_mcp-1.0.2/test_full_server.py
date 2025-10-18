#!/usr/bin/env python3
"""
完整的MCP服务器功能测试
"""

import json
import subprocess
import time
import os

def test_mcp_server():
    """完整测试MCP服务器功能"""
    print("完整测试MCP服务器功能...")
    
    # 设置环境变量
    env = os.environ.copy()
    env['XMIND_DATA_DIR'] = './xmind_data'
    
    # 启动服务器进程
    print("1. 启动服务器...")
    try:
        server_process = subprocess.Popen(
            ["python", "xmind_mcp_server.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=0,
            env=env,
            encoding='utf-8',
            errors='replace'
        )
        
        # 等待服务器启动
        time.sleep(2)
        
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
            server_process.stdin.write(request_json)
            server_process.stdin.flush()
            
            # 读取响应
            response = server_process.stdout.readline()
            if response:
                return json.loads(response)
            return None
        
        # 测试1: 初始化
        print("2. 测试初始化...")
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
            print("初始化失败")
            return
        
        # 测试2: 工具列表
        print("3. 测试工具列表...")
        tools_response = send_request("tools/list", {}, 2)
        
        if tools_response:
            tools = tools_response.get('result', {}).get('tools', [])
            print(f"可用工具: {len(tools)} 个")
            for tool in tools:
                print(f"  - {tool.get('name', 'unknown')}: {tool.get('description', 'no description')}")
        else:
            print("工具列表失败")
        
        # 测试3: 创建思维导图
        print("4. 测试创建思维导图...")
        create_response = send_request("tools/call", {
            "name": "create_mind_map",
            "arguments": {
                "title": "测试思维导图",
                "topics": ["主题1", "主题2", "主题3"]
            }
        }, 3)
        
        if create_response:
            print(f"创建结果: {create_response}")
        else:
            print("创建失败")
        
        # 测试完成，发送关闭请求
        print("5. 关闭服务器...")
        shutdown_response = send_request("shutdown", {}, 4)
        if shutdown_response:
            print(f"关闭结果: {json.dumps(shutdown_response, ensure_ascii=False, indent=2)}")
        
        # 6. 退出
        print("6. 退出程序...")
        exit_request = {
            "jsonrpc": "2.0",
            "id": 5,
            "method": "exit"
        }
        exit_json = json.dumps(exit_request) + '\n'
        server_process.stdin.write(exit_json)
        server_process.stdin.flush()
        
        # 等待服务器进程结束
        time.sleep(1)
        
    except Exception as e:
        print(f"测试失败: {e}")
        
    finally:
        # 确保关闭所有资源
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
        
        # 终止服务器进程
        try:
            server_process.terminate()
            server_process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            server_process.kill()
            server_process.wait()
        except:
            pass
            
    print("测试完成!")

if __name__ == "__main__":
    test_mcp_server()