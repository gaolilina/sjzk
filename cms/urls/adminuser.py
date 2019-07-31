from django.conf.urls import url

from cms.views.adminuser.list_detail import AllAdminUserList, AdminUserDetail

urlpatterns = [
    # 筛选管理端用户
    url(r'^$', AllAdminUserList.as_view()),
    # 用户详情
    url(r'^(?P<user_id>\d+)/$', AdminUserDetail.as_view()),
]
