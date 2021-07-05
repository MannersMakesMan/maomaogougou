import json
import re
import time
from rest_framework import serializers

# from zy_api_testing.models import SceneApiConf, ApiManage, DataManage, Scene, ApiParams
from system_settings.models import Dataexplain, DataDictionary
from zy_api_testing.models import SceneApiConf, ApiManage, Scene, ApiParams, PARAMS_POSITION_LIST, SingleApiParams
from zy_api_testing.tools import DealRequestConf, deal_api_params, MakeDataParamStructure, DealRequestJsonPartData


class ApiManageSerializerModify(serializers.ModelSerializer):
    # api
    server = serializers.CharField(required=True, error_messages={'required': '所属服务名 不能为空'})
    tag = serializers.CharField(required=True, error_messages={'required': '所属tag 不能为空'})
    path = serializers.CharField(required=True, error_messages={'required': 'api地址 不能为空'})
    api_desc = serializers.CharField(required=True, error_messages={'required': '注释 不能为空'})
    tag_english_desc = serializers.CharField(required=False)
    request_method = serializers.CharField(required=True, error_messages={'required': '请求方式 不能为空'})
    request_params_json = serializers.CharField(required=True, error_messages={'required': '请求参数模板 不能为空'})
    response_params_json = serializers.CharField(required=True, error_messages={'required': '返回参数模板 不能为空'})
    param_in = serializers.CharField(required=True, error_messages={'required': '请求参数所在位置 不能为空'})
    # request_params_json = serializers.SerializerMethodField()
    # response_params_json = serializers.SerializerMethodField()
    deprecated = serializers.IntegerField(required=False, min_value=0, max_value=1, error_messages={'min_value': '是否弃用 请输入0-1之间的值',
                                                                                                    'max_value': '是否弃用 请输入0-1之间的值'})
    exception_flag = serializers.IntegerField(required=False, min_value=0, max_value=1, error_messages={'min_value': '是否弃用 请输入0-1之间的值',
                                                                                                    'max_value': '是否弃用 请输入0-1之间的值'})
    id = serializers.IntegerField(required=False)

    def validate_param_in(self, param_in):
        return param_in.replace('"', "'")

    def validate_request_params_json(self, request_params_json):
        try:
            request_params_ls = {}
            request_params_json = request_params_json.replace('0,', '"",')
            request_params_json = request_params_json.replace('0}', '""}')
            request_params_json = request_params_json.replace('true,', '"",')
            request_params_json = request_params_json.replace('None,', '"",')
            request_params_json = request_params_json.replace('None}', '""}')
            request_params_json = request_params_json.replace('true}', '""}')
            for params_position, request_data in eval(request_params_json).items():
                if params_position not in PARAMS_POSITION_LIST:
                    raise serializers.ValidationError('手动添加/修改 请求参数 所在位置错误')
                structure = MakeDataParamStructure(request_data)
                data = structure.get_data()
                print(data)
                deal = DealRequestJsonPartData(data)
                one_part_data = deal.get_data()
                request_params_ls[params_position] = one_part_data
            self.initial_data['request_params_ls'] = json.dumps(request_params_ls)
            return request_params_json
        except Exception as e:
            raise serializers.ValidationError('手动添加/修改 入参json格式错误')

    def validate_response_params_json(self, response_params_json):
        try:
            if response_params_json == '{}' or response_params_json == '':
                raise Exception('Not Has Param')
                # return response_params_json
            response_params_json = response_params_json.replace('0,', '"",')
            response_params_json = response_params_json.replace('0}', '""}')
            response_params_json = response_params_json.replace('true,', '"",')
            response_params_json = response_params_json.replace('None,', '"",')
            response_params_json = response_params_json.replace('None}', '""}')
            response_params_json = response_params_json.replace('true}', '""}')
            response_params_json = response_params_json.replace('[null]', '[""]')
            response_params_json = response_params_json.replace('null,', '"",')
            response_params_json = response_params_json.replace('null}', '""}')
            structure = MakeDataParamStructure(eval(response_params_json))
            data = structure.get_data()
            print(data)
            deal = DealRequestJsonPartData(data)
            response_params_ls = deal.get_data()
            self.initial_data['response_params_ls'] = json.dumps(response_params_ls)
            return response_params_json
        except Exception as e:
            if str(e) == 'Not Has Param':
                raise serializers.ValidationError('出参不能无参数')
            raise serializers.ValidationError('出参json格式错误')

    class Meta:
        model = ApiManage
        fields = (
            'id', 'server', 'tag', 'path', 'api_desc', 'tag_english_desc', 'exception_flag', 'exception_log', 'request_method', 'request_params_json', 'param_in', 'response_params_json', 'request_params_ls', 'deprecated', 'has_manual', 'response_params_ls'
        )


