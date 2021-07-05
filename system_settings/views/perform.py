# -*- coding: utf-8 -*-
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q
from django.forms import model_to_dict
from drf_yasg2.utils import swagger_auto_schema
from drf_yasg2 import openapi
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView

from automated_testing.common.api_response import JsonResponse
from common.thread_task import thread_task_main
from common.tools import check_ip
from system_settings.models import Environment, PerformMachine
from system_settings.serializers import PerformMachineSerializerAdd, PerformMachineSerializerQuery
from system_settings.tools import error_response, success_response


class PerformMachineAddView(APIView):
    authentication_classes = ()
    permission_classes = []

    @swagger_auto_schema(
        operation_summary='执行机信息 新增',

        manual_parameters=[
            openapi.Parameter(name='AUTHORIZATION', in_=openapi.IN_HEADER, description='登录验证',
                              type=openapi.TYPE_STRING),
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'perform_ip': openapi.Schema(type=openapi.TYPE_STRING, description='执行机ip'),
                'entry_name': openapi.Schema(type=openapi.TYPE_INTEGER, description='项目id'),
                'java_version': openapi.Schema(type=openapi.TYPE_STRING, description='java版本'),
                'operating_system': openapi.Schema(type=openapi.TYPE_INTEGER, description='操作系统  ex : {0:windows server 2008,1:windows server 2012, 2:windows 10,3:Centos 6,4:Centos 7'),
                'browser_version': openapi.Schema(type=openapi.TYPE_STRING, description='浏览器版本'),
                'browser_type': openapi.Schema(type=openapi.TYPE_INTEGER, description='浏览器类型  ex: {0:chrome,1:firefox,2: ie}'),
                'machine_description': openapi.Schema(type=openapi.TYPE_STRING, description='执行机使用描述'),
                'remark': openapi.Schema(type=openapi.TYPE_STRING, description='备注'),
            }
        )
    )
    def post(self, request):
        """执行机 增加"""
        data = JSONParser().parse(request)
        perform_ip = data.get('perform_ip')
        if check_ip(perform_ip):
            data['status'] = 1
        else:
            data['status'] = 0
        perform_serializer = PerformMachineSerializerAdd(data=data)
        if perform_serializer.is_valid():
            data = perform_serializer.save()
            return success_response(data=PerformMachineSerializerQuery(data).data, msg='新增执行机信息成功！')
        else:
            return error_response(msg=perform_serializer.errors)


class PerformMachineView(APIView):
    authentication_classes = ()
    permission_classes = []

    @swagger_auto_schema(
        operation_summary='执行机 单个查询'
    )
    def get(self, request, pk):
        """执行机 单个查询"""
        if pk:
            perform_obj = PerformMachine.objects.filter(pk=pk).first()
            if perform_obj:
                perform_serializer = PerformMachineSerializerQuery(perform_obj)
                return success_response(data=perform_serializer.data, msg='执行机信息查询成功！')
            return error_response(msg='执行机信息查询成功，无数据信息！')
        else:
            return error_response(msg='查询条件id为空，无数据信息！')

    @swagger_auto_schema(
        operation_summary='执行机信息修改',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'perform_ip': openapi.Schema(type=openapi.TYPE_STRING, description='执行机ip'),
                'entry_name': openapi.Schema(type=openapi.TYPE_INTEGER, description='项目id'),
                'java_version': openapi.Schema(type=openapi.TYPE_STRING, description='java版本'),
                'operating_system': openapi.Schema(type=openapi.TYPE_INTEGER, description='操作系统  ex : {0:windows server 2008,1:windows server 2012, 2:windows 10,3:Centos 6,4:Centos 7'),
                'browser_version': openapi.Schema(type=openapi.TYPE_STRING, description='浏览器版本'),
                'browser_type': openapi.Schema(type=openapi.TYPE_INTEGER, description='浏览器类型  ex: {0:chrome,1:firefox,2: ie}'),
                'machine_description': openapi.Schema(type=openapi.TYPE_STRING, description='执行机使用描述'),
                'remark': openapi.Schema(type=openapi.TYPE_STRING, description='备注'),
            }
        )
    )
    def put(self, request, pk):
        if pk:
            data = JSONParser().parse(request)
            perform_obj = PerformMachine.objects.filter(id=pk).first()
            perform_obj_serializer = PerformMachineSerializerAdd(instance=perform_obj, data=data)
            if perform_obj_serializer.is_valid():
                perform_obj_serializer.save()
                return success_response(data='', msg="成功")
            else:
                return error_response(msg=perform_obj_serializer.errors)
        else:
            return error_response(msg="id为空！")


