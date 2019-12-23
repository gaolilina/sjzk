from django.conf.urls import url

from cms.views.user.im import RegisterToHuanXin, RegisterAllUserToHuanXin, UpdateAllUserPassword

urlpatterns = [
    url(r'^registertohuanxin/$', RegisterToHuanXin.as_view()),
    url(r'^registertohuanxin/all/$', RegisterAllUserToHuanXin.as_view()),
    url(r'^updatepsd/all/$', UpdateAllUserPassword.as_view()),
]
