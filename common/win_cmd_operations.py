import re
import winrm


class winrm_operations():
    # winrm远程操作工具类 --> windows
    def __init__(self, AUTOMATED_UI_TESTING_CONF):

        self.win_server = winrm.Session('http://{}/wsman'.format(AUTOMATED_UI_TESTING_CONF['host']), auth=(AUTOMATED_UI_TESTING_CONF['user'], AUTOMATED_UI_TESTING_CONF['psw']))

    def win_wrn_connect(self):
        # 创建远程winrm链接
        try:
            self.win_server.run_cmd('dir')
            return self.win_server
        except Exception as e:
            return False

    def exe_dir(self, cd_path):
        # 远程windows执行 dir命令 返回文件列表
        rep = self.win_server.run_cmd('cd {} && {}: && dir'.format(cd_path, cd_path.split(":")[0])).std_out.decode()
        rep_ls = rep.split('\r\n')
        file_ls = []
        for i in rep_ls:
            if ('.py' in i or 'DIR' in i or 'xlsx' in i or 'html' in i) and '_pycache' not in i:
                value = re.split('[ ]+', i)[-1]
                if value != '.' and value != '..':
                    file_ls.append(value)
        return file_ls

    def exe_cmd(self, cmd_str):
        # 执行命令
        rep = self.win_server.run_cmd(cmd_str)
        return rep.std_out.decode(), rep.std_err.decode()

    def exe_upload_file(self, remote_ip, remote_path, local_file_path):
        # 从本机上传文件到远端linux 此前两终端必须注册密钥 实现免密登录
        cmd_str = 'scp {} root@{}:{}'.format(local_file_path, remote_ip, remote_path)
        self.win_server.run_cmd('scp {} root@{}:{}'.format(local_file_path, remote_ip, remote_path))

    def exe_download_file(self, remote_ip, remote_path, local_file_path):
        # 从远端下载文件到本地 此前两终端必须注册密钥 实现免密登录
        cmd_str = 'scp root@{}:{} {}'.format(remote_ip, remote_path, local_file_path)
        self.win_server.run_cmd('scp root@{}:{} {}'.format(remote_ip, remote_path, local_file_path))









