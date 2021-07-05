
from automatic_ui.common import selenium_functions, selenium_locations
from automatic_ui.common.tools import get_model_classes, get_class_functions
from common.tools import serializers_save
from system_settings.models import Dataexplain, DataDictionary
from user_interface_test.models import UiFunctions, CommonParams
from user_interface_test.serializers import UiFunctionsSerializerAdd


# def get_functions():
#     function_ls = get_model_classes(selenium_functions)
#     location_ls = get_model_classes(selenium_locations)
#     iframe_location_ls = [i for i in location_ls if i['function'] != 'location_switch_iframe_by_index']
#     assert_function_ls = get_model_classes(assert_functions)
#     function_data = {"functions": [], "assert_functions": []}
#     for function_dic in function_ls:
#         exec("from automatic_ui.common.selenium_functions import *")
#         function = function_dic['function']
#         function_methods = get_class_functions(eval(function))
#         for function_method in function_methods:
#             if function_method['is_need_button']:
#                 if function != 'switch_iframe_functions':
#                     function_method['locations'] = iframe_location_ls
#                 else:
#                     function_method['locations'] = location_ls
#             else:
#                 function_method['locations'] = []
#         function_dic['methods'] = function_methods
#         function_data['functions'].append(function_dic)
#     for assert_function_dic in assert_function_ls:
#         exec("from automatic_ui.common.assert_functions import *")
#         assert_function = assert_function_dic['function']
#         assert_function_methods = get_class_functions(eval(assert_function))
#         for assert_function_method in assert_function_methods:
#             if assert_function_method['is_need_button']:
#                 assert_function_method['locations'] = iframe_location_ls
#             else:
#                 assert_function_method['locations'] = []
#         assert_function_dic['methods'] = assert_function_methods
#         function_data['assert_functions'].append(assert_function_dic)
#     return function_data


def save_functions():
    try:
        # 存储ui执行函数
        UiFunctions.objects.all().delete()
        function_ls = get_model_classes(selenium_functions)
        iframe_location_ls = get_model_classes(selenium_locations)
        location_ls = [i for i in iframe_location_ls if i['function'] != 'location_switch_iframe_by_index']
        # assert_function_ls = get_model_classes(assert_functions)
        # 断言数据 是否和功能选择同存一个下拉框
        for function_dic in function_ls:
            function_dic['function_level'] = 0
            function_dic['super_function'] = ''
            # if function_dic['description'] == "输入值":
            #     print(11)
            serializers_save(UiFunctionsSerializerAdd, function_dic)
            exec("from automatic_ui.common.selenium_functions import *")
            function = function_dic['function']
            function_methods = get_class_functions(eval(function))
            for function_method in function_methods:
                function_method['super_function'] = function
                function_method['function_level'] = 1
                serializers_save(UiFunctionsSerializerAdd, function_method)
                if function_method['is_need_button']:
                    if function != 'switch_iframe_functions':
                        for iframe_location in location_ls:
                            iframe_location['super_function'] = function_method['function']
                            iframe_location['function_level'] = 2
                            serializers_save(UiFunctionsSerializerAdd, iframe_location)
                    else:
                        for location in iframe_location_ls:
                            location['super_function_name'] = function_method['function']
                            location['function_level'] = 2
                            serializers_save(UiFunctionsSerializerAdd, location)

    except Exception as e:
        pass


def save_params():
    # 存储默认参数
    default_params = [{
            "id": 1,
            "param_desc": "显式等待超时时间",
            "param_value": "10",
        },
        {
            "id": 2,
            "param_desc": "显式等待轮询时间",
            "param_value": "0.5",
        },
        {
            "id": 3,
            "param_desc": "隐式等待超时时间",
            "param_value": "10",
        }]
    default_date_explains = [{
        "dictionary_code": "A0000001",
        "dictionary_explain": "API接口测试登录验证",
        "default_data_dics": [{
            "DictionarySubitem_code": "a0000001",
            "dictionary_item1": "/userAuth/login",
            "dictionary_item2": "",
            "DictionarySubitem_explain": "登录接口路径",
            "item_desc": "登录接口路径",
            "Dataexplain_id": 1,

        },
        {
            "DictionarySubitem_code": "a0000002",
            "dictionary_item1": "Authorization",
            "dictionary_item2": "",
            "DictionarySubitem_explain": "发送请求时token所在的位置",
            "item_desc": "发送请求时token所在的位置",
            "Dataexplain_id": 1,
        },
        {
            "DictionarySubitem_code": "a0000003",
            "dictionary_item1": "rep['data']['jwtInfo']",
            "dictionary_item2": "",
            "DictionarySubitem_explain": "从登录响应中获取token的位置",
            "item_desc": "登录接口路径",
            "Dataexplain_id": 1,
        },
        {
            "DictionarySubitem_code": "a0000004",
            "dictionary_item1": "userCode",
            "dictionary_item2": "admin",
            "DictionarySubitem_explain": "用户名配置",
            "item_desc": "用户名配置",
            "Dataexplain_id": 1,
        },
        {
            "DictionarySubitem_code": "a0000005",
            "dictionary_item1": "password",
            "dictionary_item2": "123456",
            "DictionarySubitem_explain": "密码配置",
            "item_desc": "密码配置",
            "Dataexplain_id": 1,
        }, ]
        },
        {
            "dictionary_code": "A0000002",
            "dictionary_explain": "UI用例类型选项",
            "default_data_dics": [{
                "DictionarySubitem_code": "a0000001",
                "dictionary_item1": "web ui",
                "dictionary_item2": "",
                "DictionarySubitem_explain": "类型1",
                "item_desc": "类型1",
        }, ],
        },
        ]

    try:
        for param in default_params:
            if not CommonParams.objects.filter(param_desc=param["param_desc"]):
                CommonParams.objects.create(param_desc=param['param_desc'], param_value=param['param_value'])

        for default_date_explain in default_date_explains:
            if not Dataexplain.objects.filter(dictionary_code=default_date_explain['dictionary_code']):
                date_explain_obj = Dataexplain.objects.create(dictionary_code=default_date_explain['dictionary_code'], dictionary_explain=default_date_explain['dictionary_explain'])
                for default_data_dic in default_date_explain['default_data_dics']:
                    if not DataDictionary.objects.filter(DictionarySubitem_code=default_data_dic['DictionarySubitem_code']):
                        DataDictionary.objects.create(
                            DictionarySubitem_code=default_data_dic['DictionarySubitem_code'],
                            dictionary_item1=default_data_dic['dictionary_item1'],
                            dictionary_item2=default_data_dic['dictionary_item2'],
                            DictionarySubitem_explain=default_data_dic['DictionarySubitem_explain'],
                            Dataexplain_id=date_explain_obj
                        )
    except Exception as e:
        pass


if __name__ == "__main__":
    save_functions()
