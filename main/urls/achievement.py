from django.conf.urls import url

from ..views.common import *

urls = [
    # 点赞
    url(r'^(?P<achievement_id>[0-9]+)/likers/$', UserAchievementLikerList.as_view(),
        name='likers'),
    url(r'^(?P<achievement_id>[0-9]+)/likers/(?P<other_user_id>[0-9]+)/$',
        UserAchievementLiker.as_view(), name='liker')
]
