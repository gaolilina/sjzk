from django.conf.urls import url

from ..views.vote import *


urls = [
    url(r'^user/(?P<user_id>[0-9]+)/$', UserList.as_view(), name='user_list'),
    url(r'^user/(?P<vote_id>[0-9]+)/$', UserDetail.as_view(), name='user_detail'),
    url(r'^user/(?P<option_id>[0-9]+)/$', UserOption.as_view(), name='user_option'),
    url(r'^lab/(?P<lab_id>[0-9]+)/$', LabList.as_view(), name='lab_list'),
    url(r'^lab/(?P<vote_id>[0-9]+)/$', LabDetail.as_view(), name='lab_detail'),
    url(r'^lab/(?P<option_id>[0-9]+)/$', LabOption.as_view(), name='lab_option'),
]
