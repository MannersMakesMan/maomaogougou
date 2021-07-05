from django.core.paginator import Paginator
from django.db.models import Q
from drf_yasg2 import openapi
from drf_yasg2.utils import swagger_auto_schema
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView

from asset_information.models import VmServer, Server
from asset_information.serializers import VmSerializerAdd, VmSerializerQuery
from automated_testing.common.api_response import JsonResponse
from common.thread_task import thread_task_main
from common.tools import check_ip


class VirtualMachineView(APIView):
    authentication_classes = ()
    permission_classes = []

    def check_vm_ping_task_func(self, server_id):
        # 多线程 服务器检测 任务执行函数
        vm_obj = VmServer.objects.filter(id=server_id).first()
        if vm_obj:
            vm_ip = vm_obj.Virtual_machine_IP
            if check_ip(vm_ip):
                vm_obj.Usage_status = 1
            else:
                vm_obj.Usage_status = 0
            vm_obj.save()

    @swagger_auto_schema(
        operation_summary='虚拟机 增加',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'server': openapi.Schema(type=openapi.TYPE_INTEGER, description='所属服务器id'),
                'Virtual_machine_IP': openapi.Schema(type=openapi.TYPE_STRING, description='虚拟机ip'),
                'Virtual_machine_username': openapi.Schema(type=openapi.TYPE_STRING, description='虚拟机账号'),
                'Virtual_machine_password': openapi.Schema(type=openapi.TYPE_STRING, description='虚拟机密码 base64加密后的'),
                'entry_name': openapi.Schema(type=openapi.TYPE_STRING, description='项目名称'),
                'project_manager': openapi.Schema(type=openapi.TYPE_INTEGER, description='项目经理id'),
                'operating_system': openapi.Schema(type=openapi.TYPE_INTEGER, description='操作系统id'),
                'purpose': openapi.Schema(type=openapi.TYPE_INTEGER, description='虚拟机用途id'),
                'Virtual_machine_CPU': openapi.Schema(type=openapi.TYPE_INTEGER, description='虚拟机CPU（核）'),
                'Virtual_machine_memory': openapi.Schema(type=openapi.TYPE_INTEGER, description='虚拟机内存（G）'),
                'Virtual_machine_hard_disk': openapi.Schema(type=openapi.TYPE_INTEGER, description='虚拟机硬盘（G）'),
                'person_liable': openapi.Schema(type=openapi.TYPE_INTEGER, description='管理责任人'),
            }))
    def post(self, request):
        """虚拟机 增加 此接口需要先拉取表单数据字典"""
        data = JSONParser().parse(request)
        vm_serializer = VmSerializerAdd(data=data)
        if vm_serializer.is_valid():
            vm_serializer.save()
            return JsonResponse(code="999999", msg="成功")
        else:
            return JsonResponse(msg=vm_serializer.errors, code="999998")

    @swagger_auto_schema(
        operation_summary='虚拟机 单删群删',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'ids': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_STRING),
                                      description='需要删除的虚拟机id列表 ')
            }))
    def delete(self, request):
        """虚拟机 单删群删"""
        data = JSONParser().parse(request)
        delete_ids = data['ids']
        try:
            for id in delete_ids:
                vm_obj = VmServer.objects.filter(id=id).first()
                if vm_obj:
                    server_obj = vm_obj.server
                    server_obj.vm_num -= 1
                    server_obj.save()
                    vm_obj.delete()

                else:
                    return JsonResponse(code="999998", msg="数据错误!")
        except Exception as e:
            JsonResponse(code="999998", msg="失败!")
        return JsonResponse(code="999999", msg="成功!")

        # try:  # 数据如果有误，数据库执行会出错
        #     rows = VmServer.objects.filter(pk__in=delete_ids).delete()
        # except Exception as e:
        #     return JsonResponse(code="999998", msg="数据错误!")

        # if rows:
        #     return JsonResponse(code="999999", msg="删除成功!")
        # JsonResponse(code="999998", msg="失败!")

    @swagger_auto_schema(
        operation_summary='虚拟机 列表页(多条件筛选)',
        manual_parameters=[
            openapi.Parameter(name='page', in_=openapi.IN_QUERY, description='页码', type=openapi.TYPE_STRING),
            openapi.Parameter(name='page_size', in_=openapi.IN_QUERY, description='数量', type=openapi.TYPE_STRING),
            openapi.Parameter(name='operating_system', in_=openapi.IN_QUERY, description='虚拟机操作系统id', type=openapi.TYPE_STRING),
            openapi.Parameter(name='purpose', in_=openapi.IN_QUERY, description='虚拟机用途id', type=openapi.TYPE_STRING),
            openapi.Parameter(name='person_liable', in_=openapi.IN_QUERY, description='管理责任人姓名 模糊', type=openapi.TYPE_STRING),
            openapi.Parameter(name='entry_name', in_=openapi.IN_QUERY, description='项目名称', type=openapi.TYPE_STRING),

        ])
    def get(self, request):
        """虚拟机 群查 列表页(多条件筛选)"""
        page_size = int(request.GET.get("page_size", 20))
        page = int(request.GET.get("page", 1))

        queryset = VmServer.objects.all()
        operating_system = request.GET.get("operating_system")  # 虚拟机操作系统
        purpose = request.GET.get("purpose")  # 虚拟机用途
        person_liable = request.GET.get("person_liable")  # 管理责任人
        entry_name = request.GET.get("entry_name")  # 项目名称
        aQ = Q()
        if operating_system:  # 多字段筛选
            aQ.add(Q(operating_system=int(operating_system)), Q.AND)
        if purpose:
            aQ.add(Q(purpose=int(purpose)), Q.AND)
        if person_liable:
            aQ.add(Q(person_liable__Real_name__contains=person_liable), Q.AND)
        if entry_name:
            aQ.add(Q(entry_name__contains=entry_name), Q.AND)

        queryset = queryset.filter(aQ).order_by("id")

        paginator = Paginator(queryset, page_size)  # paginator对象
        total = len(queryset)  # 总数量
        try:
            obm = paginator.page(page)
            vm_serialize = VmSerializerQuery(obm, many=True)
            return_data = vm_serialize.data
            thread_task_main([i['id'] for i in return_data], 3, self.check_vm_ping_task_func)  # 执行批量ip检测

        except Exception as _e:
            return_data = []

        return JsonResponse(data={"data": return_data,
                                  "page": page,
                                  "total": total
                                  }, code="999999", msg="成功")


