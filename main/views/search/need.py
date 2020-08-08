from django import forms
from django.http import JsonResponse
from django.views.generic import View

from main.models import User, Team
from main.models.need import TeamNeed
from util.decorator.param import validate_args, fetch_object


class NeedSearch(View):
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
        'status': forms.IntegerField(required=False, min_value=0, max_value=2),
        'type': forms.IntegerField(required=False, min_value=0, max_value=2),
        'province': forms.CharField(required=False, max_length=100),
        'field': forms.CharField(required=False, max_length=100),
        'team_id': forms.IntegerField(required=False, min_value=0),
        'title': forms.CharField(required=False, max_length=20),
    })
    @fetch_object(Team.objects, 'team', force=False)
    def get(self, request, title=None, team=None, type=None, status=None, province=None, field=None, offset=0, limit=10, **kwargs):
        """
        获取发布中的需求列表

        :param offset: 起始量
        :param limit: 偏移量
        :param type: 需求类型 - 0: member, 1: outsource, 2: undertake
        :param status: 需求状态 - 0: pending, 1: completed, 2: removed
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
        qs = TeamNeed.objects
        if title is not None:
            qs = qs.filter(title__contains=title)
        if team is not None:
            qs = qs.filter(team=team)
        if type is not None:
            qs = qs.filter(type=type)
        if status is not None:
            qs = qs.filter(status=status)
        else:
            qs = qs.filter(status=0)
        if province is not None:
            qs = qs.filter(province=province)
        if field is not None:
            qs = qs.filter(field=field)
        c = qs.count()
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
            need_dic['field'] = n.field
            need_dic['province'] = n.province
            l.append(need_dic)
        return JsonResponse({'count': c, 'list': l, 'code': 0})
