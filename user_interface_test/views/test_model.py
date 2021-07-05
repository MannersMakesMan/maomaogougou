# -*- coding: utf-8 -*-
import hashlib

from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q
from django.forms import model_to_dict
from drf_yasg2.utils import swagger_auto_schema
from drf_yasg2 import openapi
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView

from account_system.models import UserProfile
from account_system.serializers import UserSerializerQuery
from account_system.tools import get_real_name
from system_settings.models import DataDictionary, Dataexplain, Project
from system_settings.serializers import ProjectSerializerQuery, ProjectSerializerAdd
from system_settings.tools import error_response, success_response
from user_interface_test.models import CommonParams, TestAppModel, TestCase
from user_interface_test.serializers import UiTestParamsSerializerQuery, UiTestParamsSerializerAdd, \
    TestModelSerializerAdd, TestModelSelectSerializerQuery, TestModelSerializerQuery
from zy_api_testing.tools import DelException, api_list_query


class TestModelQueryView(APIView):
    authentication_classes = ()
    permission_classes = []

    @swagger_auto_schema(
        operation_summary='应用模块 树形结构全量查询 项目-模块-页面',
        manual_parameters=[
            openapi.Parameter(name='AUTHORIZATION', in_=openapi.IN_HEADER, description='登录验证', type=openapi.TYPE_STRING),
            openapi.Parameter(name='model_level', in_=openapi.IN_QUERY, description='模块级别 0/1/2 项目/模块/页面',
                              type=openapi.TYPE_INTEGER),
            openapi.Parameter(name='id', in_=openapi.IN_QUERY, description='id',
                              type=openapi.TYPE_INTEGER),
        ])
    def get(self, request):
        def get_project_manager(obj):
            if obj.project_manager:
                return obj.project_manager.Real_name
            else:
                return None

        def get_Test_Leader(obj):
            if obj.Test_Leader:
                return obj.Test_Leader.Real_name
            else:
                return None

        def get_dev_user(obj):
            if obj.dev_user:
                data = UserSerializerQuery(UserProfile.objects.filter(id=obj.dev_user).first()).data
                return data.get('Real_name')
            else:
                return None

        def get_test_user(obj):
            if obj.test_user:
                data = UserSerializerQuery(UserProfile.objects.filter(id=obj.test_user).first()).data
                return data.get('Real_name')
            else:
                return None
        try:
            id = request.GET.get('id', '')
            model_level = request.GET.get('model_level', '')
            return_data = []
            if not (id and model_level):
                project_objs = Project.objects.all()
                for project_obj in project_objs:
                    model_dic_ls = []
                    entry_name = project_obj.entry_name
                    project_dic = {
                        "id": project_obj.id,
                        "hash_key": hashlib.md5("project_{}".format(project_obj.id).encode('utf8')).hexdigest(),
                        "entry_name": entry_name,
                        "model_name": "",
                        "page_name": "",
                        "test_leader": get_Test_Leader(project_obj),
                        "dev_leader": get_project_manager(project_obj),
                        "create_time": str(project_obj.create_time).split(".")[0],
                        "update_time": str(project_obj.update_time).split(".")[0],
                        "update_user": project_obj.update_user,
                        "remark": project_obj.remark,
                        "children": model_dic_ls
                        }
                    return_data.append(project_dic)
                    for model_obj in TestAppModel.objects.filter(super_id=project_obj.id, model_level=1):
                        page_dic_ls = []
                        model_name = model_obj.model_name
                        model_dic = {
                            "id": model_obj.id,
                            "hash_key": hashlib.md5("model_{}".format(model_obj.id).encode('utf8')).hexdigest(),
                            "entry_name": entry_name,
                            "model_name": model_name,
                            "page_name": "",
                            "test_leader": get_test_user(model_obj),
                            "dev_leader": get_dev_user(model_obj),
                            "create_time": str(model_obj.create_time).split(".")[0],
                            "update_time": str(model_obj.update_time).split(".")[0],
                            "update_user": model_obj.update_user,
                            "remark": model_obj.remark,
                            "children": page_dic_ls
                        }
                        model_dic_ls.append(model_dic)
                        for page_obj in TestAppModel.objects.filter(super_id=model_obj.id, model_level=2):
                            page_name = page_obj.model_name
                            page_dic = {
                                "id": page_obj.id,
                                "hash_key": hashlib.md5("page_{}".format(page_obj.id).encode('utf8')).hexdigest(),
                                "entry_name": entry_name,
                                "model_name": model_name,
                                "page_name": page_name,
                                "test_leader": get_test_user(page_obj),
                                "dev_leader": get_dev_user(page_obj),
                                "create_time": str(page_obj.create_time).split(".")[0],
                                "update_time": str(page_obj.update_time).split(".")[0],
                                "update_user": page_obj.update_user,
                                "remark": page_obj.remark,
                                "children": []
                            }
                            page_dic_ls.append(page_dic)
            elif model_level == "0":
                project_objs = Project.objects.filter(id=id)
                for project_obj in project_objs:
                    model_dic_ls = []
                    entry_name = project_obj.entry_name
                    project_dic = {
                        "id": project_obj.id,
                        "hash_key": hashlib.md5("project_{}".format(project_obj.id).encode('utf8')).hexdigest(),
                        "entry_name": entry_name,
                        "model_name": "",
                        "page_name": "",
                        "test_leader": get_Test_Leader(project_obj),
                        "dev_leader": get_project_manager(project_obj),
                        "create_time": str(project_obj.create_time).split(".")[0],
                        "update_time": str(project_obj.update_time).split(".")[0],
                        "update_user": project_obj.update_user,
                        "remark": project_obj.remark,
                        "children": model_dic_ls
                        }
                    return_data.append(project_dic)
                    for model_obj in TestAppModel.objects.filter(super_id=project_obj.id, model_level=1):
                        page_dic_ls = []
                        model_name = model_obj.model_name
                        model_dic = {
                            "id": model_obj.id,
                            "hash_key": hashlib.md5("model_{}".format(model_obj.id).encode('utf8')).hexdigest(),
                            "entry_name": entry_name,
                            "model_name": model_name,
                            "page_name": "",
                            "test_leader": get_test_user(model_obj),
                            "dev_leader": get_dev_user(model_obj),
                            "create_time": str(model_obj.create_time).split(".")[0],
                            "update_time": str(model_obj.update_time).split(".")[0],
                            "update_user": model_obj.update_user,
                            "remark": model_obj.remark,
                            "children": page_dic_ls
                        }
                        model_dic_ls.append(model_dic)
                        for page_obj in TestAppModel.objects.filter(super_id=model_obj.id, model_level=2):
                            page_name = page_obj.model_name
                            page_dic = {
                                "id": page_obj.id,
                                "hash_key": hashlib.md5("page_{}".format(page_obj.id).encode('utf8')).hexdigest(),
                                "entry_name": entry_name,
                                "model_name": model_name,
                                "page_name": page_name,
                                "test_leader": get_test_user(page_obj),
                                "dev_leader": get_dev_user(page_obj),
                                "create_time": str(page_obj.create_time).split(".")[0],
                                "update_time": str(page_obj.update_time).split(".")[0],
                                "update_user": page_obj.update_user,
                                "remark": page_obj.remark,
                                "children": []
                            }
                            page_dic_ls.append(page_dic)
            elif model_level == "1":
                model_dic_ls = []
                model_obj = TestAppModel.objects.filter(id=id, model_level=model_level).first()
                if not model_obj:
                    return error_response(msg="未找到此模块")
                entry_name = Project.objects.get(id=model_obj.super_id).entry_name
                model_name = model_obj.model_name
                page_dic_ls = []
                model_dic = {
                    "id": model_obj.id,
                    "hash_key": hashlib.md5("model_{}".format(model_obj.id).encode('utf8')).hexdigest(),
                    "entry_name": entry_name,
                    "model_name": model_name,
                    "page_name": "",
                    "test_leader": get_test_user(model_obj),
                    "dev_leader": get_dev_user(model_obj),
                    "create_time": str(model_obj.create_time).split(".")[0],
                    "update_time": str(model_obj.update_time).split(".")[0],
                    "update_user": model_obj.update_user,
                    "remark": model_obj.remark,
                    "children": page_dic_ls
                }
                model_dic_ls.append(model_dic)
                for page_obj in TestAppModel.objects.filter(super_id=model_obj.id, model_level=2):
                    page_name = page_obj.model_name
                    page_dic = {
                        "id": page_obj.id,
                        "hash_key": hashlib.md5("page_{}".format(page_obj.id).encode('utf8')).hexdigest(),
                        "entry_name": entry_name,
                        "model_name": model_name,
                        "page_name": page_name,
                        "test_leader": get_test_user(page_obj),
                        "dev_leader": get_dev_user(page_obj),
                        "create_time": str(page_obj.create_time).split(".")[0],
                        "update_time": str(page_obj.update_time).split(".")[0],
                        "update_user": page_obj.update_user,
                        "remark": page_obj.remark,
                        "children": []
                    }
                    page_dic_ls.append(page_dic)
                return_data = model_dic_ls
            elif model_level == "2":
                page_obj = TestAppModel.objects.filter(id=id, model_level=model_level).first()
                if not page_obj:
                    return error_response(msg="未找到此页面")
                model_obj = TestAppModel.objects.get(id=page_obj.super_id)
                model_name = model_obj.model_name
                entry_name = Project.objects.get(id=model_obj.super_id).entry_name
                page_name = page_obj.model_name
                page_dic_ls = []
                page_dic = {
                    "id": page_obj.id,
                    "hash_key": hashlib.md5("page_{}".format(page_obj.id).encode('utf8')).hexdigest(),
                    "entry_name": entry_name,
                    "model_name": model_name,
                    "page_name": page_name,
                    "test_leader": get_test_user(page_obj),
                    "dev_leader": get_dev_user(page_obj),
                    "create_time": str(page_obj.create_time).split(".")[0],
                    "update_time": str(page_obj.update_time).split(".")[0],
                    "update_user": page_obj.update_user,
                    "remark": page_obj.remark,
                    "children": []
                }
                page_dic_ls.append(page_dic)
                return_data = page_dic_ls
            return success_response(msg="成功", data=return_data)
        except Exception as _:
            return error_response('失败!')


