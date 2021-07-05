import os
import re
import shutil
import time
from datetime import datetime

from automatic_ui.common.runAll import AllTest
from automatic_ui.ui_script_generate import ui_script_generate
from basic_configuration.settings import BASE_DIR, local_ip


class ui_script_execution:
    def __init__(self):
        self.ui_script_file_name = "test_{}.py".format(str(datetime.now().strftime("%Y%m%d%H%M%S%f")))
        # 生成的 临时api文件名
        self.ui_script_path = os.path.join(BASE_DIR, 'automatic_ui', 'ui_script_temporary', self.ui_script_file_name)
        # 生成的 临时api文件路径
        self.ui_script_template_path = os.path.join(BASE_DIR, 'automatic_ui', 'common', 'ui_script_template.txt')
        # api文件模板
        with open(self.ui_script_template_path, 'r', encoding='utf-8') as f:
            self.ui_script = f.read()
        self.is_save_test_report = False

    def execution_ui_case(self, execution_data):
        # 单个测试用例执行 返回日志
        test_case = ui_script_generate.generate_single_case(execution_data['test_case_data'][0])
        result = self.ui_script.format(implicit_wait_timeout=execution_data['implicitly_wait_timeout'],
                                       explicit_wait_timeout=execution_data['explicit_wait_timeout'],
                                       explicit_wait_poll_time=execution_data['explicit_wait_poll_time'],
                                       remoteip=execution_data['remote_ip'],
                                       function_position=test_case
                                       ).replace('function_name_9527', 'test_1')
        f = open(self.ui_script_path, 'w', encoding='utf-8')
        f.write(result)
        f.close()
        exec('from automatic_ui.ui_script_temporary.{} import SceneSetting'.format(self.ui_script_file_name.replace('.py', '')))
        test_log = AllTest.run_test_case(eval('SceneSetting'))
        test_log_ls = test_log.split('\n')
        begin_index = 0
        end_index = 0
        for index, i in enumerate(test_log_ls):
            # 为测试日志添加样式 执行成功标绿 执行失败标红
            if "SyntaxError:" in i:
                end_index = index
                test_log_ls[index] = test_log_ls[index].replace("SyntaxError:", "")
                test_log_ls[index] = "<strong><font color='#FF0000'>{}</font></strong>".format(test_log_ls[index])
                test_log_ls[index+1] = "<strong><font color='#FF0000'>{}</font></strong>".format(test_log_ls[index+1])
            elif i == "E":
                begin_index = index
            elif "success" in i:
                test_log_ls[index] = "<strong><font color='green'>{}</font></strong>".format(test_log_ls[index])
        test_log_ls = test_log_ls[:begin_index] + test_log_ls[end_index:]
        # 删除测试日志中无用数据
        test_log = "\n".join(test_log_ls)

        os.remove(self.ui_script_path)
        return test_log

    # def execution_ui_scene_case(self, execution_data):
    #     # 测试场景执行
    #     test_steps = {'steps_data': []}
    #     for i in execution_data['test_case_data']:
    #         test_steps['url'] = i['url']
    #         test_steps['steps_data'] += i['steps_data']
    #     test_scene_case = ui_script_generate.generate_single_case(test_steps)
    #
    #     result = self.ui_script.format(implicit_wait_timeout=execution_data['implicitly_wait_timeout'],
    #                                    explicit_wait_timeout=execution_data['explicit_wait_timeout'],
    #                                    explicit_wait_poll_time=execution_data['explicit_wait_poll_time'],
    #                                    remoteip=execution_data['remote_ip'],
    #                                    function_position=test_scene_case
    #                                    ).replace('test_9527', 'test_1')
    #     f = open(self.ui_script_path, 'w', encoding='utf-8')
    #     f.write(result)
    #     f.close()
    #     # 生成场景代码
    #     all_test = AllTest()
    #     report_path = all_test.run(self.ui_script_file_name, 'SceneSetting', ['test_1'])
    #     # 执行测试场景 生成测试报告
    #     os.remove(self.ui_script_path)
    #     # 删除场景代码
    #     f = open(report_path, encoding='utf-8')
    #     file_content = f.read()
    #     f.close()
    #     time.sleep(0.5)
    #     file_name = os.path.basename(report_path)
    #     action_time = re.findall('开始时间:</strong>(.*?)</p>', file_content)
    #     spend_time = re.findall('运行时长:</strong>(.*?)</p>', file_content)
    #     test_result = re.findall('状态:</strong>(.*?)</p>', file_content)
    #     # 解析测试报告
    #     if not self.is_save_test_report:
    #         os.remove(report_path)
    #     # 是否删除测试报告
    #     return {'file_name': file_name,
    #             'action_time': action_time[0].strip() if action_time else None,
    #             'spend_time': spend_time[0].strip() if spend_time else None,
    #             'result': test_result[0].strip() if test_result else None,
    #             'text_content': file_content,
    #             'report_src': "{}/Operation_maintenance/test_report?test_type=ui&file_name={}".format(local_ip, file_name)}

    def execution_ui_scene_case(self, execution_data):
        screenshot_path = os.path.join(BASE_DIR, 'automatic_ui', 'ui_script_temporary', self.ui_script_file_name).replace(".py", "")
        execution_data['screenshot_path'] = screenshot_path
        # 错误截图的存储路径
        test_scene_case, function_ls = ui_script_generate.generate_scene_case(execution_data, self.ui_script)
        f = open(self.ui_script_path, 'w', encoding='utf-8')
        f.write(test_scene_case)
        f.close()
        # 生成场景代码
        all_test = AllTest()
        report_path = all_test.run(self.ui_script_file_name, 'SceneSetting', function_ls)
        # 执行测试场景 生成测试报告
        os.remove(self.ui_script_path)

        # 删除场景代码
        f = open(report_path, encoding='utf-8')
        file_content = f.read()
        f.close()
        # 删除存储异常截图文件夹
        shutil.rmtree(screenshot_path)
        time.sleep(0.5)
        file_name = os.path.basename(report_path)
        action_time = re.findall('开始时间:</strong>(.*?)</p>', file_content)
        spend_time = re.findall('运行时长:</strong>(.*?)</p>', file_content)
        test_result = re.findall('状态:</strong>(.*?)</p>', file_content)
        # 解析测试报告
        if not self.is_save_test_report:
            os.remove(report_path)
        # 是否删除测试报告
        return {'file_name': file_name,
                'action_time': action_time[0].strip() if action_time else None,
                'spend_time': spend_time[0].strip() if spend_time else None,
                'result': test_result[0].strip() if test_result else None,
                'text_content': file_content,
                'report_src': "{}/Operation_maintenance/test_report?test_type=ui&file_name={}".format(local_ip, file_name)}


