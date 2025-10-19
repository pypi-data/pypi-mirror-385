#!/usr/bin/env python3
"""
XMind MCP PyPI 发布脚本
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, check=True):
    """运行命令并返回结果"""
    print(f"运行命令: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"错误: {result.stderr}")
        sys.exit(1)
    if result.stdout:
        print(result.stdout)
    return result

def main():
    """主发布流程"""
    print("🚀 XMind MCP PyPI 发布工具")
    print("=" * 50)
    
    # 检查当前目录
    project_root = Path.cwd()
    if not (project_root / "pyproject.toml").exists():
        print("❌ 错误: 未找到 pyproject.toml 文件")
        print("请确保在项目根目录运行此脚本")
        sys.exit(1)
    
    print(f"项目目录: {project_root}")
    
    # 步骤1: 清理旧的构建文件
    print("\n📦 步骤1: 清理旧的构建文件")
    dist_dir = project_root / "dist"
    if dist_dir.exists():
        for file in dist_dir.glob("*"):
            file.unlink()
            print(f"删除: {file}")
    
    # 步骤2: 运行测试
    print("\n🧪 步骤2: 运行核心测试")
    result = run_command("python test_mcp_with_path.py", check=False)
    if result.returncode != 0:
        print("⚠️  测试失败，是否继续发布？(y/N)")
        if input().lower() != 'y':
            sys.exit(1)
    
    # 步骤3: 构建包
    print("\n🔨 步骤3: 构建包")
    run_command("python -m build")
    
    # 步骤4: 检查包
    print("\n🔍 步骤4: 检查包")
    run_command("twine check dist/*")
    
    # 步骤5: 发布到测试PyPI（可选）
    print("\n🧪 步骤5: 发布到测试PyPI？ (y/N)")
    if input().lower() == 'y':
        print("发布到测试PyPI...")
        run_command("twine upload --repository testpypi dist/*")
        print("✅ 已发布到测试PyPI")
        print("测试PyPI地址: https://test.pypi.org/project/xmind-mcp/")
    
    # 步骤6: 发布到正式PyPI
    print("\n🚀 步骤6: 发布到正式PyPI？ (y/N)")
    if input().lower() == 'y':
        print("发布到正式PyPI...")
        run_command("twine upload dist/*")
        print("✅ 已发布到正式PyPI")
        print("PyPI地址: https://pypi.org/project/xmind-mcp/")
    
    print("\n" + "=" * 50)
    print("🎉 发布流程完成！")
    print("\n📋 后续步骤:")
    print("1. 在GitHub上创建发布版本")
    print("2. 更新文档和版本说明")
    print("3. 通知用户新版本可用")

if __name__ == "__main__":
    main()