#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
XMind MCP 一键发布脚本

功能：
- 语义化版本校验与写入（pyproject.toml + 可选 _version.py）
- 清理旧构建产物
- 安装构建与上传工具（build、twine）
- 构建分发包 (sdist, wheel)
- Twine校验并可选上传到PyPI/TestPyPI
- 使用uvx基于本地产物进行安装与基础功能验证

用法示例：
python scripts/release.py --new-version 1.0.4 --upload --repository pypi
python scripts/release.py --new-version 1.0.4 --upload --repository testpypi
python scripts/release.py --new-version 1.0.4
"""
import argparse
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PYPROJECT = ROOT / "pyproject.toml"
VERSION_FILE = ROOT / "_version.py"
DIST_DIR = ROOT / "dist"
BUILD_DIR = ROOT / "build"
EGG_INFO_DIR = ROOT / "xmind_mcp.egg-info"

SEMVER_RE = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?$")


def run(cmd, cwd=None, check=True):
    print(f"$ {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, encoding="utf-8")
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr)
    if check and result.returncode != 0:
        raise SystemExit(f"Command failed: {' '.join(cmd)}")
    return result


def update_pyproject_version(new_version: str):
    content = PYPROJECT.read_text(encoding="utf-8")
    content = re.sub(r"^version\s*=\s*\".*?\"", f"version = \"{new_version}\"", content, flags=re.MULTILINE)
    PYPROJECT.write_text(content, encoding="utf-8")
    print(f"✅ pyproject.toml 版本已更新为 {new_version}")


def update_version_file(new_version: str):
    # 如果存在_version.py，则同步更新；否则跳过
    if VERSION_FILE.exists():
        VERSION_FILE.write_text(f"__version__ = version = '{new_version}'\n", encoding="utf-8")
        print(f"✅ _version.py 版本已更新为 {new_version}")
    else:
        print("ℹ️ 跳过 _version.py（文件不存在）")


def clean_build_artifacts():
    for path in [DIST_DIR, BUILD_DIR, EGG_INFO_DIR]:
        if path.exists():
            shutil.rmtree(path)
            print(f"🧹 已删除 {path}")
    print("✅ 构建环境已清理")


def ensure_tools():
    # 安装必要工具：build、twine
    run([sys.executable, "-m", "pip", "install", "-U", "build", "twine"])


def build_dist():
    run([sys.executable, "-m", "build"], cwd=str(ROOT))
    print("✅ 构建完成")


def twine_check():
    run([sys.executable, "-m", "twine", "check", str(DIST_DIR / "*")], cwd=str(ROOT))
    print("✅ Twine校验通过")


def twine_upload(repository: str):
    repo_url = {
        "pypi": None,  # 使用默认PyPI
        "testpypi": "https://test.pypi.org/legacy/",
    }.get(repository.lower())

    # 确保Windows控制台使用UTF-8编码，避免Rich进度条编码错误
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")

    cmd = [sys.executable, "-m", "twine", "upload", str(DIST_DIR / "*")]
    if repo_url:
        cmd.extend(["--repository-url", repo_url])
    run(cmd, cwd=str(ROOT))
    print(f"✅ 已上传到 {repository}")

# 新增：加载令牌环境文件

def load_env_file(path: str):
    env_path = Path(path)
    if env_path.exists():
        print(f"🔐 加载令牌环境文件: {env_path}")
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, value = line.split("=", 1)
                os.environ[key.strip()] = value.strip()
    else:
        print(f"⚠️ 未找到令牌文件: {env_path}，将使用系统环境变量")


def uvx_basic_validation(new_version: str):
    # 使用uvx从本地构建产物运行：检查版本与基本帮助
    wheel_candidates = list(DIST_DIR.glob(f"xmind_mcp-{new_version}-*.whl"))
    sdist_candidates = list(DIST_DIR.glob("xmind-mcp-*.tar.gz"))
    if not wheel_candidates and not sdist_candidates:
        raise SystemExit("未找到构建的whl或sdist包，用于uvx验证")

    spec = str(wheel_candidates[0] if wheel_candidates else sdist_candidates[0])
    print(f"🔍 使用uvx验证: {spec}")

    # 版本输出
    run(["uvx", "--from", spec, "xmind-mcp", "--version"], check=False)
    # 帮助输出
    run(["uvx", "--from", spec, "xmind-mcp", "--help"], check=False)
    # 依赖导入验证
    run(["uvx", "--from", spec, "python", "-c", "import mcp, bs4, docx, openpyxl; print('deps-ok')"], check=True)
    print("✅ uvx 基础功能与依赖验证通过")

# 新增：从PyPI安装进行验证

def uvx_pypi_validation(new_version: str):
    spec = f"xmind-mcp=={new_version}"
    print(f"🔍 从PyPI验证: {spec}")
    run(["uvx", "--from", spec, "xmind-mcp", "--version"], check=False)
    run(["uvx", "--from", spec, "xmind-mcp", "--help"], check=False)
    run(["uvx", "--from", spec, "python", "-c", "import mcp, bs4, docx, openpyxl; print('deps-ok-pypi')"], check=True)
    print("✅ PyPI 安装与依赖验证通过")


def main():
    parser = argparse.ArgumentParser(description="XMind MCP 发布工具")
    parser.add_argument("--new-version", required=True, help="新版本号（语义化版本）")
    parser.add_argument("--upload", action="store_true", help="构建后上传到仓库")
    parser.add_argument("--repository", default="pypi", choices=["pypi", "testpypi"], help="上传目标仓库")
    # 新增：令牌环境文件路径，默认使用 configs/.pypi-token.env
    parser.add_argument("--env-file", default=str(ROOT / "configs/.pypi-token.env"), help="PyPI令牌环境文件路径")

    args = parser.parse_args()
    new_version = args.new_version.strip()

    if not SEMVER_RE.match(new_version):
        raise SystemExit(f"版本号不符合语义化规范: {new_version}")

    print(f"🚀 开始发布流程：版本 {new_version}")

    update_pyproject_version(new_version)
    update_version_file(new_version)
    clean_build_artifacts()
    ensure_tools()
    build_dist()
    twine_check()

    if args.upload:
        # 先加载环境令牌（如存在），再上传
        load_env_file(args.env_file)
        twine_upload(args.repository)

    # 构建后，无论是否上传，都进行一次本地uvx验证
    uvx_basic_validation(new_version)

    # 若上传到正式PyPI，则再进行一次从PyPI拉取的验证
    if args.upload and args.repository.lower() == "pypi":
        uvx_pypi_validation(new_version)

    print("🎉 全流程完成")


if __name__ == "__main__":
    main()