"""
下载器模块
负责下载OpenSSH源码压缩包和安装脚本
"""

import requests
import os


class Downloader:
    """下载器类"""
    
    def __init__(self, download_dir="/tmp/ssh-upgrade"):
        """
        初始化下载器
        
        Args:
            download_dir: 下载目录路径
        """
        self.download_dir = download_dir
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
        })
        
        # 创建下载目录
        os.makedirs(self.download_dir, exist_ok=True)
    
    def download_file(self, url, filename=None, chunk_size=8192):
        """
        下载文件
        
        Args:
            url: 文件URL
            filename: 保存的文件名，如果为None则从URL提取
            chunk_size: 下载块大小
            
        Returns:
            str: 下载文件的完整路径
        """
        if filename is None:
            filename = os.path.basename(url)
        
        filepath = os.path.join(self.download_dir, filename)
        
        try:
            response = self.session.get(url, stream=True, timeout=60)
            response.raise_for_status()
            
            # 获取文件大小
            total_size = int(response.headers.get('content-length', 0))
            
            with open(filepath, 'wb') as f:
                downloaded_size = 0
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:
                        f.write(chunk)
                        downloaded_size += len(chunk)
                        
                        # 显示下载进度
                        if total_size > 0:
                            progress = (downloaded_size / total_size) * 100
                            print(f"\r下载进度: {progress:.1f}%", end="", flush=True)
            
            print()  # 换行
            
            # 验证文件完整性
            if self._verify_file(filepath, total_size):
                return filepath
            else:
                raise Exception("文件下载不完整或损坏")
                
        except requests.RequestException as e:
            # 清理可能损坏的文件
            if os.path.exists(filepath):
                os.remove(filepath)
            raise Exception(f"下载失败: {e}")
    
    def download_install_script(self, script_url="https://gitee.com/liumou_site/openssh/raw/master/compile/SSH.py"):
        """
        下载安装脚本
        
        Args:
            script_url: 安装脚本URL
            
        Returns:
            str: 安装脚本的完整路径
        """
        return self.download_file(script_url, "SSH.py")
    
    def _verify_file(self, filepath, expected_size):
        """
        验证文件完整性和大小
        
        Args:
            filepath: 文件路径
            expected_size: 期望的文件大小
            
        Returns:
            bool: 文件是否完整
        """
        if not os.path.exists(filepath):
            return False
        
        actual_size = os.path.getsize(filepath)
        
        if expected_size > 0 and actual_size != expected_size:
            return False
        
        # 检查文件是否可读
        try:
            with open(filepath, 'rb') as f:
                # 读取文件头检查是否为有效的压缩文件
                header = f.read(4)
                if header.startswith(b'\x1f\x8b'):  # gzip格式
                    return True
                elif header.startswith(b'\xfd7z'):  # xz格式
                    return True
                else:
                    # 可能是文本文件（如Python脚本）
                    return actual_size > 0
        except:
            return False
    
    def cleanup(self):
        """
        清理下载目录
        """
        import shutil
        if os.path.exists(self.download_dir):
            shutil.rmtree(self.download_dir)
    
    def get_download_dir(self):
        """
        获取下载目录路径
        
        Returns:
            str: 下载目录路径
        """
        return self.download_dir