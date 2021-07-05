import os
import time
import re
import datetime
import shutil

import redis
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse
from django.views.decorators.clickjacking import xframe_options_exempt
from drf_yasg2 import openapi
from rest_framework.parsers import JSONParser
from rest_framework.authentication import TokenAuthentication
from drf_yasg2.utils import swagger_auto_schema
import requests

from manage import pro_path
from rest_framework.views import APIView
from common.redis_pool import redis_pool
from common.parse_excel import parse_excel
from common.tools import parse_pymodel
from automated_testing.common.api_response import JsonResponse
from common.ssh_oprerations import ssh_oprerations
from basic_configuration.settings import AUTOMATED_UI_TESTING_CONF, AUTOMATED_API_TESTING_CONF
from test_exe_conf.models import UiTestConfig, ApiTestConfig, UiTestReport, ApiTestReport
from test_exe_conf.serializers import UiTestReportSerializers, ApiTestReportSerializers


class automated_testing(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = []

    filter_key_words = ['__init__.py', '.zip', '.log', '.idea', '__pycache__', '.pyc', '.doc', '~$', '.lnk',
                        'test.py']  # 需要过滤的文件名
    path_type_LS = (
        'ui_common', 'ui_test_report', 'ui_test_file', 'ui_case_ls',
        'api_common', 'api_test_report', 'api_test_file', 'api_case_ls')


    def filter_path(self, file_name):
        # 筛选无用文件
        useful_flag = True
        for i in self.filter_key_words:
            if not (i not in file_name and file_name not in i and i != file_name):
                useful_flag = False
        return useful_flag

    @swagger_auto_schema(
        operation_summary='UI&API 文件扫描',
    )
    def put(self, request):
        """
        扫描UI API项目树形结构以及读取测试用例函数信息 无参数
        """
        ssh_opr = ssh_oprerations(AUTOMATED_API_TESTING_CONF)
        ssh_flag = ssh_opr.exec_cmd_connect()
        if not ssh_flag:
            return JsonResponse(code="999982", msg="API自动化远程机(linux)链接失败 请检查网络或登录信息!")

        redis_conn = redis.Redis(connection_pool=redis_pool)  # redis链接
        redis_data_tree = {}
        redis_data_path = {}
        ui_project_path = AUTOMATED_UI_TESTING_CONF['ui_test_pro_path']  # ui测试项目路径
        api_project_path = AUTOMATED_API_TESTING_CONF['api_test_pro_path']  # api测试项目路径

        # UI自动化测试 公共方法存储
        ui_common_path = '{}/common/'.format(ui_project_path)
        ui_common_file_ls = [i for i in os.listdir(ui_common_path) if self.filter_path(i)]
        redis_data_tree['ui_common'] = [{'label': i, 'path': ui_common_path + i} for i in ui_common_file_ls if
                                        self.filter_path(i)]
        redis_data_path['ui_common'] = {i: ui_common_path + i for i in ui_common_file_ls if self.filter_path(i)}

        # UI自动化测试 测试文件管理
        ui_test_file_path = '{}/testFile/case/'.format(ui_project_path)
        ui_test_file_file_data = []
        ui_test_file_file_path_ls = {}
        for ui_test_file_level1 in [i for i in os.listdir(ui_test_file_path) if self.filter_path(i)]:
            ui_test_file_path_level1 = "{}{}/".format(ui_test_file_path, ui_test_file_level1)
            if '.' not in ui_test_file_level1:
                ui_test_file_model_dict = {'label': ui_test_file_path_level1, 'children': []}
                index = 0
                for ui_test_file_level2 in [i for i in os.listdir(ui_test_file_path_level1) if self.filter_path(i)]:
                    ui_test_file_path_level2 = "{}{}/".format(ui_test_file_path_level1, ui_test_file_level2)
                    ui_test_file_model_dict['children'].append(
                        {'label': ui_test_file_level2, 'path': ui_test_file_path_level2[0: -1]})
                    ui_test_file_file_path_ls[ui_test_file_level2] = ui_test_file_path_level2[0: -1]
                    index += 1
                ui_test_file_file_data.append(ui_test_file_model_dict)

            else:
                ui_test_file_file_data.append({'label': ui_test_file_level1, 'path': ui_test_file_path_level1[0: -1]})
                ui_test_file_file_path_ls[ui_test_file_level1] = ui_test_file_path_level1[0: -1]

        redis_data_tree['ui_test_file'] = ui_test_file_file_data
        redis_data_path['ui_test_file'] = ui_test_file_file_path_ls

        # UI自动化测试 测试报告管理存储
        ui_test_report_path = '{}/result/'.format(ui_project_path)
        ui_test_report_file_path_ls = {}
        ui_test_report_dict_ls = []  # 存储进入mysql的数据
        remove_ls = []  # 待删除的列表
        index = 0  # 加入下标 避免暴力查找
        for ui_test_report_level1 in [i for i in os.listdir(ui_test_report_path) if self.filter_path(i)]:
            report_time = datetime.date(int(ui_test_report_level1[0: 4]), int(ui_test_report_level1[4: 6]),
                                        int(ui_test_report_level1[6: 8]))
            now_date = datetime.datetime.now().date()
            if now_date.__sub__(report_time).days > 30:  # 筛选超过30天的测试报告
                remove_ls.append(ui_test_report_level1)
                continue
            ui_test_report_path_level1 = ui_test_report_path + ui_test_report_level1
            for ui_test_report_level2 in [i for i in os.listdir(ui_test_report_path_level1) if self.filter_path(i)]:
                ui_test_report_path_level2 = "{}/{}".format(ui_test_report_path_level1, ui_test_report_level2)
                ui_test_report_file_path_ls[
                    "{}_{}".format(ui_test_report_level1, ui_test_report_level2)] = ui_test_report_path_level2
                ui_test_report_dict_ls.append({
                    'file_path': ui_test_report_path_level2,
                    'file_name': "{}_{}".format(ui_test_report_level1, ui_test_report_level2),
                    'action_time': datetime.datetime(int(ui_test_report_level1[0: 4]), int(ui_test_report_level1[4: 6]),
                                                     int(ui_test_report_level1[6: 8]),
                                                     int(ui_test_report_level1[8: 10]),
                                                     int(ui_test_report_level1[10: 12]),
                                                     int(ui_test_report_level1[12: 14])),
                    'spend_time': None,
                    'tester': 'tester',
                    'result': '',
                })
            index += 1
        UiTestReport.objects.all().delete()  # 清空表
        for i in remove_ls:
            shutil.rmtree('{}{}'.format(ui_test_report_path, i))
            # 删除本地超过30天的测试报告
        test_report_serializers = UiTestReportSerializers(data=ui_test_report_dict_ls, many=True)  # 存储
        test_report_serializers.is_valid(raise_exception=True)
        test_report_serializers.save()
        redis_data_path['ui_test_report'] = ui_test_report_file_path_ls

        # UI自动化测试 测试用例管理
        ui_function_ls = {}
        ui_case_file_path_ls = {}
        ui_case_file_data = []
        ui_case_ls_path = '{}/testCase/ui_testCase/'.format(ui_project_path)
        for ui_case_ls_level1 in [i for i in os.listdir(ui_case_ls_path) if
                                  self.filter_path(i)]:
            ui_case_ls_path_level1 = "{}{}/".format(ui_case_ls_path, ui_case_ls_level1)
            if '.' not in ui_case_ls_level1:
                ui_case_model_dict = {'label': ui_case_ls_level1, 'children': []}
                index = 0  # 优化 加入下标 避免暴力查找
                for ui_case_ls_level2 in [i for i in os.listdir(ui_case_ls_path_level1) if
                                          self.filter_path(i)]:
                    ui_case_ls_path_level2 = "{}{}/".format(ui_case_ls_path_level1, ui_case_ls_level2)
                    if '.' not in ui_case_ls_level2:
                        ui_case_model_dict['children'].append({'label': ui_case_ls_level2, 'children': []})
                        for ui_case_ls_level3 in [i for i in os.listdir(ui_case_ls_path_level2)
                                                  if self.filter_path(i)]:
                            ui_case_ls_path_level3 = "{}{}/".format(ui_case_ls_path_level2, ui_case_ls_level3)
                            if '.' not in ui_case_ls_level3:
                                pass
                            else:
                                ui_case_model_dict['children'][index]['children'].append(
                                    {'label': ui_case_ls_level3, 'path': ui_case_ls_path_level3[0: -1]})
                                ui_case_file_path_ls[ui_case_ls_level3] = ui_case_ls_path_level3[0: -1]
                                ui_function_ls = parse_pymodel(ui_case_ls_path_level3[0: -1], ui_case_ls_level3,
                                                               ui_function_ls, ui_case_ls_path_level3[0: -1])

                    else:
                        ui_case_model_dict['children'].append(
                            {'label': ui_case_ls_level2, 'path': ui_case_ls_path_level2[0: -1]})
                        ui_case_file_path_ls[ui_case_ls_level2] = ui_case_ls_path_level2[0: -1]
                        ui_function_ls = parse_pymodel(ui_case_ls_path_level2[0: -1], ui_case_ls_level2, ui_function_ls,
                                                       ui_case_ls_path_level2[0: -1])

                    index += 1
                ui_case_file_data.append(ui_case_model_dict)
            else:
                ui_case_file_data.append({'label': ui_case_ls_level1, 'path': ui_case_ls_path_level1[0: -1]})
                ui_case_file_path_ls[ui_case_ls_level1] = ui_case_ls_path_level1[0: -1]
                ui_function_ls = parse_pymodel(ui_case_ls_path_level1[0: -1], ui_case_ls_level1, ui_function_ls,
                                               ui_case_ls_path_level1[0: -1])

        redis_data_tree['ui_case_ls'] = ui_case_file_data
        redis_data_path['ui_case_ls'] = ui_case_file_path_ls

        # API自动化测试 公共方法管理
        api_common_path = '{}/common/'.format(api_project_path)
        api_common_file_ls = ssh_opr.exec_cmd('cd {} && ls'.format(api_common_path), 'ls')
        redis_data_tree['api_common'] = [{'label': i, 'path': api_common_path + i} for i in api_common_file_ls
                                         if self.filter_path(i)]
        redis_data_path['api_common'] = {i: api_common_path + i for i in api_common_file_ls if
                                         self.filter_path(i)}

        # API自动化测试 测试文件管理
        api_api_excel_path = '{}/testFile/case/'.format(api_project_path)
        api_api_excel_file_ls = ssh_opr.exec_cmd('cd {} && ls'.format(api_api_excel_path), 'ls')
        redis_data_tree['api_test_file'] = [{'label': i, 'path': api_api_excel_path + i} for i in api_api_excel_file_ls
                                            if self.filter_path(i)]
        redis_data_path['api_test_file'] = {i: api_api_excel_path + i for i in api_api_excel_file_ls if
                                            self.filter_path(i)}

        # # UI自动化测试 测试执行脚本存储
        # api_run_path = '{}/runAll_remote.py'.format(api_project_path)
        # redis_data_tree['api_run'] = [{'label': 'runAll_remote.py', 'path': api_run_path}]
        # redis_data_path['api_run'] = {'runAll_remote.py': api_run_path}

        # API自动化测试 测试报告管理存储
        api_test_report_path = '{}/result/'.format(api_project_path)
        api_test_report_file_path_ls = {}
        api_test_report_dict_ls = []
        index = 0  # 加入下标 避免暴力查找
        for api_test_report_level1 in [i for i in ssh_opr.exec_cmd('cd {} && ls'.format(api_test_report_path), 'ls') if
                                       self.filter_path(i)]:
            report_time = datetime.date(int(api_test_report_level1[0: 4]), int(api_test_report_level1[4: 6]),
                                        int(api_test_report_level1[6: 8]))
            now_date = datetime.datetime.now().date()
            if now_date.__sub__(report_time).days > 30:  # 筛选超过30天的测试报告
                remove_ls.append(api_test_report_level1)
                continue
            api_test_report_path_level1 = api_test_report_path + api_test_report_level1
            for api_test_report_level2 in [i for i in
                                           ssh_opr.exec_cmd('cd {} && ls'.format(api_test_report_path_level1), 'ls') if
                                           self.filter_path(i)]:
                api_test_report_path_level2 = "{}/{}".format(api_test_report_path_level1, api_test_report_level2)
                api_test_report_file_path_ls[
                    "{}_{}".format(api_test_report_level1, api_test_report_level2)] = api_test_report_path_level2
                api_test_report_dict_ls.append({
                    'file_path': api_test_report_path_level2,
                    'file_name': "{}_{}".format(api_test_report_level1, api_test_report_level2),
                    'action_time': datetime.datetime(int(api_test_report_level1[0: 4]),
                                                     int(api_test_report_level1[4: 6]),
                                                     int(api_test_report_level1[6: 8]),
                                                     int(api_test_report_level1[8: 10]),
                                                     int(api_test_report_level1[10: 12]),
                                                     int(api_test_report_level1[12: 14])),
                    'spend_time': None,
                    'tester': 'tester',
                    'result': '',
                })
            index += 1
        ApiTestReport.objects.all().delete()  # 清空表
        for i in remove_ls:
            shutil.rmtree('{}{}'.format(api_test_report_path, i))
            # 删除本地超过30天的测试报告
        test_report_serializers = ApiTestReportSerializers(data=api_test_report_dict_ls, many=True)  # 存储
        test_report_serializers.is_valid(raise_exception=True)
        test_report_serializers.save()
        redis_data_path['api_test_report'] = api_test_report_file_path_ls

        # API自动化测试 测试用例管理
        api_function_ls = {}
        api_case_file_path = '{}/testCase/api_case/'.format(api_project_path)
        api_case_file_ls = ssh_opr.exec_cmd('cd {} && ls'.format(api_case_file_path), 'ls')
        redis_data_tree['api_case_ls'] = []
        for api_case_file_name in api_case_file_ls:
            if self.filter_path(api_case_file_name):
                redis_data_tree['api_case_ls'].append(
                    {'label': api_case_file_name, 'path': api_case_file_path + api_case_file_name})
                file_content = ssh_opr.open_file(api_case_file_path + api_case_file_name)  # 读取远程文件数据
                temporary_file_name = "{}_{}".format(int(round(time.time())), api_case_file_name)
                temporary_file_path = "{}/automated_testing/ssh_excel_temporary/{}".format(pro_path, temporary_file_name)
                temporary = open(temporary_file_path, 'w')  # 创建本地临时文件用于解析
                temporary.write(file_content)
                temporary.close()
                api_function_ls = parse_pymodel(temporary_file_path, api_case_file_name, api_function_ls,
                                                api_case_file_path + api_case_file_name)
                os.remove(temporary_file_path)
        redis_data_path['api_case_ls'] = {i: api_case_file_path + i for i in api_case_file_ls if self.filter_path(i)}

        for key in zip(redis_data_tree.keys(), redis_data_path.keys()):
            redis_key = key[0]
            redis_conn.delete("{}_tree".format(redis_key))
            redis_conn.delete("{}_path".format(redis_key))
            redis_conn.set("{}_tree".format(redis_key), str(redis_data_tree[redis_key]))
            redis_conn.hmset("{}_path".format(redis_key), redis_data_path[redis_key])

        redis_conn.delete("{}_path".format('ui_test_report'))
        redis_conn.delete("{}_path".format('api_test_report'))
        redis_conn.hmset("{}_path".format('ui_test_report'), redis_data_path['ui_test_report'])
        redis_conn.hmset("{}_path".format('api_test_report'), redis_data_path['api_test_report'])

        redis_conn.delete('ui_function_ls')
        redis_conn.delete('api_function_ls')
        redis_conn.hmset('ui_function_ls', ui_function_ls)
        redis_conn.hmset('api_function_ls', api_function_ls)

        return JsonResponse(code="999999", msg="目录结构更新成功!")

    @swagger_auto_schema(
        operation_summary='API&UI 项目模块tree结构查询',
        manual_parameters=[
            openapi.Parameter(name='path_type', in_=openapi.IN_QUERY, description='查询的模块名称 {}'.format('/'.join(path_type_LS)), type=openapi.TYPE_STRING),
            openapi.Parameter(name='page', in_=openapi.IN_QUERY, description='页码 当 path_type=ui_test_report/api_test_report 存在此参数', type=openapi.TYPE_STRING),
            openapi.Parameter(name='page_size', in_=openapi.IN_QUERY, description='数量 当 path_type=ui_test_report/api_test_report 存在此参数', type=openapi.TYPE_STRING),
            openapi.Parameter(name='file_name', in_=openapi.IN_QUERY, description='测试报告文件名 当 path_type=ui_test_report/api_test_report 存在此参数', type=openapi.TYPE_STRING),
        ])
    def get(self, request):
        """ 查询 对应菜单模块的tree结构"""
        path_type = request.GET.get("path_type")
        if path_type not in self.path_type_LS:
            return JsonResponse(code="999996", msg="参数有误!")
        redis_conn = redis.Redis(connection_pool=redis_pool)  # redis链接
        if 'test_report' in path_type:   # 测试报告走mysql 非树形结构 分页
            test_type = path_type.split('_')[0]
            page_size = int(request.GET.get("page_size"))
            page = int(request.GET.get("page"))
            file_name = request.GET.get("file_name")

            aQ = Q()
            if file_name:  # 多字段筛选
                aQ.add(Q(file_name__contains=file_name), Q.AND)
            queryset = eval('{}TestReport.objects.filter(aQ).order_by("-id")'.format(test_type.capitalize()))

            paginator = Paginator(queryset, page_size)  # paginator对象
            total = len(queryset)  # 总数量
            try:
                obm = paginator.page(page)

                serialize = eval('{}TestReportSerializers(obm, many=True)'.format(test_type.capitalize()))

                return_data = {"data": serialize.data,
                               "page": page,
                               "total": total}

            except Exception as _e:
                return_data = []
        else:
            return_data = eval(redis_conn.get("{}_tree".format(path_type)))
        return JsonResponse(data=return_data, code="999999", msg="成功!")


class automated_testing_file_edit(APIView):
    # 自动化测试 通过ssh 修改/查询远程主机文件
    authentication_classes = (TokenAuthentication,)
    permission_classes = []
    path_type_LS = (
        'ui_common', 'ui_test_report', 'ui_test_file', 'ui_case_ls',
        'api_common', 'api_test_report', 'api_test_file', 'api_case_ls')  # 可查询的文件类型
    edit_path_type_LS = (
        'ui_common', 'ui_case_ls', 'api_common', 'api_case_ls'
    ) # 可编辑的文件类型
    file_data_type_LS = ('str')

    @swagger_auto_schema(
        operation_summary='API&UI 文件数据查询',
        manual_parameters=[
            openapi.Parameter(name='file_id', in_=openapi.IN_QUERY, description='测试配置执行时 查看测试报告 使用此参数 其余使用file_name参数',
                              type=openapi.TYPE_STRING),
            openapi.Parameter(name='file_name', in_=openapi.IN_QUERY, description='查询文件名称', type=openapi.TYPE_STRING),
            openapi.Parameter(name='route_type', in_=openapi.IN_QUERY,
                              description='查询文件所属模块 {}'.format('/'.join(path_type_LS)), type=openapi.TYPE_STRING),
            openapi.Parameter(name='file_data_type', in_=openapi.IN_QUERY, description='返回数据类型 固定 str',
                              type=openapi.TYPE_STRING),
        ])
    def get(self, request):
        # 根据文件名 返回 文件字符串
        route_type = request.GET.get('route_type')  # 上级菜单名称
        if route_type not in self.path_type_LS:
            return JsonResponse(code="999996", msg="参数有误!")
        try:
            file_id = request.GET.get('file_id')
            config_object = eval('{}TestConfig.objects.get(id=file_id)'.format(route_type.split('_')[0].capitalize()))
            file_name = config_object.test_report
            if not file_name:
                return JsonResponse(code="999981", msg="未找到文件, 请联系管理员!")
        except:
            file_name = request.GET.get("file_name")


        file_data_type = request.GET.get("file_data_type")  # 返回文件 数据类型
        if file_data_type not in self.file_data_type_LS:
            return JsonResponse(code="999996", msg="参数有误!")
        redis_conn = redis.Redis(connection_pool=redis_pool)  # redis链接
        file_path = redis_conn.hget("{}_path".format(route_type), file_name)  # 文件路径

        if not file_path:
            return JsonResponse(code="999981", msg="未找到文件, 请联系管理员!")

        if 'api' in route_type:  # 进行api相关文件查询 执行ssh链接
            ssh_opr = ssh_oprerations(AUTOMATED_API_TESTING_CONF)
            if not ssh_opr.sftp_connect():
                return JsonResponse(code="999982", msg="API自动化远程机(linux)链接失败 请检查网络或登录信息!")
            if 'test_file' in route_type:
                file_content = ssh_opr.open_file(file_path, 'rb')
            else:
                file_content = ssh_opr.open_file(file_path)

            if not file_content:
                return JsonResponse(code="999981", msg="未找到文件, 请联系管理员!")
        else:  # 进行ui相关文件查询 执行本地

            if 'test_file' not in route_type:
                file_content = open(file_path, 'r', encoding='utf-8').read()

        res_data = {'file_name': file_name,
                    'file_data_type': file_data_type,
                    }
        if 'test_file' not in route_type and 'test_report' not in route_type:
            res_data['file_content'] = file_content

        if route_type == 'api_test_file':  # 查询excel文件 先将远程主机excel写入本地临时文件 本地解析数据进行返回 删除本地临时文件
            temporary_file_name = "{}_{}".format(int(round(time.time())), file_name)
            temporary_file_path = "{}/automated_testing/ssh_excel_temporary/{}".format(pro_path, temporary_file_name)
            temporary = open(temporary_file_path, 'wb')
            temporary.write(file_content)
            temporary.close()
            res_data['file_content'] = parse_excel(temporary_file_path)
            os.remove(temporary_file_path)
        elif route_type == 'ui_test_file':
            res_data['file_content'] = parse_excel(file_path)

        if route_type == 'ui_test_report' or route_type == 'api_test_report':
            if file_content == '':
                return JsonResponse(code="999981", msg="未找到文件, 请联系管理员!")
            tester = re.findall('测试人员:</strong>(.*?)</p>', file_content)
            start_time = re.findall('开始时间:</strong>(.*?)</p>', file_content)
            spend_time = re.findall('运行时长:</strong>(.*?)</p>', file_content)
            test_result = re.findall('状态:</strong>(.*?)</p>', file_content)

            report_obj = eval('{}TestReport.objects.get(file_name=file_name)'.format(route_type.split('_')[0].capitalize()))
            report_obj.spend_time = spend_time[0] if spend_time else ''
            report_obj.result = test_result[0] if test_result else ''
            report_obj.save()

            res_data['tester'] = tester[0] if tester else ''
            res_data['start_time'] = start_time[0] if start_time else ''
            res_data['spend_time'] = spend_time[0] if spend_time else ''
            res_data['test_result'] = test_result[0] if test_result else ''
            if route_type == 'ui_test_report':
                res_data['report_src'] = '/Operation_maintenance/test_report?test_type=ui&file_name={}'.format(
                    file_name)
            else:
                res_data['report_src'] = '/Operation_maintenance/test_report?test_type=api&file_name={}'.format(
                    file_name)

        return JsonResponse(data=res_data, code="999999", msg="成功!")

    @swagger_auto_schema(
        operation_summary='API&UI项目 文件修改',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'file_name': openapi.Schema(type=openapi.TYPE_STRING, description='查询文件名称'),
                'route_type': openapi.Schema(type=openapi.TYPE_STRING,
                                             description='查询文件所属模块 {}'.format('/'.join(edit_path_type_LS))),
                'file_content': openapi.Schema(type=openapi.TYPE_STRING, description='需要写入的文件内容(全量)'),
            }))
    def post(self, request):
        """修改文件 上传文件接口"""
        data = JSONParser().parse(request)
        redis_conn = redis.Redis(connection_pool=redis_pool)  # redis链接
        file_name = data["file_name"]  # 文件名

        route_type = data['route_type']  # 上级菜单名称
        if route_type not in self.edit_path_type_LS:
            return JsonResponse(code="999996", msg="参数有误!")
        file_content = data['file_content']  # 需要写入的文件内容
        file_path = redis_conn.hget("{}_path".format(route_type), file_name)  # 文件路径

        if not file_path:
            return JsonResponse(code="999981", msg="未找到文件, 请联系管理员!")

        if 'api' in route_type:  # 进行api相关文件查询 执行ssh链接
            ssh_opr = ssh_oprerations(AUTOMATED_API_TESTING_CONF)
            if not ssh_opr.sftp_connect():
                return JsonResponse(code="999982", msg="API自动化远程机(linux)链接失败 请检查网络或登录信息!")
            flag = ssh_opr.write_file(file_path, file_content)
            if not flag:
                return JsonResponse(code="999981", msg="未找到文件, 请联系管理员!")
        else:  # 进行ui相关文件修改 进行本地读写
            try:
                f = open(file_path, 'w', encoding='utf-8')
                f.write(file_content)
                f.close()
            except Exception as e:
                return JsonResponse(code="999981", msg="未找到文件, 请联系管理员!")

        return JsonResponse(code="999999", msg="成功!")


