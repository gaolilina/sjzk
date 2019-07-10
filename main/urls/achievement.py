from django.conf.urls import url

from ..views.achievement import *
from ..views.achievement_team import *

urls = [
    # 点赞
    url(r'^(?P<achievement_id>[0-9]+)/like/$', AchievementDoWhoView.as_view(), name='liker', kwargs={'who': 'likers'}),
    # 需求
    url(r'^(?P<achievement_id>[0-9]+)/require/$', AchievementDoWhoView.as_view(), name='require', kwargs={'who': 'requirers'}),
    # 成果列表，发布成果
    url(r'^$', AllUserAchievementListView.as_view(), name='all_achievements'),
    # 单挑成果
    url(r'^(?P<achievement_id>[0-9]+)/$', AllUserAchievementView.as_view(), name='achievement'),

    ### 团队
    # 所有团队成果
    url(r'^team/$', AllTeamAchievementListView.as_view(), name='all_achievements'),
    # 某团队成果/发布成果
    url(r'^team/(?P<team_id>[0-9]+)/$', TeamAchievementList.as_view(), name='achievements'),
    url(r'^(?P<achievement_id>[0-9]+)/team/$', AllTeamAchievementView.as_view(), name='achievement'),
]
