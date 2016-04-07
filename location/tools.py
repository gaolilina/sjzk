from django.core.exceptions import ObjectDoesNotExist

from location.models import Province, City, UserLocation, TeamLocation


def get_location(obj):
    """
    获取对象的位置信息

    """
    try:  # from UserLocation
        province_id = obj.location.province.id \
            if obj.location.province else None
        city_id = obj.location.city.id \
            if obj.location.city else None
        return [province_id, city_id]
    except ObjectDoesNotExist:
        return [None, None]


def set_location(obj, location: list):
    """
    设置对象位置信息

    :param obj: 带位置属性的对象
    :param location: 位置信息，格式：[x, y]，x：省索引，y：市索引

    """
    # 检查省、市索引有效性
    province = Province.objects.get(id=location[0]) if location[0] else None
    city = City.objects.get(id=location[1]) if location[1] else None
    if city and city.province != province:
        raise ValueError('the given city does not belong to the given province')

    try:
        loc = obj.location
    except ObjectDoesNotExist:
        class_name = obj.__class__.__name__
        if class_name == 'User':
            model = UserLocation
        elif class_name == 'Team':
            model = TeamLocation
        else:
            raise TypeError('invalid object type')

        loc = obj.location = model()

    loc.province = province
    loc.city = city
    loc.save()