class api_test_case_create(APIView):
    # API自动化测试 执行swagger解析脚本 执行测试用例生成脚本
    authentication_classes = (TokenAuthentication,)
    permission_classes = []

    Swagger_parse_file_name = 'swagger_parse_main.py'  # 请求swagger 解析脚本
    GenerationScript_file_name = 'GenerationScript_main.py'  # 生成测试用例脚本

    @swagger_auto_schema(
        operation_summary='API自动化测试 swagger数据解析 测试用例生成 测试文件生成',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'action_type': openapi.Schema(type=openapi.TYPE_STRING,
                                              description='执行方式 SwaggerParse/GenerationTestFile/GenerationScript'),
                'swagger_url': openapi.Schema(type=openapi.TYPE_STRING,
                                              description='swagger地址 当action_type=SwaggerParse 需要此参数'),
            }))
    def post(self, request):
        """链接API自动化测试执行机 远程执行swaggger数据解析 生成测试用例"""
        data = JSONParser().parse(request)
        action_type = data['action_type']  # 执行方式
        ssh_opr = ssh_oprerations(AUTOMATED_API_TESTING_CONF)
        if not ssh_opr.exec_cmd_connect():
            return JsonResponse(code="999982", msg="虚拟机链接失败 请检查网络或登录信息!")

        if action_type == 'SwaggerParse':
            # 执行swagger解析
            swagger_url = data['swagger_url']
            exec_result = ssh_opr.exec_cmd('cd {} && source bin/activate && cd .. && python3 {} {}'.format(
                AUTOMATED_API_TESTING_CONF['api_test_env_path'], self.Swagger_parse_file_name, swagger_url))
            try:
                if '/v2/api-docs' in swagger_url:
                    pass
                else:
                    swagger_url = swagger_url + '/v2/api-docs'
                res_json = requests.get(swagger_url, timeout=2).json()  # 这才是swagger接口请求的地址
                if 'success' in exec_result:
                    return JsonResponse(data=res_json, code='999999', msg='成功!')

            except Exception as e:
                return JsonResponse(data='请求swagger地址错误. url: {},  异常如下: {}'.format(swagger_url, e), code='999998', msg='失败!')

        elif action_type == 'GenerationTestFile':
            # 执行测试脚本生成
            exec_result = ssh_opr.exec_cmd('cd {} && source bin/activate && cd .. && python3 {} {}'.format(
                AUTOMATED_API_TESTING_CONF['api_test_env_path'], self.Swagger_parse_file_name, action_type))

        elif action_type == 'GenerationScript':
            # 执行测试用例生成
            exec_result = ssh_opr.exec_cmd('cd {} && source bin/activate && cd .. && python3 {}'.format(
                AUTOMATED_API_TESTING_CONF['api_test_env_path'], self.GenerationScript_file_name))
        else:
            return JsonResponse(code="999996", msg="参数有误!")

        if 'success' in exec_result:
            res_data = exec_result.replace('success', '')
            code = '999999'
            msg = '成功!'
        else:
            code = '999998'
            msg = '失败!'
            res_data = "\n".join(re.findall("==(.*?)==", exec_result))

        return JsonResponse(data=res_data, code=code, msg=msg)


