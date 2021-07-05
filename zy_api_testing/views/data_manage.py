# -*- coding: utf-8 -*-
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q
from django.forms import model_to_dict
from drf_yasg2.utils import swagger_auto_schema
from drf_yasg2 import openapi
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView

from system_settings.tools import error_response, success_response
from zy_api_testing.models import SceneApiConf, ApiManage, ApiParams, Scene
from zy_api_testing.serializers import SceneSerializerAdd, SceneSerializerQuery, ApiManageSerializerQuery, \
    ApiDataSceneApiConfSerializerQuery

# 列表页多条件查询抽取 ，暂时只支持等值查询 ， 不支持模糊查询
from zy_api_testing.tools import api_list_query


def data_list_query(data, page, page_size, model, query_params):
    """
    :param data: request.GET
    :param page: 页数
    :param page_size: 每页元素个数
    :param query_params: 列表  包含 所有可能查询的元素键， 需与数据库字段名对应上
    :model : 数据库模型类
    :return:
    """
    where = Q()
    for i in range(len(query_params)):
        key = query_params[i]
        query_params[i] = data.get(query_params[i])
        if query_params[i]:
            tempStr = " where & Q(" + key + "="+query_params[i]+")"
            where = eval(tempStr)
    queryset = model.objects.filter(where).order_by('id')
    total = len(queryset)
    paginator = Paginator(queryset, page_size)  # paginator对象
    try:
        obm = paginator.page(page)
    except:
        obm = []
    return total, obm

def deal_scene(scene_id):
    """
    :param scene_id: 场景id
    :return: request_list
    """
    scene = []
    # 根据排序值查询 场景下接口
    if SceneApiConf.objects.filter(scene=scene_id):
        one_api_data_list = list(SceneApiConf.objects.filter(scene=scene_id).order_by('sort').values('id', 'api'))
        for api_data in one_api_data_list:
            # 获取单个接口的所有次数 执行请求数据
            a_api = []
            scene_id = api_data.get("id")
            api_manage_obj = model_to_dict(ApiManage.objects.filter(id=api_data.get('api')).first())
            api_params_objs = ApiParams.objects.filter(api_conf_id=scene_id).order_by('sort')
            for api_param in api_params_objs:
                one_api_request_params = {}  # 单个接口的单次请求参数
                data = model_to_dict(api_param)
                request_params = eval(data.get('end_request_json'))
                assert_data = eval(data.get('end_asset_json'))
                request_params['headers'] = {}
                one_api_request_params['request_params'] = request_params
                one_api_request_params['assert_data'] = assert_data
                one_api_request_params['global_param_key'] = '20222'
                one_api_request_params['global_param_value'] = '11111'
                one_api_request_params['api_desc'] = api_manage_obj.get('api_desc')
                one_api_request_params['request_method'] = api_manage_obj.get('request_method')
                one_api_request_params['path'] = api_manage_obj.get('path')
                a_api.append(one_api_request_params)  # 添加单次请求数据
            scene.append(a_api)  # 添加单接口多次请求数据
        return True, scene
    else:
        return False, '场景id错误'



class DelException(Exception):
    pass

class DataManageView(APIView):
    authentication_classes = ()
    permission_classes = []



    @swagger_auto_schema(
        operation_summary='测试数据 单删群删',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'ids': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_STRING),
                                      description='需要删除的测试数据ids')
            }))
    def delete(self, request):
        """测试数据 单删群删"""
        try:
            with transaction.atomic():
                data = JSONParser().parse(request)
                delete_ids = data.get('ids')
                for id in delete_ids:
                    task_obj = ApiManage.objects.filter(id=id)
                    if task_obj:
                        # 是否有场景正在使用当前接口
                        if SceneApiConf.objects.filter(api=task_obj.first().id):
                            raise DelException("DelException")
                        task_obj.first().delete()
                    else:
                        return error_response(msg="数据错误!")
        except Exception as e:
            if str(e) == 'DelException':
                return error_response(msg='当前接口正在被使用,无法删除: {}'.format(id))
            else:
                return error_response(msg='删除失败！')
        return success_response(data='', msg="成功!")

    @swagger_auto_schema(
        operation_summary='测试数据管理页面 (多条件筛选)',
        manual_parameters=[
            openapi.Parameter(name='page', in_=openapi.IN_QUERY, description='页码', type=openapi.TYPE_STRING),
            openapi.Parameter(name='page_size', in_=openapi.IN_QUERY, description='数量', type=openapi.TYPE_STRING),
            openapi.Parameter(name='api_desc', in_=openapi.IN_QUERY, description='接口名称', type=openapi.TYPE_STRING),
        ])
    def get(self, request):
        try:
            data = request.GET
            page = int(data.get('page', 1))
            page_size = int(data.get('page_size', 15))

            where = Q()
            if data.get('api_desc'):  # 多字段筛选
                api_id_list = [i.get('id') for i in list(ApiManage.objects.filter(api_desc__contains=data.get('api_desc')).values('id'))]
                where.add(Q(api__in=api_id_list), Q.AND)
            queryset = SceneApiConf.objects.filter(where).order_by('-scene')
            total = len(queryset)
            paginator = Paginator(queryset, page_size)  # paginator对象
            try:
                obm = paginator.page(page)
            except:
                obm = []

            # total, obm = api_list_query(data, page, page_size, SceneApiConf, '-scene', ['api.api_desc'])
            try:
                data_manage_serialize = ApiDataSceneApiConfSerializerQuery(obm, many=True)
                return_data = data_manage_serialize.data
                response = {
                    "data": return_data,
                    "page": page,
                    "total": total
                }
            except Exception as _e:
                response = {}
            return success_response(data=response, msg='查询成功！')
        except Exception as e:
            return error_response(msg='失败!')

class DataManageDetailView(APIView):
    authentication_classes = ()
    permission_classes = []

    @swagger_auto_schema(
        operation_summary='测试数据查询 单查',
    )
    def get(self, request, pk):
        """测试数据查询 单查"""
        if pk:
            api_obj = ApiManage.objects.filter(pk=pk).first()
            if api_obj:
                server_serializer = ApiManageSerializerQuery(api_obj)
                return success_response(data=server_serializer.data, msg="成功!")
            return error_response(msg="无数据!")
        else:
            return error_response(msg="id为空!")

    @swagger_auto_schema(
        operation_summary='测试数据 修改',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'professional_name': openapi.Schema(type=openapi.TYPE_STRING, description='业务名称'),
                'scene_name': openapi.Schema(type=openapi.TYPE_STRING, description='场景名称'),
                'api_desc': openapi.Schema(type=openapi.TYPE_STRING, description='接口描述'),
                'sever_name': openapi.Schema(type=openapi.TYPE_STRING, description='服务名称'),
                'founder': openapi.Schema(type=openapi.TYPE_STRING, description='创建者'),
                'Remark': openapi.Schema(type=openapi.TYPE_STRING, description='备注'),
                'update_time': openapi.Schema(type=openapi.TYPE_INTEGER, description='最后修改时间'),
            }))

    def put(self,request, pk):
        """测试数据 修改 此接口需要先拉取表单数据字典"""
        if pk:
            data = JSONParser().parse(request)
            data_manage_obj = Scene.objects.filter(id=pk).first()
            if data_manage_obj:
                server_serializer = SceneSerializerAdd(instance=data_manage_obj, data=data)
                if server_serializer.is_valid():
                    server_serializer.save()
                else:
                    return error_response(msg="修改失败！")
                return success_response(msg="修改成功!")
            return error_response(msg="无数据!")
        else:
            return error_response(msg="id为空!")
