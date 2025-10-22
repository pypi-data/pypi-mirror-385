"""
日志记录器模块
负责记录安装过程的日志
"""

import logging
import os
import sys
from datetime import datetime


def setup_logger(log_dir="/var/log/ssh-auto-upgrade"):
    """
    设置日志记录器
    
    Args:
        log_dir: 日志目录路径
        
    Returns:
        logging.Logger: 配置好的日志记录器
    """
    # 创建日志目录
    os.makedirs(log_dir, exist_ok=True)
    
    # 生成日志文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"ssh_upgrade_{timestamp}.log")
    
    # 创建日志记录器
    logger = logging.getLogger("ssh_auto_upgrade")
    logger.setLevel(logging.INFO)
    
    # 避免重复添加处理器
    if logger.handlers:
        return logger
    
    # 创建文件处理器
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    
    # 创建格式化器
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # 添加处理器到记录器
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


def log_installation_start(logger, version_info):
    """
    记录安装开始信息
    
    Args:
        logger: 日志记录器
        version_info: 版本信息
    """
    logger.info("=" * 60)
    logger.info("OpenSSH自动升级开始")
    logger.info(f"目标版本: {version_info.get('version', '未知')}")
    logger.info(f"下载URL: {version_info.get('download_url', '未知')}")
    logger.info("=" * 60)


def log_installation_step(logger, step_name, status="开始"):
    """
    记录安装步骤信息
    
    Args:
        logger: 日志记录器
        step_name: 步骤名称
        status: 步骤状态
    """
    logger.info(f"[{step_name}] {status}")


def log_installation_success(logger, version_info):
    """
    记录安装成功信息
    
    Args:
        logger: 日志记录器
        version_info: 版本信息
    """
    logger.info("=" * 60)
    logger.info("OpenSSH自动升级成功完成")
    logger.info(f"安装版本: {version_info.get('version', '未知')}")
    logger.info("=" * 60)


def log_installation_error(logger, error_message, step_name=None):
    """
    记录安装错误信息
    
    Args:
        logger: 日志记录器
        error_message: 错误信息
        step_name: 发生错误的步骤名称
    """
    if step_name:
        logger.error(f"[{step_name}] 失败: {error_message}")
    else:
        logger.error(f"安装失败: {error_message}")


def log_verification_result(logger, verification_result):
    """
    记录验证结果
    
    Args:
        logger: 日志记录器
        verification_result: 验证结果字典
    """
    logger.info("安装验证结果:")
    logger.info(f"  成功: {verification_result.get('success', False)}")
    logger.info(f"  SSH服务状态: {verification_result.get('ssh_service_active', False)}")
    logger.info(f"  当前版本: {verification_result.get('current_version', '未知')}")
    
    if not verification_result.get('success', False):
        logger.warning("安装验证发现问题，建议手动检查")


def get_log_file_path(logger):
    """
    获取当前日志文件路径
    
    Args:
        logger: 日志记录器
        
    Returns:
        str: 日志文件路径，如果没有文件处理器则返回None
    """
    for handler in logger.handlers:
        if isinstance(handler, logging.FileHandler):
            return handler.baseFilename
    return None