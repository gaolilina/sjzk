from django import forms
from django.http import JsonResponse
from django.views.generic import View

from main.models import User, Team
from main.models.need import TeamNeed
from main.utils import abort, get_score_stage
from util.decorator.auth import app_auth
from util.decorator.param import validate_args, fetch_object


class FollowedTeamNeedList(View):
    @app_auth
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
        'status': forms.IntegerField(required=False, min_value=0, max_value=2),
        'type': forms.IntegerField(required=False, min_value=0, max_value=2)
    })
    def get(self, request, type=None, status=None, offset=0, limit=10, ):
        """获取用户的关注需求列表

        :param offset: 起始量
        :param limit: 偏移量
        :param type: 需求类型
        :param status: 需求状态
        :return:
            count: 需求总数
            list: 需求列表
                need_id: 需求ID
                team_id: 团队ID
                team_name: 团队名称
                icon_url: 团队头像
                status: 需求状态
                title: 需求标题
                number: 所需人数/团队人数
                degree: 需求学历
                members: 需求的加入者
                time_created: 发布时间
        """
        c = request.user.followed_needs.count()
        qs = request.user.followed_needs.all()

        if type is not None:
            qs = qs.filter(type=type)
        if status is not None:
            qs = qs.filter(status=status)
        needs = qs[offset:offset + limit]
        l = list()
        for n in needs:
            need_dic = dict()
            members = dict()
            if n.members:
                ids = n.members.split("|")
                for id in ids:
                    id = int(id)
                    if n.type == 0:
                        members[id] = User.enabled.get(id=id).name
                    else:
                        members[id] = Team.enabled.get(id=id).name
            need_dic['id'] = n.id
            need_dic['team_id'] = n.team.id
            need_dic['team_name'] = n.team.name
            need_dic['number'] = n.number
            need_dic['icon_url'] = n.team.icon
            need_dic['status'] = n.status
            need_dic['title'] = n.title
            need_dic['degree'] = n.degree
            need_dic['members'] = members
            need_dic['time_created'] = n.time_created
            l.append(need_dic)
        return JsonResponse({'count': c, 'list': l, 'code': 0})


class FollowedTeamNeed(View):
    @fetch_object(TeamNeed.objects, 'need')
    @app_auth
    def get(self, request, need):
        """判断当前用户是否关注了need"""

        if request.user.followed_needs.filter(followed=need).exists():
            abort(200)
        abort(403, '未关注该需求')

    @fetch_object(TeamNeed.objects, 'need')
    @app_auth
    def post(self, request, need):
        """令当前用户关注need"""

        if request.user.followed_needs.filter(followed=need).exists():
            abort(403, '已经关注过该需求')
        request.user.followed_needs.create(followed=need)
        request.user.score += get_score_stage(1)
        request.user.score_records.create(
            score=get_score_stage(1), type="活跃度", description="增加一个关注")
        request.user.save()
        abort(200)

    @fetch_object(TeamNeed.objects, 'need')
    @app_auth
    def delete(self, request, need):
        """令当前用户取消关注need"""

        qs = request.user.followed_needs.filter(followed=need)
        if qs.exists():
            # 积分
            request.user.score -= get_score_stage(1)
            request.user.score_records.create(
                score=-get_score_stage(1), type="活跃度",
                description="取消关注")
            qs.delete()
            abort(200)
        abort(403, '未关注过该需求')