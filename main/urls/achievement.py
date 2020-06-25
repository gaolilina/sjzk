from django.conf.urls import url

from main.views.achievement.action import AchievementDoWhoView, AchievementDetail
from main.views.achievement.publish import PublishTeamAchievement, PublishUserAchievement
from main.views.search.achievement import SearchTeamAchievement
from ..views.achievement import *

urls = [
    # 点赞
    url(r'^(?P<achievement_id>[0-9]+)/like/$', AchievementDoWhoView.as_view(), name='liker', kwargs={'who': 'likers'}),
    # 需求
    url(r'^(?P<achievement_id>[0-9]+)/require/$', AchievementDoWhoView.as_view(), name='require', kwargs={'who': 'requirers'}),
    # 单挑成果
    url(r'^(?P<achievement_id>[0-9]+)/$', AchievementDetail.as_view(), name='achievement'),
    # 发布个人成果
    url(r'^$', PublishUserAchievement.as_view(), name='all_achievements'),
    # 发布成团队果
    url(r'^team/(?P<team_id>[0-9]+)/$', PublishTeamAchievement.as_view(), name='achievements'),




    #============================================ 弃用
    # 所有团队成果
    url(r'^team/$', SearchTeamAchievement.as_view(), name='all_achievements'),
    url(r'^(?P<achievement_id>[0-9]+)/team/$', AchievementDetail.as_view(), name='achievement'),

]
