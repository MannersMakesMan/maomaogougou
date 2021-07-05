# -*- coding: utf-8 -*-
import re

from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q
from django.forms import model_to_dict
from drf_yasg2.utils import swagger_auto_schema
from drf_yasg2 import openapi
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView

from automatic_ui.ui_functions_manage import save_functions, save_params
from account_system.tools import get_real_name
from system_settings.tools import error_response, success_response
from user_interface_test_code.models import CommonParams, TestCaseData
from user_interface_test_code.serializers import UiTestParamsSerializerQuery, UiTestParamsSerializerAdd, \
    UiTestParamsDropDownBoxSerializerQuery
from zy_api_testing.tools import DelException, api_list_query

# 更新ui function数据
save_functions()
# 更新公共参数默认参数
save_params()

CANNOT_DELETE_ID_LIST = ['1', '2', '3', 1, 2, 3]


class CommonParamQueryView(APIView):
    authentication_classes = ()
    permission_classes = []

    @swagger_auto_schema(
        operation_summary='ui公共参数 (多条件筛选)',
        manual_parameters=[
            openapi.Parameter(name='AUTHORIZATION', in_=openapi.IN_HEADER, description
            ='登录验证',type=openapi.TYPE_STRING),
            openapi.Parameter(name='page', in_=openapi.IN_QUERY, description='页码', type=openapi.TYPE_STRING),
            openapi.Parameter(name='page_size', in_=openapi.IN_QUERY, description='数量', type=openapi.TYPE_STRING),
            openapi.Parameter(name='entry_name_id', in_=openapi.IN_QUERY, description='项目id', type=openapi.TYPE_STRING),
            openapi.Parameter(name='param_desc', in_=openapi.IN_QUERY, description='参数名称', type=openapi.TYPE_STRING)
        ])
    def get(self, request):
        try:
            data = request.GET
            page = int(data.get('page', 1))
            page_size = int(data.get('page_size', 15))
            total, obm = api_list_query(data, page, page_size, CommonParams, 'id', ['entry_name_id', 'param_desc'], accurate_ls=['entry_name_id'])
            try:
                api_manage_serialize = UiTestParamsSerializerQuery(obm, many=True)
                # api_manage_serialize = ApiManageSerializerConfQuery(obm, many=True)
                return_data = api_manage_serialize.data
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


class CommonParamDropDownBox(APIView):
    authentication_classes = ()
    permission_classes = []

    @swagger_auto_schema(
        operation_summary='ui公共参数 下拉框查询',
        manual_parameters=[
            openapi.Parameter(name='AUTHORIZATION', in_=openapi.IN_HEADER, description
            ='登录验证', type=openapi.TYPE_STRING),
            openapi.Parameter(name='param_desc', in_=openapi.IN_QUERY, description='参数名', type=openapi.TYPE_STRING),
        ])
    def get(self, request):
        try:
            data = request.GET
            param_desc = data.get('param_desc', '')
            if param_desc:
                # common_param_objs = CommonParams.objects.all()
                # api_manage_serialize = UiTestParamsDropDownBoxSerializerQuery(common_param_objs, many=True)
                # return_data = api_manage_serialize.data
                # # return_data = []
                # for i in return_data:
                #     a = '.*?'+param_desc+'.*?'
                #     if re.search('.*?'+param_desc+'.*?', i['param_desc']):
                #         return_data.append(i)

                obm = CommonParams.objects.filter(param_desc__contains=param_desc)
                try:
                    api_manage_serialize = UiTestParamsDropDownBoxSerializerQuery(obm, many=True)
                    return_data = api_manage_serialize.data

                except Exception as _:
                    return_data = []
            else:
                return_data = []
            response = {
                "data": return_data,
            }
            return success_response(data=response, msg='查询成功！')
        except Exception as _:
            return error_response('失败!')