class PerformMachineListView(APIView):
    authentication_classes = ()
    permission_classes = []

    def check_perform_ping_task_func(self, server_id):
        # 多线程 服务器检测 任务执行函数
        perform_obj = PerformMachine.objects.filter(id=server_id).first()
        if perform_obj:
            perform_ip = perform_obj.perform_ip
            if check_ip(perform_ip):
                if perform_obj.status != 1:
                    perform_obj.status = 1
                    perform_obj.save()
            else:
                if perform_obj.status != 0:
                    perform_obj.status = 0
                    perform_obj.save()


    @swagger_auto_schema(
        operation_summary='执行机信息 列表页(多条件筛选)',
        manual_parameters=[
            openapi.Parameter(name='AUTHORIZATION', in_=openapi.IN_HEADER, description='登录验证', type=openapi.TYPE_STRING),
            openapi.Parameter(name='page', in_=openapi.IN_QUERY, description='页码', type=openapi.TYPE_STRING),
            openapi.Parameter(name='page_size', in_=openapi.IN_QUERY, description='数量', type=openapi.TYPE_STRING),
            openapi.Parameter(name='perform_ip', in_=openapi.IN_QUERY, description='执行机ip', type=openapi.TYPE_STRING),
            openapi.Parameter(name='operating_system', in_=openapi.IN_QUERY, description='操作系统', type=openapi.TYPE_INTEGER),
            openapi.Parameter(name='entry_name', in_=openapi.IN_QUERY, description='项目id', type=openapi.TYPE_INTEGER),
        ])
    def get(self, request):
        try:
            page_size = int(request.GET.get("page_size", 15))
            page = int(request.GET.get("page", 1))
            perform_ip = request.GET.get('perform_ip')
            operating_system = request.GET.get('operating_system')
            entry_name = request.GET.get('entry_name')
            aQ = Q()
            if perform_ip:  # 多字段筛选
                aQ.add(Q(perform_ip=perform_ip), Q.AND)
            if operating_system:  # 多字段筛选
                aQ.add(Q(operating_system=operating_system), Q.AND)
            if entry_name:
                aQ.add(Q(entry_name=entry_name), Q.AND)

            queryset = PerformMachine.objects.filter(aQ).order_by("id")
            total = len(queryset)  # 总数量
            paginator = Paginator(queryset, page_size)  # paginator对象
            try:
                obm = paginator.page(page)
                perform_serialize = PerformMachineSerializerQuery(obm, many=True)
                return_data = perform_serialize.data
                thread_task_main([i['id'] for i in return_data], 3, self.check_perform_ping_task_func)  # 执行批量ip检测
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
        operation_summary='执行机信息 单删群删',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'ids': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_STRING),
                                      description='需要的执行机id列表 ')
            }))
    def delete(self, request):
        try:
            with transaction.atomic():
                data = JSONParser().parse(request)
                delete_ids = data['ids']
                for id in delete_ids:
                    perform_obj = PerformMachine.objects.filter(id=id)
                    if perform_obj:
                        perform_obj.first().delete()
                    else:
                        return error_response(msg="数据错误!")
        except Exception as e:
            return error_response(msg="失败!")
        return success_response(data='', msg="成功!")


class PerformMachineAllListView(APIView):
    authentication_classes = ()
    permission_classes = []

    @swagger_auto_schema(
        operation_summary='执行机全部ip查询 用于ui自动化执行 ip选择',
        manual_parameters=[
            openapi.Parameter(name='AUTHORIZATION', in_=openapi.IN_HEADER, description='登录验证', default='dev', type=openapi.TYPE_STRING)]
    )
    def get(self, request):
        try:
            vm_worker_tree = [{"label": i.perform_ip, "id": i.id} for i in PerformMachine.objects.all()]
        except Exception as e:
            vm_worker_tree = []

        return JsonResponse(data=vm_worker_tree, code="999999", msg="成功!")
