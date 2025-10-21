# SunnyNet Linux 使用指南

## 概述

SunnyNet v1.1.0 已支持 Linux 平台。本文档将指导你如何在 Linux 上安装和使用 SunnyNet。

## 系统要求

- Linux 操作系统（任何发行版）
- Python 3.7 或更高版本
- 64位系统（推荐）
- SunnyNet64.so 共享库文件

## 安装步骤

### 1. 安装 Python 包

```bash
pip install SunnyNet
```

### 2. 获取 Linux 库文件

你需要获取 `SunnyNet64.so` 共享库文件。请联系 SunnyNet 开发者或在以下渠道获取：

- QQ 群: 751406884
- QQ 群: 545120699
- QQ 群: 170902713
- QQ 群: 616787804
- 官网: https://esunny.vip

### 3. 放置库文件

将 `SunnyNet64.so` 文件放置在以下任一位置：

#### 选项 1: 包安装目录（推荐）

```bash
# 查找 SunnyNet 安装位置
python -c "import SunnyNet; import os; print(os.path.dirname(SunnyNet.__file__))"

# 将 .so 文件复制到该目录
sudo cp SunnyNet64.so /path/to/SunnyNet/
```

#### 选项 2: 当前工作目录

```bash
# 将 .so 文件复制到你的项目目录
cp SunnyNet64.so /path/to/your/project/
```

#### 选项 3: 系统库路径

```bash
# 复制到系统库目录
sudo cp SunnyNet64.so /usr/local/lib/

# 更新库缓存
sudo ldconfig
```

## 验证安装

运行以下命令验证安装是否成功：

```python
python << EOF
from SunnyNet import SunnyNet, Version
print(f"SunnyNet 版本: {Version()}")
print("安装成功!")
EOF
```

## 使用示例

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-

from SunnyNet.SunnyNet import SunnyNet
from SunnyNet.Event import HTTPEvent

def http_callback(conn: HTTPEvent):
    if conn.get_event_type() == conn.EVENT_TYPE_REQUEST:
        print(f"请求: {conn.get_url()}")
    elif conn.get_event_type() == conn.EVENT_TYPE_RESPONSE:
        print(f"响应: {conn.get_url()}")

# 创建实例
app = SunnyNet()
app.set_port(2025)

# 注意：Linux 上证书安装可能需要手动操作
# app.install_cert_to_system()

# 设置回调
app.set_callback(http_callback=http_callback)

# 启动服务
if app.start():
    print("SunnyNet 已在 Linux 上启动")
    print("监听端口: 2025")
    # 保持运行
    import time
    while True:
        time.sleep(1)
else:
    print(f"启动失败: {app.error()}")
```

## Linux 特别说明

### 1. 权限问题

某些功能可能需要 root 权限：

```bash
sudo python your_script.py
```

### 2. 防火墙配置

如果需要外部访问，请配置防火墙：

```bash
# UFW
sudo ufw allow 2025/tcp

# iptables
sudo iptables -A INPUT -p tcp --dport 2025 -j ACCEPT
```

### 3. 系统代理设置

Linux 上设置系统代理：

```bash
# 临时设置
export http_proxy="http://127.0.0.1:2025"
export https_proxy="http://127.0.0.1:2025"

# 或使用 gsettings (GNOME)
gsettings set org.gnome.system.proxy mode 'manual'
gsettings set org.gnome.system.proxy.http host '127.0.0.1'
gsettings set org.gnome.system.proxy.http port 2025
```

### 4. 证书安装

Linux 上手动安装证书：

```bash
# 导出证书
python -c "from SunnyNet.SunnyNet import SunnyNet; app = SunnyNet(); print(app.export_cert())" > sunny.crt

# 安装到系统（Ubuntu/Debian）
sudo cp sunny.crt /usr/local/share/ca-certificates/
sudo update-ca-certificates

# 安装到系统（CentOS/RHEL）
sudo cp sunny.crt /etc/pki/ca-trust/source/anchors/
sudo update-ca-trust
```

## 限制说明

在 Linux 平台上，以下功能暂不支持或需要额外配置：

1. **驱动模式**: `open_drive()` 不支持
2. **自动 IE 代理**: `set_ie_proxy()` 不支持
3. **进程注入**: 需要使用其他方法（如 iptables 重定向）

## 故障排除

### 问题 1: 找不到库文件

**错误信息**:
```
载入库文件失败: [Errno 2] No such file or directory: 'SunnyNet64.so'
```

**解决方法**:
1. 确认 `SunnyNet64.so` 文件存在
2. 检查文件权限: `chmod +x SunnyNet64.so`
3. 使用绝对路径测试

### 问题 2: 权限被拒绝

**错误信息**:
```
Permission denied
```

**解决方法**:
```bash
# 给予执行权限
chmod +x SunnyNet64.so

# 或使用 root 权限运行
sudo python your_script.py
```

### 问题 3: 依赖库缺失

**错误信息**:
```
libpthread.so.0: cannot open shared object file
```

**解决方法**:
```bash
# Ubuntu/Debian
sudo apt-get install libc6

# CentOS/RHEL
sudo yum install glibc
```

## 获取帮助

如果遇到问题，请：

1. 查看详细错误信息
2. 加入 QQ 群寻求帮助
3. 访问官网: https://esunny.vip

## 更多信息

- [主 README](README.md)
- [API 文档](https://esunny.vip)
- [示例代码](Dome.py)

