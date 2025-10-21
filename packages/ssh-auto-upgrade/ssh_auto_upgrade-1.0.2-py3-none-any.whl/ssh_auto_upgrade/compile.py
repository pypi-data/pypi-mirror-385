#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
"""
@File    :   SSH.py
@Time    :   2024-07-23 09:56
@Author  :   坐公交也用券
@Version :   1.0
@Contact :   faith01238@hotmail.com
@Homepage : https://liumou.site
@Desc    :   当前文件作用
"""
import logging
import os
import subprocess
import sys
import time
from argparse import ArgumentParser
from datetime import datetime
from shutil import copy2
from sys import exit

# 创建一个自定义的日志记录器
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# 创建一个自定义的日志处理器，设置其输出格式
formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(filename)s:%(lineno)d | %(funcName)s | %(message)s')
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(formatter)
logger.addHandler(handler)


def service(p: str):
	"""
	创建Service
	:param p:
	:return:
	"""
	os.system("mkdir -p /usr/lib/systemd/system_bak/")
	os.system("cp -rf /usr/lib/systemd/system/ssh*.service /usr/lib/systemd/system_bak/")
	os.system('rm -f /usr/lib/systemd/system/ssh*.service')
	if os.path.exists("/etc/init.d/sshd"):
		os.system('rm -f /etc/init.d/sshd')
	f = '/usr/lib/systemd/system/sshd.service'
	txt = f"""[Unit]
Description=This is a manually generated SSH service file
After=network.target
StartLimitIntervalSec=5

[Service]
Type=simple
User=root
ExecStart={p}
StandardOutput=journal
KillMode=control-group
Restart=on-failure
RestartPreventExitStatus=255
StandardError=inherit
SyslogIdentifier=sshd

[Install]
WantedBy=multi-user.target
Alias=sshd.service
"""
	try:
		with open(f, 'w', encoding="utf-8") as fp:
			fp.write(txt)
	except Exception as e:
		logger.error(e)
		return
	os.system(f"systemctl daemon-reload")
	os.system(f"systemctl enable sshd.service")
	os.system(f"systemctl restart sshd.service")
	os.system(f"systemctl status sshd.service")


def create_service():
	"""

	:return:
	"""
	p = os.path.join(dst_arg, "sbin/sshd")
	if not os.path.isfile(p):
		logger.error(f"未找到openssh,请使用-s参数指定openssh安装目录: {p}")
		return
	logger.info("将仅生成Service文件,如需重新编译请先删除")
	service(p=p)
	exit(0)


