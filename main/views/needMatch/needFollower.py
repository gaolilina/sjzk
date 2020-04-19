from django import forms
from django.http import JsonResponse
from django.views.generic import View

from main.models.user import User
from main.models import Activity
from main.models import Competition
from main.utils import abort
from util.decorator.auth import app_auth
from util.decorator.param import fetch_object, validate_args

from modellib.models.need import UserNeed


class FollowedNeed(View):
    @fetch_object(UserNeed.objects, 'need')
    @app_auth
    def get(self, request, need):
        """判断当前用户是否关注了该需求"""

        if request.user.followed_need.filter(
                followed=need).exists():
            abort(200)
        abort(404, '未关注该活动')

    @fetch_object(UserNeed.objects, 'need')
    @app_auth
    def post(self, request, need):
        """令当前用户关注需求"""

        if request.user.followed_need.filter(
                followed=need).exists():
            abort(403, '已经关注过该需求')

        request.user.followed_need.create(followed=need)
        request.user.save()
        abort(200)

    @fetch_object(UserNeed.objects, 'need')
    @app_auth
    def delete(self, request, need):
        """令当前用户取消关注需求"""

        qs = request.user.followed_need.filter(followed=need)
        if qs.exists():
            qs.delete()
            abort(200)
        abort(403, '未关注过该需求')



class FollowedNeedList(View):
    ORDERS = ['time_created', '-time_created']

    @app_auth
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
        'activity_id': forms.IntegerField(required=False),
        'competition_id': forms.IntegerField(required=False),
    })
    @fetch_object(Activity.objects, 'activity', force=False)
    @fetch_object(Competition.objects, 'competition', force=False)
    def get(self, request, offset=0, limit=10, competition=None, activity=None):
        """获取用户的关注收藏列表

        :param offset: 偏移量
        :param limit: 数量上限
        :param activity_id: 活动id
        :param competition_id: 竞赛id

        :return:
            count: 收藏总数
            list: 需求列表
                id: 需求ID
                field: 需求标签
                desc: 需求描述
                like: 需求点赞

        """

        qs = request.user.followed_need.all()
        list = []
        c = 0
        for follow in qs:
            if follow.followed.competition == competition and follow.followed.activity==activity:
                list.append(follow.followed)
                c += 1
        qs = list[offset:offset + limit]
        l = [{'id': a.id,
              'user_id': a.user_id,
              'desc': a.desc,
              'liker_count': a.user.likers.count(),
              'field': a.field,

            } for a in qs]
        return JsonResponse({'count': c, 'list': l})