class ApiManageSerializerQuery(serializers.ModelSerializer):

    path = serializers.CharField()
    request_params_swagger = serializers.SerializerMethodField()
    response_params_swagger = serializers.SerializerMethodField()
    request_params_json = serializers.SerializerMethodField()
    response_params_json = serializers.SerializerMethodField()
    param_in = serializers.SerializerMethodField()

    def get_param_in(self, obj):
        return eval(obj.param_in)

    def get_response_params_swagger(self, obj):
        end_data = {}
        try:
            data = eval(obj.response_params_swagger)
            failed_item = {}
            success_item = {}
            for key, value in data.items():
                if key != '200':
                    failed_item[key] = value
                else:
                    success_item[key] = value
            end_data['success_response'] = success_item
            end_data['failed_response'] = failed_item
        except Exception as e:
            return end_data
        return end_data

    def get_request_params_swagger(self, obj):
        end_data = {}
        try:
            data = eval(obj.request_params_swagger)
            for key, value in data.items():
                if key != 'header':
                    end_data[key] = value
        except Exception as e:
            return end_data
        return end_data

    def get_request_params_json(self, obj):
        try:
            data = eval(obj.request_params_json)
        except Exception as e:
            data = {}
        return data

    def get_response_params_json(self, obj):
        try:
            data = eval(obj.response_params_json)
        except Exception as e:
            data = {}
        return data

    class Meta:
        model = ApiManage
        fields = (
            'id', 'server', 'tag', 'path', 'api_desc', 'tag_english_desc', 'has_manual', 'request_method', 'request_params_swagger', 'response_params_swagger', 'update_time', 'request_params_json', 'response_params_json', 'deprecated', 'exception_flag', 'param_in', 'exception_log'
        )

class ApiManageSerializerConfQuery(serializers.ModelSerializer):
    request_params_ls = serializers.SerializerMethodField()
    response_params_ls = serializers.SerializerMethodField()
    request_params_json = serializers.SerializerMethodField()
    response_params_json = serializers.SerializerMethodField()


    def get_request_params_json(self, obj):
        data = eval(obj.request_params_json)
        return data

    def get_response_params_json(self, obj):
        data = eval(obj.response_params_json)
        return data

    def get_request_params_ls(self, obj):
        request_params = obj.request_params_ls
        params_conf_ls = []
        if request_params and request_params != '{}':
            for params_position in eval(obj.param_in):
                if params_position != 'header':
                    deal_params = DealRequestConf(eval(obj.request_params_ls).get(params_position), 'request_ls', params_position)
                    request_params = deal_params.get_data()
                    params_conf_ls.extend(request_params)
        return params_conf_ls

    def get_response_params_ls(self, obj):
        response_params_ls = obj.response_params_ls
        if response_params_ls and response_params_ls != '{}':
            try:
                deal_params = DealRequestConf(eval(obj.response_params_ls), 'assert')
                response_params_ls = deal_params.get_data()
            # print(request_params)
            except Exception as e:
                print(obj.path)
        # print(request_params)
        return response_params_ls

    # def get_asdas(self,obj):
    #     return obj.asdas
    def get_response_params_swagger(self, obj):
        data = eval(obj.response_params_swagger)
        end_data = {}
        failed_item = {}
        success_item = {}
        for key, value in data.items():
            if key != '200':
                failed_item[key] = value
            else:
                success_item[key] = value
        end_data['success_response'] = success_item
        # end_data['failed_response'] = failed_item
        return end_data

    def get_request_params_swagger(self, obj):
        data = eval(obj.request_params_swagger)
        end_data = {}
        for key, value in data.items():
            if key != 'header':
                end_data[key] = value
        return end_data

    class Meta:
        model = ApiManage
        fields = (
            'id', 'param_in', 'request_params_ls', 'response_params_ls', 'request_params_json', 'has_manual', 'response_params_json', 'path', 'api_desc'
        )


