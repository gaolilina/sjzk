from django.conf.urls import url

from web.views.need import IDoSomethingOnUserNeed, UserNeedList, MyUserNeedList, DeleteMyUserNeed

urlpatterns = [
    url(r'^$', UserNeedList.as_view()),
    url(r'^me/$', MyUserNeedList.as_view()),
    url(r'^(?P<need_id>\d+)/$', DeleteMyUserNeed.as_view()),
    url(r'^(?P<need_id>\d+)/like/$', IDoSomethingOnUserNeed.as_view(), kwargs={'field': 'likers'}),
]
