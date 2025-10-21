#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SunnyNet 库文件下载地址配置示例

使用方法：
1. 复制此文件到 SunnyNet/library_urls.py
2. 将下面的示例地址替换为实际的下载地址
3. 重新构建和发布包

推荐方案：
- 使用 CDN 或云存储服务托管库文件
- 使用 GitHub Releases 托管
- 使用自己的服务器
"""

# 库文件下载地址
# 格式: "平台_架构": "下载地址"
LIBRARY_URLS = {
    # Windows 平台
    # 示例: "windows_64": "https://github.com/user/repo/releases/download/v1.0/SunnyNet64.dll"
    "windows_64": "https://your-cdn.com/downloads/SunnyNet64.dll",
    "windows_32": "https://your-cdn.com/downloads/SunnyNet.dll",
    # Linux 平台
    # 示例: "linux_64": "https://github.com/user/repo/releases/download/v1.0/SunnyNet64.so"
    "linux_64": "https://your-cdn.com/downloads/SunnyNet64.so",
    "linux_32": "https://your-cdn.com/downloads/SunnyNet.so",
    # macOS 平台
    # 示例: "darwin_64": "https://github.com/user/repo/releases/download/v1.0/SunnyNet64.dylib"
    "darwin_64": "https://your-cdn.com/downloads/SunnyNet64.dylib",
    "darwin_32": "https://your-cdn.com/downloads/SunnyNet.dylib",
}


# 以下是几个托管方案示例：

# 方案 1: GitHub Releases
"""
LIBRARY_URLS = {
    "windows_64": "https://github.com/yourusername/SunnyNet/releases/download/v1.1.0/SunnyNet64.dll",
    "windows_32": "https://github.com/yourusername/SunnyNet/releases/download/v1.1.0/SunnyNet.dll",
    "linux_64": "https://github.com/yourusername/SunnyNet/releases/download/v1.1.0/SunnyNet64.so",
    "linux_32": "https://github.com/yourusername/SunnyNet/releases/download/v1.1.0/SunnyNet.so",
    "darwin_64": "https://github.com/yourusername/SunnyNet/releases/download/v1.1.0/SunnyNet64.dylib",
    "darwin_32": "https://github.com/yourusername/SunnyNet/releases/download/v1.1.0/SunnyNet.dylib",
}
"""

# 方案 2: 自建服务器
"""
BASE_URL = "https://esunny.vip/downloads"
LIBRARY_URLS = {
    "windows_64": f"{BASE_URL}/SunnyNet64.dll",
    "windows_32": f"{BASE_URL}/SunnyNet.dll",
    "linux_64": f"{BASE_URL}/SunnyNet64.so",
    "linux_32": f"{BASE_URL}/SunnyNet.so",
    "darwin_64": f"{BASE_URL}/SunnyNet64.dylib",
    "darwin_32": f"{BASE_URL}/SunnyNet.dylib",
}
"""

# 方案 3: 阿里云 OSS / 腾讯云 COS
"""
LIBRARY_URLS = {
    "windows_64": "https://your-bucket.oss-cn-hangzhou.aliyuncs.com/sunnynet/SunnyNet64.dll",
    "linux_64": "https://your-bucket.oss-cn-hangzhou.aliyuncs.com/sunnynet/SunnyNet64.so",
    # ...
}
"""


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
