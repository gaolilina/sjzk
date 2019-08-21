from django.conf.urls import url

from admin.views.admin_users import *

urls = [
    url(r'^$', AdminUsersInfo.as_view(), name='info'),
    url(r'^icon/$', AdminUsersIcon.as_view(), name='icon'),
    url(r'^identify/$', AdminUsersIndentify.as_view(), name='identify'),
]
