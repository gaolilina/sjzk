from django.conf.urls import url

from admin.views.activity.check import ActivityCheck
from admin.views.activity.list_detail import ActivityView, ActivityList
from admin.views.admin_activity import *

urls = [
    url(r'^(?P<activity_id>\d+)?/check/$', ActivityCheck.as_view(), name='activity_check'),

    # 老接口
    url(r'^activity/list/(?P<id>\w+)?$', ActivityList.as_view(), name='activity_list'),
    url(r'^activity/(?P<id>\w+)$', ActivityView.as_view(), name='activity'),
    url(r'^add$', AdminActivityAdd.as_view(), name='add'),
    url(r'^view/(?P<id>\w+)$', AdminActivityView.as_view(), name='view'),
    url(r'^edit/(?P<id>\w+)$', AdminActivityEdit.as_view(), name='edit'),
    url(r'^list$', AdminActivityList.as_view(), name='list'),
    url(r'^view/(?P<id>\w+)/excel.csv$', AdminActivityExcelView.as_view(), name='excel'),
]
