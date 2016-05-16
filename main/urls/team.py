from django.conf.urls import url

from main.views.team import Teams
urls = [
    url(r'^$', Teams.as_view(), name='root'),
]