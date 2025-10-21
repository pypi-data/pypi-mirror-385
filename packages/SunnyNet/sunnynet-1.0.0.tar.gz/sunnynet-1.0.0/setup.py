from setuptools import setup, find_packages
import os

# 读取README文件
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="SunnyNet",
    version="1.0.0",
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
        'SunnyNet': ['*.dll'],
        '': ['*.dll'],
    },
    keywords="network proxy middleware http tcp udp websocket",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/SunnyNet/issues",
        "Source": "https://github.com/yourusername/SunnyNet",
    },
)

