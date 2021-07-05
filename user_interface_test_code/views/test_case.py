# -*- coding: utf-8 -*-
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q
from django.forms import model_to_dict
from drf_yasg2.utils import swagger_auto_schema
from drf_yasg2 import openapi
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView

from account_system.tools import get_real_name
from common.tools import check_ip
from system_settings.models import DataDictionary, Dataexplain
from system_settings.tools import error_response, success_response
from user_interface_test_code.models import CommonParams, TestAppModel, TestCase, UiFunctions, TestCaseData, UiTestScene, \
    UiSceneTestCaseIndex
from user_interface_test_code.serializers import UiTestParamsSerializerQuery, UiTestParamsSerializerAdd, \
    TestModelSerializerQuery, TestModelSerializerAdd, TestModelSelectSerializerQuery, TestCaseQuerySerializers, \
    TestCaseAddSerializer, UiFunctionsSerializerQuery, TestCaseDataSerializerQuery
from user_interface_test_code.tools import get_one_test_case_data
from zy_api_testing.tools import DelException, api_list_query
from automatic_ui.ui_script_execution import ui_script_execution

class TestCaseQueryView(APIView):
    authentication_classes = ()
    permission_classes = []

    @swagger_auto_schema(
        operation_summary='测试用例 (多条件筛选)',
        manual_parameters=[
            openapi.Parameter(name='AUTHORIZATION', in_=openapi.IN_HEADER, description='登录验证',type=openapi.TYPE_STRING),
            openapi.Parameter(name='page', in_=openapi.IN_QUERY, description='页码', type=openapi.TYPE_STRING),
            openapi.Parameter(name='page_size', in_=openapi.IN_QUERY, description='数量', type=openapi.TYPE_STRING),
            openapi.Parameter(name='test_app_model_id', in_=openapi.IN_QUERY, description='界面id', type=openapi.TYPE_STRING),
            openapi.Parameter(name='case_number', in_=openapi.IN_QUERY, description='用例编号', type=openapi.TYPE_STRING),
            openapi.Parameter(name='case_name', in_=openapi.IN_QUERY, description='用例名称', type=openapi.TYPE_STRING)
        ])
    def get(self, request):
        try:
            data = request.GET
            page = int(data.get('page', 1))
            page_size = int(data.get('page_size', 15))
            total, obm = api_list_query(data, page, page_size, TestCase, 'id', ['test_app_model_id', 'case_number', 'case_name'], accurate_ls=['test_app_model_id'])
            try:
                test_case_serialize = TestCaseQuerySerializers(obm, many=True)
                return_data = test_case_serialize.data
                response = {
                    "data": return_data,
                    "page": page,
                    "total": total
                }
            except Exception as _e:
                response = {}
            return success_response(data=response, msg='查询成功！')
        except Exception as e:
            return error_response('失败!')


class TestCaseAdd(APIView):
    authentication_classes = ()
    permission_classes = []


    @swagger_auto_schema(
        operation_summary='测试用例 新增',
        manual_parameters=[
            openapi.Parameter(name='AUTHORIZATION', in_=openapi.IN_HEADER, description='登录验证',type=openapi.TYPE_STRING),],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'test_app_model_id': openapi.Schema(type=openapi.TYPE_STRING, description='界面id'),
                'case_number': openapi.Schema(type=openapi.TYPE_STRING, description='用例编号'),
                'case_name': openapi.Schema(type=openapi.TYPE_STRING, description='用例名称'),
                'case_type': openapi.Schema(type=openapi.TYPE_STRING, description='用例类型'),
                'failed_up': openapi.Schema(type=openapi.TYPE_STRING, description='后续执行步骤0/1  中断/继续'),
                'is_common_function': openapi.Schema(type=openapi.TYPE_NUMBER, description='是否是公共用例 0/1'),
                'remark': openapi.Schema(type=openapi.TYPE_STRING, description='备注')
            }
        )
    )
    def post(self, request):
        """应用模块 增加"""
        try:
            data = JSONParser().parse(request)
            data['update_user'] = get_real_name(request)

            test_case_serializer = TestCaseAddSerializer(data=data)
            if test_case_serializer.is_valid():
                data = test_case_serializer.save()
                return success_response(data=model_to_dict(data), msg='新增测试用例信息成功！')
            else:
                return error_response(msg=test_case_serializer.errors)
        except Exception as e:
            return error_response('失败！！！')

    @swagger_auto_schema(
        operation_summary='测试用例 修改',
        manual_parameters=[
            openapi.Parameter(name='AUTHORIZATION', in_=openapi.IN_HEADER, description='登录验证',type=openapi.TYPE_STRING),],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='id'),
                'test_app_model_id': openapi.Schema(type=openapi.TYPE_STRING, description='界面id'),
                'case_number': openapi.Schema(type=openapi.TYPE_STRING, description='用例编号'),
                'case_name': openapi.Schema(type=openapi.TYPE_STRING, description='用例名称'),
                'case_type': openapi.Schema(type=openapi.TYPE_STRING, description='用例类型'),
                'failed_up': openapi.Schema(type=openapi.TYPE_STRING, description='后续执行步骤0/1  中断/继续'),
                'is_common_function': openapi.Schema(type=openapi.TYPE_NUMBER, description='是否是公共用例 0/1'),
                'remark': openapi.Schema(type=openapi.TYPE_STRING, description='备注')
            }
        )
    )
    def put(self, request):
        """测试用例 修改"""
        try:
            data = JSONParser().parse(request)
            try:
                data['update_user'] = get_real_name(request)
            except:
                pass
            id = data.get('id')
            test_case = TestCase.objects.filter(id=id)
            if not test_case:
                return error_response('id错误')
            test_case_serializer = TestCaseAddSerializer(instance=test_case.first(), data=data)
            if test_case_serializer.is_valid():
                data = test_case_serializer.save()
                return success_response(data=model_to_dict(data), msg='修改测试用例信息成功！')
            else:
                return error_response(msg=test_case_serializer.errors)
        except Exception as e:
            return error_response('失败！！！')

    @swagger_auto_schema(
        operation_summary='测试用例 单删群删',
        manual_parameters=[openapi.Parameter(name='AUTHORIZATION', in_=openapi.IN_HEADER, description='登录验证', type=openapi.TYPE_STRING),],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'ids': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_STRING),
                                      description='需要删除的测试用例id列表 ')
            }))
    def delete(self, request):
        """测试用例 单删群删"""
        data = JSONParser().parse(request)
        test_case_ids = set()
        for test_scene_obj in UiSceneTestCaseIndex.objects.all():
            test_case_ids.add(test_scene_obj.test_case_id)
        try:
            with transaction.atomic():
                delete_ids = data['ids']
                for id in delete_ids:
                    if int(id) not in test_case_ids:
                        test_case = TestCase.objects.filter(id=id).first()
                        if test_case:
                            TestCaseData.objects.filter(test_case_id=int(id)).delete()
                            test_case.delete()
                        else:
                            return error_response(msg="数据错误!")
                    else:
                        return error_response(msg="此用例已被场景关联 无法删除!")
        except Exception as e:
            return error_response(msg="失败!")
        return success_response(data='', msg="成功!")

    @swagger_auto_schema(
        operation_summary='测试步骤方法, 下拉框接口',
        manual_parameters=[
        openapi.Parameter(name='AUTHORIZATION', in_=openapi.IN_HEADER, description='登录验证', type=openapi.TYPE_STRING),
        openapi.Parameter(name='super_function', in_=openapi.IN_QUERY, description='上级接口名称', type=openapi.TYPE_STRING),],
        )
    def get(self, request):
        try:
            super_function = request.GET.get('super_function')
            if super_function:
                ui_func_objs = UiFunctions.objects.filter(super_function=super_function)
            else:
                ui_func_objs = UiFunctions.objects.filter(function_level=0)
            return_data = UiFunctionsSerializerQuery(ui_func_objs, many=True).data
            if super_function == 'assert_function':
                # 选择断言方式时 增加默认字段
                for i in return_data:
                    i['is_need_assert'] = 1
            elif super_function == 'mysql_function':
                # 选择mysql执行时  增加默认字段
                for i in return_data:
                    i['is_need_mysql'] = 1
            return success_response(data=return_data, msg='成功')
        except Exception as e:
            return error_response('失败')


