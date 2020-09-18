import datetime

from django import forms
from django.http import JsonResponse
from django.views.generic import View

from main.models import Team, Achievement
from main.utils import abort, get_score_stage, save_uploaded_image, deal_tags
from main.utils.decorators import require_verification_token, require_role_token
from main.utils.dfa import check_bad_words
from util.decorator.auth import app_auth
from util.decorator.param import fetch_object, validate_args


class PublishTeamAchievement(View):
    ORDERS = ('time_created', '-time_created')

    @fetch_object(Team.enabled, 'team')
    @app_auth
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
        'order': forms.IntegerField(required=False, min_value=0, max_value=3),
    })
    def get(self, request, team, offset=0, limit=10, order=1):
        """获取某团队发布的成果
        TODO 使用 SearchTeamAchievement

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
              'tags': deal_tags(a.tags),
              'time_created': a.time_created} for a in achievements]
        return JsonResponse({'count': c, 'list': l, 'code': 0})

    @require_verification_token
    @fetch_object(Team.enabled, 'team')
    @validate_args({
        'description': forms.CharField(min_length=1, max_length=100),
        'name': forms.CharField(min_length=1, max_length=40),
        'tags': forms.CharField(max_length=256, required=False),
    })
    def post(self, request, team, name, description, tags):
        """发布成果

        :param description: 成果描述
        :return: achievement_id: 成果id
        """
        if request.user != team.owner:
            abort(403, '只有队长可以操作')

        if check_bad_words(description):
            abort(400, '含有非法词汇')

        achievement_num = team.achievements.count()
        if achievement_num == 0:
            team.score += get_score_stage(2)
            team.score_records.create(
                score=get_score_stage(2), type="初始数据",
                description="首次发布团队成果")

        achievement = Achievement(team=team, name=name, description=description, user=request.user, tags=tags)
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
        return JsonResponse({'achievement_id': achievement.id, 'code': 0})


class PublishUserAchievement(View):
    ORDERS = ('time_created', '-time_created')

    @require_role_token
    def get(self, request, offset=0, limit=10, order=1):
        """获取当前用户发布的成果
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
        c = request.user.achievements.count()
        achievements = request.user.achievements.order_by(k)[i:j]
        l = [{'id': a.id,
              'name': a.name,
              'user_id': request.user.id,
              'user_name': request.user.name,
              'require_count': a.requirers.count(),
              'is_require': request.user in a.requirers.all(),
              'yes_count': a.likers.count(),
              'is_yes': request.user in a.likers.all(),
              'icon_url': request.user.icon,
              'description': a.description,
              'picture': a.picture,
              'time_created': a.time_created,
              'tags': deal_tags(a.tags)} for a in achievements]
        return JsonResponse({'count': c, 'list': l, 'code': 0})


    @require_role_token
    @validate_args({
        'description': forms.CharField(min_length=1, max_length=100),
        'name': forms.CharField(min_length=1, max_length=40),
        'tags': forms.CharField(max_length=256, required=False)
    })
    def post(self, request, name, description, tags):
        """发布成果

        :param description: 成果描述
        :return: achievement_id: 成果id
        """
        # 检查非法词汇
        if check_bad_words(description):
            abort(400, '含有非法词汇')
        system_param = request.param
        # 检查发布的时间间隔
        last_time = datetime.datetime.now() + datetime.timedelta(minutes=system_param.publish_min_minute)
        if Achievement.objects.filter(user=request.user, time_created__gt=last_time).count() > 0:
            abort(403, '发布成果时间间隔不能小于{}分钟'.format_map(system_param.publish_min_minute))
        # 检查上传图片数量
        max_pic = system_param.pic_max + 1
        if 'image' + str(max_pic) in request.FILES:
            abort(403, '最多上传' + str(system_param.pic_max) + '张图片')
        pics = [
            request.FILES.get('image' + str(i)) if 'image' + str(i) in request.FILES else None
                for i in range(1, max_pic)]
        achievement = Achievement(user=request.user, description=description, name=name, tags=tags)
        if len(pics) != 0:
            filenames = []
            for p in pics:
                if p is None:
                    continue
                filenames.append(save_uploaded_image(p))
            achievement.picture = str(filenames)
        else:
            abort(500, '图片上传失败')
        achievement.save()

        return JsonResponse({'achievement_id': achievement.id, 'code': 0})