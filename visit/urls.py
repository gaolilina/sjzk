from django.conf.urls import url, include

from user.models import User
from visit import views

user_urlpatterns = [  # namespace: user:visitor
    url(r'^$', views.visitor, kwargs={'obj_type': User}, name='root'),
    url(r'^total/$', views.visitor_total, kwargs={'obj_type': User},
        name='total'),
    url(r'^today/$', views.visitor,
        kwargs={'obj_type': User, 'only_today': True}, name='today'),
    url(r'^today/total/$', views.visitor_total,
        kwargs={'obj_type': User, 'only_today': True}, name='today_total'),
]

user_urls = [url(r'^visitor/', include(user_urlpatterns, namespace='visitor'))]
