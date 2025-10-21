#!/usr/bin/env python3
"""
libimobiledevice-wrapper 包的主模块
"""

__version__ = "1.0.0"
__author__ = "Huang-Jacky"
__email__ = "hjc853@gmail.com"

from .core import LibiMobileDevice, LibiMobileDeviceError
from .webdriveragent import WebDriverAgent, WebDriverAgentError
from . import utils

__all__ = [
    "LibiMobileDevice",
    "LibiMobileDeviceError", 
    "WebDriverAgent",
    "WebDriverAgentError",
    "utils",
]
