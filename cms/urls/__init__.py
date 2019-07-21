from django.conf.urls import url, include

from cms.urls import role, function

urlpatterns = [
    url(r'^role/', include(role)),
    url(r'^function/', include(function)),
]
