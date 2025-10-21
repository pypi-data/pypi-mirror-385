from setuptools import setup, find_packages
from setuptools.command.install import install
from setuptools.command.develop import develop
import os
import sys
import subprocess


class PostInstallCommand(install):
    """安装后执行的自定义命令"""

    def run(self):
        install.run(self)
        # 安装完成后尝试下载库文件
        try:
            print("\n" + "=" * 60)
            print("正在下载平台相关的库文件...")
            print("=" * 60)
            subprocess.check_call([sys.executable, "-m", "SunnyNet.download_libs"])
        except Exception as e:
            print(f"\n⚠ 自动下载库文件失败: {e}")
            print("请手动运行: python -m SunnyNet.download_libs")


class PostDevelopCommand(develop):
    """开发模式安装后执行的自定义命令"""

    def run(self):
        develop.run(self)
        try:
            print("\n正在下载平台相关的库文件...")
            subprocess.check_call([sys.executable, "-m", "SunnyNet.download_libs"])
        except Exception as e:
            print(f"\n⚠ 自动下载库文件失败: {e}")


# 读取README文件
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="SunnyNet",
    version="1.3.3",
    author="秦天",
    author_email="",
    description="SunnyNet网络中间件 - 强大的网络代理和抓包工具",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/SunnyNet",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Internet :: Proxy Servers",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.7",
    install_requires=[
        # 添加项目依赖
    ],
    include_package_data=True,
    package_data={
        "SunnyNet": ["*.dll", "*.so", "*.dylib"],
        "": ["*.dll", "*.so", "*.dylib"],
    },
    keywords="network proxy middleware http tcp udp websocket",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/SunnyNet/issues",
        "Source": "https://github.com/yourusername/SunnyNet",
    },
    cmdclass={
        "install": PostInstallCommand,
        "develop": PostDevelopCommand,
    },
)
