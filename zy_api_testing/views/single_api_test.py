import copy
import json

from django.db import transaction
from drf_yasg2 import openapi
from drf_yasg2.utils import swagger_auto_schema
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView

from account_system.tools import get_real_name
from automated_testing.common.api_response import JsonResponse
from automatic_api.api_scene_execution import api_scene_execution
from system_settings.models import Environment
from system_settings.tools import success_response, error_response
from test_exe_conf.serializers import ApiTestReportSerializers
from zy_api_testing.models import ApiManage, SingleApiParams
from zy_api_testing.serializers import SingleApiParamsSerializerAdd, QuerySingleApiParamsSerializer
from zy_api_testing.tools import deal_param_ls, DealRequestConf, DealRequestLsConf, PutSameLayer, DealToParamsJson, \
    Resolver, AssertDataDealResolver, deal_single_api


# class SingleApiTableParam(APIView):
#     authentication_classes = ()
#     permission_classes = []
#
#     @swagger_auto_schema(
#         operation_summary='单api测试 入参出参查询(匹配前端表单组件数据结构)',
#         manual_parameters=[
#             openapi.Parameter(name='AUTHORIZATION', in_=openapi.IN_HEADER, description='登录验证', type=openapi.TYPE_STRING),
#         ],)
#
#     def get(self, request, pk):
#         # 单api 入参出参查询(匹配前端表单组件数据结构)
#         if pk:
#             ApiManage_obj = ApiManage.objects.filter(pk=pk).first()
#             if ApiManage_obj:
#                 req_param_ls = eval(ApiManage_obj.request_params_ls)
#                 # 入参列表
#                 rep_param_ls = eval(ApiManage_obj.response_params_ls)
#                 request_params = []
#                 for param_in in req_param_ls:
#                     if req_param_ls.get('body', None):
#                         deal_params = DealRequestLsConf(req_param_ls[param_in], 'request_ls', param_in)
#                         start_data = deal_params.get_data()
#                         deal_params = PutSameLayer(start_data)
#                         request_params += deal_params.get_data()
#
#                 rep_obj = DealRequestLsConf(rep_param_ls, 'assert')
#                 rep_result = rep_obj.get_data()
#                 rep_obj = PutSameLayer(rep_result)
#                 rep_result = rep_obj.get_data()
#                 rep_result.insert(0, {'assert_type': '', 'param': 'response.status_code', 'type': 'int', 'description': '响应状态码(外层)', 'id': -1, 'is_ignore_key': 0, 'is_children': 0, 'children': []})
#                 # 返回参数 添加默认参数 response.status_code
#
#                 if not ApiManage_obj.request_table_json:
#                     # 没有历史数据 存储
#                     ApiManage_obj.request_table_json = str(request_params)
#                 else:
#                     # 存在历史数据 与新的参数数据做对比
#                     last_request_table_json = ApiManage_obj.request_table_json
#                     if eval(last_request_table_json) != request_params:
#                         # 对比失败 覆盖原值
#                         ApiManage_obj.request_table_json = str(request_params)
#
#
#                 if not ApiManage_obj.response_table_json:
#                     ApiManage_obj.response_table_json = str(rep_result)
#                 ApiManage_obj.save()
#
#                 return JsonResponse(data={"req_params": request_params, "rep_result": rep_result}, code="999999", msg="成功!")
#             return JsonResponse(code="999998", msg="无数据!")
#         else:
#             return JsonResponse(code="999998", msg="id为空!")


