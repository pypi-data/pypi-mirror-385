#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SunnyNet 库文件自动下载脚本
在 pip 安装后自动下载对应平台的库文件
"""

import os
import sys
import platform
import struct
import urllib.request
import ssl
from pathlib import Path


# 库文件下载地址配置
# TODO: 请替换为实际的下载地址
LIBRARY_URLS = {
    "windows_64": "https://example.com/downloads/SunnyNet64.dll",
    "windows_32": "https://example.com/downloads/SunnyNet.dll",
    "linux_64": "https://example.com/downloads/SunnyNet64.so",
    "linux_32": "https://example.com/downloads/SunnyNet.so",
    "darwin_64": "https://example.com/downloads/SunnyNet64.dylib",
    "darwin_32": "https://example.com/downloads/SunnyNet.dylib",
}


def get_platform_key():
    """获取当前平台的标识符"""
    system = platform.system().lower()
    is_64bit = struct.calcsize("P") * 8 == 64
    arch = "64" if is_64bit else "32"
    return f"{system}_{arch}"


def get_library_filename():
    """获取当前平台需要的库文件名"""
    system = platform.system().lower()
    is_64bit = struct.calcsize("P") * 8 == 64

    if system == "windows":
        return "SunnyNet64.dll" if is_64bit else "SunnyNet.dll"
    elif system == "linux":
        return "SunnyNet64.so" if is_64bit else "SunnyNet.so"
    elif system == "darwin":
        return "SunnyNet64.dylib" if is_64bit else "SunnyNet.dylib"
    else:
        return None


def get_install_dir():
    """获取 SunnyNet 包的安装目录"""
    try:
        import SunnyNet

        return Path(SunnyNet.__file__).parent
    except ImportError:
        # 如果还未安装，使用当前目录
        return Path(__file__).parent / "SunnyNet"


def download_file(url, dest_path, show_progress=True):
    """
    下载文件

    Args:
        url: 下载地址
        dest_path: 目标路径
        show_progress: 是否显示进度
    """
    print(f"正在下载: {url}")
    print(f"目标路径: {dest_path}")

    try:
        # 创建 SSL 上下文（允许自签名证书）
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

        # 发送请求
        with urllib.request.urlopen(url, context=ssl_context) as response:
            total_size = int(response.headers.get("content-length", 0))
            block_size = 8192
            downloaded = 0

            with open(dest_path, "wb") as f:
                while True:
                    chunk = response.read(block_size)
                    if not chunk:
                        break
                    f.write(chunk)
                    downloaded += len(chunk)

                    if show_progress and total_size > 0:
                        percent = (downloaded / total_size) * 100
                        print(
                            f"\r下载进度: {percent:.1f}% ({downloaded}/{total_size} 字节)",
                            end="",
                        )

        if show_progress:
            print()  # 换行
        print(f"✓ 下载完成: {dest_path}")
        return True

    except Exception as e:
        print(f"✗ 下载失败: {e}")
        return False


def download_library(force=False):
    """
    下载当前平台所需的库文件

    Args:
        force: 是否强制下载（即使文件已存在）
    """
    print("=" * 60)
    print("SunnyNet 库文件自动下载")
    print("=" * 60)

    # 获取平台信息
    system = platform.system()
    platform_key = get_platform_key()
    lib_filename = get_library_filename()

    print(f"\n系统信息:")
    print(f"  操作系统: {system}")
    print(f"  平台标识: {platform_key}")
    print(f"  需要文件: {lib_filename}")

    if lib_filename is None:
        print(f"\n✗ 不支持的操作系统: {system}")
        return False

    # 获取下载地址
    url = LIBRARY_URLS.get(platform_key)
    if not url:
        print(f"\n✗ 未配置该平台的下载地址: {platform_key}")
        print(f"\n提示: 请手动下载 {lib_filename} 并放置到 SunnyNet 包目录")
        return False

    # 获取安装目录
    install_dir = get_install_dir()
    dest_path = install_dir / lib_filename

    print(f"\n安装目录: {install_dir}")

    # 检查文件是否已存在
    if dest_path.exists() and not force:
        print(f"\n✓ 库文件已存在: {dest_path}")
        file_size = dest_path.stat().st_size
        print(f"  文件大小: {file_size:,} 字节")

        response = input("\n是否重新下载? (y/N): ").strip().lower()
        if response != "y":
            print("跳过下载")
            return True

    # 确保目录存在
    install_dir.mkdir(parents=True, exist_ok=True)

    # 下载文件
    print()
    success = download_file(url, dest_path)

    if success:
        # 在 Linux/Mac 上设置执行权限
        if platform.system().lower() in ["linux", "darwin"]:
            try:
                os.chmod(dest_path, 0o755)
                print(f"✓ 已设置执行权限")
            except Exception as e:
                print(f"⚠ 设置执行权限失败: {e}")

        print("\n" + "=" * 60)
        print("✓ 库文件下载并安装成功!")
        print("=" * 60)
        return True
    else:
        print("\n" + "=" * 60)
        print("✗ 库文件下载失败")
        print("=" * 60)
        print(f"\n请手动下载 {lib_filename} 到:")
        print(f"  {install_dir}")
        return False


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="下载 SunnyNet 库文件")
    parser.add_argument("-f", "--force", action="store_true", help="强制重新下载")
    parser.add_argument("-u", "--url", help="自定义下载地址")

    args = parser.parse_args()

    # 如果提供了自定义 URL
    if args.url:
        platform_key = get_platform_key()
        LIBRARY_URLS[platform_key] = args.url

    download_library(force=args.force)


if __name__ == "__main__":
    main()
