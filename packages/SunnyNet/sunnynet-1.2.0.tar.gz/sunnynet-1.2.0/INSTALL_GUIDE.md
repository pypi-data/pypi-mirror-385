# SunnyNet 安装和发布指南

## 🔧 配置自动下载功能

SunnyNet v1.1.0 支持在 pip 安装时自动下载对应平台的库文件。

### 步骤 1: 配置下载地址

#### 方法 A: 修改配置文件

1. 编辑 `SunnyNet/library_urls.py` 文件
2. 将示例 URL 替换为实际的下载地址：

```python
LIBRARY_URLS = {
    "windows_64": "https://your-server.com/downloads/SunnyNet64.dll",
    "windows_32": "https://your-server.com/downloads/SunnyNet.dll",
    "linux_64": "https://your-server.com/downloads/SunnyNet64.so",
    "linux_32": "https://your-server.com/downloads/SunnyNet.so",
    "darwin_64": "https://your-server.com/downloads/SunnyNet64.dylib",
    "darwin_32": "https://your-server.com/downloads/SunnyNet.dylib",
}
```

#### 方法 B: 使用环境变量

用户可以通过环境变量覆盖下载地址：

```bash
export SUNNYNET_WINDOWS_64_URL="https://your-url.com/SunnyNet64.dll"
export SUNNYNET_LINUX_64_URL="https://your-url.com/SunnyNet64.so"
```

### 步骤 2: 托管库文件

#### 推荐方案 1: GitHub Releases

1. 在 GitHub 仓库创建 Release
2. 上传各平台的库文件
3. 使用 Release 的下载链接

```python
LIBRARY_URLS = {
    "windows_64": "https://github.com/user/repo/releases/download/v1.1.0/SunnyNet64.dll",
    "linux_64": "https://github.com/user/repo/releases/download/v1.1.0/SunnyNet64.so",
    # ...
}
```

#### 推荐方案 2: 云存储 CDN

使用阿里云 OSS、腾讯云 COS、AWS S3 等：

```python
BASE_URL = "https://your-bucket.oss-cn-hangzhou.aliyuncs.com/sunnynet"
LIBRARY_URLS = {
    "windows_64": f"{BASE_URL}/SunnyNet64.dll",
    "linux_64": f"{BASE_URL}/SunnyNet64.so",
    # ...
}
```

#### 推荐方案 3: 官网服务器

```python
LIBRARY_URLS = {
    "windows_64": "https://esunny.vip/downloads/SunnyNet64.dll",
    "linux_64": "https://esunny.vip/downloads/SunnyNet64.so",
    # ...
}
```

### 步骤 3: 构建并发布

```bash
# 清理旧文件
rm -rf dist build *.egg-info

# 构建包
python -m build

# 检查包
python -m twine check dist/*

# 上传到 PyPI
python -m twine upload --username __token__ --password YOUR_TOKEN dist/*
```

## 📦 用户安装体验

### 自动安装（推荐）

配置好下载地址后，用户只需：

```bash
pip install SunnyNet
```

安装过程中会自动：
1. 检测操作系统和架构
2. 下载对应的库文件
3. 安装到正确的位置

输出示例：
```
Installing collected packages: SunnyNet
  Running setup.py install for SunnyNet ... 
============================================================
正在下载平台相关的库文件...
============================================================

系统信息:
  操作系统: Linux
  平台标识: linux_64
  需要文件: SunnyNet64.so

正在下载: https://example.com/SunnyNet64.so
下载进度: 100.0% (40592384/40592384 字节)
✓ 下载完成

✓ 库文件下载并安装成功!
Successfully installed SunnyNet-1.1.0
```

### 手动安装（备用）

如果自动下载失败，用户可以手动操作：

```bash
# 方法 1: 使用命令行工具
sunnynet-download

# 方法 2: 作为模块运行
python -m SunnyNet.download_libs

# 方法 3: 指定自定义 URL
sunnynet-download --url https://your-url.com/SunnyNet64.so

# 方法 4: 强制重新下载
sunnynet-download --force
```

