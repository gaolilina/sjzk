from django import forms
from django.http import JsonResponse
from django.views.generic import View

from main.models import Team, Achievement
from main.utils import abort, save_uploaded_image, get_score_stage
from main.utils.decorators import *
from main.utils.dfa import check_bad_words

__all__ = ('AllTeamAchievementListView', 'AllTeamAchievementView', 'TeamAchievementList',)


# noinspection PyUnusedLocal
class AllTeamAchievementListView(View):
    ORDERS = ('time_created', '-time_created')

    @require_token
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
        'order': forms.IntegerField(required=False, min_value=0, max_value=3),
    })
    def get(self, request, offset=0, limit=10, order=1):
        """获取所有团队发布的成果

        :param offset: 偏移量
        :param limit: 数量上限
        :param order: 排序方式
            0: 发布时间升序
            1: 发布时间降序（默认值）
        :return:
            count: 成果总数
            list: 成果列表
                id: 成果ID
                team_id: 团队ID
                team_name: 团队名称
                icon_url: 团队头像
                description: 成果描述
                picture: 图片
                time_created: 发布时间
        """
        i, j, k = offset, offset + limit, self.ORDERS[order]
        c = Achievement.objects.count()
        # 团队成果，要 team 非空
        achievements = Achievement.objects.filter(team__isnull=False).order_by(k)[i:j]
        l = [{'id': a.id,
              'team_id': a.team.id,
              'team_name': a.team.name,
              'icon_url': a.team.icon,
              'description': a.description,
              'picture': a.picture,
              'yes_count': a.likers.count(),
              'is_yes': request.user in a.likers.all(),
              'require_count': a.requirers.count(),
              'is_require': request.user in a.requirers.all(),
              'time_created': a.time_created} for a in achievements]
        return JsonResponse({'count': c, 'list': l})


# noinspection PyUnusedLocal
class AllTeamAchievementView(View):
    @require_verification_token
    @fetch_object(Achievement.objects, 'achievement')
    def get(self, request, user, achievement):
        """获取成果详情"""
        return JsonResponse({
            'achievement_id': achievement.id,
            'team_id': achievement.team.id,
            'team_name': achievement.team.name,
            'icon_url': achievement.team.icon,
            'desc': achievement.description,
            'pics': achievement.picture,
        })

    @fetch_object(Achievement.objects, 'achievement')
    @require_verification_token
    def delete(self, request, team, achievement):
        """删除成果"""

        if request.user != achievement.team.owner:
            abort(403, '只有队长可以操作')
        achievement.delete()
        abort(200)


# noinspection PyUnusedLocal
class TeamAchievementList(View):
    ORDERS = ('time_created', '-time_created')

    @fetch_object(Team.enabled, 'team')
    @require_token
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
        'order': forms.IntegerField(required=False, min_value=0, max_value=3),
    })
    def get(self, request, team, offset=0, limit=10, order=1):
        """获取某团队发布的成果

        :param offset: 偏移量
        :param limit: 数量上限
        :param order: 排序方式
            0: 发布时间升序
            1: 发布时间降序（默认值）
        :return:
            count: 成果总数
            list: 成果列表
                id: 成果ID
                description: 成果描述
                picture: 图片
                time_created: 发布时间
        """
        i, j, k = offset, offset + limit, self.ORDERS[order]
        c = team.achievements.count()
        achievements = team.achievements.order_by(k)[i:j]
        l = [{'id': a.id,
              'description': a.description,
              'picture': a.picture,
              'time_created': a.time_created} for a in achievements]
        return JsonResponse({'count': c, 'list': l})

    @require_verification_token
    @fetch_object(Team.enabled, 'team')
    @validate_args({
        'description': forms.CharField(min_length=1, max_length=100),
    })
    def post(self, request, team, description):
        """发布成果

        :param description: 成果描述
        :return: achievement_id: 成果id
        """
        if request.user != team.owner:
            abort(403, '只有队长可以操作')

        if check_bad_words(description):
            abort(403, '含有非法词汇')

        achievement_num = team.achievements.count()
        if achievement_num == 0:
            team.score += get_score_stage(2)
            team.score_records.create(
                score=get_score_stage(2), type="初始数据",
                description="首次发布团队成果")

        achievement = Achievement(team=team, description=description)
        picture = request.FILES.get('image')
        if picture:
            filename = save_uploaded_image(picture)
            if filename:
                achievement.picture = filename
        else:
            abort(400, '图片上传失败')
        achievement.save()

        request.user.score += get_score_stage(1)
        request.user.score_records.create(
            score=get_score_stage(1), type="能力", description="发布一个团队成果")
        request.user.save()
        team.score += get_score_stage(1)
        team.score_records.create(
            score=get_score_stage(1), type="活跃度", description="发布一个团队成果")
        team.save()
        return JsonResponse({'achievement_id': achievement.id})
