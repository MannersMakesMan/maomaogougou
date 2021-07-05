from django.conf.urls import url

from zy_api_testing.views.api_manage import ApiManageListView, ApiManageSelectData, ApiManageDeal, GetOneApiManageDetail
from zy_api_testing.views.api_params import ApiParamsAdd
from zy_api_testing.views.data_manage import DataManageDetailView, DataManageView
from zy_api_testing.views.scene import SceneDetailView, SceneView, SceneSelect
from zy_api_testing.views.scene_api_conf import ApiConfList, GetSceneApiConf
from zy_api_testing.views.single_api_test import SingleApiParam, SingleApiExecution
from zy_api_testing.views.scene_api_conf import ApiConfList, GetSceneApiConf, SceneConfExchange

urlpatterns = [
    url(r'^apiManageList$', ApiManageListView.as_view()),
    url(r'^apiMange$', ApiManageListView.as_view()),
    url(r'^apiManageSelect$', ApiManageSelectData.as_view()),
    url(r'^apiManageSelectDetail$', GetOneApiManageDetail.as_view()),
    url(r'^apiManageDeal$', ApiManageDeal.as_view()),
    url(r'^apiConfList$', ApiConfList.as_view()),
    url(r'^getsceneConf$', GetSceneApiConf.as_view()),
    url(r'^apiParamsAdd$', ApiParamsAdd.as_view()),
    # 业务场景相关
    url(r'^SceneSelect$', SceneSelect.as_view()),
    url(r'^Scene/(?P<pk>[0-9]+)$', SceneDetailView.as_view()),
    url(r'^Scene$', SceneView.as_view()),
    url(r'^SceneConfExchange$', SceneConfExchange.as_view()),
    # 测试数据管理
    url(r'data_Manage/(?P<pk>[0-9]+)$', DataManageDetailView.as_view()),
    url(r'data_Manage$', DataManageView.as_view()),
    # 单场景测试相关接口
    # url(r'SingleApiTableParam/(?P<pk>[0-9]+)$', SingleApiTableParam.as_view()),
    url(r'SingleApiParam$', SingleApiParam.as_view()),
    url(r'SingleApiExecution$', SingleApiExecution.as_view()),
]
