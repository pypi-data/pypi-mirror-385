from setuptools import setup, find_packages
from setuptools.command.install import install
from setuptools.command.develop import develop
import sys
import subprocess


class PostInstallCommand(install):
    """安装后执行的自定义命令"""

    def run(self):
        install.run(self)
        # 安装完成后尝试下载库文件
        # 仅在实际pip install时执行，构建wheel时跳过
        import os

        # 检测是否在wheel构建过程中
        if "bdist_wheel" in sys.argv or os.environ.get("PIP_BUILD_TRACKER"):
            # wheel构建过程，跳过
            print("\n[提示] 首次使用前请运行: sunnynet install")
            return

        # 检查是否在交互式终端中
        try:
            if not sys.stdin.isatty():
                print("\n[提示] 首次使用前请运行: sunnynet install")
                return
        except:
            # 某些环境可能不支持isatty()
            print("\n[提示] 首次使用前请运行: sunnynet install")
            return

        try:
            print("\n" + "=" * 60)
            print("正在下载平台相关的库文件...")
            print("=" * 60)
            # 尝试使用 sunnynet install 命令
            try:
                subprocess.check_call(["sunnynet", "install"])
            except (subprocess.CalledProcessError, FileNotFoundError):
                # 如果 sunnynet 命令不可用，使用模块方式调用
                subprocess.check_call([sys.executable, "-m", "SunnyNet.cli", "install"])
        except Exception as e:
            print(f"\n[!] Auto-download library failed: {e}")
            print("Please run manually: sunnynet install")


class PostDevelopCommand(develop):
    """开发模式安装后执行的自定义命令"""

    def run(self):
        develop.run(self)
        # 检查是否在交互式终端中
        import os

        # 检查是否在交互式终端中
        try:
            if not sys.stdin.isatty():
                print("\n[提示] 首次使用前请运行: sunnynet install")
                return
        except:
            print("\n[提示] 首次使用前请运行: sunnynet install")
            return

        try:
            print("\n正在下载平台相关的库文件...")
            # 尝试使用 sunnynet install 命令
            try:
                subprocess.check_call(["sunnynet", "install"])
            except (subprocess.CalledProcessError, FileNotFoundError):
                # 如果 sunnynet 命令不可用，使用模块方式调用
                subprocess.check_call([sys.executable, "-m", "SunnyNet.cli", "install"])
        except Exception as e:
            print(f"\n[!] Auto-download library failed: {e}")
            print("Please run manually: sunnynet install")


# 读取README文件
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="SunnyNet",
    version="1.5.13",
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
