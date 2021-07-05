from drf_yasg2 import openapi
from drf_yasg2.utils import swagger_auto_schema

from rest_framework.views import APIView
from account_system.models import PermissionGroup
from automated_testing.common.api_response import JsonResponse
from account_system.serializers import PermissionGroupSerializer

from django.db import transaction
from rest_framework.parsers import JSONParser


class PermissionGroupView(APIView):
    authentication_classes = ()
    permission_classes = []

    @swagger_auto_schema(
        operation_summary='权限查询',
        manual_parameters=[
            # openapi.Parameter(name='ID', in_=openapi.IN_QUERY, description='ID', type=openapi.TYPE_STRING)
        ])
    def get(self, request):
        permissions = PermissionGroup.objects.all()
        res = PermissionGroupSerializer(permissions, many=True)
        return JsonResponse(data=res.data, code="999999", msg="成功")

    @swagger_auto_schema(
        operation_summary='权限分组增加',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'permissiongroup_name': openapi.Schema(type=openapi.TYPE_STRING, description='permission_name'),

                'permissiongroup_desc': openapi.Schema(type=openapi.TYPE_STRING, description='permission_desc'),
            }))
    def post(self, request):
        data = PermissionGroupSerializer(data=request.data)

        if data.is_valid():
            data.save()
            return JsonResponse(data=data.data, code="999999", msg="成功")
        else:
            return JsonResponse(data=data.errors, code="999998", msg="失败")

    @swagger_auto_schema(
        operation_summary='权限分组修改',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'id': openapi.Schema(type=openapi.TYPE_STRING, description='id'),
                'permissiongroup_name': openapi.Schema(type=openapi.TYPE_STRING, description='permission_name'),
                'permissiongroup_desc': openapi.Schema(type=openapi.TYPE_STRING, description='permission_desc'),
            }))
    def put(self, request):
        data = JSONParser().parse(request)
        id = data["id"]
        permission = PermissionGroup.objects.get(id=id)
        ser = PermissionGroupSerializer(permission, data=data)
        with transaction.atomic():
            if ser.is_valid():
                ser.save()
                return JsonResponse(data=ser.data, code="999999", msg="成功")
            else:
                return JsonResponse(data=ser.errors, code="999998", msg="失败")

    @swagger_auto_schema(
        operation_summary='权限分组删除',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'id': openapi.Schema(type=openapi.TYPE_STRING, description='id'),

            }))
    def delete(self, request):
        data = JSONParser().parse(request)
        id = data["id"]
        try:
            permission = PermissionGroup.objects.get(id=id)
            permission.delete()
            return JsonResponse(code="999999", msg="成功")
        except:
            return JsonResponse(code="999998", msg="失败")
