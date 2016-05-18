from django.core.exceptions import ObjectDoesNotExist
from django.db import models


class Province(models.Model):
    """
    省级行政区

    """
    name = models.CharField(max_length=20)

    class Meta:
        db_table = 'location_province'


class City(models.Model):
    """
    市级行政区

    """
    name = models.CharField(max_length=20)
    province = models.ForeignKey(Province, models.CASCADE, 'cities')

    class Meta:
        db_table = 'location_city'


class Location(models.Model):
    """
    地区信息基类

    """
    province = models.ForeignKey(
        Province, models.SET_NULL, default=None, null=True)
    city = models.ForeignKey(
        City, models.SET_NULL, default=None, null=True)

    class Meta:
        abstract = True

    @staticmethod
    def get(obj):
        """
        获取对象的位置信息

        """
        try:
            pid = obj.location.province.id if obj.location.province else None
            cid = obj.location.city.id if obj.location.city else None
            return [pid, cid]
        except ObjectDoesNotExist:
            return [None, None]

    @staticmethod
    def set(obj, location_list):
        """
        设置对象位置信息

        :param obj: 带位置属性的对象
        :param location_list: 位置信息，格式：[province_id, city_id]

        """
        # 检查省、市索引有效性
        try:
            pid, cid = location_list
            province = Province.objects.get(id=pid) if pid else None
            city = City.objects.get(id=cid) if cid else None
        except ObjectDoesNotExist:
            raise ValueError('location not exists')

        if city and city.province != province:
            raise ValueError('invalid location')

        model_name = type(obj).__name__
        if model_name == 'User':
            location, created = UserLocation.objects.get_or_create(
                user=obj, defaults={'province': province, 'city': city})
        elif model_name == 'Team':
            location, created = TeamLocation.objects.get_or_create(
                team=obj, defaults={'province': province, 'city': city})
        else:
            raise TypeError('object does not have location attribute')

        if not created:
            location.province = province
            location.city = city
            location.save()


class UserLocation(Location):
    """
    用户所在地区

    """
    user = models.OneToOneField('User', models.CASCADE, related_name='location')

    class Meta:
        db_table = 'user_location'


class TeamLocation(Location):
    """
    团队所在地区

    """
    team = models.OneToOneField('Team', models.CASCADE, related_name='location')

    class Meta:
        db_table = 'team_location'
