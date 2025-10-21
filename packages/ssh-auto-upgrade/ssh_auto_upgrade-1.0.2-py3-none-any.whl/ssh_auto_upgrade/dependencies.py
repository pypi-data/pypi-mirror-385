"""
依赖管理模块
负责检测和安装编译OpenSSH所需的系统依赖
"""

import subprocess
import platform
import os
import sys
from typing import List, Dict, Tuple

from .dependency_constants import (
    REQUIRED_DEPENDENCIES,
    PACKAGE_MANAGERS,
    PACKAGE_MANAGER_UPDATE_COMMANDS,
    PACKAGE_MANAGER_INSTALL_COMMANDS,
    DEPENDENCY_DESCRIPTIONS
)


class DependencyManager:
    """依赖管理器类"""
    
    def __init__(self):
        """初始化依赖管理器"""
        self.system_info = self._detect_system_info()
        self.package_manager = self._detect_package_manager()
        
        # 使用常量定义中的依赖配置
        self.required_dependencies = REQUIRED_DEPENDENCIES
    
    def _detect_system_info(self) -> Dict[str, str]:
        """检测系统信息"""
        system_info = {
            'system': platform.system(),
            'release': platform.release(),
            'version': platform.version(),
            'machine': platform.machine(),
            'distro': self._get_linux_distro()
        }
        return system_info
    
    def _get_linux_distro(self) -> str:
        """获取Linux发行版信息"""
        try:
            # 尝试读取/etc/os-release文件
            with open('/etc/os-release', 'r') as f:
                for line in f:
                    if line.startswith('ID='):
                        return line.split('=')[1].strip().strip('"')
        except:
            pass
        return 'unknown'
    
    def _detect_package_manager(self) -> str:
        """检测包管理器"""
        # 使用常量定义中的包管理器列表
        for pm in PACKAGE_MANAGERS:
            try:
                result = subprocess.run([pm, '--version'], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    return pm
            except (subprocess.SubprocessError, FileNotFoundError):
                continue
        
        return 'unknown'
    
    def check_dependency(self, package_name: str) -> bool:
        """检查单个依赖是否已安装"""
        try:
            # 使用which命令检查可执行文件是否存在
            result = subprocess.run(['which', package_name], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                return True
            
            # 对于库文件，尝试使用pkg-config检查
            if package_name.endswith('-dev') or package_name.endswith('-devel'):
                lib_name = package_name.replace('-dev', '').replace('-devel', '')
                result = subprocess.run(['pkg-config', '--exists', lib_name], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    return True
            
            return False
            
        except (subprocess.SubprocessError, FileNotFoundError):
            return False
    
    def check_all_dependencies(self) -> Tuple[bool, List[str]]:
        """检查所有必需的依赖"""
        if self.package_manager == 'unknown':
            return False, ["无法检测到支持的包管理器"]
        
        missing_deps = []
        
        # 获取当前包管理器对应的依赖列表
        deps = self.required_dependencies.get(self.package_manager, [])
        
        for dep in deps:
            if not self.check_dependency(dep):
                missing_deps.append(dep)
        
        return len(missing_deps) == 0, missing_deps
    
    def install_dependencies(self, update_first: bool = True) -> Tuple[bool, str]:
        """安装缺失的依赖"""
        if self.package_manager == 'unknown':
            return False, "无法检测到支持的包管理器"
        
        try:
            # 首先更新包管理器缓存
            if update_first:
                print("正在更新包管理器缓存...")
                update_cmd = PACKAGE_MANAGER_UPDATE_COMMANDS.get(self.package_manager)
                if update_cmd:
                    result = subprocess.run(update_cmd, capture_output=True, text=True)
                    if result.returncode != 0:
                        return False, f"包管理器缓存更新失败: {result.stderr}"
            
            # 检查缺失的依赖
            all_installed, missing_deps = self.check_all_dependencies()
            
            if all_installed:
                return True, "所有依赖已安装"
            
            # 安装缺失的依赖
            print(f"正在安装缺失的依赖: {', '.join(missing_deps)}")
            
            install_cmd = PACKAGE_MANAGER_INSTALL_COMMANDS.get(self.package_manager)
            if install_cmd:
                cmd = install_cmd + missing_deps
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode == 0:
                    return True, "依赖安装成功"
                else:
                    return False, f"依赖安装失败: {result.stderr}"
            else:
                return False, f"不支持的包管理器: {self.package_manager}"
            
        except Exception as e:
            return False, f"安装依赖时出错: {str(e)}"
    
    def ensure_dependencies(self, auto_install: bool = True) -> Tuple[bool, str]:
        """确保所有依赖已安装"""
        print("检查编译依赖...")
        print(f"检测到系统: {self.system_info['distro']}")
        print(f"检测到包管理器: {self.package_manager}")
        
        # 检查依赖状态
        all_installed, missing_deps = self.check_all_dependencies()
        
        if all_installed:
            print("✓ 所有编译依赖已安装")
            return True, "所有依赖已安装"
        
        print(f"缺失的依赖: {', '.join(missing_deps)}")
        
        if not auto_install:
            return False, "存在缺失的依赖，请手动安装"
        
        # 自动安装缺失的依赖
        print("开始自动安装缺失的依赖...")
        success, message = self.install_dependencies()
        
        if success:
            print("✓ 依赖安装成功")
            return True, message
        else:
            print(f"✗ 依赖安装失败: {message}")
            # 安装失败时直接终止程序
            sys.exit(f"依赖安装失败: {message}")


def main():
    """测试函数"""
    manager = DependencyManager()
    
    print("系统信息:")
    for key, value in manager.system_info.items():
        print(f"  {key}: {value}")
    
    print(f"包管理器: {manager.package_manager}")
    
    # 检查依赖状态
    all_installed, missing_deps = manager.check_all_dependencies()
    
    if all_installed:
        print("✓ 所有依赖已安装")
    else:
        print(f"缺失的依赖: {', '.join(missing_deps)}")
        
        # 询问是否安装
        response = input("是否自动安装缺失的依赖? (y/n): ")
        if response.lower() == 'y':
            success, message = manager.install_dependencies()
            print(message)


if __name__ == "__main__":
    main()