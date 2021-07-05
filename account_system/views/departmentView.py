from drf_yasg2 import openapi
from drf_yasg2.utils import swagger_auto_schema
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView
from account_system.models import UserProfile
from account_system.serializers import DepartmentSerializerAdd, DepartmentSerializerQuery
from django.db import transaction
from account_system.models import Department
from django.db.models import Q
from account_system.util import get_code
from system_settings.tools import error_response, success_response


class DepartMentViewSet(APIView):
    authentication_classes = ()
    permission_classes = []

    @swagger_auto_schema(
        operation_summary='获取单个部门数据',
        manual_parameters=[
            openapi.Parameter(name='id', in_=openapi.IN_QUERY, description='部门id',
                              type=openapi.TYPE_STRING),
        ])
    def get(self, request):
        try:
            id = request.GET.get("id", '')
            depart_obj = Department.objects.filter(id=id)
            if not depart_obj:
                return error_response(msg='id错误，无数据')
            depart_serializer = DepartmentSerializerQuery(depart_obj.first())
            return success_response(data=depart_serializer.data, msg='成功')
        except Exception as e:
            return error_response(msg='失败')

    @swagger_auto_schema(
        operation_summary='部门新增',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'department_name': openapi.Schema(type=openapi.TYPE_STRING, description='部门名称'),
                'super_department_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='上级部门id'),
                'remark': openapi.Schema(type=openapi.TYPE_STRING, description='备注'),
            }))
    def post(self, request):
        data = JSONParser().parse(request)
        try:
            data['department_code'] = get_code()
            super_department_id = data.get('super_department_id')
            if super_department_id:
                if not Department.objects.filter(id=super_department_id):
                    return error_response(msg="该上级部门信息不存在!")
                else:
                    data['super_department_name'] = Department.objects.filter(id=super_department_id).first().department_name
                    data['super_department_code'] = Department.objects.filter(id=super_department_id).first().department_code
            depart_obj = DepartmentSerializerAdd(data=data)
            if depart_obj.is_valid():
                depart_obj.save()
                return success_response(data=depart_obj.data, msg="部门新增成功")
            else:
                return error_response(depart_obj.errors)
        except Exception as e:
            return error_response(msg="失败!")

    @swagger_auto_schema(
        operation_summary='部门修改',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='部门id'),
                'department_name': openapi.Schema(type=openapi.TYPE_STRING, description='部门名称'),
                'super_department_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='上级部门id'),
                'remark': openapi.Schema(type=openapi.TYPE_STRING, description='备注'),
            }))
    def put(self, request):
        with transaction.atomic():
            data = JSONParser().parse(request)
            id = data.get('id')
            if not id:
                return error_response(msg="id为空")
            super_department_id = data.get('super_department_id')
            if super_department_id:
                if not Department.objects.filter(id=super_department_id):
                    return error_response(msg="该上级部门信息不存在!")
                else:
                    data['super_department_name'] = Department.objects.filter(id=super_department_id).first().department_name
                    data['super_department_code'] = Department.objects.filter(id=super_department_id).first().department_code

            else:
                if Department.objects.get(id=id).super_department_id:
                    Department.objects.filter(id=id).update(super_department_name='', super_department_code='', super_department_id=None)

            data['department_code'] = get_code()
            depart_obj = Department.objects.filter(id=id)
            if not depart_obj:
                return error_response(msg="找不到对象")

            flag = check_depart_super(depart_obj.first(), super_department_id)
            if flag:  # 修改的上级部门为非子级， 正常修改
                pass
            else:  # 修改的上级部门为子级， 修改当前部门的子级的父级为当前部门的父级
                Department.objects.filter(super_department_id=depart_obj.first().id).update(super_department_id=depart_obj.first().super_department_id)
            put_depart_obj = DepartmentSerializerAdd(instance=depart_obj.first(), data=data)
            if put_depart_obj.is_valid():
                put_depart_obj.save()
                return success_response(data=put_depart_obj.data, msg="成功")
            else:
                return error_response(msg=put_depart_obj.errors)

    @swagger_auto_schema(
        operation_summary='部门 单删群删',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'ids': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_STRING),
                                      description='需要删除的部门id列表 ')
            }))
    def delete(self, request):
        try:
            with transaction.atomic():
                data = JSONParser().parse(request)
                delete_ids = data.get('ids')
                for id in delete_ids:
                    depart_obj = Department.objects.filter(id=id)
                    if depart_obj:
                        flag, msg = check_delete_depart(depart_obj.first())
                        if not flag:
                            raise Exception('ex')
                            return error_response(msg="部门"+msg+"或子部门下存在员工，无法删除!")
                    else:
                        return error_response(msg="数据错误!")
                return success_response(data='', msg='成功')
        except Exception as e:
            if str(e) == 'ex':
                return error_response(msg="失败 , 部门或子部门下存在员工，无法删除!")
            return error_response(msg="失败!")


class DepartMentTreeView(APIView):
    authentication_classes = ()
    permission_classes = []

    @swagger_auto_schema(
        operation_summary='树形部门 /修改部门前调用，根据部门不同获取下拉框数据',
        manual_parameters=[
            openapi.Parameter(name='id', in_=openapi.IN_QUERY, description='部门id /修改传入',
                              type=openapi.TYPE_STRING),
        ])
    def get(self, request):
        try:
            id = request.GET.get("id", None)
            tree_data = []
            if id:
                root_depart_objs = Department.objects.filter(id=id)
            else:
                root_depart_objs = Department.objects.filter(Q(super_department_id__isnull=True)|Q(super_department_id=''))
            for root_depart in root_depart_objs:
                depart_serializer = DepartmentSerializerQuery(root_depart)
                data = depart_serializer.data
                data['children'] = []
                get_depart_tree(data['children'], root_depart)
                tree_data.append(data)
            return success_response(data=tree_data, msg='成功')
        except Exception as e:
            return error_response(msg='失败')


def get_depart_tree(data_list, depart_obj):
    depart_objs = Department.objects.filter(super_department_id=depart_obj.id)
    if depart_objs:
        for depart_obj in depart_objs:
            # if depart_obj.super_department_id == ex_id:
            #     continue
            depart_serializer = DepartmentSerializerQuery(depart_obj)
            data = depart_serializer.data
            data['children'] = []
            get_depart_tree(data['children'], depart_obj)
            data_list.append(data)


def check_delete_depart(depart_object):
    if UserProfile.objects.filter(department=depart_object.id):
        return False, depart_object.department_name
    depart_objs = Department.objects.filter(super_department_id=depart_object.id)
    for depart_obj in depart_objs:
        flag, msg = check_delete_depart(depart_obj)
        if not flag:
            return False, depart_obj.department_name
    depart_object.delete()
    return True, ''


def check_depart_super(depart_obj, change_super_department_id):
    if depart_obj.id == change_super_department_id:
        return False
    depart_objs = Department.objects.filter(super_department_id=depart_obj.id)
    for depart_obj in depart_objs:
        flag = check_depart_super(depart_obj, change_super_department_id)
        if not flag:
            return False
    return True
