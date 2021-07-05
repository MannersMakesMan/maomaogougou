from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q
from drf_yasg2 import openapi
from drf_yasg2.utils import swagger_auto_schema
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView

from account_system.models import Position
from account_system.serializers import PositionSerializerQuery, PositionSerializerAdd
from automated_testing.common.api_response import JsonResponse


class PositionView(APIView):
    authentication_classes = ()
    permission_classes = []

    @swagger_auto_schema(
        operation_summary='职位 列表页',
        manual_parameters=[
            openapi.Parameter(name='page_size', in_=openapi.IN_QUERY, description='每页数量',
                              type=openapi.TYPE_STRING),
            openapi.Parameter(name='page', in_=openapi.IN_QUERY, description='页码',
                              type=openapi.TYPE_STRING),
            openapi.Parameter(name='position_name', in_=openapi.IN_QUERY, description='职位名称',
                              type=openapi.TYPE_STRING)

        ])
    def get(self, request):
        try:
            page_size = int(request.GET.get("page_size", 10))
            page = int(request.GET.get("page", 1))
        except (TypeError, ValueError):
            return JsonResponse(code="999985", msg="page_size/page参数必须为int")
        aQ = Q()
        position_name = request.GET.get('position_name')
        queryset = Position.objects.all()
        if position_name:
            aQ.add(Q(position_name__contains=position_name), Q.AND)
        queryset = queryset.filter(aQ).order_by("id")
        paginator = Paginator(queryset, page_size)  # paginator对象
        total = len(queryset)
        try:
            obm = paginator.page(page)
            serialize = PositionSerializerQuery(obm, many=True)
            return_data = serialize.data
        except Exception as _e:
            return_data = []

        return JsonResponse(data={"data": return_data,
                                  "page": page,
                                  "total": total
                                  }, code="999999", msg="成功")
    @swagger_auto_schema(
        operation_summary='职位 增加',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'position_name': openapi.Schema(type=openapi.TYPE_STRING, description='职位名称'),
                'position_desc': openapi.Schema(type=openapi.TYPE_STRING, description='职位叙述'),
                'remark': openapi.Schema(type=openapi.TYPE_STRING, description='备注'),
            }))
    def post(self, request):
        """职位 增加"""
        data = JSONParser().parse(request)
        position_serializer = PositionSerializerAdd(data=data)
        if position_serializer.is_valid():
            position_serializer.save()
            return JsonResponse(code="999999", msg="成功", data=position_serializer.data)
        else:
            return JsonResponse(msg=position_serializer.errors, code="999998")

    @swagger_auto_schema(
        operation_summary='职位删除 单删 群删',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'ids': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_STRING),
                                      description='需要删除的职位id列表 ')
            }))
    def delete(self, request):
        data = JSONParser().parse(request)
        delete_ids = data['ids']
        try:  # 数据如果有误，数据库执行会出错
            rows = Position.objects.filter(pk__in=delete_ids).delete()
        except Exception as e:
            return JsonResponse(code="999998", msg="数据错误!")
        if rows:
            return JsonResponse(code="999999", msg="删除成功!")
        JsonResponse(code="999998", msg="失败!")


class PositionDetailView(APIView):
    authentication_classes = ()
    permission_classes = []

    @swagger_auto_schema(
        operation_summary='职位信息 单查',
    )
    def get(self, request, pk):
        """服务器信息查询 单查"""
        if pk:
            server_obj = Position.objects.filter(pk=pk).first()
            if server_obj:
                server_serializer = PositionSerializerQuery(server_obj)
                return JsonResponse(data=server_serializer.data, code="999999", msg="成功!")
            return JsonResponse(code="999998", msg="无数据!")
        else:
            return JsonResponse(code="999998", msg="id为空!")

    @swagger_auto_schema(
        operation_summary='职位信息 修改',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'position_name': openapi.Schema(type=openapi.TYPE_STRING, description='职位名称'),
                'position_desc': openapi.Schema(type=openapi.TYPE_STRING, description='职位叙述'),
                'remark': openapi.Schema(type=openapi.TYPE_STRING, description='备注'),
            }))
    def put(self, request, pk):
        if pk:
            data = JSONParser().parse(request)
            server_obj = Position.objects.filter(id=int(pk)).first()
            if server_obj:
                server_serializer = PositionSerializerAdd(instance=server_obj, data=data)
                if server_serializer.is_valid():
                    server_serializer.save()
                else:
                    return JsonResponse(msg=server_serializer.errors, code="999998")
                return JsonResponse(code="999999", msg="成功!", data=server_serializer.data)
            return JsonResponse(code="999998", msg="无数据!")
        else:
            return JsonResponse(code="999998", msg="id为空!")