### 离线安装

用户也可以完全手动放置库文件：

```bash
# 1. 下载库文件到本地
wget https://example.com/SunnyNet64.so

# 2. 找到安装目录
python -c "import SunnyNet; import os; print(os.path.dirname(SunnyNet.__file__))"

# 3. 复制库文件
cp SunnyNet64.so /path/to/SunnyNet/
```

## 🔐 安全建议

### HTTPS 支持

确保下载地址使用 HTTPS：

```python
# ✓ 推荐
"windows_64": "https://example.com/SunnyNet64.dll"

# ✗ 不推荐
"windows_64": "http://example.com/SunnyNet64.dll"
```

### 文件校验（可选）

可以添加 SHA256 校验：

```python
LIBRARY_CHECKSUMS = {
    "windows_64": "abc123...",
    "linux_64": "def456...",
}
```

## 🧪 测试自动下载

在发布前测试自动下载功能：

```bash
# 1. 构建包
python -m build

# 2. 在虚拟环境中测试
python -m venv test_env
source test_env/bin/activate  # Linux/Mac
# test_env\Scripts\activate  # Windows

# 3. 安装测试
pip install dist/sunnynet-1.1.0-py3-none-any.whl

# 4. 验证
python -c "from SunnyNet import Version; print(Version())"

# 5. 检查库文件
ls -la $(python -c "import SunnyNet; import os; print(os.path.dirname(SunnyNet.__file__))")
```

## ❓ 常见问题

### Q1: 下载失败怎么办？

**A:** 自动下载失败时会提示用户手动下载：

```
⚠ 自动下载库文件失败
请手动运行: python -m SunnyNet.download_libs
或手动下载文件到: /path/to/SunnyNet/
```

### Q2: 如何支持离线安装？

**A:** 将库文件直接打包到 wheel 中：

```bash
# 将 DLL/SO 文件放到 SunnyNet/ 目录
cp SunnyNet64.dll SunnyNet/
cp SunnyNet64.so SunnyNet/

# 构建时会自动包含
python -m build
```

### Q3: 如何更新下载地址？

**A:** 发布新版本前更新 `SunnyNet/library_urls.py` 即可。

### Q4: 能否按需下载？

**A:** 当前实现会在安装后自动下载当前平台的库文件，不会下载其他平台的文件。

## 📊 不同方案对比

| 方案 | 优点 | 缺点 | 推荐度 |
|------|------|------|--------|
| GitHub Releases | 免费、稳定 | 国内速度慢 | ⭐⭐⭐⭐ |
| 云存储 CDN | 速度快、稳定 | 需要付费 | ⭐⭐⭐⭐⭐ |
| 自建服务器 | 完全控制 | 需要维护 | ⭐⭐⭐ |
| 打包到 wheel | 离线可用 | 包体积大 | ⭐⭐⭐⭐ |

## 🚀 最佳实践

### 推荐方案：混合方式

1. **Windows DLL** - 直接打包到 wheel（用户最多）
2. **Linux SO** - 自动下载（服务器用户可联网）
3. **macOS dylib** - 自动下载（用户较少）

配置示例：

```python
# SunnyNet/library_urls.py
LIBRARY_URLS = {
    # Windows 已打包，不需要下载
    "windows_64": None,  
    "windows_32": None,
    
    # Linux/Mac 自动下载
    "linux_64": "https://cdn.example.com/SunnyNet64.so",
    "darwin_64": "https://cdn.example.com/SunnyNet64.dylib",
}
```

## 📝 更新 README

记得在 README 中说明安装过程：

```markdown
## 安装

```bash
pip install SunnyNet
```

安装时会自动下载对应平台的库文件。如果自动下载失败：

```bash
# 手动下载
sunnynet-download

# 或者手动放置库文件到包目录
```
\`\`\`
```

---

**更新日期**: 2025-10-20  
**版本**: v1.1.0

