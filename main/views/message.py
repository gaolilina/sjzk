from django import forms
from django.db import transaction
from django.http import JsonResponse
from django.views.generic import View

from main.decorators import require_token, validate_input, check_object_id
from main.models import User, Team
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
                unread_count: 未读消息数
                update_time: 最近联系时间
                last_message: 最近一条消息
                    content: 消息内容
                    is_sharing: 是否分享消息
                    sharing_type: 分享类型
                    sharing_object_id: 分享对象ID
        """
        i, j = offset, offset + limit
        c = request.user.contacts.count()
        qs = request.user.contacts.all()[i:j]
        l = [{'id': r.contact.id,
              'username': r.contact.username,
              'icon_url': r.contact.icon_url,
              'unread_count': request.user.messages.filter(
                  other_user=r.contact, direction=0, is_read=False).count(),
              'update_time': r.update_time,
              'last_message': {
                  'content': r.last_message.content,
                  'is_sharing': r.last_message.is_sharing,
                  'sharing_type': r.last_message.sharing_type,
                  'sharing_object_id': r.last_message.sharing_object_id,
              }} for r in qs]
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
                direction: 收发方向，0-收，1-发
                content: 消息内容
                is_sharing: 是否分享消息
                sharing_type: 分享类型
                sharing_object_id: 分享对象ID
                sharing_object_name: 分享对象名称
                sharing_object_icon_url: 分享对象图标
                create_time: 消息发送时间
        """
        i, j = offset, offset + limit
        qs = request.user.messages.filter(other_user=user)
        c = qs.count()
        l = [{'direction': r.direction,
              'content': r.content,
              'is_sharing': r.is_sharing,
              'sharing_type': r.sharing_type,
              'sharing_object_id': r.sharing_object_id,
              'sharing_object_name': r.sharing_object_name,
              'sharing_object_icon_url': r.sharing_object_icon_url,
              'create_time': r.create_time} for r in qs[i:j]]
        # 将拉取的消息标记为已读
        ids = qs[i:j].values('id')
        request.user.messages.filter(id__in=ids).update(is_read=True)
        uc = qs.filter(is_read=False).count()
        return JsonResponse({'count': c, 'unread_count': uc, 'list': l})

    post_dict = {'content': forms.CharField(max_length=256)}

    @check_object_id(User.enabled, 'user')
    @require_token
    @validate_input(post_dict)
    @transaction.atomic
    def post(self, request, user, content):
        """
        向某用户发送消息

        """
        # 总共保存两条消息记录，更新或创建两次联系记录
        msg = request.user.messages.create(other_user=user, direction=1,
                                           content=content, is_sharing=False)
        r, created = request.user.contacts.get_or_create(
            contact=user, defaults={'last_message': msg})
        if not created:
            r.last_message = msg
            r.save()

        msg = user.messages.create(other_user=request.user, direction=0,
                                   content=content, is_sharing=False)
        r, created = user.contacts.get_or_create(
            contact=request.user, defaults={'last_message': msg})
        if not created:
            r.last_message = msg
            r.save()

        return Http200()


class Share(View):
    post_dict = {'content': forms.CharField(max_length=256, required=False)}

    @validate_input(post_dict)
    @transaction.atomic
    def post(self, request, user, obj_type, obj_id, content=''):
        """
        向user分享obj

        :param content: 可选的备注信息

        """
        # 总共保存两条消息记录，更新或创建两次联系记录
        msg = request.user.messages.create(
            other_user=user, direction=1, content=content, is_sharing=True,
            sharing_object_type=obj_type, sharing_object_id=obj_id,
        )
        r, created = request.user.contacts.get_or_create(
            contact=user, defaults={'last_message': msg})
        if not created:
            r.last_message = msg
            r.save()

        msg = user.messages.create(
            other_user=request.user, direction=0, content=content,
            is_sharing=False, sharing_object_type=obj_type,
            sharing_object_id=obj_id,
        )
        r, created = user.contacts.get_or_create(
            contact=request.user, defaults={'last_message': msg})
        if not created:
            r.last_message = msg
            r.save()

        return Http200()


# noinspection PyMethodOverriding
class UserShare(Share):
    @check_object_id(User.enabled, 'user')
    @check_object_id(User.enabled, 'other_user')
    @require_token
    def post(self, request, user, other_user):
        """
        向user分享other_user

        """
        return super(UserShare, self).post(request, user, 'user', other_user.id)


# noinspection PyMethodOverriding
class TeamShare(Share):
    @check_object_id(User.enabled, 'user')
    @check_object_id(Team.enabled, 'team')
    @require_token
    def post(self, request, user, team):
        """
        向user分享team

        """
        return super(TeamShare, self).post(request, user, 'team', team.id)
