# coding=utf-8
import sys
import os
import unittest
from datetime import datetime
from io import StringIO

from automatic_api.common.HTMLTestRunner import HTMLTestRunner
from automatic_api.common.paramunittest import ParamUnittestSuite
from basic_configuration.settings import BASE_DIR


class AllTest:
    def set_case_suite(self, file_name, class_name, function_ls):
        """
        添加测试函数
        """
        exec('from automatic_api.api_script_temporary.{} import *'.format(file_name.replace('.py', '')))
        suite = unittest.TestSuite()
        p = ParamUnittestSuite(suite)
        for i in function_ls:
            exec("p.addTest(eval(class_name), '{}', '')".format(i))
        return p

    def run(self, file_name, class_name, function_ls):
        """
        执行测试
        """
        resultPath = os.path.join(BASE_DIR, 'automatic_api', 'result', str(datetime.now().strftime("%Y%m%d%H%M%S%f")+'_report.html'))
        fp = open(resultPath, 'wb')
        suit = self.set_case_suite(file_name, class_name, function_ls)
        if suit is not None:
            print('********TEST START********')
            runner = HTMLTestRunner(verbosity=2, stream=fp, title='赢.投资交易系统自动化测试报告', description='Test Description')
            runner.run(suit)
            print('********TEST END********')
            return resultPath
        else:
            fp.close()
        return resultPath

    @classmethod
    def run_test_case(cls, test_class_obj):
        # 单个用例执行 返回测试日志
        suite = unittest.TestSuite()
        suite = ParamUnittestSuite(suite)
        suite.addTest(test_class_obj, 'test_9527', '')
        stream = StringIO()
        runner = unittest.TextTestRunner(stream=stream)
        runner.run(suite)
        stream.seek(0)
        # 提取执行日志
        return stream.read()


if __name__ == '__main__':
    obj = AllTest()
    obj.run('test_20210129104145768169.py', 'SceneSetting', ['test_1', 'test_2', 'test_3', 'test_4', 'test_5'])