class Upgrade:
	def __init__(self, dst, email, urls, file, ssl=None):
		"""

		:param dst: 设置安装目录
		:param email: 设置邮箱
		:param urls: 设置升级包地址
		:param file: 设置本地升级包
		:param ssl: 设置OPENSSL 安装目录
		"""
		self.email = email
		self.dst = dst
		self.ssl = ssl
		self.file = file
		logger.debug(str(file).replace(".tar.gz", ''))
		self.tmp_dir = os.path.join(os.getcwd(), str(file).replace(".tar.gz", ''))
		self.url = urls
		self.filename = file
		self.failed = False
		self.dst_bin = os.path.join(self.dst, "bin")
		self.dst_sbin = os.path.join(self.dst, "sbin")
		self.ssh_dst_etc = os.path.join(self.dst, "etc")
		self.ssl_use = False
		self.sshd_new = os.path.join(self.dst_sbin, "sshd")

	def check(self):
		"""
		检测参数
		:return:
		"""
		if self.ssl is None:
			print("本次安装未指定openssl,如需指定请使用-s参数指定openssl安装目录")
			return
		else:
			if not os.path.exists(self.ssl):
				print(f"指定的openssl目录不存在: {self.ssl}")
				exit(5)
		self.ssl_use = True

	def download(self):
		"""
		下载压缩包
		:return:
		"""
		# 如果文件已经存在则先删除
		if os.path.exists(self.filename):
			os.remove(self.filename)
		print("正在下载压缩包")
		# 开始下载并判断下载结果，如果下载失败则退出
		if os.system(f"wget {self.url}") != 0:
			print("下载失败")
			exit(1)

	def untar(self):
		"""
		解压压缩包
		:return:
		"""
		print("正在解压压缩包")
		# 根据文件扩展名选择解压命令
		if self.filename.endswith('.tar.gz') or self.filename.endswith('.tgz'):
			# 解压tar.gz文件
			c = f"tar -zxf {self.filename}"
		else:
			# 解压普通tar文件
			c = f"tar -xvf {self.filename}"
		
		# 执行解压命令
		if os.system(c) != 0:
			print("解压失败")
			exit(2)

	def compile(self):
		"""
		编译源码
		:return:
		"""
		if not os.path.isdir(self.tmp_dir):
			print(f"找不到解压目录: {self.tmp_dir}")
			exit(4)
		print("正在编译源码")
		os.chdir(self.tmp_dir)
		c = f"./configure --prefix={self.dst} "
		if self.ssl_use:
			c += f" --with-ssl-dir={self.ssl}"
		if os.system(c) != 0:
			print(f"预编译配置失败: [ {c} ]")
			exit(3)
		if os.system(f"make") != 0:
			print("编译失败: [ make ]")
			exit(4)

	def install(self):
		"""
		安装
		:return:
		"""
		print("正在安装")
		os.chdir(self.tmp_dir)
		c = "make install"
		if os.system(c) != 0:
			print(f"安装失败: [ {c} ]")
			exit(5)

	def clean(self):
		"""
		清理
		:return:
		"""
		print("正在清理")
		if os.path.exists(self.tmp_dir):
			os.system(f"rm -rf {self.tmp_dir}")
		if os.path.exists(self.filename):
			os.system(f"rm -f {self.filename}")

	def link_ssh_conf(self):
		"""
		链接sshd_config文件
		:return:
		"""
		dst = "/etc/ssh"
		# 获取当前时间,格式如下： 202405201230
		formatted_datetime = datetime.now().strftime('%Y%m%d%H%M%S')
		# 拼接文件名
		conf_new = f"{dst}_{formatted_datetime}"
		# 开始备份
		if os.path.exists(dst):
			c = f"mv {dst} {conf_new}"
			if os.system(c) == 0:
				logger.info(f"备份成功: [ {c} ]")
			else:
				logger.error(f"备份失败: [ {c} ]")
				exit(1)

		os.symlink(self.ssh_dst_etc, dst)

	def open_root(self):
		"""
		开启root登录
		:return:
		"""
		# 检查是否存在root登录参数选项
		# 拼接源路径
		sshd_config = os.path.join(self.dst, "etc/sshd_config")
		if not os.path.exists(sshd_config):
			logger.error(f"配置文件不存在: [ {sshd_config} ]")
			exit(2)
		# 获取文件内容，判断是否存在注释符号
		c = f"grep ^PermitRootLogin {sshd_config}"
		if os.system(c) != 0:
			# 如果不存在则添加
			c = f"sed -i '$aPermitRootLogin yes' {sshd_config}"
			if os.system(c) != 0:
				logger.error(f"添加root登录失败[ {sshd_config} ]")
				exit(2)
			else:
				logger.info(f"添加root登录成功,请在完成升级配置后关闭[ {sshd_config} ]")
		else:
			# 如果存在则替换
			c = f"sed -i 's/PermitRootLogin.*/PermitRootLogin yes/g' {sshd_config}"
			if os.system(c) != 0:
				logger.error(f"开启root登录失败[ {sshd_config} ]")
				exit(2)
			else:
				logger.info(f"开启root登录成功,请在完成升级配置后关闭[ {sshd_config} ]")

	def link_ssh_bin(self):
		"""
		连接
		:return:
		"""
		# 先获取当前安装的可执行文件列表
		ssh_list = os.listdir(self.dst_bin)
		for file in ssh_list:
			# 获取当前系统PATH目录中是否存在对应的链接文件
			r = subprocess.getstatusoutput(f"which {file}")
			if r[0] == 0:
				# 如果存在则删除
				os.system(f"rm -f {r[1]}")
			# 创建链接文件
			src = os.path.join(self.dst_bin, file)
			c = f"ln -s {src} /usr/bin/{file}"
			if os.system(c) == 0:
				print(f"创建链接文件成功: [ {c} ]")
			else:
				print(f"创建链接文件失败: [ {c} ]")
				self.failed = True
		# 替换sbin的sshd
		# 先获取旧的sshd
		sshd_old = subprocess.getoutput("which sshd")
		# 先删除旧的
		os.system(f"rm -f {sshd_old}")
		# 创建新的
		c = f"cp -rfi {self.sshd_new} /usr/sbin/sshd"
		if os.system(c) == 0:
			print(f"创建链接文件成功: [ {c} ]")
		else:
			print(f"创建链接文件失败: [ {c} ]")
			self.failed = True
		# 复制ssh-keygen
		os.system("rm -f /usr/bin/ssh-keygen")
		try:
			copy2(os.path.join(self.dst_bin, "ssh-keygen"), "/usr/bin/ssh-keygen")
			print("复制ssh-keygen成功")
		except Exception as e:
			print(f"复制ssh-keygen失败: [ {e} ]")
			self.failed = True

	def restart(self):
		"""
		重启
		:return:
		"""
		if self.failed:
			print("存在链接文件创建失败,请手动创建链接文件并重启服务")
			exit(8)
		print("正在重启服务验证")
		# 先重载配置
		if os.system("systemctl daemon-reload") != 0:
			print("服务重载失败")
			exit(7)
		if os.system("systemctl restart sshd") != 0:
			print("服务重启失败")
			exit(6)
		print("升级成功")

	def profile(self):
		"""
		写入profile文件
		:return:
		"""
		lib = os.path.join(self.dst, "lib")
		path_bin = os.path.join(self.dst, "bin")

		# 判断LD_LIBRARY_PATH变量是否存在 lib
		LD_LIBRARY_PATH_txt = False
		if "LD_LIBRARY_PATH" in os.environ:
			if lib not in os.environ["LD_LIBRARY_PATH"]:
				lib = f"{lib}:{os.environ['LD_LIBRARY_PATH']}"
				LD_LIBRARY_PATH_txt = True
		else:
			LD_LIBRARY_PATH_txt = True

		print("正在写入profile文件")
		try:
			with open(file="/etc/profile", mode="a+", encoding="utf-8") as f:
				# if write_path:
				# 	f.write(f"export PATH={path_bin}\n")
				if LD_LIBRARY_PATH_txt:
					f.write(f"export LD_LIBRARY_PATH={lib}\n")
		except Exception as e:
			print(f"写入profile文件失败:  {e}")
			exit(9)
		print("写入profile文件成功")
		# 开始加载新的配置
		os.system("source /etc/profile")
		os.environ["PATH"] = f"{path_bin}:{os.environ['PATH']}"
		os.environ["LD_LIBRARY_PATH"] = lib

	def reconstruction(self):
		"""
		重建.ssh
		:return:
		"""
		# 开始删除.ssh
		print("正在重建.ssh")
		# 通过HOME目录和.ssh拼接
		ssh_dir = os.path.join(os.environ["HOME"], ".ssh")
		os.system(f"rm -rf {ssh_dir}")
		# 开始执行密钥创建并设置预定义的邮箱
		if os.system(f"ssh-keygen -t rsa -b 4096 -C \"{self.email}\" -f {ssh_dir}/id_rsa -N \"\"") != 0:
			print("密钥创建失败")
			exit(10)
		print("重建.ssh成功")

	def start(self, download):
		"""

		:param download:
		:return:
		"""
		self.check()
		if download:
			self.download()
		self.untar()
		self.compile()
		self.install()
		self.link_ssh_bin()
		self.link_ssh_conf()
		self.profile()
		self.reconstruction()
		# self.write_sshd()
		self.open_root()
		self.clean()
		# service("/usr/sbin/sshd")
		create_service()
		self.restart()



