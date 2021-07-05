from automatic_ui.common.selenium_functions import *
from automatic_ui.common.selenium_locations import *


class ui_script_generate:
    @classmethod
    def generate_single_case(cls, generate_data, test_case_index, test_scene_desc='default'):
        # 生成单一测试用例代码 每次单例执行/场景执行前
        driver_get_template = 'self.driver.get("{url}")\n'
        # 打开网址模板
        indent_template = '            '
        # 缩进模板
        step_template = '        try:\n' \
                        '{step_code}\n' \
                        '        except Exception as e:\n' \
                        '            self.driver.save_screenshot(os.path.join(screenshot_path, str("{test_case_index}") + ".png"))\n' \
                        '            exception_detail = traceback.format_exc()\n' \
                        '            exception_handle(exception_detail, "{step_desc}")\n\n'
        # 步骤异常捕获模板
        test_function_template = '    def {function_name}(self):\n' \
                                 '        """{test_scene_desc}"""\n' \
                                 '{driver_get}' \
                                 '{step}'
        # 单例函数模板
        single_test_function_name = 'test_9527'
        # 单例函数函数名 拼接场景时候用于替换函数名

        driver_get_case = '        ' + driver_get_template.format(url=generate_data['url'])
        step_case_ls = []
        for step_data in generate_data['steps_data']:
            step_code = ''
            value = step_data['value'].replace("'", '"')
            function = step_data['function']
            if function == 'switch_case':
                # 用例切换时 在报告中打印用例名称
                step_code += "        print('==============================================用例:{}==============================================')\n".format(value)
                step_case_ls.append(step_code)
                continue

            step_desc = step_data.get("step_desc", '')
            function_methods = eval(step_data['function_method'])
            location = step_data['location']
            location_param = step_data['location_param'].replace("'", '"')
            mysql_info = str(step_data['mysql_info']).replace("'", '"')

            if function == 'assert_function':
                # 是否是断言方法
                ele_attribute = step_data['ele_attribute']
                assert_value = step_data['assert_value']
                function_code, is_need_value, is_need_button = eval('{}.{}(ele_attribute, assert_value)'.format(function, function_methods[0]))
                step_code += indent_template + function_code
            elif function == 'mysql_function':
                # 是否是mysql操作方法
                value = step_data['value'].replace('"', "'")
                function_code, is_need_value, is_need_button = eval('{}.{}({}, value)'.format(function, function_methods[0], mysql_info))
                step_code += indent_template + function_code
            else:
                if value:
                    for function_method in function_methods:
                        function_code, is_need_value, is_need_button = eval('{}.{}(value)'.format(function, function_method))
                        step_code += indent_template + function_code
                else:
                    for function_method in function_methods:
                        function_code, is_need_value, is_need_button = eval('{}.{}()'.format(function, function_method))
                        step_code += indent_template + function_code

            if is_need_button:
                if function == 'drop_down_box_function':
                    location_code = eval('{}(location_param)[1]'.format(location))
                else:
                    location_code = eval('{}(location_param)[0]'.format(location))
                step_code = indent_template + "time.sleep(0.5)\n" + indent_template + location_code + step_code
            step_code += indent_template + "print('{}-success')".format(step_desc)
            step_code = step_template.format(step_code=step_code, step_desc=step_desc, test_case_index=test_case_index+1)
            step_case_ls.append(step_code)
        test_function_code = test_function_template.format(test_scene_desc=test_scene_desc, step=''.join(step_case_ls),
                                                                function_name=single_test_function_name,
                                                                driver_get=driver_get_case)
        return test_function_code

    @classmethod
    def generate_scene_case(cls, generate_scene_data, template_case):
        # 生成测试场景代码
        test_case_ls = []
        function_name_ls = []
        single_test_function_name = 'test_9527'
        for index, test_case in enumerate(generate_scene_data['test_case_data']):
            test_case = ui_script_generate.generate_single_case(test_case, index, generate_scene_data['test_scene_desc'])
            function_name = 'test_{}'.format(index+1)
            test_case = test_case.replace(single_test_function_name, function_name) + "\n"
            test_case_ls.append(test_case)
            function_name_ls.append(function_name)
        scene_code = template_case.format(implicit_wait_timeout=generate_scene_data['implicitly_wait_timeout'],
                                          explicit_wait_timeout=generate_scene_data['explicit_wait_timeout'],
                                          explicit_wait_poll_time=generate_scene_data['explicit_wait_poll_time'],
                                          remoteip=generate_scene_data['remote_ip'],
                                          function_position="".join(test_case_ls),
                                          screenshot_path=generate_scene_data['screenshot_path'])
        return scene_code, function_name_ls


if __name__ == '__main__':
    pass