class VirtualMachineDetailView(APIView):
    authentication_classes = ()
    permission_classes = []

    @swagger_auto_schema(
        operation_summary='虚拟机信息查询 单查',
    )
    def get(self, request, pk):
        """虚拟机信息查询 单查"""
        if pk:
            vm_obj = VmServer.objects.filter(pk=pk).first()
            if vm_obj:
                vm_serializer = VmSerializerQuery(vm_obj)
                return JsonResponse(data=vm_serializer.data, code="999999", msg="成功!")
            return JsonResponse(code="999998", msg="无数据!")
        else:
            return JsonResponse(code="999998", msg="id为空!")

    @swagger_auto_schema(
        operation_summary='虚拟机信息 修改',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'server': openapi.Schema(type=openapi.TYPE_INTEGER, description='所属服务器id'),
                'Virtual_machine_IP': openapi.Schema(type=openapi.TYPE_STRING, description='虚拟机ip'),
                'Virtual_machine_username': openapi.Schema(type=openapi.TYPE_STRING, description='虚拟机账号'),
                'Virtual_machine_password': openapi.Schema(type=openapi.TYPE_STRING, description='虚拟机密码 base64加密后的'),
                'entry_name': openapi.Schema(type=openapi.TYPE_STRING, description='项目名称'),
                'project_manager': openapi.Schema(type=openapi.TYPE_INTEGER, description='项目经理id'),
                'operating_system': openapi.Schema(type=openapi.TYPE_INTEGER, description='操作系统id'),
                'purpose': openapi.Schema(type=openapi.TYPE_INTEGER, description='虚拟机用途id'),
                'Virtual_machine_CPU': openapi.Schema(type=openapi.TYPE_INTEGER, description='虚拟机CPU（核）'),
                'Virtual_machine_memory': openapi.Schema(type=openapi.TYPE_INTEGER, description='虚拟机内存（G）'),
                'Virtual_machine_hard_disk': openapi.Schema(type=openapi.TYPE_INTEGER, description='虚拟机硬盘（G）'),
                'person_liable': openapi.Schema(type=openapi.TYPE_INTEGER, description='管理责任人id'),
            }))
    def put(self, request, pk):
        """'虚拟机信息 修改 此接口需要先拉取表单数据字典"""
        if pk:
            data = JSONParser().parse(request)
            vm_obj = VmServer.objects.filter(id=pk).first()
            if vm_obj:
                vm_serializer = VmSerializerAdd(instance=vm_obj, data=data)
                if vm_serializer.is_valid():
                    vm_serializer.save()
                    return JsonResponse(code="999999", msg="成功!")
                else:
                    return JsonResponse(msg=vm_serializer.errors, code="999998")
            return JsonResponse(code="999998", msg="无数据!")
        else:
            return JsonResponse(code="999998", msg="id为空!")