def use():
	"""
	使用免责声明
	:return:
	"""
	print("""
	免责声明:
	操作系统环境问题由使用者自行维护,此脚本只是个人编写，不代表任何平台或单位
	1. 本脚本仅供学习交流使用,请勿用于非法用途
	2. 脚本作者不对因使用本脚本而导致的任何问题或损失负责,请先自行阅读源码后再决定是否继续
	3. 可接受脚本bug反馈，但是不提供使用指导,请自行判断,不懂的地方可以通过-h参数获取帮助
	4. 如遇到代码问题可自行修改源码或者反馈，但是作者不会保障及时的修复
	5. 下班时间不会回复、处理任何此类脚本的问题
	""")
	# 非交互模式，直接继续执行
	print("非交互模式，自动继续执行...")


def compile_openssh(download_url, install_dir="/usr/local/openssh", ssl_dir=None, email="liumou@qq.com"):
	"""
	编译安装OpenSSH的主函数
	
	Args:
		download_url: OpenSSH源码下载URL
		install_dir: 安装目录，默认为/usr/local/openssh
		ssl_dir: OpenSSL安装目录，可选
		email: 用于重建.ssh的邮箱地址
	
	Returns:
		bool: 安装是否成功
	"""
	try:
		# 解析文件名
		filename = download_url.split("/")[-1]
		
		# 创建升级实例
		upgrade = Upgrade(dst=install_dir, ssl=ssl_dir, urls=download_url, file=filename, email=email)
		
		# 执行安装
		upgrade.start(download=True)
		
		return True
		
	except Exception as e:
		logger.error(f"OpenSSH编译安装失败: {e}")
		return False


