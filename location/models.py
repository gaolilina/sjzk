from django.db import models

from team.models import Team
from user.models import User


class Province(models.Model):
    """
    省级行政区索引

    """
    name = models.CharField(max_length=10)
    users = models.ManyToManyField(User, '+', through='UserLocation')
    teams = models.ManyToManyField(Team, '+', through='TeamLocation')

    class Meta:
        db_table = 'location_province'

    def __repr__(self):
        return '<Province - %s>' % self.name


class City(models.Model):
    """
    市级行政区索引

    """
    name = models.CharField(max_length=10)
    province = models.ForeignKey(Province, models.CASCADE, 'cities', 'city')

    class Meta:
        db_table = 'location_city'

    def __repr__(self):
        return '<City - %s (%s)>' % (self.name, self.province.name)


class LocationInfo(models.Model):
    province = models.ForeignKey(
        Province, models.SET_NULL, blank=True, null=True, related_name='+')
    city = models.ForeignKey(
        City, models.SET_NULL, blank=True, null=True, related_name='+')

    class Meta:
        abstract = True


class UserLocation(LocationInfo):
    """
    APP用户位置

    """
    user = models.OneToOneField(User, models.CASCADE, related_name='location')

    class Meta:
        db_table = 'user_location'


class TeamLocation(LocationInfo):
    """
    团队位置

    """
    team = models.OneToOneField(Team, models.CASCADE, related_name='location')

    class Meta:
        db_table = 'team_location'
