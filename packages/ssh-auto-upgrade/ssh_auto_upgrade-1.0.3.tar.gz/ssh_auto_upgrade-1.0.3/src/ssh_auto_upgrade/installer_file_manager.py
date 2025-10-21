"""
安装器文件管理模块
专门处理OpenSSH安装过程中的文件系统操作功能
"""

import os
import shutil
from pathlib import Path


class InstallerFileManager:
    """安装器文件管理器"""
    
    def __init__(self):
        """初始化文件管理器"""
        pass
    
    def delete_old_openssh_dir(self, install_dir="/usr/local/openssh"):
        """
        删除旧的OpenSSH安装目录
        
        Args:
            install_dir: OpenSSH安装目录
            
        Returns:
            bool: 删除是否成功
        """
        try:
            if os.path.exists(install_dir):
                print(f"正在删除旧的OpenSSH安装目录: {install_dir}")
                shutil.rmtree(install_dir)
                print(f"旧的OpenSSH安装目录删除成功: {install_dir}")
                return True
            else:
                print(f"OpenSSH安装目录不存在，无需删除: {install_dir}")
                return True
        except Exception as e:
            print(f"删除OpenSSH安装目录失败: {e}")
            return False
    
    def create_directory(self, directory_path):
        """
        创建目录
        
        Args:
            directory_path: 目录路径
            
        Returns:
            bool: 创建是否成功
        """
        try:
            Path(directory_path).mkdir(parents=True, exist_ok=True)
            print(f"目录创建成功: {directory_path}")
            return True
        except Exception as e:
            print(f"创建目录失败: {directory_path}, 错误: {e}")
            return False
    
    def copy_file(self, source_path, destination_path):
        """
        复制文件
        
        Args:
            source_path: 源文件路径
            destination_path: 目标文件路径
            
        Returns:
            bool: 复制是否成功
        """
        try:
            shutil.copy2(source_path, destination_path)
            print(f"文件复制成功: {source_path} -> {destination_path}")
            return True
        except Exception as e:
            print(f"文件复制失败: {source_path} -> {destination_path}, 错误: {e}")
            return False
    
    def move_file(self, source_path, destination_path):
        """
        移动文件
        
        Args:
            source_path: 源文件路径
            destination_path: 目标文件路径
            
        Returns:
            bool: 移动是否成功
        """
        try:
            shutil.move(source_path, destination_path)
            print(f"文件移动成功: {source_path} -> {destination_path}")
            return True
        except Exception as e:
            print(f"文件移动失败: {source_path} -> {destination_path}, 错误: {e}")
            return False
    
    def file_exists(self, file_path):
        """
        检查文件是否存在
        
        Args:
            file_path: 文件路径
            
        Returns:
            bool: 文件是否存在
        """
        return os.path.exists(file_path)
    
    def directory_exists(self, directory_path):
        """
        检查目录是否存在
        
        Args:
            directory_path: 目录路径
            
        Returns:
            bool: 目录是否存在
        """
        return os.path.exists(directory_path) and os.path.isdir(directory_path)
    
    def backup_file(self, file_path, backup_suffix=".backup"):
        """
        备份文件
        
        Args:
            file_path: 文件路径
            backup_suffix: 备份文件后缀
            
        Returns:
            bool: 备份是否成功
        """
        try:
            if not self.file_exists(file_path):
                print(f"文件不存在，无需备份: {file_path}")
                return True
            
            backup_path = file_path + backup_suffix
            if self.copy_file(file_path, backup_path):
                print(f"文件备份成功: {file_path} -> {backup_path}")
                return True
            else:
                print(f"文件备份失败: {file_path}")
                return False
        except Exception as e:
            print(f"文件备份失败: {file_path}, 错误: {e}")
            return False


def main():
    """测试函数"""
    manager = InstallerFileManager()
    
    # 测试目录创建
    test_dir = "/tmp/test_installer_dir"
    if manager.create_directory(test_dir):
        print(f"目录创建测试成功: {test_dir}")
    
    # 测试文件存在检查
    if manager.file_exists("/etc/passwd"):
        print("/etc/passwd 文件存在")
    
    # 测试目录存在检查
    if manager.directory_exists("/etc"):
        print("/etc 目录存在")


if __name__ == "__main__":
    main()