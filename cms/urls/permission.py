from django.conf.urls import url

from cms.views.control.user_role import ManageUserRole

urlpatterns = [
    # 为用户指派角色
    url(r'^user/(?P<user_id>\w+)/$', ManageUserRole.as_view())
]
