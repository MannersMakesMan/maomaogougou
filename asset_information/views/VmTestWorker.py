import redis
from drf_yasg2 import openapi
from drf_yasg2.utils import swagger_auto_schema
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView

from asset_information.models import TestVmWorker
from asset_information.serializers import VmSerializerAdd, VmTestWorkerSerializerAdd
from automated_testing.common.api_response import JsonResponse
from common.redis_pool import redis_pool


class VmTestWorkerTreeView(APIView):
    authentication_classes = ()
    permission_classes = []

    @swagger_auto_schema(
        operation_summary='测试执行机 集群&单机 树形结构查询'
    )
    def get(self, request):
        """测试执行机 集群&单机 树形结构查询 无参数"""
        # colonys = TestVmWorker.objects.all().values_list('cluster_name').distinct()
        # colonys = list(set([i[0] for i in colonys]))
        # vm_worker_tree = []
        #
        # for colony in colonys:
        #     colony_tree = {}
        #     colony_tree['label'] = colony
        #     colony_tree['children'] = [{
        #         "label": i.virtual_machine.Virtual_machine_IP,
        #         "id": i.id
        #     } for i in TestVmWorker.objects.filter(cluster_name=colony)]
        #     vm_worker_tree.append(colony_tree)
        try:
            vm_worker_tree = [{"label": i.virtual_machine.Virtual_machine_IP, "id": i.id} for i in TestVmWorker.objects.all()]
        except Exception as e:
            vm_worker_tree = []


        return JsonResponse(data=vm_worker_tree, code="999999", msg="成功!")


class VmTestWorker(APIView):
    authentication_classes = ()
    permission_classes = []

    @swagger_auto_schema(
        operation_summary='测试执行机 增加',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'virtual_machine': openapi.Schema(type=openapi.TYPE_INTEGER, description='虚拟机id'),
                'cluster_name': openapi.Schema(type=openapi.TYPE_STRING, description='集群名称'),
                'machine_description': openapi.Schema(type=openapi.TYPE_STRING, description='执行机使用描述'),
                'testing_phase': openapi.Schema(type=openapi.TYPE_INTEGER, description='测试阶段'),
                'browser_type': openapi.Schema(type=openapi.TYPE_INTEGER, description='浏览器类型'),
                'browser_version': openapi.Schema(type=openapi.TYPE_STRING, description='浏览器版本'),
                'test_owner': openapi.Schema(type=openapi.TYPE_INTEGER, description='管理责任人'),
                'max_parallel_task': openapi.Schema(type=openapi.TYPE_INTEGER, description='最大并行任务数量'),
            }))
    def post(self, request):
        """测试执行机 增加 此接口需要先拉取表单数据字典"""
        data = JSONParser().parse(request)
        vm_worker_serializer = VmTestWorkerSerializerAdd(data=data)
        if vm_worker_serializer.is_valid():
            vm_worker_serializer.save()
            redis_conn = redis.Redis(connection_pool=redis_pool)  # redis链接
            ip = vm_worker_serializer.validated_data['virtual_machine'].Virtual_machine_IP
            hmset_data = {"{}_worker{}".format(ip, i): 'usable' for i in range(1, vm_worker_serializer.validated_data['max_parallel_task'])}
            redis_conn.hmset(ip, hmset_data)

            return JsonResponse(code="999999", msg="成功")
        else:
            return JsonResponse(msg=vm_worker_serializer.errors, code="999998")


