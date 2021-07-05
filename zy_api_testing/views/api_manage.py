# -*- coding: utf-8 -*-
import json

from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q, Count
from django.forms import model_to_dict
from drf_yasg2.utils import swagger_auto_schema
from drf_yasg2 import openapi
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView

from system_settings.tools import success_response, error_response
from zy_api_testing.models import ApiManage, SceneApiConf, SingleApiParams
from zy_api_testing.serializers import ApiManageSerializerQuery, SerializerQueryAllApi, ApiManageSerializerConfQuery, \
    ApiManageSerializerModify
from zy_api_testing.tools import api_list_query, DelException, deal_scene, send_emails

ASSERT_TYPE_SELECT = ['==', '!=', 'in']
PARAMS_TYPE_SELECT = ['before_rep', 'string', 'integer', 'boolean', 'array']
ASSERT_DATA_TYPE_SELECT = ['string', 'integer', 'boolean', 'array']


class ApiManageListView(APIView):
    authentication_classes = ()
    permission_classes = []

    @swagger_auto_schema(
        operation_summary='api管理页面 (多条件筛选)',
        manual_parameters=[
            openapi.Parameter(name='page', in_=openapi.IN_QUERY, description='页码', type=openapi.TYPE_STRING),
            openapi.Parameter(name='page_size', in_=openapi.IN_QUERY, description='数量', type=openapi.TYPE_STRING),
            openapi.Parameter(name='tag', in_=openapi.IN_QUERY, description='tag/功能', type=openapi.TYPE_STRING),
            openapi.Parameter(name='api_desc', in_=openapi.IN_QUERY, description='接口名', type=openapi.TYPE_STRING),
            openapi.Parameter(name='path', in_=openapi.IN_QUERY, description='请求路径', type=openapi.TYPE_STRING),
            openapi.Parameter(name='exception_flag', in_=openapi.IN_QUERY, description='解析结果', type=openapi.TYPE_STRING)
        ])
    def get(self, request):
        try:
            data = request.GET
            page = int(data.get('page', 1))
            page_size = int(data.get('page_size', 15))
            total, obm = api_list_query(data, page, page_size, ApiManage, 'id', ['tag', 'api_desc', 'path', 'exception_flag'])
            try:
                api_manage_serialize = ApiManageSerializerQuery(obm, many=True)
                # api_manage_serialize = ApiManageSerializerConfQuery(obm, many=True)
                return_data = api_manage_serialize.data
                response = {
                    "data": return_data,
                    "page": page,
                    "total": total
                }
            except Exception as _e:
                response = {}
            return success_response(data=response, msg='查询成功！')
        except Exception as e:
            return error_response('失败!')

    @swagger_auto_schema(
        operation_summary='api管理 单删群删',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'ids': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_STRING),
                                      description='需要删除的api id列表 ')
            }))
    def delete(self, request):
        """api管理 单删群删"""
        msg = ''
        try:
            with transaction.atomic():
                data = JSONParser().parse(request)
                delete_ids = data.get('ids')
                for id in delete_ids:
                    task_obj = ApiManage.objects.filter(id=id)
                    # single_param_obj = SingleApiParams.objects.filter(api_id=id)
                    if task_obj:
                        # 是否有场景正在使用当前接口
                        if SceneApiConf.objects.filter(api=task_obj.first().id):
                            msg += '{} 正在被场景使用,无法删除\n'.format(task_obj.first().path)
                        task_obj.first().delete()
                        if msg:
                            return error_response(msg=msg)
                    else:
                        return error_response(msg="无此数据!")
        except Exception as e:
            return error_response(msg='删除失败！')
        return success_response(data='', msg="成功!")


class ApiManageSelectData(APIView):
    authentication_classes = ()
    permission_classes = []

    @swagger_auto_schema(
        operation_summary='获取api下拉框',
        manual_parameters=[
            # openapi.Parameter(name='id', in_=openapi.IN_QUERY, description='api id', type=openapi.TYPE_STRING),
        ])
    def get(self, request):
        try:
            # flag, data = deal_scene(5)
            # return success_response(data, msg='成功!')
            # 仅查询未启用 且 解析未报错的
            api_query_all = ApiManage.objects.filter(deprecated=0, exception_flag=1)
            serializer_data_list = SerializerQueryAllApi(api_query_all, many=True)
            return success_response(data=serializer_data_list.data, msg='成功!')
        except Exception as e:
            return error_response(msg='失败！')

    @swagger_auto_schema(
        operation_summary='获取tag/功能下拉框',
        manual_parameters=[
            # openapi.Parameter(name='id', in_=openapi.IN_QUERY, description='api id', type=openapi.TYPE_STRING),
        ])
    def post(self, request):
        try:
            tag_list = [i.get('tag') for i in list(ApiManage.objects.values('tag').annotate(c=Count('id')).order_by('tag').values('tag'))]
            return success_response(data=tag_list, msg='成功!')
        except Exception as e:
            return error_response(msg='失败！')


