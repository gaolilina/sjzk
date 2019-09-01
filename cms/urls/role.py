from django.conf.urls import url

from cms.views.control.role import AllRoleList, RoleDetail, RoleControlledByMe, MyRoleDetail
from cms.views.control.role_function import RoleFunction, ManageRoleFunction

urlpatterns = [
    # 所有角色列表
    url(r'^$', AllRoleList.as_view()),
    # 我的角色详情
    url(r'^my/$', MyRoleDetail.as_view()),
    # 我管理的角色列表
    url(r'^child/$', RoleControlledByMe.as_view()),
    # 角色详情
    url(r'^(?P<role_id>\d+)/$', RoleDetail.as_view()),
    # 角色拥有的功能
    url(r'^(?P<role_id>\d+)/function/$', RoleFunction.as_view()),
    # 管理角色的功能
    url(r'^(?P<role_id>\d+)/function/(?P<function_id>\w+)/$', ManageRoleFunction.as_view()),
]
