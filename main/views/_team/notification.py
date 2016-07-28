from django import forms
from django.http import JsonResponse
from django.views.generic import View
from main.models.notification import TeamNotificationReceipt
from main.responses import Http403, Http200

from main.models import Team
from main.utils.decorators import require_token, validate_args, fetch_object


class Notifications(View):
    get_dict = {
        'offset': forms.IntegerField(required=False, min_value=0),
        'limit': forms.IntegerField(required=False, min_value=0),
    }

    @fetch_object(Team.enabled, 'team')
    @require_token
    @validate_args(get_dict)
    def get(self, request, team, offset=0, limit=10):
        """
        获取系统通知列表

        :param team_id: 团队ID
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
        if request.user != team.owner:
            return Http403('recent user ha not authority')

        i, j = offset, offset + limit
        qs = team.notifications
        c = qs.count()
        l = [{'id': r.id,
              'sender': r.sender,
              'content': r.content,
              'create_time': r.create_time} for r in qs.all()[i:j]]
        # 将已拉取的通知标记为已读
        ids = qs.all()[i:j].values('id')
        request.team.notifications.filter(id__in=ids).update(is_read=True)
        uc = qs.filter(is_read=False).count()
        return JsonResponse({'count': c, 'unread_count': uc, 'list': l})

    @fetch_object(Team.enabled, 'team')
    @require_token
    def delete(self, request, team):
        """
        将所有通知标记为删除状态

        :param team_id: 团队ID
        """
        if request.user != team.owner:
            return Http403('recent user ha not authority')

        team.notifications.update(is_enabled=False)
        return Http200()


class Notification(View):
    @fetch_object(Team.enabled, 'team')
    @fetch_object(TeamNotificationReceipt.enabled, 'receipt')
    @require_token
    def delete(self, request, team, receipt):
        """
        将某凭据对应的通知标记为删除状态

        :param team_id: 团队ID
        :param receipt_id: 收据ID
        """
        if request.user != team.owner:
            return Http403('recent user ha not authority')

        receipt.is_enabled = False
        receipt.save(update_fields=['is_enabled'])
        return Http200()
