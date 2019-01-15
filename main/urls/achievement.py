from django.conf.urls import url

from ..views.achievement import *

urls = [
    # 点赞
    url(r'^(?P<achievement_id>[0-9]+)/likers/$', UserAchievementLikerList.as_view(),
        name='likers'),
    # 点赞
    url(r'^(?P<achievement_id>[0-9]+)/likers/(?P<other_user_id>[0-9]+)/$',
        UserAchievementLiker.as_view(), name='liker'),
    # 需求
    url(r'^(?P<achievement_id>[0-9]+)/require/(?P<other_user_id>[0-9]+)/$',
        UserAchievementRequire.as_view(), name='require'),
    # 发布/获取成果
    url(r'^(?P<user_id>[0-9]+)/achievements/$', AchievementList.as_view(),
        name='achievements'),
    # 成果列表
    url(r'^$', AllAchievementList.as_view(),
        name='all_achievements'),
    # 单挑成果
    url(r'^(?P<achievement_id>[0-9]+)/$',
        AllAchievement.as_view(), name='achievement'),
]
