from django.conf.urls import url

from cms.views.word.field import FieldList, FieldEnable

urlpatterns = [
    url(r'^field/$', FieldList.as_view()),
    url(r'^field/(?P<field_id>\d+)/enable/$', FieldEnable.as_view()),
]
