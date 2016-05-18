from django.conf.urls import url

from main.views.team import Teams, Profile, Icon
urls = [
    # 获取所有团队列表(get)或者创建团队(post)
    url(r'^$', Teams.as_view(), name='root'),
    # 获取团队的基本信息(get)或者修改团队的基本信息(post)
    url(r'^(?P<team_id>[0-9]+)/profile/$',
        Profile.as_view(), name='profile'),
    # 获取(get)或者设置团队头像(post)
    url(r'^(?P<team_id>[0-9]+)/icon/$',Icon.as_view(), name='icon'),
]