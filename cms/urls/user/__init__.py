from django.conf.urls import url

from cms.views.user.im import RegisterToHuanXin

urlpatterns = [
    url(r'^registertohuanxin/$', RegisterToHuanXin.as_view()),
]