class CommonParamsAdd(APIView):
    authentication_classes = ()
    permission_classes = []

    @swagger_auto_schema(
        operation_summary='ui公共参数 单查',
        manual_parameters=[
        openapi.Parameter(name='AUTHORIZATION', in_=openapi.IN_HEADER, description='登录验证',type=openapi.TYPE_STRING),
        openapi.Parameter(name='param', in_=openapi.IN_QUERY, description='公共参数名称', type=openapi.TYPE_STRING),],
    )
    def get(self, request):
        """公共参数信息 单查"""
        data = request.GET
        param_name = data.get("param", None)
        if param_name:
            param_objs = CommonParams.objects.filter(param_desc=param_name)
            if param_objs:
                return_data = {
                    "id": param_objs[0].id,
                    "param_value": param_objs[0].param_value
                }
                return success_response(data=return_data, msg="成功!")
            else:
                return success_response("无参数")
        return success_response("无参数")



    @swagger_auto_schema(
        operation_summary='ui公共参数 新增',
        manual_parameters=[
            openapi.Parameter(name='AUTHORIZATION', in_=openapi.IN_HEADER, description='登录验证',type=openapi.TYPE_STRING),],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'entry_name_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='项目id'),
                'param_desc': openapi.Schema(type=openapi.TYPE_STRING, description='参数名'),
                'param_value': openapi.Schema(type=openapi.TYPE_STRING, description='参数值'),
                'remark': openapi.Schema(type=openapi.TYPE_STRING, description='备注')
            }
        )
    )
    def post(self, request):
        """公共参数信息 新增"""
        try:
            data = JSONParser().parse(request)
            data['update_user'] = get_real_name(request)
            common_params_serializer = UiTestParamsSerializerAdd(data=data)
            if common_params_serializer.is_valid():
                data = common_params_serializer.save()
                return success_response(data=model_to_dict(data), msg='新增公共参数信息成功！')
            else:
                return error_response(msg=common_params_serializer.errors)
        except Exception as e:
            return error_response('失败！！！')

    @swagger_auto_schema(
        operation_summary='ui公共参数 修改',
        manual_parameters=[
            openapi.Parameter(name='AUTHORIZATION', in_=openapi.IN_HEADER, description='登录验证',type=openapi.TYPE_STRING),],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='id'),
                'entry_name_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='项目id'),
                'param_desc': openapi.Schema(type=openapi.TYPE_STRING, description='参数名'),
                'param_value': openapi.Schema(type=openapi.TYPE_STRING, description='参数值'),
                'remark': openapi.Schema(type=openapi.TYPE_STRING, description='备注')
            }
        )
    )
    def put(self, request):
        """公共参数信息 修改"""
        try:
            data = JSONParser().parse(request)
            data['update_user'] = get_real_name(request)
            id = data.get('id')
            commom_objs = CommonParams.objects.filter(id=id)
            if not commom_objs:
                return error_response('id错误')
            common_params_serializer = UiTestParamsSerializerAdd(instance=commom_objs.first(), data=data)
            if common_params_serializer.is_valid():
                data = common_params_serializer.save()
                return success_response(data=model_to_dict(data), msg='修改公共参数信息成功！')
            else:
                return error_response(msg=common_params_serializer.errors)
        except Exception as _:
            return error_response('失败！！！')

    @swagger_auto_schema(
        operation_summary='公共参数 单删群删',
        manual_parameters=[openapi.Parameter(name='AUTHORIZATION', in_=openapi.IN_HEADER, description='登录验证', type=openapi.TYPE_STRING),],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'ids': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_STRING),
                                      description='需要删除的公共参数id列表 ')
            }))
    def delete(self, request):
        """公共参数 单删群删"""
        try:
            with transaction.atomic():
                data = JSONParser().parse(request)
                delete_ids = data['ids']
                for id in delete_ids:
                    if id in CANNOT_DELETE_ID_LIST:
                        raise Exception('cannot_delete')
                    steps_obj = TestCaseData.objects.filter(func_common_param_id=int(id))
                    if not steps_obj:
                        common_obj = CommonParams.objects.filter(id=id).first()
                        if common_obj:
                             common_obj.delete()
                        else:
                            return error_response(msg="无此数额据!")
                    else:
                        raise Exception('Be associated')
        except Exception as e:
            if str(e) == 'cannot_delete':
                return error_response('初始公共参数无法删除')
            elif str(e) == 'Be associated':
                return error_response('此参数被测试用例关联 请取消关联')
            return error_response(msg="失败!")
        return success_response(data='', msg="成功!")
