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
from zy_api_testing.models import ApiManage, SceneApiConf, ApiParams
from zy_api_testing.serializers import SceneApiConfSerializerQuery, SceneApiConfSerializerAdd, SceneGetOneConf, \
    ApiParamsSerializerAdd, QueryApiParamsSerializer
from zy_api_testing.tools import api_list_query, DelException, Resolver, AssertDataDealResolver


class ApiParamsAdd(APIView):
    authentication_classes = ()
    permission_classes = []

    @swagger_auto_schema(
        operation_summary='获取单个配置接口配置参数',
        manual_parameters=[
            openapi.Parameter(name='api_conf_id', in_=openapi.IN_QUERY, description='配置接口id', type=openapi.TYPE_STRING)
        ])
    def get(self, request):
        try:
            data = request.GET
            param_objs = ApiParams.objects.filter(api_conf_id=data.get('api_conf_id'))
            if not param_objs:
                return error_response('错误的配置id')
            obm = param_objs.first()
            try:
                api_param_serialize = QueryApiParamsSerializer(obm)
                # api_manage_serialize = ApiManageSerializerConfQuery(obm, many=True)
                return_data = api_param_serialize.data
                response = {
                    "data": return_data,
                }
            except Exception as _e:
                response = {}
            return success_response(data=response, msg='查询成功！')
        except Exception as e:
            return error_response('失败!')

    @swagger_auto_schema(
        operation_summary='场景api数据 新增',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'api_conf_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='接口配置id'),
                'putin_params_json': openapi.Schema(type=openapi.TYPE_INTEGER, description='请求参数表格数据'),
                'asset_json': openapi.Schema(type=openapi.TYPE_INTEGER, description='断言表格数据'),
                # 'sort': openapi.Schema(type=openapi.TYPE_INTEGER, description='数据的排序值'),
            }
        )
    )
    def post(self, request):
        """api配置数据 增加"""
        try:
            with transaction.atomic():
                # all_data = JSONParser().parse(request).get('all_data')
                data = JSONParser().parse(request)
                # for data in all_data:
                api_conf_id = data.get('api_conf_id')
                ApiParams.objects.filter(api_conf_id=api_conf_id).delete()  # 确保每条配置只存在一天生效请求，断言参数
                putin_params_json = eval(data.get('putin_params_json'))
                asset_json = eval(data.get('asset_json'))
                param_in = SceneApiConf.objects.get(id=api_conf_id).api.param_in
                # param_in = ApiManage.objects.get(id = api_manage_id).param_in
                end_request_json = {}
                for param_position in eval(param_in):
                    resolver = Resolver(putin_params_json, param_position)
                    data_dict = resolver.get_end_dict()
                    end_request_json[param_position] = data_dict
                resolver_asset = AssertDataDealResolver(asset_json)
                data['end_asset_json'] = json.dumps(resolver_asset.get_end_list())
                data['end_request_json'] = json.dumps(end_request_json)
                data['putin_params_json'] = json.dumps(putin_params_json)
                data['asset_json'] = json.dumps(asset_json)
                api_params_serializer = ApiParamsSerializerAdd(data=data)
                if api_params_serializer.is_valid():
                    save_data = api_params_serializer.save()
                else:
                    raise Exception('validateError')
                return success_response(data={'id': save_data.api_conf_id.id}, msg='新增api配置数据信息成功！')
        except Exception as e:
            if str(e) == 'validateError':
                return error_response(msg=api_params_serializer.errors)
            else:
                return error_response("失败")

    @swagger_auto_schema(
        operation_summary='场景api数据 修改',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'all_data': openapi.Schema(type=openapi.TYPE_INTEGER, description='修改api请求参数全量数据'),
                'api_conf_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='接口配置id'),
            }
        )
    )
    def put(self, request):
        """api配置数据 修改"""
        with transaction.atomic():
            try:
                request_data = request.data
                # 先删除该配置下的所有api参数：
                api_conf_id = request_data.get('api_conf_id')
                ApiParams.objects.filter(api_conf_id=api_conf_id).delete()
                all_data = request_data.get('all_data')
                for data in all_data:
                    api_conf_id = data.get('api_conf_id')
                    putin_params_json = data.get('putin_params_json')
                    asset_json = data.get('asset_json')
                    param_in = SceneApiConf.objects.get(id=api_conf_id).api.param_in
                    # param_in = ApiManage.objects.get(id = api_manage_id).param_in
                    end_request_json = {}
                    for param_position in eval(param_in):
                        resolver = Resolver(putin_params_json, param_position)
                        data_dict = resolver.get_end_dict()
                        end_request_json[param_position] = data_dict
                    resolver_asset = AssertDataDealResolver(asset_json)
                    data['end_asset_json'] = json.dumps(resolver_asset.get_end_list())
                    data['end_request_json'] = json.dumps(end_request_json)
                    data['putin_params_json'] = json.dumps(putin_params_json)
                    data['asset_json'] = json.dumps(asset_json)
                    api_params_serializer = ApiParamsSerializerAdd(data=data)
                    if api_params_serializer.is_valid():
                        api_params_serializer.save()
                    else:
                        raise Exception('validError')

                return success_response(data='', msg='新增api配置数据信息成功！')
            except Exception as e:
                if str(e)=='validError':
                    return error_response(msg=api_params_serializer.errors)
                else:
                    return error_response(msg='失败！！！')
