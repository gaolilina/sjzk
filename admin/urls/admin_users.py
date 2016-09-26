from django.conf.urls import url

from admin.views.admin_user import AdminUsers

urls = [
    url(r'^$', AdminUsers.as_view(), name='info'),
]
