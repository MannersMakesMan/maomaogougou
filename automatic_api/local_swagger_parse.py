import json
from copy import deepcopy

import requests

from zy_api_testing.models import ApiManage
from zy_api_testing.serializers import ApiManageSerializerAdd


class AnalysisSwaggerJson:
    def __init__(self, swagger_url):
        self.swagger_url = swagger_url

        # self.model_suffix = ['对象', "»»", "»"]

        # self.swagger_dic = json.loads(open('zhongyin_swagger.json', encoding='gbk').read())
        self.swagger_dic = {}
        # 临时写法
        self.host_url = ''
        # 路由地址
        self.all_api_detail = []
        # 存储解析后的 api参数详情
        self.exception_logs = []
        # 接口解析 错误信息存储

    def req_swagger(self):
        # 请求swagger 返回json
        try:
            if '/v2/api-docs' not in self.swagger_url:
                self.swagger_url = self.swagger_url + '/v2/api-docs'
            rep = requests.get(self.swagger_url, timeout=2)  # 这才是swagger接口请求的地址
            if rep.status_code == 200:
                # a = eval(rep.text)
                self.swagger_dic = rep.json()

        except Exception as e:
            return {'exception_log': '请求swagger地址错误. url: {},  异常如下: {}'.format(self.swagger_url, e)}
        add_api_manage_data = self.swagger_json_parse()
        return {'swagger_json': self.swagger_dic, 'exception_log': '\n'.join(self.exception_logs), "add_api_ls": add_api_manage_data}

    def param_dic_scann(self, model_dic, new_param_structure, last_model_name=''):
        # 递归提取model 拼接为swagger原生结构
        global break_flag, is_map_param
        if not break_flag:
            return 'maximum recursion'

        else:
            params_dic = model_dic['properties']
            for param in params_dic:
                param_dic = params_dic[param]

                if '$ref' in param_dic:
                    model_name = param_dic['$ref']
                    if model_name == last_model_name:
                        # 出现相同model_name 退出递归
                        break_flag = False

                    param_dic['items'] = deepcopy(self.get_model_dic(param_dic['$ref']))
                    new_param_structure[param] = {"type": 'object', 'items': {}}
                    self.param_dic_scann(param_dic['items'], new_param_structure[param]['items'], model_name)

                elif param_dic['type'] == 'array':
                    if '$ref' in param_dic['items']:
                        model_name = param_dic['items']['$ref']
                        if model_name == last_model_name:
                            # 出现相同model_name 退出递归
                            break_flag = False
                        param_dic['items'] = deepcopy(self.get_model_dic(param_dic['items']['$ref']))
                        new_param_structure[param] = {"type": param_dic['type'], 'items': {}}
                        if 'additionalProperties' not in param_dic['items']:
                            self.param_dic_scann(param_dic['items'], new_param_structure[param]['items'], model_name)
                        else:
                            is_map_param = True
                    else:
                        new_param_structure[param] = {"type": param_dic['type'], 'items': param_dic['items']}
                elif param_dic['type'] == 'object':
                    if 'additionalProperties' not in param_dic:
                        new_param_structure[param] = param_dic
                        print(14)
                    else:
                        new_param_structure[param] = {"type": param_dic['type'], 'items': {}}
                        is_map_param = True
                else:
                    new_param_structure[param] = param_dic

    def param_ls_scann(self, model_dic, new_param_ls, ahead_param=''):
        # 递归将swagger接口信息原生格式 转换为 同层级接口参数字典
        for param in model_dic:
            param_dic = model_dic[param]

            level_param = "{}.{}".format(ahead_param, param) if ahead_param else param
            level_param_dict = {
                "value": None,
                'type': param_dic['type'] if 'type' in param_dic else 'object',
                'description': param_dic['description'] if 'description' in param_dic else '',
                'example': param_dic['example'] if 'example' in param_dic else '',
                'format': param_dic['format'] if 'format' in param_dic else '',
            }
            if param_dic['type'] == 'array':
                if 'items' in param_dic:
                    # a = eval(str([param_dic['items']]).replace("'items'", "'value'"))
                    if 'type' in param_dic['items']:
                        level_param_dict["value"] = [param_dic['items']]
                        new_param_ls[level_param] = level_param_dict
                    else:
                        # level_param_dict["value"] = [param_dic['items']]
                        level_param_dict["value"] = [{}]
                        self.param_ls_scann(param_dic['items'], level_param_dict["value"][0])
                        new_param_ls[level_param] = level_param_dict


            elif param_dic['type'] == 'object':
                if 'items' in param_dic:
                    # level_param_dict["value"] = param_dic['items']
                    self.param_ls_scann(param_dic['items'], new_param_ls, ahead_param=level_param)

            # elif 'properties' in param_dic:
            #     self.param_ls_scann(param_dic, new_param_ls, ahead_param=level_param)
            else:
                new_param_ls[level_param] = level_param_dict

    # def param_json_scann(self, model_dic, new_param_json):
    #     # 递归将swagger原生接口信息 转换为直接可以请求的json
    #
    #     params_dic = model_dic['properties']
    #     for param in params_dic:
    #         param_dic = params_dic[param]
    #         param_dic['type'] = param_dic['type'] if 'type' in param_dic else 'object'
    #         if param_dic['type'] == 'array':
    #             if 'properties' in param_dic['items']:
    #                 new_param_json[param] = [{}]
    #                 self.param_json_scann(param_dic['items'], new_param_json[param][0])
    #             else:
    #                 new_param_json[param] = ['{}'.format(param_dic['items']['type'])]
    #
    #         elif param_dic['type'] == 'object':
    #             if 'items' in param_dic:
    #                 if 'properties' in param_dic['items']:
    #                     new_param_json[param] = {}
    #                     self.param_json_scann(param_dic['items'], new_param_json[param])
    #                 else:
    #                     print(12)
    #             elif 'additionalProperties' in param_dic:
    #                 if 'properties' in param_dic['additionalProperties']:
    #                     new_param_json[param] = {}
    #                     self.param_json_scann(param_dic['additionalProperties'], new_param_json[param])
    #                 else:
    #                     new_param_json[param] = {param_dic['additionalProperties']['type']}
    #
    #         elif 'properties' in param_dic:
    #             new_param_json[param] = {}
    #             self.param_json_scann(param_dic['items'], new_param_json[param])
    #
    #         else:
    #             new_param_json[param] = '{}'.format(param_dic['type'])

    def param_json_scann(self, model_dic, new_param_json):
        # 递归将swagger原生接口信息 转换为直接可以请求的json
        global is_map_param, is_map_param
        params_dic = model_dic['properties']
        for param in params_dic:
            param_dic = params_dic[param]
            param_dic['type'] = param_dic['type'] if 'type' in param_dic else 'object'
            param_dic['description'] = param_dic['description'] if 'description' in param_dic else 'None'
            param_dic['format'] = param_dic['format'] if 'format' in param_dic else 'None'
            if param_dic['type'] == 'array':
                if 'properties' in param_dic['items']:
                    new_param_json[param] = [{}]
                    self.param_json_scann(param_dic['items'], new_param_json[param][0])
                else:
                    param_dic['items']['format'] = param_dic['items']['format'] if 'format' in param_dic['items'] else 'None'
                    param_dic['items']['description'] = param_dic['items']['description'] if 'description' in param_dic['items'] else 'None'
                    param_dic['items']['type'] = param_dic['items']['type'] if 'type' in param_dic['items'] else 'object'
                    new_param_json[param] = ['{}-{}-{}'.format(param_dic['items']['type'], param_dic['items']['format'], param_dic['items']['description'])]

            elif param_dic['type'] == 'object':
                if 'items' in param_dic:
                    if 'properties' in param_dic['items']:
                        new_param_json[param] = {}
                        self.param_json_scann(param_dic['items'], new_param_json[param])
                    else:
                        if 'additionalProperties' in param_dic:
                            is_map_param = True
                        else:
                            print(12)
                elif 'additionalProperties' in param_dic:
                    is_map_param = True
                    if 'properties' in param_dic['additionalProperties']:
                        new_param_json[param] = {}
                        self.param_json_scann(param_dic['additionalProperties'], new_param_json[param])
                    else:
                        param_dic['additionalProperties']['format'] = param_dic['additionalProperties']['format'] if 'format' in param_dic['additionalProperties'] else 'None'
                        param_dic['additionalProperties']['description'] = param_dic['additionalProperties']['description'] if 'description' in param_dic['additionalProperties'] else 'None'
                        new_param_json[param] = {}
                else:
                    new_param_json[param] = {}
                    print(11)

            elif 'properties' in param_dic:
                new_param_json[param] = {}
                self.param_json_scann(param_dic['items'], new_param_json[param])

            else:
                new_param_json[param] = '{}-{}-{}'.format(param_dic['type'], param_dic['format'], param_dic['description'])

    def get_model_dic(self, model_name):
        # 提取参数model
        if '#/definitions/' in model_name:
            model_name = model_name.replace('#/definitions/', '')
        if model_name not in self.api_param_models:
            model_name = model_name + '对象'
            if model_name not in self.api_param_models:
                model_name = model_name + '»'
                # if model_name not in self.api_param_models:
                #     return False
        return self.api_param_models[model_name]

    def swagger_json_parse(self):
        server_name = 'default' if self.swagger_dic['basePath'] == '/' else self.swagger_dic['basePath'].replace('/', '')
        # 服务名
        self.host_url = self.swagger_dic['host'] if server_name == 'default' else self.swagger_dic['host'] + '/' + server_name
        # 路由地址
        self.tag_ls = {i['name']: i['description'] for i in self.swagger_dic['tags']}

        api_details = self.swagger_dic['paths']
        # 原生swagger 每个api的详情数据
        self.api_param_models = self.swagger_dic['definitions']
        # 原生swagger api参数model数据
        for api_url in api_details:
            for request_method in api_details[api_url]:
                api_detail_template = {
                    "path": '',
                    # 路由地址
                    "tag": '',
                    # 所属tag
                    "tag_english_desc": '',
                    # 所属tag英文
                    "server": '',
                    # 所属服务
                    "api_desc": '',
                    # api功能注释
                    "request_method": '',
                    # 请求方式
                    'param_in': [],
                    # 参数所在位置 body/query/path/headers...

                    'headers': [],
                    # 请求头

                    "request_params_swagger": {},
                    # 请求参数 原生swagger格式
                    "request_params_json": {},
                    # 请求参数 json格式 直接可以请求
                    "request_params_ls": {},
                    # 请求参数 全部参数数据字典

                    "response_params_swagger": {},
                    # 返回参数 原生swagger格式
                    "response_params_json": {},
                    # 返回参数 json格式
                    "response_params_ls": {},
                    # 返回参数 全部参数数据字典

                    "deprecated": False,
                    # 是否已弃用
                    "exception_flag": 1,
                    # 接口数据是否可用
                    "exception_log": '',
                    # 接口数据问题日志
                }
                # 解析后的api详情模板 初始化
                swagger_api_dic = api_details[api_url][request_method]
                # 请求方式
                api_detail_template['request_method'] = request_method
                api_detail_template['server'] = server_name
                api_detail_template['tag'] = swagger_api_dic['tags'][0]
                api_detail_template['tag_english_desc'] = self.tag_ls[api_detail_template['tag']]
                api_detail_template['api_desc'] = swagger_api_dic['summary']
                api_detail_template['path'] = api_url
                api_detail_template['deprecated'] = 1 if swagger_api_dic['deprecated'] else 0

                new_param_ls = {}
                new_param_structure = {}
                new_param_json = {}
                new_rep_param_ls = {}
                new_rep_param_structure = {}
                new_rep_param_json = {}
                global break_flag, is_map_param
                break_flag = True
                # 接口是否执行递归扫描的标志
                is_map_param = False

                if api_url == "/common/updateAudit/{tableName}/{id}":
                    print(1)

                if 'parameters' not in swagger_api_dic:
                    self.exception_logs.append('tag:{}, path:{} 缺失请求参数字段 parameters'.format(api_detail_template['tag'], api_url))
                    api_detail_template['exception_flag'] = 0
                    api_detail_template['exception_log'] += '\n' + '缺失请求参数字段 parameters'
                    continue
                for swagger_param_dic in swagger_api_dic['parameters']:
                    if 'in' not in swagger_param_dic:
                        self.exception_logs.append(
                            'tag:{}, path:{} 请求参数{} 缺失必要字段 in'.format(api_detail_template['tag'], api_url,
                                                                      swagger_param_dic['name']))
                        api_detail_template['exception_flag'] = 0
                        api_detail_template['exception_log'] += '\n' + '请求参数{} 缺失必要字段 in'.format(swagger_param_dic['name'])
                        continue
                    swagger_param_in = swagger_param_dic['in']
                    # 参数所在位置 body/query/header/path
                    if swagger_param_in not in api_detail_template['param_in']:
                        api_detail_template['param_in'].append(swagger_param_in)

                    if swagger_param_in in ['query', 'path', 'header', 'formData']:
                        # 参数位置在 query path header formData 中 保留全部参数
                        param = swagger_param_dic['name']
                        del swagger_param_dic['name']
                        del swagger_param_dic['in']

                        if swagger_param_in not in api_detail_template['request_params_swagger']:
                            api_detail_template['request_params_swagger'][swagger_param_in] = {}
                        api_detail_template['request_params_swagger'][swagger_param_in][param] = swagger_param_dic

                        if swagger_param_in not in api_detail_template['request_params_ls']:
                            api_detail_template['request_params_ls'][swagger_param_in] = {}
                        api_detail_template['request_params_ls'][swagger_param_in][param] = swagger_param_dic
                        if swagger_param_in == 'formData':
                            api_detail_template['exception_flag'] = 0
                            api_detail_template['exception_log'] += '\n' + '出现formData类型字段'
                    else:

                        # 参数位置在 body中 需要取model
                        if 'items' in swagger_param_dic['schema']:
                            # 列表嵌套model
                            if '$ref' in swagger_param_dic['schema']['items']:
                                model_dic = self.get_model_dic(swagger_param_dic['schema']['items']['$ref'])
                                new_param_structure[swagger_param_dic['name']] = {
                                    'name': swagger_param_dic['name'],
                                    'description': swagger_param_dic[
                                        'description'] if 'description' in swagger_param_dic else '',
                                    'required': swagger_param_dic[
                                        'required'] if 'required' in swagger_param_dic else True,
                                    'type': 'array',
                                    'items': {},
                                    'is_ignore_key': True
                                }
                                new_param_ls[swagger_param_dic['name']] = {
                                    'name': swagger_param_dic['name'],
                                    'description': swagger_param_dic[
                                        'description'] if 'description' in swagger_param_dic else '',
                                    'required': swagger_param_dic[
                                        'required'] if 'required' in swagger_param_dic else True,
                                    'type': 'array',
                                    'is_ignore_key': True,
                                    'value': [{}],
                                }
                                # new_param_json[swagger_param_dic['name']] = [{}]
                                new_param_json = [{}]

                                self.param_dic_scann(model_dic, new_param_structure[swagger_param_dic['name']]['items'])
                                self.param_ls_scann(new_param_structure[swagger_param_dic['name']]['items'],
                                                    new_param_ls[swagger_param_dic['name']]['value'][0])
                                self.param_json_scann(model_dic, new_param_json[0])
                                if is_map_param:
                                    api_detail_template['exception_flag'] = 0
                                    api_detail_template['exception_log'] += '\n' + '接口入参 出现类型为map的参数'

                            else:
                                # 对象嵌套model 此情况body键名 不产生实际作用
                                new_param_structure[swagger_param_dic['name']] = {
                                    'name': swagger_param_dic['name'],
                                    'description': swagger_param_dic[
                                        'description'] if 'description' in swagger_param_dic else '',
                                    'required': swagger_param_dic[
                                        'required'] if 'required' in swagger_param_dic else True,
                                    'type': 'array',
                                    'items': swagger_param_dic['schema']['items'],
                                    'is_ignore_key': True,
                                }
                                new_param_ls[swagger_param_dic['name']] = {
                                    'name': swagger_param_dic['name'],
                                    'description': swagger_param_dic[
                                        'description'] if 'description' in swagger_param_dic else '',
                                    'required': swagger_param_dic[
                                        'required'] if 'required' in swagger_param_dic else True,
                                    'type': 'array',
                                    'value': [{'type': swagger_param_dic['schema']['items']['type']}],
                                    'is_ignore_key': True
                                }
                                if swagger_param_dic['schema']['type'] == 'array':
                                    swagger_param_dic['schema']['items']['format'] = swagger_param_dic['schema']['items']['format'] if 'format' in swagger_param_dic['schema']['items'] else 'None'
                                    swagger_param_dic['schema']['items']['type'] = swagger_param_dic['schema']['items']['type'] if 'type' in swagger_param_dic['schema']['items'] else 'None'
                                    swagger_param_dic['schema']['items']['description'] = swagger_param_dic['schema']['items']['description'] if 'description' in swagger_param_dic['schema']['items'] else 'None'

                                    new_param_json = ['{}-{}-{}'.format(swagger_param_dic['schema']['items']['type'], swagger_param_dic['schema']['items']['format'], swagger_param_dic['schema']['items']['description'])]
                                else:
                                    print(13)

                        else:
                            if '$ref' not in swagger_param_dic['schema']:
                                new_param_structure[swagger_param_dic['name']] = {
                                    'name': swagger_param_dic['name'],
                                    'description': swagger_param_dic[
                                        'description'] if 'description' in swagger_param_dic else '',
                                    'required': swagger_param_dic[
                                        'required'] if 'required' in swagger_param_dic else True,
                                    'type': 'array',
                                    'items': swagger_param_dic['schema'],
                                    'is_ignore_key': True,
                                }
                                new_param_ls[swagger_param_dic['name']] = {
                                    'name': swagger_param_dic['name'],
                                    'description': swagger_param_dic[
                                        'description'] if 'description' in swagger_param_dic else '',
                                    'required': swagger_param_dic[
                                        'required'] if 'required' in swagger_param_dic else True,
                                    'type': 'array',
                                    'value': {'type': swagger_param_dic['schema']['type']},
                                    'is_ignore_key': True
                                }
                                new_param_json[swagger_param_dic['name']] = '{}-{}-{}'.format(
                                    swagger_param_dic['schema']['type'],
                                    swagger_param_dic['format'] if 'format' in swagger_param_dic else None,
                                    swagger_param_dic['description'] if 'description' in swagger_param_dic else None)
                            elif swagger_param_dic['schema']['$ref'] != '#/definitions/String':
                                # 此model 为swagger未编辑情况
                                try:
                                    model_dic = deepcopy(self.get_model_dic(swagger_param_dic['schema']['$ref']))
                                except KeyError as _e:
                                    self.exception_logs.append('tag:{}, path:{} 接口入参 出现未定义model {}'.format(api_detail_template['tag'], api_url, _e.args[0]))
                                    api_detail_template['exception_flag'] = 0
                                    api_detail_template['exception_log'] += '\n' + '接口入参 出现未定义model {}'.format(_e.args[0])
                                    continue
                                if api_url == '/navQuery/pageList':
                                    print(1)
                                self.param_dic_scann(model_dic, new_param_structure)
                                if break_flag:
                                    self.param_ls_scann(new_param_structure, new_param_ls)
                                    self.param_json_scann(model_dic, new_param_json)
                                    if is_map_param:
                                        api_detail_template['exception_flag'] = 0
                                        api_detail_template['exception_log'] += '\n' + '接口入参 出现类型为map的参数'
                                else:
                                    self.exception_logs.append(
                                        'tag:{}, path:{} 接口入参 出现无限递归参数'.format(api_detail_template['tag'], api_url))
                                    api_detail_template['exception_flag'] = 0
                                    api_detail_template['exception_log'] += '\n' + '接口入参 出现无限递归参数'

                            else:
                                self.exception_logs.append('tag:{}, path:{} 未定义请求参数'.format(api_detail_template['tag'], api_url))
                                api_detail_template['exception_flag'] = 0
                                api_detail_template['exception_log'] += '\n' + '未定义body请求参数'

                        api_detail_template['request_params_swagger']['body'] = new_param_structure
                        api_detail_template['request_params_json'] = new_param_json
                        api_detail_template['request_params_ls']['body'] = new_param_ls
                for rep_status in swagger_api_dic['responses']:
                    rep_param_dic = swagger_api_dic['responses'][rep_status]
                    # if api_url == "/AccountInfo/listAccountNet/{fundAcc}":
                    #     print(1)
                    if rep_status == '200':
                        if 'schema' in rep_param_dic:
                            if "items" in rep_param_dic['schema']:
                                if "$ref" in rep_param_dic['schema']["items"]:
                                    model_dic = deepcopy(self.get_model_dic(rep_param_dic['schema']["items"]['$ref']))
                                    break_flag = True
                                    is_map_param = False
                                    # if api_url == '/AccountInfo/listFrozenAccount/{fundAcc}':
                                    #     print(1)
                                    self.param_dic_scann(model_dic, new_rep_param_structure)

                                    if break_flag:
                                        self.param_ls_scann(new_rep_param_structure, new_rep_param_ls)
                                        self.param_json_scann(model_dic, new_rep_param_json)

                                        if is_map_param:
                                            api_detail_template['exception_flag'] = 0
                                            api_detail_template['exception_log'] += '\n' + '接口出参 出现类型为map的参数'
                                    else:
                                        self.exception_logs.append(
                                            'tag:{}, path:{} 接口出参 出现无限递归参数'.format(api_detail_template['tag'], api_url))
                                        api_detail_template['exception_flag'] = 0
                                        api_detail_template['exception_log'] += '\n' + '接口出参 出现无限递归参数'
                            elif "$ref" in rep_param_dic['schema']:
                                model_dic = deepcopy(self.get_model_dic(rep_param_dic['schema']['$ref']))
                                break_flag = True
                                is_map_param = False
                                # if api_url == '/AccountInfo/listFrozenAccount/{fundAcc}':
                                #     print(1)
                                self.param_dic_scann(model_dic, new_rep_param_structure)

                                if break_flag:
                                    self.param_ls_scann(new_rep_param_structure, new_rep_param_ls)
                                    self.param_json_scann(model_dic, new_rep_param_json)

                                    if is_map_param:
                                        api_detail_template['exception_flag'] = 0
                                        api_detail_template['exception_log'] += '\n' + '接口出参 出现类型为map的参数'
                                else:
                                    self.exception_logs.append(
                                        'tag:{}, path:{} 接口出参 出现无限递归参数'.format(api_detail_template['tag'], api_url))
                                    api_detail_template['exception_flag'] = 0
                                    api_detail_template['exception_log'] += '\n' + '接口出参 出现无限递归参数'

                        api_detail_template['response_params_swagger'][rep_status] = new_rep_param_structure
                        api_detail_template['response_params_ls'] = new_rep_param_ls
                        api_detail_template['response_params_json'] = new_rep_param_json

                    else:
                        api_detail_template['response_params_swagger'][rep_status] = rep_param_dic
                for i in api_detail_template:
                    if i not in ['deprecated', 'exception_flag']:
                        api_detail_template[i] = str(api_detail_template[i])

                self.all_api_detail.append(api_detail_template)
        print(self.exception_logs)
        return self.save_api_detail()

    def save_api_detail(self):
        # old_api_manage_data = [{'path': i.path, 'request_method': i.request_method} for i in ApiManage.objects.all()]
        # 原api列表
        add_api_manage_data = []
        # 新增的api列表
        for api_detail in self.all_api_detail:
            api_manage_serializers = ApiManageSerializerAdd(data=api_detail)  # 存储
            if api_manage_serializers.is_valid():
                add_api_manage_data.append({'path': api_detail['path'], 'request_method': api_detail['request_method']})
                api_manage_serializers.save()
            else:
                # 已存在数据 修改其它字段
                api_manage_object = ApiManage.objects.get(request_method=api_detail['request_method'],
                                                          path=api_detail['path'])
                if not api_manage_object.has_manual:  # 仅修改未手动添加 / 修改的
                    for i in api_detail:
                        if i not in ['path', 'request_method', 'exception_log']:
                            if i in ['tag', 'server', 'api_desc', 'tag_english_desc']:
                                exec('api_manage_object.{} = "{}"'.format(i, api_detail[i]))

                            elif i in ['deprecated', 'exception_flag']:
                                exec('api_manage_object.{} = {}'.format(i, api_detail[i]))
                            else:
                                exec('api_manage_object.{} = str({})'.format(i, api_detail[i]))
                    api_manage_object.exception_log = api_detail['exception_log']
                    api_manage_object.save()

        # new_api_manage_data = [{'path': i['path'], 'request_method': i['request_method']} for i in self.all_api_detail]
        # delete_api_manage_data = [i for i in old_api_manage_data if i not in new_api_manage_data]
        # be_associated_api_manage_data = []
        # for i in delete_api_manage_data:
        #     api_manage_object = ApiManage.objects.get(request_method=i['request_method'], path=i['path'])
        #     try:
        #         api_manage_object.delete()
        #     except Exception as _e:
        #         be_associated_api_manage_data.append({'path': i['path'], 'request_method': i['request_method']})
        # 删除的api列表
        return add_api_manage_data






if __name__ == "__main__":
    swagger_parse = AnalysisSwaggerJson('http://192.168.0.49:10018/dfas-base-biz')
    a = swagger_parse.req_swagger()
    print(1)
    swagger_parse = AnalysisSwaggerJson('')
    swagger_parse.swagger_json_parse()
