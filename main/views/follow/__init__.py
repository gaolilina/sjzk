from django import forms
from django.http import JsonResponse
from django.views.generic import View

from util.decorator.param import validate_args


class SomethingFollower(View):
    get_dict = {
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
        'order': forms.IntegerField(required=False, min_value=0, max_value=3),
    }
    ORDERS = ('time_created', '-time_created',
              'follower__name', '-follower__name')

    @validate_args(get_dict)
    def get(self, request, obj, offset=0, limit=10, order=1):
        """获取粉丝列表

        :param offset: 偏移量
        :param order: 排序方式
            0: 关注时间升序
            1: 关注时间降序（默认值）
            2: 昵称升序
            3: 昵称降序
        :return:
            count: 粉丝总数
            list: 粉丝列表
                id: 用户ID
                username: 用户名
                name: 用户昵称
                icon_url: 头像
                time_created: 关注时间
        """
        c = obj.followers.count()
        qs = obj.followers.order_by(self.ORDERS[order])[offset:offset + limit]
        l = [{'id': r.follower.id,
              'username': r.follower.username,
              'name': r.follower.name,
              'icon_url': r.follower.icon,
              'time_created': r.time_created} for r in qs]
        return JsonResponse({'count': c, 'list': l})