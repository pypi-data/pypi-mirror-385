"""
版本检测模块
负责从OpenSSH官方源检测最新版本
"""

import requests
from bs4 import BeautifulSoup
import re


class VersionDetector:
    """版本检测器类"""
    
    def __init__(self, mirror_url="https://mirrors.aliyun.com/openssh/portable/"):
        """
        初始化版本检测器
        
        Args:
            mirror_url: 镜像源URL，默认为阿里云镜像
        """
        self.mirror_url = mirror_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
        })
    
    def get_latest_version(self):
        """
        获取最新版本信息
        
        Returns:
            dict: 包含版本信息的字典
            {
                'version': '10.2p1',
                'download_url': 'https://mirrors.aliyun.com/openssh/portable/openssh-10.2p1.tar.gz',
                'filename': 'openssh-10.2p1.tar.gz'
            }
        """
        try:
            response = self.session.get(self.mirror_url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 查找所有.tar.gz文件
            tar_files = []
            for link in soup.find_all('a', href=True):
                href = link['href']
                if href.endswith('.tar.gz') and href.startswith('openssh-'):
                    tar_files.append(href)
            
            if not tar_files:
                raise ValueError("未找到OpenSSH压缩包文件")
            
            # 提取版本号并排序
            versions = []
            for filename in tar_files:
                # 匹配openssh-版本号.tar.gz格式
                match = re.match(r'openssh-(\d+\.\d+p\d+)\.tar\.gz', filename)
                if match:
                    version_str = match.group(1)
                    # 将版本号转换为可排序的元组
                    version_parts = version_str.replace('p', '.').split('.')
                    version_tuple = tuple(int(x) for x in version_parts)
                    versions.append((version_tuple, version_str, filename))
            
            if not versions:
                raise ValueError("未找到有效的OpenSSH版本")
            
            # 按版本号排序，获取最新版本
            latest_version = max(versions, key=lambda x: x[0])
            
            return {
                'version': latest_version[1],
                'download_url': f"{self.mirror_url}{latest_version[2]}",
                'filename': latest_version[2]
            }
            
        except requests.RequestException as e:
            raise Exception(f"网络请求失败: {e}")
        except Exception as e:
            raise Exception(f"版本检测失败: {e}")
    
    def check_current_version(self):
        """
        检查当前系统安装的OpenSSH版本
        
        Returns:
            str: 当前版本号，如果无法检测返回None
        """
        import subprocess
        
        try:
            result = subprocess.run(
                ['ssh', '-V'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                # 提取版本号，格式如: OpenSSH_8.9p1, OpenSSL 1.1.1w 11 Sep 2023
                version_match = re.search(r'OpenSSH_(\d+\.\d+p\d+)', result.stderr)
                if version_match:
                    return version_match.group(1)
            
            return None
            
        except (subprocess.SubprocessError, FileNotFoundError):
            return None