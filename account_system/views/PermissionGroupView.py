from django.core.paginator import Paginator
from django.db.models import Q
from drf_yasg2 import openapi
from drf_yasg2.utils import swagger_auto_schema
from rest_framework.views import APIView
from account_system.models import PermissionGroup, PermissionViewResources
from account_system.tools import save_permissionview_resource
from automated_testing.common.api_response import JsonResponse
from account_system.serializers import PermissionGroupSerializerQuery, PermissionGroupSerializerAdd, \
    PermissionResourcesSerializerQuery
from rest_framework.parsers import JSONParser

save_permissionview_resource()

class PermissionGroupView(APIView):
    authentication_classes = ()
    permission_classes = []

    @swagger_auto_schema(
        operation_summary='权限组 列表页',
        manual_parameters=[
            openapi.Parameter(name='AUTHORIZATION', in_=openapi.IN_HEADER, description='登录验证',
                        type=openapi.TYPE_STRING, default="dev"),
            openapi.Parameter(name='page_size', in_=openapi.IN_QUERY, description='每页数量',
                              type=openapi.TYPE_STRING),
            openapi.Parameter(name='page', in_=openapi.IN_QUERY, description='页码',
                              type=openapi.TYPE_STRING)
        ])
    def get(self, request):
        try:
            page_size = int(request.GET.get("page_size", 10))
            page = int(request.GET.get("page", 1))
        except (TypeError, ValueError):
            return JsonResponse(code="999985", msg="page_size/page参数必须为int")
        queryset = PermissionGroup.objects.all().order_by("id")

        paginator = Paginator(queryset, page_size)  # paginator对象
        total = len(queryset)
        try:
            obm = paginator.page(page)
            serialize = PermissionGroupSerializerQuery(obm, many=True)
            return_data = serialize.data
        except Exception as _e:
            return_data = []

        return JsonResponse(data={"data": return_data,
                                  "page": page,
                                  "total": total
                                  }, code="999999", msg="成功")

    @swagger_auto_schema(
        operation_summary='权限组 增加',
        manual_parameters=[
            openapi.Parameter(name='AUTHORIZATION', in_=openapi.IN_HEADER, description='登录验证',
                              type=openapi.TYPE_STRING, default="dev"),],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'permission_group_name': openapi.Schema(type=openapi.TYPE_STRING, description='权限组名称'),
                'permission_group_desc': openapi.Schema(type=openapi.TYPE_STRING, description='权限组描述'),
            }))
    def post(self, request):
        """权限组 增加"""
        data = JSONParser().parse(request)
        permission_group_serializer = PermissionGroupSerializerAdd(data=data)
        if permission_group_serializer.is_valid():
            permission_group_serializer.save()
            return JsonResponse(code="999999", msg="成功", data=permission_group_serializer.data)
        else:
            return JsonResponse(msg=permission_group_serializer.errors, code="999998")

    @swagger_auto_schema(
        operation_summary='权限组删除 单删 群删',
        manual_parameters=[
            openapi.Parameter(name='AUTHORIZATION', in_=openapi.IN_HEADER, description='登录验证',
                              type=openapi.TYPE_STRING, default="dev"), ],
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
            rows = PermissionGroup.objects.filter(pk__in=delete_ids).delete()
        except Exception as e:
            return JsonResponse(code="999998", msg="数据错误!")
        if rows:
            return JsonResponse(code="999999", msg="删除成功!")
        JsonResponse(code="999998", msg="失败!")


class PermissionGroupDetailView(APIView):
    authentication_classes = ()
    permission_classes = []

    @swagger_auto_schema(
        operation_summary='权限组信息 单查',
        manual_parameters=[
            openapi.Parameter(name='AUTHORIZATION', in_=openapi.IN_HEADER, description='登录验证',
                              type=openapi.TYPE_STRING, default="dev"), ],
    )
    def get(self, request, pk):
        """权限组信息 单查"""
        if pk:
            server_obj = PermissionGroup.objects.filter(pk=pk).first()
            if server_obj:
                server_serializer = PermissionGroupSerializerQuery(server_obj)
                return JsonResponse(data=server_serializer.data, code="999999", msg="成功!")
            return JsonResponse(code="999998", msg="无数据!")
        else:
            return JsonResponse(code="999998", msg="id为空!")

    @swagger_auto_schema(
        operation_summary='权限组信息 修改',
        manual_parameters=[
            openapi.Parameter(name='AUTHORIZATION', in_=openapi.IN_HEADER, description='登录验证',
                              type=openapi.TYPE_STRING, default="dev"), ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'permission_group_name': openapi.Schema(type=openapi.TYPE_STRING, description='权限组名称'),
                'permission_group_desc': openapi.Schema(type=openapi.TYPE_STRING, description='权限组描述'),
            }))
    def put(self, request, pk):
        if pk:
            data = JSONParser().parse(request)
            server_obj = PermissionGroup.objects.filter(id=int(pk)).first()
            if server_obj:
                permission_group_serializer = PermissionGroupSerializerAdd(instance=server_obj, data=data)
                if permission_group_serializer.is_valid():
                    permission_group_serializer.save()
                else:
                    return JsonResponse(msg=permission_group_serializer.errors, code="999998")
                return JsonResponse(code="999999", msg="成功!", data=permission_group_serializer.data)
            return JsonResponse(code="999998", msg="无数据!")
        else:
            return JsonResponse(code="999998", msg="id为空!")


