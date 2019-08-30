from django import forms
from django.http import JsonResponse
from django.views.generic import View

from main.utils import action, abort
from util.decorator.auth import app_auth
from util.decorator.param import validate_args


class FavoredActionList(View):
    get_dict = {
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
        'order': forms.IntegerField(required=False, min_value=0, max_value=1),
        'is_expert': forms.IntegerField(required=False)
    }
    ORDERS = ('time_created', '-time_created')

    @validate_args(get_dict)
    def get(self, request, obj, offset=0, limit=10, order=1, is_expert=None):
        """获取动态收藏列表

        :param offset: 偏移量
        :param order: 排序方式
            0: 收藏时间升序
            1: 收藏时间降序（默认值）
        :return:
            count: 收藏总数
            list: 收藏列表
                action_id: 动态id
                id: 主语的id
                name: 主语的名称
                icon: 主语的头像
                action: 相关动作
                object_type: 相关对象的类型
                object_id: 相关对象的ID
                object_name: 相关对象名称
                icon_url: 头像
                related_object_type: 额外相关对象的类型
                related_object_id: 额外相关对象的ID
                related_object_name: 额外相关对象的名称
                liker_count: 点赞数
                comment_count: 评论数
                time_created: 创建时间
        """
        if is_expert == 1:
            obj = obj.filter(favored__entity__role__contains='专家')
        elif is_expert == 0:
            obj = obj.exclude(favored__entity__role__contains='专家')
        c = obj.count()
        qs = obj.order_by(self.ORDERS[order])[offset:offset + limit]

        l = [{'id': i.favored.entity.id,
              'action_id': i.favored.id,
              'name': i.favored.entity.name,
              'icon': i.favored.entity.icon,
              'action': i.favored.action,
              'object_type': i.favored.object_type,
              'object_id': i.favored.object_id,
              'object_name': action.get_object_name(i.favored),
              'icon_url': action.get_object_icon(i.favored),
              'related_object_type': i.favored.related_object_type,
              'related_object_id': i.favored.related_object_id,
              'related_object_name': action.get_related_object_name(i.favored),
              'liker_count': i.favored.likers.count(),
              'comment_count': i.favored.comments.count(),
              'time_created': i.favored.time_created,
              } for i in qs]
        return JsonResponse({'count': c, 'list': l})


class FavoredEntity(View):
    """与当前用户收藏行为相关的View"""

    @app_auth
    def get(self, request, entity):
        """判断当前用户是否收藏过某个对象"""

        if entity.favorers.filter(favorer=request.user).exists():
            abort(200)
        abort(404, '未收藏过')

    @app_auth
    def post(self, request, entity):
        """收藏某个对象"""

        if not entity.favorers.filter(favorer=request.user).exists():
            entity.favorers.create(favorer=request.user)

            request.user.save()
        abort(200)

    @app_auth
    def delete(self, request, entity):
        """对某个对象取消点赞"""

        entity.favorers.filter(favorer=request.user).delete()
        abort(200)