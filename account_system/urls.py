from django.conf.urls import url

from account_system.views.CommonView import ParamDicView
from account_system.views.PermissionGroupView import PermissionGroupView, PermissionGroupResourcesView, \
    PermissionGroupDetailView
from account_system.views.PositionView import PositionView, PositionDetailView
from account_system.views.accountView import ObtainAuthToken, UserInfoView, LogoutView, UserView, UserDetailView, \
    PermissionInfoView
from account_system.views.departmentView import DepartMentViewSet, DepartMentTreeView
# from account_system.views.test import Test111

urlpatterns = [
    # 用户相关
    url(r'login', ObtainAuthToken.as_view()),
    url(r'logout', LogoutView.as_view()),
    # url(r'info', UserInfoView.as_view()),
    url(r'user/(?P<pk>[0-9]+)$', UserDetailView.as_view()),
    url(r'user', UserView.as_view()),
    # 部门相关
    url('department', DepartMentViewSet.as_view()),
    url(r'departtree', DepartMentTreeView.as_view()),
    # 职位相关
    url(r'position/(?P<pk>[0-9]+)$', PositionDetailView.as_view()),
    url(r'position', PositionView.as_view()),
    # 权限组相关
    url(r'permission_group/(?P<pk>[0-9]+)$', PermissionGroupDetailView.as_view()),
    url(r'permission_group', PermissionGroupView.as_view()),
    # 权限组 关联权限资源相关
    url(r'permission_resources/(?P<pk>[0-9]+)$', PermissionGroupResourcesView.as_view()),
    # 公共请求 表单数据字典
    url(r'paramdic', ParamDicView.as_view()),
    #户权限接口
    url(r'UserPermissionInfo', PermissionInfoView.as_view()),
    #用户信息接口
    url(r'Userinfo', UserInfoView.as_view()),
    # url(r'test', Test111.as_view()),
]
