#! /usr/bin/env python3
# -*- coding: utf-8 -*-

from django.conf.urls import url

from admin.views.analysis import PaperAnalysis
from admin.views.paper import PaperList, PaperDetail, PaperSwitch, PaperAdd

urls = [
    url(r'^$', PaperList.as_view(), name='list'), # 调查问卷列表
    url(r'^add/$', PaperAdd.as_view(), name='add'), # 创建调查问卷
    url(r'^(?P<paper_id>\d+)/$', PaperDetail.as_view(), name='detail'), # 调查问卷详情
    url(r'^(?P<paper_id>\d+)/switch/$', PaperSwitch.as_view(), name='switch'), # 开启/关闭调查问卷
    url(r'^(?P<paper_id>\d+)/analysis/$', PaperAnalysis.as_view(), name='analysis'), # 分析调查问卷
]