class TestModelAdd(APIView):
    authentication_classes = ()
    permission_classes = []

    @swagger_auto_schema(
        operation_summary='应用模块 新增',
        manual_parameters=[
            openapi.Parameter(name='AUTHORIZATION', in_=openapi.IN_HEADER, description='登录验证', type=openapi.TYPE_STRING), ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'model_level': openapi.Schema(type=openapi.TYPE_INTEGER, description='模块级别 0/1/2 项目/模块/页面'),
                'super_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='上级id'),
                'model_name': openapi.Schema(type=openapi.TYPE_STRING, description='模块名'),
                'dev_user': openapi.Schema(type=openapi.TYPE_INTEGER, description='开发负责人id'),
                'test_user': openapi.Schema(type=openapi.TYPE_INTEGER, description='测试负责人id'),
                'remark': openapi.Schema(type=openapi.TYPE_STRING, description='备注')
            }
        )
    )
    def post(self, request):
        """应用模块 增加"""
        with transaction.atomic():
            try:
                data = JSONParser().parse(request)
                data['update_user'] = get_real_name(request)
                if data['model_level'] == 0:
                    data['project_manager'] = data.pop('dev_user')
                    data['Test_Leader'] = data.pop('test_user')
                    del data['super_id']
                    test_model_serializer = ProjectSerializerAdd(data=data)
                    if test_model_serializer.is_valid():
                        model_obj = test_model_serializer.save()
                        return success_response(data=model_obj, msg='新增项目成功！')  # do
                    else:
                        return error_response(msg=test_model_serializer.errors)
                else:
                    if data['model_level'] == 2:
                        data['model_name'] = data.pop('page_name')
                    test_model_serializer = TestModelSerializerAdd(data=data)
                    if test_model_serializer.is_valid():
                        model_obj = test_model_serializer.save()
                        if data['model_level'] == 1:
                            return success_response(data=TestModelSerializerQuery(model_obj).data, msg='新增模块成功！')
                        else:
                            return success_response(data=TestModelSerializerQuery(model_obj).data, msg='新增页面成功！')
                    else:
                        return error_response(msg=test_model_serializer.errors)
            except Exception as _:
                return error_response('失败！！！')

    @swagger_auto_schema(
        operation_summary='应用模块 修改',
        manual_parameters=[
            openapi.Parameter(name='AUTHORIZATION', in_=openapi.IN_HEADER, description='登录验证',type=openapi.TYPE_STRING), ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='id'),
                'model_level': openapi.Schema(type=openapi.TYPE_INTEGER, description='模块级别 0/1/2 项目/模块/页面'),
                'model_name': openapi.Schema(type=openapi.TYPE_STRING, description='模块名'),
                'dev_user': openapi.Schema(type=openapi.TYPE_STRING, description='开发负责人id'),
                'test_user': openapi.Schema(type=openapi.TYPE_STRING, description='测试负责人id'),
                'remark': openapi.Schema(type=openapi.TYPE_STRING, description='备注')
            }
        )
    )
    def put(self, request):
        """应用模块 修改"""
        with transaction.atomic():
            try:
                data = JSONParser().parse(request)
                id = data['id']
                data['update_user'] = get_real_name(request)
                if data['model_level'] == 0:
                    data['project_manager'] = data.pop('dev_user')
                    data['Test_Leader'] = data.pop('test_user')
                    project_obj = Project.objects.filter(id=id).first()
                    if not project_obj:
                        return error_response('未找到此项目！')
                    test_model_serializer = ProjectSerializerAdd(instance=project_obj, data=data)
                    if test_model_serializer.is_valid():
                        project_obj = test_model_serializer.save()
                        return success_response(data=ProjectSerializerQuery(project_obj).data, msg='新增项目成功！')
                    else:
                        return error_response(msg=test_model_serializer.errors)
                else:
                    model_obj = TestAppModel.objects.filter(id=id).first()
                    if not model_obj:
                        if data['model_level'] == 1:
                            return error_response('未找到此模块！')
                        else:
                            return error_response('未找到此页面！')
                    test_model_serializer = TestModelSerializerAdd(instance=model_obj, data=data)
                    if data['model_level'] == 2:
                        data['model_name'] = data.pop('page_name')
                    if test_model_serializer.is_valid():
                        model_obj = test_model_serializer.save()
                        if data['model_level'] == 1:
                            return success_response(data=TestModelSerializerQuery(model_obj).data, msg='新增模块成功！')
                        else:
                            return success_response(data=TestModelSerializerQuery(model_obj).data, msg='新增页面成功！')
                    else:
                        return error_response(msg=test_model_serializer.errors)
            except Exception as _:
                return error_response('失败！')

    @swagger_auto_schema(
        operation_summary='应用模块 删除',
        manual_parameters=[openapi.Parameter(name='AUTHORIZATION', in_=openapi.IN_HEADER, description='登录验证', type=openapi.TYPE_STRING),],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='需要删除的应用模块id'),
            }))
    def delete(self, request):
        """应用模块 单删群删"""
        try:
            with transaction.atomic():
                data = JSONParser().parse(request)
                delete_id = data['id']
                test_model_obj = TestAppModel.objects.filter(id=delete_id).first()
                if test_model_obj:
                    if test_model_obj.model_level == 1:
                        # 删除模块
                        page_objs = TestAppModel.objects.filter(super_id=delete_id, model_level=2)
                        # 检查模块下的页面 是否关联测试用例
                        for page_obj in page_objs:
                            if TestCase.objects.filter(test_app_model_id=page_obj.id):
                                raise DelException('TestCase')
                        for page_obj in page_objs:
                            page_obj.delete()
                    else:
                        # 删除页面 盛大
                        # 检查页面 是否关联测试用例
                        if TestCase.objects.filter(test_app_model_id=test_model_obj.id):
                            raise DelException('TestCase')
                    test_model_obj.delete()
                    return success_response(msg="成功!")
                else:
                    return error_response(msg="未找到此模块!")
        except Exception as _e:
            if str(_e) == "TestCase":
                return error_response(msg="无法删除 页面下下已关联测试用例!")
            return error_response(msg="失败!")

    @swagger_auto_schema(
        operation_summary='应用模块/界面下拉, 用例类型下拉框接口',
        manual_parameters=[openapi.Parameter(name='AUTHORIZATION', in_=openapi.IN_HEADER, description='登录验证', type=openapi.TYPE_STRING), ],)
    def get(self, request):
        try:
            test_model_objs = TestAppModel.objects.filter(model_level=2)
            return_data = TestModelSelectSerializerQuery(test_model_objs, many=True).data
            data_id = Dataexplain.objects.get(dictionary_code='A0000002').id
            case_type_list = [i.get('dictionary_item1') for i in list(DataDictionary.objects.filter(Dataexplain_id=data_id).values('dictionary_item1'))]
            response = {
                'test_models': return_data,
                'case_type_list': case_type_list
            }
            return success_response(data=response, msg='成功')
        except Exception as e:
            return error_response('失败')
