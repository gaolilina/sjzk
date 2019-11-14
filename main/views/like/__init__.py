from django import forms
from django.http import JsonResponse
from django.views.generic import View

from main.models import User, UserAction, Team, TeamAction
from main.utils import abort, get_score_stage
from main.utils.recommender import record_like_user, record_like_team
from util.decorator.auth import app_auth
from util.decorator.param import validate_args


class ILikeSomethingSimple(View):
    """与当前用户点赞行为相关的View"""

    @app_auth
    def post(self, request, entity):
        """对某个对象点赞"""
        entity.likers.add(request.user)
        abort(200)

    @app_auth
    def delete(self, request, entity):
        """对某个对象取消点赞"""
        entity.likers.remove(request.user)
        abort(200)


class ILikeSomething(View):
    """与当前用户点赞行为相关的View，后面逐渐使用上面那个"""

    @app_auth
    def get(self, request, entity):
        """判断当前用户是否对某个对象点过赞"""

        if entity.likers.filter(liker=request.user).exists():
            abort(200)
        abort(404, '未点过赞')

    @app_auth
    def post(self, request, entity):
        """对某个对象点赞"""

        if not entity.likers.filter(liker=request.user).exists():
            entity.likers.create(liker=request.user)
            # 积分
            request.user.score += get_score_stage(1)
            request.user.score_records.create(
                score=get_score_stage(1), type="活跃度", description="给他人点赞")
            # 特征模型
            if isinstance(entity, User):
                record_like_user(request.user, entity)
            elif isinstance(entity, UserAction):
                record_like_user(request.user, entity.entity)
            elif isinstance(entity, Team):
                record_like_team(request.user, entity)
            elif isinstance(entity, TeamAction):
                record_like_user(request.user, entity.entity)
            else:
                pass

            request.user.save()
        abort(200)

    @app_auth
    def delete(self, request, entity):
        """对某个对象取消点赞"""

        # 积分
        request.user.score -= get_score_stage(1)
        request.user.score_records.create(
            score=-get_score_stage(1), type="活跃度", description="取消给他人点赞")
        request.user.save()
        entity.likers.filter(liker=request.user).delete()
        abort(200)


class SomethingLikers(View):
    ORDERS = (
        'time_created', '-time_created',
        'follower__name', '-follower__name',
    )

    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
        'order': forms.IntegerField(required=False, min_value=0, max_value=3),
    })
    def get(self, request, obj, offset=0, limit=10, order=1):
        """获取对象的点赞者列表

        :param offset: 偏移量
        :param order: 排序方式
            0: 点赞时间升序
            1: 点赞时间降序（默认值）
            2: 昵称升序
            3: 昵称降序
        :return:
            count: 总点赞量
            list: 点赞者列表
                id: 用户ID
                username: 用户名
                name: 用户昵称
                icon_url: 用户头像URL
                time_created: 点赞时间
        """
        i, j, k = offset, offset + limit, self.ORDERS[order]
        c = obj.likers.count()
        qs = obj.likers.order_by(k)[i:j]
        l = [{'id': r.liker.id,
              'username': r.liker.username,
              'name': r.liker.name,
              'icon_url': r.liker.icon,
              'time_created': r.time_created} for r in qs]
        return JsonResponse({'count': c, 'list': l})


class Liker(View):
    def get(self, request, entity, other_user):
        """判断other_user是否对某个实体点过赞"""

        if entity.likers.filter(liker=other_user).exists():
            abort(200)
        abort(404, '未点赞')
