from django.conf.urls import url

from ..views.achievement import *

urls = [
    # 点赞
    url(r'^(?P<achievement_id>[0-9]+)/like/$', UserAchievementLikerView.as_view(), name='liker'),
    # 需求
    url(r'^(?P<achievement_id>[0-9]+)/require/$', UserAchievementRequireView.as_view(), name='require'),
    # 成果列表，发布成果
    url(r'^$', AllAchievementList.as_view(), name='all_achievements'),
    # 单挑成果
    url(r'^(?P<achievement_id>[0-9]+)/$', AllAchievement.as_view(), name='achievement'),
]
