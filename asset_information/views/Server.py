from django.core.paginator import Paginator
from django.db.models import Q
from drf_yasg2 import openapi
from drf_yasg2.utils import swagger_auto_schema
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView

from automated_testing.common.api_response import JsonResponse

from asset_information.models import Server
from asset_information.serializers import ServerSerializerAdd, ServerSerializerQuery
from common.thread_task import thread_task_main
from common.tools import check_ip


class ServerView(APIView):
    authentication_classes = ()
    permission_classes = []

    def check_server_ping_task_func(self, server_id):
        # 多线程 服务器检测 任务执行函数
        server_obj = Server.objects.filter(id=server_id).first()
        if server_obj:
            server_ip = server_obj.server_ip
            if check_ip(server_ip):
                server_obj.Usage_status = 1
            else:
                server_obj.Usage_status = 0
            server_obj.save()

    @swagger_auto_schema(
        operation_summary='服务器 增加',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'server_ip': openapi.Schema(type=openapi.TYPE_STRING, description='服务器IP地址'),
                'operating_system': openapi.Schema(type=openapi.TYPE_INTEGER, description='操作系统id'),
                'server_model': openapi.Schema(type=openapi.TYPE_STRING, description='服务器型号'),
                'server_cpu': openapi.Schema(type=openapi.TYPE_INTEGER, description='服务器CPU（核）'),
                'server_memory': openapi.Schema(type=openapi.TYPE_INTEGER, description='服务器内存（G）'),
                'server_disk': openapi.Schema(type=openapi.TYPE_INTEGER, description='服务器硬盘（T）'),
                'user_department': openapi.Schema(type=openapi.TYPE_INTEGER, description='使用部门id'),
                'person_liable': openapi.Schema(type=openapi.TYPE_INTEGER, description='管理责任人id'),
            }))
    def post(self, request):
        """服务器 增加 此接口需要先拉取表单数据字典"""
        data = JSONParser().parse(request)
        server_serializer = ServerSerializerAdd(data=data)
        if server_serializer.is_valid():
            server_serializer.save()
            return JsonResponse(code="999999", msg="成功")
        else:
            return JsonResponse(msg=server_serializer.errors, code="999998")

    @swagger_auto_schema(
        operation_summary='服务器 列表页(多条件筛选)',
        manual_parameters=[
            openapi.Parameter(name='page', in_=openapi.IN_QUERY, description='页码', type=openapi.TYPE_STRING),
            openapi.Parameter(name='page_size', in_=openapi.IN_QUERY, description='数量', type=openapi.TYPE_STRING),
            openapi.Parameter(name='server_ip', in_=openapi.IN_QUERY, description='服务器ip', type=openapi.TYPE_STRING),
            openapi.Parameter(name='person_liable', in_=openapi.IN_QUERY, description='管理责任人', type=openapi.TYPE_STRING),
            openapi.Parameter(name='AUTHORIZATION', in_=openapi.IN_HEADER, description='登录验证',
                              type=openapi.TYPE_STRING),
        ])
    def get(self, request):
        """服务器 群查 列表页(多条件筛选)"""
        page_size = int(request.GET.get("page_size", 20))
        page = int(request.GET.get("page", 1))

        queryset = Server.objects.all()
        server_ip = request.GET.get("server_ip")  # 服务器ip
        person_liable = request.GET.get("person_liable")  # 管理责任人
        aQ = Q()
        if server_ip:  # 多字段筛选
            aQ.add(Q(server_ip__contains=server_ip), Q.AND)
        if person_liable:
            aQ.add(Q(person_liable__Real_name__contains=person_liable), Q.AND)
        queryset = queryset.filter(aQ).order_by("id")
        paginator = Paginator(queryset, page_size)  # paginator对象
        total = len(queryset)  # 总数量
        try:
            obm = paginator.page(page)
            server_serialize = ServerSerializerQuery(obm, many=True)
            return_data = server_serialize.data
            thread_task_main([i['id'] for i in return_data], 1, self.check_server_ping_task_func)  # 执行批量ip检测

        except Exception as _e:
            return_data = []

        return JsonResponse(data={"data": return_data,
                                  "page": page,
                                  "total": total
                                  }, code="999999", msg="成功")

    @swagger_auto_schema(
        operation_summary='服务器 单删群删',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'ids': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_STRING),
                                      description='需要删除的服务器id列表 ')
            }))
    def delete(self, request):
        """服务器 单删群删"""
        data = JSONParser().parse(request)
        delete_ids = data['ids']
        try:  # 数据如果有误，数据库执行会出错
            rows = Server.objects.filter(pk__in=delete_ids).delete()
        except Exception as e:
            return JsonResponse(code="999998", msg="数据错误!")

        if rows:
            return JsonResponse(code="999999", msg="删除成功!")
        JsonResponse(code="999998", msg="失败!")

class ServerDetailView(APIView):
    authentication_classes = ()
    permission_classes = []

    @swagger_auto_schema(
        operation_summary='服务器信息查询 单查',
    )
    def get(self, request, pk):
        """服务器信息查询 单查"""
        if pk:
            server_obj = Server.objects.filter(pk=pk).first()
            if server_obj:
                server_serializer = ServerSerializerQuery(server_obj)
                return JsonResponse(data=server_serializer.data, code="999999", msg="成功!")
            return JsonResponse(code="999998", msg="无数据!")
        else:
            return JsonResponse(code="999998", msg="id为空!")

    @swagger_auto_schema(
        operation_summary='服务器信息 修改',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'server_ip': openapi.Schema(type=openapi.TYPE_STRING, description='服务器IP地址'),
                'operating_system': openapi.Schema(type=openapi.TYPE_INTEGER, description='操作系统id'),
                'server_model': openapi.Schema(type=openapi.TYPE_STRING, description='服务器型号'),
                'server_cpu': openapi.Schema(type=openapi.TYPE_INTEGER, description='服务器CPU（核）'),
                'server_memory': openapi.Schema(type=openapi.TYPE_INTEGER, description='服务器内存（G）'),
                'server_disk': openapi.Schema(type=openapi.TYPE_INTEGER, description='服务器硬盘（T）'),
                'user_department': openapi.Schema(type=openapi.TYPE_INTEGER, description='使用部门id'),
                'person_liable': openapi.Schema(type=openapi.TYPE_INTEGER, description='管理责任人id'),
            }))
    def put(self, request, pk):
        """服务器信息 修改 此接口需要先拉取表单数据字典"""
        if pk:
            data = JSONParser().parse(request)
            server_obj = Server.objects.filter(id=pk).first()
            if server_obj:
                server_serializer = ServerSerializerAdd(instance=server_obj, data=data)
                if server_serializer.is_valid():
                    server_serializer.save()
                else:
                    return JsonResponse(msg=server_serializer.errors, code="999998")
                return JsonResponse(code="999999", msg="成功!")
            return JsonResponse(code="999998", msg="无数据!")
        else:
            return JsonResponse(code="999998", msg="id为空!")