class ExecuteCase(APIView):
    authentication_classes = ()
    permission_classes = []

    @swagger_auto_schema(
        operation_summary='测试用例 执行',
        manual_parameters=[openapi.Parameter(name='AUTHORIZATION', in_=openapi.IN_HEADER, description='登录验证', type=openapi.TYPE_STRING), ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'test_case_ids': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_STRING), description='测试用例id'),
                'remote_ip': openapi.Schema(type=openapi.TYPE_STRING, description='执行机ip'),
                'environment_ip': openapi.Schema(type=openapi.TYPE_STRING, description='用例名称'),
                'case_type': openapi.Schema(type=openapi.TYPE_STRING, description='用例类型/ui'),
                'common_case_ids': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_STRING),
                                      description='公共用例id列表 ')
            }))
    def post(self, request):
        # try:
        data = JSONParser().parse(request)
        test_case_id = data.get('test_case_ids')[0]
        remote_ip = data.get('remote_ip')
        common_case_ids = data.get('common_case_ids', [])
        # ping ip
        if not check_ip(remote_ip):
            return error_response('该执行机无法连接')
        environment_ip = data.get('environment_ip')
        if not test_case_id or not remote_ip or not environment_ip:
            return error_response("参数未传递！！！")
        if not TestCase.objects.filter(id=test_case_id):
            return error_response("测试用例不存在！！！")
        if not TestCaseData.objects.filter(test_case_id=test_case_id):
            return error_response("该测试用例下不存在执行步骤！！！")
        explicit_wait_timeout = CommonParams.objects.get(id=1).param_value
        explicit_wait_poll_time = CommonParams.objects.get(id=2).param_value
        implicitly_wait_timeout = CommonParams.objects.get(id=3).param_value
        common_case_ids.append(test_case_id)
        test_case_ids = common_case_ids
        # 获取执行数据
        # try:
        execution_test_case_data = get_one_test_case_data(test_case_ids, environment_ip, explicit_wait_timeout, explicit_wait_poll_time, implicitly_wait_timeout, remote_ip)
        # except Exception as e:
        #     return error_response('生成测试数据失败！！！')
        script_execution = ui_script_execution()
        result = script_execution.execution_ui_case(execution_test_case_data)
        return success_response(data=result, msg="成功")


class CommonCaseLs(APIView):
    authentication_classes = ()
    permission_classes = []

    @swagger_auto_schema(
        operation_summary='公共方法 选择',
        manual_parameters=[openapi.Parameter(name='AUTHORIZATION', in_=openapi.IN_HEADER, description='登录验证', type=openapi.TYPE_STRING),
                           openapi.Parameter(name='case_name', in_=openapi.IN_QUERY, description='用例名称', type=openapi.TYPE_STRING)],)

    def get(self, request):
        try:
            case_name = request.GET.get('case_name', '')
            common_functions = TestCase.objects.filter(is_common_function=1, case_name__contains=case_name)
            data = [{"id": i.id, "case_name": i.case_name} for i in common_functions]

        except Exception as _:
            data = []
        return success_response(data=data, msg="成功")
