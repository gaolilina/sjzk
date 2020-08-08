from django import forms
from django.http import JsonResponse
from django.views.generic import View

from main.models import User
from main.utils import abort, get_score_stage
from main.views.follow import SomethingFollower
from util.decorator.auth import app_auth
from util.decorator.param import fetch_object, validate_args


class UserFollowerList(SomethingFollower):
    @fetch_object(User.enabled, 'user')
    @app_auth
    def get(self, request, user=None):
        user = user or request.user
        return super().get(request, user)


class FollowedUserList(View):
    ORDERS = [
        'time_created', '-time_created',
        'followed__name', '-followed__name',
    ]

    @app_auth
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
        'order': forms.IntegerField(required=False, min_value=0, max_value=3),
    })
    def get(self, request, offset=0, limit=10, order=1):
        """获取用户的关注用户列表

        :param offset: 偏移量
        :param order: 排序方式
            0: 关注时间升序
            1: 关注时间降序（默认值）
            2: 昵称升序
            3: 昵称降序
        :return:
            count: 关注的用户总数
            list: 关注的用户列表
                id: 用户ID
                username: 用户名
                name: 用户昵称
                icon_url: 用户头像
                time_created: 关注时间
        """
        c = request.user.followed_users.count()
        qs = request.user.followed_users.order_by(
            self.ORDERS[order])[offset:offset + limit]
        l = [{'id': r.followed.id,
              'username': r.followed.username,
              'name': r.followed.name,
              'icon_url': r.followed.icon,
              'time_created': r.time_created} for r in qs]
        return JsonResponse({'count': c, 'list': l, 'code': 0})


class FollowedUser(View):
    @app_auth
    @fetch_object(User.enabled, 'user')
    def get(self, request, user):
        """判断当前用户是否关注了user"""

        if request.user.followed_users.filter(followed=user).exists():
            abort(200)
        abort(403, '未关注该用户')

    @app_auth
    @fetch_object(User.enabled, 'user')
    def post(self, request, user):
        """令当前用户关注user"""

        if request.user.followed_users.filter(followed=user).exists():
            abort(403, '已经关注过')
        request.user.followed_users.create(followed=user)
        # 积分
        request.user.score += get_score_stage(1)
        request.user.score_records.create(
            score=get_score_stage(1), type="活跃度", description="增加关注")
        user.score += get_score_stage(1)
        user.score_records.create(
            score=get_score_stage(1), type="受欢迎度", description="被关注")
        request.user.save()
        user.save()
        abort(200)

    @app_auth
    @fetch_object(User.enabled, 'user')
    def delete(self, request, user):
        """令当前用户取消关注user"""

        qs = request.user.followed_users.filter(followed=user)
        if qs.exists():
            # 积分
            request.user.score -= get_score_stage(1)
            request.user.score_records.create(
                score=-get_score_stage(1), type="活跃度", description="取消关注")
            user.score -= get_score_stage(1)
            user.score_records.create(
                score=-get_score_stage(1), type="受欢迎度",
                description="被关注取消")
            request.user.save()
            user.save()
            qs.delete()
            abort(200)
        abort(403, '未关注过该用户')