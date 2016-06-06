from django import forms
from django.http import JsonResponse
from django.views.generic import View

from main.decorators import require_token, validate_input, validate_json_input
from main.models import User, UserTag


class UserSearch(View):
    pagination = dict(
        offset=forms.IntegerField(required=False, min_value=0),
        limit=forms.IntegerField(required=False, min_value=0),
        order=forms.IntegerField(required=False, min_value=0, max_value=3),
    )
    available_orders = ('create_time', '-create_time', 'name', '-name')
    conditions = dict(username=forms.CharField(max_length=15))

    @require_token
    @validate_input(pagination)
    @validate_json_input(conditions)
    def get(self, request, data, offset=0, limit=10, order=1):
        """
        搜索用户

        :param offset: 偏移量
        :param limit: 数量上限
        :param order: 排序方式
            0: 注册时间升序
            1: 注册时间降序（默认值）
            2: 昵称升序
            3: 昵称降序
        :param data: 搜索条件
            username: 用户名包含字段

        :return:
            count: 用户总数
            list: 用户列表
                id: 用户ID
                username: 用户名
                name: 用户昵称
                gender: 性别
                like_count: 点赞数
                fan_count: 粉丝数
                visitor_count: 访问数
                icon_url: 用户头像URL
                tags: 标签
                create_time: 注册时间
        """
        i, j, k = offset, offset + limit, self.available_orders[order]
        c = User.enabled.filter(username__icontain=data['username']).count()
        users = User.enabled.order_by(k)[i:j]
        l = [{'id': u.id,
              'username': u.username,
              'name': u.name,
              'gender': u.profile.gender,
              'like_count': u.like_count,
              'fan_count': u.fan_count,
              'visitor_count': u.visitor_count,
              'icon_url': u.icon_url,
              'tags': UserTag.objects.get_tags(u),
              'create_time': u.create_time} for u in users]
        return JsonResponse({'count': c, 'list': l})
