#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SunnyNet 库文件下载地址配置
请在这里配置各平台库文件的下载地址
"""

# GitHub 仓库配置
GITHUB_REPO = "kiss-kedaya/SunnyNet"
RELEASE_VERSION = "v1.3.3"  # 发布版本号

# 使用 GitHub Releases 下载（适合大文件，无大小限制）
# 格式: https://github.com/{user}/{repo}/releases/download/{version}/{filename}
# 优点：稳定、无文件大小限制、官方支持
RELEASE_BASE = f"https://github.com/{GITHUB_REPO}/releases/download/{RELEASE_VERSION}"

# 库文件下载地址
# 格式: "平台_架构": "下载地址"
LIBRARY_URLS = {
    # Windows 平台 - 从 GitHub Releases 下载 ✅
    "windows_64": f"{RELEASE_BASE}/SunnyNet64.dll",
    "windows_32": f"{RELEASE_BASE}/SunnyNet.dll",
    # Linux 平台 - 从 GitHub Releases 下载 ✅
    # 重命名文件以区分架构
    "linux_64": f"{RELEASE_BASE}/libSunnyNet-arm64.so",  # ARM 64位
    "linux_32": f"{RELEASE_BASE}/libSunnyNet-x86.so",  # x86 32位
    # macOS 平台
    "darwin_64": None,  # 暂未提供 macOS 版本
    "darwin_32": None,
}

# 可选：使用 GitHub Releases (更稳定，推荐用于正式版本)
# 取消下面的注释来使用 Releases 方式
# RELEASE_VERSION = "v1.1.0"
# RELEASE_BASE = f"https://github.com/{GITHUB_REPO}/releases/download/{RELEASE_VERSION}"
# LIBRARY_URLS = {
#     "windows_64": f"{RELEASE_BASE}/SunnyNet64.dll",
#     "windows_32": f"{RELEASE_BASE}/SunnyNet.dll",
#     "linux_64": f"{RELEASE_BASE}/SunnyNet64.so",
#     "linux_32": f"{RELEASE_BASE}/SunnyNet.so",
#     "darwin_64": f"{RELEASE_BASE}/SunnyNet64.dylib",
#     "darwin_32": f"{RELEASE_BASE}/SunnyNet.dylib",
# }


def get_library_url(system, arch):
    """
    获取指定平台的库文件下载地址

    Args:
        system: 操作系统名称 (windows/linux/darwin)
        arch: 架构 (32/64)

    Returns:
        str: 下载地址，如果未配置则返回 None
    """
    platform_key = f"{system.lower()}_{arch}"
    return LIBRARY_URLS.get(platform_key)


def set_library_url(system, arch, url):
    """
    设置指定平台的库文件下载地址

    Args:
        system: 操作系统名称 (windows/linux/darwin)
        arch: 架构 (32/64)
        url: 下载地址
    """
    platform_key = f"{system.lower()}_{arch}"
    LIBRARY_URLS[platform_key] = url
