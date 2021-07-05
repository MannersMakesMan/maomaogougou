import logging
import threading
import re
import os
from datetime import datetime

import redis
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
from drf_yasg2 import openapi
from drf_yasg2.utils import swagger_auto_schema
from rest_framework.authentication import TokenAuthentication
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView

from automated_testing.common.api_response import JsonResponse
from common.redis_pool import redis_pool
from common.ssh_oprerations import ssh_oprerations
from test_exe_conf.models import UiTestConfig, ApiTestConfig
from test_exe_conf.serializers import UiTestConfigSerializers, ApiTestConfigSerializers, UiTestConfigListSerializers, \
    ApiTestConfigListSerializers, UiTestReportSerializers, ApiTestReportSerializers
from basic_configuration.settings import AUTOMATED_UI_TESTING_CONF, AUTOMATED_API_TESTING_CONF

logger = logging.getLogger(__name__)  # 这里使用 __name__ 动态搜索定义的 logger 配置，这里有一个层次关系的知识点。


class TestTask(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = ()
    test_type_ls = ['ui', 'api']

    @swagger_auto_schema(
        operation_summary='UI&API 测试场景 增加',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'test_type': openapi.Schema(type=openapi.TYPE_STRING, description='测试类型 {}'.format('/'.join(test_type_ls))),
                'name': openapi.Schema(type=openapi.TYPE_STRING, description='任务名称'),
                'model_name': openapi.Schema(type=openapi.TYPE_STRING, description='模块名称'),
                'function_name': openapi.Schema(type=openapi.TYPE_STRING, description='功能名称'),
                'scene_name': openapi.Schema(type=openapi.TYPE_STRING, description='场景名称'),
                'scene_desc': openapi.Schema(type=openapi.TYPE_STRING, description='场景描述'),
                'build_user': openapi.Schema(type=openapi.TYPE_STRING, description='创建用户'),
                'ids': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_STRING), description='拼接的函数id列表'),
                # 列表参数 参照这种写法
            }))
    def post(self, request):
        """测试场景&配置 增加"""
        data = JSONParser().parse(request)
        redis_conn = redis.Redis(connection_pool=redis_pool)  # redis链接
        test_type = data['test_type']
        if test_type not in self.test_type_ls:
            return JsonResponse(code="999996", msg="参数有误!")
        ui_func_ids = data['ids']
        methods = ''
        methods_remark = ''
        method_ids = ''
        method_py_path = ''
        for id in ui_func_ids:
            function_dict = eval(redis_conn.hget("{}_function_ls".format(test_type), id))
            function_name = function_dict['function']
            function_remark = function_dict['function_remark']
            function_class_remark = function_dict['function_class_remark']
            class_name = function_dict['function_class']
            function_path = function_dict['file_path']
            methods += '{}-{}--'.format(class_name, function_name)
            methods_remark += '{}:{}-->'.format(function_class_remark, function_remark)
            method_ids += '{}-->'.format(id)
            py_path_ls = function_path.split('/')[4:]
            method_py_path += 'from-{}-import-*--'.format(".".join(py_path_ls)).replace('.py', '')
        data['method'] = methods
        data['method_remark'] = methods_remark
        data['method_id_ls'] = method_ids
        data['method_py_path'] = method_py_path
        del data['ids']
        del data['test_type']

        if test_type == 'ui':
            config_serializer = UiTestConfigSerializers(data=data)
        else:
            config_serializer = ApiTestConfigSerializers(data=data)
        if config_serializer.is_valid():

            config_serializer.save()

            return JsonResponse(data={
                "id": config_serializer.data.get("id")
            }, code="999999", msg="成功")
        else:
            return JsonResponse(code="999998", msg="失败")

    @swagger_auto_schema(
        operation_summary='UI&API 测试场景 删除',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'test_type': openapi.Schema(type=openapi.TYPE_STRING, description='测试类型 {}'.format('/'.join(test_type_ls))),
                'ids': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_STRING),
                                      description='需要删除的场景id列表')
            }))
    def delete(self, request):
        """删除单条或多条 测试场景&配置数据"""
        data = JSONParser().parse(request)
        delete_ids = data['ids']
        test_type = data['test_type']
        if test_type not in self.test_type_ls:
            return JsonResponse(code="999996", msg="参数有误!")
        try:  # 数据如果有误，数据库执行会出错
            if test_type == 'ui':
                rows = UiTestConfig.objects.filter(pk__in=delete_ids).delete()
            else:
                rows = ApiTestConfig.objects.filter(pk__in=delete_ids).delete()
        except Exception as e:
            return JsonResponse(code="999999", msg="数据错误")

        if rows:
            return JsonResponse(code="999999", msg="删除成功")
        JsonResponse(code="999999", msg="失败")


    @swagger_auto_schema(
        operation_summary='UI&API 测试场景 单个查询',
        manual_parameters=[
            openapi.Parameter(name='id', in_=openapi.IN_QUERY, description='测试场景id', type=openapi.TYPE_STRING),
            openapi.Parameter(name='test_type', in_=openapi.IN_QUERY, description='测试类型 {}'.format('/'.join(test_type_ls)), type=openapi.TYPE_STRING),
        ])
    def get(self, request):
        pk = request.GET.get('id')
        test_type = request.GET.get('test_type')
        if test_type not in self.test_type_ls:
            return JsonResponse(code="999996", msg="参数有误!")
        return_data = []
        if pk:
            book_obj = eval("{}TestConfig.objects.filter(pk=pk).first()".format(test_type.capitalize()))
            book_ser = eval("{}TestConfigSerializers(book_obj)".format(test_type.capitalize()))
            return_data = book_ser.data
        return JsonResponse(data=return_data, code="999999", msg="成功！")

    @swagger_auto_schema(
        operation_summary='UI&API 测试场景 修改',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'id': openapi.Schema(type=openapi.TYPE_STRING, description='需要修改的 测试场景id'),
                'test_type': openapi.Schema(type=openapi.TYPE_STRING,
                                            description='测试类型 {}'.format('/'.join(test_type_ls))),
                'name': openapi.Schema(type=openapi.TYPE_STRING, description='任务名称'),
                'model_name': openapi.Schema(type=openapi.TYPE_STRING, description='模块名称'),
                'function_name': openapi.Schema(type=openapi.TYPE_STRING, description='功能名称'),
                'scene_name': openapi.Schema(type=openapi.TYPE_STRING, description='场景名称'),
                'scene_desc': openapi.Schema(type=openapi.TYPE_STRING, description='场景描述'),
                'build_user': openapi.Schema(type=openapi.TYPE_STRING, description='创建用户'),
                'ids': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_STRING),
                                      description='拼接的函数id列表'),
                # 列表参数 参照这种写法
            }))
    def put(self, request):
        """UI&API 测试场景 修改"""
        data = JSONParser().parse(request)
        redis_conn = redis.Redis(connection_pool=redis_pool)  # redis链接

        pk = data['id']
        test_type = data['test_type']
        if test_type not in self.test_type_ls:
            return JsonResponse(code="999996", msg="参数有误!")
        ui_func_ids = data['ids']
        del data['id']
        del data['test_type']
        methods = ''
        methods_remark = ''
        method_ids = ''
        method_py_path = ''
        for id in ui_func_ids:
            function_dict = eval(redis_conn.hget("{}_function_ls".format(test_type), id))
            function_name = function_dict['function']
            function_remark = function_dict['function_remark']
            class_name = function_dict['function_class']
            function_class_remark = function_dict['function_class_remark']
            function_path = function_dict['file_path']
            methods += '{}-{}--'.format(class_name, function_name)
            methods_remark += '{}:{}-->'.format(function_class_remark, function_remark)
            method_ids += '{}-->'.format(id)
            py_path_ls = function_path.split('/')[4:]
            method_py_path += 'from-{}-import-*--'.format(".".join(py_path_ls)).replace('.py', '')
        data['method'] = methods
        data['method_remark'] = methods_remark
        data['method_id_ls'] = method_ids
        data['method_py_path'] = method_py_path
        if pk:
            try:
                # 与增的区别在于，需要明确被修改的对象，交给序列化类
                book_instance = eval("{}TestConfig.objects.get(pk=pk)".format(test_type.capitalize()))
            except:
                return JsonResponse(code="999998", msg="失败")
            book_ser = UiTestConfigSerializers(instance=book_instance, data=data)
            if book_ser.is_valid(raise_exception=True):
                book_ser.save()
                return JsonResponse(code="999999", msg="成功")

            else:
                return JsonResponse(code="999998", msg="失败")