if __name__ == "__main__":
    execution_test_case_data = {
        'remote_ip': '127.0.0.1',
        # 执行机ip
        'explicit_wait_timeout': '10',
        # 显式等待超时时间
        'explicit_wait_poll_time': '0.5',
        # 显式等待轮询时间
        'implicitly_wait_timeout': '10',
        # 隐式等待时间
        'test_case_data': [
            {'url': '192.168.0.49:8000/index',
             'steps_data': [
                 {
                     'function': 'execute_js_function',
                     # 操作方式
                     'function_methods': ['execute_js'],
                     # 操作步骤
                     'location': '',
                     # 定位方式
                     'location_param': '',
                     # 定位参数
                     'value': 'window.scrollTo(0,document.body.scrollHeight)',
                     # 输入参数
                 },
                 # 步骤1
                 {
                     'step_desc': '',
                     # 步骤注释
                     'function': 'click_function',
                     'function_methods': ['origin'],
                     'location': 'location_by_id',
                     'location_param': 'test_id',
                     'value': '',
                 },
                 {
                     'step_desc': '',
                     # 步骤注释
                     'function': 'click_function',
                     'function_methods': ['js_click', 'origin'],
                     'location': 'location_by_class_name',
                     'location_param': 'test_class_name',
                     'value': '',
                 },
                 {
                     'step_desc': '',
                     # 步骤注释
                     'function': 'submit_function',
                     'function_methods': ['origin'],
                     'location': 'location_by_tag_name',
                     'location_param': 'test_tag_name',
                     'value': '',
                 },
                 {
                     'step_desc': '',
                     # 步骤注释
                     'function': 'right_click_function',
                     'function_methods': ['origin'],
                     'location': 'location_by_link_text',
                     'location_param': 'test_link_text',
                     'value': '',
                 },
                 {
                     'step_desc': '',
                     # 步骤注释
                     'function': 'right_click_function',
                     'function_methods': ['origin'],
                     'location': 'location_by_xpath',
                     'location_param': './*[@id="test_id"]',
                     'value': '',
                 },
                 {
                     'step_desc': '',
                     # 步骤注释
                     'function': 'send_key_function',
                     'function_methods': ['origin'],
                     'location': 'location_by_css_selector',
                     'location_param': 'head > meta:nth-child(6)',
                     'value': 'test',
                 },
                 {
                     'step_desc': '',
                     # 步骤注释
                     'function': 'send_key_function',
                     'function_methods': ['analog_keyboard'],
                     'location': 'location_by_partial_link_text',
                     'location_param': 'test',
                     'value': 'test',
                 },
                 {
                     'step_desc': '',
                     # 步骤注释
                     'function': 'mouse_hover_function',
                     'function_methods': ['origin'],
                     'location': 'location_by_partial_link_text',
                     'location_param': 'test',
                     'value': '',
                 },
                 {
                     'step_desc': '',
                     # 步骤注释
                     'function': 'switch_iframe_function',
                     'function_methods': ['into_iframe'],
                     'location': 'location_switch_iframe_by_index',
                     'location_param': '0',
                     'value': '',
                 },
                 {
                     'step_desc': '',
                     # 步骤注释
                     'function': 'forced_wait_function',
                     'function_methods': ['origin'],
                     'location': '',
                     'location_param': '',
                     'value': '1',
                 },
                 {
                     'step_desc': '',
                     # 步骤注释
                     'function': 'alert_operate_function',
                     'function_methods': ['accept'],
                     'location': '',
                     'location_param': '',
                     'value': '',
                 },
             ]},
            {'url': '192.168.0.49:8000/index',
             'steps_data': [
                 {
                     'function': 'execute_js_function',
                     # 操作方式
                     'function_methods': ['execute_js'],
                     # 操作步骤
                     'location': '',
                     # 定位方式
                     'location_param': '',
                     # 定位参数
                     'value': 'window.scrollTo(0,document.body.scrollHeight)',
                     # 输入参数
                 },
                 # 步骤1
                 {
                     'step_desc': '',
                     # 步骤注释
                     'function': 'assert_function',
                     # 断言方法
                     'function_methods': ['equal_to'],
                     # 可选 equal_to not_equal_to contain
                     'location': 'location_by_class_name',
                     'location_param': 'test_class_name',
                     'value': '',
                     'ele_attribute': 'class',
                     # 断言元素的属性
                     'assert_value': '200'
                     # 断言元素的值
                 },
                 # 断言参数模板
                 {
                     'step_desc': '',
                     # 步骤注释
                     'function': 'click_function',
                     'function_methods': ['origin'],
                     'location': 'location_by_id',
                     'location_param': 'test_id',
                     'value': '',
                 },
                 {
                     'step_desc': '',
                     # 步骤注释
                     'function': 'click_function',
                     'function_methods': ['js_click', 'origin'],
                     'location': 'location_by_class_name',
                     'location_param': 'test_class_name',
                     'value': '',
                 },
                 {
                     'step_desc': '',
                     # 步骤注释
                     'function': 'submit_function',
                     'function_methods': ['origin'],
                     'location': 'location_by_tag_name',
                     'location_param': 'test_tag_name',
                     'value': '',
                 },
                 {
                     'step_desc': '',
                     # 步骤注释
                     'function': 'right_click_function',
                     'function_methods': ['origin'],
                     'location': 'location_by_link_text',
                     'location_param': 'test_link_text',
                     'value': '',
                 },
                 {
                     'step_desc': '',
                     # 步骤注释
                     'function': 'right_click_function',
                     'function_methods': ['origin'],
                     'location': 'location_by_xpath',
                     'location_param': './*[@id="test_id"]',
                     'value': '',
                 },
                 {
                     'step_desc': '',
                     # 步骤注释
                     'function': 'send_key_function',
                     'function_methods': ['origin'],
                     'location': 'location_by_css_selector',
                     'location_param': 'head > meta:nth-child(6)',
                     'value': 'test',
                 },
                 {
                     'step_desc': '',
                     # 步骤注释
                     'function': 'send_key_function',
                     'function_methods': ['analog_keyboard'],
                     'location': 'location_by_partial_link_text',
                     'location_param': 'test',
                     'value': 'test',
                 },
                 {
                     'step_desc': '',
                     # 步骤注释
                     'function': 'mouse_hover_function',
                     'function_methods': ['origin'],
                     'location': 'location_by_partial_link_text',
                     'location_param': 'test',
                     'value': '',
                 },
                 {
                     'step_desc': '',
                     # 步骤注释
                     'function': 'switch_iframe_function',
                     'function_methods': ['into_iframe'],
                     'location': 'location_switch_iframe_by_index',
                     'location_param': '0',
                     'value': '',
                 },
                 {
                     'step_desc': '',
                     # 步骤注释
                     'function': 'forced_wait_function',
                     'function_methods': ['origin'],
                     'location': '',
                     'location_param': '',
                     'value': '1',
                 },
                 {
                     'step_desc': '',
                     # 步骤注释
                     'function': 'alert_operate_function',
                     'function_methods': ['accept'],
                     'location': '',
                     'location_param': '',
                     'value': '',
                 },
             ]},

        ]
        # 单例步骤数据
    }
    # 测试数据
    ui_script_execution = ui_script_execution()
    ui_script_execution.execution_ui_case(execution_test_case_data)
