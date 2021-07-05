from django.conf.urls import url
from asset_information.views.Server import ServerView, ServerDetailView
from asset_information.views.VirtualMachine import VirtualMachineView, VirtualMachineDetailView
from asset_information.views.CommonView import ParamDicView
from asset_information.views.VmTestWorker import VmTestWorkerTreeView, VmTestWorker

urlpatterns = [
    # 服务器相关
    url(r'server/(?P<pk>[0-9]+)$', ServerDetailView.as_view()),
    url(r'server', ServerView.as_view()),
    # 虚拟机相关
    url(r'virtual_machine/(?P<pk>[0-9]+)$', VirtualMachineDetailView.as_view()),
    url(r'virtual_machine', VirtualMachineView.as_view()),
    # 执行机相关 已迁移至系统配置管理模块
    # url(r'vm_test_worker_tree', VmTestWorkerTreeView.as_view()),
    # url(r'vm_test_worker', VmTestWorker.as_view()),
    # 公共
    url(r'paramdic', ParamDicView.as_view()),
]

