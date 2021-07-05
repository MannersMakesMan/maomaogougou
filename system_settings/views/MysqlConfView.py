from django.core.paginator import Paginator
from django.db.models import Q
from drf_yasg2 import openapi
from drf_yasg2.utils import swagger_auto_schema
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView

from common.mysql_operation import mysql_operation
from common.thread_task import thread_task_main
from common.tools import check_ip
from system_settings.models import MysqlInfo
from system_settings.serializers import MysqlInfoSerializerAdd, MysqlInfoSerializerQuery, \
    MysqlInfoDropDownBoxSerializerQuery
from system_settings.tools import error_response, success_response
from user_interface_test.models import TestCaseData


class MysqlInfoView(APIView):
    authentication_classes = ()
    permission_classes = []

    def check_mysql_connect_task_func(self, mysql_info):
        # 多线程 数据库检测 执行函数
        mysql_obj = MysqlInfo.objects.get(id=id)
        try:
            mysql_operation.create_connect(mysql_info)
            mysql_obj.status = 1

        except Exception as _:
            mysql_obj.status = 0
        mysql_obj.save()


    @swagger_auto_schema(
        operation_summary='mysql配置 增加',
        manual_parameters=[
            openapi.Parameter(name='AUTHORIZATION', in_=openapi.IN_HEADER, description='登录验证',
                              type=openapi.TYPE_STRING),
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'connect_name': openapi.Schema(type=openapi.TYPE_STRING, description='链接名'),
                'host': openapi.Schema(type=openapi.TYPE_STRING, description='ip地址'),
                'port': openapi.Schema(type=openapi.TYPE_STRING, description='端口号'),
                'user': openapi.Schema(type=openapi.TYPE_STRING, description='账号'),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description='密码'),
                'table_name': openapi.Schema(type=openapi.TYPE_STRING, description='数据库'),
                'remark': openapi.Schema(type=openapi.TYPE_STRING, description='备注'),
            }))
    def post(self, request):
        data = JSONParser().parse(request)
        mysql_serializer = MysqlInfoSerializerAdd(data=data)
        if mysql_serializer.is_valid():
            return_data = mysql_serializer.save()
            return success_response(data=return_data.id, msg="mysql链接添加成功")
        else:
            return error_response(msg=mysql_serializer.errors)

    @swagger_auto_schema(
        operation_summary='mysql配置 单删群删',
        manual_parameters=[
            openapi.Parameter(name='AUTHORIZATION', in_=openapi.IN_HEADER, description='登录验证',
                              type=openapi.TYPE_STRING),
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'ids': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_INTEGER),
                                      description='需要删除的mysql配置id列表 ')
            }))
    def delete(self, request):
        data = JSONParser().parse(request)
        delete_ids = data['ids']
        try:
            for id in delete_ids:
                if TestCaseData.objects.filter(mysql_info_id=int(id)):
                    return error_response(msg="删除失败, mysql配置被测试用例关联")
                mysql_info_obj = MysqlInfo.objects.filter(id=int(id)).first()
                if mysql_info_obj:
                    mysql_info_obj.delete()
                else:
                    return error_response(msg="无此数据")
        except Exception as _:
            return error_response(msg="删除失败")
        return success_response(msg="删除成功")


    @swagger_auto_schema(
        operation_summary='mysql配置 列表页(多条件筛选)',
        manual_parameters=[
            openapi.Parameter(name='AUTHORIZATION', in_=openapi.IN_HEADER, description='登录验证',
                              type=openapi.TYPE_STRING),
            openapi.Parameter(name='page', in_=openapi.IN_QUERY, description='页码', type=openapi.TYPE_STRING),
            openapi.Parameter(name='page_size', in_=openapi.IN_QUERY, description='数量', type=openapi.TYPE_STRING),
            openapi.Parameter(name='host', in_=openapi.IN_QUERY, description='ip地址', type=openapi.TYPE_STRING),
            openapi.Parameter(name='table_name', in_=openapi.IN_QUERY, description='数据库名', type=openapi.TYPE_STRING),
            openapi.Parameter(name='connect_name', in_=openapi.IN_QUERY, description='链接名', type=openapi.TYPE_STRING),

        ])
    def get(self, request):
        """虚拟机 群查 列表页(多条件筛选)"""
        page_size = int(request.GET.get("page_size", 20))
        page = int(request.GET.get("page", 1))

        queryset = MysqlInfo.objects.all()
        host = request.GET.get("host", '')
        table_name = request.GET.get("table_name", '')
        connect_name = request.GET.get("connect_name", '')
        aQ = Q()
        if host:  # 多字段筛选
            aQ.add(Q(host__contains=host), Q.AND)
        if table_name:
            aQ.add(Q(table_name__contains=table_name), Q.AND)
        if connect_name:
            aQ.add(Q(connect_name__contains=connect_name), Q.AND)

        queryset = queryset.filter(aQ).order_by("id")

        paginator = Paginator(queryset, page_size)  # paginator对象
        total = len(queryset)  # 总数量
        try:
            obm = paginator.page(page)
            vm_serialize = MysqlInfoSerializerQuery(obm, many=True)
            return_data = vm_serialize.data
            thread_task_main([{
                "host": i["host"],
                "port": i["port"],
                "user": i["user"],
                "password": i["password"],
                "database": i["table_name"],
                "connect_timeout": 1,
            } for i in return_data], 5, self.check_mysql_connect_task_func)  # 执行批量ip检测

        except Exception as _e:
            return_data = []

        return success_response(data={"data": return_data, "page": page, "total": total}, msg="成功")


