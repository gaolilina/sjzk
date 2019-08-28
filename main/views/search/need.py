from django import forms
from django.http import JsonResponse
from django.views.generic import View

from main.models import User, Team
from main.models.need import TeamNeed
from util.decorator.param import validate_args


class NeedSearch(View):
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
        'status': forms.IntegerField(required=False, min_value=0, max_value=2),
        'type': forms.IntegerField(required=False, min_value=0, max_value=2),
        'name': forms.CharField(max_length=20),
    })
    def get(self, request, name, type=None, status=None, offset=0, limit=10):
        """
        搜索发布中的需求列表

        :param offset: 偏移量
        :param name: 标题包含字段
        :param type: 需求的类型，默认为获取全部
        :param status: 需求状态，默认为获取全部
        :return:
            count: 需求总数
            list: 需求列表
                need_id: 需求ID
                team_id: 团队ID
                team_name: 团队名称
                icon_url: 团队头像
                status: 需求状态
                type: 需求类型
                title: 需求标题
                number: 所需人数/团队人数
                degree: 需求学历
                members: 需求的加入者
                time_created: 发布时间
        """
        qs = TeamNeed.objects.filter(title__icontains=name)
        if status is not None:
            # 按需求状态搜索
            qs = qs.filter(status=status)
        if type is not None:
            # 按需求类别搜索
            qs = qs.filter(type=type)
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
            need_dic['type'] = n.type
            need_dic['title'] = n.title
            need_dic['degree'] = n.degree
            need_dic['members'] = members
            need_dic['time_created'] = n.time_created
            l.append(need_dic)
        return JsonResponse({'count': c, 'list': l})