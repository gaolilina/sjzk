from django.http import JsonResponse

# from team.models import Team
from user.models import User
from visit.tools import get_visitor_info, get_visitor_total
from web_service.decorators import web_service


@web_service(method='GET')
def visitor(request, type, id=None, only_today=False, data=None):
    """
    获取对象的访客列表

    :param type: 对象类型
    :param id: 对象ID
    :param only_today: 仅限今日数据？
    :param data:
        offset: 偏移量（默认值：0）
        limit: 数量上限（默认值：10）
    :return: JSON Array
        id: 用户ID
        name: 用户昵称
        last_visit_time: 最近访问时间
    """
    offset = 0 if not data or 'offset' not in data else data['offset']
    limit = 10 if not data or 'limit' not in data else data['limit']

    if type == User:
        visitor_info = get_visitor_info(request.user, only_today, offset, limit)
        r = []
        for i in visitor_info:
            r.append({
                'id': i.visitor.id,
                'name': i.visitor.name,
                'last_visit_time': i.last_visit_time,
            })
        return JsonResponse(r, safe=False)
    # elif obj_type == Team:
    #     pass


@web_service(method='GET')
def visitor_total(request, type, id=None, only_today=False):
    """
    获取对象总访问量

    :param type: 对象类型
    :param id: 对象ID
    :param only_today: 仅限今日数据？
    :return:
        total: 访问量
    """
    if type == User:
        d = {'total': get_visitor_total(request.user, only_today)}
        return JsonResponse(d)
    # elif obj_type == Team:
    #     pass
