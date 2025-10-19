#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
XMind MCP STDIO 客户端测试脚本
验证 xmind-mcp CLI 与 MCP 服务器的基本可用性
"""

import sys
import os
import time
import json
import subprocess
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def log(msg: str):
    print(msg)


def test_cli_version(use_chinese: bool = True) -> float:
    title = "🧪 CLI版本测试" if use_chinese else "🧪 CLI Version Test"
    log(f"\n{title}")
    try:
        result = subprocess.run(
            [sys.executable, "-m", "xmind_mcp_server", "--version"],
            capture_output=True,
            text=True,
            encoding="utf-8"
        )
        ok = result.returncode == 0 and "XMind MCP Server" in (result.stdout + result.stderr)
        if ok:
            log("✅ xmind-mcp 版本输出正常") if use_chinese else log("✅ xmind-mcp version output OK")
            return 100.0
        else:
            log(f"❌ 版本输出异常: rc={result.returncode}\nstdout={result.stdout}\nstderr={result.stderr}") if use_chinese else log(f"❌ Version output failed: rc={result.returncode}\nstdout={result.stdout}\nstderr={result.stderr}")
            return 0.0
    except Exception as e:
        log(f"❌ 执行失败: {e}") if use_chinese else log(f"❌ Execution failed: {e}")
        return 0.0


def test_stdio_start(use_chinese: bool = True) -> float:
    title = "🚀 STDIO启动测试" if use_chinese else "🚀 STDIO Start Test"
    log(f"\n{title}")
    try:
        # 以调试模式启动，等待片刻后结束进程
        proc = subprocess.Popen(
            [sys.executable, "-m", "xmind_mcp_server", "--debug"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8"
        )
        time.sleep(1.5)
        started = proc.poll() is None
        # 读取部分输出以确认日志
        try:
            out = proc.stdout.read(0) if proc.stdout else ""
        except Exception:
            out = ""
        # 结束进程
        proc.terminate()
        try:
            proc.wait(timeout=2)
        except Exception:
            proc.kill()
        if started:
            log("✅ 服务器进程已启动 (STDIO)") if use_chinese else log("✅ Server process started (STDIO)")
            return 100.0
        else:
            log("❌ 服务器进程未能启动") if use_chinese else log("❌ Server process failed to start")
            return 0.0
    except Exception as e:
        log(f"❌ 启动失败: {e}") if use_chinese else log(f"❌ Start failed: {e}")
        return 0.0


def test_tools_invocation(use_chinese: bool = True) -> float:
    title = "🔧 工具函数调用测试" if use_chinese else "🔧 Tool Invocation Test"
    log(f"\n{title}")
    try:
        # 直接导入服务器模块并调用已注册的工具函数，验证基础逻辑
        import xmind_mcp_server as server
        # 使用默认目录列出XMind文件
        result_json = server.list_xmind_files(None)
        data = json.loads(result_json) if isinstance(result_json, str) else result_json
        ok = isinstance(data, dict) and data.get("count", 0) >= 0 and isinstance(data.get("files", []), list)
        if ok:
            log(f"✅ 工具调用成功，发现 {data.get('count', 0)} 个文件") if use_chinese else log(f"✅ Tool call OK, found {data.get('count', 0)} files")
            return 100.0
        else:
            log("❌ 工具返回异常结构") if use_chinese else log("❌ Tool returned unexpected structure")
            return 0.0
    except Exception as e:
        log(f"❌ 工具调用失败: {e}") if use_chinese else log(f"❌ Tool invocation failed: {e}")
        return 0.0


def main():
    use_chinese = True if "--english" not in sys.argv else False
    header = "🚀 XMind MCP STDIO 客户端测试" if use_chinese else "🚀 XMind MCP STDIO Client Tests"
    log(header)
    log(f"项目路径: {project_root}") if use_chinese else log(f"Project root: {project_root}")

    rates = []
    rates.append(test_cli_version(use_chinese))
    rates.append(test_stdio_start(use_chinese))
    rates.append(test_tools_invocation(use_chinese))

    overall = sum(rates) / len(rates) if rates else 0.0
    log("\n📊 测试总结") if use_chinese else log("\n📊 Test Summary")
    log(f"  通过率: {overall:.1f}%") if use_chinese else log(f"  Pass rate: {overall:.1f}%")

    # 输出统一格式的结尾行，便于run_all_tests提取
    end_line = ("通过率: " if use_chinese else "Pass rate: ") + f"{overall:.1f}%"
    print(end_line)


if __name__ == "__main__":
    main()