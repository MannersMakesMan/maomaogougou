import os
import subprocess
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
import pandas as pd
from pandas import DataFrame

from automatic_api.local_swagger_parse import AnalysisSwaggerJson
from common.parse_ui_testCase import format_ui_case
from common.regular_ls import REGEX_PY_MODEL, REGEX_FOLD
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

    filter_key_words = ['__init__.py', '.zip', '.log', '.idea', '__pycache__', '.pyc', '.doc', '~$', '.lnk']  # 需要过滤的文件名
    path_type_LS = (
        'ui_common', 'ui_test_report', 'ui_test_file', 'ui_case_ls',
        'api_common', 'api_test_report', 'api_test_file', 'api_case_ls')

    ui_project_path = AUTOMATED_UI_TESTING_CONF['ui_test_pro_path']  # ui测试项目路径
    api_project_path = AUTOMATED_API_TESTING_CONF['api_test_pro_path']  # api测试项目路径

    def filter_path(self, file_name):
        # 筛选无用文件
        useful_flag = True
        for i in self.filter_key_words:
            if not (i not in file_name and file_name not in i and i != file_name):
                useful_flag = False
        return useful_flag

    def ui_test_case_scan(self, redis_conn):
        # UI自动化测试 测试用例管理 树形结构扫描
        ui_function_ls = {}
        ui_case_file_path_ls = {}
        ui_case_file_data = []
        ui_case_ls_path = '{}/testCase/ui_testCase/'.format(self.ui_project_path)
        for ui_case_ls_level1 in [i for i in os.listdir(ui_case_ls_path) if self.filter_path(i)]:
            ui_case_ls_path_level1 = "{}{}/".format(ui_case_ls_path, ui_case_ls_level1)
            if '.' not in ui_case_ls_level1:
                ui_case_model_dict = {'label': ui_case_ls_level1, 'path': ui_case_ls_path_level1[0: -1], 'children': []}
                index = 0  # 优化 加入下标 避免暴力查找
                for ui_case_ls_level2 in [i for i in os.listdir(ui_case_ls_path_level1) if self.filter_path(i)]:
                    ui_case_ls_path_level2 = "{}{}/".format(ui_case_ls_path_level1, ui_case_ls_level2)
                    if '.' not in ui_case_ls_level2:
                        ui_case_model_dict['children'].append({'label': ui_case_ls_level2, 'path': ui_case_ls_path_level2[0: -1], 'children': []})
                        index1 = 0
                        for ui_case_ls_level3 in [i for i in os.listdir(ui_case_ls_path_level2) if self.filter_path(i)]:
                            ui_case_ls_path_level3 = "{}{}/".format(ui_case_ls_path_level2, ui_case_ls_level3)
                            if '.' not in ui_case_ls_level3:
                                ui_case_model_dict['children'][index]['children'].append({'label': ui_case_ls_level3, 'path': ui_case_ls_path_level3[0: -1], 'children': []})
                                for ui_case_ls_level4 in [i for i in os.listdir(ui_case_ls_path_level3) if self.filter_path(i)]:
                                    ui_case_ls_path_level4 = "{}{}/".format(ui_case_ls_path_level3, ui_case_ls_level4)
                                    if "." not in ui_case_ls_level4:
                                        pass
                                    else:
                                        ui_case_model_dict['children'][index]['children'][index1]['children'].append({'label': ui_case_ls_level4, 'path': ui_case_ls_path_level4[0: -1]})
                                        ui_case_file_path_ls[ui_case_ls_level4] = ui_case_ls_path_level4[0: -1]
                                        ui_function_ls = parse_pymodel(ui_case_ls_path_level4[0: -1], ui_case_ls_level4, ui_function_ls, ui_case_ls_path_level4[0: -1])

                            else:
                                ui_case_model_dict['children'][index]['children'].append({'label': ui_case_ls_level3, 'path': ui_case_ls_path_level3[0: -1]})
                                ui_case_file_path_ls[ui_case_ls_level3] = ui_case_ls_path_level3[0: -1]
                                ui_function_ls = parse_pymodel(ui_case_ls_path_level3[0: -1], ui_case_ls_level3, ui_function_ls, ui_case_ls_path_level3[0: -1])
                            index1 += 1
                    else:
                        ui_case_model_dict['children'].append({'label': ui_case_ls_level2, 'path': ui_case_ls_path_level2[0: -1]})
                        ui_case_file_path_ls[ui_case_ls_level2] = ui_case_ls_path_level2[0: -1]
                        ui_function_ls = parse_pymodel(ui_case_ls_path_level2[0: -1], ui_case_ls_level2, ui_function_ls, ui_case_ls_path_level2[0: -1])
                    index += 1
                ui_case_file_data.append(ui_case_model_dict)
            else:
                ui_case_file_data.append({'label': ui_case_ls_level1, 'path': ui_case_ls_path_level1[0: -1]})
                ui_case_file_path_ls[ui_case_ls_level1] = ui_case_ls_path_level1[0: -1]
                ui_function_ls = parse_pymodel(ui_case_ls_path_level1[0: -1], ui_case_ls_level1, ui_function_ls, ui_case_ls_path_level1[0: -1])
        redis_conn.delete('ui_function_ls')
        redis_conn.hmset('ui_function_ls', ui_function_ls)
        redis_conn.delete("ui_case_ls_path")
        redis_conn.hmset("ui_case_ls_path", ui_case_file_path_ls)
        redis_conn.delete("ui_case_ls_tree")
        redis_conn.set("ui_case_ls_tree", str(ui_case_file_data))


    # def api_test_case_scan(self, redis_conn):
    #     # API自动化测试 测试用例管理
    #     api_function_ls = {}
    #     api_case_file_path_ls = {}
    #     api_case_file_data = []
    #     api_case_ls_path = '{}/testCase/api_case/'.format(self.api_project_path)
    #     for api_case_ls_level1 in [i for i in os.listdir(api_case_ls_path) if self.filter_path(i)]:
    #         api_case_ls_path_level1 = "{}{}/".format(api_case_ls_path, api_case_ls_level1)
    #         if '.' not in api_case_ls_level1:
    #             api_case_model_dict = {'label': api_case_ls_level1, 'path': api_case_ls_path_level1[0: -1],
    #                                    'children': []}
    #             index = 0  # 优化 加入下标 避免暴力查找
    #             for api_case_ls_level2 in [i for i in os.listdir(api_case_ls_path_level1) if self.filter_path(i)]:
    #                 api_case_ls_path_level2 = "{}{}/".format(api_case_ls_path_level1, api_case_ls_level2)
    #                 if '.' not in api_case_ls_level2:
    #                     api_case_model_dict['children'].append(
    #                         {'label': api_case_ls_level2, 'path': api_case_ls_path_level2[0: -1], 'children': []})
    #                     for api_case_ls_level3 in [i for i in os.listdir(api_case_ls_path_level2) if
    #                                                self.filter_path(i)]:
    #                         api_case_ls_path_level3 = "{}{}/".format(api_case_ls_path_level2, api_case_ls_level3)
    #                         if '.' not in api_case_ls_level3:
    #                             pass
    #                         else:
    #                             api_case_model_dict['children'][index]['children'].append(
    #                                 {'label': api_case_ls_level3, 'path': api_case_ls_path_level3[0: -1]})
    #                             api_case_file_path_ls[api_case_ls_level3] = api_case_ls_path_level3[0: -1]
    #                             api_function_ls = parse_pymodel(api_case_ls_path_level3[0: -1], api_case_ls_level3,
    #                                                             api_function_ls, api_case_ls_path_level3[0: -1], 'api')
    #                 index += 1
    #             api_case_file_data.append(api_case_model_dict)
    #
    #     redis_conn.delete('api_function_ls')
    #     redis_conn.hmset('api_function_ls', api_function_ls)
    #     redis_conn.delete("api_case_ls_path")
    #     redis_conn.hmset("api_case_ls_path", api_case_file_path_ls)
    #     redis_conn.delete("api_case_ls_tree")
    #     redis_conn.set("api_case_ls_tree", str(api_case_file_data))


    def ui_test_file_scan(self, redis_conn):
        ui_test_file_file_path_ls = {}
        ui_test_file_file_data = []
        ui_test_file_path = '{}/testFile/case/'.format(self.ui_project_path)
        for ui_test_file_level1 in [i for i in os.listdir(ui_test_file_path) if self.filter_path(i)]:
            ui_test_file_path_level1 = "{}{}/".format(ui_test_file_path, ui_test_file_level1)
            if '.' not in ui_test_file_level1:
                ui_test_file_model_dict = {'label': ui_test_file_level1, 'path': ui_test_file_path_level1[0: -1], 'children': []}
                index = 0  # 优化 加入下标 避免暴力查找
                for ui_test_file_level2 in [i for i in os.listdir(ui_test_file_path_level1) if self.filter_path(i)]:
                    ui_test_file_path_level2 = "{}{}/".format(ui_test_file_path_level1, ui_test_file_level2)
                    if '.' not in ui_test_file_level2:
                        ui_test_file_model_dict['children'].append({'label': ui_test_file_level2, 'path': ui_test_file_path_level2[0: -1], 'children': []})
                        index1 = 0
                        for ui_test_file_level3 in [i for i in os.listdir(ui_test_file_path_level2) if self.filter_path(i)]:
                            ui_test_file_path_level3 = "{}{}/".format(ui_test_file_path_level2, ui_test_file_level3)
                            if '.' not in ui_test_file_level3:
                                ui_test_file_model_dict['children'][index]['children'].append({'label': ui_test_file_level3, 'path': ui_test_file_path_level3[0: -1], 'children': []})
                                for ui_test_file_level4 in [i for i in os.listdir(ui_test_file_path_level3) if self.filter_path(i)]:
                                    ui_test_file_path_level4 = "{}{}/".format(ui_test_file_path_level3, ui_test_file_level4)
                                    if "." not in ui_test_file_level4:
                                        pass
                                    else:
                                        ui_test_file_model_dict['children'][index]['children'][index1]['children'].append({'label': ui_test_file_level4, 'path': ui_test_file_path_level4[0: -1]})
                                        ui_test_file_file_path_ls[ui_test_file_level4] = ui_test_file_path_level4[0: -1]

                            else:
                                ui_test_file_model_dict['children'][index]['children'].append({'label': ui_test_file_level3, 'path': ui_test_file_path_level3[0: -1]})
                                ui_test_file_file_path_ls[ui_test_file_level3] = ui_test_file_path_level3[0: -1]
                            index1 += 1
                    else:
                        ui_test_file_model_dict['children'].append({'label': ui_test_file_level2, 'path': ui_test_file_path_level2[0: -1]})
                        ui_test_file_file_path_ls[ui_test_file_level2] = ui_test_file_path_level2[0: -1]
                    index += 1
                ui_test_file_file_data.append(ui_test_file_model_dict)
            else:
                ui_test_file_file_data.append({'label': ui_test_file_level1, 'path': ui_test_file_path_level1[0: -1]})
                ui_test_file_file_path_ls[ui_test_file_level1] = ui_test_file_path_level1[0: -1]

        redis_conn.delete("ui_test_file_path")
        redis_conn.hmset("ui_test_file_path", ui_test_file_file_path_ls)
        redis_conn.delete("ui_test_file_tree")
        redis_conn.set("ui_test_file_tree", str(ui_test_file_file_data))

    @swagger_auto_schema(
        operation_summary='UI&API 文件扫描',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'scan_type': openapi.Schema(type=openapi.TYPE_STRING, description='扫描的模块 all/ui_case_ls/api_case_ls/ui_test_file'),
            })
    )
    def put(self, request):
        """
        扫描UI API项目树形结构以及读取测试用例函数信息 无参数
        """
        redis_conn = redis.Redis(connection_pool=redis_pool)  # redis链接
        data = JSONParser().parse(request)
        scan_type = data['scan_type']

        if scan_type == 'ui_case_ls':
            self.ui_test_case_scan(redis_conn)
            return JsonResponse(code="999999", msg="目录结构更新成功!")

        # elif scan_type == 'api_case_ls':
        #     self.api_test_case_scan(redis_conn)
        #     return JsonResponse(code="999999", msg="目录结构更新成功!")

        elif scan_type == 'ui_test_file':
            self.ui_test_file_scan(redis_conn)
            return JsonResponse(code="999999", msg="目录结构更新成功!")

        else:

            self.ui_test_case_scan(redis_conn)
            # self.api_test_case_scan(redis_conn)
            self.ui_test_file_scan(redis_conn)

            redis_data_tree = {}
            redis_data_path = {}

            # UI自动化测试 公共方法存储
            ui_common_path = '{}/common/'.format(self.ui_project_path)
            ui_common_file_ls = [i for i in os.listdir(ui_common_path) if self.filter_path(i)]
            redis_data_tree['ui_common'] = [{'label': i, 'path': ui_common_path + i} for i in ui_common_file_ls if self.filter_path(i)]
            redis_data_path['ui_common'] = {i: ui_common_path + i for i in ui_common_file_ls if self.filter_path(i)}


            # UI自动化测试 测试报告管理存储
            ui_test_report_path = '{}/result/'.format(self.ui_project_path)
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
                try:
                    shutil.rmtree('{}{}'.format(ui_test_report_path, i))
                except:
                    pass
                # 删除本地超过30天的测试报告
            test_report_serializers = UiTestReportSerializers(data=ui_test_report_dict_ls, many=True)  # 存储
            test_report_serializers.is_valid(raise_exception=True)
            test_report_serializers.save()
            redis_data_path['ui_test_report'] = ui_test_report_file_path_ls

            # # API自动化测试 公共方法管理
            # api_common_path = '{}/common/'.format(self.api_project_path)
            # api_common_file_ls = [i for i in os.listdir(api_common_path) if self.filter_path(i)]
            # redis_data_tree['api_common'] = [{'label': i, 'path': api_common_path + i} for i in api_common_file_ls
            #                                  if self.filter_path(i)]
            # redis_data_path['api_common'] = {i: api_common_path + i for i in api_common_file_ls if
            #                                  self.filter_path(i)}
            #
            # # API自动化测试 测试文件管理
            # api_test_file_file_path_ls = {}
            # api_test_file_file_data = []
            # api_test_file_path = '{}/automatic_api/result/'.format(pro_path)
            # for api_test_file_level1 in [i for i in os.listdir(api_test_file_path) if self.filter_path(i)]:
            #     api_test_file_path_level1 = "{}{}/".format(api_test_file_path, api_test_file_level1)
            #     if '.' not in api_test_file_level1:
            #         api_test_file_model_dict = {'label': api_test_file_level1, 'path': api_test_file_path_level1[0: -1], 'children': []}
            #         index = 0  # 优化 加入下标 避免暴力查找
            #         for api_test_file_level2 in [i for i in os.listdir(api_test_file_path_level1) if self.filter_path(i)]:
            #             api_test_file_path_level2 = "{}{}/".format(api_test_file_path_level1, api_test_file_level2)
            #             if '.' not in api_test_file_level2:
            #                 api_test_file_model_dict['children'].append({'label': api_test_file_level2, 'path': api_test_file_path_level2[0: -1], 'children': []})
            #                 for api_test_file_level3 in [i for i in os.listdir(api_test_file_path_level2) if self.filter_path(i)]:
            #                     api_test_file_path_level3 = "{}{}/".format(api_test_file_path_level2, api_test_file_level3)
            #                     if '.' not in api_test_file_level3:
            #                         pass
            #                     else:
            #                         api_test_file_model_dict['children'][index]['children'].append({'label': api_test_file_level3, 'path': api_test_file_path_level3[0: -1]})
            #                         api_test_file_file_path_ls[api_test_file_level3] = api_test_file_path_level3[0: -1]
            #             index += 1
            #         api_test_file_file_data.append(api_test_file_model_dict)
            # redis_data_tree['api_test_file'] = api_test_file_file_data
            # redis_data_path['api_test_file'] = api_test_file_file_path_ls
            #
            #
            # # API自动化测试 测试报告管理存储
            # api_test_report_path = '{}/result/'.format(self.api_project_path)
            # api_test_report_file_path_ls = {}
            # api_test_report_dict_ls = []
            # index = 0  # 加入下标 避免暴力查找
            # for api_test_report_level1 in [i for i in os.listdir(api_test_report_path) if self.filter_path(i)]:
            #     report_time = datetime.date(int(api_test_report_level1[0: 4]), int(api_test_report_level1[4: 6]),
            #                                 int(api_test_report_level1[6: 8]))
            #     now_date = datetime.datetime.now().date()
            #     if now_date.__sub__(report_time).days > 30:  # 筛选超过30天的测试报告
            #         remove_ls.append(api_test_report_level1)
            #         continue
            #     api_test_report_path_level1 = api_test_report_path + api_test_report_level1
            #     for api_test_report_level2 in [i for i in os.listdir(api_test_report_path_level1) if self.filter_path(i)]:
            #         api_test_report_path_level2 = "{}/{}".format(api_test_report_path_level1, api_test_report_level2)
            #         api_test_report_file_path_ls[
            #             "{}_{}".format(api_test_report_level1, api_test_report_level2)] = api_test_report_path_level2
            #         api_test_report_dict_ls.append({
            #             'file_path': api_test_report_path_level2,
            #             'file_name': "{}_{}".format(api_test_report_level1, api_test_report_level2),
            #             'action_time': datetime.datetime(int(api_test_report_level1[0: 4]),
            #                                              int(api_test_report_level1[4: 6]),
            #                                              int(api_test_report_level1[6: 8]),
            #                                              int(api_test_report_level1[8: 10]),
            #                                              int(api_test_report_level1[10: 12]),
            #                                              int(api_test_report_level1[12: 14])),
            #             'spend_time': None,
            #             'tester': 'tester',
            #             'result': '',
            #         })
            #     index += 1
            # ApiTestReport.objects.all().delete()  # 清空表
            # for i in remove_ls:
            #     try:
            #         shutil.rmtree('{}{}'.format(api_test_report_path, i))
            #     except:
            #         pass
            #     # 删除本地超过30天的测试报告
            # test_report_serializers = ApiTestReportSerializers(data=api_test_report_dict_ls, many=True)  # 存储
            # test_report_serializers.is_valid(raise_exception=True)
            # test_report_serializers.save()
            # redis_data_path['api_test_report'] = api_test_report_file_path_ls

            # redis文件存储
            for key in zip(redis_data_tree.keys(), redis_data_path.keys()):
                redis_key = key[0]
                redis_conn.delete("{}_tree".format(redis_key))
                redis_conn.delete("{}_path".format(redis_key))
                redis_conn.set("{}_tree".format(redis_key), str(redis_data_tree[redis_key]))
                redis_conn.hmset("{}_path".format(redis_key), redis_data_path[redis_key])

            redis_conn.delete("{}_path".format('ui_test_report'))
            # redis_conn.delete("{}_path".format('api_test_report'))
            redis_conn.hmset("{}_path".format('ui_test_report'), redis_data_path['ui_test_report'])
            # redis_conn.hmset("{}_path".format('api_test_report'), redis_data_path['api_test_report'])

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
            try:
                return_data = eval(redis_conn.get("{}_tree".format(path_type)))
            except Exception as e:
                return_data = []
            if 'ui_case_ls' in path_type:
                return_data.append({'root_path': '{}/testCase/ui_testCase'.format(self.ui_project_path)})
            elif 'ui_test_file' in path_type:
                return_data.append({'root_path': '{}/testFile/case'.format(self.ui_project_path)})

        return JsonResponse(data=return_data, code="999999", msg="成功!")


