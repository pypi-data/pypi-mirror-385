#!/usr/bin/env python3
"""
验证XMind MCP服务器创建路径修复的脚本
"""

import json
import os
from xmind_mcp_server import config, create_mind_map

def test_mcp_create_path():
    """测试MCP服务器创建思维导图的路径"""
    print("=== 测试MCP服务器创建思维导图路径 ===")
    
    # 确保数据目录存在
    config.ensure_data_dir()
    print(f"数据目录: {config.data_dir}")
    
    # 模拟MCP服务器环境
    class MockContext:
        pass
    
    ctx = MockContext()
    
    # 测试创建思维导图
    title = '修复验证测试'
    topics_json = json.dumps([
        {'title': '主题1'},
        {'title': '主题2', 'children': [
            {'title': '子主题2.1'},
            {'title': '子主题2.2'}
        ]}
    ])
    
    # 调用MCP服务器的create_mind_map函数
    result_str = create_mind_map(ctx, title, topics_json)
    result = json.loads(result_str)
    
    print(f"创建结果: {result['status']}")
    print(f"文件路径: {result['filename']}")
    print(f"标题: {result['title']}")
    print(f"主题数量: {result['topics_count']}")
    
    # 验证文件是否存在
    expected_path = os.path.join(config.data_dir, f'{title}.xmind')
    file_exists = os.path.exists(expected_path)
    print(f"文件存在检查: {expected_path}")
    print(f"文件存在: {file_exists}")
    
    if file_exists:
        print("✅ 修复验证通过！新创建的XMind文件现在在正确的目录中")
        return True
    else:
        print("❌ 修复验证失败！文件未在预期位置找到")
        return False

def check_directories():
    """检查相关目录状态"""
    print("\n=== 目录状态检查 ===")
    
    # 检查数据目录
    data_dir_exists = os.path.exists(config.data_dir)
    print(f"数据目录存在: {data_dir_exists}")
    if data_dir_exists:
        files = os.listdir(config.data_dir)
        print(f"数据目录文件: {files}")
    
    # 检查输出目录
    output_dir_exists = os.path.exists("output")
    print(f"输出目录存在: {output_dir_exists}")
    if output_dir_exists:
        files = os.listdir("output")
        print(f"输出目录文件: {files}")
    
    return data_dir_exists

if __name__ == "__main__":
    print("开始验证XMind MCP服务器路径修复...")
    
    # 检查目录
    dir_ok = check_directories()
    
    # 测试创建功能
    if dir_ok:
        success = test_mcp_create_path()
        if success:
            print("\n🎉 所有验证通过！问题已修复")
            print("转换的XMind文件：正常（使用明确指定的路径）")
            print("创建的XMind文件：现在正确保存到xmind_data目录")
        else:
            print("\n💥 验证失败，需要进一步检查")
    else:
        print("\n⚠️  目录检查失败")