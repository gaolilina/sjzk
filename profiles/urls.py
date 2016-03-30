from django.conf.urls import url, include

from profiles import views

user_urlpatterns = [  # namespace: user:profile
    url(r'^$', views.user_profile, name='root'),
    url(r'^(?P<user_id>[0-9]+)/$', views.user_profile, name='id'),
]

user_urls = [url(r'^profile/', include(user_urlpatterns, namespace='profile'))]