class PermissionGroupResourcesView(APIView):
    authentication_classes = ()
    permission_classes = []

    def get_permission_resource_tree(self, data_list, permission_resource_obj):
        permission_resource_objs = PermissionViewResources.objects.filter(super_resource_id=permission_resource_obj.id)
        if permission_resource_objs:
            for permission_resource_obj in permission_resource_objs:
                permission_resource_serializer = PermissionResourcesSerializerQuery(permission_resource_obj)
                data = permission_resource_serializer.data
                data['is_allow'] = True if str(data['id']) in self.permission_ids else False
                data['children'] = []
                self.get_permission_resource_tree(data['children'], permission_resource_obj)
                data_list.append(data)

    @swagger_auto_schema(
        operation_summary='权限组 对应权限资源 查询',
        manual_parameters=[openapi.Parameter(name='AUTHORIZATION', in_=openapi.IN_HEADER, description='登录验证',
                                              type=openapi.TYPE_STRING, default="dev"), ],
    )
    def get(self, request, pk):
        permission_group_obj = PermissionGroup.objects.filter(id=pk).order_by('id')
        if permission_group_obj:
            permission_group_obj = permission_group_obj[0]
            permission_ids = permission_group_obj.permission_ids
            if permission_ids:
                self.permission_ids = permission_ids.split('_')
            else:
                self.permission_ids = []
            tree_data = []
            root_permission_resource_objs = PermissionViewResources.objects.filter(Q(super_resource_id__isnull=True) | Q(super_resource_id=''))
            for root_permission_resource_obj in root_permission_resource_objs:
                permission_resource_serializer = PermissionResourcesSerializerQuery(root_permission_resource_obj)
                data = permission_resource_serializer.data
                data['children'] = []
                self.get_permission_resource_tree(data['children'], root_permission_resource_obj)
                tree_data.append(data)
            return JsonResponse(code="999999", msg="查询成功！", data=tree_data)
        else:
            return JsonResponse(code="999998", msg="id为空!")

    @swagger_auto_schema(
        operation_summary='权限组 对应权限资源 修改',
        manual_parameters=[
            openapi.Parameter(name='AUTHORIZATION', in_=openapi.IN_HEADER, description='登录验证',
                              type=openapi.TYPE_STRING, default="dev"), ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'ids': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_STRING),
                                      description='权限组 允许的权限资源id列表')
            })
    )
    def put(self, request, pk):
        data = JSONParser().parse(request)
        permission_resource = "_".join(data['ids'])
        permission_group_objs = PermissionGroup.objects.filter(id=int(pk))
        if permission_group_objs:
            permission_group_obj = permission_group_objs[0]
            permission_group_obj.permission_ids = permission_resource
            permission_group_obj.save()
            return JsonResponse(code="999999", msg="成功!")
        else:
            return JsonResponse(code="999998", msg="id为空!")
