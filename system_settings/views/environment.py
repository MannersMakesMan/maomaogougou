# -*- coding: utf-8 -*-
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q
from drf_yasg2.utils import swagger_auto_schema
from drf_yasg2 import openapi
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView

from automated_testing.common.api_response import JsonResponse
from system_settings.models import Environment, Project, PerformMachine
from system_settings.serializers import EnvironmentSerializerAdd, EnvironmentSerializerQuery, \
    PerformMachineSerializerQuery
from system_settings.tools import error_response, success_response


class EnvironmentAddView(APIView):
    authentication_classes = ()
    permission_classes = []

    @swagger_auto_schema(
        operation_summary='根据测试环境，查找执行机',
        manual_parameters=[
            openapi.Parameter(name='environment_id', in_=openapi.IN_QUERY, description='环境id',
                              type=openapi.TYPE_STRING),
        ])
    def get(self, request):
        try:
            environment_id = request.GET.get('environment_id')
            if not environment_id:
                return error_response('失败!')
            entry_id_list = [i['entry_name'] for i in list(Environment.objects.filter(id=environment_id).values('entry_name'))]
            perform_objs = PerformMachine.objects.filter(entry_name__in=entry_id_list)
            perform_serialize = PerformMachineSerializerQuery(perform_objs, many=True)
            return_data = perform_serialize.data
            return success_response(data=return_data, msg='查询成功！')
        except Exception as e:
            return error_response('失败!')

    @swagger_auto_schema(
        operation_summary='测试环境信息 新增',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'environmental_name': openapi.Schema(type=openapi.TYPE_STRING, description='环境名称'),
                'entry_name': openapi.Schema(type=openapi.TYPE_INTEGER, description='项目id'),
                'Test_type': openapi.Schema(type=openapi.TYPE_INTEGER, description="测试类型-- 0: 'UI自动化测试'),1: 'API自动化测试"),
                'Testing_phase': openapi.Schema(type=openapi.TYPE_INTEGER, description="(0:UT测试,1:SIT测试,2:UAT测试,3:生产验收"),
                'Test_address': openapi.Schema(type=openapi.TYPE_STRING, description='测试地址'),
                'Test_account': openapi.Schema(type=openapi.TYPE_STRING, description='测试账号'),
                'Test_password': openapi.Schema(type=openapi.TYPE_STRING, description='测试密码'),
                'remark': openapi.Schema(type=openapi.TYPE_STRING, description='备注')
            }
        )
    )
    def post(self, request):
        """测试环境 增加"""
        data = JSONParser().parse(request)
        environ_serializer = EnvironmentSerializerAdd(data=data)
        if environ_serializer.is_valid():
            environ_serializer.save()
            return success_response(data='', msg='新增环境信息成功！')
        else:
            return error_response(msg=environ_serializer.errors)


class EnvironmentView(APIView):
    authentication_classes = ()
    permission_classes = []

    @swagger_auto_schema(
        operation_summary='环境信息 单个查询'
    )
    def get(self, request, pk):
        """环境信息 单个查询"""
        if pk:
            environ_obj = Environment.objects.filter(pk=pk).first()
            if environ_obj:
                environ_serializer = EnvironmentSerializerQuery(environ_obj)
                return success_response(data=environ_serializer.data, msg='环境信息查询成功！')
            return error_response(msg='环境信息查询成功，无数据信息！')
        else:
            return error_response(msg='查询条件id为空，无数据信息！')

    @swagger_auto_schema(
        operation_summary='测试环境信息修改',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'environmental_name': openapi.Schema(type=openapi.TYPE_STRING, description='环境名称'),
                'entry_name': openapi.Schema(type=openapi.TYPE_INTEGER, description='项目id'),
                'Test_type': openapi.Schema(type=openapi.TYPE_INTEGER, description="测试类型-- (0: 'UI自动化测试',1: 'API自动化测试')"),
                'Testing_phase': openapi.Schema(type=openapi.TYPE_INTEGER,
                                                description="(0:UT测试,1:SIT测试,2:UAT测试,3:生产验收"),
                'Test_address': openapi.Schema(type=openapi.TYPE_STRING, description='测试地址'),
                'Test_account': openapi.Schema(type=openapi.TYPE_STRING, description='测试账号'),
                'Test_password': openapi.Schema(type=openapi.TYPE_STRING, description='测试密码'),
                'remark': openapi.Schema(type=openapi.TYPE_STRING, description='备注')
            }
        )
    )
    def put(self, request, pk):
        if pk:
            data = JSONParser().parse(request)
            environ_obj = Environment.objects.filter(id=pk).first()
            environ_obj_serializer = EnvironmentSerializerAdd(instance=environ_obj, data=data)
            if environ_obj_serializer.is_valid():
                environ_obj_serializer.save()
                return success_response(data='', msg="成功")
            else:
                return error_response(msg=environ_obj_serializer.errors)
        else:
            return error_response(msg="id为空！")


class EnvironmentListView(APIView):
    authentication_classes = ()
    permission_classes = []

    @swagger_auto_schema(
        operation_summary='环境管理 列表页(多条件筛选)',
        manual_parameters=[
            openapi.Parameter(name='page', in_=openapi.IN_QUERY, description='页码', type=openapi.TYPE_STRING),
            openapi.Parameter(name='page_size', in_=openapi.IN_QUERY, description='数量', type=openapi.TYPE_STRING),
            openapi.Parameter(name='environmental_name', in_=openapi.IN_QUERY, description='环境名称', type=openapi.TYPE_STRING),
            openapi.Parameter(name='entry_name', in_=openapi.IN_QUERY, description='项目id',
                              type=openapi.TYPE_INTEGER),
        ])
    def get(self, request):
        try:
            page_size = int(request.GET.get("page_size", 15))
            page = int(request.GET.get("page", 1))
            environmental_name = request.GET.get('environmental_name')
            entry_name = request.GET.get('entry_name')
            aQ = Q()
            if environmental_name:  # 多字段筛选
                aQ.add(Q(environmental_name__contains=environmental_name), Q.AND)
            if entry_name:
                aQ.add(Q(entry_name=entry_name), Q.AND)

            queryset = Environment.objects.filter(aQ).order_by("id")
            total = len(queryset)  # 总数量
            paginator = Paginator(queryset, page_size)  # paginator对象
            try:
                obm = paginator.page(page)
                environ_serialize = EnvironmentSerializerQuery(obm, many=True)
                return_data = environ_serialize.data
                response = {
                    "data": return_data,
                    "page": page,
                    "total": total
                }
            except Exception as _e:
                response = {}
            return success_response(data=response, msg='环境信息查询成功！')
        except Exception as e:
            return error_response('失败!')

    @swagger_auto_schema(
        operation_summary='环境信息 单删群删',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'ids': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_STRING),
                                      description='需要的环境信息id列表 ')
            }))
    def delete(self, request):
        try:
            with transaction.atomic():
                data = JSONParser().parse(request)
                delete_ids = data['ids']
                for id in delete_ids:
                    environ_obj = Environment.objects.filter(id=id)
                    if environ_obj:
                        environ_obj.first().delete()
                    else:
                        return error_response(msg="数据错误!")
        except Exception as e:
            return error_response(msg="失败!")
        return success_response(data='', msg="成功!")
