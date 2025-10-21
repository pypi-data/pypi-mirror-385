"""
systemd服务管理模块
"""

import os
import subprocess
import shutil
from pathlib import Path


class ServiceManager:
    """systemd服务管理器"""
    
    def __init__(self, service_name="ssh-auto-upgrade", install_dir="/usr/local/bin"):
        """
        初始化服务管理器
        
        Args:
            service_name: 服务名称
            install_dir: 安装目录
        """
        self.service_name = service_name
        self.install_dir = install_dir
        self.service_file_path = f"/etc/systemd/system/{service_name}.service"
        self.executable_path = f"{install_dir}/ssh-auto-upgrade"
    
    def check_systemd_available(self):
        """检查systemd是否可用"""
        try:
            result = subprocess.run(["systemctl", "--version"], 
                                  capture_output=True, text=True)
            return result.returncode == 0
        except (subprocess.SubprocessError, FileNotFoundError):
            return False
    
    def create_service_file(self, description="OpenSSH Auto Upgrade Service", 
                          user="root", group="root"):
        """
        创建systemd服务文件
        
        Args:
            description: 服务描述
            user: 运行用户
            group: 运行组
        """
        service_content = f"""[Unit]
Description={description}
After=network.target

[Service]
Type=simple
User={user}
Group={group}
ExecStart={self.executable_path} --daemon --mirror https://mirrors.aliyun.com/openssh/portable/
Restart=always
RestartSec=60
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
"""
        
        try:
            # 确保目录存在
            Path("/etc/systemd/system").mkdir(parents=True, exist_ok=True)
            
            # 写入服务文件
            with open(self.service_file_path, 'w') as f:
                f.write(service_content)
            
            # 设置正确的权限
            os.chmod(self.service_file_path, 0o644)
            
            return True, "服务文件创建成功"
            
        except Exception as e:
            return False, f"创建服务文件失败: {str(e)}"
    
    def install_executable(self):
        """安装可执行文件到系统目录"""
        try:
            # 获取当前脚本路径
            current_script = Path(__file__).parent.parent / "ssh_auto_upgrade" / "main.py"
            
            # 确保安装目录存在
            Path(self.install_dir).mkdir(parents=True, exist_ok=True)
            
            # 创建可执行文件
            executable_content = f"""#!/usr/bin/env python3
import sys
from ssh_auto_upgrade.main import main

if __name__ == "__main__":
    sys.exit(main())
"""
            
            with open(self.executable_path, 'w') as f:
                f.write(executable_content)
            
            # 设置可执行权限
            os.chmod(self.executable_path, 0o755)
            
            return True, "可执行文件安装成功"
            
        except Exception as e:
            return False, f"安装可执行文件失败: {str(e)}"
    
    def enable_service(self):
        """启用服务"""
        try:
            # 重新加载systemd配置
            subprocess.run(["systemctl", "daemon-reload"], check=True)
            
            # 启用服务
            subprocess.run(["systemctl", "enable", self.service_name], check=True)
            
            return True, "服务启用成功"
            
        except subprocess.CalledProcessError as e:
            return False, f"启用服务失败: {str(e)}"
    
    def start_service(self):
        """启动服务"""
        try:
            result = subprocess.run(["systemctl", "start", self.service_name], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                return True, "服务启动成功"
            else:
                return False, f"服务启动失败: {result.stderr}"
                
        except subprocess.CalledProcessError as e:
            return False, f"启动服务失败: {str(e)}"
    
    def stop_service(self):
        """停止服务"""
        try:
            result = subprocess.run(["systemctl", "stop", self.service_name], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                return True, "服务停止成功"
            else:
                return False, f"服务停止失败: {result.stderr}"
                
        except subprocess.CalledProcessError as e:
            return False, f"停止服务失败: {str(e)}"
    
    def disable_service(self):
        """禁用服务"""
        try:
            result = subprocess.run(["systemctl", "disable", self.service_name], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                return True, "服务禁用成功"
            else:
                return False, f"服务禁用失败: {result.stderr}"
                
        except subprocess.CalledProcessError as e:
            return False, f"禁用服务失败: {str(e)}"
    
    def remove_service(self):
        """移除服务"""
        try:
            # 停止服务
            self.stop_service()
            
            # 禁用服务
            self.disable_service()
            
            # 删除服务文件
            if os.path.exists(self.service_file_path):
                os.remove(self.service_file_path)
            
            # 删除可执行文件
            if os.path.exists(self.executable_path):
                os.remove(self.executable_path)
            
            # 重新加载systemd配置
            subprocess.run(["systemctl", "daemon-reload"], check=True)
            
            return True, "服务移除成功"
            
        except Exception as e:
            return False, f"移除服务失败: {str(e)}"
    
    def get_service_status(self):
        """获取服务状态"""
        try:
            result = subprocess.run(["systemctl", "status", self.service_name], 
                                  capture_output=True, text=True)
            
            return result.returncode == 0, result.stdout
            
        except subprocess.CalledProcessError as e:
            return False, f"获取服务状态失败: {str(e)}"
    
    def register_service(self, user="root", group="root"):
        """
        注册systemd服务
        
        Args:
            user: 运行用户
            group: 运行组
        """
        # 检查systemd是否可用
        if not self.check_systemd_available():
            return False, "systemd不可用，无法注册服务"
        
        # 检查权限
        if os.geteuid() != 0:
            return False, "需要root权限来注册systemd服务"
        
        try:
            # 安装可执行文件
            success, message = self.install_executable()
            if not success:
                return False, message
            
            # 创建服务文件
            success, message = self.create_service_file(user=user, group=group)
            if not success:
                return False, message
            
            # 启用服务
            success, message = self.enable_service()
            if not success:
                return False, message
            
            return True, "systemd服务注册成功"
            
        except Exception as e:
            return False, f"注册服务失败: {str(e)}"


def main():
    """测试函数"""
    manager = ServiceManager()
    
    # 检查systemd
    if manager.check_systemd_available():
        print("systemd可用")
    else:
        print("systemd不可用")
    
    # 测试服务状态
    success, status = manager.get_service_status()
    print(f"服务状态: {success}")
    print(f"状态信息: {status}")


if __name__ == "__main__":
    main()