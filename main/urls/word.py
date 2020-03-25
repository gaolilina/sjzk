from django.conf.urls import url

from main.views.word.field import FieldList
from main.views.word.skill import SkillList
from main.views.ComboBox import comboBox

urlpatterns = [
    url(r'^field/$', FieldList.as_view()),
    url(r'^skill/$', SkillList.as_view()),
    url(r'^(?P<key>\S+)/$', comboBox.as_view()),
]
