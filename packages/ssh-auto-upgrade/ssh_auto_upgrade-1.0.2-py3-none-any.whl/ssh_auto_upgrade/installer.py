"""
安装器模块
负责执行OpenSSH的安装过程
"""

import subprocess
import os
import sys
import time
import re

# 导入编译模块
from .compile import compile_openssh
# 导入依赖管理模块
from .dependencies import DependencyManager


class Installer:
    """安装器类"""
    
    def __init__(self, download_url, install_dir="/usr/local/openssh", ssl_dir=None):
        """
        初始化安装器
        
        Args:
            download_url: OpenSSH源码下载URL
            install_dir: 安装目录，默认为/usr/local/openssh
            ssl_dir: OpenSSL安装目录，可选
        """
        self.download_url = download_url
        self.install_dir = install_dir
        self.ssl_dir = ssl_dir
    
    def check_cls_service(self):
        """
        检查CLS服务是否存在
        
        Returns:
            bool: CLS服务是否存在
        """
        try:
            result = subprocess.run(
                ['systemctl', 'list-unit-files', 'cls.service'],
                capture_output=True,
                text=True
            )
            return 'cls.service' in result.stdout
        except Exception:
            return False
    
    def stop_cls_service(self):
        """
        停止CLS服务
        
        Returns:
            bool: 停止是否成功
        """
        try:
            if not self.check_cls_service():
                print("CLS服务不存在，无需停止")
                return True
            
            print("正在停止CLS服务...")
            result = subprocess.run(
                ['systemctl', 'stop', 'cls.service'],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print("CLS服务停止成功")
                return True
            else:
                print(f"CLS服务停止失败: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"停止CLS服务时出错: {e}")
            return False
    
    def start_cls_service(self):
        """
        启动CLS服务
        
        Returns:
            bool: 启动是否成功
        """
        try:
            if not self.check_cls_service():
                print("CLS服务不存在，无需启动")
                return True
            
            print("正在启动CLS服务...")
            result = subprocess.run(
                ['systemctl', 'start', 'cls.service'],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print("CLS服务启动成功")
                return True
            else:
                print(f"CLS服务启动失败: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"启动CLS服务时出错: {e}")
            return False
    
    def install_openssh(self):
        """
        执行OpenSSH安装
        
        Returns:
            bool: 安装是否成功
        """
        try:
            print(f"开始安装OpenSSH...")
            print(f"下载URL: {self.download_url}")
            print(f"安装目录: {self.install_dir}")
            if self.ssl_dir:
                print(f"OpenSSL目录: {self.ssl_dir}")
            
            # 停止CLS服务，避免升级过程中被误检测执行重置
            if not self.stop_cls_service():
                print("警告: CLS服务停止失败，继续执行安装...")
            
            # 直接调用编译模块进行安装
            success = compile_openssh(
                download_url=self.download_url,
                install_dir=self.install_dir,
                ssl_dir=self.ssl_dir
            )
            
            # 无论安装是否成功，都尝试启动CLS服务
            cls_started = self.start_cls_service()
            
            if success:
                print("OpenSSH安装成功!")
                if cls_started:
                    print("CLS服务已重新启动")
                return True
            else:
                print("OpenSSH安装失败!")
                if cls_started:
                    print("CLS服务已重新启动")
                return False
                
        except Exception as e:
            # 异常情况下也尝试启动CLS服务
            self.start_cls_service()
            raise Exception(f"安装失败: {e}")
    
    def verify_installation(self):
        """
        验证安装是否成功
        
        Returns:
            dict: 验证结果
        """
        try:
            # 检查SSH服务状态
            result = subprocess.run(
                ['systemctl', 'status', 'sshd'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            ssh_active = result.returncode == 0
            
            # 检查新版本
            version_result = subprocess.run(
                ['ssh', '-V'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            version_match = re.search(r'OpenSSH_(\d+\.\d+p\d+)', version_result.stderr)
            current_version = version_match.group(1) if version_match else "未知"
            
            return {
                'success': ssh_active,
                'ssh_service_active': ssh_active,
                'current_version': current_version,
                'service_status': result.stdout if ssh_active else result.stderr
            }
            
        except subprocess.SubprocessError as e:
            return {
                'success': False,
                'error': str(e),
                'ssh_service_active': False,
                'current_version': "未知"
            }
    
    def rollback_if_needed(self, original_version):
        """
        如果需要，回滚到原始版本
        
        Args:
            original_version: 原始版本号
            
        Returns:
            bool: 回滚是否成功
        """
        try:
            print("检测到安装问题，尝试回滚...")
            
            # 这里可以实现回滚逻辑
            # 由于OpenSSH安装比较复杂，回滚可能需要系统包管理器
            # 暂时只记录警告
            print(f"警告: 安装可能有问题，原始版本为: {original_version}")
            print("建议手动检查系统状态")
            
            return False
            
        except Exception as e:
            print(f"回滚失败: {e}")
            return False