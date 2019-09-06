from django.conf.urls import url

from main.views.word.field import FieldList
from main.views.word.skill import SkillList

urlpatterns = [
    url(r'^field/$', FieldList.as_view()),
    url(r'^skill/$', SkillList.as_view()),
]
