# -*- coding: utf-8 -*-
import json

from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q
from django.forms import model_to_dict
from drf_yasg2.utils import swagger_auto_schema
from drf_yasg2 import openapi
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView

from account_system.tools import get_real_name
from system_settings.models import DataDictionary, Dataexplain
from system_settings.tools import error_response, success_response
from user_interface_test_code.models import CommonParams, TestAppModel, TestCase, UiFunctions, TestCaseData
from user_interface_test_code.serializers import UiTestParamsSerializerQuery, UiTestParamsSerializerAdd, \
    TestModelSerializerQuery, TestModelSerializerAdd, TestModelSelectSerializerQuery, TestCaseQuerySerializers, \
    TestCaseAddSerializer, UiFunctionsSerializerQuery, TestCaseDataSerializerQuery, TestCaseDataSerializerAdd
from zy_api_testing.tools import DelException, api_list_query


class TestCaseDataQueryView(APIView):
    authentication_classes = ()
    permission_classes = []

    @swagger_auto_schema(
        operation_summary='测试步骤 (多条件筛选)',
        manual_parameters=[
            openapi.Parameter(name='AUTHORIZATION', in_=openapi.IN_HEADER, description='登录验证', type=openapi.TYPE_STRING),
            openapi.Parameter(name='page', in_=openapi.IN_QUERY, description='页码', type=openapi.TYPE_STRING),
            openapi.Parameter(name='page_size', in_=openapi.IN_QUERY, description='数量', type=openapi.TYPE_STRING),
            openapi.Parameter(name='test_case_id', in_=openapi.IN_QUERY, description='测试用例id', type=openapi.TYPE_STRING),
        ])
    def get(self, request):
        try:
            data = request.GET
            page = int(data.get('page', 1))
            page_size = int(data.get('page_size', 15))
            if not data.get('test_case_id'):
                return error_response('请传入测试用例id')
            total, obm = api_list_query(data, page, page_size, TestCaseData, 'sort', ['test_case_id'], has_parent=True)
            try:
                test_case_data_serialize = TestCaseDataSerializerQuery(obm, many=True)
                return_data = test_case_data_serialize.data
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


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass

    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass

    return False

class TestCaseDataAdd(APIView):
    authentication_classes = ()
    permission_classes = []


    @swagger_auto_schema(
        operation_summary='测试用例 步骤数据 新增',
        manual_parameters=[
            openapi.Parameter(name='AUTHORIZATION', in_=openapi.IN_HEADER, description='登录验证',type=openapi.TYPE_STRING), ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'test_case_id': openapi.Schema(type=openapi.TYPE_STRING, description='测试用例id'),
                'all_data_list': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'test_case_id': openapi.Schema(type=openapi.TYPE_STRING, description='测试用例id'),
                        'step_desc': openapi.Schema(type=openapi.TYPE_STRING, description='步骤描述'),
                        'field_desc': openapi.Schema(type=openapi.TYPE_STRING, description='字段名'),
                        'location_func': openapi.Schema(type=openapi.TYPE_STRING, description='定位方法名'),
                        'operate_func': openapi.Schema(type=openapi.TYPE_STRING, description='执行方法名'),
                        'action_func': openapi.Schema(type=openapi.TYPE_ARRAY, description='步骤方法列表', items=openapi.Items(type=openapi.TYPE_STRING),),
                        'location_value': openapi.Schema(type=openapi.TYPE_STRING, description='定位参数'),
                        'func_param': openapi.Schema(type=openapi.TYPE_STRING, description='执行方法传递参数'),
                        'ele_attribute': openapi.Schema(type=openapi.TYPE_STRING, description='断言 元素的属性'),
                        'assert_value': openapi.Schema(type=openapi.TYPE_STRING, description='断言 元素的值'),
                        'extension': openapi.Schema(type=openapi.TYPE_STRING, description='预留字段'),
                        'sort': openapi.Schema(type=openapi.TYPE_STRING, description='步骤排序值'),
                        'is_need_value': openapi.Schema(type=openapi.TYPE_NUMBER, description='是否需要 方法传递参数 传递参数 0/1'),
                        'is_need_button': openapi.Schema(type=openapi.TYPE_NUMBER, description='是否需要 定位 0/1'),
                        'is_need_assert': openapi.Schema(type=openapi.TYPE_NUMBER, description='是否需要 断言 0/1'),
                        'is_need_mysql': openapi.Schema(type=openapi.TYPE_NUMBER, description='是否需要 mysql数据库 0/1'),
                        'func_common_param_id': openapi.Schema(type=openapi.TYPE_NUMBER, description='公共参数id'),
                        'mysql_info_id': openapi.Schema(type=openapi.TYPE_NUMBER, description='mysql 信息id'),
                    }
                ), description='测试步骤数据 '),
            }
        )
    )
    def post(self, request):
        """测试步骤 增加"""
        with transaction.atomic():
            try:
                data = JSONParser().parse(request)
                all_data_list = data.get('all_data_list')
                test_case_id = data.get("test_case_id")
                # 先删除当前测试用例下 所有已存在步骤
                flag = is_number(test_case_id)
                if not flag or not TestCase.objects.filter(id=test_case_id):
                    return error_response('不存在的测试用例id {}'.format(test_case_id))
                TestCaseData.objects.filter(test_case_id=test_case_id).delete()
                for one_data in all_data_list:
                    try:
                        one_data['update_user'] = get_real_name(request)
                    except:
                        pass
                    one_data['action_func'] = json.dumps(one_data['action_func'])
                    test_case_data_serializer = TestCaseDataSerializerAdd(data=one_data)
                    if test_case_data_serializer.is_valid():
                        test_case_data_serializer.save()
                    else:
                        raise Exception('add_failed')
                return success_response(msg='成功')
            except Exception as e:
                if str(e) == 'add_failed':
                    return error_response(msg=test_case_data_serializer.errors)
                return error_response('失败！！！')

