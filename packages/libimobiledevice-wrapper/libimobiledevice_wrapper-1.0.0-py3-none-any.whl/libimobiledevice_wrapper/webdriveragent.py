#!/usr/bin/env python3
"""
WebDriverAgent 接口支持模块
提供 WebDriverAgent 的 Python 封装
"""

import asyncio
import json
import logging
import time
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin

import aiohttp

logger = logging.getLogger(__name__)


class WebDriverAgentError(Exception):
    """WebDriverAgent 操作异常"""

    def __init__(self, message: str, status_code: Optional[int] = None, response: Optional[str] = None):
        super().__init__(message)
        self.status_code = status_code
        self.response = response


class WebDriverAgent:
    """WebDriverAgent 接口封装类"""

    def __init__(self, device_udid: str, wda_port: int = 8100,
                 wda_host: str = "localhost", timeout: int = 30):
        """
        初始化 WebDriverAgent
        
        Args:
            device_udid: 设备 UDID
            wda_port: WebDriverAgent 端口
            wda_host: WebDriverAgent 主机
            timeout: 请求超时时间
        """
        self.device_udid = device_udid
        self.wda_port = wda_port
        self.wda_host = wda_host
        self.timeout = timeout
        self.base_url = f"http://{wda_host}:{wda_port}"
        self.session_id: Optional[str] = None
        self._session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        """异步上下文管理器入口"""
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.stop()

    async def start(self) -> None:
        """启动 WebDriverAgent"""
        if self._session is None:
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            self._session = aiohttp.ClientSession(timeout=timeout)

        # 检查 WebDriverAgent 是否已运行
        try:
            await self._check_status()
            logger.info(f"WebDriverAgent 已在 {self.base_url} 运行")
        except WebDriverAgentError:
            logger.info("WebDriverAgent 未运行，请先启动 WebDriverAgent")
            raise WebDriverAgentError("WebDriverAgent 未运行，请先启动 WebDriverAgent")

    async def stop(self) -> None:
        """停止 WebDriverAgent 连接"""
        if self.session_id:
            await self.delete_session()

        if self._session:
            await self._session.close()
            self._session = None

    async def _check_status(self) -> Dict[str, Any]:
        """检查 WebDriverAgent 状态"""
        url = urljoin(self.base_url, "/status")

        async with self._session.get(url) as response:
            if response.status != 200:
                raise WebDriverAgentError(
                    f"WebDriverAgent 状态检查失败: HTTP {response.status}",
                    status_code=response.status
                )

            return await response.json()

    async def _make_request(self, method: str, endpoint: str,
                            data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        发送 HTTP 请求到 WebDriverAgent
        
        Args:
            method: HTTP 方法
            endpoint: API 端点
            data: 请求数据
            
        Returns:
            响应数据
        """
        url = urljoin(self.base_url, endpoint)

        try:
            if method.upper() == "GET":
                async with self._session.get(url) as response:
                    response_data = await response.json()
            elif method.upper() == "POST":
                async with self._session.post(url, json=data) as response:
                    response_data = await response.json()
            elif method.upper() == "DELETE":
                async with self._session.delete(url) as response:
                    response_data = await response.json()
            else:
                raise WebDriverAgentError(f"不支持的 HTTP 方法: {method}")

            if response.status >= 400:
                error_msg = response_data.get('value', {}).get('message', '未知错误')
                raise WebDriverAgentError(
                    f"WebDriverAgent 请求失败: {error_msg}",
                    status_code=response.status,
                    response=json.dumps(response_data, ensure_ascii=False)
                )

            return response_data

        except aiohttp.ClientError as e:
            raise WebDriverAgentError(f"网络请求失败: {e}")
        except json.JSONDecodeError as e:
            raise WebDriverAgentError(f"响应解析失败: {e}")

    async def create_session(self, capabilities: Optional[Dict[str, Any]] = None) -> str:
        """
        创建 WebDriver 会话
        
        Args:
            capabilities: 会话能力配置
            
        Returns:
            会话 ID
        """
        if capabilities is None:
            capabilities = {
                "platformName": "iOS",
                "deviceName": self.device_udid,
                "udid": self.device_udid
            }

        data = {"capabilities": {"alwaysMatch": capabilities}}
        response = await self._make_request("POST", "/session", data)

        self.session_id = response.get("sessionId")
        if not self.session_id:
            raise WebDriverAgentError("创建会话失败：未返回会话 ID")

        logger.info(f"WebDriver 会话已创建: {self.session_id}")
        return self.session_id

    async def delete_session(self) -> None:
        """删除 WebDriver 会话"""
        if not self.session_id:
            return

        try:
            await self._make_request("DELETE", f"/session/{self.session_id}")
            logger.info(f"WebDriver 会话已删除: {self.session_id}")
        finally:
            self.session_id = None

    async def get_session_info(self) -> Dict[str, Any]:
        """获取会话信息"""
        if not self.session_id:
            raise WebDriverAgentError("没有活动的会话")

        return await self._make_request("GET", f"/session/{self.session_id}")

    # 应用操作方法

    async def launch_app(self, bundle_id: str) -> None:
        """
        启动应用
        
        Args:
            bundle_id: 应用包 ID
        """
        if not self.session_id:
            raise WebDriverAgentError("没有活动的会话")

        data = {
            "bundleId": bundle_id
        }

        await self._make_request("POST", f"/session/{self.session_id}/wda/apps/launch", data)
        logger.info(f"应用已启动: {bundle_id}")

    async def terminate_app(self, bundle_id: str) -> None:
        """
        终止应用
        
        Args:
            bundle_id: 应用包 ID
        """
        if not self.session_id:
            raise WebDriverAgentError("没有活动的会话")

        data = {
            "bundleId": bundle_id
        }

        await self._make_request("POST", f"/session/{self.session_id}/wda/apps/terminate", data)
        logger.info(f"应用已终止: {bundle_id}")

    async def get_app_state(self, bundle_id: str) -> int:
        """
        获取应用状态
        
        Args:
            bundle_id: 应用包 ID
            
        Returns:
            应用状态 (0: 未运行, 1: 后台运行, 2: 前台运行, 3: 未知)
        """
        if not self.session_id:
            raise WebDriverAgentError("没有活动的会话")

        data = {
            "bundleId": bundle_id
        }

        response = await self._make_request("POST", f"/session/{self.session_id}/wda/apps/state", data)
        return response.get("value", 0)

    async def get_active_app(self) -> Dict[str, Any]:
        """获取当前活动应用信息"""
        if not self.session_id:
            raise WebDriverAgentError("没有活动的会话")

        response = await self._make_request("GET", f"/session/{self.session_id}/wda/activeAppInfo")
        return response.get("value", {})

    async def screenshot(self) -> bytes:
        """截取屏幕截图"""
        if not self.session_id:
            raise WebDriverAgentError("没有活动的会话")

        response = await self._make_request("GET", f"/session/{self.session_id}/screenshot")
        import base64
        return base64.b64decode(response.get("value", ""))

    async def tap(self, x: int, y: int) -> None:
        """
        点击屏幕
        
        Args:
            x: X 坐标
            y: Y 坐标
        """
        if not self.session_id:
            raise WebDriverAgentError("没有活动的会话")

        data = {
            "x": x,
            "y": y
        }

        await self._make_request("POST", f"/session/{self.session_id}/wda/tap/0", data)
        logger.info(f"已点击坐标: ({x}, {y})")

    async def swipe(self, start_x: int, start_y: int, end_x: int, end_y: int, duration: float = 0.5) -> None:
        """
        滑动屏幕
        
        Args:
            start_x: 起始 X 坐标
            start_y: 起始 Y 坐标
            end_x: 结束 X 坐标
            end_y: 结束 Y 坐标
            duration: 滑动持续时间（秒）
        """
        if not self.session_id:
            raise WebDriverAgentError("没有活动的会话")

        data = {
            "fromX": start_x,
            "fromY": start_y,
            "toX": end_x,
            "toY": end_y,
            "duration": duration
        }

        await self._make_request("POST", f"/session/{self.session_id}/wda/dragfromtoforduration", data)
        logger.info(f"已滑动: ({start_x}, {start_y}) -> ({end_x}, {end_y})")

    async def get_window_size(self) -> Dict[str, int]:
        """获取窗口大小"""
        if not self.session_id:
            raise WebDriverAgentError("没有活动的会话")

        response = await self._make_request("GET", f"/session/{self.session_id}/window/size")
        return response.get("value", {})

    async def find_element(self, by: str, value: str) -> str:
        """
        查找元素
        
        Args:
            by: 查找方式 (accessibility id, class name, id, name, xpath, etc.)
            value: 查找值
            
        Returns:
            元素 ID
        """
        if not self.session_id:
            raise WebDriverAgentError("没有活动的会话")

        data = {
            "using": by,
            "value": value
        }

        response = await self._make_request("POST", f"/session/{self.session_id}/element", data)
        element_id = response.get("value", {}).get("ELEMENT")

        if not element_id:
            raise WebDriverAgentError(f"未找到元素: {by}={value}")

        return element_id

    async def find_elements(self, by: str, value: str) -> List[str]:
        """
        查找多个元素
        
        Args:
            by: 查找方式
            value: 查找值
            
        Returns:
            元素 ID 列表
        """
        if not self.session_id:
            raise WebDriverAgentError("没有活动的会话")

        data = {
            "using": by,
            "value": value
        }

        response = await self._make_request("POST", f"/session/{self.session_id}/elements", data)
        elements = response.get("value", [])

        return [elem.get("ELEMENT") for elem in elements if elem.get("ELEMENT")]

    async def click_element(self, element_id: str) -> None:
        """
        点击元素
        
        Args:
            element_id: 元素 ID
        """
        if not self.session_id:
            raise WebDriverAgentError("没有活动的会话")

        await self._make_request("POST", f"/session/{self.session_id}/element/{element_id}/click")
        logger.info(f"已点击元素: {element_id}")

    async def send_keys(self, element_id: str, text: str) -> None:
        """
        向元素发送文本
        
        Args:
            element_id: 元素 ID
            text: 要发送的文本
        """
        if not self.session_id:
            raise WebDriverAgentError("没有活动的会话")

        data = {"value": list(text)}
        await self._make_request("POST", f"/session/{self.session_id}/element/{element_id}/value", data)
        logger.info(f"已向元素 {element_id} 发送文本: {text}")

    async def get_element_text(self, element_id: str) -> str:
        """
        获取元素文本
        
        Args:
            element_id: 元素 ID
            
        Returns:
            元素文本
        """
        if not self.session_id:
            raise WebDriverAgentError("没有活动的会话")

        response = await self._make_request("GET", f"/session/{self.session_id}/element/{element_id}/text")
        return response.get("value", "")

    async def get_element_attribute(self, element_id: str, attribute: str) -> str:
        """
        获取元素属性
        
        Args:
            element_id: 元素 ID
            attribute: 属性名
            
        Returns:
            属性值
        """
        if not self.session_id:
            raise WebDriverAgentError("没有活动的会话")

        response = await self._make_request("GET",
                                            f"/session/{self.session_id}/element/{element_id}/attribute/{attribute}")
        return response.get("value", "")

    async def press_home(self) -> None:
        """按下 Home 键"""
        if not self.session_id:
            raise WebDriverAgentError("没有活动的会话")

        await self._make_request("POST", f"/session/{self.session_id}/wda/homescreen")
        logger.info("已按下 Home 键")

    async def press_back(self) -> None:
        """按下返回键"""
        if not self.session_id:
            raise WebDriverAgentError("没有活动的会话")

        await self._make_request("POST", f"/session/{self.session_id}/back")
        logger.info("已按下返回键")

    async def lock_screen(self) -> None:
        """锁定屏幕"""
        if not self.session_id:
            raise WebDriverAgentError("没有活动的会话")

        await self._make_request("POST", f"/session/{self.session_id}/wda/lock")
        logger.info("屏幕已锁定")

    async def unlock_screen(self) -> None:
        """解锁屏幕"""
        if not self.session_id:
            raise WebDriverAgentError("没有活动的会话")

        await self._make_request("POST", f"/session/{self.session_id}/wda/unlock")
        logger.info("屏幕已解锁")

    async def wait_for_element(self, by: str, value: str, timeout: int = 10) -> str:
        """
        等待元素出现
        
        Args:
            by: 查找方式
            value: 查找值
            timeout: 超时时间（秒）
            
        Returns:
            元素 ID
        """
        start_time = time.time()

        while time.time() - start_time < timeout:
            try:
                return await self.find_element(by, value)
            except WebDriverAgentError:
                await asyncio.sleep(0.5)

        raise WebDriverAgentError(f"等待元素超时: {by}={value}")

    async def wait_for_app(self, bundle_id: str, timeout: int = 10) -> None:
        """
        等待应用启动
        
        Args:
            bundle_id: 应用包 ID
            timeout: 超时时间（秒）
        """
        start_time = time.time()

        while time.time() - start_time < timeout:
            state = await self.get_app_state(bundle_id)
            if state == 2:
                return
            await asyncio.sleep(0.5)

        raise WebDriverAgentError(f"等待应用启动超时: {bundle_id}")
