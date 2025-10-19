#!/usr/bin/env python3
"""
XMind MCP Server - FastMCP Implementation
只使用真实XMind核心引擎，移除所有模拟实现
"""

import logging
import sys
import json
import os
import argparse
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from contextlib import asynccontextmanager
from typing import AsyncIterator

# 导入版本信息
try:
    from xmind_mcp import __version__ as __version__
except Exception:
    try:
        from _version import version as __version__
    except Exception:
        __version__ = "0.0.0"  # 统一回退版本

# 导入真实的XMind核心引擎
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    from xmind_core_engine import (
        get_engine, 
        read_xmind_file as core_read_xmind_file, 
        create_mind_map as core_create_mind_map, 
        analyze_mind_map as core_analyze_mind_map, 
        convert_to_xmind as core_convert_to_xmind, 
        list_xmind_files as core_list_xmind_files
    )
    REAL_ENGINE_AVAILABLE = True
    logging.info("真实XMind核心引擎已加载")
except ImportError as e:
    REAL_ENGINE_AVAILABLE = False
    logging.error(f"真实XMind核心引擎加载失败: {e}")
    logging.error("MCP服务器无法启动，需要真实引擎支持")
    sys.exit(1)

# 尝试导入FastMCP，失败则回退到标准实现
try:
    from mcp.server.fastmcp import FastMCP, Context
    FASTMCP_AVAILABLE = True
    logging.info("使用FastMCP实现")
except ImportError:
    FASTMCP_AVAILABLE = False
    logging.warning("FastMCP不可用，使用标准MCP实现")
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("XMindMCPServer")

# 全局配置
XMIND_DATA_DIR = os.getenv("XMIND_DATA_DIR", "./xmind_data")

@dataclass
class XMindConfig:
    data_dir: str = XMIND_DATA_DIR
    
    def ensure_data_dir(self):
        """确保数据目录存在"""
        Path(self.data_dir).mkdir(parents=True, exist_ok=True)

# 全局配置实例
config = XMindConfig()

