from django.conf.urls import url

from ..views.achievement import *

urls = [
    # 点赞
    url(r'^(?P<achievement_id>[0-9]+)/likers/$', UserAchievementLikerList.as_view(),
        name='likers'),
    url(r'^(?P<achievement_id>[0-9]+)/likers/(?P<other_user_id>[0-9]+)/$',
        UserAchievementLiker.as_view(), name='liker'),
    # 发布/获取成果
    url(r'^(?P<user_id>[0-9]+)/achievements/$', AchievementList.as_view(),
        name='achievements'),
]
