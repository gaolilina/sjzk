from django import forms
from django.db import transaction
from django.http import JsonResponse
from django.views.generic import View

from main.models import Team
from main.models.need import TeamNeed
from main.utils import abort, action, get_score_stage
from main.utils.decorators import require_verification_token
from util.decorator.auth import app_auth
from util.decorator.param import fetch_object, validate_args


class NeedTeamList(View):
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
                id: 团队ID
                name: 团队昵称
                icon_url: 团队头像
                owner_id: 创建者ID
                liker_count: 点赞数
                visitor_count: 最近7天访问数
                member_count: 团队成员人数
                fields: 所属领域，格式：['field1', 'field2']
                tags: 标签，格式：['tag1', 'tag2', ...]
                time_created: 注册时间
        """
        i, j, k = offset, offset + limit, self.ORDERS[order]
        tids = []
        if need.members:
            ids = need.members.split("|")
            for tid in ids:
                tids.append(int(tid))
            members = Team.enabled.filter(id__in=tids)
            c = members.count()
            rs = members.order_by(k)[i:j]
            l = [{'id': r.id,
                  'name': r.name,
                  'icon_url': r.icon,
                  'owner_id': r.owner.id,
                  'liker_count': r.likers.count(),
                  'visitor_count': r.visitors.count(),
                  'member_count': r.members.count(),
                  'fields': [r.field1, r.field2],
                  'tags': [tag.name for tag in r.tags.all()],
                  'time_created': r.time_created} for r in rs]
        else:
            c = 0
            l = []
        return JsonResponse({'count': c, 'list': l})


class NeedRequestList(View):
    @fetch_object(TeamNeed.objects, 'need')
    @fetch_object(Team.enabled, 'team')
    @app_auth
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
    })
    def get(self, request, need, team, offset=0, limit=10):
        """获取需求的合作申请列表

        :param offset: 偏移量
        :return: request.user 不为团队创始人时，404
        :return: request.user 为团队创始人时
            count: 申请总数
            list: 申请列表
                id: 申请者ID
                team_id: 申请团队ID
                name: 申请团队名称
                icon_url: 申请团队头像
                time_created: 申请时间
        """
        if request.user == need.team.owner and need.team == team:
            # 拉取需求的申请合作信息
            c = need.cooperation_requests.count()
            qs = need.cooperation_requests.all()[offset:offset + limit]

            l = [{'id': r.sender.owner.id,
                  'team_id': r.sender.id,
                  'name': r.sender.name,
                  'icon_url': r.sender.icon,
                  'time_created': r.time_created} for r in qs]
            return JsonResponse({'count': c, 'list': l})
        abort(404, '只有队长可以操作')

    @fetch_object(TeamNeed.objects, 'need')
    @fetch_object(Team.enabled, 'team')
    @require_verification_token
    def post(self, request, need, team):
        """向需求发出合作申请

        """
        if need.cooperation_requests.filter(sender=team).exists():
            abort(404, '合作申请已经发送过')
        if need.cooperation_invitations.filter(invitee=team).exists():
            abort(404, '合作申请已经发送过')
        if request.user == team.owner:
            need.cooperation_requests.create(sender=team)
            abort(200)
        abort(404, '只有队长能操作')


class NeedRequest(View):

    @fetch_object(TeamNeed.objects, 'need')
    @fetch_object(Team.enabled, 'team')
    @require_verification_token
    def post(self, request, need, team):
        """同意加入申请并将创始人加入自己团队（对方需发送过合作申请）"""

        if request.user != need.team.owner:
            abort(404, '只有队长能操作')

        if need.cooperation_requests.filter(sender=team).exists():
            # 在事务中建立关系，并删除对应的申请合作
            with transaction.atomic():
                need.cooperation_requests.filter(sender=team).delete()
                if need.team.members.filter(user=team.owner).exists():
                    abort(200)
                # 保存需求的加入团队Id
                if len(need.members) > 0:
                    need.members = need.members + "|" + str(team.id)
                else:
                    need.members = str(team.id)
                need.save()

                need.team.members.create(user=team.owner)
                action.join_team(team.owner, need.team)
                request.user.score += get_score_stage(1)
                request.user.score_records.create(
                    score=get_score_stage(1), type="能力",
                    description="与其他团队合作")
                team.score += get_score_stage(1)
                team.score_records.create(
                    score=get_score_stage(1), type="能力",
                    description="与其他团队合作")
                request.user.save()
                team.save()
            abort(200)
        abort(404, '对方未发送过申请合作')

    @fetch_object(TeamNeed.objects, 'need')
    @fetch_object(Team.enabled, 'team')
    @require_verification_token
    def delete(self, request, need, team):
        """忽略某团队的合作申请"""

        if request.user != need.team.owner:
            abort(403, '只有队长可以操作')

        qs = need.cooperation_requests.filter(sender=team)
        if not qs.exists():
            abort(404, '合作申请不存在')
        qs.delete()
        abort(200)


class TeamApplyNeedList(View):
    @fetch_object(Team.enabled, 'team')
    @app_auth
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
    })
    def get(self, request, team, offset=0, limit=10):
        """获取团队发出的的合作申请列表

        :param offset: 偏移量
        :return: request.user 不为团队创始人时，404
        :return: request.user 为团队创始人时
            count: 申请总数
            list: 申请列表
                team_id: 申请的团队ID
                need_id: 申请的需求ID
                title: 申请的需求标题
                name: 申请团队名称
                icon_url: 申请团队头像
                time_created: 申请时间
        """
        if request.user == team.owner:
            # 拉取申请合作信息
            c = team.cooperation_requests.count()
            qs = team.cooperation_requests.all()[offset:offset + limit]

            l = [{'team_id': r.need.team.id,
                  'id': r.need.id,
                  'name': r.need.team.name,
                  'title': r.need.title,
                  'icon_url': r.need.team.icon,
                  'time_created': r.time_created} for r in qs]
            return JsonResponse({'count': c, 'list': l})
        abort(404, '只有队长能操作')
