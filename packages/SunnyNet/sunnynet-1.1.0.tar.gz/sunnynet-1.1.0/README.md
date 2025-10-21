# SunnyNet - 网络中间件

SunnyNet 是一个强大的 Python 网络中间件库，提供 HTTP/HTTPS、TCP、UDP 和 WebSocket 代理功能。

## 功能特性

- 🌐 **HTTP/HTTPS 代理**: 支持 HTTP 和 HTTPS 请求拦截和修改
- 🔐 **SSL/TLS 支持**: 内置证书管理，支持 HTTPS 解密
- 🔌 **TCP/UDP 代理**: 完整的 TCP 和 UDP 连接管理
- 💬 **WebSocket 支持**: WebSocket 连接拦截和数据处理
- 🎯 **进程过滤**: 可按进程名称或 PID 进行网络捕获
- 🔧 **驱动支持**: 支持 NFAPI 和 Proxifier 驱动
- 🎲 **JA3 指纹伪装**: 支持随机 JA3 指纹，绕过指纹识别
- 📝 **脚本支持**: 内置脚本编辑器，支持动态脚本

## 安装

```bash
pip install SunnyNet
```

### 获取对应平台的库文件

SunnyNet 需要相应平台的库文件才能运行：

- **Windows**: `SunnyNet64.dll` (已包含在包中)
- **Linux**: `SunnyNet64.so` (需要单独提供)
- **macOS**: `SunnyNet64.dylib` (需要单独提供)

如果你在 Linux 或 macOS 上运行，请确保：
1. 下载对应平台的库文件
2. 将库文件放置在以下位置之一：
   - 包安装目录下的 `SunnyNet/` 文件夹
   - 当前工作目录
   - 或通过 `LD_LIBRARY_PATH` (Linux) / `DYLD_LIBRARY_PATH` (macOS) 环境变量指定

**注意**: 如果库文件不存在，会显示详细的错误提示和所需文件的位置。

## 快速开始

```python
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
app.install_cert_to_system()

# 设置回调
app.set_callback(http_callback=http_callback)

# 启动服务
if app.start():
    print("SunnyNet 已启动")
    app.set_ie_proxy()  # 设置系统代理
else:
    print(f"启动失败: {app.error()}")
```

## 主要模块

### SunnyNet - 主中间件类

```python
from SunnyNet.SunnyNet import SunnyNet

app = SunnyNet()
app.set_port(2025)  # 设置端口
app.start()  # 启动服务
app.stop()  # 停止服务
```

### HTTPClient - HTTP 客户端

```python
from SunnyNet.HTTPClient import SunnyHTTPClient

client = SunnyHTTPClient()
client.set_random_tls(True)  # 启用随机 TLS 指纹
client.open("GET", "https://example.com")
client.send()
print(client.get_body_string())
```

### CertManager - 证书管理

```python
from SunnyNet.CertManager import CertManager

cert = CertManager()
cert.create("example.com")
print(cert.export_pub_key())
```

### Queue - 消息队列

```python
from SunnyNet.Queue import Queue

queue = Queue("queue_name")
queue.create()
queue.push("message")
print(queue.pull_string())
```

## 进阶功能

### 进程过滤

```python
# 捕获指定进程
app.process_add_name("chrome.exe")
app.process_add_pid(1234)

# 捕获所有进程
app.process_all(True, False)
```

### 上游代理

```python
# 设置代理
app.set_proxy("http://127.0.0.1:8888", 30000)

# 设置代理规则
app.set_proxy_rules(".*google.*|.*facebook.*")
```

### 驱动模式

```python
# 加载 NFAPI 驱动（需要管理员权限）
if app.open_drive(True):
    print("驱动加载成功")
    app.process_all(True, False)
```

## 事件回调

### HTTP 事件

```python
def http_callback(conn: HTTPEvent):
    if conn.get_event_type() == conn.EVENT_TYPE_REQUEST:
        # 修改请求
        conn.get_request().set_header("User-Agent", "Custom UA")
    elif conn.get_event_type() == conn.EVENT_TYPE_RESPONSE:
        # 处理响应
        body = conn.get_response().body_auto_str()
```

### TCP 事件

```python
def tcp_callback(conn: TCPEvent):
    if conn.get_event_type() == conn.EVENT_TYPE_SEND:
        print(f"TCP 发送: {len(conn.get_body())} 字节")
    elif conn.get_event_type() == conn.EVENT_TYPE_RECEIVE:
        print(f"TCP 接收: {len(conn.get_body())} 字节")
```

### WebSocket 事件

```python
def ws_callback(conn: WebSocketEvent):
    if conn.get_event_type() == conn.EVENT_TYPE_SEND:
        print(f"WS 发送: {conn.get_body()}")
    elif conn.get_event_type() == conn.EVENT_TYPE_RECEIVE:
        print(f"WS 接收: {conn.get_body()}")
```

## 系统要求

### Windows
- Windows 7 及以上（需要 KB3033929 补丁用于 NFAPI 驱动）
- Python 3.7+
- 管理员权限（驱动模式需要）

### Linux
- Python 3.7+
- 需要 SunnyNet64.so 共享库文件
- 注意：Linux版本目前暂不支持驱动模式

### macOS
- Python 3.7+
- 需要 SunnyNet64.dylib 动态库文件
- 注意：macOS版本目前暂不支持驱动模式

## 注意事项

1. HTTPS 拦截需要安装证书：`app.install_cert_to_system()`
2. 驱动模式需要管理员权限（仅 Windows）
3. NFAPI 驱动在 Windows 7 上需要 KB3033929 补丁
4. Proxifier 驱动不支持 UDP 和 32 位系统
5. Linux 和 macOS 版本需要相应的共享库文件（.so 或 .dylib）
6. 跨平台支持：代码会自动检测操作系统并加载对应的库文件

## 许可证

MIT License

## 联系方式

- QQ 群: 751406884

## 更新日志

### v1.1.0 (2025-10-20)
- ✨ 新增跨平台支持（Windows、Linux、macOS）
- 🔧 自动检测操作系统并加载对应的库文件
- 📝 优化错误提示，显示详细的平台和路径信息
- 🐛 修复库文件路径查找逻辑
- 📚 更新文档，添加跨平台使用说明

### v1.0.0 (2025-04-13)
- 首次发布
- 支持 HTTP/HTTPS、TCP、UDP、WebSocket
- 支持进程过滤
- 支持驱动模式
- 支持 JA3 指纹伪装

