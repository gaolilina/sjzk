from django.conf.urls import url

from user import views

urls = [  # namespace: user
    url(r'^$', views.user, name='root'),
    url(r'^total/$', views.user_total, name='total'),
    url(r'^token/$', views.user_token, name='token'),
    url(r'^username/$', views.user_username, name='username'),
    url(r'^password/$', views.user_password, name='password'),
]
