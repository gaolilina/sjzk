from django.conf.urls import url
from web.views.ComboBox import comboBox

urlpatterns = [
    # 查询给定key的详细信息
    url(r'^(?P<key>\S+)/$', comboBox.as_view()),
]
