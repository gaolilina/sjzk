from django.conf.urls import url, include

from main.urls import search, paper
from . import user, current_user, team, forum, activity, competition, system, lab, topic, vote, achievement, auth, \
    friend, need, task, like_old, like, follow, favor, action, feedback, report, experience, word, comment

urlpatterns = [
    url(r'^users/', include(user.urls, namespace='user')),
    url(r'^achievement/', include(achievement.urls, namespace='achievement')),
    url(r'^me/', include(current_user.urls)),
    # 点赞
    url(r'^like/', include(like)),
    # 收藏
    url(r'^favor/', include(favor)),
    # 关注
    url(r'^follow/', include(follow)),
    # 经历
    url(r'^experience/', include(experience)),
    # 团队
    url(r'^teams/', include(team.urls)),
    url(r'^teams/', include(need.urls)),
    url(r'^teams/', include(task.urls)),
    url(r'^activity/', include(activity)),
    url(r'^competition/', include(competition.urls, namespace='competition')),
    url(r'^system/', include(system.urls, namespace='system')),

    url(r'^auth/', include(auth.urls, namespace='auth')),
    url(r'^friend/', include(friend.urls, namespace='friend')),
    url(r'^search/', include(search.urlpatterns, namespace='search')),
    url(r'^paper/', include(paper.urls, namespace='paper')),
    url(r'^word/', include(word)),

    ###############################弃用
    url(r'^users/current/', include(current_user.urls, namespace='current_user')),
    # 点赞
    url(r'^users/current/', include(like_old.urls)),
    # 粉丝
    url(r'^users/current/followed/', include(follow)),
    # 收藏
    url(r'^users/current/favored/', include(favor)),
    # 动态
    url(r'^users/current/', include(action)),
    # 反馈
    url(r'^users/current/', include(feedback)),
    # 举报
    url(r'^users/current/', include(report)),
    # 评论
    url(r'^users/current/', include(comment)),
    url(r'^labs/', include(lab.urls, namespace='lab')),
    url(r'^topic/', include(topic.urls, namespace='topic')),
    url(r'^vote/', include(vote.urls, namespace='vote')),
    url(r'^forum/', include(forum.urls, namespace='forum')),
]
