from django.conf.urls import url

from web.views.me import Profile

urlpatterns = [
    url(r'^info/$', Profile.as_view()),
]
