from django.conf.urls import url
from cms.views.comboBox.mamageWord import mamageComboBox, getComboBox

urlpatterns = [
    url(r'^(?P<word_id>\d+)/$', mamageComboBox.as_view()),
    url(r'^$', getComboBox.as_view()),
]