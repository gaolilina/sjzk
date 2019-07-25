from django.conf.urls import url

from cms.views.control.role import RoleList, RoleDetail
from cms.views.control.role_function import RoleFunction, ManageRoleFunction

urlpatterns = [
    url(r'^$', RoleList.as_view()),
    url(r'^(?P<role_id>\d+)/$', RoleDetail.as_view()),
    url(r'^(?P<role_id>\d+)/function/$', RoleFunction.as_view()),
    url(r'^(?P<role_id>\d+)/function/(?P<function_id>\w+)/$', ManageRoleFunction.as_view()),
]
