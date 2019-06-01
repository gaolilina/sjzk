from django.conf.urls import url

from main.views.paper import PaperList

urls = [
    # 调查问卷列表
    url(r'^$', PaperList.as_view(), name='list'),
]
