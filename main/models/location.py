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


class County(models.Model):
    """
    县级行政区

    """
    name = models.CharField(max_length=20)
    city = models.ForeignKey(City, models.CASCADE, 'counties')

    class Meta:
        db_table = 'location_county'


class LocationManager(models.Manager):
    def get_location(self, obj):
        """
        获取对象的位置信息

        """
        try:
            r = self.get(object=obj)
            pro_name = r.province.name if r.province else None
            cit_name = r.city.name if r.city else None
            cou_name = r.county.name if r.county else None
            return [pro_name, cit_name, cou_name]
        except ObjectDoesNotExist:
            return [None, None, None]

    def set_location(self, obj, location):
        """
        设置对象位置信息

        :param obj: 带位置属性的对象
        :param location: 位置信息，格式：[province_name, city_name, county_name]

        """
        # 检查省、市、区(县)索引有效性
        try:
            pro_name, cit_name, cou_name = location
            province = Province.objects.get(name=pro_name) if pro_name else None
            city = City.objects.get(name=cit_name) if cit_name else None
            county = County.objects.get(name=cou_name) if cou_name else None
        except ObjectDoesNotExist:
            raise ValueError('location not exists')

        if city and city.province != province:
            raise ValueError('invalid location')

        if county and county.city != city:
            raise ValueError('invalid location')

        r, created = self.get_or_create(
                object=obj, defaults={'province': province, 'city': city,
                                      'county': county})
        if not created:
            r.province = province
            r.city = city
            r.county = county
            r.save()


class Location(models.Model):
    """
    地区信息基类

    """
    object = None
    province = models.ForeignKey(
        Province, models.SET_NULL, default=None, null=True)
    city = models.ForeignKey(
        City, models.SET_NULL, default=None, null=True)
    county = models.ForeignKey(
        County, models.SET_NULL, default=None, null=True)

    objects = LocationManager()

    class Meta:
        abstract = True


class UserLocation(Location):
    """
    用户所在地区

    """
    object = models.OneToOneField(
        'User', models.CASCADE, related_name='location')

    class Meta:
        db_table = 'user_location'


class TeamLocation(Location):
    """
    团队所在地区

    """
    object = models.OneToOneField(
        'Team', models.CASCADE, related_name='location')

    class Meta:
        db_table = 'team_location'


class TeamNeedLocation(Location):
    """
    需求限定地区

    """
    object = models.OneToOneField(
        'TeamNeed', models.CASCADE, related_name='location')

    class Meta:
        db_table = 'need_location'
