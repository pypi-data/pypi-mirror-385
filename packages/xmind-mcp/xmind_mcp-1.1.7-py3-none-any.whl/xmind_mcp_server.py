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

# 强制设置工作目录为项目目录
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(PROJECT_ROOT)
logger.info(f"工作目录已设置为: {PROJECT_ROOT}")

@dataclass
class XMindConfig:
    def ensure_data_dir(self):
        """确保数据目录存在 - 现在使用相对路径"""
        pass  # 不再需要单独的数据目录配置

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
    def create_mind_map(ctx: Context, title: str, topics_json: str, output_path: str = None) -> str:
        """创建新的思维导图
        
        Args:
            title: 思维导图标题
            topics_json: 主题JSON结构（支持字符串或字典/列表格式）
            output_path: 可选的输出文件路径，如果不指定则使用默认路径
        """
        try:
            # 修复字典参数问题 - 统一处理topics_json格式
            if isinstance(topics_json, (dict, list)):
                # 如果已经是Python对象，直接使用
                topics_data = topics_json
                logger.info(f"topics_json是Python对象: {type(topics_json)}")
            elif isinstance(topics_json, str):
                # 如果是字符串，尝试解析为JSON
                try:
                    topics_data = json.loads(topics_json)
                    logger.info(f"topics_json字符串解析成功")
                except json.JSONDecodeError:
                    # 如果解析失败，创建简单的主题结构
                    topics_data = [{"title": topics_json}]
                    logger.info(f"topics_json作为简单字符串处理")
            else:
                # 其他类型，转换为字符串后处理
                topics_data = [{"title": str(topics_json)}]
                logger.info(f"topics_json转换为字符串: {type(topics_json)}")
            
            # 使用核心引擎的sanitize方法来处理文件名
            engine = get_engine()
            safe_title = engine._sanitize_filename(title)
            
            # 确定输出路径 - 基于项目目录
            if output_path:
                # 如果指定了输出路径，使用指定的路径
                final_output_path = output_path
                output_dir = os.path.dirname(final_output_path)
                if output_dir and not os.path.exists(output_dir):
                    os.makedirs(output_dir)
                logger.info(f"使用指定输出路径: {final_output_path}")
            else:
                # 默认保存到项目目录的output子目录
                output_dir = "output"
                if not os.path.exists(output_dir):
                    os.makedirs(output_dir)
                final_output_path = os.path.join(output_dir, f"{safe_title}.xmind")
                logger.info(f"使用默认输出路径: {final_output_path}")
            
            # 将topics_data转换回JSON字符串供核心引擎使用
            topics_json_str = json.dumps(topics_data, ensure_ascii=False)
            
            # 调用核心引擎创建思维导图
            result = core_create_mind_map(title, topics_json_str, final_output_path)
            logger.info(f"创建思维导图: {title} -> {final_output_path}")
            
            # 验证文件是否真的被创建
            if os.path.exists(final_output_path):
                logger.info(f"文件创建成功，大小: {os.path.getsize(final_output_path)} 字节")
                
                # 修改返回格式
                result_data = result
                if isinstance(result_data, dict) and result_data.get("status") == "success":
                    # 获取绝对路径
                    abs_path = os.path.abspath(final_output_path)
                    # 修改返回数据
                    result_data["filename"] = os.path.basename(final_output_path)
                    result_data["message"] = f"思维导图已创建: {abs_path}"
                    result_data["absolute_path"] = abs_path
                    result_data["output_path"] = final_output_path
                    
                    return json.dumps(result_data, ensure_ascii=False)
            else:
                logger.error(f"文件创建失败，路径: {final_output_path}")
            
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
        """列出XMind文件
        
        Args:
            directory: 要搜索的目录，如果为None则使用项目output目录
        """
        try:
            if directory is None:
                # 默认使用项目目录的output子目录
                directory = "output"
            
            # 确保目录存在
            if not os.path.exists(directory):
                return json.dumps({
                    "status": "error",
                    "message": f"目录不存在: {directory}"
                }, ensure_ascii=False)
            
            # 搜索.xmind文件
            xmind_files = []
            for root, dirs, files in os.walk(directory):
                for file in files:
                    if file.endswith('.xmind'):
                        file_path = os.path.join(root, file)
                        try:
                            stat = os.stat(file_path)
                            xmind_files.append({
                                "name": file,
                                "path": file_path,
                                "size": stat.st_size,
                                "modified": stat.st_mtime
                            })
                        except OSError:
                            continue
            
            logger.info(f"在目录 {directory} 中找到 {len(xmind_files)} 个XMind文件")
            
            return json.dumps({
                "status": "success",
                "directory": directory,
                "files": xmind_files,
                "count": len(xmind_files),
                "message": f"在 {directory} 中找到 {len(xmind_files)} 个XMind文件"
            }, ensure_ascii=False)
            
        except Exception as e:
            logger.error(f"列出XMind文件错误: {e}")
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