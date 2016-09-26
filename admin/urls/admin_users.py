from django.conf.urls import url

from admin.views.admin_user import AdminUsersInfo

urls = [
    url(r'^$', AdminUsersInfo.as_view(), name='info'),
]
