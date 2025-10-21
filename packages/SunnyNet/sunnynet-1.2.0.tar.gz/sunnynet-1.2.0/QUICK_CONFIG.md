# SunnyNet 自动下载配置快速指南

## 📝 配置下载地址

### 第1步：编辑配置文件

打开 `SunnyNet/library_urls.py`，填入实际的下载地址：

```python
# SunnyNet/library_urls.py

LIBRARY_URLS = {
    # Windows 64位 DLL
    "windows_64": "https://你的服务器.com/SunnyNet64.dll",
    
    # Windows 32位 DLL
    "windows_32": "https://你的服务器.com/SunnyNet.dll",
    
    # Linux 64位 SO
    "linux_64": "https://你的服务器.com/SunnyNet64.so",
    
    # Linux 32位 SO
    "linux_32": "https://你的服务器.com/SunnyNet.so",
    
    # macOS 64位 dylib
    "darwin_64": "https://你的服务器.com/SunnyNet64.dylib",
    
    # macOS 32位 dylib
    "darwin_32": "https://你的服务器.com/SunnyNet.dylib",
}
```

### 第2步：常见配置示例

#### 示例 1: 使用 GitHub Releases

```python
BASE = "https://github.com/yourusername/SunnyNet/releases/download/v1.1.0"

LIBRARY_URLS = {
    "windows_64": f"{BASE}/SunnyNet64.dll",
    "windows_32": f"{BASE}/SunnyNet.dll",
    "linux_64": f"{BASE}/SunnyNet64.so",
    "linux_32": f"{BASE}/SunnyNet.so",
    "darwin_64": f"{BASE}/SunnyNet64.dylib",
    "darwin_32": f"{BASE}/SunnyNet.dylib",
}
```

#### 示例 2: 使用官网服务器

```python
LIBRARY_URLS = {
    "windows_64": "https://esunny.vip/downloads/lib/SunnyNet64.dll",
    "linux_64": "https://esunny.vip/downloads/lib/SunnyNet64.so",
    "darwin_64": "https://esunny.vip/downloads/lib/SunnyNet64.dylib",
    # 如果不提供32位版本，可以设置为 None
    "windows_32": None,
    "linux_32": None,
    "darwin_32": None,
}
```

#### 示例 3: 使用云存储 CDN

```python
# 阿里云 OSS
CDN = "https://your-bucket.oss-cn-beijing.aliyuncs.com/sunnynet"

# 腾讯云 COS
# CDN = "https://your-bucket-123456.cos.ap-guangzhou.myqcloud.com/sunnynet"

LIBRARY_URLS = {
    "windows_64": f"{CDN}/SunnyNet64.dll",
    "linux_64": f"{CDN}/SunnyNet64.so",
    "darwin_64": f"{CDN}/SunnyNet64.dylib",
}
```

### 第3步：测试配置

在构建前测试下载地址是否有效：

```bash
# 测试 Windows 64位
curl -I "https://your-url.com/SunnyNet64.dll"

# 测试 Linux 64位
curl -I "https://your-url.com/SunnyNet64.so"
```

### 第4步：构建并发布

```bash
# 清理旧文件
rm -rf dist build *.egg-info

# 构建
python -m build

# 检查
python -m twine check dist/*

# 上传
python -m twine upload --username __token__ --password YOUR_TOKEN dist/*
```

## ⚙️ 高级配置

### 方案 A: 只为 Windows 打包 DLL，其他平台自动下载

这样可以减小包体积，同时保证 Windows 用户（占大多数）的体验：

```python
# SunnyNet/library_urls.py
LIBRARY_URLS = {
    # Windows DLL 已打包在 wheel 中，不需要下载
    "windows_64": None,
    "windows_32": None,
    
    # Linux/Mac 用户自动下载
    "linux_64": "https://your-cdn.com/SunnyNet64.so",
    "darwin_64": "https://your-cdn.com/SunnyNet64.dylib",
}
```

### 方案 B: 所有平台都自动下载

最小化包体积：

```python
LIBRARY_URLS = {
    "windows_64": "https://your-cdn.com/SunnyNet64.dll",
    "linux_64": "https://your-cdn.com/SunnyNet64.so",
    "darwin_64": "https://your-cdn.com/SunnyNet64.dylib",
}
```

同时从 `SunnyNet/` 目录删除 DLL 文件：

```bash
rm SunnyNet/SunnyNet64.dll
```

### 方案 C: 使用环境变量（用户自定义）

用户可以通过环境变量指定下载地址：

```python
# SunnyNet/download_libs.py 中添加
import os

def get_library_url_from_env(platform_key):
    """从环境变量获取下载地址"""
    env_key = f"SUNNYNET_{platform_key.upper().replace('_', '_')}_URL"
    return os.getenv(env_key)
```

用户使用：

```bash
export SUNNYNET_LINUX_64_URL="https://custom-url.com/SunnyNet64.so"
pip install SunnyNet
```

## 📋 检查清单

发布前检查：

- [ ] 已配置所有平台的下载地址
- [ ] 下载地址可正常访问（返回 200）
- [ ] 库文件大小合理（~40MB）
- [ ] 使用 HTTPS 协议
- [ ] 测试在虚拟环境中安装
- [ ] 测试自动下载功能
- [ ] 更新 README 说明
- [ ] 更新版本号

## 🔍 故障排查

### 问题：下载地址返回 404

```bash
# 检查 URL
curl -I "https://your-url.com/SunnyNet64.dll"
```

### 问题：下载被防火墙阻止

尝试使用国内 CDN或镜像。

### 问题：SSL 证书错误

确保服务器配置了有效的 SSL 证书。

## 💡 提示

1. **使用 CDN**: 提供更快的下载速度
2. **设置缓存**: 减少服务器压力
3. **压缩文件**: 考虑使用 .gz 压缩
4. **版本管理**: URL 中包含版本号
5. **备用地址**: 配置多个下载源

---

**需要帮助？** 加入 QQ 群：751406884

