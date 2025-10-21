# libimobiledevice-wrapper

一个基于 libimobiledevice 的 Python 封装工具，支持 iOS 设备管理和自动化操作。

## 功能特性

- 🔧 完整的 libimobiledevice 命令封装
- ⚡ 异步支持（asyncio）
- 🛡️ 统一的错误处理机制
- 🖥️ 命令行工具（CLI）
- 🚀 WebDriverAgent 接口支持
- 📱 iOS 设备管理
- 🔍 设备信息获取
- 📦 应用安装和管理

## 安装

### 前置要求

确保系统已安装 libimobiledevice：

```bash
# macOS
brew install libimobiledevice

# Ubuntu/Debian
sudo apt-get install libimobiledevice6 libimobiledevice-utils

# CentOS/RHEL
sudo yum install libimobiledevice
```

### Python 包安装

```bash
pip install libimobiledevice-wrapper
```

或从源码安装：

```bash
git clone https://github.com/Huang-Jacky/libimobiledevice-wrapper.git
cd libimobiledevice-wrapper
pip install -e .
```

## 快速开始

### 基本使用

```python
from libimobiledevice_wrapper import LibiMobileDevice

# 同步使用
device = LibiMobileDevice()
devices = device.list_devices()
print(f"连接的设备: {devices}")

# 异步使用
import asyncio

async def main():
    device = LibiMobileDevice()
    devices = await device.list_devices_async()
    print(f"连接的设备: {devices}")

asyncio.run(main())
```

### 命令行工具（两种用法）

1) 全局命令（推荐）

安装后会提供可执行命令 `libidevice`：

```bash
# 列出连接的设备
libidevice list-devices

# 获取设备信息
libidevice info --udid <device_udid>

# 安装应用
libidevice install --udid <device_udid> /path/to/app.ipa

# 获取应用信息
libidevice app-info --udid <device_udid> --bundle-id com.example.app

# 简洁日志捕获
device = LibiMobileDevice()
monitor = device.monitor_device_logs(
    udid="<device_udid>",
    keywords=["error", "MTG"],
    log_file_path="logs.txt",
    duration=60  # 60秒后自动停止
)
monitor.start()
time.sleep(30)  # 捕获30秒
monitor.stop()  # 自动保存到文件

# 或使用上下文管理器
with device.monitor_device_logs(udid="<device_udid>", keywords=["error"], log_file_path="logs.txt") as monitor:
    time.sleep(30)
# 自动停止并保存

# 启动应用
libidevice launch --udid <device_udid> --bundle-id com.example.app
```

**注意：启动应用功能需要开发者磁盘镜像支持**
- 如果遇到 "Could not start com.apple.debugserver!" 错误
- 需要先挂载开发者磁盘镜像：`ideviceimagemounter -u <udid> <path_to_DeveloperDiskImage.dmg>`
- 或者手动在设备上启动应用，然后使用日志监控功能

遇到找不到命令时：
- 使用 PyPI 安装：`python3 -m pip install libimobiledevice-wrapper`（然后执行 `pyenv rehash` 如使用 pyenv）
- 或使用完整路径（示例）：`~/.pyenv/versions/3.10.6/bin/libidevice list-devices`
- 或参考第 2 种用法（模块方式）

2) 模块方式（备用）

```bash
# 列出连接的设备
python3 -m libimobiledevice_wrapper.cli list-devices

# 获取设备信息
python3 -m libimobiledevice_wrapper.cli info --udid <device_udid>

# 安装应用
python3 -m libimobiledevice_wrapper.cli install --udid <device_udid> /path/to/app.ipa

# 获取应用信息
python3 -m libimobiledevice_wrapper.cli app-info --udid <device_udid> --bundle-id com.example.app

# 获取设备日志
python3 -m libimobiledevice_wrapper.cli device-logs --udid <device_udid> --duration 60 --keywords "error,exception"

# 实时监控设备日志
python3 -m libimobiledevice_wrapper.cli device-logs --udid <device_udid> --keywords "error"

# 启动应用
python3 -m libimobiledevice_wrapper.cli launch --udid <device_udid> --bundle-id com.example.app
```

**注意：启动应用功能需要开发者磁盘镜像支持**
- 如果遇到 "Could not start com.apple.debugserver!" 错误
- 需要先挂载开发者磁盘镜像：`ideviceimagemounter -u <udid> <path_to_DeveloperDiskImage.dmg>`
- 或者手动在设备上启动应用，然后使用日志监控功能

## API 文档

### LibiMobileDevice 类

主要的设备管理类，提供所有 libimobiledevice 功能的封装。

#### 设备管理

- `list_devices()` - 列出连接的设备
- `get_device_info(udid)` - 获取设备信息
- `get_device_props(udid)` - 获取设备属性

#### 应用管理

- `install_app(udid, app_path)` - 安装应用
- `uninstall_app(udid, bundle_id)` - 卸载应用
- `list_apps(udid)` - 列出已安装应用
- `get_app_info(udid, bundle_id)` - 获取指定应用的详细信息
- `launch_app(udid, bundle_id)` - 启动应用（需要开发者磁盘镜像支持）

#### 文件操作

- `pull_file(udid, remote_path, local_path)` - 从设备拉取文件
- `push_file(udid, local_path, remote_path)` - 推送文件到设备

#### 系统操作

- `reboot_device(udid)` - 重启设备
- `shutdown_device(udid)` - 关机设备

#### 日志管理

- `get_device_logs(udid, duration, keywords)` - 获取设备日志
- `monitor_device_logs(udid, keywords, callback, log_file_path, duration)` - 实时监控设备日志
  - 自动保存到文件，无需手动调用 save_logs
  - 支持关键字过滤
  - 支持指定时长自动停止
  - 支持上下文管理器

## 错误处理

所有方法都包含统一的错误处理：

```python
from libimobiledevice_wrapper import LibiMobileDeviceError

try:
    device = LibiMobileDevice()
    devices = device.list_devices()
except LibiMobileDeviceError as e:
    print(f"设备操作失败: {e}")
```

## 异步支持

所有方法都提供异步版本：

```python
import asyncio
from libimobiledevice_wrapper import LibiMobileDevice

async def main():
    device = LibiMobileDevice()
    
    # 异步方法以 _async 结尾
    devices = await device.list_devices_async()
    info = await device.get_device_info_async(devices[0])
    
asyncio.run(main())
```

## WebDriverAgent 支持

```python
from libimobiledevice_wrapper import WebDriverAgent

wda = WebDriverAgent(device_udid="<device_udid>")
await wda.start()
session = await wda.create_session()
```

## 开发

### 运行测试

```bash
pytest
```

### 代码格式化

```bash
black libimobiledevice_wrapper/
```

### 类型检查

```bash
mypy libimobiledevice_wrapper/
```

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！