def create_user():
	"""
	创建sshd用户
	:return:
	"""
	# 先判断是否已存在
	if subprocess.getstatusoutput("id sshd")[0] != 0:
		if os.system("useradd sshd") != 0:
			logger.error("用户创建失败")


if __name__ == "__main__":
	start_time = time.time()
	# 设置传参自定义URL
	url = 'https://mirrors.aliyun.com/openssh/portable/openssh-10.0p1.tar.gz'
	arg = ArgumentParser(description='当前脚本版本: 1.0_20250528', prog="OpenSshCompileInstall")
	h = f"在线模式: 自定义设置压缩包链接(当设置文件路径则忽略此参数),默认: {url}"
	arg.add_argument("-u", "--url", help=h, default=url, required=False)
	h = "离线模式: 手动指定压缩包路径,不从网页下载(默认使用网页下载)"
	arg.add_argument("-f", "--file", help=h, required=False)
	h = f"设置openssl的安装路径(如需指定openssl版本则需要传入此参数),例如: /usr/local/openssl3.3.0"
	arg.add_argument("-ssl", "--ssl", help=h, required=False)
	# 设置程序安装目录自定义
	arg.add_argument("-d", "--dst", help=f"设置程序安装目录,默认: /usr/local/openssh", default="/usr/local/openssh")
	h = f"新版本安装后需要重建.ssh,默认使用邮箱: liumou@qq.com进行重建"
	arg.add_argument("-e", "--email", help=h, default="liumou@qq.com")
	# 使用布尔值判断是否需要创建service
	arg.add_argument("-q", "--quit", help=f"创建service之后直接退出", action="store_true")
	url = arg.parse_args().url
	filename = arg.parse_args().file
	ssl_arg = arg.parse_args().ssl
	dst_arg = arg.parse_args().dst
	email_arg = arg.parse_args().email
	quit_arg = arg.parse_args().quit
	download_ = False
	if filename:
		filename = os.path.abspath(filename)
	else:
		filename = str(url.split("/")[-1])
		download_ = True
	if quit_arg:
		create_service()
		exit(0)

	use()
	logger.debug(f"参数: {arg.parse_args()}")
	create_user()
	os.system("mkdir -p /var/empty")
	upgrade = Upgrade(dst=dst_arg, ssl=ssl_arg, urls=url, file=filename, email=email_arg)
	upgrade.start(download=download_)
	logger.info(f"升级完成->耗时: {time.time() - start_time}")
