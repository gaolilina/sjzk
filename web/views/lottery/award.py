from django import forms

from modellib.models import LotteryParticipant, Lottery
from util.base.view import BaseView
from util.decorator.auth import client_auth
from util.decorator.param import validate_args, fetch_object


class ReceiveAward(BaseView):

    @client_auth
    @validate_args({
        'award_id': forms.IntegerField(),
    })
    @fetch_object(LotteryParticipant.objects, 'award')
    def post(self, request, award, **kwargs):
        if award.lottery.user != request.user:
            return self.fail(1, '无权操作')
        LotteryParticipant.objects.filter(id=award.id).update(is_handled=True)
        if not LotteryParticipant.objects.filter(lottery=award.lottery, is_handled=False).exists():
            return self.fail(10, "奖品全部领取完成")
        return self.success()


class UserReceiveAward(BaseView):

    @client_auth
    @validate_args({
        'lottery_id': forms.IntegerField(),
    })
    @fetch_object(Lottery.objects, 'lottery')
    def post(self, request, lottery, **kwargs):
        qs = LotteryParticipant.objects.filter(lottery=lottery, user=request.user)
        if not qs.exists():
            return self.fail(1, '无中奖信息')
        LotteryParticipant.objects.filter(id=qs.first().id).update(is_handled=True)
        if not LotteryParticipant.objects.filter(lottery=lottery, is_handled=False).exists():
            return self.fail(10, "奖品全部领取完成")
        return self.success()