class ApiManageSerializerAdd(serializers.ModelSerializer):
    # api详情 添加
    class Meta:
        model = ApiManage
        fields = (
            'id', 'response_params_ls', 'param_in', 'request_params_ls', 'server', 'tag', 'path', 'api_desc', 'tag_english_desc', 'request_method', 'request_params_swagger', 'response_params_swagger', 'update_time', 'request_params_json', 'response_params_json', 'deprecated', 'exception_flag', 'exception_log'
        )


class SerializerQueryAllApi(serializers.ModelSerializer):
    api_desc = serializers.SerializerMethodField()

    def get_api_desc(self, obj):
        data = obj.api_desc.replace(' ', '') + obj.path
        return data

    class Meta:
        model = ApiManage
        fields = (
            'id',  'api_desc'
        )


class SceneApiConfSerializerQuery(serializers.ModelSerializer):

    scene = serializers.SerializerMethodField()
    api = serializers.SerializerMethodField()
    sort = serializers.IntegerField()
    putin_params_conf = serializers.CharField()
    asset_conf = serializers.CharField()
    update_time = serializers.DateTimeField()
    create_time = serializers.DateTimeField()
    remark = serializers.CharField()

    def get_api(self, obj):
        if obj.api:
            data = ApiManageSerializerQuery(obj.api).data
            return {
                'id': data.get('id'),
                'path': data.get('path'),
                'api_desc': data.get('api_desc'),
                'request_method': data.get('request_method'),
                'request_params_json': data.get('request_params_json'),
                'response_params_json': data.get('response_params_json')
            }
        else:
            return None

    def get_scene(self, obj):
        if obj.scene:
            return obj.scene.id
        else:
            return None


    class Meta:
        model = SceneApiConf
        fields = (
            'id', 'scene', 'api', 'sort', 'putin_params_conf', 'asset_conf', 'create_time', 'update_time', 'remark'
        )


class SceneGetOneConf(serializers.ModelSerializer):
    putin_params_conf = serializers.SerializerMethodField()
    asset_conf = serializers.SerializerMethodField()
    sort = serializers.IntegerField()

    def get_putin_params_conf(self, obj):
        if obj.putin_params_conf:
            try:
                return eval(obj.putin_params_conf)
            except:
                return []
        else:
            return None

    def get_asset_conf(self, obj):
        if obj.asset_conf:
            try:
                return eval(obj.asset_conf)
            except:
                return []
        else:
            return None

    class Meta:
        model = SceneApiConf
        fields = (
            'id',  'sort', 'putin_params_conf', 'asset_conf'
        )


