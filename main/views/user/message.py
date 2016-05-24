import json

from django import forms
from django.db import transaction
from django.http import JsonResponse
from django.views.generic import View

from main.decorators import require_token, validate_input, check_object_id
from main.models import User, Contact, Message
from main.responses import Http200


class Contacts(View):
    get_dict = {
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
    }

    @require_token
    @validate_input(get_dict)
    def get(self, request, offset=0, limit=10):
        """
        获取联系人列表

        :param offset: 偏移量
        :param limit: 数量上限
        :return:
            count: 联系人总数
            list: 联系人列表
                id: 用户ID
                username: 用户名
                icon_url: 头像URL
                count: 总消息数
                unread_count: 未读消息数
                last_message: 最近一条消息
                    id: 消息ID
                    sender_id: 发送者ID
                    receiver_id: 接受者ID
                    data: 消息数据（JSON）
                    create_time: 发送时间
        """
        i, j = offset, offset + limit
        qs = Contact.enabled.related_to(request.user)
        c = qs.count()
        l = []
        for r in qs[i:j]:
            u = r.user_a if request.user != r.user_a else r.user_b
            l.append({
                'id': u.id,
                'username': u.username,
                'icon_url': u.icon_url,
                'count': Message.enabled.related_to(request.user, u).count(),
                'unread_count': Message.enabled.filter(
                    sender=u, receiver=request.user, is_read=False).count(),
                'last_message': {
                    'id': r.last_message.id,
                    'sender_id': r.last_message.sender.id,
                    'receiver_id': r.last_message.receiver.id,
                    'data': r.last_message.data,
                    'create_time': r.last_message.create_time,
                }
            })
        return JsonResponse({'count': c, 'list': l})


class Messages(View):
    get_dict = {
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
    }

    @check_object_id(User.enabled, 'user')
    @require_token
    @validate_input(get_dict)
    def get(self, request, user, offset=0, limit=10):
        """
        获取与某用户相关的消息

        :param offset: 偏移量
        :param limit: 数量上限
        :return:
            count: 消息总数
            unread_count: （拉取之后）未读消息数
            list: 消息列表
                id: 消息ID
                sender_id: 发送者ID
                receiver_id: 接受者ID
                data: 消息数据（JSON）
                create_time: 消息发送时间
        """
        i, j = offset, offset + limit
        qs = Message.enabled.related_to(request.user, user)
        c = qs.count()
        l = [{'id': r.id,
              'sender_id': r.sender.id,
              'receiver_id': r.receiver.id,
              'data': r.data,
              'create_time': r.create_time} for r in qs[i:j]]
        # 将拉取的消息标记为已读
        ids = qs[i:j].values('id')
        Message.enabled.filter(id__in=ids).update(is_read=True)
        uc = Message.enabled.filter(
            sender=user, receiver=request.user, is_read=False).count()
        return JsonResponse({'count': c, 'unread_count': uc, 'list': l})

    post_dict = {'content': forms.CharField(max_length=200)}

    @check_object_id(User.enabled, 'user')
    @require_token
    @transaction.atomic
    def post(self, request, user, content):
        """
        向某用户发送消息

        """
        data = {'content': content, 'is_sharing': False}
        data = json.dumps(data)
        # 保存消息数据
        msg = Message.enabled.create(
            sender=request.user, receiver=user, data=data)
        # 更新联系人消息
        Contact.enabled.update_record(request.user, user, msg)
        return Http200()