class test_report_view(APIView):
    # 测试报告接口
    authentication_classes = (TokenAuthentication,)
    permission_classes = []
    test_type_ls = ['ui', 'api']

    @swagger_auto_schema(
        operation_summary='API&UI 测试报告查询',
        manual_parameters=[
            openapi.Parameter(name='test_type', in_=openapi.IN_QUERY,
                              description='查询的模块名称 {}'.format('/'.join(test_type_ls)), type=openapi.TYPE_STRING),
            openapi.Parameter(name='file_name', in_=openapi.IN_QUERY, description='查询测试报告文件名', type=openapi.TYPE_STRING)
        ])
    @xframe_options_exempt
    def get(self, request):
        test_type = request.GET.get('test_type')
        file_name = request.GET.get('file_name')
        redis_conn = redis.Redis(connection_pool=redis_pool)  # redis链接
        file_path = redis_conn.hget("{}_test_report_path".format(test_type), file_name)  # 文件路径

        if not file_path:
            return JsonResponse(code="999981", msg="未找到文件, 请联系管理员!")

        if test_type == 'api':
            ssh_opr = ssh_oprerations(AUTOMATED_API_TESTING_CONF)
            if not ssh_opr.sftp_connect():
                return JsonResponse(code="999982", msg="API自动化远程机(linux)链接失败 请检查网络或登录信息!")
            file_content = ssh_opr.open_file(file_path, 'rb')
            return HttpResponse(content=file_content, )  # 使用绝对路径返回html文件方式
        else:
            return HttpResponse(content=open(file_path).read(), )  # 使用绝对路径返回html文件方式