class SceneApiConfSerializerAdd(serializers.ModelSerializer):
    scene = serializers.IntegerField(required=True, error_messages={'required': '场景id不能为空！'})
    api = serializers.IntegerField(required=True, error_messages={'required': '接口id不能为空！'})
    sort = serializers.IntegerField(required=True, min_value=1, max_value=99999,
                                    error_messages={
                                        'required': 'sort不能为空！','min_value': '排序值 请输入1-99999',
                                                    'max_value': '排序值 请输入1~99999！'})
    putin_params_conf = serializers.CharField()
    asset_conf = serializers.CharField()
    remark = serializers.CharField(required=False, min_length=1, max_length=255,
                                   error_messages={'min_value': '备注 请输入1-255长度的字符',
                                                   'max_length': '备注 请输入1~255个字符！'})

    def validate_scene(self, scene):
        if not Scene.objects.filter(id=scene):
            raise serializers.ValidationError('不存在该场景')
        return Scene.objects.filter(id=scene).first()

    def validate_api(self, api):
        if not ApiManage.objects.filter(id=api):
            raise serializers.ValidationError('不存在该接口')
        return ApiManage.objects.filter(id=api).first()

    def validate_putin_params_conf(self, putin_params_conf):

        return putin_params_conf

    def validate_asset_conf(self, asset_conf):
        # 断言配置处校验  type 为 boolean  时 不允许assert_type  修改为 in
        try:
            asset_conf = eval(asset_conf)
            # for asset in asset_conf:
            #     if asset.get('type') == 'boolean' and asset.get('assert_type') == 'in':
            flag = check_asser_type(asset_conf)
            if not flag:
                raise Exception('boolean_in')
        except Exception as e:
            if str(e) == 'boolean_in':
                raise serializers.ValidationError('断言配置错误 : 断言数据类型为boolean时, 断言类型不能为in')
            else:
                raise serializers.ValidationError('断言配置错误')
        return json.dumps(asset_conf)
    class Meta:
        model = SceneApiConf
        fields = (
        'scene', 'api', 'sort', 'putin_params_conf', 'asset_conf', 'remark'
        )



def check_asser_type(accert_list):
    for asset in accert_list:
        if asset.get('type') == 'array' and asset.get('children'):
            flag = check_asser_type(asset.get('children'))
            if flag:
                return True
            else:
                return False
        if asset.get('type') == 'boolean' and asset.get('assert_type') == 'in':
            return False
    return True
    # def validate(self, attrs):
    #     # 判断该场景是否需要登录 & 当前新增场景接口配置是否为场景下第一个接口  再校验当前接口是否为登录接口
    #     scene = attrs['scene']
    #     api = attrs['api']
    #     sort = attrs['sort']
    #     if Scene.objects.get(id=scene).need_login == 1 and sort == 1:
    #         # 场景需要登录 且为场景下第一个接口
    #         path = ApiManage.objects.get(id=api).path  # 获取当前接口 路径
    #         try:
    #             data_id = Dataexplain.objects.get(dictionary_code='A0000001').id   # 获取登录配置id
    #             login_api_path = DataDictionary.objects.get(Dataexplain_id=data_id, DictionarySubitem_code='a0000001').dictionary_item1
    #         except:
    #             raise serializers.ValidationError('错误!! 请检查登录接口配置')
    #         if path != login_api_path:
    #             raise serializers.ValidationError('该场景配置为需要登录 ,第一个接口为登录接口，请检查！！！')
    #     return attrs




class ApiParamsSerializerAdd(serializers.ModelSerializer):
    api_conf_id = serializers.IntegerField()
    putin_params_json = serializers.CharField(required=True, error_messages={'required': '请求参数不能为空'})
    asset_json = serializers.CharField(required=True, error_messages={'required': '断言参数不能为空'})
    end_request_json = serializers.CharField(required=True, error_messages={'required': '解析最终参数错误'})
    end_asset_json = serializers.CharField(required=True, error_messages={'required': '解析最终断言参数错误'})
    # sort = serializers.IntegerField(required=True, min_value=1, max_value=99999,
    #                                 error_messages={
    #                                     'required': 'sort不能为空！', 'min_value': '排序值 请输入1-99999',
    #                                                 'max_value': '排序值 请输入1~99999！'})

    def validate_api_conf_id(self, api_conf_id):
        if not SceneApiConf.objects.filter(id=api_conf_id):
            raise serializers.ValidationError('api_id 错误')
        return SceneApiConf.objects.filter(id=api_conf_id).first()

    class Meta:
        model = ApiParams
        fields = (
            'api_conf_id', 'putin_params_json', 'asset_json', 'end_request_json', 'end_asset_json', 'sort'
        )

