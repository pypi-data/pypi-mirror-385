"""
SSH自动升级工具主程序
"""

import argparse
import sys
import os

# 添加模块路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from ssh_auto_upgrade.version_detector import VersionDetector
from ssh_auto_upgrade.downloader import Downloader
from ssh_auto_upgrade.installer import Installer
from ssh_auto_upgrade.service_manager import ServiceManager
from ssh_auto_upgrade.logger import (
    setup_logger, 
    log_installation_start, 
    log_installation_step,
    log_installation_success,
    log_installation_error,
    log_verification_result
)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='OpenSSH自动升级工具')
    parser.add_argument('--mirror', '-m', 
                        default='https://mirrors.aliyun.com/openssh/portable/',
                        help='OpenSSH镜像源URL')
    parser.add_argument('--script-url', '-s',
                        default='https://gitee.com/liumou_site/openssh/raw/master/compile/SSH.py',
                        help='安装脚本URL')
    parser.add_argument('--download-dir', '-d',
                        default='/tmp/ssh-upgrade',
                        help='下载目录')
    parser.add_argument('--log-dir', '-l',
                        default='/var/log/ssh-auto-upgrade',
                        help='日志目录')
    parser.add_argument('--force', '-f',
                        action='store_true',
                        help='强制升级，即使版本相同也执行安装')
    parser.add_argument('--dry-run',
                        action='store_true',
                        help='模拟运行，不实际执行安装')
    parser.add_argument('--service',
                        action='store_true',
                        help='注册为systemd服务')
    
    args = parser.parse_args()
    
    # 设置日志
    logger = setup_logger(args.log_dir)
    
    # 处理服务注册
    if args.service:
        try:
            print("正在注册systemd服务...")
            service_manager = ServiceManager()
            
            # 检查systemd是否可用
            if not service_manager.check_systemd_available():
                print("错误: systemd不可用，无法注册服务")
                return 1
            
            # 检查权限
            if os.geteuid() != 0:
                print("错误: 需要root权限来注册systemd服务")
                return 1
            
            # 注册服务
            success, message = service_manager.register_service()
            
            if success:
                print(f"成功: {message}")
                print("\n服务已注册，可以使用以下命令管理:")
                print("  systemctl start ssh-auto-upgrade    # 启动服务")
                print("  systemctl stop ssh-auto-upgrade     # 停止服务")
                print("  systemctl status ssh-auto-upgrade   # 查看服务状态")
                print("  systemctl enable ssh-auto-upgrade   # 启用开机自启")
                print("  systemctl disable ssh-auto-upgrade  # 禁用开机自启")
                return 0
            else:
                print(f"错误: {message}")
                return 1
                
        except Exception as e:
            print(f"服务注册失败: {str(e)}")
            return 1
    
    try:
        # 检查当前版本
        detector = VersionDetector(args.mirror)
        current_version = detector.check_current_version()
        
        if current_version:
            print(f"当前OpenSSH版本: {current_version}")
            logger.info(f"当前OpenSSH版本: {current_version}")
        else:
            print("无法检测当前OpenSSH版本")
            logger.warning("无法检测当前OpenSSH版本")
        
        # 获取最新版本
        log_installation_step(logger, "版本检测")
        latest_version_info = detector.get_latest_version()
        
        print(f"最新OpenSSH版本: {latest_version_info['version']}")
        print(f"下载URL: {latest_version_info['download_url']}")
        
        # 检查是否需要升级
        if current_version == latest_version_info['version'] and not args.force:
            print("当前已是最新版本，无需升级")
            logger.info("当前已是最新版本，无需升级")
            return 0
        
        if args.dry_run:
            print("模拟运行模式，不执行实际安装")
            print(f"将升级到版本: {latest_version_info['version']}")
            logger.info("模拟运行模式，安装被跳过")
            return 0
        
        # 记录安装开始
        log_installation_start(logger, latest_version_info)
        
        # 下载安装脚本
        log_installation_step(logger, "下载安装脚本")
        downloader = Downloader(args.download_dir)
        script_path = downloader.download_install_script(args.script_url)
        
        print(f"安装脚本下载完成: {script_path}")
        
        # 执行安装
        log_installation_step(logger, "执行安装")
        installer = Installer(script_path, latest_version_info['download_url'])
        
        if installer.install_openssh():
            # 验证安装
            log_installation_step(logger, "验证安装")
            verification_result = installer.verify_installation()
            
            log_verification_result(logger, verification_result)
            
            if verification_result['success']:
                log_installation_success(logger, latest_version_info)
                print("OpenSSH升级成功完成!")
                
                # 显示新版本信息
                new_version = verification_result['current_version']
                print(f"新版本: {new_version}")
                
                return 0
            else:
                error_msg = "安装验证失败"
                log_installation_error(logger, error_msg, "验证安装")
                
                # 尝试回滚
                if current_version:
                    installer.rollback_if_needed(current_version)
                
                return 1
        else:
            error_msg = "安装过程失败"
            log_installation_error(logger, error_msg, "执行安装")
            return 1
            
    except KeyboardInterrupt:
        print("\n用户中断安装过程")
        logger.warning("用户中断安装过程")
        return 130
    except Exception as e:
        error_msg = str(e)
        print(f"安装失败: {error_msg}")
        log_installation_error(logger, error_msg)
        return 1
    finally:
        # 清理临时文件
        try:
            if 'downloader' in locals():
                downloader.cleanup()
        except:
            pass


if __name__ == "__main__":
    sys.exit(main())