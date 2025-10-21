#!/usr/bin/env python3
"""
测试模块
提供基本的测试功能
"""

import asyncio
import tempfile
from pathlib import Path
from typing import List

import pytest

from .core import LibiMobileDevice, LibiMobileDeviceError
from .webdriveragent import WebDriverAgent, WebDriverAgentError


class TestLibiMobileDevice:
    """LibiMobileDevice 测试类"""
    
    def setup_method(self):
        """测试前准备"""
        self.device = LibiMobileDevice()
    
    def test_list_devices(self):
        """测试列出设备"""
        try:
            devices = self.device.list_devices()
            assert isinstance(devices, list)
            print(f"发现的设备: {devices}")
        except LibiMobileDeviceError as e:
            print(f"设备列表获取失败: {e}")
    
    def test_get_device_info(self):
        """测试获取设备信息"""
        devices = self.device.list_devices()
        if not devices:
            pytest.skip("没有连接的设备")
        
        udid = devices[0]
        try:
            info = self.device.get_device_info(udid)
            assert isinstance(info, dict)
            assert len(info) > 0
            print(f"设备信息: {info}")
        except LibiMobileDeviceError as e:
            print(f"设备信息获取失败: {e}")
    
    def test_get_device_props(self):
        """测试获取设备属性"""
        devices = self.device.list_devices()
        if not devices:
            pytest.skip("没有连接的设备")
        
        udid = devices[0]
        try:
            props = self.device.get_device_props(udid)
            assert isinstance(props, dict)
            print(f"设备属性: {props}")
        except LibiMobileDeviceError as e:
            print(f"设备属性获取失败: {e}")
    
    def test_list_apps(self):
        """测试列出应用"""
        devices = self.device.list_devices()
        if not devices:
            pytest.skip("没有连接的设备")
        
        udid = devices[0]
        try:
            apps = self.device.list_apps(udid)
            assert isinstance(apps, list)
            print(f"已安装应用: {apps}")
        except LibiMobileDeviceError as e:
            print(f"应用列表获取失败: {e}")
    
    @pytest.mark.asyncio
    async def test_async_methods(self):
        """测试异步方法"""
        try:
            devices = await self.device.list_devices_async()
            assert isinstance(devices, list)
            print(f"异步发现的设备: {devices}")
            
            if devices:
                udid = devices[0]
                info = await self.device.get_device_info_async(udid)
                assert isinstance(info, dict)
                print(f"异步获取的设备信息: {info}")
                
        except LibiMobileDeviceError as e:
            print(f"异步操作失败: {e}")


class TestWebDriverAgent:
    """WebDriverAgent 测试类"""
    
    def setup_method(self):
        """测试前准备"""
        devices = LibiMobileDevice().list_devices()
        if not devices:
            pytest.skip("没有连接的设备")
        
        self.device_udid = devices[0]
        self.wda = WebDriverAgent(self.device_udid)
    
    @pytest.mark.asyncio
    async def test_wda_connection(self):
        """测试 WebDriverAgent 连接"""
        try:
            await self.wda.start()
            status = await self.wda._check_status()
            assert isinstance(status, dict)
            print(f"WebDriverAgent 状态: {status}")
        except WebDriverAgentError as e:
            print(f"WebDriverAgent 连接失败: {e}")
        finally:
            await self.wda.stop()
    
    @pytest.mark.asyncio
    async def test_wda_session(self):
        """测试 WebDriverAgent 会话"""
        try:
            await self.wda.start()
            
            # 创建会话
            session_id = await self.wda.create_session()
            assert session_id is not None
            print(f"会话已创建: {session_id}")
            
            # 获取会话信息
            session_info = await self.wda.get_session_info()
            assert isinstance(session_info, dict)
            print(f"会话信息: {session_info}")
            
            # 获取窗口大小
            window_size = await self.wda.get_window_size()
            assert isinstance(window_size, dict)
            print(f"窗口大小: {window_size}")
            
            # 删除会话
            await self.wda.delete_session()
            print("会话已删除")
            
        except WebDriverAgentError as e:
            print(f"WebDriverAgent 会话测试失败: {e}")
        finally:
            await self.wda.stop()
    
    @pytest.mark.asyncio
    async def test_wda_app_operations(self):
        """测试应用操作"""
        try:
            await self.wda.start()
            await self.wda.create_session()
            
            # 获取当前活动应用
            active_app = await self.wda.get_active_app()
            print(f"当前活动应用: {active_app}")
            
            # 获取应用状态
            if active_app.get('bundleId'):
                bundle_id = active_app['bundleId']
                state = await self.wda.get_app_state(bundle_id)
                print(f"应用状态: {state}")
            
        except WebDriverAgentError as e:
            print(f"应用操作测试失败: {e}")
        finally:
            await self.wda.stop()
    
    @pytest.mark.asyncio
    async def test_wda_screenshot(self):
        """测试截图功能"""
        try:
            await self.wda.start()
            await self.wda.create_session()
            
            # 截取屏幕截图
            screenshot = await self.wda.screenshot()
            assert isinstance(screenshot, bytes)
            assert len(screenshot) > 0
            print(f"截图大小: {len(screenshot)} 字节")
            
            # 保存截图到临时文件
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
                f.write(screenshot)
                temp_path = f.name
            
            print(f"截图已保存到: {temp_path}")
            
            # 清理临时文件
            Path(temp_path).unlink()
            
        except WebDriverAgentError as e:
            print(f"截图测试失败: {e}")
        finally:
            await self.wda.stop()


def run_basic_tests():
    """运行基本测试"""
    print("开始运行基本测试...")
    
    # 测试 LibiMobileDevice
    print("\n=== 测试 LibiMobileDevice ===")
    device = LibiMobileDevice()
    
    try:
        devices = device.list_devices()
        print(f"发现的设备: {devices}")
        
        if devices:
            udid = devices[0]
            info = device.get_device_info(udid)
            print(f"设备信息: {info}")
            
            apps = device.list_apps(udid)
            print(f"已安装应用: {apps}")
        
    except LibiMobileDeviceError as e:
        print(f"测试失败: {e}")
    
    # 测试异步功能
    print("\n=== 测试异步功能 ===")
    
    async def test_async():
        try:
            devices = await device.list_devices_async()
            print(f"异步发现的设备: {devices}")
            
            if devices:
                udid = devices[0]
                info = await device.get_device_info_async(udid)
                print(f"异步获取的设备信息: {info}")
                
        except LibiMobileDeviceError as e:
            print(f"异步测试失败: {e}")
    
    asyncio.run(test_async())
    
    print("\n基本测试完成!")


if __name__ == "__main__":
    run_basic_tests()
