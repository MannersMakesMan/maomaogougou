# -*- coding: utf-8 -*-
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q
from drf_yasg2.utils import swagger_auto_schema
from drf_yasg2 import openapi
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView

from system_settings.serializers import ProjectSerializerAdd, ProjectSerializerQuery
from automated_testing.common.api_response import JsonResponse
from system_settings.tools import error_response, success_response
from system_settings.models import Project, Environment, PerformMachine
from zy_api_testing.tools import DelException


class ProjectAddView(APIView):
    authentication_classes = ()
    permission_classes = []

    @swagger_auto_schema(
        operation_summary='项目信息 新增',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'entry_name': openapi.Schema(type=openapi.TYPE_STRING, description='项目名称'),
                'project_manager': openapi.Schema(type=openapi.TYPE_INTEGER, description='项目经理id'),
                'Test_Leader': openapi.Schema(type=openapi.TYPE_INTEGER, description='测试负责人id'),
                'Project_description': openapi.Schema(type=openapi.TYPE_STRING, description='项目描述'),
                'remark': openapi.Schema(type=openapi.TYPE_STRING, description='备注')
            }
        )
    )
    def post(self, request):
        """项目信息 增加"""
        data = JSONParser().parse(request)
        project_serializer = ProjectSerializerAdd(data=data)
        if project_serializer.is_valid():
            project_serializer.save()
            return success_response(data='', msg='新增项目信息成功！')
        else:
            return error_response(msg=project_serializer.errors)

    @swagger_auto_schema(
        operation_summary='项目管理 修改',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'id': openapi.Schema(type=openapi.TYPE_STRING, description='项目id'),
                'entry_name': openapi.Schema(type=openapi.TYPE_STRING, description='项目名称'),
                'project_manager': openapi.Schema(type=openapi.TYPE_INTEGER, description='项目经理id'),
                'Test_Leader': openapi.Schema(type=openapi.TYPE_INTEGER, description='测试负责人id'),
                'Project_description': openapi.Schema(type=openapi.TYPE_STRING, description='项目描述'),
                'remarks': openapi.Schema(type=openapi.TYPE_STRING, description='备注')
            }
        ))
    def put(self, request):
        try:
            data = JSONParser().parse(request)
            pk = data.get('id')
            if not pk:
                return error_response(msg='id is None')
            project_obj = Project.objects.filter(id=pk).first()
            project_serializer = ProjectSerializerAdd(instance=project_obj, data=data)
            if project_serializer.is_valid():
                project_serializer.save()
                return success_response(data='', msg="成功")
            else:
                return error_response(msg=project_serializer.errors)
        except Exception as e:
            return error_response(msg='失败!!')

    @swagger_auto_schema(
        operation_summary='項目管理 单删群删',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'ids': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_STRING),
                                      description='需要删除的項目id列表 ')
            }))
    def delete(self, request):
        try:
            with transaction.atomic():
                data = JSONParser().parse(request)
                delete_ids = data['ids']
                for id in delete_ids:
                    project_obj = Project.objects.filter(id=id).first()
                    if project_obj:
                        # 删除项目时校验： 是否有关联该项目的环境， 是否有关联该项目的执行机
                        if Environment.objects.filter(entry_name=project_obj.id):
                            raise DelException('Env')
                        if PerformMachine.objects.filter(entry_name=project_obj.id):
                            raise DelException('Pro')
                        project_obj.delete()
                    else:
                        return error_response(msg="数据错误!")
        except Exception as e:
            if str(e)=='Env':
                return error_response(msg="删除失败 项目: {},下存才关联测试环境".format(project_obj.entry_name))
            if str(e)=='Pro':
                return error_response(msg="删除失败 项目: {},下存才关联执行机".format(project_obj.entry_name))
            return error_response(msg="失败!")
        return success_response(data='', msg="成功!")



class ProjectView(APIView):
    authentication_classes = ()
    permission_classes = []

    @swagger_auto_schema(
        operation_summary='项目信息 单个查询'
    )
    def get(self, request, pk):
        """项目信息 单个查询"""
        if pk:
            project_obj = Project.objects.filter(pk=pk).first()
            if project_obj:
                project_serializer = ProjectSerializerQuery(project_obj)
                return success_response(data=project_serializer.data, msg='项目信息查询成功！')
            return error_response(msg='项目信息查询成功，无数据信息！')
        else:
            return error_response(msg='查询条件id为空，无数据信息！')




class ProjectListView(APIView):
    authentication_classes = ()
    permission_classes = []

    @swagger_auto_schema(
        operation_summary='项目管理 列表页(多条件筛选)',
        manual_parameters=[
            openapi.Parameter(name='page', in_=openapi.IN_QUERY, description='页码', type=openapi.TYPE_STRING),
            openapi.Parameter(name='page_size', in_=openapi.IN_QUERY, description='数量', type=openapi.TYPE_STRING),
            openapi.Parameter(name='entry_name', in_=openapi.IN_QUERY, description='项目名称', type=openapi.TYPE_STRING),
            openapi.Parameter(name='project_manager', in_=openapi.IN_QUERY, description='项目管理人', type=openapi.TYPE_INTEGER),
        ])
    def get(self, request):
        try:
            page_size = int(request.GET.get("page_size", 15))
            page = int(request.GET.get("page", 1))
            entry_name = request.GET.get('entry_name')
            project_manager = request.GET.get('project_manager')
            aQ = Q()
            if entry_name:  # 多字段筛选
                aQ.add(Q(entry_name__contains=entry_name), Q.AND)
            if project_manager:
                aQ.add(Q(project_manager=project_manager), Q.AND)

            queryset = Project.objects.filter(aQ).order_by("id")

            total = len(queryset)  # 总数量
            paginator = Paginator(queryset, page_size)  # paginator对象
            try:
                obm = paginator.page(page)
                project_serialize = ProjectSerializerQuery(obm, many=True)
                return_data = project_serialize.data
                response = {
                    "data": return_data,
                    "page": page,
                    "total": total
                }
            except Exception as _e:
                response = {}
            return success_response(data=response, msg='项目信息查询成功！')
        except Exception as e:
            return  error_response(msg='失败!!')
