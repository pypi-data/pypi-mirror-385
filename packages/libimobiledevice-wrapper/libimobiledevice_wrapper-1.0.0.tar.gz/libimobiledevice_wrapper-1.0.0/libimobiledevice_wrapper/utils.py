#!/usr/bin/env python3
"""
工具模块
提供一些实用的辅助功能
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

logger = logging.getLogger(__name__)


def setup_logging(level: str = "INFO", log_file: Optional[Union[str, Path]] = None) -> None:
    """
    设置日志配置
    
    Args:
        level: 日志级别
        log_file: 日志文件路径
    """
    log_level = getattr(logging, level.upper(), logging.INFO)

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    if log_file:
        log_file = Path(log_file)
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)


def format_device_info(info: Dict[str, Any]) -> str:
    """
    格式化设备信息为可读字符串
    
    Args:
        info: 设备信息字典
        
    Returns:
        格式化的设备信息字符串
    """
    lines = []

    if "DeviceName" in info:
        lines.append(f"设备名称: {info['DeviceName']}")
    if "ProductName" in info:
        lines.append(f"产品名称: {info['ProductName']}")
    if "ProductVersion" in info:
        lines.append(f"系统版本: {info['ProductVersion']}")
    if "BuildVersion" in info:
        lines.append(f"构建版本: {info['BuildVersion']}")

    if "HardwareModel" in info:
        lines.append(f"硬件型号: {info['HardwareModel']}")
    if "CPUArchitecture" in info:
        lines.append(f"CPU架构: {info['CPUArchitecture']}")

    if "TotalDiskCapacity" in info:
        total_gb = int(info['TotalDiskCapacity']) // (1024**3)
        lines.append(f"总存储容量: {total_gb} GB")
    if "TotalDataCapacity" in info:
        data_gb = int(info['TotalDataCapacity']) // (1024**3)
        lines.append(f"可用存储容量: {data_gb} GB")

    if "WiFiAddress" in info:
        lines.append(f"WiFi地址: {info['WiFiAddress']}")
    if "BluetoothAddress" in info:
        lines.append(f"蓝牙地址: {info['BluetoothAddress']}")
    
    return "\n".join(lines)


def format_apps_list(apps: List[Dict[str, str]]) -> str:
    """
    格式化应用列表为可读字符串
    
    Args:
        apps: 应用信息列表
        
    Returns:
        格式化的应用列表字符串
    """
    if not apps:
        return "未发现已安装的应用"
    
    lines = []
    lines.append(f"已安装应用 ({len(apps)} 个):")
    lines.append("-" * 50)
    
    for i, app in enumerate(apps, 1):
        lines.append(f"{i:3d}. {app['name']}")
        lines.append(f"     Bundle ID: {app['bundle_id']}")
        lines.append("")
    
    return "\n".join(lines)


def save_json(data: Any, file_path: Union[str, Path], indent: int = 2) -> None:
    """
    保存数据为 JSON 文件
    
    Args:
        data: 要保存的数据
        file_path: 文件路径
        indent: JSON 缩进
    """
    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=indent)
    
    logger.info(f"数据已保存到: {file_path}")


def load_json(file_path: Union[str, Path]) -> Any:
    """
    从 JSON 文件加载数据
    
    Args:
        file_path: 文件路径
        
    Returns:
        加载的数据
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"文件不存在: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def validate_udid(udid: str) -> bool:
    """
    验证 UDID 格式
    
    Args:
        udid: 设备 UDID
        
    Returns:
        是否为有效格式
    """
    if not udid:
        return False
    
    # UDID 通常是 40 个字符的十六进制字符串
    if len(udid) == 40 and all(c in '0123456789ABCDEFabcdef' for c in udid):
        return True

    return len(udid) >= 20


def get_app_bundle_id_from_path(app_path: Union[str, Path]) -> Optional[str]:
    """
    从应用路径获取 Bundle ID
    
    Args:
        app_path: 应用文件路径
        
    Returns:
        Bundle ID 或 None
    """
    app_path = Path(app_path)
    
    if not app_path.exists():
        return None

    if app_path.suffix.lower() == '.ipa':
        logger.warning("IPA 文件 Bundle ID 解析暂未实现")
        return None

    if app_path.is_dir() and app_path.suffix.lower() == '.app':
        info_plist = app_path / "Info.plist"
        if info_plist.exists():
            try:
                import plistlib
                with open(info_plist, 'rb') as f:
                    plist = plistlib.load(f)
                return plist.get('CFBundleIdentifier')
            except Exception as e:
                logger.error(f"解析 Info.plist 失败: {e}")
                return None
    
    return None


def format_file_size(size_bytes: int) -> str:
    """
    格式化文件大小为可读字符串
    
    Args:
        size_bytes: 字节数
        
    Returns:
        格式化的文件大小字符串
    """
    if size_bytes == 0:
        return "0 B"
    
    units = ['B', 'KB', 'MB', 'GB', 'TB']
    size = float(size_bytes)
    unit_index = 0
    
    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1
    
    return f"{size:.1f} {units[unit_index]}"


def create_backup_filename(udid: str, suffix: str = "backup") -> str:
    """
    创建备份文件名
    
    Args:
        udid: 设备 UDID
        suffix: 文件后缀
        
    Returns:
        备份文件名
    """
    from datetime import datetime
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{udid}_{timestamp}.{suffix}"
