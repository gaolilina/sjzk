from django import forms

from modellib.models import LotteryParticipant
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
        return self.success()
