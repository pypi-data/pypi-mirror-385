"""
SSH Auto Upgrade Package
自动检测和升级OpenSSH的工具包
"""

__version__ = "1.0.0"
__author__ = "SSH Auto Upgrade Team"

from .version_detector import VersionDetector
from .downloader import Downloader
from .installer import Installer
from .service_manager import ServiceManager

# 从logger模块导入函数
from .logger import (
    setup_logger,
    log_installation_start,
    log_installation_step,
    log_installation_success,
    log_installation_error,
    log_verification_result
)

__all__ = [
    "VersionDetector", 
    "Downloader", 
    "Installer",
    "ServiceManager",
    "setup_logger",
    "log_installation_start",
    "log_installation_step", 
    "log_installation_success",
    "log_installation_error",
    "log_verification_result"
]