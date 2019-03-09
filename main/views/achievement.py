from django import forms
from django.http import JsonResponse
from django.views.generic import View

from main.utils import abort, save_uploaded_image
from main.utils.dfa import check_bad_words
from ..models import Achievement
from ..utils.decorators import *


# noinspection PyMethodOverriding
class AchievementDoWhoView(View):
    """
    成果都有关联的群体，比如点赞者，需求者，他们称之为 who
    需要添加或移除 who 中的成员，请使用该类
    """

    @require_token
    @fetch_object(Achievement.objects, 'achievement')
    def post(self, request, achievement, who):
        achievement[who].add(request.user)
        return JsonResponse({})

    @require_token
    @fetch_object(Achievement.objects, 'achievement')
    def delete(self, request, achievement, who):
        achievement[who].remove(request.user)
        return JsonResponse({})


# noinspection PyUnusedLocal
class AllUserAchievementListView(View):
    ORDERS = ('time_created', '-time_created')

    @require_token
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
        'order': forms.IntegerField(required=False, min_value=0, max_value=3),
    })
    def get(self, request, offset=0, limit=10, order=1):
        """获取所有用户发布的成果

        :param offset: 偏移量
        :param limit: 数量上限
        :param order: 排序方式
            0: 发布时间升序
            1: 发布时间降序（默认值）
        :return:
            count: 成果总数
            list: 成果列表
                id: 成果ID
                user_id: 团队ID
                user_name: 团队名称
                icon_url: 团队头像
                description: 成果描述
                picture: 图片
                time_created: 发布时间
        """
        i, j, k = offset, offset + limit, self.ORDERS[order]
        c = Achievement.objects.count()
        achievements = Achievement.objects.filter(team=None).order_by(k)[i:j]
        l = [{'id': a.id,
              'user_id': a.user.id,
              'user_name': a.user.unit1 if a.user.is_role_verified else a.user.name,
              'icon_url': a.user.icon,
              'description': a.description,
              'picture': a.picture,
              'time_created': a.time_created,
              'yes_count': a.likers.count(),
              'is_yes': request.user in a.likers.all(),
              'require_count': a.requirers.count(),
              'is_require': request.user in a.requirers.all(),
              } for a in achievements]
        return JsonResponse({'count': c, 'list': l})

    @require_verification_token
    @validate_args({
        'description': forms.CharField(min_length=1, max_length=100),
    })
    def post(self, request, description):
        """发布成果

        :param description: 成果描述
        :return: achievement_id: 成果id
        """
        if check_bad_words(description):
            abort(403, '含有非法词汇')

        achievement = Achievement(user=request.user, description=description)
        pics = [request.FILES.get('image'), request.FILES.get('image2'), request.FILES.get('image3')]
        if len(pics) != 0:
            filenames = []
            for p in pics:
                if p is None:
                    continue
                filenames.append(save_uploaded_image(p))
            achievement.picture = str(filenames)
        else:
            abort(400, '图片上传失败')
        achievement.save()

        return JsonResponse({'achievement_id': achievement.id})


# noinspection PyUnusedLocal
class AllUserAchievementView(View):
    @require_verification_token
    @fetch_object(Achievement.objects, 'achievement')
    def get(self, request, achievement):
        """获取成果详情"""
        user = request.user
        return JsonResponse({
            'achievement_id': achievement.id,
            'user_id': achievement.user.id,
            'user_name': achievement.user.unit1 if achievement.user.is_role_verified else achievement.user.name,
            'icon_url': achievement.user.icon,
            'desc': achievement.description,
            'pics': achievement.picture,
            'yes_count': achievement.likers.count(),
            'is_yes': request.user in achievement.likers.all(),
            'require_count': achievement.requirers.count(),
            'is_require': request.user in achievement.requirers.all(),
        })

    @require_verification_token
    @fetch_object(Achievement.objects, 'achievement')
    def delete(self, request, achievement):
        """删除成果"""
        user = request.user
        achievement.delete()
        abort(200)
