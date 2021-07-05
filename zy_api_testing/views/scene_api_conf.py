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
from zy_api_testing.models import ApiManage, SceneApiConf, Scene, ApiParams
from zy_api_testing.serializers import SceneApiConfSerializerQuery, SceneApiConfSerializerAdd, SceneGetOneConf, \
    ApiManageSerializerConfQuery, ApiParamsSerializerAdd
from zy_api_testing.tools import api_list_query, DelException, juged_type, check_one_request_conf, Resolver, \
    AssertDataDealResolver, check_has_history_data, check_has_assert_history_data
from zy_api_testing.views.api_manage import ASSERT_TYPE_SELECT, PARAMS_TYPE_SELECT

BOOL_VALUE_SELECT = ['True', 'False', 'None']


class ApiConfList(APIView):
    authentication_classes = ()
    permission_classes = []

    @swagger_auto_schema(
        operation_summary='场景配置api页面 (多条件筛选)',
        manual_parameters=[
            openapi.Parameter(name='page', in_=openapi.IN_QUERY, description='页码', type=openapi.TYPE_STRING),
            openapi.Parameter(name='page_size', in_=openapi.IN_QUERY, description='数量', type=openapi.TYPE_STRING),
            openapi.Parameter(name='scene', in_=openapi.IN_QUERY, description='场景id', type=openapi.TYPE_STRING),
            openapi.Parameter(name='id', in_=openapi.IN_QUERY, description='场景配置id', type=openapi.TYPE_STRING),
        ])
    def get(self, request):
        try:
            data = request.GET
            page = int(data.get('page', 1))
            page_size = int(data.get('page_size', 15))
            if not data.get('scene'):
                return error_response('场景id为空')
            total, obm = api_list_query(data, page, page_size, SceneApiConf, 'sort', ['scene', 'id'], has_parent=True)
            try:
                api_conf_serialize = SceneApiConfSerializerQuery(obm, many=True)
                return_data = api_conf_serialize.data
                response = {
                    "data": return_data,
                    "page": page,
                    "total": total,
                    "asert_select_type": ASSERT_TYPE_SELECT,
                    "params_select_type": PARAMS_TYPE_SELECT
                }
                if len(return_data) == 1:
                    response['has_data'] = 1 if len(ApiParams.objects.filter(api_conf_id=return_data[0].get('id'))) > 0 else 0
            except Exception as _e:
                response = {}
            return success_response(data=response, msg='查询成功！')
        except Exception as e:
            return error_response('失败!')

    @swagger_auto_schema(
        operation_summary='场景配置api 单删群删',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'ids': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_STRING),
                                      description='需要删除的api场景配置 id列表 '),
            }))
    def delete(self, request):
        """场景配置api 单删群删"""
        try:
            with transaction.atomic():
                data = JSONParser().parse(request)
                delete_ids = data.get('ids')
                for id in delete_ids:
                    api_conf_obj = SceneApiConf.objects.filter(id=id)
                    if api_conf_obj:
                        # 校验下个接口是否使用了当前接口的返回参数 为入参的值
                        next_apt = SceneApiConf.objects.filter(scene=api_conf_obj.first().scene, sort=int(api_conf_obj.first().sort) + 1)
                        if next_apt:
                            putin_params_conf = next_apt.first().putin_params_conf
                            flag = juged_type(putin_params_conf)
                            if not flag:
                                raise DelException('DelException')
                        # 校验当前场景下 排序值大于当前接口 . 接口 排序值-1
                        all_scene_abj = SceneApiConf.objects.filter(scene=api_conf_obj.first().scene, sort__gt=api_conf_obj.first().sort)
                        for api_obj in all_scene_abj:
                            api_obj.sort = api_obj.sort - 1
                            api_obj.save()
                        ApiParams.objects.filter(api_conf_id=id).delete()
                        api_conf_obj.first().delete()
                    else:
                        return error_response(msg="数据错误!")
        except Exception as e:
            if str(e) == 'DelException':
                return error_response(msg='接口存在参数传递  无法删除: {}'.format(id))
            else:
                return error_response(msg='删除失败！')
        return success_response(data='', msg="成功!")

    @swagger_auto_schema(
        operation_summary='场景配置api 新增',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'scene': openapi.Schema(type=openapi.TYPE_INTEGER, description='场景id'),
                'api': openapi.Schema(type=openapi.TYPE_INTEGER, description='选择接口id'),
                'sort': openapi.Schema(type=openapi.TYPE_INTEGER, description='接口在场景中的排序值'),
                'putin_params_conf': openapi.Schema(type=openapi.TYPE_STRING, description='入参配置'),
                'asset_conf': openapi.Schema(type=openapi.TYPE_STRING, description='断言配置'),
                'remark': openapi.Schema(type=openapi.TYPE_STRING, description='备注')
            }
        )
    )
    def post(self, request):
        """场景信息 增加"""
        try:
            data = JSONParser().parse(request)
            # try:
            #     if data.get('putin_params_conf') and data.get('asset_conf'):
            #             data['putin_params_conf'] = json.dumps('putin_params_conf')
            #             data['asset_conf'] = json.dumps('asset_conf')
            # except:
            #     return error_response("配置字段参数传递错误！！！")
            api_conf_serializer = SceneApiConfSerializerAdd(data=data)
            if api_conf_serializer.is_valid():
                if data.get('sort') in [1, '1']:
                    flag = check_one_request_conf(eval(data.get('putin_params_conf')))
                    if not flag:
                        raise DelException('DelException')
                save_data = api_conf_serializer.save()
                return success_response(data={'id': save_data.id}, msg='新增场景api配置信息成功！')
            else:
                return error_response(msg=api_conf_serializer.errors)
        except Exception as e:
            if str(e) == 'DelException':
                return error_response(msg='入参配置错误!!')
            return error_response(msg='失败!!')

    @swagger_auto_schema(
        operation_summary='场景配置api 修改',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='配置id'),
                'scene': openapi.Schema(type=openapi.TYPE_INTEGER, description='场景id'),
                'api': openapi.Schema(type=openapi.TYPE_INTEGER, description='选择接口id'),
                'sort': openapi.Schema(type=openapi.TYPE_INTEGER, description='接口在场景中的排序值'),
                'putin_params_conf': openapi.Schema(type=openapi.TYPE_STRING, description='入参配置'),
                'asset_conf': openapi.Schema(type=openapi.TYPE_STRING, description='断言配置'),
                'remark': openapi.Schema(type=openapi.TYPE_STRING, description='备注')
            }
        )
    )
    def put(self, request):
        try:
            with transaction.atomic():
                data = JSONParser().parse(request)
                pk = data.get('id')
                if not pk:
                    return error_response(msg='id is None')
                api_conf_obj = SceneApiConf.objects.filter(id=pk).first()
                if api_conf_obj.api.id != data.get('api'):
                    return error_response("执行接口无法修改")


                api_conf_serializer = SceneApiConfSerializerAdd(instance=api_conf_obj, data=data)
                if api_conf_serializer.is_valid():
                    if data.get('sort') in [1, '1']:
                        flag = check_one_request_conf(eval(data.get('putin_params_conf')))
                        if not flag:
                            raise DelException('DelException')
                    save_data = api_conf_serializer.save()
                    print(model_to_dict(save_data))
                    # 判断当前配置是否存在参数
                    api_params_objs = ApiParams.objects.filter(api_conf_id=pk)
                    if (api_params_objs):
                        # 使当前修改conf匹配历史参数，未修改数据类型 且字段存在参数进行保存
                        putin_params_conf = eval(save_data.putin_params_conf)
                        asset_conf = eval(save_data.asset_conf)


                        params_obj = api_params_objs.first()
                        params_json = eval(params_obj.putin_params_json)
                        asset_json = eval(params_obj.asset_json)

                        check_has_history_data(putin_params_conf, params_json)

                        # for in_conf in putin_params_conf:
                        #     for params_data in params_json:
                        #         if in_conf['param'] == params_data['param'] and (in_conf['type']!='array' and not in_conf.get('children')):
                        #             in_conf['value'] = params_data.get('value') if params_data.get('value') else ''
                        #         elif in_conf['type'] == 'array' and in_conf.get('children') and params_data.get('children') and in_conf['param'] == params_data['param'] and params_data['type'] == 'array':
                        #             pass  # 开始递归

                        check_has_assert_history_data(asset_conf, asset_json)
                        # for in_assert in asset_conf:
                        #     for assert_data in asset_json:
                        #         if in_assert['param'] == assert_data['param']:
                        #             in_assert['value'] = assert_data.get('value') if assert_data.get('value') else ''

                        # 保存
                        # 删除当前配置已存在的请求参数, 更改配置 则已配置的请求参数无效
                        ApiParams.objects.filter(api_conf_id=pk).delete()

                        param_in = SceneApiConf.objects.get(id=pk).api.param_in
                        # param_in = ApiManage.objects.get(id = api_manage_id).param_in
                        end_request_json = {}
                        for param_position in eval(param_in):
                            resolver = Resolver(putin_params_conf, param_position)
                            data_dict = resolver.get_end_dict()
                            end_request_json[param_position] = data_dict
                        resolver_asset = AssertDataDealResolver(asset_conf)
                        data['end_asset_json'] = json.dumps(resolver_asset.get_end_list())
                        data['end_request_json'] = json.dumps(end_request_json)
                        data['putin_params_json'] = json.dumps(putin_params_conf)
                        data['asset_json'] = json.dumps(asset_conf)
                        data['api_conf_id'] = pk
                        api_params_serializer = ApiParamsSerializerAdd(data=data)
                        if api_params_serializer.is_valid():
                            save_params_data = api_params_serializer.save()
                        else:
                            raise Exception('validateError')


                    return success_response(data={'id': save_data.id}, msg="修改成功!!!")
                else:
                    return error_response(msg=api_conf_serializer.errors)
        except Exception as e:
            if str(e) == 'DelException':
                return error_response(msg='入参配置错误!!')
            return error_response(msg='失败!!')


