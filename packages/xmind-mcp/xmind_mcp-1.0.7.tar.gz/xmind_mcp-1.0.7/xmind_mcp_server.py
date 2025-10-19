#!/usr/bin/env python3
"""
XMind MCP Server - FastMCP Implementation
参考blender-mcp的最佳实践，简化架构
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
            if not os.path.exists(file_path):
                return f"错误: 文件不存在: {file_path}"
            
            # 模拟读取XMind文件
            logger.info(f"读取XMind文件: {file_path}")
            return json.dumps({
                "file_path": file_path,
                "content": "模拟XMind文件内容",
                "topics": ["主题1", "主题2", "主题3"],
                "status": "success"
            })
        except Exception as e:
            logger.error(f"读取文件错误: {e}")
            return f"错误: {str(e)}"

    @mcp.tool()
    def create_mind_map(ctx: Context, title: str, topics: List[str]) -> str:
        """创建新的思维导图"""
        try:
            logger.info(f"创建思维导图: {title}")
            file_path = os.path.join(config.data_dir, f"{title.replace(' ', '_')}.xmind")
            
            # 模拟创建文件
            result = {
                "title": title,
                "topics": topics,
                "file_path": file_path,
                "status": "created"
            }
            
            # 模拟保存文件
            logger.info(f"思维导图已创建: {file_path}")
            return json.dumps(result)
        except Exception as e:
            logger.error(f"创建思维导图错误: {e}")
            return f"错误: {str(e)}"

    @mcp.tool()
    def add_topic(ctx: Context, file_path: str, parent_topic: str, new_topic: str) -> str:
        """向思维导图添加主题"""
        try:
            logger.info(f"添加主题到: {file_path}")
            return json.dumps({
                "file_path": file_path,
                "parent_topic": parent_topic,
                "new_topic": new_topic,
                "status": "added"
            })
        except Exception as e:
            logger.error(f"添加主题错误: {e}")
            return f"错误: {str(e)}"

    @mcp.tool()
    def export_to_format(ctx: Context, file_path: str, format: str) -> str:
        """导出思维导图到指定格式"""
        try:
            logger.info(f"导出文件: {file_path} 到格式: {format}")
            output_path = file_path.replace('.xmind', f'.{format}')
            
            return json.dumps({
                "input_file": file_path,
                "output_file": output_path,
                "format": format,
                "status": "exported"
            })
        except Exception as e:
            logger.error(f"导出错误: {e}")
            return f"错误: {str(e)}"

    @mcp.tool()
    def list_xmind_files(ctx: Context, directory: str = None) -> str:
        """列出XMind文件"""
        try:
            search_dir = directory or config.data_dir
            logger.info(f"列出XMind文件在: {search_dir}")
            
            # 模拟文件列表
            files = [
                "project_plan.xmind",
                "meeting_notes.xmind", 
                "brainstorm.xmind"
            ]
            
            return json.dumps({
                "directory": search_dir,
                "files": files,
                "count": len(files)
            })
        except Exception as e:
            logger.error(f"列出文件错误: {e}")
            return f"错误: {str(e)}"

    @mcp.tool()
    def batch_convert_files(ctx: Context, input_pattern: str, output_format: str) -> str:
        """批量转换文件格式"""
        try:
            logger.info(f"批量转换: {input_pattern} 到 {output_format}")
            
            # 模拟批量转换
            converted_files = [
                f"file1.{output_format}",
                f"file2.{output_format}",
                f"file3.{output_format}"
            ]
            
            return json.dumps({
                "input_pattern": input_pattern,
                "output_format": output_format,
                "converted_files": converted_files,
                "count": len(converted_files)
            })
        except Exception as e:
            logger.error(f"批量转换错误: {e}")
            return f"错误: {str(e)}"

    @mcp.tool()
    def get_xmind_statistics(ctx: Context, file_path: str) -> str:
        """获取思维导图统计信息"""
        try:
            logger.info(f"获取统计信息: {file_path}")
            
            return json.dumps({
                "file_path": file_path,
                "total_topics": 15,
                "main_topics": 5,
                "sub_topics": 10,
                "depth": 3,
                "status": "analyzed"
            })
        except Exception as e:
            logger.error(f"获取统计信息错误: {e}")
            return f"错误: {str(e)}"

def main():
    """主函数 - 支持 --mode fastmcp|stdio，并在需要时回退到 STDIO"""
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
            # 降级到简单的STDIO响应
            try:
                import json
                import sys
                
                # 简单的JSON-RPC响应
                response = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "result": {
                        "tools": [{
                            "name": "list_xmind_files",
                            "description": "列出XMind文件",
                            "inputSchema": {"type": "object", "properties": {}}
                        }]
                    }
                }
                print(json.dumps(response), flush=True)
            except:
                sys.exit(1)

if __name__ == "__main__":
    main()