from automatic_ui.common import selenium_functions, selenium_locations, assert_functions
from automatic_ui.common.tools import get_model_classes, get_class_functions


def get_functions():
    function_ls = get_model_classes(selenium_functions)
    location_ls = get_model_classes(selenium_locations)
    iframe_location_ls = [i for i in location_ls if i['function'] != 'location_switch_iframe_by_index']
    assert_function_ls = get_model_classes(assert_functions)
    function_data = {"functions": [], "assert_functions": []}
    for function_dic in function_ls:
        exec("from automatic_ui.common.selenium_functions import *")
        function = function_dic['function']
        function_methods = get_class_functions(eval(function))
        for function_method in function_methods:
            if function_method['is_need_button']:
                if function != 'switch_iframe_functions':
                    function_method['locations'] = iframe_location_ls
                else:
                    function_method['locations'] = location_ls
            else:
                function_method['locations'] = []
        function_dic['methods'] = function_methods
        function_data['functions'].append(function_dic)
    for assert_function_dic in assert_function_ls:
        exec("from automatic_ui.common.assert_functions import *")
        assert_function = assert_function_dic['function']
        assert_function_methods = get_class_functions(eval(assert_function))
        for assert_function_method in assert_function_methods:
            if assert_function_method['is_need_button']:
                assert_function_method['locations'] = iframe_location_ls
            else:
                assert_function_method['locations'] = []
        assert_function_dic['methods'] = assert_function_methods
        function_data['assert_functions'].append(assert_function_dic)
    return function_data


if __name__ == "__main__":
    get_functions()