class MethodsLs(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = ()
    test_type_ls = ['ui', 'api']

    @swagger_auto_schema(
        operation_summary='UI&API 测试用例 函数列表页面',
        manual_parameters=[
            openapi.Parameter(name='test_type', in_=openapi.IN_QUERY, description='测试类型 {}'.format('/'.join(test_type_ls)), type=openapi.TYPE_STRING),
        ])
    def get(self, request):
        """UI&API 测试用例 函数列表页面 无参数"""
        test_type = request.GET.get('test_type')
        if test_type not in self.test_type_ls:
            return JsonResponse(code="999996", msg="参数有误!")

        redis_conn = redis.Redis(connection_pool=redis_pool)  # redis链接
        methods_data = redis_conn.hgetall("{}_function_ls".format(test_type))
        return_data = []
        for id in methods_data.keys():
            method_dict = eval(methods_data[id])
            method_dict['id'] = id
            method_dict['function_remark'] = method_dict['function_class_remark'] + ':' + method_dict['function_remark']
            return_data.append(method_dict)
        return JsonResponse(data=return_data, code="999999", msg="成功!")


class TestTaskLs(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = ()
    test_type_ls = ['ui', 'api']

    @swagger_auto_schema(
        operation_summary='UI&API 测试场景列表页',
        manual_parameters=[
            openapi.Parameter(name='page', in_=openapi.IN_QUERY, description='页码', type=openapi.TYPE_STRING),
            openapi.Parameter(name='page_size', in_=openapi.IN_QUERY, description='数量', type=openapi.TYPE_STRING),
            openapi.Parameter(name='model_name', in_=openapi.IN_QUERY, description='模块名称', type=openapi.TYPE_STRING),
            openapi.Parameter(name='function_name', in_=openapi.IN_QUERY, description='功能名称', type=openapi.TYPE_STRING),
            openapi.Parameter(name='test_type', in_=openapi.IN_QUERY, description='测试类型 {}'.format('/'.join(test_type_ls)), type=openapi.TYPE_STRING),
        ])
    def get(self, request):
        """UI&API 测试场景列表页 此接口需要前端轮询 实时更新 测试场景 运行状态"""
        try:
            page_size = int(request.GET.get("page_size", 20))
            page = int(request.GET.get("page", 1))
        except (TypeError, ValueError):
            return JsonResponse(code="999985", msg="page_size/page参数必须为int")

        test_type = request.GET.get('test_type')
        if test_type not in self.test_type_ls:
            return JsonResponse(code="999996", msg="参数有误!")

        queryset = eval("{}TestConfig.objects.all()".format(test_type.capitalize()))
        model_name = request.GET.get("model_name")  # 模块名称
        function_name = request.GET.get("function_name")  # 功能名称
        aQ = Q()
        if model_name:  # 多字段筛选
            aQ.add(Q(model_name__contains=model_name), Q.AND)
        if function_name:
            aQ.add(Q(function_name__contains=function_name), Q.AND)

        queryset = queryset.filter(aQ).order_by("id")

        paginator = Paginator(queryset, page_size)  # paginator对象
        total = len(queryset)  # 总数量
        try:
            obm = paginator.page(page)
            serialize = eval('{}TestConfigListSerializers(obm, many=True)'.format(test_type.capitalize()))
            return_data = serialize.data

        except Exception as _e:
            return_data = []

        return JsonResponse(data={"data": return_data,
                                  "page": page,
                                  "total": total
                                  }, code="999999", msg="成功")
