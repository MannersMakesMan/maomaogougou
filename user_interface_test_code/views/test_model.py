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
from system_settings.models import DataDictionary, Dataexplain
from system_settings.tools import error_response, success_response
from user_interface_test_code.models import CommonParams, TestAppModel
from user_interface_test_code.serializers import UiTestParamsSerializerQuery, UiTestParamsSerializerAdd, \
    TestModelSerializerQuery, TestModelSerializerAdd, TestModelSelectSerializerQuery
from zy_api_testing.tools import DelException, api_list_query


class TestModelQueryView(APIView):
    authentication_classes = ()
    permission_classes = []

    @swagger_auto_schema(
        operation_summary='应用模块 (多条件筛选)',
        manual_parameters=[
            openapi.Parameter(name='AUTHORIZATION', in_=openapi.IN_HEADER, description='登录验证',type=openapi.TYPE_STRING),
            openapi.Parameter(name='page', in_=openapi.IN_QUERY, description='页码', type=openapi.TYPE_STRING),
            openapi.Parameter(name='page_size', in_=openapi.IN_QUERY, description='数量', type=openapi.TYPE_STRING),
            openapi.Parameter(name='entry_name_id', in_=openapi.IN_QUERY, description='项目id', type=openapi.TYPE_STRING),
            openapi.Parameter(name='fun_name', in_=openapi.IN_QUERY, description='功能名称', type=openapi.TYPE_STRING),
            openapi.Parameter(name='interface_name', in_=openapi.IN_QUERY, description='界面名称', type=openapi.TYPE_STRING)
        ])
    def get(self, request):
        try:
            data = request.GET
            page = int(data.get('page', 1))
            page_size = int(data.get('page_size', 15))
            total, obm = api_list_query(data, page, page_size, TestAppModel, 'id', ['entry_name_id', 'fun_name', 'interface_name'], accurate_ls=['entry_name_id'])
            try:
                test_model_serialize = TestModelSerializerQuery(obm, many=True)
                # api_manage_serialize = ApiManageSerializerConfQuery(obm, many=True)
                return_data = test_model_serialize.data
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


class TestModelAdd(APIView):
    authentication_classes = ()
    permission_classes = []


    @swagger_auto_schema(
        operation_summary='应用模块 新增',
        manual_parameters=[
            openapi.Parameter(name='AUTHORIZATION', in_=openapi.IN_HEADER, description='登录验证',type=openapi.TYPE_STRING),],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'entry_name_id': openapi.Schema(type=openapi.TYPE_STRING, description='项目id'),
                'fun_name': openapi.Schema(type=openapi.TYPE_STRING, description='功能名'),
                'model_name': openapi.Schema(type=openapi.TYPE_STRING, description='模块名'),
                'interface_name': openapi.Schema(type=openapi.TYPE_STRING, description='界面名'),
                 'dev_user': openapi.Schema(type=openapi.TYPE_STRING, description='开发负责人id'),
                'test_user': openapi.Schema(type=openapi.TYPE_STRING, description='测试负责人id'),
                'remark': openapi.Schema(type=openapi.TYPE_STRING, description='备注')
            }
        )
    )
    def post(self, request):
        """应用模块 增加"""
        try:
            data = JSONParser().parse(request)
            try:
                data['update_user'] = get_real_name(request)
            except:
                pass
            test_model_serializer = TestModelSerializerAdd(data=data)
            if test_model_serializer.is_valid():
                data = test_model_serializer.save()
                return success_response(data=model_to_dict(data), msg='新增应用模块信息成功！')
            else:
                return error_response(msg=test_model_serializer.errors)
        except Exception as e:
            return error_response('失败！！！')

    @swagger_auto_schema(
        operation_summary='应用模块 修改',
        manual_parameters=[
            openapi.Parameter(name='AUTHORIZATION', in_=openapi.IN_HEADER, description='登录验证',type=openapi.TYPE_STRING),],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='id'),
                'entry_name_id': openapi.Schema(type=openapi.TYPE_STRING, description='项目id'),
                'fun_name': openapi.Schema(type=openapi.TYPE_STRING, description='功能名'),
                'model_name': openapi.Schema(type=openapi.TYPE_STRING, description='模块名'),
                'interface_name': openapi.Schema(type=openapi.TYPE_STRING, description='界面名'),
                 'dev_user': openapi.Schema(type=openapi.TYPE_STRING, description='开发负责人id'),
                'test_user': openapi.Schema(type=openapi.TYPE_STRING, description='测试负责人id'),
                'remark': openapi.Schema(type=openapi.TYPE_STRING, description='备注')
            }
        )
    )
    def put(self, request):
        """应用模块 修改"""
        try:
            data = JSONParser().parse(request)
            try:
                data['update_user'] = get_real_name(request)
            except:
                pass
            id = data.get('id')
            test_model = TestAppModel.objects.filter(id=id)
            if not test_model:
                return error_response('id错误')
            test_model_serializer = TestModelSerializerAdd(instance=test_model.first(), data=data)
            if test_model_serializer.is_valid():
                data = test_model_serializer.save()
                return success_response(data=model_to_dict(data), msg='修改应用模块信息成功！')
            else:
                return error_response(msg=test_model_serializer.errors)
        except Exception as e:
            return error_response('失败！！！')

    @swagger_auto_schema(
        operation_summary='应用模块 单删群删',
        manual_parameters=[openapi.Parameter(name='AUTHORIZATION', in_=openapi.IN_HEADER, description='登录验证', type=openapi.TYPE_STRING),],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'ids': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_STRING),
                                      description='需要删除的应用模块id列表 ')
            }))
    def delete(self, request):
        """应用模块 单删群删"""
        try:
            with transaction.atomic():
                data = JSONParser().parse(request)
                delete_ids = data['ids']
                for id in delete_ids:
                    test_model = TestAppModel.objects.filter(id=id).first()
                    if test_model:
                         test_model.delete()
                    else:
                        return error_response(msg="数据错误!")
        except Exception as e:
            return error_response(msg="失败!")
        return success_response(data='', msg="成功!")

    @swagger_auto_schema(
        operation_summary='应用模块/界面下拉, 用例类型下拉框接口',
        manual_parameters=[openapi.Parameter(name='AUTHORIZATION', in_=openapi.IN_HEADER, description='登录验证',type=openapi.TYPE_STRING), ],)
    def get(self, request):
        try:
            test_model_objs = TestAppModel.objects.all()
            return_data = TestModelSelectSerializerQuery(test_model_objs, many=True).data
            data_id = Dataexplain.objects.get(dictionary_code='A0000002').id
            case_type_list = [i.get('dictionary_item1') for i in list(DataDictionary.objects.filter(Dataexplain_id=data_id).values('dictionary_item1'))]
            response = {
                'test_models': return_data,
                'case_type_list': case_type_list
            }
            return success_response(data=response, msg='成功')
        except Exception as e:
            return error_response('失败')
