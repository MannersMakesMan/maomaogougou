import os
import re
from datetime import datetime

from automatic_api.runAll import AllTest
from basic_configuration.settings import local_ip, BASE_DIR


class api_scene_execution:
    def __init__(self):
        self.is_save_test_report = False
        # 是否保存测试报告
        self.default_timeout = 10
        # 默认超时时间
        self.api_script_file_name = "test_{}.py".format(str(datetime.now().strftime("%Y%m%d%H%M%S%f")))
        # 生成的 临时api文件名
        self.api_script_path = os.path.join(BASE_DIR, 'automatic_api', 'api_script_temporary', self.api_script_file_name)
        # 生成的 临时api文件注释
        self.api_script_template_path = os.path.join(BASE_DIR, 'automatic_api', 'common', 'api_script_template.txt')
        # api文件模板
        self.call_template = '        last_rep = self.{function_name}({param})'
        # 调用代码模板
        self.function_ls = []
        self.global_param_key = ''
        self.global_function = '    def {function_name}(self):\n' \
                               '        """{api_desc}"""\n' \
                               '        global go_on_flag, global_param\n' \
                               '        try:\n' \
                               '            go_on_flag = False\n' \
                               '            headers = {headers}\n' \
                               '            data = {body}\n' \
                               '            url = "{url}"\n' \
                               '            go_on_flag = True\n' \
                               '        except Exception as e:\n' \
                               '            raise SyntaxError("权限接口参数错误")\n' \
                               '        try:\n' \
                               '            go_on_flag = False\n' \
                               '            response = requests.{request_method}(url, data=json.dumps(data), headers=headers, timeout={timeout})\n' \
                               '            print("url:", url)\n' \
                               '            print("status_code:", response.status_code)\n' \
                               '            go_on_flag = True\n' \
                               '        except Exception as e:\n' \
                               '            raise SyntaxError("接口超时")\n' \
                               '        assert response.status_code == 200\n' \
                               '\n' \
                               '        rep = json.loads(response.text)\n' \
                               '        print(rep)\n' \
                               '        global_param = {global_param_value}\n' \
                               '\n' \
        # 提取全局变量的函数
        self.function_template_once = '    def {function_name}(self):\n' \
                                      '        """{api_desc}"""\n' \
                                      '        global go_on_flag, global_param, before_rep\n' \
                                      '        if not go_on_flag:\n' \
                                      '            raise SyntaxError("上方接口执行失败 停止执行")\n' \
                                      '        try:\n' \
                                      '            go_on_flag = False\n' \
                                      '            headers = {headers}\n' \
                                      '            go_on_flag = True\n' \
                                      '        except Exception as e:\n' \
                                      '            if "list index out of range" == str(e):\n' \
                                      '                raise SyntaxError("列表索引超出范围")\n' \
                                      '            raise SyntaxError("上方接口字段 " + str(e)[1: -1] + " 提取失败")\n' \
                                      '\n' \
                                      '        try:\n' \
                                      '            go_on_flag = False\n' \
                                      '            data = {body}\n' \
                                      '            url = "{url}"\n' \
                                      '{query_param}\n' \
                                      '{path_param}\n' \
                                      '            go_on_flag = True\n' \
                                      '        except Exception as e:\n' \
                                      '            if "list index out of range" == str(e):\n' \
                                      '                raise SyntaxError("列表索引超出范围")\n' \
                                      '            raise SyntaxError("上方接口字段 " + str(e)[1: -1] + " 提取失败")\n' \
                                      '\n' \
                                      '        try:\n' \
                                      '            go_on_flag = False\n' \
                                      '            response = requests.{request_method}(url, data=json.dumps(data), headers=headers, timeout={timeout})\n' \
                                      '            go_on_flag = True\n' \
                                      '        except Exception as e:\n' \
                                      '            raise SyntaxError("接口超时")' \
                                      '\n' \
                                      '        print("url:", url)\n' \
                                      '        print("status_code:", response.status_code)\n' \
                                      '        assert response.status_code == 200\n' \
                                      '        {is_pass_before_rep}\n' \
                                      '        rep = json.loads(response.text)\n' \
                                      '        print(rep)\n\n' \
                                      '        go_on_flag = False\n' \
                                      '{assert_ls}\n' \
                                      '        go_on_flag = True\n' \
                                      '\n' \

        # 函数模板 api只执行单次的情况
        self.function_template_repeat = '    def {function_name}(self):\n' \
                                 '        """{api_desc}"""\n' \
                                 '        global go_on_flag, global_param, before_rep\n' \
                                 '        if not go_on_flag:\n' \
                                 '            raise SyntaxError("上方接口执行失败 停止执行")\n' \
                                 '        try:\n' \
                                 '            headers = {headers}\n' \
                                 '        except Exception as e:\n' \
                                 '            if "list index out of range" == str(e):\n' \
                                 '                raise SyntaxError("列表索引超出范围")\n' \
                                 '            raise SyntaxError("上方接口字段 " + str(e)[1: -1] + " 提取失败")\n' \
                                 '\n' \
                                 '        try:\n' \
                                 '            data = {body}\n' \
                                 '            url = "{url}"\n' \
                                 '{query_param}\n' \
                                 '{path_param}\n' \
                                 '        except Exception as e:\n' \
                                 '            if "list index out of range" == str(e):\n' \
                                 '                raise SyntaxError("列表索引超出范围")\n' \
                                 '            raise SyntaxError("上方接口字段 " + str(e)[1: -1] + " 提取失败")\n' \
                                 '\n' \
                                 '        try:\n' \
                                 '            response = requests.{request_method}(url, data=json.dumps(data), headers=headers, timeout={timeout})\n' \
                                 '        except Exception as e:\n' \
                                 '            raise SyntaxError("接口超时")' \
                                 '\n' \
                                 '        print("url:", url)\n' \
                                 '        print("status_code:", response.status_code)\n' \
                                 '        assert response.status_code == 200\n' \
                                 '        rep = json.loads(response.text)\n' \
                                 '        print(rep)\n\n' \
                                 '        go_on_flag = False\n' \
                                 '{assert_ls}\n' \
                                 '        go_on_flag = True\n' \
                                 '\n' \

        # 函数模板 api执行多次的情况 除最后一次
        self.function_template_repeat_last = '    def {function_name}(self):\n' \
                                 '        """{api_desc}"""\n' \
                                 '        global go_on_flag, global_param, before_rep\n' \
                                 '        if not go_on_flag:\n' \
                                 '            raise SyntaxError("上方接口执行失败 停止执行")\n' \
                                 '        try:\n' \
                                 '            go_on_flag = False\n' \
                                 '            headers = {headers}\n' \
                                 '            go_on_flag = True\n' \
                                 '        except Exception as e:\n' \
                                 '            if "list index out of range" == str(e):\n' \
                                 '                raise SyntaxError("列表索引超出范围")\n' \
                                 '            raise SyntaxError("上方接口字段 " + str(e)[1: -1] + " 提取失败")\n' \
                                 '\n' \
                                 '        try:\n' \
                                 '            go_on_flag = False\n' \
                                 '            url = "{url}"\n' \
                                 '            data = {body}\n' \
                                 '{query_param}\n' \
                                 '{path_param}\n' \
                                 '            go_on_flag = True\n' \
                                 '        except Exception as e:\n' \
                                 '            if "list index out of range" == str(e):\n' \
                                 '                raise SyntaxError("列表索引超出范围")\n' \
                                 '            raise SyntaxError("上方接口字段 " + str(e)[1: -1] + " 提取失败")\n' \
                                 '\n' \
                                 '        try:\n' \
                                 '            go_on_flag = False\n' \
                                 '            response = requests.{request_method}(url, data=json.dumps(data), headers=headers, timeout={timeout})\n' \
                                 '            go_on_flag = True\n' \
                                 '\n' \
                                 '        except Exception as e:\n' \
                                 '            raise SyntaxError("接口超时")\n' \
                                 '        print("url:", url)\n' \
                                 '        print("status_code:", response.status_code)\n' \
                                 '        assert response.status_code == 200\n' \
                                 '        {is_pass_before_rep}\n' \
                                 '        rep = json.loads(response.text)\n' \
                                 '        print(rep)\n\n' \
                                 '\n' \
                                 '{assert_ls}\n' \
                                 '\n' \

        # 函数模板 api执行多次 最后一次的情况
        self.assert_template = '        assert {assert_param} {assert_type} {assert_value}'
        # 断言模板
        self.pass_before_rep = 'before_rep = json.loads(response.text)'
        # 参数传递模板
        self.query_param_template = '            {query_param} = urllib.parse.quote("{query_param_value}")\n' \
                                    '            url = url + "{query_param}=" + str({query_param}) + "&"'
        # query参数模板
        self.path_param_template = '            path_param = "{path_param_value}"\n' \
                                   '            url = url.replace("{path_param}", path_param)'
        # path参数模板
        self.function_name_ls = []
        # 函数名称 列表

    def generate_code_main(self, request_data):
        # 生成测试用例脚本
        index = 0
        for index1, api_data in enumerate(request_data):
            for index2, api_data_repeat in enumerate(api_data):
                index += 1
                function_name = "test_{}".format(index)
                self.function_name_ls.append(function_name)
                headers = {
                    "Content-Type": "application/json;charset=UTF-8"
                }
                url = api_data_repeat['path']
                # 默认请求头
                data = {}
                query_param_ls = []
                path_param_ls = []
                assert_ls = []
                for param_in in api_data_repeat['request_params']:
                    if self.global_param_key:
                        headers[self.global_param_key] = 'global_param'
                    if param_in == 'headers':
                        # 拼接headers参数
                        for key, value in api_data_repeat['request_params'][param_in].items():
                            headers[key] = value
                    elif param_in == 'query':
                        # 拼接query参数
                        for key, value in api_data_repeat['request_params'][param_in].items():
                            query_param_ls.append(self.query_param_template.format(query_param=key, query_param_value=value))

                        # url = "{}?{}".format(url, "&".join(["{}={}".format(key, value) for key, value in api_data_repeat['request_params'][param_in].items()]))
                    elif param_in == 'path':
                        # 拼接path参数
                        for key, value in api_data_repeat['request_params'][param_in].items():
                            # path_param_ls.append(self.path_param_template.replace("path_param_value", key).replace("path_param", value))
                            path_param_ls.append(self.path_param_template.format(path_param="{"+key+"}", path_param_value=value))

                        # for key, value in api_data_repeat['request_params'][param_in].items():
                        #     url = eval("url.format({}=value)".format(key))
                    elif param_in == 'body':
                        # 拼接body参数
                        data = api_data_repeat['request_params'][param_in]

                for i in api_data_repeat['assert_data']:
                    # 拼接断言代码
                    if not (i['assert_type'] and i['value'] and i['param']):
                        continue
                    if i['param'] == "response['status_code']":
                        self.assert_template = '        assert response.status_code {assert_type} {assert_value}'
                        assert_script = self.assert_template.format(assert_type=i['assert_type'], assert_value=i['value'])
                    elif i['assert_type'] == 'in':
                        if i['type'] == 'string' or i['type'] == 'integer':
                            self.assert_template = '        assert "{assert_value}" {assert_type} {assert_param}'
                        assert_script = self.assert_template.format(assert_value=i['value'], assert_type=i['assert_type'],
                                                                    assert_param=i['param'])
                    else:
                        if i['type'] == 'string':
                            self.assert_template = '        assert {assert_param} {assert_type} "{assert_value}"'
                        elif i['type'] == 'boolean':
                            i['value'] = i['value'].capitalize()
                            self.assert_template = '        assert {assert_param} {assert_type} {assert_value}'
                        elif i['type'] == 'integer':
                            self.assert_template = '        assert {assert_param} {assert_type} {assert_value}'
                        assert_script = self.assert_template.format(assert_value=i['value'], assert_type=i['assert_type'],
                                                                    assert_param=i['param'])
                    assert_ls.append(assert_script)
                self.assert_template = '        assert {assert_param} {assert_type} {assert_value}'
                if query_param_ls:
                    url = url + "?"
                if 'global_param_key' in api_data_repeat and 'global_param_value' in api_data_repeat and len(api_data) == 1:
                    self.global_param_key = api_data_repeat['global_param_key']
                    function_script = self.global_function.format(function_name=function_name,
                                                                request_method=api_data_repeat['request_method'],
                                                                url=url, body=data, headers=headers,
                                                                assert_ls="\n".join(assert_ls),
                                                                query_param="\n".join(query_param_ls),
                                                                path_param="\n".join(path_param_ls),
                                                                api_desc=api_data_repeat['api_desc'] + "-登录管理",
                                                                global_param_value=api_data_repeat['global_param_value'],
                                                                timeout=self.default_timeout)
                elif len(api_data) == 1:
                    # 单个api只执行一次
                    function_script = self.function_template_once.format(function_name=function_name,
                                                                request_method=api_data_repeat['request_method'],
                                                                url=url, body=data, headers=headers,
                                                                assert_ls="\n".join(assert_ls),
                                                                query_param="\n".join(query_param_ls),
                                                                path_param="\n".join(path_param_ls),
                                                                api_desc=api_data_repeat['api_desc'] + "-第{}次".format(index2+1),
                                                                is_pass_before_rep=self.pass_before_rep,
                                                                timeout=self.default_timeout)
                else:
                    # 单个api执行多次
                    if index2 == len(api_data)-1:
                        # 单个api执行多次 最后一次
                        function_script = self.function_template_repeat_last.format(function_name=function_name,
                                                                request_method=api_data_repeat['request_method'],
                                                                url=url, body=data, headers=headers,
                                                                assert_ls="\n".join(assert_ls),
                                                                query_param="\n".join(query_param_ls),
                                                                path_param="\n".join(path_param_ls),
                                                                api_desc=api_data_repeat['api_desc'] + "-第{}次".format(index2+1),
                                                                is_pass_before_rep=self.pass_before_rep,
                                                                timeout=self.default_timeout)
                    else:
                        # 单个api执行多次
                        function_script = self.function_template_repeat.format(function_name=function_name,
                                                                request_method=api_data_repeat['request_method'],
                                                                url=url, body=data, headers=headers,
                                                                assert_ls="\n".join(assert_ls),
                                                                query_param="\n".join(query_param_ls),
                                                                path_param="\n".join(path_param_ls),
                                                                api_desc=api_data_repeat['api_desc'] + "-第{}次".format(index2+1),
                                                                timeout=self.default_timeout)
                self.function_ls.append(function_script)

        with open(self.api_script_template_path, 'r', encoding='utf-8') as f:
            api_script = f.read()

        result = api_script.format(function_position="\n".join(self.function_ls)).replace("'global_param'", "global_param")
        for i in re.findall('"(.*?)"', result):
            if '[' in i and ']' in i:
                result = result.replace('"{}"'.format(i), '{}'.format(i))
        with open(self.api_script_path, 'w', encoding='utf-8') as f:
            f.write(result)

    def scene_execution(self, request_data):
        # api场景测试执行
        self.generate_code_main(request_data)
        # 生成测试代码
        all_test = AllTest()
        report_path = all_test.run(self.api_script_file_name, 'SceneSetting', self.function_name_ls)
        f = open(report_path, encoding='utf-8')
        file_content = f.read()
        f.close()
        os.remove(self.api_script_path)
        file_name = report_path.split('/')[-1]
        action_time = re.findall('开始时间:</strong>(.*?)</p>', file_content)
        spend_time = re.findall('运行时长:</strong>(.*?)</p>', file_content)
        test_result = re.findall('状态:</strong>(.*?)</p>', file_content)
        if not self.is_save_test_report:
            os.remove(report_path)
        return {'file_name': file_name,
                'action_time': action_time[0].strip() if action_time else None,
                'spend_time': spend_time[0].strip() if spend_time else None,
                'result': test_result[0].strip() if test_result else None,
                'text_content': file_content,
                'report_src': "{}/Operation_maintenance/test_report?test_type=api&file_name={}".format(local_ip, file_name)}

    def single_execution(self, request_data):
        # api单例测试执行
        self.generate_code_main(request_data)
        exec('from automatic_api.api_script_temporary.{} import SceneSetting'.format(self.api_script_file_name.replace('.py', '')))
        test_log = AllTest.run_test_case(eval('SceneSetting'))
        os.remove(self.api_script_path)
        return test_log



