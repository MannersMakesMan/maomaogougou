from django.conf.urls import url

from system_settings.views.MysqlConfView import MysqlInfoView, MysqlInfoViewDetail, MysqlTableDropDownBox
from system_settings.views.environment import EnvironmentAddView, EnvironmentView, EnvironmentListView
from system_settings.views.perform import PerformMachineView, PerformMachineAddView, PerformMachineListView, \
    PerformMachineAllListView
from system_settings.views.project import ProjectAddView, ProjectView, ProjectListView
from system_settings.views.time_task import TaskView, ControlTask
from system_settings.views.DataDict import DataDictList, SonDataDict

urlpatterns = [
    # mysql配置相关
    url(r'^Mysqlinfo/(?P<pk>[0-9]+)$', MysqlInfoViewDetail.as_view()),
    url(r'^MysqlinfoDropDownBox', MysqlTableDropDownBox.as_view()),
    url(r'^Mysqlinfo', MysqlInfoView.as_view()),

    # 项目相关
    url(r'^project/(?P<pk>[0-9]+)$', ProjectView.as_view()),
    url(r'^project$', ProjectAddView.as_view()),
    url(r'^projectList$', ProjectListView.as_view()),
    # 环境相关
    url(r'^environment/(?P<pk>[0-9]+)$', EnvironmentView.as_view()),
    url(r'^environment$', EnvironmentAddView.as_view()),
    url(r'^environmentList$', EnvironmentListView.as_view()),
    # 执行机相关
    url(r'^Perform/(?P<pk>[0-9]+)$', PerformMachineView.as_view()),
    url(r'^Perform$', PerformMachineAddView.as_view()),
    url(r'^PerformList$', PerformMachineListView.as_view()),
    url(r'^PerformIpList$', PerformMachineAllListView.as_view()),

    url(r'^task$',TaskView.as_view()),
    url(r'^controltask$',ControlTask.as_view()),
    url(r'^DataDict$',DataDictList.as_view()),
    url(r'^SonDataDict$',SonDataDict.as_view())
]
