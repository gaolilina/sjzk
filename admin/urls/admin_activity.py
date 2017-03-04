from django.conf.urls import url

from admin.views.admin_activity import *

urls = [
    url(r'^add$', AdminActivityAdd.as_view(), name='add'),
    url(r'^view/(?P<id>\w+)$', AdminActivityView.as_view(), name='view'),
    url(r'^edit/(?P<id>\w+)$', AdminActivityEdit.as_view(), name='edit'),
    url(r'^list$', AdminActivityList.as_view(), name='list'),
    url(r'^view/(?P<id>\w+)/excel.csv$', AdminActivityExcelView.as_view(), name='excel'),
]
