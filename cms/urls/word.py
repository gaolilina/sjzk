from django.conf.urls import url

from cms.views.word.field import FieldList, FieldEnable
from cms.views.word.skill import SkillList, SkillEnable

urlpatterns = [
    url(r'^field/$', FieldList.as_view()),
    url(r'^field/(?P<field_id>\d+)/enable/$', FieldEnable.as_view()),
    url(r'^skill/$', SkillList.as_view()),
    url(r'^skill/(?P<skill_id>\d+)/enable/$', SkillEnable.as_view()),
]
