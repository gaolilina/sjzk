from django.conf.urls import url

from main.views.report import Report

urlpatterns = [
    # 举报
    url(r'^report/$', Report.as_view()),
]
