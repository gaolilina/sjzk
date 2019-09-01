from django.conf.urls import url

from cms.views.adminuser.control import ResetPassword, EnableControl
from cms.views.adminuser.list_detail import AllAdminUserList, AdminUserDetail, ManagerControlledByMe

urlpatterns = [
    # 筛选管理端用户
    url(r'^$', AllAdminUserList.as_view()),
    url(r'^my/$', ManagerControlledByMe.as_view()),
    # 用户详情
    url(r'^(?P<user_id>\d+)/$', AdminUserDetail.as_view()),
    url(r'^(?P<user_id>\d+)/resetpsd/$', ResetPassword.as_view()),
    url(r'^(?P<user_id>\d+)/enable/$', EnableControl.as_view()),
]
