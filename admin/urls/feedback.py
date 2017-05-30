from django.conf.urls import url

from admin.views.feedback import *

urls = [
    url(r'^$', Feedback.as_view(), name='feedback'),
    url(r'^report$', Report.as_view(), name='report'),
    url(r'^report/(?P<id>\w+)$', ReportDeal.as_view(), name='report'),
]
