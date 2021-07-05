import datetime

import hashlib
import subprocess

from django.core.mail import send_mail

from basic_configuration.settings import EMAIL_HOST_USER


def parse_pymodel(temporary, file_name, function_ls, path, parse_type='ui'):
    # 解析py文件 返回类及函数注释
    f = open(temporary, 'r', encoding='utf-8')
    a = f.readlines()

    function_class = ''
    function_class_remark = ''
    for index in range(len(a)):
        function_dict = {}
        value = a[index]
        if 'class' in value and 'unittest' in value:
            function_class = value
            if parse_type == 'api':
                function_class_remark = path.split('/')[-2]
            else:
                function_class_remark = a[index + 1]
                if not check_contain_chinese(function_class_remark):
                    function_class_remark = '无注释'
        if 'def' in value and 'self' in value and 'test' in value and 'setParameters' not in value:
            function_remark = a[index+1].replace(' ', '').replace('\n', '').replace('#', '').replace('"', '')
            if not check_contain_chinese(function_remark):
                function_remark = '无注释'
            function_dict['function'] = value.replace(' ', '').replace('(self):\n', '').replace('def', '')
            function_dict['function_remark'] = function_remark
            function_dict['file'] = file_name
            function_dict['file_path'] = path
            function_dict['function_class'] = function_class.replace(' ', '').replace('class', '').replace('(unittest.TestCase):\n', '')
            function_dict['function_class_remark'] = function_class_remark.replace(' ', '').replace('\n', '').replace('#', '')
            function_ls[exe_md5(function_dict['function']+function_dict['file'])] = str(function_dict)
    return function_ls


def exe_md5(string):
    # 加密字符串为md5
    m = hashlib.md5()
    b = string.encode(encoding='utf-8')
    m.update(b)
    str_md5 = m.hexdigest()
    return str_md5


def check_ip(ip):
    # 检测ip是否能ping通
    result = subprocess.call('ping -W 1 -c 1 %s' % ip, stdout=subprocess.PIPE, shell=True)
    if result == 0:
        return True
    else:
        return False


def check_contain_chinese(check_str):
    # 检测字符串中是否存在中文
    for ch in check_str.encode('utf-8').decode('utf-8'):
        if u'\u4e00' <= ch <= u'\u9fff':
            return True
    return False


def serializers_save(serializer, data):
    serializers_obj = serializer(data=data)
    if serializers_obj.is_valid():
        serializers_obj.save()
    else:
        return serializers_obj.errors


def send_emails(Title, context, target):
    """
    # send_mail的参数分别是  邮件标题，邮件内容，发件箱(settings.py中设置过的那个)，收件箱列表(可以发送给多个人),失败静默(若发送失败，报错提示我们)
    params:
        Title: 邮件标题
        context: 内容
        target: 目标邮箱 ， 列表
    """
    try:
        flag = send_mail(Title, '', EMAIL_HOST_USER, target, html_message=context, fail_silently=False)
        if not flag:
            return False, '发送失败'
    except Exception as e:
        return False, str(e)

if __name__ == "__main__":
    # check_ip("192.168.0.")
    send_emails('测试', '内容', ['1733346588@qq.com'])
