from django import forms
from django.http import JsonResponse
from django.views.generic import View
from main.responses import Http200

from main.models import NotificationReceipt
from main.utils.decorators import require_token, validate_args, fetch_object


class Notifications(View):
    get_dict = {
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
    }

    @require_token
    @validate_args(get_dict)
    def get(self, request, offset=0, limit=10):
        """
        获取通知列表

        :param offset: 偏移量
        :param limit: 数量上限
        :return:
            count: 通知总数
            unread_count: 未读通知总数
            list:
                id: 接收凭据ID
                sender: 发送方名称
                content: 通知内容
                create_time: 发送时间
        """
        i, j = offset, offset + limit
        qs = request.user.notifications
        c = qs.count()
        l = [{'id': r.id,
              'sender': r.sender,
              'content': r.content,
              'create_time': r.create_time} for r in qs.all()[i:j]]
        # 将已拉取的通知标记为已读
        ids = qs.all()[i:j].values('id')
        request.user.notifications.filter(id__in=ids).update(is_read=True)
        uc = qs.filter(is_read=False).count()
        return JsonResponse({'count': c, 'unread_count': uc, 'list': l})

    @require_token
    def delete(self, request):
        """
        将所有通知标记为删除状态

        """
        request.user.notifications.update(is_enabled=False)
        return Http200()


class Notification(View):
    @fetch_object(NotificationReceipt.enabled, 'receipt')
    @require_token
    def delete(self, request, receipt):
        """
        将某收据对应的通知标记为删除状态

        """
        receipt.is_enabled = False
        receipt.save(update_fields=['is_enabled'])
        return Http200()
