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


# 直接配置下载地址（避免导入触发 SunnyDLL 加载）
GITHUB_REPO = "kiss-kedaya/SunnyNet"
RELEASE_VERSION = "v1.3.3"

# GitHub 加速镜像列表（按优先级排序）
GITHUB_MIRRORS = [
    "https://github.com",  # 官方源（国外优先）
    "https://gh-proxy.com",  # gh-proxy
    "https://ghproxy.com",  # ghproxy
    "https://gh.ddlc.top",  # ddlc
    "https://ghps.cc",  # ghps
    "https://cdn.gh-proxy.com",  # cdn gh-proxy
]

def get_release_url(mirror, filename):
    """根据镜像源生成下载URL"""
    github_path = f"https://github.com/{GITHUB_REPO}/releases/download/{RELEASE_VERSION}/{filename}"
    if mirror == "https://github.com":
        return github_path
    else:
        # 镜像格式: mirror/github_url
        return f"{mirror}/{github_path}"

# 库文件名映射
LIBRARY_FILES = {
    "windows_64": "SunnyNet64.dll",
    "windows_32": "SunnyNet.dll",
    "linux_64": "libSunnyNet-arm64.so",
    "linux_32": "libSunnyNet-x86.so",
    "darwin_64": None,
    "darwin_32": None,
}

# 保持向后兼容
LIBRARY_URLS = {k: (get_release_url(GITHUB_MIRRORS[0], v) if v else None) for k, v in LIBRARY_FILES.items()}


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
        # Linux 文件名为 libSunnyNet.so (不区分32/64位)
        return "libSunnyNet.so"
    elif system == "darwin":
        return "SunnyNet64.dylib" if is_64bit else "SunnyNet.dylib"
    else:
        return None


def get_install_dir():
    """获取 SunnyNet 包的安装目录"""
    # 使用当前文件所在目录（即 SunnyNet 包目录）
    return Path(__file__).parent


def download_file(url, dest_path, show_progress=True, timeout=30):
    """
    下载文件

    Args:
        url: 下载地址
        dest_path: 目标路径
        show_progress: 是否显示进度
        timeout: 超时时间（秒）
    """
    try:
        # 创建 SSL 上下文（允许自签名证书）
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

        # 发送请求
        request = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(request, context=ssl_context, timeout=timeout) as response:
            total_size = int(response.headers.get("content-length", 0))
            block_size = 8192
            downloaded = 0

            # 显示文件大小
            if total_size > 0:
                size_mb = total_size / 1024 / 1024
                print(f"文件大小: {size_mb:.2f} MB")

            with open(dest_path, "wb") as f:
                while True:
                    chunk = response.read(block_size)
                    if not chunk:
                        break
                    f.write(chunk)
                    downloaded += len(chunk)

                    if show_progress and total_size > 0:
                        percent = (downloaded / total_size) * 100
                        downloaded_mb = downloaded / 1024 / 1024
                        total_mb = total_size / 1024 / 1024
                        # 使用进度条显示
                        bar_length = 30
                        filled = int(bar_length * downloaded / total_size)
                        bar = "█" * filled + "░" * (bar_length - filled)
                        print(
                            f"\r下载进度: [{bar}] {percent:.1f}% ({downloaded_mb:.1f}/{total_mb:.1f} MB)",
                            end="",
                            flush=True
                        )

        if show_progress:
            print()  # 换行
        print(f"✓ 下载完成")
        return True

    except Exception as e:
        if show_progress:
            print()  # 确保错误信息在新行
        print(f"✗ 下载失败: {e}")
        return False


