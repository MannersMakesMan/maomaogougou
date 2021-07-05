import os
import re
import shutil
import subprocess
import threading
from datetime import datetime

import redis
from drf_yasg2 import openapi
from drf_yasg2.utils import swagger_auto_schema
from rest_framework.authentication import TokenAuthentication
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView

from asset_information.models import VmServer, TestVmWorker
from automated_testing.common.api_response import JsonResponse
from basic_configuration.settings import AUTOMATED_UI_TESTING_CONF, AUTOMATED_API_TESTING_CONF
from common.redis_pool import redis_pool
from common.ssh_oprerations import ssh_oprerations
from common.tools import check_ip
from test_exe_conf.models import UiTestConfig, ApiTestConfig
from test_exe_conf.serializers import ApiTestReportSerializers, UiTestReportSerializers


class TestCaseExecute(APIView):
    # 执行单个 或 批量测试场景 异步执行 每个测试场景数据写入数据库
    authentication_classes = (TokenAuthentication,)
    permission_classes = ()
    test_type_ls = ['ui', 'api']

    def exe_ui(self, test_type, id, ip=None):
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
                mothod_path_code = configObject.method_py_path
                exe_log = subprocess.getoutput('cd {} && source ./bin/activate && cd {} && python3 runAll_remote.py -t -importcode {} -execode {} -ip {}'.format(
                    AUTOMATED_UI_TESTING_CONF['ui_test_env_path'], AUTOMATED_UI_TESTING_CONF['ui_test_pro_path'], mothod_path_code, methohds, "http://{}:4444/wd/hub".format(ip)))
            else:  # api自动化 远程ssh 执行cmd命令
                exe_log = subprocess.getoutput('cd {} && source ./bin/activate && cd {} && python3 runAll_remote.py {}'.format(
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

    def exc_all_ui(self, methods_data, test_type, vm_ip, temporary_path_ls):
        for id in methods_data:
            self.exe_ui(test_type, id, vm_ip)
        # 执行完删除临时文件
        if test_type == 'api':
            for temporary_path in temporary_path_ls:
                os.remove(temporary_path)

    @swagger_auto_schema(
        operation_summary='UI&API 启动 测试场景测试',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'test_conf_ls': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_STRING), description='需要执行的测试场景id列表'),
                # 列表参数 参照这种写法
                'test_type': openapi.Schema(type=openapi.TYPE_STRING, description='测试类型 {}'.format('/'.join(test_type_ls))),
                'vm_work': openapi.Schema(type=openapi.TYPE_STRING, description='测试执行机id 当test_type=ui需要此参数'),
            }))
    def post(self, request):
        """启动 测试场景测试 异步执行"""
        data = JSONParser().parse(request)
        methods_data = data['test_conf_ls']

        vm_ip = None
        temporary_path_ls = None

        test_type = data['test_type']
        if test_type not in self.test_type_ls:
            return JsonResponse(code="999996", msg="参数有误!")

        if len(methods_data) == 1:
            if eval("{}TestConfig.objects.get(id=methods_data[0]).teststatus".format(test_type.capitalize())) == 1:
                return JsonResponse(code="999982", msg="任务执行中!请勿重复启动!")

        if test_type == 'api':
            redis_conn = redis.Redis(connection_pool=redis_pool)  # redis链接
            # 提取api测试场景 调用的全部 function_id
            try:
                function_id_ls = set()
                for config_id in methods_data:
                    for function_id in ApiTestConfig.objects.get(id=config_id).method_id_ls.split('-->')[0: -1]:
                        function_id_ls.add(function_id)
                # 提取function所在py文件路径 并将临时文件拷贝到临时文件夹
                py_path_ls = set()
                for function_id in list(function_id_ls):
                    file_path = eval(redis_conn.hget('api_function_ls', function_id))['file_path']
                    py_path_ls.add(file_path)
                temporary_path_ls = []
                for py_path in list(py_path_ls):
                    temporary_path = os.path.join(AUTOMATED_API_TESTING_CONF['api_test_pro_path'], 'run_all_remote_temporary')
                    shutil.copy(py_path, temporary_path)
                    temporary_path_ls.append(os.path.join(temporary_path, py_path.split('/')[-1]))
            except Exception as e:
                return JsonResponse(code="999998", msg="执行失败 请重新拼接测试场景!")
        else:
            vm_work_id = data['vm_work']
            vm_worker_obj = TestVmWorker.objects.get(id=vm_work_id)
            if not vm_worker_obj:
                return JsonResponse(code="999996", msg="没有此执行机!请检查执行机配置!")
            vm_ip = vm_worker_obj.virtual_machine.Virtual_machine_IP
            if not check_ip(vm_ip):
                return JsonResponse(code="999982", msg="此虚拟机无法链接 请更换执行机!")
        t = threading.Thread(target=self.exc_all_ui, args=(methods_data, test_type, vm_ip, temporary_path_ls, ))  # 异步执行测试场景
        t.start()

        return JsonResponse(code="999999", msg="任务执行中!")

class uiCaseExecutorView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = []

    @swagger_auto_schema(
        operation_summary='UI测试用例 单个执行 用于调试',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'vm_work': openapi.Schema(type=openapi.TYPE_STRING, description='执行机id'),
                'file_name': openapi.Schema(type=openapi.TYPE_STRING, description='执行py文件名'),
                'file_path': openapi.Schema(type=openapi.TYPE_STRING, description='py文件的上层路径 不带文件名'),
            }))

    def post(self, request):
        """UI测试用例 单个执行 用于调试 返回执行日志"""
        data = JSONParser().parse(request)

        vm_work_id = data['vm_work']
        file_name = data['file_name']
        file_path = data['file_path']
        vm_worker_obj = TestVmWorker.objects.get(id=vm_work_id)
        if not vm_worker_obj:
            return JsonResponse(code="999996", msg="没有此执行机!请检查执行机配置!")
        vm_ip = vm_worker_obj.virtual_machine.Virtual_machine_IP
        if not check_ip(vm_ip):
            return JsonResponse(code="999982", msg="此虚拟机无法链接 请更换执行机!")

        # f = open(AUTOMATED_UI_TESTING_CONF['webdriver_remote_ip_conf_path'], 'r', encoding='utf-8')
        # file_content_ls = [i for i in f.readlines() if 'remoteip' not in i]
        # file_content_ls.append("\nremoteip = '{}:4444/wd/hub'".format(vm_ip))
        # f.close()
        # f = open(AUTOMATED_UI_TESTING_CONF['webdriver_remote_ip_conf_path'], 'w', encoding='utf-8')
        # f.write("".join(file_content_ls))
        # f.close()

        exe_log = subprocess.getoutput(
            'cd {} && source ./bin/activate && cd {} && python3 {} {}'.format(
                AUTOMATED_UI_TESTING_CONF['ui_test_env_path'], file_path, file_name, vm_ip))

        if "urllib3.exceptions.MaxRetryError" in exe_log:
            return JsonResponse(data=exe_log, code="999998", msg="执行机链接失败!请检查执行是否启动jar包!")

        return JsonResponse(data=exe_log, code="999999", msg="执行完成!")
