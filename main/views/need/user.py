from django import forms
from django.db import transaction
from django.http import JsonResponse
from django.views.generic import View

from main.models import User
from main.models.need import TeamNeed
from main.utils import abort, action, get_score_stage
from main.utils.decorators import require_verification_token
from util.decorator.auth import app_auth
from util.decorator.param import fetch_object, validate_args


class MemberNeedRequestList(View):
    @fetch_object(TeamNeed.objects, 'need')
    @app_auth
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
    })
    def get(self, request, need, offset=0, limit=10):
        """获取人员需求的加入申请列表

        :param offset: 偏移量
        :return: request.user 不为团队创始人时，404
        :return: request.user 为团队创始人时
            count: 申请总数
            list: 申请列表
                id: 申请者ID
                username: 申请者用户名
                name: 申请者昵称
                icon_url: 申请者头像
                description: 备注
                time_created: 申请时间
        """
        if request.user == need.team.owner:
            # 拉取人员需求下团队的加入申请信息
            c = need.member_requests.count()
            qs = need.member_requests.all()[offset:offset + limit]

            l = [{'id': r.sender.id,
                  'username': r.sender.username,
                  'name': r.sender.name,
                  'icon_url': r.sender.icon,
                  'description': r.description,
                  'time_created': r.time_created} for r in qs]
            return JsonResponse({'count': c, 'list': l})
        abort(404, '只有队长可以操作')

    @fetch_object(TeamNeed.objects, 'need')
    @require_verification_token
    @validate_args({
        'description': forms.CharField(required=False, max_length=100),
    })
    def post(self, request, need, description=''):
        """向人员需求发出加入申请

        :param description: 附带消息
        """
        if request.user == need.team.owner:
            abort(403, '队长不能操作')

        if need.team.members.filter(user=request.user).exists():
            abort(403, '已经是对方团队成员')

        if need.team.member_requests.filter(user=request.user).exists():
            abort(200)

        if need.team.invitations.filter(user=request.user).exists():
            abort(403, '对方团队已经发送邀请')

        need.member_requests.create(sender=request.user,
                                    description=description)
        abort(200)


class MemberNeedRequest(View):
    @fetch_object(TeamNeed.objects, 'need')
    @fetch_object(User.enabled, 'user')
    @require_verification_token
    def post(self, request, need, user):
        """将目标用户添加为自己的团队成员（对方需发送过人员需求下的加入团队申请）"""

        if request.user != need.team.owner:
            abort(403, '只有队长可以操作')

        if not need.member_requests.filter(sender=user):
            abort(403, '对方未发送申请')

        # 若对方已是团队成员则不做处理
        if need.team.members.filter(user=user).exists():
            abort(200)

        # 在事务中建立关系，并删除对应的加团队申请
        with transaction.atomic():
            need.member_requests.filter(sender=user).delete()
            # 保存需求的加入成员Id
            if len(need.members) > 0:
                need.members = need.members + "|" + str(user.id)
            else:
                need.members = str(user.id)
            need.save()
            need.team.members.create(user=user)
            action.join_team(user, need.team)
            # 积分
            request.user.score += get_score_stage(1)
            request.user.score_records.create(
                score=get_score_stage(1), type="能力", description="加入团队成功")
            need.team.score += get_score_stage(1)
            need.team.score_records.create(
                score=get_score_stage(1), type="能力",
                description="成功招募一个成员")
            request.user.save()
            need.team.save()
        abort(200)

    @fetch_object(TeamNeed.objects, 'need')
    @fetch_object(User.enabled, 'user')
    @require_verification_token
    def delete(self, request, need, user):
        """忽略某用户人员需求下的加团队请求"""

        if request.user != need.team.owner:
            abort(403, '只有队长可以操作')

        qs = need.member_requests.filter(sender=user)
        if not qs.exists():
            abort(404, '申请不存在')
        qs.delete()
        abort(200)


class NeedUserList(View):
    ORDERS = (
        'time_created',
        '-time_created',
        'name',
        '-name',
    )

    @fetch_object(TeamNeed.objects, 'need')
    @app_auth
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
        'order': forms.IntegerField(required=False, min_value=0, max_value=3),
    })
    def get(self, request, need, offset=0, limit=10, order=1):
        """获取需求的成员列表

        :param offset: 偏移量
        :param order: 排序方式
            0: 成为成员时间升序
            1: 成为成员时间降序（默认值）
            2: 昵称升序
            3: 昵称降序
        :return:
            count: 成员总数
            list: 成员列表
                id: 用户ID
                username:用户名
                name: 用户昵称
                icon_url: 用户头像
                tags: 标签
                gender: 性别
                liker_count: 点赞数
                follower_count: 粉丝数
                visitor_count: 访问数
                time_created: 注册时间
        """
        i, j, k = offset, offset + limit, self.ORDERS[order]
        uids = []
        if need.members:
            ids = need.members.split("|")
            for uid in ids:
                uids.append(int(uid))
            members = User.enabled.filter(id__in=uids)
            c = members.count()
            rs = members.order_by(k)[i:j]
            l = [{'id': r.id,
                  'username': r.username,
                  'name': r.name,
                  'icon_url': r.icon,
                  'tags': [tag.name for tag in r.tags.all()],
                  'gender': r.gender,
                  'liker_count': r.likers.count(),
                  'follower_count': r.followers.count(),
                  'visitor_count': r.visitors.count(),
                  'time_created': r.time_created} for r in rs]
        else:
            c = 0
            l = []
        return JsonResponse({'count': c, 'list': l})