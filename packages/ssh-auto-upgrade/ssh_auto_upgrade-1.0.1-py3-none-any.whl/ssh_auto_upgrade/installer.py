"""
安装器模块
负责执行OpenSSH的安装过程
"""

import subprocess
import os
import sys
import time


class Installer:
    """安装器类"""
    
    def __init__(self, script_path, download_url):
        """
        初始化安装器
        
        Args:
            script_path: 安装脚本路径
            download_url: OpenSSH源码下载URL
        """
        self.script_path = script_path
        self.download_url = download_url
    
    def install_openssh(self):
        """
        执行OpenSSH安装
        
        Returns:
            bool: 安装是否成功
        """
        try:
            # 检查脚本是否存在
            if not os.path.exists(self.script_path):
                raise FileNotFoundError(f"安装脚本不存在: {self.script_path}")
            
            # 检查脚本是否可执行
            if not os.access(self.script_path, os.X_OK):
                os.chmod(self.script_path, 0o755)
            
            # 执行安装命令
            cmd = [sys.executable, self.script_path, "-u", self.download_url]
            
            print(f"开始安装OpenSSH...")
            print(f"命令: {' '.join(cmd)}")
            
            # 执行安装过程
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            # 实时输出安装日志
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    print(output.strip())
            
            # 等待进程结束
            return_code = process.wait()
            
            if return_code == 0:
                print("OpenSSH安装成功!")
                return True
            else:
                print(f"安装失败，返回码: {return_code}")
                return False
                
        except subprocess.SubprocessError as e:
            raise Exception(f"安装过程出错: {e}")
        except Exception as e:
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
                ['systemctl', 'status', 'ssh'],
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
            
            import re
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