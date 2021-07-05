from drf_yasg2 import openapi
from drf_yasg2.utils import swagger_auto_schema
from rest_framework.views import APIView

from account_system.models import UserProfile, Department
from asset_information.models import OS_TYPE, VM_PURPOSE, Server
from asset_information.serializers import UserLsSerializer, DepartMentLsSerializer, ServerSerializer
from automated_testing.common.api_response import JsonResponse
from system_settings.models import Project, Test_type, Testing_phase, BROWSER_TYPE, Task_period_type, Environment, \
    JOB_TYPE
from system_settings.serializers import ProjectSerializerQuery, EnvironmentSerializerForeignQuery
from zy_api_testing.models import PARAMS_POSITION_LIST, REQUEST_METHOD, DEPRECATED_LIST
from zy_api_testing.views.api_manage import ASSERT_TYPE_SELECT, PARAMS_TYPE_SELECT, ASSERT_DATA_TYPE_SELECT
from zy_api_testing.views.scene_api_conf import BOOL_VALUE_SELECT


class ParamDicView(APIView):
    authentication_classes = ()
    permission_classes = []

    @swagger_auto_schema(
        operation_summary='公共请求 表单数据字典',
        manual_parameters=[
            openapi.Parameter(name='AUTHORIZATION', in_=openapi.IN_HEADER, description='登录验证', type=openapi.TYPE_STRING),
            openapi.Parameter(name='form_data', in_=openapi.IN_QUERY, description='数据字典类型 Server/VirtualMachine/VirtualMachineLs/projectEnvironment/AddApiNeedParams/Environment/perForm/TaskPeriod/SelectEnvironment/ApiSceneNeed', type=openapi.TYPE_STRING),
        ])
    def get(self, request):
        """增加&修改数据 表单数据字典"""
        form_data = request.GET.get('form_data')

        if form_data == 'Server':
            # 服务器增加 修改 数据字典
            user_obj = UserProfile.objects.all()
            user_serializer = UserLsSerializer(user_obj, many=True)
            department = Department.objects.all()
            department_serializer = DepartMentLsSerializer(department, many=True)
            return_data = {
                "person_liable": user_serializer.data,
                "user_department": department_serializer.data,
                "operating_system": [{'id': i[0], 'name': i[1]}for i in OS_TYPE],
            }
        elif form_data == 'VirtualMachine':
            user_obj = UserProfile.objects.all()
            user_serializer = UserLsSerializer(user_obj, many=True)
            server_obj = Server.objects.all()
            server_serializer = ServerSerializer(server_obj, many=True)
            return_data = {
                'server': server_serializer.data,
                'operating_system': [{'id': i[0], 'name': i[1]}for i in OS_TYPE],
                'purpose': [{'id': i[0], 'name': i[1]}for i in VM_PURPOSE],
                'person_liable': user_serializer.data,
                'project_manager': user_serializer.data,
            }
        elif form_data == 'VirtualMachineLs':
            return_data = {
                'purpose': [{'id': i[0], 'name': i[1]} for i in VM_PURPOSE],
                'operating_system': [{'id': i[0], 'name': i[1]} for i in OS_TYPE],
            }
        elif form_data == 'projectEnvironment':
            user_obj = UserProfile.objects.all()
            user_serializer = UserLsSerializer(user_obj, many=True)
            return_data = {
                'test_leader': user_serializer.data,
                'project_manager': user_serializer.data,
            }
        elif form_data == 'Environment':
            # user_obj = UserProfile.objects.all()
            # user_serializer = UserLsSerializer(user_obj, many=True)
            project_obj = Project.objects.all()
            project_serializer = ProjectSerializerQuery(project_obj, many=True)
            return_data = {
                # 'test_leader': user_serializer.data,
                # 'project_manager': user_serializer.data,
                'project_data': project_serializer.data,
                'test_type': [{'id': i[0], 'label':i[1]} for i in Test_type],
                'Testing_phase': [{'id': i[0], 'label': i[1]} for i in Testing_phase]
            }
        elif form_data == 'perForm':
            project_obj = Project.objects.all()
            project_serializer = ProjectSerializerQuery(project_obj, many=True)
            return_data = {
                'browser_type': [{'id': i[0], 'name': i[1]} for i in BROWSER_TYPE],
                'project_data': project_serializer.data,
                'operating_system': [{'id': i[0], 'name': i[1]} for i in OS_TYPE],
            }
        elif form_data == 'TaskPeriod':
            return_data = {
                'Task_period_type': [{'id': i[0], 'name': i[1]} for i in Task_period_type],
                'job_type': [{'id': i[0], 'name': i[1]} for i in JOB_TYPE],
            }
        elif form_data == 'SelectEnvironment':
            environment_obj = Environment.objects.all()
            environment_serializer = EnvironmentSerializerForeignQuery(environment_obj, many=True)
            return_data = {
                'environment_select_list': environment_serializer.data,
            }
        elif form_data == 'ApiSceneNeed':
            # environment_obj = Environment.objects.all()
            # environment_serializer = EnvironmentSerializerForeignQuery(environment_obj, many=True)
            return_data = {
                'assert_type_select': ASSERT_TYPE_SELECT,
                'params_type_select': PARAMS_TYPE_SELECT,
                'assert_data_type_select': ASSERT_DATA_TYPE_SELECT,
                'bool_value_select': BOOL_VALUE_SELECT
            }
        elif form_data == 'AddApiNeedParams':
            # environment_obj = Environment.objects.all()
            # environment_serializer = EnvironmentSerializerForeignQuery(environment_obj, many=True)
            return_data = {
                'params_position_list': PARAMS_POSITION_LIST,
                'request_method': REQUEST_METHOD,
                'deprecated_list': [{'id': i[0], 'name': i[1]} for i in DEPRECATED_LIST]
            }
        else:
            return JsonResponse(code="999996", msg="参数有误!")

        return JsonResponse(data=return_data, code="999999", msg='成功')