class ApiManageDeal(APIView):
    authentication_classes = ()
    permission_classes = []

    @swagger_auto_schema(
        operation_summary='单选接口 展示初始配置信息',
        manual_parameters=[
            openapi.Parameter(name='id', in_=openapi.IN_QUERY, description='api id', type=openapi.TYPE_STRING),
        ])
    def get(self, request):
        try:
            id = request.GET.get('id')
            if not id:
                return error_response(msg='id 为空')
            query = ApiManage.objects.filter(id=id)
            if not query:
                return error_response(msg='无数据')
            serializer_obj = ApiManageSerializerConfQuery(query.first())
            data = serializer_obj.data
            data['asert_select_type'] = ASSERT_TYPE_SELECT
            data['params_select_type'] = PARAMS_TYPE_SELECT
            return success_response(data=data, msg='成功!')
        except Exception as e:
            return error_response(msg='失败！')


class GetOneApiManageDetail(APIView):
    authentication_classes = ()
    permission_classes = []

    @swagger_auto_schema(
        operation_summary='获取单个api详情',
        manual_parameters=[
            openapi.Parameter(name='AUTHORIZATION', in_=openapi.IN_HEADER, description='登录验证', type=openapi.TYPE_STRING),
            openapi.Parameter(name='id', in_=openapi.IN_QUERY, description='api id', type=openapi.TYPE_STRING),
        ],
    )
    def get(self, request):
        try:
            id = request.GET.get('id')
            if not id:
                return error_response(msg='id 为空')
            query = ApiManage.objects.filter(id=id)
            if not query:
                return error_response(msg='无数据')
            # data = model_to_dict(query.first())
            serializer = ApiManageSerializerQuery(query.first())
            return success_response(data=serializer.data, msg='成功!')
        except Exception as e:
            return error_response(msg='失败！')


    @swagger_auto_schema(
        operation_summary='新增/修改api',
        manual_parameters=[
            openapi.Parameter(name='AUTHORIZATION', in_=openapi.IN_HEADER, description='登录验证', type=openapi.TYPE_STRING),
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'server': openapi.Schema(type=openapi.TYPE_STRING, description='所属服务名'),
                'tag': openapi.Schema(type=openapi.TYPE_STRING, description='tag标签'),
                'path': openapi.Schema(type=openapi.TYPE_STRING, description='请求路径'),
                'api_desc': openapi.Schema(type=openapi.TYPE_STRING, description='接口名称'),
                'tag_english_desc': openapi.Schema(type=openapi.TYPE_STRING, description='接口英文描述'),
                'request_method': openapi.Schema(type=openapi.TYPE_NUMBER, description='请求方式'),
                'request_params_json': openapi.Schema(type=openapi.TYPE_STRING, description='请求参数json'),
                'response_params_json': openapi.Schema(type=openapi.TYPE_STRING, description='响应参数json'),
                'deprecated': openapi.Schema(type=openapi.TYPE_STRING, description='是否弃用 0/1  '),
                'param_in': openapi.Schema(type=openapi.TYPE_STRING, description='请求参数所在位置'),
                'id': openapi.Schema(type=openapi.TYPE_STRING, description='api  id 传为修改 不传新增'),
            })
    )
    def post(self, request):
        # try:
        data = JSONParser().parse(request)
        data['has_manual'] = 1
        data['exception_flag'] = 1
        data['exception_log'] = ''
        data['request_params_json'] = json.dumps(data['request_params_json'])
        data['response_params_json'] = json.dumps(data['response_params_json'])
        if data.get('id'):   # 修改
            api_obj = ApiManage.objects.filter(id=data.get('id')).first()
            api_manage_ser = ApiManageSerializerModify(instance=api_obj, data=data)
        else:  # 新增
            api_manage_ser = ApiManageSerializerModify(data=data)
        if api_manage_ser.is_valid():
            api_manage_ser.save()
        else:
            return error_response(api_manage_ser.errors)
        return success_response(data='', msg='新增接口数据成功！！！')
        # except Exception as e:
        #     return error_response(msg='失败')



# class ApiManageView(APIView):
#     authentication_classes = ()
#     permission_classes = []
#
#     @swagger_auto_schema(
#         operation_summary='获取单个api详情',
#         manual_parameters=[
#             openapi.Parameter(name='id', in_=openapi.IN_QUERY, description='api id', type=openapi.TYPE_STRING),
#         ])
#     def get(self, request):
#         id = request.GET.get('id', '')
#         if not id:
#             return error_response(msg='id 为空')
#         ApiManage_obj = ApiManage.objects.filter(id=id)

