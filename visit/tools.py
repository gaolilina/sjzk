from django.db import transaction
from django.db.models import Sum
from django.utils import timezone


@transaction.atomic
def update_visitor(obj, visitor):
    """
    更新对象的来访记录

    :param obj: 被访问对象
    :param visitor: 来访用户

    """
    now = timezone.now()
    visitor_info, is_created = obj.visitor_info.get_or_create(
        visitor=visitor, defaults={'count': 1, 'last_visit_time': now})

    if not is_created:  # 同日内同一访客多次访问不更新访问计数
        if now.date() != visitor_info.last_visit_time.date():
            visitor_info.count += 1
        visitor_info.last_visit_time = now
        visitor_info.save()


def get_visitor_info(obj, only_today, offset, limit) -> list:
    """
    获取对象的访客列表

    :param obj: 被访问对象
    :param only_today: 仅限今日数据？
    :param offset: 偏移量（默认值：0）
    :param limit: 数量上限（默认值：10）

    """
    if only_today:
        today = timezone.now().date()
        return obj.visitor_info.filter(
            last_visit_time__date=today)[offset:offset+limit]
    else:
        return obj.visitor_info.all()[offset:offset+limit]


def get_visitor_total(obj, only_today):
    """
    获取对象的访客数量

    :param obj: 被访问对象
    :param only_today: 仅限今日数据？

    """
    if only_today:
        today = timezone.now().date()
        return obj.visitor_info.filter(last_visit_time__date=today).count()
    else:
        d = obj.visitor_info.aggregate(Sum('count'))
        return d['count__sum'] if d['count__sum'] else 0
