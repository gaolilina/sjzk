from django.db import transaction

from tag.models import Tag


def get_tags(obj) -> list:
    """
    获取对象标签

    """
    tags = []
    for i in obj.tag_info.all():
        tags.append(i.tag.name)

    return tags


def set_tags(obj, tags: list):
    """
    设置对象标签

    :param obj: 带标签属性的对象
    :param tags: 标签列表，长度不大于5

    """
    if len(tags) > 5:
        raise ValueError('too many tags')

    with transaction.atomic():  # 先删后设
        for i in obj.tag_info.all():
            i.delete()

        for i in range(len(tags)):
            name = tags[i].strip()
            if not name:
                raise ValueError('invalid tag name')
            tag, is_created = Tag.objects.get_or_create(name=name)
            tag_info = obj.tag_info.model(order=i, tag=tag)
            obj.tag_info.add(tag_info, bulk=False)