if FASTMCP_AVAILABLE:
    # FastMCP实现
    @asynccontextmanager
    async def server_lifespan(server: FastMCP) -> AsyncIterator[Dict[str, Any]]:
        """管理服务器生命周期"""
        logger.info("XMind MCP服务器启动")
        config.ensure_data_dir()
        yield {}
        logger.info("XMind MCP服务器关闭")

    # 创建FastMCP服务器
    mcp = FastMCP("XMindMCP")

    @mcp.tool()
    def read_xmind_file(ctx: Context, file_path: str) -> str:
        """读取XMind文件内容"""
        try:
            result = core_read_xmind_file(file_path)
            logger.info(f"读取XMind文件: {file_path}")
            return json.dumps(result, ensure_ascii=False)
        except Exception as e:
            logger.error(f"读取文件错误: {e}")
            return f"错误: {str(e)}"

    @mcp.tool()
    def create_mind_map(ctx: Context, title: str, topics_json: str) -> str:
        """创建新的思维导图"""
        try:
            # 使用核心引擎的sanitize方法来处理文件名
            # 从核心引擎获取引擎实例来处理文件名
            engine = get_engine()
            safe_title = engine._sanitize_filename(title)
            
            # 构建输出路径 - 使用相对路径，与convert_to_xmind保持一致
            output_dir = "output"
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            output_path = os.path.join(output_dir, f"{safe_title}.xmind")
            
            # 调用核心引擎创建思维导图
            result = core_create_mind_map(title, topics_json, output_path)
            logger.info(f"创建思维导图: {title} -> {output_path}")
            
            # 验证文件是否真的被创建
            if os.path.exists(output_path):
                logger.info(f"文件创建成功，大小: {os.path.getsize(output_path)} 字节")
                
                # 修改返回格式：filename只包含文件名，message包含绝对路径
                # result已经是字典对象，不需要json.loads
                result_data = result
                if result_data.get("status") == "success":
                    # 获取绝对路径
                    abs_path = os.path.abspath(output_path)
                    # 修改返回数据 - 只返回文件名，不包含路径
                    result_data["filename"] = f"{safe_title}.xmind"  # 只返回文件名
                    result_data["message"] = f"思维导图已创建: {abs_path}"  # message包含绝对路径
                    result_data["absolute_path"] = abs_path  # 额外添加绝对路径字段
                    
                    return json.dumps(result_data, ensure_ascii=False)
            else:
                logger.error(f"文件创建失败，路径: {output_path}")
            
            return json.dumps(result, ensure_ascii=False)
        except Exception as e:
            logger.error(f"创建思维导图错误: {e}")
            return f"错误: {str(e)}"

    @mcp.tool()
    def analyze_mind_map(ctx: Context, file_path: str) -> str:
        """分析思维导图结构"""
        try:
            result = core_analyze_mind_map(file_path)
            logger.info(f"分析思维导图: {file_path}")
            return json.dumps(result, ensure_ascii=False)
        except Exception as e:
            logger.error(f"分析思维导图错误: {e}")
            return f"错误: {str(e)}"

    @mcp.tool()
    def convert_to_xmind(ctx: Context, source_file: str, output_file: str = None) -> str:
        """将其他格式文件转换为XMind格式"""
        try:
            result = core_convert_to_xmind(source_file, output_file)
            logger.info(f"转换文件为XMind格式: {source_file}")
            return json.dumps(result, ensure_ascii=False)
        except Exception as e:
            logger.error(f"文件转换错误: {e}")
            return f"错误: {str(e)}"

    @mcp.tool()
    def list_xmind_files(ctx: Context, directory: str = None) -> str:
        """列出XMind文件"""
        try:
            search_dir = directory or config.data_dir
            result = core_list_xmind_files(search_dir, recursive=True)
            logger.info(f"列出XMind文件在: {search_dir}")
            return json.dumps(result, ensure_ascii=False)
        except Exception as e:
            logger.error(f"列出文件错误: {e}")
            return f"错误: {str(e)}"

def main():
    """主函数 - 支持 --mode fastmcp|stdio"""
    parser = argparse.ArgumentParser(description='XMind MCP服务器')
    parser.add_argument('--version', action='version', version=f'XMind MCP Server {__version__}')
    parser.add_argument('--debug', action='store_true', help='启用调试模式')
    parser.add_argument('--mode', choices=['fastmcp', 'stdio'], help='选择运行模式：fastmcp 或 stdio')
    parser.add_argument('--stdio', action='store_true', help='以 STDIO 模式运行（别名）')

    args = parser.parse_args()

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        print("调试模式已启用")

    requested_mode = 'fastmcp' if FASTMCP_AVAILABLE else 'stdio'
    if args.stdio:
        requested_mode = 'stdio'
    if args.mode:
        requested_mode = args.mode

    if requested_mode == 'fastmcp':
        if not FASTMCP_AVAILABLE:
            logger.error("FastMCP 不可用，请安装 mcp[cli]>=1.3.0 或使用 --mode stdio")
            sys.exit(1)
        print("启动XMind MCP服务器 (FastMCP模式)")
        logger.info("启动XMind MCP服务器 (FastMCP模式)")
        mcp.run()
    else:
        print("启动XMind MCP服务器 (STDIO模式)")
        logger.info("启动XMind MCP服务器 (STDIO模式)")
        try:
            # 使用已验证的STDIO实现
            import subprocess
            import sys
            
            # 运行简化的STDIO MCP服务器
            cmd = [sys.executable, "-m", "xmind_mcp.stdio_server"]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"STDIO服务器启动失败: {result.stderr}")
                sys.exit(1)
                
        except Exception as e:
            logger.error(f"STDIO 模式启动失败: {e}")
            sys.exit(1)

if __name__ == "__main__":
    main()