class SingleApiParamsSerializerAdd(serializers.ModelSerializer):
    putin_params_json = serializers.CharField(required=True, error_messages={'required': '请求参数不能为空'})
    req_table_data = serializers.CharField(required=True, error_messages={'required': '请求参数不能为空(前端兼容数据)'})
    rep_table_data = serializers.CharField(required=True, error_messages={'required': '请求参数不能为空(前端兼容数据)'})
    asset_json = serializers.CharField(required=True, error_messages={'required': '断言参数不能为空'})
    end_request_json = serializers.CharField(required=True, error_messages={'required': '解析最终参数错误'})
    end_asset_json = serializers.CharField(required=True, error_messages={'required': '解析最终断言参数错误'})
    sort = serializers.IntegerField(required=True, min_value=1, max_value=99999,
                                    error_messages={
                                        'required': 'sort不能为空！', 'min_value': '排序值 请输入1-99999',
                                                    'max_value': '排序值 请输入1~99999！'})
    api = serializers.IntegerField(required=True, error_messages={'required': '所属API 不能为空'})

    def validate_api(self, api):
        if not ApiManage.objects.filter(id=api):
            raise serializers.ValidationError('api_id 错误')
        return ApiManage.objects.filter(id=api).first()

    class Meta:
        model = SingleApiParams
        fields = (
            'putin_params_json', 'asset_json', 'end_request_json', 'end_asset_json', 'req_table_data', 'rep_table_data', 'sort', 'api'
        )



class SceneSerializerQuery(serializers.ModelSerializer):
    # 业务场景查询 表单验证 序列化
    professional_name = serializers.CharField()
    scene_name = serializers.CharField()
    scene_desc = serializers.CharField()
    remark = serializers.CharField()
    update_time = serializers.DateTimeField()
    need_login = serializers.IntegerField()

    class Meta:
        model = Scene
        fields = ('id', 'professional_name', 'scene_name', 'scene_desc', 'remark', 'need_login', 'update_time')


class SceneSerializerAdd(serializers.ModelSerializer):
    # 业务场景 添加&修改 表单验证 反序列化
    professional_name = serializers.CharField(required=True, min_length=1, max_length=200, error_messages={'required': '业务名称 不能为空',
                                                                                                           'min_value': '业务名称 请输入1-20长度的字符',
                                                                                                           'max_value': '业务名称 请输入1-20长度的字符'})
    scene_name = serializers.CharField(required=True, min_length=1, max_length=200, error_messages={'required': '场景名称 不能为空',
                                                                                                    'min_value': '场景名称 请输入1-20长度的字符',
                                                                                                    'max_value': '场景名称 请输入1-20长度的字符'})

    need_login = serializers.IntegerField(required=True, min_value=0, max_value=1, error_messages={'required': '场景登录 不能为空',
                                                                                                 'min_value': '场景登录 请输入0-1之间的值',
                                                                                                 'max_value': '场景登录 请输入0-1之间的值'})

    def validate_scene_name(self, scene_name):
        if not self.initial_data.get("id"):
            if Scene.objects.filter(scene_name=scene_name, professional_name=self.initial_data.get("professional_name")):
                raise serializers.ValidationError('同一业务下场景名称不能重复')
        else:
            if Scene.objects.filter(scene_name=scene_name, professional_name=self.initial_data.get("professional_name")).exclude(id=self.initial_data.get("id")).all():
                raise serializers.ValidationError('同一业务下场景名称不能重复')
        return scene_name

    class Meta:
        model = Scene
        fields = ('professional_name', 'scene_name', 'scene_desc', 'remark', 'need_login')


class ApiParamsSerializerQuery(serializers.ModelSerializer):


    class Meta:
        model = ApiParams
        fields = (
            'api_conf_id', 'putin_params_json', 'asset_json', 'end_request_json', 'end_asset_json', 'sort'
        )

