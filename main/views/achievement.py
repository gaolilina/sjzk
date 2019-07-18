import datetime

from django import forms
from django.http import JsonResponse
from django.views.generic import View

from main.utils import abort, save_uploaded_image
from main.utils.dfa import check_bad_words
from main.views.search.achievement import SearchUserAchievement
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

    def get(self, request, offset=0, limit=10, order=1):
        return SearchUserAchievement().get(request, offset, limit, order)

    @require_role_token
    @validate_args({
        'description': forms.CharField(min_length=1, max_length=100),
    })
    def post(self, request, description):
        """发布成果

        :param description: 成果描述
        :return: achievement_id: 成果id
        """
        # 检查非法词汇
        if check_bad_words(description):
            abort(403, '含有非法词汇')
        system_param = request.param
        # 检查发布的时间间隔
        last_time = datetime.datetime.now() + datetime.timedelta(minutes=system_param.publish_min_minute)
        if Achievement.objects.filter(user=request.user, time_created__gt=last_time).count() > 0:
            abort(403, '发布成果时间间隔不能小于{}分钟'.format_map(system_param.publish_min_minute))
        # 检查上传图片数量
        max_pic = system_param.pic_max + 1
        if 'image' + str(max_pic) in request.FILES:
            abort(403, '最多上传' + str(max_pic) + '张图片')
        pics = [
            request.FILES.get('image' + str(i)) if 'image' + str(i) in request.FILES else None
                for i in range(1, max_pic)]
        achievement = Achievement(user=request.user, description=description)
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
            'yes_count': achievement.likers.count(), # 点赞数
            'is_yes': request.user in achievement.likers.all(), # 是否点赞
            'require_count': achievement.requirers.count(), # 需求树
            'is_require': request.user in achievement.requirers.all(), # 是否需求
        })

    @require_verification_token
    @fetch_object(Achievement.objects, 'achievement')
    def delete(self, request, achievement):
        """删除成果"""
        user = request.user
        achievement.delete()
        abort(200)
