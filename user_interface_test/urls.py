from django.conf.urls import url

from user_interface_test.views.common_params import CommonParamQueryView, CommonParamsAdd, CommonParamDropDownBox
from user_interface_test.views.test_case import TestCaseTreeQueryView, TestCaseAdd, ExecuteCase, CommonCaseLs, \
    TestCaseQueryView
from user_interface_test.views.test_case_data import TestCaseDataQueryView, TestCaseStepDetail, \
    TestCaseStep
from user_interface_test.views.test_model import TestModelQueryView, TestModelAdd
from user_interface_test.views.ui_scene import TestSceneAdd, TestSceneQueryView, ExecuteScene, TestSceneData

urlpatterns = [
    # 公共参数
    url(r'^uiCommonList$', CommonParamQueryView.as_view()),
    url(r'^uiCommonOperate$', CommonParamsAdd.as_view()),
    url(r'uiCommonParamDropDownBox', CommonParamDropDownBox.as_view()),

    # 测试模块/界面
    url(r'^testModelList$', TestModelQueryView.as_view()),
    url(r'^testModelOperate$', TestModelAdd.as_view()),

    # 测试用例
    url(r'^testCaselList$', TestCaseQueryView.as_view()),
    url(r'^testCaseTree$', TestCaseTreeQueryView.as_view()),
    url(r'^testCaseOperate$', TestCaseAdd.as_view()),
    url(r'^executeCase$', ExecuteCase.as_view()),

    url(r'^testCaseDatalList$', TestCaseDataQueryView.as_view()),
    # url(r'^testCaseDataOperate$', TestCaseDataAdd.as_view()),

    # 测试场景数据
    url(r'^testScenelList$', TestSceneQueryView.as_view()),
    url(r'^testSceneOperate$', TestSceneAdd.as_view()),
    url(r'^executeScene$', ExecuteScene.as_view()),
    url(r'^testSceneDataOperate$', TestSceneData.as_view()),

    # 测试用例数据
    url(r'^testStepData/(?P<pk>[0-9]+)$', TestCaseStepDetail.as_view()),
    url(r'^testStepData', TestCaseStep.as_view()),

    # 公共方法
    url(r'^commonCaseList$', CommonCaseLs.as_view()),
]
