from drf_yasg2 import openapi
from drf_yasg2.utils import swagger_auto_schema
from rest_framework.views import APIView

from account_system.models import PermissionGroup, Position
from account_system.serializers import PermissionGroupLsSerializer, PositionLsSerializerQuery
from automated_testing.common.api_response import JsonResponse


class ParamDicView(APIView):
    authentication_classes = ()
    permission_classes = []

    @swagger_auto_schema(
        operation_summary='公共请求 表单数据字典',
        manual_parameters=[
            openapi.Parameter(name='HTTP_AUTHORIZATION', in_=openapi.IN_HEADER, description='登录验证',
                              type=openapi.TYPE_STRING),
            openapi.Parameter(name='form_data', in_=openapi.IN_QUERY, description='数据字典类型 user_add/', type=openapi.TYPE_STRING),
        ])
    def get(self, request):
        """增加&修改数据 表单数据字典"""
        form_data = request.GET.get('form_data')
        if form_data == 'user_add':
            # 用户修改下拉框
            permission_group_obj = PermissionGroup.objects.all()
            permission_group_serializer = PermissionGroupLsSerializer(permission_group_obj, many=True)
            position_obj = Position.objects.all()
            position_serializer = PositionLsSerializerQuery(position_obj, many=True)
            return_data = {
                "permission_group": permission_group_serializer.data,
                "position": position_serializer.data,
            }
        else:
            return JsonResponse(code="999996", msg="参数有误!")

        return JsonResponse(data=return_data, code="999999", msg='成功')