def download_file_with_mirrors(filename, dest_path, show_progress=True):
    """
    使用多个镜像源尝试下载文件
    
    Args:
        filename: 文件名
        dest_path: 目标路径
        show_progress: 是否显示进度
    
    Returns:
        bool: 是否成功
    """
    print(f"\n正在下载: {filename}")
    print(f"目标路径: {dest_path}")
    
    for i, mirror in enumerate(GITHUB_MIRRORS, 1):
        url = get_release_url(mirror, filename)
        mirror_name = mirror.replace("https://", "")
        
        print(f"\n[{i}/{len(GITHUB_MIRRORS)}] 尝试镜像: {mirror_name}")
        print(f"URL: {url}")
        
        success = download_file(url, dest_path, show_progress, timeout=60)
        
        if success:
            return True
        
        # 如果不是最后一个镜像，继续尝试
        if i < len(GITHUB_MIRRORS):
            print("正在尝试下一个镜像...")
    
    print(f"\n✗ 所有镜像都下载失败")
    print(f"\n💡 您也可以手动下载:")
    print(f"   1. 访问: https://github.com/{GITHUB_REPO}/releases/tag/{RELEASE_VERSION}")
    print(f"   2. 下载: {filename}")
    print(f"   3. 放置到: {dest_path.parent}")
    return False


def download_library_to_path(url, dest_path, lib_filename):
    """
    下载库文件到指定路径（用于 CLI）
    
    Args:
        url: 下载地址（用于获取文件名）
        dest_path: 目标路径（Path 对象）
        lib_filename: 本地文件名
    
    Returns:
        bool: 是否成功
    """
    # 从 URL 获取原始文件名
    url_filename = url.split("/")[-1]
    
    # 使用多镜像下载
    if url_filename != lib_filename:
        # 先下载到临时位置
        temp_path = dest_path.parent / url_filename
        success = download_file_with_mirrors(url_filename, temp_path)
        
        if success:
            try:
                if dest_path.exists():
                    dest_path.unlink()
                temp_path.rename(dest_path)
                print(f"✓ 文件已重命名为: {lib_filename}")
            except Exception as e:
                print(f"⚠ 重命名失败: {e}")
                return False
    else:
        success = download_file_with_mirrors(url_filename, dest_path)
    
    if success:
        # 在 Linux/Mac 上设置执行权限
        if platform.system().lower() in ["linux", "darwin"]:
            try:
                os.chmod(dest_path, 0o755)
                print(f"✓ 已设置执行权限")
            except Exception as e:
                print(f"⚠ 设置执行权限失败: {e}")
    
    return success


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

    # 获取安装目录
    install_dir = get_install_dir()
    dest_path = install_dir / lib_filename

    print(f"\n安装目录: {install_dir}")

    # 检查本地文件是否已存在
    if dest_path.exists():
        print(f"\n✓ 库文件已存在: {dest_path}")
        file_size = dest_path.stat().st_size
        print(f"  文件大小: {file_size:,} 字节")
        if not force:
            print("✓ 跳过下载")
            return True

    # 获取下载地址
    url = LIBRARY_URLS.get(platform_key)
    if not url or url is None:
        print(f"\n⚠️  该平台暂未提供自动下载: {platform_key}")
        print(f"\n提示:")
        print(f"  1. 请手动下载 {lib_filename}")
        print(f"  2. 将文件放置到: {install_dir}")
        print(f"  3. 或联系开发者获取该平台版本")
        print(f"\nQQ 群: 751406884, 545120699, 170902713, 616787804")
        print(f"官网: https://esunny.vip")
        return False

    # 如果强制下载，询问用户
    if dest_path.exists() and force:
        response = input("\n文件已存在，是否重新下载? (y/N): ").strip().lower()
        if response != "y":
            print("取消下载")
            return True

    # 确保目录存在
    install_dir.mkdir(parents=True, exist_ok=True)

    # 下载文件（可能需要临时文件名）
    print()

    # 检查 URL 中的文件名（用于 GitHub Releases）
    url_filename = url.split("/")[-1]

    # 如果 URL 文件名和本地文件名不同，先下载到临时位置
    if url_filename != lib_filename:
        temp_path = install_dir / url_filename
        success = download_file(url, temp_path)

        if success:
            # 重命名为最终文件名
            try:
                if dest_path.exists():
                    dest_path.unlink()
                temp_path.rename(dest_path)
                print(f"✓ 文件已重命名为: {lib_filename}")
            except Exception as e:
                print(f"⚠ 重命名失败: {e}")
                return False
    else:
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
