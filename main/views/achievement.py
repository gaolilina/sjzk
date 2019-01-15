from django import forms
from django.http import JsonResponse
from django.views.generic import View

from main.utils import abort, save_uploaded_image
from main.utils.dfa import check_bad_words
from main.views.common import LikerList, Liker
from ..models import User, UserAchievementLiker, \
    UserAchievement

from ..utils.decorators import *


# noinspection PyMethodOverriding
class UserAchievementLikerList(LikerList):
    @require_token
    @fetch_object(UserAchievement.objects, 'achievement')
    def get(self, request, achievement):
        return super().get(request, achievement)

    @require_token
    @fetch_object(UserAchievement.objects, 'achievement')
    def post(self, request, achievement):
        UserAchievementLiker(liked=achievement, liker=request.user).save()
        return JsonResponse({})

    @require_token
    @fetch_object(UserAchievement.objects, 'achievement')
    def delete(self, request, achievement):
        UserAchievementLiker.objects.get(liked=achievement, liker=request.user).delete()
        return JsonResponse({})


class UserAchievementRequire(Liker):
    @fetch_object(UserAchievement.objects, 'achievement')
    @fetch_object(User.enabled, 'other_user')
    @require_token
    def get(self, request, achievement, other_user):
        return super(UserAchievementRequire, self).get(request, achievement, other_user)


# noinspection PyUnusedLocal
class AchievementList(View):
    ORDERS = ('time_created', '-time_created')

    @fetch_object(User.enabled, 'user')
    @require_token
    @validate_args({
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
        'order': forms.IntegerField(required=False, min_value=0, max_value=3),
    })
    def get(self, request, user, offset=0, limit=10, order=1):
        """获取团队发布的成果

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
        c = user.achievements.count()
        achievements = user.achievements.order_by(k)[i:j]
        l = [{'id': a.id,
              'description': a.description,
              'picture': a.picture,
              'time_created': a.time_created,
              'yes_count': a.likers.count(),
              'is_yes': request.user in a.likers.all()} for a in achievements]
        return JsonResponse({'count': c, 'list': l})

    @fetch_object(User.enabled, 'user')
    @require_verification_token
    @validate_args({
        'description': forms.CharField(min_length=1, max_length=100),
    })
    def post(self, request, user, description):
        """发布成果

        :param description: 成果描述
        :return: achievement_id: 成果id
        """
        if check_bad_words(description):
            abort(403, '含有非法词汇')

        achievement = UserAchievement(user=user, description=description)
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
class AllAchievementList(View):
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
        c = UserAchievement.objects.count()
        achievements = UserAchievement.objects.order_by(k)[i:j]
        l = [{'id': a.id,
              'user_id': a.user.id,
              'user_name': a.user.name,
              'icon_url': a.user.icon,
              'description': a.description,
              'picture': a.picture,
              'time_created': a.time_created,
              'yes_count': a.likers.count(),
              'is_yes': request.user in a.likers.all()} for a in achievements]
        return JsonResponse({'count': c, 'list': l})


# noinspection PyUnusedLocal
class AllAchievement(View):
    @fetch_object(UserAchievement.objects, 'achievement')
    @require_verification_token
    def delete(self, request, user, achievement):
        """删除成果"""

        achievement.delete()
        abort(200)