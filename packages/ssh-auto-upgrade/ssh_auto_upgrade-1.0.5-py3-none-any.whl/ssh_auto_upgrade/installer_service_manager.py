"""
安装器服务管理模块
专门处理OpenSSH安装过程中的系统服务管理功能
复用service_manager.py的通用服务管理能力
"""

import subprocess
from .service_manager import ServiceManager


class InstallerServiceManager:
    """安装器服务管理器"""
    
    def __init__(self):
        """初始化服务管理器"""
        # 复用ServiceManager的基础功能
        self.service_manager = ServiceManager()
    
    def check_service_exists(self, service_name):
        """
        检查服务是否存在
        
        Args:
            service_name: 服务名称
            
        Returns:
            bool: 服务是否存在
        """
        try:
            # 创建特定服务的ServiceManager实例
            service_mgr = ServiceManager(service_name=service_name)
            # 复用ServiceManager的检查逻辑
            success, _ = service_mgr.get_service_status()
            return success
        except Exception:
            return False
    
    def check_service_status(self, service_name):
        """
        检查服务状态
        
        Args:
            service_name: 服务名称
            
        Returns:
            dict: 包含服务状态信息的字典
        """
        try:
            result = {
                'exists': False,
                'is_active': False,
                'is_enabled': False
            }
            
            # 检查服务是否存在
            result['exists'] = self.check_service_exists(service_name)
            
            if not result['exists']:
                return result
            
            # 检查服务是否正在运行
            service_mgr = ServiceManager(service_name=service_name)
            try:
                subprocess.run(['systemctl', 'is-active', service_name], check=True)
                result['is_active'] = True
            except subprocess.CalledProcessError:
                result['is_active'] = False
            
            # 检查服务是否启用开机自启
            try:
                subprocess.run(['systemctl', 'is-enabled', service_name], check=True)
                result['is_enabled'] = True
            except subprocess.CalledProcessError:
                result['is_enabled'] = False
            
            return result
            
        except Exception as e:
            print(f"检查服务 {service_name} 状态时出错: {e}")
            return {'exists': False, 'is_active': False, 'is_enabled': False}
    
    def stop_service(self, service_name):
        """
        停止服务
        
        Args:
            service_name: 服务名称
            
        Returns:
            bool: 停止是否成功
        """
        try:
            if not self.check_service_exists(service_name):
                print(f"服务 {service_name} 不存在，无需停止")
                return True
            
            print(f"正在停止服务: {service_name}")
            service_mgr = ServiceManager(service_name=service_name)
            success, message = service_mgr.stop_service()
            
            if success:
                print(f"服务 {service_name} 停止成功")
                return True
            else:
                print(f"服务 {service_name} 停止失败: {message}")
                return False
                
        except Exception as e:
            print(f"停止服务 {service_name} 时出错: {e}")
            return False
    
    def start_service(self, service_name):
        """
        启动服务
        
        Args:
            service_name: 服务名称
            
        Returns:
            bool: 启动是否成功
        """
        try:
            if not self.check_service_exists(service_name):
                print(f"服务 {service_name} 不存在，无需启动")
                return True
            
            print(f"正在启动服务: {service_name}")
            service_mgr = ServiceManager(service_name=service_name)
            success, message = service_mgr.start_service()
            
            if success:
                print(f"服务 {service_name} 启动成功")
                return True
            else:
                print(f"服务 {service_name} 启动失败: {message}")
                return False
                
        except Exception as e:
            print(f"启动服务 {service_name} 时出错: {e}")
            return False
    
    def disable_service_autostart(self, service_name):
        """
        禁用服务开机自启
        
        Args:
            service_name: 服务名称
            
        Returns:
            bool: 禁用是否成功
        """
        try:
            if not self.check_service_exists(service_name):
                print(f"服务 {service_name} 不存在，无需禁用开机自启")
                return True
            
            print(f"正在禁用服务 {service_name} 的开机自启")
            service_mgr = ServiceManager(service_name=service_name)
            success, message = service_mgr.disable_service()
            
            if success:
                print(f"服务 {service_name} 开机自启已禁用")
                return True
            else:
                print(f"禁用服务 {service_name} 开机自启失败: {message}")
                return False
                
        except Exception as e:
            print(f"禁用服务 {service_name} 开机自启时出错: {e}")
            return False
    
    def check_native_ssh_service(self):
        """
        检查系统原生SSH服务状态
        
        Returns:
            dict: 包含原生SSH服务信息的字典
        """
        try:
            result = {
                'exists': False,
                'service_name': None,
                'is_active': False,
                'is_enabled': False,
                'is_native': False  # 是否为原生SSH服务
            }
            
            # 只检查原生SSH服务名称（ssh），不检查编译安装的sshd
            ssh_services = ['ssh', 'openssh-server']
            
            for service_name in ssh_services:
                service_status = self.check_service_status(service_name)
                
                if service_status['exists']:
                    result['exists'] = True
                    result['service_name'] = service_name
                    result['is_active'] = service_status['is_active']
                    result['is_enabled'] = service_status['is_enabled']
                    result['is_native'] = True  # 这些是原生SSH服务
                    break
            
            return result
            
        except Exception as e:
            print(f"检查原生SSH服务时出错: {e}")
            return {'exists': False, 'service_name': None, 'is_active': False, 'is_enabled': False, 'is_native': False}
    
    def disable_native_ssh_service(self):
        """
        禁用原生SSH服务，避免端口冲突
        
        Returns:
            bool: 禁用是否成功
        """
        try:
            ssh_info = self.check_native_ssh_service()
            
            if not ssh_info['exists']:
                print("系统未安装原生SSH服务，无需禁用")
                return True
            
            # 只有当检测到的是原生SSH服务时才进行禁用
            if not ssh_info['is_native']:
                print("检测到的SSH服务不是原生服务，无需禁用")
                return True
            
            service_name = ssh_info['service_name']
            print(f"检测到原生SSH服务: {service_name}")
            
            # 停止原生SSH服务
            if ssh_info['is_active']:
                if not self.stop_service(service_name):
                    print(f"警告: 原生SSH服务 {service_name} 停止失败")
            
            # 禁用原生SSH服务开机自启
            if ssh_info['is_enabled']:
                if not self.disable_service_autostart(service_name):
                    print(f"警告: 原生SSH服务 {service_name} 禁用开机自启失败")
            
            # 检查是否成功禁用
            final_check = self.check_native_ssh_service()
            if not final_check['is_active'] and not final_check['is_enabled']:
                print("原生SSH服务已成功禁用")
                return True
            else:
                print("警告: 原生SSH服务禁用可能不完整")
                return False
                
        except Exception as e:
            print(f"禁用原生SSH服务时出错: {e}")
            return False


def main():
    """测试函数"""
    manager = InstallerServiceManager()
    
    # 测试CLS服务检查
    cls_status = manager.check_service_status('cls')
    print(f"CLS服务状态: {cls_status}")
    
    # 测试原生SSH服务检查
    ssh_status = manager.check_native_ssh_service()
    print(f"原生SSH服务状态: {ssh_status}")


if __name__ == "__main__":
    main()