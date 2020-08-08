from django import forms
from django.http import JsonResponse
from django.views.generic import View

from util.decorator.auth import app_auth
from util.decorator.param import validate_args


class UserScoreRecord(View):
    ORDERS = ('time_created', '-time_created')

    @app_auth
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
        'order': forms.IntegerField(required=False, min_value=0, max_value=1),
    })
    def get(self, request, offset=0, limit=10, order=1):
        """获取用户的积分明细

        :param offset: 拉取的起始
        :param limit: 拉取的数量上限
        :return:
            count: 明细的总条数
            list:
                score: 积分
                type: 积分类别
                description: 描述
                time_created: 时间

        """
        k = self.ORDERS[order]
        r = request.user.score_records.all()
        c = r.count()
        qs = r.order_by(k)[offset: offset + limit]
        l = [{'description': s.description,
              'score': s.score,
              'type': s.type,
              'time_created': s.time_created} for s in qs]
        return JsonResponse({'count': c, 'list': l, 'code': 0})