#!/usr/bin/env python3
"""
libimobiledevice 核心封装模块
提供所有 libimobiledevice 命令的 Python 封装
"""

import asyncio
import logging
import re
import subprocess
import threading
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

logger = logging.getLogger(__name__)


class LibiMobileDeviceError(Exception):
    """libimobiledevice 操作异常"""

    def __init__(self, message: str, command: Optional[str] = None,
                 return_code: Optional[int] = None, stderr: Optional[str] = None):
        super().__init__(message)
        self.command = command
        self.return_code = return_code
        self.stderr = stderr


class LibiMobileDevice:
    """libimobiledevice 命令封装类"""

    def __init__(self, timeout: int = 30):
        """
        初始化 LibiMobileDevice
        
        Args:
            timeout: 命令执行超时时间（秒）
        """
        self.timeout = timeout
        self._check_libimobiledevice()

    def _check_libimobiledevice(self) -> None:
        """检查 libimobiledevice 是否已安装"""
        try:
            subprocess.run(["idevice_id", "--help"],
                           capture_output=True, check=True, timeout=5)
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            raise LibiMobileDeviceError(
                "libimobiledevice 未安装或不在 PATH 中。请先安装 libimobiledevice。"
            )

    def _run_command(self, command: List[str], timeout: Optional[int] = None) -> subprocess.CompletedProcess:
        """
        执行命令并处理错误
        
        Args:
            command: 要执行的命令列表
            timeout: 超时时间
            
        Returns:
            subprocess.CompletedProcess
            
        Raises:
            LibiMobileDeviceError: 命令执行失败
        """
        timeout = timeout or self.timeout

        try:
            logger.debug(f"执行命令: {' '.join(command)}")
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=True
            )
            return result
        except subprocess.TimeoutExpired as e:
            raise LibiMobileDeviceError(
                f"命令执行超时 ({timeout}秒): {' '.join(command)}",
                command=" ".join(command),
                stderr=e.stderr
            )
        except subprocess.CalledProcessError as e:
            raise LibiMobileDeviceError(
                f"命令执行失败: {e.stderr or e.stdout}",
                command=" ".join(command),
                return_code=e.returncode,
                stderr=e.stderr
            )
        except FileNotFoundError:
            raise LibiMobileDeviceError(
                f"命令未找到: {command[0]}",
                command=" ".join(command)
            )

    async def _run_command_async(self, command: List[str],
                                 timeout: Optional[int] = None) -> subprocess.CompletedProcess:
        """
        异步执行命令并处理错误
        
        Args:
            command: 要执行的命令列表
            timeout: 超时时间
            
        Returns:
            subprocess.CompletedProcess
            
        Raises:
            LibiMobileDeviceError: 命令执行失败
        """
        timeout = timeout or self.timeout

        try:
            logger.debug(f"异步执行命令: {' '.join(command)}")
            process = await asyncio.create_subprocess_exec(
                *command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await asyncio.wait_for(
                process.communicate(), timeout=timeout
            )

            stdout_str = stdout.decode('utf-8') if stdout else ""
            stderr_str = stderr.decode('utf-8') if stderr else ""

            if process.returncode != 0:
                raise LibiMobileDeviceError(
                    f"命令执行失败: {stderr_str or stdout_str}",
                    command=" ".join(command),
                    return_code=process.returncode,
                    stderr=stderr_str
                )

            result = subprocess.CompletedProcess(
                args=command,
                returncode=process.returncode,
                stdout=stdout_str,
                stderr=stderr_str
            )
            return result

        except asyncio.TimeoutError:
            raise LibiMobileDeviceError(
                f"命令执行超时 ({timeout}秒): {' '.join(command)}",
                command=" ".join(command)
            )
        except FileNotFoundError:
            raise LibiMobileDeviceError(
                f"命令未找到: {command[0]}",
                command=" ".join(command)
            )

    def list_devices(self) -> List[str]:
        """
        列出连接的设备 UDID
        
        Returns:
            设备 UDID 列表
        """
        result = self._run_command(["idevice_id", "-l"])
        devices = [line.strip() for line in result.stdout.strip().split('\n') if line.strip()]
        return devices

    async def list_devices_async(self) -> List[str]:
        """异步列出连接的设备 UDID"""
        result = await self._run_command_async(["idevice_id", "-l"])
        devices = [line.strip() for line in result.stdout.strip().split('\n') if line.strip()]
        return devices

    def get_device_info(self, udid: str) -> Dict[str, Any]:
        """
        获取设备信息
        
        Args:
            udid: 设备 UDID
            
        Returns:
            设备信息字典
        """
        result = self._run_command(["ideviceinfo", "-u", udid])
        info = {}

        for line in result.stdout.strip().split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                info[key.strip()] = value.strip()

        return info

    async def get_device_info_async(self, udid: str) -> Dict[str, Any]:
        """异步获取设备信息"""
        result = await self._run_command_async(["ideviceinfo", "-u", udid])
        info = {}

        for line in result.stdout.strip().split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                info[key.strip()] = value.strip()

        return info

    def get_device_props(self, udid: str) -> Dict[str, Any]:
        """
        获取设备属性
        
        Args:
            udid: 设备 UDID
            
        Returns:
            设备属性字典
        """
        result = self._run_command(["ideviceinfo", "-u", udid])
        props = {}

        for line in result.stdout.strip().split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                props[key.strip()] = value.strip()

        return props

    async def get_device_props_async(self, udid: str) -> Dict[str, Any]:
        """异步获取设备属性"""
        result = await self._run_command_async(["ideviceinfo", "-u", udid])
        props = {}

        for line in result.stdout.strip().split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                props[key.strip()] = value.strip()

        return props

    def install_app(self, udid: str, app_path: Union[str, Path]) -> None:
        """
        安装应用
        
        Args:
            udid: 设备 UDID
            app_path: 应用文件路径（.ipa 或 .app）
        """
        app_path = str(app_path)
        if not Path(app_path).exists():
            raise LibiMobileDeviceError(f"应用文件不存在: {app_path}")

        self._run_command(["ideviceinstaller", "-u", udid, "-i", app_path])

    async def install_app_async(self, udid: str, app_path: Union[str, Path]) -> None:
        """异步安装应用"""
        app_path = str(app_path)
        if not Path(app_path).exists():
            raise LibiMobileDeviceError(f"应用文件不存在: {app_path}")

        await self._run_command_async(["ideviceinstaller", "-u", udid, "-i", app_path])

    def uninstall_app(self, udid: str, bundle_id: str) -> None:
        """
        卸载应用
        
        Args:
            udid: 设备 UDID
            bundle_id: 应用包 ID
        """
        self._run_command(["ideviceinstaller", "-u", udid, "-U", bundle_id])

    async def uninstall_app_async(self, udid: str, bundle_id: str) -> None:
        """异步卸载应用"""
        await self._run_command_async(["ideviceinstaller", "-u", udid, "-U", bundle_id])

    def list_apps(self, udid: str) -> List[Dict[str, str]]:
        """
        列出已安装应用
        
        Args:
            udid: 设备 UDID
            
        Returns:
            应用信息列表
        """
        result = self._run_command(["ideviceinstaller", "-u", udid, "-l"])
        apps = []

        lines = result.stdout.strip().split('\n')
        if not lines:
            return apps

        for line in lines[1:]:
            if line.strip():
                parts = line.split(', ')
                if len(parts) >= 3:
                    bundle_id = parts[0].strip()
                    version = parts[1].strip().strip('"')
                    app_name = parts[2].strip().strip('"')
                    apps.append({
                        'bundle_id': bundle_id,
                        'name': app_name,
                        'version': version
                    })

        return apps

    async def list_apps_async(self, udid: str) -> List[Dict[str, str]]:
        """异步列出已安装应用"""
        result = await self._run_command_async(["ideviceinstaller", "-u", udid, "-l"])
        apps = []

        lines = result.stdout.strip().split('\n')
        if not lines:
            return apps

        for line in lines[1:]:
            if line.strip():
                parts = line.split(', ')
                if len(parts) >= 3:
                    bundle_id = parts[0].strip()
                    version = parts[1].strip().strip('"')
                    app_name = parts[2].strip().strip('"')
                    apps.append({
                        'bundle_id': bundle_id,
                        'name': app_name,
                        'version': version
                    })

        return apps

    def launch_app(self, udid: str, bundle_id: str) -> None:
        """
        启动应用
        
        Args:
            udid: 设备 UDID
            bundle_id: 应用包 ID
        """
        self._run_command(["idevicedebug", "-u", udid, "run", bundle_id])

    async def launch_app_async(self, udid: str, bundle_id: str) -> None:
        """异步启动应用"""
        await self._run_command_async(["idevicedebug", "-u", udid, "run", bundle_id])

    def get_app_info(self, udid: str, bundle_id: str) -> Dict[str, Any]:
        """
        获取指定应用的详细信息
        
        Args:
            udid: 设备 UDID
            bundle_id: 应用包 ID
            
        Returns:
            应用详细信息字典
        """
        result = self._run_command(["ideviceinstaller", "-u", udid, "-l", "-o", "xml"])

        import xml.etree.ElementTree as ET

        try:
            root = ET.fromstring(result.stdout)
            app_info = {}

            for app in root.findall('.//dict'):
                bundle_id_elem = None
                for i, elem in enumerate(app):
                    if elem.text == 'CFBundleIdentifier':
                        bundle_id_elem = app[i + 1]
                        break

                if bundle_id_elem is not None and bundle_id_elem.text == bundle_id:
                    for i in range(0, len(app), 2):
                        if i + 1 < len(app):
                            key = app[i].text
                            value_elem = app[i + 1]
                            if value_elem.text:
                                app_info[key] = value_elem.text
                            elif len(value_elem) > 0:
                                app_info[key] = self._parse_xml_element(value_elem)
                    break

            return app_info

        except ET.ParseError:
            return self._get_app_info_plutil(udid, bundle_id)

    async def get_app_info_async(self, udid: str, bundle_id: str) -> Dict[str, Any]:
        """异步获取指定应用的详细信息"""
        result = await self._run_command_async(["ideviceinstaller", "-u", udid, "-l", "-o", "xml"])

        import xml.etree.ElementTree as ET

        try:
            root = ET.fromstring(result.stdout)
            app_info = {}

            for app in root.findall('.//dict'):
                bundle_id_elem = None
                for i, elem in enumerate(app):
                    if elem.text == 'CFBundleIdentifier':
                        bundle_id_elem = app[i + 1]
                        break

                if bundle_id_elem is not None and bundle_id_elem.text == bundle_id:
                    for i in range(0, len(app), 2):
                        if i + 1 < len(app):
                            key = app[i].text
                            value_elem = app[i + 1]
                            if value_elem.text:
                                app_info[key] = value_elem.text
                            elif len(value_elem) > 0:
                                app_info[key] = self._parse_xml_element(value_elem)
                    break

            return app_info

        except ET.ParseError:
            return await self._get_app_info_plutil_async(udid, bundle_id)

    def _parse_xml_element(self, element) -> Any:
        """解析 XML 元素"""
        if element.tag == 'string':
            return element.text
        elif element.tag == 'integer':
            return int(element.text) if element.text else 0
        elif element.tag == 'real':
            return float(element.text) if element.text else 0.0
        elif element.tag == 'true':
            return True
        elif element.tag == 'false':
            return False
        elif element.tag == 'array':
            return [self._parse_xml_element(child) for child in element]
        elif element.tag == 'dict':
            result = {}
            for i in range(0, len(element), 2):
                if i + 1 < len(element):
                    key = element[i].text
                    value = self._parse_xml_element(element[i + 1])
                    result[key] = value
            return result
        else:
            return element.text

    def _get_app_info_plutil(self, udid: str, bundle_id: str) -> Dict[str, Any]:
        """使用 plutil 命令获取应用信息"""
        try:
            container_path = f"/var/mobile/Containers/Bundle/Application/*/{bundle_id}.app"
            result = self._run_command(["ideviceexec", "-u", udid, "find", container_path, "-name", "Info.plist"])

            if result.stdout.strip():
                plist_path = result.stdout.strip().split('\n')[0]
                plist_result = self._run_command(["ideviceexec", "-u", udid, "cat", plist_path])

                import tempfile
                with tempfile.NamedTemporaryFile(mode='w', suffix='.plist', delete=False) as f:
                    f.write(plist_result.stdout)
                    temp_file = f.name

                try:
                    import subprocess
                    json_result = subprocess.run(
                        ["plutil", "-convert", "json", "-o", "-", temp_file],
                        capture_output=True, text=True, check=True
                    )

                    import json
                    return json.loads(json_result.stdout)

                finally:
                    import os
                    os.unlink(temp_file)

        except Exception as e:
            logger.warning(f"获取应用详细信息失败: {e}")

        return {
            'CFBundleIdentifier': bundle_id,
            'error': '无法获取详细信息'
        }

    async def _get_app_info_plutil_async(self, udid: str, bundle_id: str) -> Dict[str, Any]:
        """异步使用 plutil 命令获取应用信息"""
        try:
            container_path = f"/var/mobile/Containers/Bundle/Application/*/{bundle_id}.app"
            result = await self._run_command_async(
                ["ideviceexec", "-u", udid, "find", container_path, "-name", "Info.plist"])

            if result.stdout.strip():
                plist_path = result.stdout.strip().split('\n')[0]
                plist_result = await self._run_command_async(["ideviceexec", "-u", udid, "cat", plist_path])

                import tempfile
                with tempfile.NamedTemporaryFile(mode='w', suffix='.plist', delete=False) as f:
                    f.write(plist_result.stdout)
                    temp_file = f.name

                try:
                    import subprocess
                    json_result = subprocess.run(
                        ["plutil", "-convert", "json", "-o", "-", temp_file],
                        capture_output=True, text=True, check=True
                    )

                    import json
                    return json.loads(json_result.stdout)

                finally:
                    import os
                    os.unlink(temp_file)

        except Exception as e:
            logger.warning(f"异步获取应用详细信息失败: {e}")

        return {
            'CFBundleIdentifier': bundle_id,
            'error': '无法获取详细信息'
        }

    def pull_file(self, udid: str, remote_path: str, local_path: Union[str, Path]) -> None:
        """
        从设备拉取文件
        
        Args:
            udid: 设备 UDID
            remote_path: 设备上的文件路径
            local_path: 本地保存路径
        """
        local_path = Path(local_path)
        local_path.parent.mkdir(parents=True, exist_ok=True)

        self._run_command(["idevicegetfile", "-u", udid, remote_path, str(local_path)])

    async def pull_file_async(self, udid: str, remote_path: str, local_path: Union[str, Path]) -> None:
        """异步从设备拉取文件"""
        local_path = Path(local_path)
        local_path.parent.mkdir(parents=True, exist_ok=True)

        await self._run_command_async(["idevicegetfile", "-u", udid, remote_path, str(local_path)])

    def push_file(self, udid: str, local_path: Union[str, Path], remote_path: str) -> None:
        """
        推送文件到设备
        
        Args:
            udid: 设备 UDID
            local_path: 本地文件路径
            remote_path: 设备上的保存路径
        """
        local_path = Path(local_path)
        if not local_path.exists():
            raise LibiMobileDeviceError(f"本地文件不存在: {local_path}")

        self._run_command(["ideviceputfile", "-u", udid, str(local_path), remote_path])

    async def push_file_async(self, udid: str, local_path: Union[str, Path], remote_path: str) -> None:
        """异步推送文件到设备"""
        local_path = Path(local_path)
        if not local_path.exists():
            raise LibiMobileDeviceError(f"本地文件不存在: {local_path}")

        await self._run_command_async(["ideviceputfile", "-u", udid, str(local_path), remote_path])

    def reboot_device(self, udid: str) -> None:
        """
        重启设备
        
        Args:
            udid: 设备 UDID
        """
        self._run_command(["idevicediagnostics", "-u", udid, "restart"])

    async def reboot_device_async(self, udid: str) -> None:
        """异步重启设备"""
        await self._run_command_async(["idevicediagnostics", "-u", udid, "restart"])

    def shutdown_device(self, udid: str) -> None:
        """
        关机设备
        
        Args:
            udid: 设备 UDID
        """
        self._run_command(["idevicediagnostics", "-u", udid, "shutdown"])

    async def shutdown_device_async(self, udid: str) -> None:
        """异步关机设备"""
        await self._run_command_async(["idevicediagnostics", "-u", udid, "shutdown"])

    def get_device_logs(self, udid: str, duration: Optional[int] = None,
                        keywords: Optional[List[str]] = None,
                        output_file: Optional[Union[str, Path]] = None) -> List[Dict[str, Any]]:
        """
        获取设备日志
        
        Args:
            udid: 设备 UDID
            duration: 监控时长（秒），None 表示持续监控直到手动停止
            keywords: 关键字过滤列表
            output_file: 输出文件路径（可选）
            
        Returns:
            过滤后的日志列表
            
        Note:
            直接输出所有 idevicesyslog 日志，通过关键字过滤来控制显示内容
        """
        import time

        logs = []
        stop_event = threading.Event()

        def log_collector():
            """日志收集线程"""
            try:
                process = subprocess.Popen(
                    ["idevicesyslog", "-u", udid],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=False
                )

                while not stop_event.is_set():
                    line_bytes = process.stdout.readline()
                    if line_bytes:
                        try:
                            line = line_bytes.decode('utf-8', errors='replace').strip()
                        except UnicodeDecodeError:
                            try:
                                line = line_bytes.decode('latin-1', errors='replace').strip()
                            except UnicodeDecodeError:
                                line = line_bytes.decode('utf-8', errors='ignore').strip()

                        log_entry = self._parse_log_line(line)
                        if log_entry:
                            if not keywords or self._matches_keywords(log_entry, keywords):
                                logs.append(log_entry)
                        else:
                            if not keywords or any(keyword.lower() in line.lower() for keyword in keywords):
                                logs.append({'timestamp': 'Unknown', 'device': 'iOS', 'process': 'Unknown', 'pid': 0,
                                             'subsystem': 'Unknown', 'level': 'Unknown', 'message': line,
                                             'raw_line': line})
                    else:
                        break

            except Exception as e:
                logger.error(f"日志收集错误: {e}")
            finally:
                if process:
                    process.terminate()

        collector_thread = threading.Thread(target=log_collector)
        collector_thread.daemon = True
        collector_thread.start()

        if duration:
            time.sleep(duration)
            stop_event.set()
            collector_thread.join(timeout=5)
        else:
            try:
                while collector_thread.is_alive():
                    time.sleep(1)
            except KeyboardInterrupt:
                stop_event.set()
                collector_thread.join(timeout=5)

        if output_file:
            self._save_logs_to_file(logs, output_file)

        return logs

    async def get_device_logs_async(self, udid: str, duration: Optional[int] = None,
                                    keywords: Optional[List[str]] = None,
                                    output_file: Optional[Union[str, Path]] = None) -> List[Dict[str, Any]]:
        """
        异步获取设备日志
        
        Args:
            udid: 设备 UDID
            duration: 监控时长（秒），None 表示持续监控直到手动停止
            keywords: 关键字过滤列表
            output_file: 输出文件路径（可选）
            
        Returns:
            过滤后的日志列表
            
        Note:
            直接输出所有 idevicesyslog 日志，通过关键字过滤来控制显示内容
        """
        import asyncio
        import time

        logs = []

        async def log_collector():
            """异步日志收集"""
            try:
                process = await asyncio.create_subprocess_exec(
                    "idevicesyslog", "-u", udid,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )

                start_time = time.time()

                while True:
                    if duration and time.time() - start_time >= duration:
                        break

                    try:
                        line_bytes = await asyncio.wait_for(process.stdout.readline(), timeout=1.0)
                        if line_bytes:
                            try:
                                line_str = line_bytes.decode('utf-8', errors='replace').strip()
                            except UnicodeDecodeError:
                                try:
                                    line_str = line_bytes.decode('latin-1', errors='replace').strip()
                                except UnicodeDecodeError:
                                    line_str = line_bytes.decode('utf-8', errors='ignore').strip()

                            log_entry = self._parse_log_line(line_str)
                            if log_entry:
                                if not keywords or self._matches_keywords(log_entry, keywords):
                                    logs.append(log_entry)
                            else:
                                if not keywords or any(keyword.lower() in line_str.lower() for keyword in keywords):
                                    logs.append(
                                        {'timestamp': 'Unknown', 'device': 'iOS', 'process': 'Unknown', 'pid': 0,
                                         'subsystem': 'Unknown', 'level': 'Unknown', 'message': line_str,
                                         'raw_line': line_str})
                        else:
                            break
                    except asyncio.TimeoutError:
                        continue
                    except KeyboardInterrupt:
                        break

            except Exception as e:
                logger.error(f"异步日志收集错误: {e}")
            finally:
                if process.returncode is None:
                    process.terminate()
                    await process.wait()

        await log_collector()

        if output_file:
            self._save_logs_to_file(logs, output_file)

        return logs

    def _parse_log_line(self, line: str) -> Optional[Dict[str, Any]]:
        """解析日志行"""
        if not line:
            return None

        try:
            pattern = r'^(\w{3} \d{1,2} \d{2}:\d{2}:\d{2}) (\w+(?:\([^)]+\))?)\[(\d+)\] (.+)$'
            match = re.match(pattern, line)

            if match:
                timestamp_str = match.group(1)
                process_name = match.group(2)
                pid = int(match.group(3))
                remaining = match.group(4)

                if ':' in remaining:
                    subsystem, level_message = remaining.split(':', 1)
                    subsystem = subsystem.strip()
                    level_message = level_message.strip()

                    if ':' in level_message:
                        level, message = level_message.split(':', 1)
                        level = level.strip()
                        message = message.strip()
                    else:
                        level = level_message
                        message = ""
                else:
                    subsystem = remaining
                    level = ""
                    message = ""

                return {
                    'timestamp': timestamp_str,
                    'device': 'iOS',
                    'process': process_name,
                    'pid': pid,
                    'subsystem': subsystem,
                    'level': level,
                    'message': message,
                    'raw_line': line
                }

            # 尝试解析应用日志格式: -[ClassName methodName] [Line number] message
            app_pattern = r'^-\[([^\]]+)\] \[Line (\d+)\] (.+)$'
            app_match = re.match(app_pattern, line)

            if app_match:
                method_name = app_match.group(1)
                line_number = int(app_match.group(2))
                message = app_match.group(3)

                class_name = method_name.split(' ')[0] if ' ' in method_name else method_name

                return {
                    'timestamp': 'App Log',
                    'device': 'iOS',
                    'process': class_name,
                    'pid': 0,
                    'subsystem': 'App',
                    'level': 'Info',
                    'message': message,
                    'raw_line': line
                }

            complex_app_pattern = r'^-\[([^\]]+)\][^[]*\[Line (\d+)\] (.+)$'
            complex_match = re.match(complex_app_pattern, line)

            if complex_match:
                method_name = complex_match.group(1)
                line_number = int(complex_match.group(2))
                message = complex_match.group(3)

                class_name = method_name.split(' ')[0] if ' ' in method_name else method_name

                return {
                    'timestamp': 'App Log',
                    'device': 'iOS',
                    'process': class_name,
                    'pid': 0,
                    'subsystem': 'App',
                    'level': 'Info',
                    'message': message,
                    'raw_line': line
                }

            return None

        except Exception as e:
            logger.debug(f"解析日志行失败: {e}")
            return None

    def _matches_keywords(self, log_entry: Dict[str, Any], keywords: List[str]) -> bool:
        """检查日志是否匹配关键字"""
        if not keywords:
            return True

        message = log_entry.get('message', '').lower()
        process = log_entry.get('process', '').lower()
        subsystem = log_entry.get('subsystem', '').lower()
        level = log_entry.get('level', '').lower()

        text_to_search = f"{message} {process} {subsystem} {level}"

        for keyword in keywords:
            if keyword.lower() in text_to_search:
                return True

        return False

    def _save_logs_to_file(self, logs: List[Dict[str, Any]], output_file: Union[str, Path]) -> None:
        """保存日志到文件"""
        output_file = Path(output_file)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w', encoding='utf-8') as f:
            for log in logs:
                f.write(
                    f"{log['timestamp']} [{log['level']}] {log['process']}[{log['pid']}] {log['subsystem']}: {log['message']}\n")

        logger.info(f"日志已保存到: {output_file}")

    def monitor_device_logs(self, udid: str, keywords: Optional[List[str]] = None,
                            callback: Optional[callable] = None,
                            log_file_path: Optional[Union[str, Path]] = None,
                            duration: Optional[int] = None) -> 'LogMonitor':
        """
        统一的设备日志监控接口
        
        Args:
            udid: 设备 UDID
            keywords: 关键字过滤列表
            callback: 日志回调函数（可选）
            log_file_path: 日志文件保存路径（可选，自动保存）
            duration: 监控时长（秒），None 表示持续监控直到手动停止
            
        Returns:
            LogMonitor: 统一的日志监控器对象
        """
        return LogMonitor(udid, keywords, callback, log_file_path, duration)


class LogMonitor:
    """日志监控器类"""

    def __init__(self, udid: str, keywords: Optional[List[str]] = None,
                 callback: Optional[callable] = None,
                 log_file_path: Optional[Union[str, Path]] = None,
                 duration: Optional[int] = None):
        self.udid = udid
        self.keywords = keywords
        self.callback = callback
        self.log_file_path = Path(log_file_path) if log_file_path else None
        self.duration = duration
        self.process = None
        self.monitor_thread = None
        self.stop_event = threading.Event()
        self.logs = []
        self.file_handle = None

    def _parse_log_line(self, line: str) -> Optional[Dict[str, Any]]:
        """解析日志行"""
        import re

        # 标准 iOS 系统日志格式
        pattern = r'^(\w{3} \d{1,2} \d{2}:\d{2}:\d{2}) (\w+(?:\([^)]+\))?)\[(\d+)\] (.+)$'
        match = re.match(pattern, line)

        if match:
            timestamp, process, pid, message = match.groups()
            return {
                'timestamp': timestamp,
                'process': process,
                'pid': pid,
                'subsystem': 'System',
                'level': 'Info',
                'message': message
            }

        # 应用特定日志格式
        app_pattern = r'-\[([^\]]+)\][^[]*\[Line (\d+)\] (.+)$'
        app_match = re.match(app_pattern, line)

        if app_match:
            method_name, line_num, message = app_match.groups()
            return {
                'timestamp': '',
                'process': 'App',
                'pid': '',
                'subsystem': 'App',
                'level': 'Debug',
                'message': f'[{method_name}] [Line {line_num}] {message}'
            }

        return None

    def _matches_keywords(self, log_entry: Dict[str, Any], keywords: List[str]) -> bool:
        """检查日志是否匹配关键字"""
        if not keywords:
            return True

        # 检查消息中是否包含关键字
        message = log_entry.get('message', '').lower()
        process = log_entry.get('process', '').lower()
        subsystem = log_entry.get('subsystem', '').lower()

        for keyword in keywords:
            keyword_lower = keyword.lower()
            if (keyword_lower in message or
                    keyword_lower in process or
                    keyword_lower in subsystem):
                return True

        return False

    def _log_monitor(self):
        """日志监控线程"""
        try:
            self.process = subprocess.Popen(
                ["idevicesyslog", "-u", self.udid],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=False
            )

            while not self.stop_event.is_set():
                if self.process.poll() is not None:
                    break

                line_bytes = self.process.stdout.readline()
                if not line_bytes:
                    time.sleep(0.05)
                    continue

                try:
                    line = line_bytes.decode('utf-8', errors='replace').strip()
                except UnicodeDecodeError:
                    try:
                        line = line_bytes.decode('latin-1', errors='replace').strip()
                    except UnicodeDecodeError:
                        line = line_bytes.decode('utf-8', errors='ignore').strip()

                if line == "[connected]":
                    continue

                log_entry = self._parse_log_line(line)

                if log_entry:
                    if self.keywords and not self._matches_keywords(log_entry, self.keywords):
                        continue

                    self.logs.append(log_entry)

                    if self.callback:
                        self.callback(log_entry)
                    else:
                        print(f"[{log_entry['level']}] {log_entry['message']}")
                else:
                    if self.keywords:
                        if not any(keyword.lower() in line.lower() for keyword in self.keywords):
                            continue

                    print(line)

        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"日志监控错误: {e}")
        finally:
            self._cleanup()

    def _cleanup(self):
        """清理资源"""
        if self.file_handle:
            self.file_handle.close()
            self.file_handle = None

        if self.process:
            try:
                self.process.terminate()

                try:
                    self.process.wait(timeout=1)
                except subprocess.TimeoutExpired:
                    self.process.kill()
                    try:
                        self.process.wait(timeout=1)
                    except subprocess.TimeoutExpired:
                        pass

                subprocess.Popen('pkill idevicesyslog', shell=True,
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.debug(f"清理进程时出现异常: {e}")
            finally:
                self.process = None

    def start(self):
        """开始监控"""
        if self.monitor_thread and self.monitor_thread.is_alive():
            import logging
            logger = logging.getLogger(__name__)
            logger.warning("日志监控已在运行")
            return

        self.stop_event.clear()
        self.monitor_thread = threading.Thread(target=self._log_monitor, daemon=True)
        self.monitor_thread.start()
        import logging
        logger = logging.getLogger(__name__)
        logger.info("设备日志监控已启动")

    def stop(self):
        """停止监控"""
        self.stop_event.set()

        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=5)

        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"日志监控已停止，共收集 {len(self.logs)} 条日志")

    def save_logs(self, output_file: Union[str, Path]):
        """保存日志到文件"""
        output_file = Path(output_file)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w', encoding='utf-8') as f:
            for log in self.logs:
                f.write(
                    f"{log['timestamp']} [{log['level']}] {log['process']}[{log['pid']}] {log['subsystem']}: {log['message']}\n")

        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"日志已保存到: {output_file}")

    def get_logs(self) -> List[Dict[str, Any]]:
        """获取收集的日志"""
        return self.logs.copy()

    def is_running(self) -> bool:
        """检查是否正在运行"""
        return self.monitor_thread and self.monitor_thread.is_alive()

    def __enter__(self):
        """上下文管理器入口"""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.stop()
