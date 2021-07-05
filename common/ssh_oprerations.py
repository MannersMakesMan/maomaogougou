import logging
logging.getLogger("paramiko").setLevel(logging.WARNING)  # 关闭 paramiko 的日志打印
import paramiko


class ssh_oprerations():
    # ssh远程链接操作的工具类 ——> linux
    def __init__(self, AUTOMATED_TESTING_CONF):

        self.user = AUTOMATED_TESTING_CONF['user']
        self.psw = AUTOMATED_TESTING_CONF['psw']
        self.trans = paramiko.Transport((AUTOMATED_TESTING_CONF['host'], int(AUTOMATED_TESTING_CONF['port'])))

    def exec_cmd_connect(self):
        # 创建 用于执行shell命令的ssh链接
        try:
            self.trans.connect(username=self.user, password=self.psw)  # 建立连接
            self.ssh = paramiko.SSHClient()
            self.ssh._transport = self.trans
            self.sftp = paramiko.SFTPClient.from_transport(self.trans)
            return True
        except Exception as _e:
            return False

    def sftp_connect(self):
        # 创建 用于文件读写的xftp链接
        try:
            self.trans.connect(username=self.user, password=self.psw)  # 建立连接
            self.sftp = paramiko.SFTPClient.from_transport(self.trans)
            return True
        except Exception as _e:
            return False

    def exec_cmd(self, cmd_str, return_data_type='str'):
        # 执行命令 返回 返回值
        stdin, stdout, stderr = self.ssh.exec_command("{} 1>&2".format(cmd_str))
        # 获取命令结果 1>&2 用于解决 执行时间过久的任务无法返回数据问题
        res, err = stdout.read(), stderr.read()
        result = res if res else err
        if return_data_type == 'str':
            return result.decode('utf-8')
        elif return_data_type == 'ls':
            return result.decode('utf-8').split('\n')[0: -1]

    def open_file(self, file_path, open_param='r'):
        # 使用xftp远程打开文件
        try:
            ssh_file_obj = self.sftp.open(file_path, open_param)  # 通过sftp打开的远程文件对象
            if open_param == 'rb':
                file_content = ssh_file_obj.read()
            else:
                file_content = ssh_file_obj.read().decode('utf-8')
            ssh_file_obj.close()  # 不用关闭也会自动关闭 强迫症~~
            return file_content
        except FileNotFoundError as _e:
            return False

    def write_file(self, file_path, file_content):
        # 使用sftp写入远程文件
        try:
            ssh_file_obj = self.sftp.open(file_path, 'w')  # 通过sftp打开的远程文件对象
            ssh_file_obj.write(file_content)
            ssh_file_obj.close()
            return True
        except FileNotFoundError as _e:
            return False

    def close(self):
        # 关闭远程链接
        self.trans.close()