class MysqlInfoViewDetail(APIView):
    authentication_classes = ()
    permission_classes = []

    @swagger_auto_schema(
        operation_summary='mysql配置 单查',
        manual_parameters=[
            openapi.Parameter(name='AUTHORIZATION', in_=openapi.IN_HEADER, description='登录验证',
                              type=openapi.TYPE_STRING),
        ],
        )
    def get(self, request, pk):
        if pk:
            mysql_obj = MysqlInfo.objects.filter(pk=pk).first()
            if mysql_obj:
                mysql_serializer = MysqlInfoSerializerQuery(mysql_obj)
                return success_response(data=mysql_serializer.data, msg="成功")
            return error_response(msg="无此配置")
        else:
            return error_response(msg="id为空!")

    @swagger_auto_schema(
        operation_summary='mysql配置 修改',
        manual_parameters=[
            openapi.Parameter(name='AUTHORIZATION', in_=openapi.IN_HEADER, description='登录验证',
                              type=openapi.TYPE_STRING),
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'connect_name': openapi.Schema(type=openapi.TYPE_STRING, description='链接名'),
                'host': openapi.Schema(type=openapi.TYPE_STRING, description='ip地址'),
                'port': openapi.Schema(type=openapi.TYPE_STRING, description='端口号'),
                'user': openapi.Schema(type=openapi.TYPE_STRING, description='账号'),
                'table_name': openapi.Schema(type=openapi.TYPE_STRING, description='数据库'),
                'remark': openapi.Schema(type=openapi.TYPE_STRING, description='备注'),
            }))
    def put(self, request, pk):
        if pk:
            data = JSONParser().parse(request)
            mysql_obj = MysqlInfo.objects.filter(id=pk).first()
            if mysql_obj:
                mysql_serializer = MysqlInfoSerializerAdd(instance=mysql_obj, data=data)
                if mysql_serializer.is_valid():
                    return_data = mysql_serializer.save()
                    return success_response(data=return_data.id, msg="成功!")
                else:
                    return error_response(msg=mysql_serializer.errors)
            return error_response(msg="无此配置")
        else:
            return error_response(msg="id为空!")


class MysqlTableDropDownBox(APIView):
    authentication_classes = ()
    permission_classes = []

    @swagger_auto_schema(
        operation_summary='mysql配置 列表页(下拉框)',
        manual_parameters=[
            openapi.Parameter(name='AUTHORIZATION', in_=openapi.IN_HEADER, description='登录验证',
                              type=openapi.TYPE_STRING),
            openapi.Parameter(name='connect_name', in_=openapi.IN_QUERY, description='链接名', type=openapi.TYPE_STRING),

        ])
    def get(self, request):
        connect_name = request.GET.get("connect_name", '')
        mysql_objs = MysqlInfo.objects.filter(connect_name__contains=connect_name)
        mysql_serializer = MysqlInfoDropDownBoxSerializerQuery(mysql_objs, many=True)
        return success_response(data=mysql_serializer.data, msg="成功")