class QueryApiParamsSerializer(serializers.ModelSerializer):
    # 场景测试 配置数据查询
    putin_params_json = serializers.SerializerMethodField()
    asset_json = serializers.SerializerMethodField()

    def get_putin_params_json(self, obj):
        try:
            return eval(obj.putin_params_json)
        except:
            return None

    def get_asset_json(self, obj):
        try:
            return eval(obj.asset_json)
        except:
            return None


    class Meta:
        model = ApiParams
        fields = (
            'api_conf_id', 'putin_params_json', 'asset_json', 'id'
        )


class QuerySingleApiParamsSerializer(serializers.ModelSerializer):
    # 单接口测试 配置数据查询
    req_table_data = serializers.SerializerMethodField()
    rep_table_data = serializers.SerializerMethodField()

    def get_req_table_data(self, obj):
        try:
            return eval(obj.req_table_data)
        except:
            return None

    def get_rep_table_data(self, obj):
        try:
            return eval(obj.rep_table_data)
        except:
            return None

    class Meta:
        model = SingleApiParams
        fields = (
            'api_id', 'req_table_data', 'rep_table_data', 'id'
        )

#
# class DataManageSerializerQuery(serializers.ModelSerializer):
#     # 测试数据查询 表单验证 序列化
#     api_name = serializers.CharField()
#     scene_name = serializers.CharField()
#     api_description = serializers.CharField()
#     sever_name = serializers.CharField()
#     founder = serializers.CharField()
#     update_time = serializers.DateTimeField()
#     Remark = serializers.CharField()
#
#     class Meta:
#         model = DataManage
#         fields = ('id', 'api_name', 'scene_name', 'api_description', 'sever_name', 'founder', 'update_time', 'Remark')
#
#
# class DataManageSerializerAdd(serializers.ModelSerializer):
#     # 测试数据 修改 表单验证 反序列化
#     api_description = serializers.CharField(required=True, error_messages={'required': '接口描述 不能为空'})
#     sever_name = serializers.CharField(required=True, error_messages={'required': '服务名称 不能为空'})
#     founder = serializers.CharField(required=True, min_length=1, max_length=20, error_messages={'required': '创建者 不能为空',
#                                                                                                 'min_value': '创建者 请输入1-20长度的字符',
#                                                                                                 'max_value': '创建者 请输入1-20长度的字符'})
#     Remark = serializers.CharField(required=True)
#
#     class Meta:
#         model = DataManage
#         fields = ('api_description', 'sever_name', 'founder', 'Remark')

# api  数据管理页面 查询相关序列化器
class ApiDataSceneApiConfSerializerQuery(serializers.ModelSerializer):

    scene = serializers.SerializerMethodField()
    api = serializers.SerializerMethodField()
    sort = serializers.IntegerField()
    update_time = serializers.DateTimeField()
    remark = serializers.CharField()

    def get_api(self, obj):
        if obj.api:
            data = ApiManageSerializerQuery(obj.api).data
            api_param = ApiParamsSerializerQuery(ApiParams.objects.filter(api_conf_id=obj.id).order_by('sort'), many=True)  # 按照sort顺时查询
            if len(api_param.data) == 0:
                putin_ls = eval(obj.putin_params_conf)
                assert_ls = eval(obj.asset_conf)
            else:
                putin_ls, assert_ls = deal_api_params(api_param.data)
            return {
                'id': data.get('id'),
                'api_desc': data.get('api_desc'),
                'children': {
                    'putin_ls': putin_ls,
                    'assert_ls': assert_ls
                },
            }
        else:
            return None

    def get_scene(self, obj):
        if obj.scene:
            return {
            'id': obj.scene.id,
            'scene_name': obj.scene.scene_name,
            'professional_name': obj.scene.professional_name
            }
        else:
            return None


    class Meta:
        model = SceneApiConf
        fields = (
            'id', 'scene', 'api', 'sort', 'update_time', 'remark'
        )
