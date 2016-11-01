from django.conf.urls import url

from admin.views.admin_activity import *

urls = [
    url(r'^add$', AdminActivityAdd.as_view(), name='add'),
    url(r'^view/(?P<id>\w+)$', AdminActivityView.as_view(), name='view'),
    url(r'^list$', AdminActivityList.as_view(), name='list'),
]
