import json
from copy import deepcopy

import requests

from zy_api_testing.models import ApiManage
from zy_api_testing.serializers import ApiManageSerializerAdd


class AnalysisSwaggerJson:
    def __init__(self, swagger_url):
        self.swagger_url = swagger_url

        self.swagger_dic = json.loads(open('test_data/zhongyin_swagger.json', encoding='gbk').read())
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
                self.swagger_dic = rep.json()
                self.swagger_json_parse()
                return {'swagger_json': self.swagger_dic, 'exception_log': '\n'.join(self.exception_logs)}
        except Exception as e:
            return {'exception_log': '请求swagger地址错误. url: {},  异常如下: {}'.format(self.swagger_url, e)}


    def param_dic_scann(self, model_dic, new_param_structure, last_model_name=''):
        # 递归提取model 拼接为swagger原生结构
        global break_flag
        if not break_flag:
            return 'maximum recursion'

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
                    self.param_dic_scann(param_dic['items'], new_param_structure[param]['items'], model_name)
                else:
                    new_param_structure[param] = {"type": param_dic['type'], 'items': param_dic['items']}

            else:
                new_param_structure[param] = param_dic

    # def param_ls_scann(self, model_dic, new_param_ls, ahead_param=''):
    #     # 递归将swagger接口信息原生格式 转换为 同层级接口参数字典
    #     params_dic = model_dic['properties']
    #     for param in params_dic:
    #         param_dic = params_dic[param]
    #
    #         level_param = "{}.{}".format(ahead_param, param) if ahead_param else param
    #         level_param_dict = {
    #             "value": None,
    #             'type': param_dic['type'] if 'type' in param_dic else 'object',
    #             'description': param_dic['description'] if 'description' in param_dic else ''
    #         }
    #
    #         if level_param_dict['type'] == 'array':
    #             if 'properties' in param_dic['items']:
    #                 level_param_dict["value"] = [param_dic['items']['properties']]
    #             else:
    #                 level_param_dict["value"] = [param_dic['items']]
    #
    #         elif level_param_dict['type'] == 'object':
    #             if 'properties' in param_dic['items']:
    #                 level_param_dict["value"] = param_dic['items']['properties']
    #             else:
    #                 level_param_dict["value"] = param_dic['items']
    #
    #
    #         elif 'properties' in param_dic:
    #             self.param_ls_scann(param_dic, new_param_ls, ahead_param=level_param)
    #
    #         new_param_ls[level_param] = level_param_dict

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
                    level_param_dict["value"] = [param_dic['items']]
                    new_param_ls[level_param] = level_param_dict

            elif param_dic['type'] == 'object':
                if 'items' in param_dic:
                    level_param_dict["value"] = param_dic['items']
                    self.param_ls_scann(param_dic['items'], new_param_ls, ahead_param=level_param)

            # elif 'properties' in param_dic:
            #     self.param_ls_scann(param_dic, new_param_ls, ahead_param=level_param)
            else:
                new_param_ls[level_param] = level_param_dict


    def param_json_scann(self, model_dic, new_param_json):
        # 递归将swagger原生接口信息 转换为直接可以请求的json

        params_dic = model_dic['properties']
        for param in params_dic:
            param_dic = params_dic[param]
            param_dic['type'] = param_dic['type'] if 'type' in param_dic else 'object'
            if param_dic['type'] == 'array':
                if 'properties' in param_dic['items']:
                    new_param_json[param] = [{}]
                    self.param_json_scann(param_dic['items'], new_param_json[param][0])
                else:
                    new_param_json[param] = ['{}'.format(param_dic['items']['type'])]

            elif param_dic['type'] == 'object':
                if 'properties' in param_dic['items']:
                    new_param_json[param] = {}
                    self.param_json_scann(param_dic['items'], new_param_json[param])
                else:
                    print(12)

            elif 'properties' in param_dic:
                new_param_json[param] = {}
                self.param_json_scann(param_dic['items'], new_param_json[param])

            else:
                new_param_json[param] = '{}'.format(param_dic['type'])



    def get_model_dic(self, model_name):
        # 提取参数model
        if '#/definitions/' in model_name:
            model_name = model_name.replace('#/definitions/', '')
        return self.api_param_models[model_name]

    def swagger_json_parse(self):
        server_name = 'default'if self.swagger_dic['data']['basePath'] == '/' else self.swagger_dic['data']['basePath'].replace('/', '')
        # 服务名
        self.host_url = self.swagger_dic['data']['host'] if server_name == 'default' else self.swagger_dic['data']['host'] + '/' + server_name
        # 路由地址

        api_details = self.swagger_dic['data']['paths']
        # 原生swagger 每个api的详情数据
        self.api_param_models = self.swagger_dic['data']['definitions']
        # 原生swagger api参数model数据
        for api_url in api_details:
            for request_method in api_details[api_url]:
                api_detail_template = {
                    "path": '',
                    # 路由地址
                    "tag": '',
                    # 所属tag
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
                }
                # 解析后的api详情模板 初始化
                swagger_api_dic = api_details[api_url][request_method]
                # 请求方式
                api_detail_template['request_method'] = request_method
                api_detail_template['server'] = server_name
                api_detail_template['tag'] = swagger_api_dic['tags'][0]
                api_detail_template['api_desc'] = swagger_api_dic['summary']
                api_detail_template['path'] = self.host_url + api_url
                api_detail_template['deprecated'] = swagger_api_dic['deprecated']

                new_param_ls = {}
                new_param_structure = {}
                new_param_json = {}
                new_rep_param_ls = {}
                new_rep_param_structure = {}
                global break_flag
                break_flag = True
                # 接口是否执行递归扫描的标志

                if 'parameters' not in swagger_api_dic:
                    self.exception_logs.append('tag:{}, path:{} 缺失请求参数字段 parameters'.format(api_detail_template['tag'], api_url))
                    continue
                for swagger_param_dic in swagger_api_dic['parameters']:
                    swagger_param_in = swagger_param_dic['in']
                    # 参数所在位置 body/query/header/path
                    if swagger_param_in not in api_detail_template['param_in']:
                        api_detail_template['param_in'].append(swagger_param_in)

                    if swagger_param_in in ['query', 'path', 'header', 'formData']:
                        # 参数位置在 query path header formData 中 保留全部参数
                        api_detail_template['request_params_swagger'][swagger_param_in] = swagger_param_dic
                    else:
                        # 参数位置在 body中 需要取model
                        if 'items' in swagger_param_dic['schema']:
                            model_dic = self.get_model_dic(swagger_param_dic['schema']['items']['$ref'])
                            new_param_structure[swagger_param_dic['name']] = {
                                'name': swagger_param_dic['name'],
                                'description': swagger_param_dic['description'] if 'description' in swagger_param_dic else '',
                                'required': swagger_param_dic['required'] if 'required' in swagger_param_dic else True,
                                'type': 'array',
                                'items': {},
                            }
                            new_param_ls[swagger_param_dic['name']] = {
                                'name': swagger_param_dic['name'],
                                'description': swagger_param_dic['description'] if 'description' in swagger_param_dic else '',
                                'required': swagger_param_dic['required'] if 'required' in swagger_param_dic else True,
                                'type': 'array',
                                'value': {},
                            }
                            new_param_json[swagger_param_dic['name']] = [{}]



                            self.param_dic_scann(model_dic, new_param_structure[swagger_param_dic['name']]['items'])
                            self.param_ls_scann(new_param_structure[swagger_param_dic['name']]['items'], new_param_ls[swagger_param_dic['name']]['value'])
                            self.param_json_scann(model_dic, new_param_json[swagger_param_dic['name']][0])

                        else:
                            model_dic = deepcopy(self.get_model_dic(swagger_param_dic['schema']['$ref']))
                            self.param_dic_scann(model_dic, new_param_structure)

                            if break_flag:
                                self.param_ls_scann(new_param_structure, new_param_ls)
                                self.param_json_scann(model_dic, new_param_json)
                            else:
                                self.exception_logs.append('tag:{}, path:{} 出现无限递归参数'.format(api_detail_template['tag'], api_url))

                        api_detail_template['request_params_swagger']['body'] = new_param_structure
                        api_detail_template['request_params_json'] = new_param_json
                        api_detail_template['request_params_ls'] = new_param_ls
                for rep_status in swagger_api_dic['responses']:
                    rep_param_dic = swagger_api_dic['responses'][rep_status]
                    if rep_status == '200':
                        if "$ref" in rep_param_dic['schema']:
                            model_dic = self.get_model_dic(rep_param_dic['schema']['$ref'])
                            # if model_dic['title'] == 'AjaxResult?PageInfoDto?NegativeNewsResponse??':
                            #     print(1)
                            break_flag = True
                            self.param_dic_scann(model_dic, new_rep_param_structure)
                            self.param_ls_scann(new_rep_param_structure, new_rep_param_ls)

                            api_detail_template['response_params_swagger'][rep_status] = new_rep_param_structure
                            api_detail_template['response_params_ls'] = new_rep_param_ls
                    else:
                        api_detail_template['response_params_swagger'][rep_status] = rep_param_dic

                for i in api_detail_template:
                    if i != 'deprecated':
                        api_detail_template[i] = str(api_detail_template[i])
                self.all_api_detail.append(api_detail_template)

        print(self.exception_logs)
        return self.save_api_detail()

    def save_api_detail(self):
        for api_detail in self.all_api_detail:
            api_manage_serializers = ApiManageSerializerAdd(data=api_detail)  # 存储
            if api_manage_serializers.is_valid():
                api_manage_serializers.save()
            else:
                api_manage_object = ApiManage.objects.get(request_method=api_detail['request_method'],
                                                          path=api_detail['path'])
                for i in api_detail:
                    if i != 'path' and i != 'request_method':
                        exec('api_manage_object.{} = "{}"'.format(i, api_detail[i]))
                api_manage_object.save()


if __name__ == "__main__":
    swagger_parse = AnalysisSwaggerJson('', '')
    swagger_parse.swagger_json_parse()
    print(2)
