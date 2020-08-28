from django.conf.urls import url

from main.views.chatIM.chat_group import *

urlpatterns = [
    #
    url(r'^(?P<team_id>[0-9]+)/create/$', GroupManagement.as_view()),
    url(r'^(?P<team_id>[0-9]+)/delete/$', GroupManagement.as_view()),
    url(r'^(?P<team_id>[0-9]+)/get/member/$', MemberManagement.as_view()),
    url(r'^(?P<team_id>[0-9]+)/add/member/(?P<user_id>[0-9]+)/$', MemberManagement.as_view()),
    url(r'^(?P<team_id>[0-9]+)/delete/member/(?P<user_id>[0-9]+)/$', MemberManagement.as_view()),
]
