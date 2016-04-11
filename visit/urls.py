from django.conf.urls import url

from user.models import User
from visit import views

user_urls = [  # /user/
    url(r'^visitor/$', views.visitor, kwargs={'type': User}, name='visitor'),
    url(r'^visitor/total/$', views.visitor_total, kwargs={'type': User},
        name='visitor_total'),
    url(r'^visitor/today/$', views.visitor,
        kwargs={'type': User, 'only_today': True}, name='visitor_today'),
    url(r'^visitor/today/total/$', views.visitor_total,
        kwargs={'type': User, 'only_today': True},
        name='visitor_today_total'),
]