if __name__ == "__main__":
    dic_test = [
        {
            'path': 'http://192.168.0.17:8001/SystemManage/project',
            # 请求地址
            'request_method': 'post',
            # 请求方式
            'api_desc': '查询xxx',
            # 接口注释
            'request_params': {
                # 请求参数
                'headers': {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
                },  # 处于请求头的参数 若无 {}
                'query': {
                    "id": 1,
                    "test": 'test',
                },  # 处于query中的参数
                'path': {
                    "code": 30,
                    "test": "test",
                },  # 处于path中的参数 若无 {}
                'body': {
                    "dataSource": "string",
                    "ipoPurchasecode": "string",
                    "reqPageNum": 0,
                    "reqPageSize": 0,
                    "subDateEnd": "string",
                    "subDateStart": "string"
                }  # 处于body中的参数 若无 {}
            },

            'assert_data': [
                # 断言列表
                {
                    'param': "rep['id']",
                    # 参数名称 rep代表接口返回数据
                    'assert_type': '==',
                    # 断言方式 ==/!=/in
                    'value': 10,
                    # 断言判断的值
                },
                {
                    'param': "rep['data']['code']",
                    'assert_type': '!=',
                    # 断言方式 ==/!=/in
                    'value': 10,
                    # 断言判断的值
                }
            ]

        },  # 场景的第一个函数
        {
            'path': '192.168.0.49:10018/dfbp-info-manage/api/infoBank/listHeadOffice',
            # 请求地址
            'request_method': 'post',
            # 请求方式
            'api_desc': '分页查询公司管理层信息',
            'request_params': {
                # 请求参数
                'headers': {
                    "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36',
                    'test': 'test'
                },  # 处于请求头的参数 若无 {}
                'query': {
                    'id': 1,
                    'test': 'test',
                },  # 处于query中的参数
                'path': {
                    'code': 30,
                    'test': 'test',
                },  # 处于path中的参数 若无 {}
                'body': {
                    'dataSource': "before_rep['data']['code']",
                    # 接收第一个接口的传递参数 before_rep代表上一个接口的返回参数
                    'ipoPurchasecode': 'string',
                    'reqPageNum': 0,
                    'reqPageSize': 0,
                    'subDateEnd': 'string',
                    'subDateStart': 'string'
                }  # 处于body中的参数 若无 {}
            },

            'assert_data': [
                # 断言列表
                {
                    'param': "rep['id']",
                    # 参数名称 rep代表当前接口返回数据
                    'assert_type': '==',
                    # 断言方式 ==/!=/in
                    'value': 10,
                    # 断言判断的值
                },
                {
                    'param': "rep['data']['code']",
                    'assert_type': '!=',
                    # 断言方式 ==/!=/in
                    'value': 10,
                    # 断言判断的值
                }
            ]
        },  # 场景的第二个函数
    ]
    single_api_dic_test1 = [
        [
            {
                'path': 'http://192.168.0.17:8001/SystemManage/project',
                # 请求地址
                'request_method': 'post',
                # 请求方式
                'api_desc': '/SystemManage/project',
                # 接口注释
                'global_param_key': 'token',
                # 存在全局变量 作为后续请求 headers参数的键名
                'global_param_value': "rep['token']",
                # 全局变量的 作为当前接口的取值
                'request_params': {
                    # 请求参数
                    'headers': {
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
                    },  # 处于请求头的参数 若无 {}
                    'query': {},  # 处于query中的参数
                    'path': {},  # 处于path中的参数 若无 {}
                    'body': {
                        "Project_description": "API自动化测试1",
                        "Test_Leader": 1,
                        "entry_name": "自动化测试1",
                        "project_manager": 1,
                        "remark": "API自动化测试1"
                    }  # 处于body中的参数 若无 {}
                },

                'assert_data': [
                    # 断言列表
                    {
                        'param': "rep['code']",
                        # 参数名称 rep代表接口返回数据
                        'assert_type': '==',
                        # 断言方式 ==/!=/in
                        'type': 'string',
                        # 断言数据的类型 string/int/boolean
                        'value': "999999",
                        # 断言判断的值 type=boolean时候 value可以为 True/False/None
                    },
                    {
                        'param': "rep['msg']",
                        'assert_type': '==',
                        # 断言方式 ==/!=/in
                        'type': 'string',
                        # 断言数据的类型 string/int/boolean
                        'value': '成功!',
                        # 断言判断的值
                    }
                ]
            },

        ],
        # 需要登录的 登录接口信息+
        [
            {
                'path': 'http://192.168.0.17:8001/SystemManage/project',
                # 请求地址
                'request_method': 'post',
                # 请求方式
                'api_desc': '/SystemManage/project',
                # 接口注释
                'request_params': {
                    # 请求参数
                    'headers': {
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
                    },  # 处于请求头的参数 若无 {}
                    'query': {},  # 处于query中的参数
                    'path': {},  # 处于path中的参数 若无 {}
                    'body': {
                        "Project_description": "API自动化测试1",
                        "Test_Leader": 1,
                        "entry_name": "自动化测试1",
                        "project_manager": 1,
                        "remark": "API自动化测试1"
                    }  # 处于body中的参数 若无 {}
                },
                'assert_data': [
                    # 断言列表
                    {
                        'param': "rep.status_code",
                        # 参数名称 rep代表接口返回数据 状态码判断
                        'assert_type': '==',
                        # 断言方式 ==/!=/in
                        'type': 'int',
                        # 断言数据的类型 string/int/boolean
                        'value': 401,
                        # 断言判断的值 type=boolean时候 value可以为 True/False/None
                    },
                    {
                        'param': "rep['msg']",
                        'assert_type': '==',
                        # 断言方式 ==/!=/in
                        'type': 'string',
                        # 断言数据的类型 string/int/boolean
                        'value': '成功!',
                        # 断言判断的值
                    }
                ]
            },
            # 单个接口 第一次执行
            {
                'path': 'http://192.168.0.17:8001/SystemManage/project',
                # 请求地址
                'request_method': 'post',
                # 请求方式
                'api_desc': '/SystemManage/project',
                # 接口注释
                'request_params': {
                    # 请求参数
                    'headers': {
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
                    },  # 处于请求头的参数 若无 {}
                    'query': {},  # 处于query中的参数
                    'path': {},  # 处于path中的参数 若无 {}
                    'body': {
                        "Project_description": "API自动化测试1",
                        "Test_Leader": 1,
                        "entry_name": "自动化测试1",
                        "project_manager": 1,
                        "remark": "API自动化测试1"
                    }  # 处于body中的参数 若无 {}
                },
                'assert_data': [
                    # 断言列表
                    {
                        'param': "rep['code']",
                        # 参数名称 rep代表接口返回数据
                        'assert_type': '==',
                        # 断言方式 ==/!=/in
                        'type': 'string',
                        # 断言数据的类型 string/int/boolean
                        'value': "999999",
                        # 断言判断的值 type=boolean时候 value可以为 True/False/None
                    },
                    {
                        'param': "rep['msg']",
                        'assert_type': '==',
                        # 断言方式 ==/!=/in
                        'type': 'string',
                        # 断言数据的类型 string/int/boolean
                        'value': '成功!',
                        # 断言判断的值
                    }
                ]
            },
            # 单个接口 第二次执行

        ],


    ]
    dic_test2 = [[{'request_params': {'body': {'userCode': 'admin', 'password': '123456'}, 'headers': {}}, 'assert_data': [], 'global_param_key': 'Authorization', 'global_param_value': "rep['data']['jwtInfo']", 'api_desc': '登录', 'request_method': 'post', 'path': 'http://192.168.0.49:10018/dfas-auth-center/userAuth/login'}], [{'request_params': {'header': {}, 'query': {'userCode': '5001', 'test': 'test'}}, 'assert_data': [{'assert_type': '==', 'param': "rep['code']", 'type': 'string', 'description': '返回状态码(根据不同状态码处理不同业务结果)', 'id': 0, 'is_ignore_key': 0, 'is_children': 0, 'value': '200'}], 'api_desc': '用户角色列表查询(用户管理中使用)', 'request_method': 'get', 'path': 'http://192.168.0.49:10018/dfas-auth-center/userRole/listOwnerRole'}], [{'request_params': {'header': {}, 'path': {'userCode': "before_rep['data'][0]['id']", "test": "test"}}, 'assert_data': [{'assert_type': '==', 'param': "rep['code']", 'type': 'string', 'description': '返回状态码(根据不同状态码处理不同业务结果)', 'id': 0, 'is_ignore_key': 0, 'is_children': 0, 'value': '200'}], 'api_desc': '锁定用户', 'request_method': 'put', 'path': 'http://192.168.0.49:10018/dfas-auth-center/user/lock/{userCode}'}]]
    # 模拟参数
    scene_execution = api_scene_execution()
    # scene_execution.scene_execution(dic_test2)
    scene_execution.single_execution(single_api_dic_test1)
