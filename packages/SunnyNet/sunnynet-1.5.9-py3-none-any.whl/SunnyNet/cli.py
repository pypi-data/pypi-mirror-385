#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SunnyNet 命令行工具
"""

import sys
import argparse
from pathlib import Path


def get_global_lib_dir():
    """获取全局库文件目录"""
    import os
    import platform

    system = platform.system().lower()

    if system == "windows":
        # Windows: %APPDATA%\SunnyNet
        base = os.environ.get("APPDATA", os.path.expanduser("~"))
        lib_dir = Path(base) / "SunnyNet" / "lib"
    else:
        # Linux/Mac: ~/.sunnynet/lib
        lib_dir = Path.home() / ".sunnynet" / "lib"

    return lib_dir


def install_command(args):
    """安装库文件到全局目录"""
    # 延迟导入，避免触发 SunnyNet 主模块加载 DLL
    import platform

    # 手动实现必要的函数，避免导入 download_libs（它会导入 SunnyDLL）
    def get_platform_key():
        import struct

        system = platform.system().lower()
        # 使用 struct.calcsize("P") 检测 Python 位数（最可靠的方法）
        # P = 指针大小，8字节=64位，4字节=32位
        is_64bit = struct.calcsize("P") == 8
        arch = "64" if is_64bit else "32"
        return f"{system}_{arch}"

    def get_library_filename():
        import struct

        system = platform.system().lower()
        # 使用 struct.calcsize("P") 检测 Python 位数
        is_64bit = struct.calcsize("P") == 8  # 8字节 = 64位
        if system == "windows":
            return "SunnyNet64.dll" if is_64bit else "SunnyNet.dll"
        elif system == "linux":
            return "libSunnyNet.so"
        elif system == "darwin":
            return "SunnyNet64.dylib" if is_64bit else "SunnyNet.dylib"
        return None

    # 获取下载URL（硬编码，避免导入）
    from . import download_libs  # 只导入这个模块，不导入主包

    print("=" * 60)
    print("SunnyNet 库文件安装")
    print("=" * 60)

    # 获取全局目录
    global_dir = get_global_lib_dir()

    print(f"\n全局安装目录: {global_dir}")

    # 获取平台信息
    system = platform.system()
    platform_key = get_platform_key()
    lib_filename = get_library_filename()

    print(f"操作系统: {system}")
    print(f"平台标识: {platform_key}")
    print(f"库文件名: {lib_filename}")

    # 获取下载地址
    url = download_libs.LIBRARY_URLS.get(platform_key)

    if not url or url is None:
        print(f"\n[!] Platform not supported for auto-download")
        print(f"Please manually download {lib_filename} and place to: {global_dir}")
        return 1

    # 创建目录
    global_dir.mkdir(parents=True, exist_ok=True)

    # 下载
    dest_path = global_dir / lib_filename

    if dest_path.exists() and not args.force:
        print(f"\n[+] Library file exists: {dest_path}")

        response = input("\n是否重新下载? (y/N): ").strip().lower()
        if response != "y":
            print("Skip download")
            return 0

    print(f"\n开始下载...")
    print(f"URL: {url}")

    success = download_libs.download_library_to_path(url, dest_path, lib_filename)

    if success:
        print("\n" + "=" * 60)
        print("[+] Library file installed successfully!")
        print("=" * 60)
        print(f"\n安装位置: {dest_path}")
        print(f"\n现在可以在任何项目中使用 SunnyNet 了！")
        return 0
    else:
        print("\n[-] Installation failed")
        return 1


def info_command(args):
    """显示安装信息"""
    import platform

    def get_library_filename():
        system = platform.system().lower()
        # 使用 sys.maxsize 更可靠地检测 Python 位数
        is_64bit = sys.maxsize > 2**31
        if system == "windows":
            return "SunnyNet64.dll" if is_64bit else "SunnyNet.dll"
        elif system == "linux":
            return "libSunnyNet.so"
        elif system == "darwin":
            return "SunnyNet64.dylib" if is_64bit else "SunnyNet.dylib"
        return None

    print("=" * 60)
    print("SunnyNet 安装信息")
    print("=" * 60)

    # 系统信息
    print(f"\n操作系统: {platform.system()}")
    print(f"架构: {platform.machine()}")
    print(f"Python: {sys.version.split()[0]}")

    # 全局目录
    global_dir = get_global_lib_dir()
    lib_filename = get_library_filename()
    global_lib = global_dir / lib_filename

    print(f"\n全局库目录: {global_dir}")
    print(f"库文件名: {lib_filename}")

    if global_lib.exists():
        size = global_lib.stat().st_size / 1024 / 1024
        print(f"\n[+] Library file installed")
        print(f"  位置: {global_lib}")
        print(f"  大小: {size:.2f} MB")
    else:
        print(f"\n[-] Library file not installed")
        print(f"\n运行以下命令安装:")
        print(f"  sunnynet install")

    # 包安装目录
    try:
        import SunnyNet

        package_dir = Path(SunnyNet.__file__).parent
        package_lib = package_dir / lib_filename

        print(f"\n包安装目录: {package_dir}")

        if package_lib.exists():
            size = package_lib.stat().st_size / 1024 / 1024
            print(f"[+] Package directory also has library file ({size:.2f} MB)")
        else:
            print(f"[-] Package directory does not have library file")
    except:
        pass

    print("\n" + "=" * 60)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(prog="sunnynet", description="SunnyNet 命令行工具")

    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # install 命令
    install_parser = subparsers.add_parser(
        "install", aliases=["i"], help="安装库文件到全局目录"
    )
    install_parser.add_argument(
        "-f", "--force", action="store_true", help="强制重新下载"
    )

    # info 命令
    info_parser = subparsers.add_parser("info", help="显示安装信息")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 0

    # 执行命令
    if args.command in ["install", "i"]:
        return install_command(args)
    elif args.command == "info":
        return info_command(args)
    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())
