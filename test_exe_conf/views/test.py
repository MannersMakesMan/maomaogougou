import os
import re
import threading
from datetime import datetime

import redis
from drf_yasg2 import openapi
from drf_yasg2.utils import swagger_auto_schema
from rest_framework.authentication import TokenAuthentication
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView

from automated_testing.common.api_response import JsonResponse
from basic_configuration.settings import AUTOMATED_UI_TESTING_CONF, AUTOMATED_API_TESTING_CONF
from common.redis_pool import redis_pool
from common.ssh_oprerations import ssh_oprerations


class TestCaseExecute(APIView):
    # 执行单个 或 批量测试场景 异步执行 每个测试场景数据写入数据库
    authentication_classes = (TokenAuthentication,)
    permission_classes = ()
    test_type_ls = ['ui', 'api']

    def exe_ui(self, id, test_type, ssh_opr):
        """
        0:未执行
        1:执行中
        2：执行成功
        3：执行失败
        :param id:
        :param methods:
        :return:
        """
        configObject = eval("{}TestConfig.objects.get(id=id)".format(test_type.capitalize()))
        methohds = configObject.method

        try:
            configObject = eval("{}TestConfig.objects.get(id=id)".format(test_type.capitalize()))
            configObject.teststatus = 1
            configObject.exe_time = datetime.now()
            configObject.save()

            if test_type == 'ui':  # ui自动化 本地执行cmd命令
                exe_log_b = os.popen('cd {} && source ./bin/activate && cd {} && python3 runAll_remote.py {}'.format(
                    AUTOMATED_UI_TESTING_CONF['ui_test_env_path'], AUTOMATED_UI_TESTING_CONF['ui_test_pro_path'], methohds))
                exe_log = exe_log_b.read()
            else:  # api自动化 远程ssh 执行cmd命令
                exe_log = ssh_opr.exec_cmd('cd {} && source ./bin/activate && cd {} && python3 runAll_remote.py {}'.format(
                    AUTOMATED_API_TESTING_CONF['api_test_env_path'], AUTOMATED_API_TESTING_CONF['api_test_pro_path'],
                    methohds))


            if 'report_path' in exe_log:
                report_path = re.findall('==(.*?)==', exe_log)[0]
                report_file_name = "_".join(report_path.split('/')[-2:])
                configObject = eval("{}TestConfig.objects.get(id=id)".format(test_type.capitalize()))
                configObject.teststatus = 2
                configObject.test_report = report_file_name
                configObject.exe_log = exe_log
                configObject.save()

                # 執行成功 向redis mysql插入新的测试报告
                redis_conn = redis.Redis(connection_pool=redis_pool)  # redis链接
                redis_conn.hset("{}_test_report_path".format(test_type), report_file_name, report_path)
                report_data = {
                    'file_path': report_path,
                    'file_name': report_file_name,
                    'action_time': datetime(int(report_file_name.split('_')[0][0: 4]), int(report_file_name.split('_')[0][4: 6]),
                                                     int(report_file_name.split('_')[0][6: 8]),
                                                     int(report_file_name.split('_')[0][8: 10]),
                                                     int(report_file_name.split('_')[0][10: 12]),
                                                     int(report_file_name.split('_')[0][12: 14])),
                    'spend_time': None,
                    'tester': 'tester',
                    'result': '',
                }
                test_report_serializers = eval("{}TestReportSerializers(data=report_data, many=False)".format(test_type.capitalize()))  # 存储
                test_report_serializers.is_valid(raise_exception=True)
                test_report_serializers.save()

            else:
                configObject = eval("{}TestConfig.objects.get(id=id)".format(test_type.capitalize()))
                configObject.teststatus = 3
                configObject.exe_log = exe_log
                configObject.save()

        except Exception as e:
            configObject = eval("{}TestConfig.objects.get(id=id)".format(test_type.capitalize()))
            configObject.teststatus = 3
            configObject.save()

    def exc_all_ui(self, methods_data, test_type, ssh_opr):
        if test_type == 'ui':  # 修改UI自动化测试项目配置文件 remoteip
            f = open(AUTOMATED_UI_TESTING_CONF['webdriver_remote_ip_conf_path'], 'r', encoding='utf-8')
            file_content_ls = [i for i in f.readlines() if 'remoteip' not in i]
            file_content_ls.append("\nremoteip = '{}:4444/wd/hub'".format(AUTOMATED_UI_TESTING_CONF["actuator_ip"], ))
            f.close()
            f = open(AUTOMATED_UI_TESTING_CONF['webdriver_remote_ip_conf_path'], 'w', encoding='utf-8')
            f.write("".join(file_content_ls))
            f.close()

        for id in methods_data:
            self.exe_ui(id, test_type, ssh_opr)

    @swagger_auto_schema(
        operation_summary='UI&API 启动 测试场景测试',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'test_conf_ls': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_STRING), description='需要执行的测试场景id列表'),
                # 列表参数 参照这种写法
                'test_type': openapi.Schema(type=openapi.TYPE_STRING, description='测试类型 {}'.format('/'.join(test_type_ls))),
            }))
    def post(self, request):
        """启动 测试场景测试 异步执行"""
        data = JSONParser().parse(request)
        methods_data = data['test_conf_ls']
        test_type = data['test_type']
        if test_type not in self.test_type_ls:
            return JsonResponse(code="999996", msg="参数有误!")
        if len(methods_data) == 1:
            if eval("{}TestConfig.objects.get(id=methods_data[0]).teststatus".format(test_type.capitalize())) == 1:
                return JsonResponse(code="999982", msg="任务执行中!请勿重复启动!")

        ssh_opr = None
        if test_type == 'api':
            ssh_opr = ssh_oprerations(AUTOMATED_API_TESTING_CONF)
            if not ssh_opr.exec_cmd_connect():
                return JsonResponse(code="999982", msg="API自动化测试执行机链接失败 请检查网络或登录信息!")

        t = threading.Thread(target=self.exc_all_ui, args=(methods_data, test_type, ssh_opr, ))  # 异步执行测试场景
        t.start()

        return JsonResponse(code="999999", msg="任务执行中!")