class SingleApiParam(APIView):
    authentication_classes = ()
    permission_classes = []

    @swagger_auto_schema(
        operation_summary='单接口测试 历史测试数据查询(匹配前端表单组件数据结构)',
        manual_parameters=[
            openapi.Parameter(name='AUTHORIZATION', in_=openapi.IN_HEADER, description='登录验证', type=openapi.TYPE_STRING),
            openapi.Parameter(name='api_id', in_=openapi.IN_QUERY, description='配置接口id', type=openapi.TYPE_STRING)
        ])
    def get(self, request):
        try:
            data = request.GET
            ApiManage_obj = ApiManage.objects.filter(id=data['api_id']).first()
            if ApiManage_obj:
                req_param_ls = eval(ApiManage_obj.request_params_ls)
                # 入参列表
                rep_param_ls = eval(ApiManage_obj.response_params_ls)
                # 出参列表
                request_params = []
                for param_in in req_param_ls:
                    if req_param_ls.get(param_in, None):
                        deal_params = DealRequestLsConf(req_param_ls[param_in], 'request_ls', param_in)
                        start_data = deal_params.get_data()
                        deal_params = PutSameLayer(start_data)
                        request_params += deal_params.get_data()

                rep_obj = DealRequestLsConf(rep_param_ls, 'assert')
                rep_result = rep_obj.get_data()
                rep_obj = PutSameLayer(rep_result)
                rep_result = rep_obj.get_data()
                rep_result.insert(0, {'assert_type': '', 'param': 'response.status_code', 'type': 'int',
                                      'description': '响应状态码(外层)', 'id': -1, 'is_ignore_key': 0, 'is_children': 0,
                                      'children': []})
                # 返回参数 添加默认参数 response.status_code
                is_need_save = False
                is_clear_param_data = False
                # 是否需要清空历史测试数据
                is_rep_modify = False
                is_req_modify = False
                if not ApiManage_obj.request_table_json:
                    # 没有历史数据 存储
                    ApiManage_obj.request_table_json = str(request_params)
                    is_need_save = True
                else:
                    # 存在历史数据 与新的参数数据做对比
                    last_request_table_json = ApiManage_obj.request_table_json
                    if eval(last_request_table_json) != request_params:
                        # 对比失败 覆盖原值
                        ApiManage_obj.response_table_json = str(rep_result)
                        is_need_save = True
                        is_req_modify = True
                        ApiManage_obj.request_table_json = str(request_params)
                        param_objs = SingleApiParams.objects.filter(api_id=data.get('api_id')).order_by('sort')
                        for param_obj in param_objs:
                            is_clear_param_data = True
                            param_obj.req_table_data = str(request_params)
                            param_obj.save()

                if not ApiManage_obj.response_table_json:
                    ApiManage_obj.response_table_json = str(rep_result)
                    is_need_save = True
                else:
                    last_response_table_json = ApiManage_obj.response_table_json
                    if eval(last_response_table_json) != rep_result:
                        ApiManage_obj.response_table_json = str(rep_result)
                        is_need_save = True
                        is_rep_modify = True
                        ApiManage_obj.response_table_json = str(rep_result)
                        param_objs = SingleApiParams.objects.filter(api_id=data.get('api_id')).order_by('sort')
                        for param_obj in param_objs:
                            is_clear_param_data = True
                            param_obj.req_table_data = str(request_params)
                            param_obj.save()

                param_objs = SingleApiParams.objects.filter(api_id=data.get('api_id')).order_by('sort')
                if is_rep_modify and is_req_modify:
                    for param_obj in param_objs:
                        param_obj.delete()
                if is_need_save:
                    ApiManage_obj.save()
                if is_rep_modify and is_req_modify:
                    return_data = [
                        {"api_id": data['api_id'], "req_table_data": request_params, "rep_table_data": rep_result,
                         "has_edited": 0}]
                else:
                    param_objs = SingleApiParams.objects.filter(api_id=data.get('api_id')).order_by('sort')
                    if param_objs:
                        api_param_serialize = QuerySingleApiParamsSerializer(param_objs, many=True)
                        api_params = api_param_serialize.data
                        for api_param in api_params:
                            api_param['has_edited'] = 1
                        return_data = api_params
                    else:
                        return_data = [
                            {"api_id": data['api_id'], "req_table_data": request_params, "rep_table_data": rep_result,
                             "has_edited": 0}]

                if is_clear_param_data:
                    msg = '接口数据结构更改 已清空历史测试数据!'
                else:
                    msg = '查询成功！'
                return success_response(data=return_data, msg=msg)
            else:
                return error_response(msg='没有此接口！')

        except Exception as e:
            return error_response('失败!')

    @swagger_auto_schema(
        operation_summary='单接口测试配置 新增',
        manual_parameters=[
            openapi.Parameter(name='AUTHORIZATION', in_=openapi.IN_HEADER, description='登录验证',
                              type=openapi.TYPE_STRING, default='dev'),
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'api': openapi.Schema(type=openapi.TYPE_INTEGER, description='测试api id'),
                'req_table_data': openapi.Schema(type=openapi.TYPE_INTEGER, description='请求参数表格数据 前端格式'),
                'rep_table_data': openapi.Schema(type=openapi.TYPE_INTEGER, description='断言表格数据 前端格式'),
                'sort': openapi.Schema(type=openapi.TYPE_INTEGER, description='数据的排序值'),
            }
        )
    )
    def post(self, request):
        try:
            data = JSONParser().parse(request)
            api_id = data.get('api')
            with transaction.atomic():
                # SingleApiParams.objects.filter(api_id=api_id).delete()  # 确保每条配置只存在一天生效请求，断言参数
                req_table_data = data.get('req_table_data')
                asset_table_data = data.get('rep_table_data')

                putin_params_json = DealToParamsJson(copy.deepcopy(req_table_data))
                asset_json = DealToParamsJson(copy.deepcopy(asset_table_data))

                api_obj = ApiManage.objects.get(id=api_id)
                param_in = api_obj.param_in

                end_request_json = {}
                for param_position in eval(param_in):
                    resolver = Resolver(putin_params_json.get_data(), param_position)
                    data_dict = resolver.get_end_dict()
                    end_request_json[param_position] = data_dict
                resolver_asset = AssertDataDealResolver(asset_json.get_data())
                data['req_table_data'] = str(req_table_data)
                data['rep_table_data'] = str(asset_table_data)
                data['end_asset_json'] = str(resolver_asset.get_end_list())
                data['end_request_json'] = str(end_request_json)
                data['putin_params_json'] = str(putin_params_json.get_data())
                data['asset_json'] = str(asset_json.get_data())
                api_params_serializer = SingleApiParamsSerializerAdd(data=data)
                if api_params_serializer.is_valid():
                    save_data = api_params_serializer.save()
                else:
                    raise Exception('validateError')
                return success_response(data={'id': save_data.id}, msg='新增api配置数据信息成功！')
        except Exception as e:
            if str(e) == 'validateError':
                return error_response(msg=api_params_serializer.errors)
            else:
                return error_response("失败")

    @swagger_auto_schema(
        operation_summary='单接口测试配置 修改',
        manual_parameters=[
            openapi.Parameter(name='AUTHORIZATION', in_=openapi.IN_HEADER, description='登录验证',
                              type=openapi.TYPE_STRING, default='dev'),
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='测试数据 id'),
                'api': openapi.Schema(type=openapi.TYPE_INTEGER, description='测试api id'),
                'req_table_data': openapi.Schema(type=openapi.TYPE_INTEGER, description='请求参数表格数据 前端格式'),
                'rep_table_data': openapi.Schema(type=openapi.TYPE_INTEGER, description='断言表格数据 前端格式'),
                'sort': openapi.Schema(type=openapi.TYPE_INTEGER, description='数据的排序值'),
            }
        )
    )
    def put(self, request):
        try:
            data = JSONParser().parse(request)
            api_id = data.get('api')
            id = data.get('id')
            with transaction.atomic():
                # SingleApiParams.objects.filter(api_id=api_id).delete()  # 确保每条配置只存在一天生效请求，断言参数
                single_param_obj = SingleApiParams.objects.filter(id=id).first()
                if not single_param_obj:
                    return error_response("无此条数据!")
                req_table_data = data.get('req_table_data')
                asset_table_data = data.get('rep_table_data')

                putin_params_json = DealToParamsJson(copy.deepcopy(req_table_data))
                asset_json = DealToParamsJson(copy.deepcopy(asset_table_data))

                api_obj = ApiManage.objects.get(id=api_id)
                param_in = api_obj.param_in

                end_request_json = {}
                for param_position in eval(param_in):
                    resolver = Resolver(putin_params_json.get_data(), param_position)
                    data_dict = resolver.get_end_dict()
                    end_request_json[param_position] = data_dict
                resolver_asset = AssertDataDealResolver(asset_json.get_data())
                data['req_table_data'] = str(req_table_data)
                data['rep_table_data'] = str(asset_table_data)
                data['end_asset_json'] = str(resolver_asset.get_end_list())
                data['end_request_json'] = str(end_request_json)
                data['putin_params_json'] = str(putin_params_json.get_data())
                data['asset_json'] = str(asset_json.get_data())
                api_params_serializer = SingleApiParamsSerializerAdd(instance=single_param_obj, data=data)
                if api_params_serializer.is_valid():
                    save_data = api_params_serializer.save()
                else:
                    raise Exception('validateError')
                return success_response(data={'id': save_data.id}, msg='修改api配置数据信息成功！')
        except Exception as e:
            if str(e) == 'validateError':
                return error_response(msg=api_params_serializer.errors)
            else:
                return error_response("失败")

    @swagger_auto_schema(
        operation_summary='单接口测试配置 测试数据删除',
        manual_parameters=[
            openapi.Parameter(name='AUTHORIZATION', in_=openapi.IN_HEADER, description='登录验证',
                              type=openapi.TYPE_STRING, default='dev'),
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'api_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='测试api id'),
                'test_param_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='需要删除的 测试数据id')
            })
    )
    def delete(self, request):
        data = JSONParser().parse(request)
        test_param_id = data['test_param_id']
        api_id = data['api_id']

        try:
            test_param_obj = SingleApiParams.objects.filter(id=test_param_id).first()
            if test_param_obj:
                test_param_other_objs = SingleApiParams.objects.filter(api=api_id, sort__gt=test_param_obj.sort)
                for test_param_other_obj in test_param_other_objs:
                    test_param_other_obj.sort += 1
                    test_param_obj.save()
                test_param_obj.delete()
            else:
                return error_response(msg='无此测试数据！')
            return success_response(msg='数据删除成功！')
        except Exception as e:
            return JsonResponse(code="999998", msg="数据错误!")


