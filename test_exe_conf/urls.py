from django.conf.urls import url

from test_exe_conf.views.ExeTestConf import TestCaseExecute, uiCaseExecutorView
from test_exe_conf.views.test import TestCaseExecute as TEST_EXECONF_TEST
from test_exe_conf.views.TestConf import TestTask, MethodsLs, TestTaskLs

urlpatterns = [
    url(r'TestTask', TestTask.as_view()),
    url(r'ExecuteTask', TestCaseExecute.as_view()),
    url(r'MethodsLs', MethodsLs.as_view()),
    url(r'TestSceneTaskLs', TestTaskLs.as_view()),
    url(r'TEST_EXECONF_TEST', TEST_EXECONF_TEST.as_view()),
    url(r'uiCaseExecutorAlone', uiCaseExecutorView.as_view()),
]
