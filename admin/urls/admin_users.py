from django.conf.urls import url

from admin.views.admin_user import *

urls = [
    url(r'^$', AdminUsersInfo.as_view(), name='info'),
    url(r'^identify$', AdminUsersIndentify.as_view(), name='identify'),
]