class SingleApiExecution(APIView):
    authentication_classes = ()
    permission_classes = []

    @swagger_auto_schema(
        operation_summary='单接口测试 执行',
        manual_parameters=[openapi.Parameter(name='AUTHORIZATION', in_=openapi.IN_HEADER, description='登录验证',
                                             type=openapi.TYPE_STRING, default='dev'), ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'environment': openapi.Schema(type=openapi.TYPE_INTEGER, description='测试环境id'),
                'api': openapi.Schema(type=openapi.TYPE_INTEGER, description='测试api id'),
                'need_login': openapi.Schema(type=openapi.TYPE_INTEGER, description='是否需要登录 1/0'),
            }))
    def post(self, request):
        data = JSONParser().parse(request)
        single_api_id = data['api']
        need_login = data['need_login']
        environment_ip = Environment.objects.get(id=data['environment']).Test_address
        flag, data = deal_single_api(single_api_id, environment_ip, need_login)
        if not flag:
            return error_response(data)
        try:
            scene_execution = api_scene_execution()
            report_data = scene_execution.scene_execution(data)

            report_data['tester'] = get_real_name(request)  # 添加测试人
            report_data['test_type'] = "API-单接口测试-{}".format(ApiManage.objects.get(id=single_api_id).api_desc)
            api_report_serializers = ApiTestReportSerializers(data=report_data)
            if api_report_serializers.is_valid():
                api_report_serializers.save()
            else:
                return error_response(api_report_serializers.errors)
        except Exception as e:
            return error_response("执行失败！")
        return success_response("执行成功", data={"report_src": report_data['report_src']})