class GetSceneApiConf(APIView):
    authentication_classes = ()
    permission_classes = []

    @swagger_auto_schema(
        operation_summary='获取接口入参断言配置, 以及上级接口的返回数据（若存在上级接口）',
        manual_parameters=[
            openapi.Parameter(name='id', in_=openapi.IN_QUERY, description='配置id', type=openapi.TYPE_STRING),
        ])
    def get(self, request):
        try:
            id = request.GET.get('id')
            query = SceneApiConf.objects.filter(id=id)
            if not (id and query):
                return error_response("id错误")
            # 查询该场景的当前接口的上级接口是否存在
            now_sort = query.first().sort
            now_scene = query.first().scene
            up_query = SceneApiConf.objects.filter(scene=now_scene.id, sort=int(now_sort)-1)
            up_api_rep_list = []
            # if up_query: # 存在上级接口
            #     up_serializer_obj = ApiManageSerializerConfQuery(up_query.first().api)
            #     rep_data = up_serializer_obj.data.get('response_params_ls')
            #     for i in rep_data:  # 将上层接口返回数据提供给当前接口入参
            #         if i.get('children') and i.get('type') == 'array':
            #             for children in i.get('children')[0]:  # 第一层列表下数据
            #                 up_api_rep_list.append('before_'+i.get('param') + '[].' + children.get('param'))
            #         else:
            #             up_api_rep_list.append('before_'+i.get('param'))
            serializer_obj = SceneGetOneConf(query.first())
            data_dict = serializer_obj.data
            data_dict['up_rep_key'] = up_api_rep_list
            data_dict['bool_type_select'] = BOOL_VALUE_SELECT
            return success_response(data=data_dict, msg='成功!')
        except Exception as e:
            return error_response(msg='失败!!')


class SceneConfExchange(APIView):
    authentication_classes = ()
    permission_classes = []

    @swagger_auto_schema(
        operation_summary='接口交换位置',
        manual_parameters=[
            openapi.Parameter(name='AUTHORIZATION', in_=openapi.IN_HEADER, description='登录验证', type=openapi.TYPE_STRING),
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'ids': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_STRING),
                                      description='需要交换顺序的两个配置 id')
            })
    )
    def post(self, request):
        try:
            data = JSONParser().parse(request)
            ids = data.get('ids')
            id_1 = ids[0]
            id_2 = ids[1]
            one_scene_obj = SceneApiConf.objects.get(id=id_1)
            two_scene_obj = SceneApiConf.objects.get(id=id_2)
            one_scene_obj.sort, two_scene_obj.sort = two_scene_obj.sort, one_scene_obj.sort
            one_scene_obj.save()
            two_scene_obj.save()
            return success_response(data='', msg='成功!')
        except Exception as e:
            return error_response(msg='失败!!')
