#! /usr/bin/env python3
# -*- coding: utf-8 -*-
from django.conf.urls import url

from web.views.lottery.action import JoinLottery, LotteryAction
from web.views.lottery.award import ReceiveAward, UserReceiveAward
from web.views.lottery.list_detail import LotteryListAndCreate, LotteryInfo
from web.views.lottery.user import LotteryJoinedUserList, MyVictoryList

urlpatterns = [
    # 抽奖列表和创建抽奖
    url(r'^$', LotteryListAndCreate.as_view()),
    # 抽奖信息
    url(r'^(?P<lottery_id>\d+)/$', LotteryInfo.as_view()),
    # 签到
    url(r'^(?P<lottery_id>\d+)/join/$', JoinLottery.as_view()),
    # 抽奖和获取获奖名单
    url(r'^(?P<lottery_id>\d+)/victory/$', LotteryAction.as_view()),
    # 抽奖池中的用户
    url(r'^(?P<lottery_id>\d+)/users/$', LotteryJoinedUserList.as_view()),
    # 领取奖品，用户主动领取奖品
    url(r'^(?P<lottery_id>\d+)/receive/$', UserReceiveAward.as_view()),
    # 领取奖品，抽奖方标识奖品被领走
    url(r'award/(?P<award_id>\d+)/receive/$', ReceiveAward.as_view()),
    # 我的中奖信息
    url(r'^my/victory/$', MyVictoryList.as_view()),
]