class automated_testing_file_edit(APIView):
    # 自动化测试 通过ssh 修改/查询远程主机文件
    authentication_classes = (TokenAuthentication,)
    permission_classes = []
    path_type_LS = (
        'ui_common', 'ui_test_report', 'ui_test_file', 'ui_case_ls',
        'api_common', 'api_test_report', 'api_test_file', 'api_case_ls')  # 可查询的文件类型
    edit_path_type_LS = (
        'ui_common', 'ui_case_ls', 'api_common', 'api_case_ls', 'api_test_file', 'ui_test_file'
    )  # 可编辑的文件类型
    upload_path_type_ls = ('ui_test_file', 'ui_case_ls')  # 可上传的文件类型
    file_data_type_LS = ('str')

    def check_selenium_ide_format(self, file_path):
        # 检测上传的py文件 是否是 selenium_ide格式的
        with open(file_path, 'r', encoding='utf-8') as f:
            value = f.read()
        if "pytest" in value and "selenium" in value and "if __name__ == '__main__':" not in value and 'setup_method' in value and 'teardown_method' in value:
            return True
        else:
            return False

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

        # if not file_path:
        #     if 'api_test_report' != route_type:
        #         return JsonResponse(code="999981", msg="未找到文件, 请联系管理员!")

        if 'test_file' in route_type:
            file_content = parse_excel(file_path)
            if file_content == False:
                return JsonResponse(code="999981", msg="未找到文件, 请联系管理员!")
        # elif 'api_test_report' == route_type:
        #     pass
        # else:
        #     file_content = open(file_path, 'r', encoding='utf-8').read()

        res_data = {'file_name': file_name,
                    'file_data_type': file_data_type}
        if 'test_report' not in route_type:
            res_data['file_content'] = file_content

        if route_type == 'ui_test_report':
            res_data['report_src'] = '/Operation_maintenance/test_report?test_type=ui&file_name={}'.format(
                file_name)
        elif route_type == 'api_test_report':
            res_data['report_src'] = '/Operation_maintenance/test_report?test_type=api&file_name={}'.format(
                file_name)

        return JsonResponse(data=res_data, code="999999", msg="成功!")

    @swagger_auto_schema(
        operation_summary='API&UI 文件修改',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'file_name': openapi.Schema(type=openapi.TYPE_STRING, description='查询文件名称'),
                'route_type': openapi.Schema(type=openapi.TYPE_STRING, description='查询文件所属模块 {}'.format('/'.join(edit_path_type_LS))),
                'file_content': openapi.Schema(type=openapi.TYPE_STRING, description='需要写入的文件内容(全量)'),
            }))
    def put(self, request):
        """修改文件"""
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

        if 'test_file' in route_type:
            df = pd.DataFrame(file_content)
            df.to_excel(file_path, index=False)

        else:
            try:
                f = open(file_path, 'w', encoding='utf-8')
                f.write(file_content)
                f.close()
            except Exception as e:
                return JsonResponse(code="999981", msg="未找到文件, 请联系管理员!")

        return JsonResponse(code="999999", msg="成功!")

    @swagger_auto_schema(
        operation_summary='UI 文件上传',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'route_type': openapi.Schema(type=openapi.TYPE_STRING, description='上传文件所属模块 {}'.format('/'.join(upload_path_type_ls))),
                'file_path': openapi.Schema(type=openapi.TYPE_STRING, description='文件路径 当前文件的上层路径 不带文件名'),
                'binary': openapi.Schema(type=openapi.TYPE_OBJECT, description='文件对象'),
            }))
    def post(self, request):
        """文件上传 暂时支持UI测试用例(修改代码为remote模式 接收命令行参数)/UI测试文件 不需要json序列化"""
        file_obj = request.FILES.get('file')
        file_path = request.POST.get('file_path')
        route_type = request.POST.get('route_type')
        try:
            file_content = file_obj.read()
        except AttributeError as e:
            return JsonResponse(code="999998", msg="上传失败 请填写表头!")

        file_name = file_obj.name
        redis_conn = redis.Redis(connection_pool=redis_pool)  # redis链接
        if redis_conn.hget('ui_case_ls_path', file_name):
            return JsonResponse(code="999998", msg="文件重名!")
        if "case_ls" in route_type:
            if '.py' not in file_name or not re.compile(REGEX_PY_MODEL).search(file_name):
                return JsonResponse(code="999998", msg="文件名非法!")
        elif "test_file" in route_type or re.compile(REGEX_FOLD).search(file_name):
            if 'xlsx' not in file_name:
                return JsonResponse(code="999998", msg="文件名非法!")

        file_path = os.path.join(file_path, file_name)
        if not os.path.isfile(file_path):
            f = open(file_path, 'wb+')
            f.write(file_content)
            f.close()
            if route_type == 'ui_case_ls':
                if self.check_selenium_ide_format(file_path):  # 判断为selenium-ide格式 进行代码修改
                    format_ui_case(file_path)
            return JsonResponse(code="999999", msg="文件上传成功!")
        else:
            return JsonResponse(code="999998", msg="已存在{}文件!".format(file_name))


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
                'swagger_url': openapi.Schema(type=openapi.TYPE_STRING, description='swagger地址'),
            }))

    def post(self, request):
        """链接API自动化测试执行机 远程执行swaggger数据解析 生成测试用例"""
        data = JSONParser().parse(request)
        SwaggerJson = AnalysisSwaggerJson(data.get('swagger_url'))
        data = SwaggerJson.req_swagger()

        return JsonResponse(data=data, code='999999', msg='success')


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
        # redis_conn = redis.Redis(connection_pool=redis_pool)  # redis链接
        try:
            test_report_obj = eval("{}TestReport.objects.get(file_name=file_name)".format(test_type.capitalize()))
            return HttpResponse(content=test_report_obj.text_content, )
        except:
            return JsonResponse(code="999981", msg="未找到文件, 请联系管理员!")
        # file_path = redis_conn.hget("{}_test_report_path".format(test_type), file_name)  # 文件路径
        # if not file_path:
        #     return JsonResponse(code="999981", msg="未找到文件, 请联系管理员!")
        #
        # return HttpResponse(content=open(file_path).read(), )  # 使用绝对路径返回html文件方式







