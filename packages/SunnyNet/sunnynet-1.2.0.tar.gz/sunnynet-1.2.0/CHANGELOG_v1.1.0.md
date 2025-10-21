# SunnyNet v1.1.0 更新说明

## 🎉 主要更新

### ✨ 跨平台支持

SunnyNet 现已支持多个操作系统平台：

- ✅ **Windows** - 完整支持（.dll）
- ✅ **Linux** - 核心功能支持（.so）
- ✅ **macOS** - 核心功能支持（.dylib）

## 📝 详细变更

### 核心功能

#### 1. 智能平台检测 (`SunnyNet/SunnyDLL.py`)

```python
# 自动检测操作系统
- Windows → 加载 .dll 文件
- Linux   → 加载 .so 文件  
- macOS   → 加载 .dylib 文件
```

**新增功能**:
- 自动检测操作系统类型
- 自动选择正确的库文件扩展名
- 智能搜索多个可能的库文件路径
- 详细的错误提示信息

#### 2. 库文件路径搜索

自动在以下位置搜索库文件：

1. 包安装目录 (`site-packages/SunnyNet/`)
2. 当前工作目录
3. 当前目录下的 `SunnyNet/` 子目录
4. 系统库路径

#### 3. 增强的错误提示

当库文件加载失败时，会显示：
- 当前操作系统信息
- 系统架构（32/64位）
- 尝试加载的文件路径
- 针对不同平台的解决建议

### 文档更新

#### 新增文档

1. **LINUX_USAGE.md** - Linux 平台详细使用指南
   - 安装步骤
   - 配置说明
   - 故障排除
   - 使用示例

2. **CHANGELOG_v1.1.0.md** - 本更新日志

#### 更新的文档

1. **README.md**
   - 添加跨平台系统要求说明
   - 添加库文件获取指南
   - 更新注意事项
   - 添加 v1.1.0 更新日志

### 打包配置更新

#### 修改的文件

1. **MANIFEST.in** - 包含 .so 和 .dylib 文件
2. **setup.py** - 更新 package_data
3. **pyproject.toml** - 更新包数据配置
4. **SunnyNet/__init__.py** - 版本号更新到 1.1.0

## 🔧 技术细节

### 代码改进

**之前**:
```python
# 硬编码 Windows DLL 路径
lib = CDLL("./SunnyNet64.dll")
```

**现在**:
```python
# 智能检测和加载
def _get_library_path():
    system = platform.system().lower()
    if system == "windows":
        lib_name = "SunnyNet64.dll"
    elif system == "linux":
        lib_name = "SunnyNet64.so"
    elif system == "darwin":
        lib_name = "SunnyNet64.dylib"
    # ... 智能路径搜索
    
lib = CDLL(lib_path)
```

### 新增依赖

- `platform` - 检测操作系统
- `os` - 路径操作
- `sys` - 系统信息

## 📦 升级指南

### 从 v1.0.0 升级到 v1.1.0

#### Windows 用户

无需额外操作，直接升级即可：

```bash
pip install --upgrade SunnyNet
```

#### Linux 用户

1. 升级 Python 包：
```bash
pip install --upgrade SunnyNet
```

2. 获取并放置 `SunnyNet64.so` 文件（联系开发者获取）

3. 验证安装：
```python
from SunnyNet import Version
print(Version())
```

#### macOS 用户

1. 升级 Python 包：
```bash
pip install --upgrade SunnyNet
```

2. 获取并放置 `SunnyNet64.dylib` 文件（联系开发者获取）

## ⚠️ 重要提示

### Linux/macOS 限制

以下功能在 Linux/macOS 上暂不支持：

1. ❌ **驱动模式** (`open_drive()`) - 仅 Windows 支持
2. ❌ **IE 代理设置** (`set_ie_proxy()`) - 仅 Windows 支持
3. ❌ **系统证书自动安装** - 需要手动安装

### 核心功能支持

以下功能在所有平台上都支持：

1. ✅ HTTP/HTTPS 代理
2. ✅ TCP/UDP 连接管理
3. ✅ WebSocket 支持
4. ✅ 请求/响应拦截和修改
5. ✅ JA3 指纹伪装
6. ✅ 上游代理设置

## 🐛 Bug 修复

- 修复库文件路径查找逻辑
- 优化错误提示信息
- 改进跨平台兼容性

## 📊 兼容性

### Python 版本

- Python 3.7+
- Python 3.8+
- Python 3.9+
- Python 3.10+
- Python 3.11+
- Python 3.13+ (已测试)

### 操作系统

| 平台 | 状态 | 核心功能 | 驱动模式 |
|------|------|---------|---------|
| Windows 7+ | ✅ 完整支持 | ✅ | ✅ |
| Windows 10/11 | ✅ 完整支持 | ✅ | ✅ |
| Linux | ✅ 核心支持 | ✅ | ❌ |
| macOS | ✅ 核心支持 | ✅ | ❌ |

## 🔜 未来计划

- [ ] 提供 Linux 和 macOS 的预编译库文件
- [ ] 改进 Linux 平台的进程捕获功能
- [ ] 添加更多平台的自动化测试
- [ ] 提供 Docker 镜像

## 💬 获取帮助

如有问题，请通过以下方式联系：

- QQ 群(一群): 751406884
- QQ 群(二群): 545120699
- QQ 群(三群): 170902713
- QQ 群(四群): 616787804
- QQ 频道: https://pd.qq.com/g/SunnyNetV5
- 官网: https://esunny.vip

## 🙏 致谢

感谢所有用户的反馈和建议，特别是对 Linux 支持的需求。

---

**发布日期**: 2025-10-20  
**版本**: v1.1.0  
**作者**: 秦天

