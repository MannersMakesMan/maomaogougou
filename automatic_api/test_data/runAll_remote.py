# coding=utf-8
import sys
import os
import unittest
from datetime import datetime

curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)

from automatic_api.test_data.test import SalesOutlets
from automatic_api.common.HTMLTestRunner import HTMLTestRunner
from automatic_api.common.paramunittest import ParamUnittestSuite




class AllTest:

    def set_case_suite(self, class_name, method_name):
        """
        set case suite
        :return:
        """
        suite = unittest.TestSuite()
        p = ParamUnittestSuite(suite)
        p.addTest(SalesOutlets, "test_netCode_add", '')

        print('report_path: =={}=='.format(self.resultPath))

        return p

    def run(self):
        """
        run test
        :return:
        """
        LocalPath = os.path.join(rootPath, 'result', str(datetime.now().strftime("%Y%m%d%H%M%S%f")))
        if not os.path.exists(LocalPath):
            os.mkdir(LocalPath)
        resultPath = os.path.join(LocalPath, 'report.html')
        fp = open(resultPath, 'wb')
        suit = self.set_case_suite()

        if suit is not None:
            print('********TEST START********')
            runner = HTMLTestRunner(verbosity=2, stream=fp, title='赢.投资交易系统自动化测试报告', description='Test Description')
            runner.run(suit)
            print('********TEST END********')
        else:
            fp.close()

if __name__ == '__main__':
    obj = AllTest()
    obj.run()
