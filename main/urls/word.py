from django.conf.urls import url

from main.views.word.field import FieldList

urlpatterns = [
    url(r'^field/', FieldList.as_view()),
    # url(r'^skill/'),
]
